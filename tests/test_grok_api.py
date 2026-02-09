#!/usr/bin/env python3
"""Test Grok API directly"""

import requests
import json

API_KEY = "[YOUR_GROK_API_KEY]"
BASE_URL = "https://api.x.ai"
MODEL = "grok-beta"

def test_grok_api():
    """Test if Grok API is accessible with current key"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Say hello"
            }
        ],
        "model": MODEL,
        "stream": False
    }
    
    url = f"{BASE_URL}/v1/chat/completions"
    
    print(f"Testing Grok API")
    print(f"URL: {url}")
    print(f"Key: {API_KEY[:20]}...")
    print(f"Model: {MODEL}\n")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{response.text}\n")
        
        if response.status_code == 200:
            print("✅ API KEY IS VALID!")
            data = response.json()
            print(f"Response: {data['choices'][0]['message']['content']}")
        else:
            print(f"❌ API ERROR - Status {response.status_code}")
            print("Your API key may be invalid or expired.")
            print("Get a new one from: https://console.x.ai/")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_grok_api()
