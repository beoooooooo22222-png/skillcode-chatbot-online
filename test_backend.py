
import os
import sys
import logging
from src.database import Database
from src.grok_service import GrokService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_backend():
    print("--- Testing Database ---")
    try:
        db = Database()
        print("✅ Database initialized")
        
        # Test getting books
        books = db.get_all_books()
        print(f"✅ Books fetched: {len(books)}")
        
        # Test search
        res = db.search_relevant_books("verbs")
        print(f"✅ Search result count: {len(res)}")
        
        # Test save conversation (mock user ID 1)
        # Assuming user 1 exists or creating one
        user = db.get_user_by_email("test@example.com")
        if not user:
             uid = db.create_user("test@example.com")
             print(f"✅ Created test user: {uid}")
             user_id = uid
        else:
             user_id = user['id']
             print(f"✅ Found test user: {user_id}")
             
        db.save_conversation(user_id, 'general', 'test message', 'test response')
        print("✅ Conversation saved")
        
    except Exception as e:
        print(f"❌ Database Error: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n--- Testing Grok/Groq Service ---")
    try:
        grok = GrokService()
        print("✅ GrokService initialized")
        
        try:
            response = grok._call_grok_api("Hello, say hi back.")
            print(f"✅ API Response: {response}")
        except Exception as e:
            print(f"❌ API Call Failed: {e}")
            
    except Exception as e:
        print(f"❌ GrokService Error: {e}")

if __name__ == "__main__":
    # Force output to stdout
    test_backend()
