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
else:
    from agents import coder_agent, critic_agent
    agents_to_use = [coder_agent, critic_agent]

def get_github_context():
    """Extracts git pull request contextual metadata if operating inside a cloud CI/CD worker."""
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        return None
        
    with open(event_path, 'r') as f:
        event_data = json.load(f)
        
    pr_url = event_data["pull_request"]["url"]
    comments_url = event_data["pull_request"]["comments_url"]
    headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
    
    # Extract the patch file containing changes
    diff_response = requests.get(f"{pr_url}.diff", headers=headers)
    return {"diff": diff_response.text, "comments_url": comments_url, "headers": headers}

async def run_pipeline():
    git_ctx = get_github_context()
    
    if git_ctx:
        task_prompt = f"Review the following pull request code changes and provide detailed feedback:\n\n{git_ctx['diff']}"
    else:
        # Default local fallback prompt for immediate verification
        task_prompt = "Write a secure function to validate user emails and compute password hash strength scores. Include both the implementation and pytest test cases."

    print(f"Initializing AI Automation Loop for Task...")
    print("-" * 80)
    
    termination = TextMentionTermination("APPROVED")
    team = RoundRobinGroupChat(agents_to_use, termination_condition=termination, max_turns=10)

    full_transcript = []
    async for message in team.run_stream(task=task_prompt):
        if message and hasattr(message, 'content') and message.content:
            log_line = f"### [{message.source.upper()}]\n{message.content}\n"
            print(log_line)
            full_transcript.append(log_line)
        
        # Add a separator between messages for readability
        if hasattr(message, 'source'):
            print("-" * 40)

    # If running inside GitHub actions, comment the full multi-agent transcript onto the PR thread
    if git_ctx and full_transcript:
        markdown_body = "## AI Multi-Agent Pipeline Execution Summary\n\n" + "\n".join(full_transcript)
        response = requests.post(git_ctx["comments_url"], json={"body": markdown_body}, headers=git_ctx["headers"])
        if response.status_code == 201:
            print("Review posted to PR")
        else:
            print(f"Failed to post to PR: {response.status_code}")
    
    print("\n" + "=" * 80)
    print("Pipeline execution completed.")

if __name__ == "__main__":
    asyncio.run(run_pipeline())