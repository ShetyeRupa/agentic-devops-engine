import subprocess
import os

def execute_code_in_sandbox(source_code: str, test_code: str) -> str:
    """
    Safely writes AI-generated source code and test scripts to disk, 
    spins up an isolated Docker container sandbox, executes pytest, 
    and captures execution performance or failure logs.
    """
    # 1. Write the code files locally to be mounted to Docker
    with open("sandbox_source.py", "w") as f:
        f.write(source_code)
        
    with open("generated_tests.py", "w") as f:
        f.write(test_code)

    # 2. Programmatically trigger the Docker build and run commands
    try:
        # Build the locked-down sandbox image
        subprocess.run(["docker", "build", "-t", "ai_devops_sandbox", "."], check=True, capture_output=True)
        
        # Run the container. Mount local python files into the app folder.
        result = subprocess.run([
            "docker", "run", "--rm", 
            "-v", f"{os.getcwd()}/sandbox_source.py:/app/sandbox_source.py",
            "-v", f"{os.getcwd()}/generated_tests.py:/app/generated_tests.py",
            "ai_devops_sandbox"
        ], capture_output=True, text=True, timeout=30) # Strict timeout to prevent infinite loops
        
        # Return stdout combined with stderr for the agent to review
        return f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"

    except subprocess.TimeoutExpired:
        return "ERROR: Code execution timed out after 30 seconds. Potential infinite loop detected."
    except Exception as e:
        return f"CRITICAL SANDBOX ERROR: {str(e)}"