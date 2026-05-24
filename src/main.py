import os
import sys
import json
import asyncio
import requests
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination

# Conditional imports based on environment
if os.getenv("GITHUB_EVENT_PATH"):
    from reviewer_agents import reviewer_agent, qa_agent
    agents_to_use = [reviewer_agent, qa_agent]
    print("Running in PR REVIEW MODE")
else:
    from agents import coder_agent, critic_agent
    agents_to_use = [coder_agent, critic_agent]
    print("Running in LOCAL DEV MODE")

def get_github_context():
    """Extracts git pull request contextual metadata and code diff if operating inside a cloud CI/CD worker."""
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        print("No GITHUB_EVENT_PATH found. Running in local mode.")
        return None
        
    try:
        with open(event_path, 'r') as f:
            event_data = json.load(f)
        
        # Extract PR information
        pr_url = event_data["pull_request"]["url"]
        comments_url = event_data["pull_request"]["comments_url"]
        headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
        
        # Extract the patch file containing actual code changes
        diff_response = requests.get(f"{pr_url}.diff", headers=headers)
        
        if diff_response.status_code == 200:
            diff_content = diff_response.text
            print(f"Successfully fetched PR diff: {len(diff_content)} characters")
            
            # Debug: Show first few lines of diff
            if diff_content:
                preview = diff_content[:200].replace('\n', '\\n')
                print(f"Diff preview: {preview}...")
            else:
                print("Warning: Diff content is empty")
                return None
        else:
            print(f"Failed to fetch diff: Status {diff_response.status_code}")
            return None
        
        return {
            "diff": diff_content,
            "comments_url": comments_url,
            "headers": headers,
            "pr_title": event_data["pull_request"].get("title", "No title"),
            "pr_author": event_data["pull_request"]["user"]["login"]
        }
        
    except Exception as e:
        print(f"Error getting GitHub context: {str(e)}")
        return None

async def run_pipeline():
    git_ctx = get_github_context()
    
    if git_ctx and git_ctx.get('diff') and len(git_ctx['diff']) > 0:
        # PR REVIEW MODE - Analyze existing code changes
        task_prompt = f"""You are reviewing a Pull Request. Please analyze the following code changes:

PULL REQUEST TITLE: {git_ctx['pr_title']}
AUTHOR: {git_ctx['pr_author']}

CODE CHANGES (DIFF):
{git_ctx['diff']}

INSTRUCTIONS FOR CODE_REVIEWER:
1. Carefully analyze each file change shown in the diff above
2. Look for security vulnerabilities, bugs, style issues, and performance problems
3. Provide specific line-by-line feedback where needed
4. Comment on the overall code quality
5. End with either 'APPROVED' if the code is good, or 'CHANGES REQUESTED' if fixes are needed

Be thorough and constructive in your review."""
        print("PR REVIEW MODE: Analyzing pull request changes")
        
    else:
        # LOCAL DEV MODE - Write new code from scratch
        task_prompt = """Write a secure function to validate user emails and compute password hash strength scores.

Requirements:
1. Create a function `validate_email(email)` that:
   - Validates email format using regex
   - Returns True for valid emails, False for invalid
   - Handles edge cases (empty string, None, invalid types)

2. Create a function `compute_password_strength(password)` that:
   - Returns a strength score from 0 to 4
   - Consider length, uppercase, lowercase, digits, special characters
   - Provide feedback on how to improve weak passwords

3. Include comprehensive pytest test cases covering:
   - Valid and invalid emails
   - Edge cases
   - Various password strengths

Return ONLY the code inside ```python ``` markdown blocks. Include both implementation and tests."""
        print("LOCAL DEV MODE: Writing new code from scratch")

    print("-" * 80)
    print("Initializing AI Automation Loop...")
    print("-" * 80)
    
    termination = TextMentionTermination("APPROVED")
    team = RoundRobinGroupChat(agents_to_use, termination_condition=termination, max_turns=10)

    full_transcript = []
    message_count = 0
    
    async for message in team.run_stream(task=task_prompt):
        message_count += 1
        if message and hasattr(message, 'content') and message.content:
            log_line = f"### [{message.source.upper()}]\n{message.content}\n"
            print(log_line)
            full_transcript.append(log_line)
        
        # Add a separator between messages for readability
        if hasattr(message, 'source'):
            print("-" * 40)
    
    print(f"Total messages exchanged: {message_count}")

    # If running inside GitHub actions, comment the full multi-agent transcript onto the PR thread
    if git_ctx and full_transcript:
        try:
            # Create a formatted markdown summary
            summary_header = f"""## AI Multi-Agent Pipeline Execution Summary

**Pull Request:** {git_ctx['pr_title']}
**Author:** {git_ctx['pr_author']}
**Status:** Pipeline completed

### Agent Conversation Transcript

"""
            markdown_body = summary_header + "\n".join(full_transcript)
            
            # Truncate if too long (GitHub has limits)
            if len(markdown_body) > 65000:
                markdown_body = markdown_body[:65000] + "\n... (truncated due to length limit)"
            
            response = requests.post(
                git_ctx["comments_url"], 
                json={"body": markdown_body}, 
                headers=git_ctx["headers"]
            )
            
            if response.status_code == 201:
                print("Successfully posted review to PR")
            else:
                print(f"Failed to post to PR: Status {response.status_code}")
                print(f"Response: {response.text[:200]}")
        except Exception as e:
            print(f"Error posting to PR: {str(e)}")
    
    print("\n" + "=" * 80)
    print("Pipeline execution completed successfully")
    print("=" * 80)

if __name__ == "__main__":
    try:
        asyncio.run(run_pipeline())
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nPipeline failed with error: {str(e)}")
        sys.exit(1)