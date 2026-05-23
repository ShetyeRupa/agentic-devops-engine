import os
import subprocess
import json
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

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

def execute_code_in_sandbox(source_code: str, test_code: str) -> str:
    """
    Safely writes AI-generated source code and test scripts to disk, 
    spins up an isolated Docker container sandbox, executes pytest, 
    and captures execution performance or failure logs.
    """
    # Clean string literals from LLM formatting markers if present
    clean_source = source_code.replace("```python", "").replace("```", "").strip()
    clean_test = test_code.replace("```python", "").replace("```", "").strip()

    with open("sandbox_source.py", "w") as f:
        f.write(clean_source)
        
    with open("generated_tests.py", "w") as f:
        f.write(clean_test)

    try:
        # Check if Docker is running
        subprocess.run(["docker", "ps"], check=True, capture_output=True)
        
        # Build the container image securely
        subprocess.run(["docker", "build", "-t", "ai_devops_sandbox", "."], check=True, capture_output=True)
        
        # Mount files and execute test framework inside the sandbox
        result = subprocess.run([
            "docker", "run", "--rm", 
            "-v", f"{os.getcwd()}/sandbox_source.py:/app/sandbox_source.py",
            "-v", f"{os.getcwd()}/generated_tests.py:/app/generated_tests.py",
            "ai_devops_sandbox"
        ], capture_output=True, text=True, timeout=20)
        
        return f"EXECUTION RESULT:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    except subprocess.TimeoutExpired:
        return "ERROR: Code execution timed out after 20 seconds. Potential infinite loop detected."
    except subprocess.CalledProcessError as e:
        return f"DOCKER ERROR: {str(e)}\nOutput: {e.output.decode() if e.output else 'None'}"
    except Exception as e:
        return f"CRITICAL SANDBOX ERROR: {str(e)}"

# Register the Python function as a tool
execute_tool = [execute_code_in_sandbox]

coder_agent = AssistantAgent(
    name="software_engineer",
    model_client=model_client,
    system_message=(
        "You are an expert Senior Python Developer. "
        "Write clean, secure Python code with proper validation and tests. "
        "Return ONLY the code inside ```python ``` markdown blocks. "
        "Include both the implementation AND pytest test cases. "
        "Do NOT try to call the execute_code_in_sandbox tool - only the code_critic uses that."
    )
)

critic_agent = AssistantAgent(
    name="code_critic",
    model_client=model_client,
    tools=execute_tool,
    system_message=(
        "You are an elite QA and Security Engineer. "
        "Your job is to test the software_engineer's code using the execute_code_in_sandbox tool.\n\n"
        "To use the tool, respond with EXACTLY this format:\n"
        "execute_code_in_sandbox(source_code='<the code to test>', test_code='<the pytest tests>')\n\n"
        "After running the tool, analyze the output. "
        "If all tests pass and code is secure, reply with exactly: APPROVED\n"
        "If tests fail, explain what's wrong and what needs to be fixed."
    )
)