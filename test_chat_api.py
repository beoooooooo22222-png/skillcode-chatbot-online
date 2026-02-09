
import requests
import json

def test_chat():
    url = "http://localhost:5000/api/chat"
    payload = {
        "message": "explain verbs for me",
        "assistant_type": "general",
        "params": {}
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    # We need a session with a logged in user
    # But for a quick test, let's just see if we can call it directly 
    # (it will fail with redirect to login if not logged in)
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_chat()
