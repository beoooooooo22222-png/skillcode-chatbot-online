#!/usr/bin/env python3
"""Test Hugging Face API"""

import requests
import json

API_KEY = "[SECRET_KEY_REMOVED]"
BASE_URL = "https://router.huggingface.co/models"
MODEL = "gpt2"

def test_hf_api():
    """Test if Hugging Face API is accessible"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": "Hello, how are you?",
        "parameters": {
            "max_new_tokens": 100
        }
    }
    
    url = f"{BASE_URL}/{MODEL}"
    
    print(f"Testing Hugging Face API")
    print(f"URL: {url}")
    print(f"Key: {API_KEY[:20]}...\n")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{response.text}\n")
        
        if response.status_code == 200:
            print("✅ API KEY IS VALID!")
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"Response: {data[0].get('generated_text', 'No text')}")
        else:
            print(f"❌ API ERROR - Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_hf_api()
