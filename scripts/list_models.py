#!/usr/bin/env python3
"""List available Gemini models"""

import requests
import json

API_KEY = "AIzaSyDkOIJvDP2sNWrDJrd5UbChL6O48EbSmPo"
BASE_URL = "https://generativelanguage.googleapis.com"

def list_models():
    """List available models"""
    
    url = f"{BASE_URL}/v1/models?key={API_KEY}"
    
    print(f"Listing available Gemini models...\n")
    
    try:
        response = requests.get(url, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{response.text}\n")
        
        if response.status_code == 200:
            data = response.json()
            print("Available models:")
            if 'models' in data:
                for model in data['models']:
                    print(f"  - {model.get('name', 'Unknown')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()
