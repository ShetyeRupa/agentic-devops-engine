import os
import requests
import json

def get_github_pr_diff() -> str:
    """Fetches the raw code modifications (diff) from the active GitHub Pull Request event environment."""
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        return "Local testing mode. No live GitHub event found."
    
    # Extract the pull request API endpoint URL from the active runner session
    import json
    with open(event_path, 'r') as f:
        event_data = json.load(f)
    
    pr_url = event_data["pull_request"]["url"]
    headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
    
    # Request the patch format of the PR code changes
    response = requests.get(f"{pr_url}.diff", headers=headers)
    return response.text

def post_github_pr_comment(comment_markdown: str):
    """Posts the multi-agent final decision directly onto the developer's pull request thread."""
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        print("Skipping comment: Local mode.")
        return

    with open(event_path, 'r') as f:
        event_data = json.load(f)
        
    comments_url = event_data["pull_request"]["comments_url"]
    headers = {
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Submit the critique payload
    requests.post(comments_url, json={"body": comment_markdown}, headers=headers)