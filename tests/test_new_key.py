#!/usr/bin/env python3
"""Test Gemini API with new key"""

import requests
import json

API_KEY = "AIzaSyCx1uDRx7gEY_Zu1wYhsrDUfPYOh-iR4g8"
BASE_URL = "https://generativelanguage.googleapis.com"
MODEL = "gemini-2.5-flash"

def test_gemini_api():
    """Test if Gemini API is accessible"""
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Hello, say hello back"
                    }
                ]
            }
        ]
    }
    
    url = f"{BASE_URL}/v1/models/{MODEL}:generateContent?key={API_KEY}"
    
    print(f"Testing Gemini API with new key")
    print(f"URL: {url}")
    print(f"Key: {API_KEY[:20]}...\n")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{response.text}\n")
        
        if response.status_code == 200:
            print("✅ API KEY IS VALID AND WORKING!")
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                reply = data['candidates'][0]['content']['parts'][0]['text']
                print(f"\nAI Response: {reply}")
            return True
        else:
            print(f"❌ API ERROR - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    test_gemini_api()
