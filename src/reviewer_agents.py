from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import os

load_dotenv()

# Setup the AI Client for local LLM
model_client = OpenAIChatCompletionClient(
    model="ollama_chat/qwen2.5-coder:1.5b",
    base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:8000/v1"),
    api_key=os.getenv("OPENAI_API_KEY", "fake"),
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": False,
        "family": "unknown",
        "structured_output": False,
    },
    temperature=0.7,
)

# Reviewer agent - analyzes PR diffs
reviewer_agent = AssistantAgent(
    name="code_reviewer",
    model_client=model_client,
    system_message=(
        "You are a Senior Code Reviewer. "
        "Your job is to analyze pull request diffs. "
        "Focus on: security vulnerabilities, code quality, bugs, and best practices. "
        "Provide specific line-by-line feedback. "
        "Be thorough but constructive. "
        "End with either 'APPROVED' if the code is good, or 'CHANGES REQUESTED' if fixes are needed."
    )
)

# QA agent - approves or rejects
qa_agent = AssistantAgent(
    name="qa_engineer",
    model_client=model_client,
    system_message=(
        "You are a QA Engineer. "
        "Review the code reviewer's analysis. "
        "If the analysis is thorough and code is good, reply with: APPROVED\n"
        "If issues were found, reply with: CHANGES REQUESTED\n"
        "Add any additional testing concerns you notice."
    )
)