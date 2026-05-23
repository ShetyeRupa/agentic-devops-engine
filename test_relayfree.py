#!/usr/bin/env python3
"""
Test script to verify RelayFreeLLM is working correctly
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_relayfree_connection():
    """Test if RelayFreeLLM is accessible"""
    base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:8000/v1")
    
    try:
        # Test health endpoint
        health_url = base_url.replace("/v1", "/health")
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print("✅ RelayFreeLLM is running!")
        else:
            print(f"⚠️  RelayFreeLLM responded with status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to RelayFreeLLM. Make sure it's running:")
        print("   docker-compose up -d")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test the chat completion endpoint
    try:
        test_payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "user", "content": "Say 'Hello, RelayFreeLLM is working!'"}
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
            print(f"✅ LLM responded: {message[:100]}...")
            return True
        else:
            print(f"❌ Chat completion failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Chat completion error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing RelayFreeLLM Setup...")
    success = test_relayfree_connection()
    if success:
        print("\n🎉 RelayFreeLLM is ready! You can now run: python src/main.py")
    else:
        print("\n⚠️  RelayFreeLLM setup has issues. Please check the error messages above.")