import requests
import json
import config

headers = {
    "Authorization": f"Bearer {config.GROK_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": config.GROK_MODEL,
    "messages": [{"role": "user", "content": "Hi"}],
    "stream": False
}

try:
    response = requests.post(
        f"{config.GROK_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
