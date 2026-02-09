from src.database import Database
import logging

logging.basicConfig(level=logging.INFO)
db = Database()

print("Testing search_relevant_books...")
try:
    results = db.search_relevant_books("test", limit=5)
    print(f"Search results: {len(results)}")
except Exception as e:
    print(f"Search failed: {e}")

print("\nTesting get_conversations...")
try:
    # Use a dummy user ID
    results = db.get_conversations(user_id=1, assistant_type='general', limit=5)
    print(f"History results: {len(results)}")
except Exception as e:
    print(f"History failed: {e}")
