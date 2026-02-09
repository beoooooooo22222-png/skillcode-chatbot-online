#!/usr/bin/env python3
"""Test Gemini API directly"""

import requests
import json

API_KEY = "AIzaSyDkOIJvDP2sNWrDJrd5UbChL6O48EbSmPo"
BASE_URL = "https://generativelanguage.googleapis.com"
MODEL = "gemini-1.0-pro"

def test_gemini_api():
    """Test if Gemini API is accessible with current key"""
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Say hello"
                    }
                ]
            }
        ]
    }
    
    url = f"{BASE_URL}/v1/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    
    print(f"Testing Gemini API")
    print(f"URL: {url}")
    print(f"Key: {API_KEY[:20]}...\n")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{response.text}\n")
        
        if response.status_code == 200:
            print("✅ API KEY IS VALID!")
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                reply = data['candidates'][0]['content']['parts'][0]['text']
                print(f"Response: {reply}")
        else:
            print(f"❌ API ERROR - Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_gemini_api()
