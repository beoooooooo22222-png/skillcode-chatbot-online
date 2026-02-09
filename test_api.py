from src.grok_service import GrokService
import logging

logging.basicConfig(level=logging.INFO)
grok = GrokService()
response = grok.get_response("test message")
print(f"Response: {response}")
