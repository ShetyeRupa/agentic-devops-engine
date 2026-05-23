#!/usr/bin/env python3
"""
Test script to verify the local LLM setup is working correctly
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_llm_connection():
    """Test if the LLM server is accessible"""
    base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:8000/v1")
    
    try:
        # Test a simple chat completion
        test_payload = {
            "model": "ollama_chat/qwen2.5-coder:1.5b",
            "messages": [
                {"role": "user", "content": "Say 'Connection successful'"}
            ],
            "max_tokens": 50
        }
        
        response = requests.post(
            f"{base_url}/chat/completions",
            json=test_payload,
            headers={"Authorization": "Bearer fake"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"LLM responded: {message}")
            return True
        else:
            print(f"Chat completion failed with status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Cannot connect to LLM server. Make sure LiteLLM is running:")
        print("  litellm --model ollama_chat/qwen2.5-coder:1.5b --port 8000")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing LLM Connection...")
    success = test_llm_connection()
    if success:
        print("Setup is ready. You can now run: python src/main.py")
    else:
        print("Setup has issues. Please check the error messages above.")