from src.database import Database
import logging

logging.basicConfig(level=logging.INFO)
db = Database()

print("Testing search_relevant_books with 'explain verbs'...")
results = db.search_relevant_books("explain verbs", limit=5)
print(f"Results found: {len(results)}")
for i, res in enumerate(results, 1):
    print(f"\n[{i}] {res['title']}")
    print(f"Snippet length: {len(res['content'])}")
    print(f"Snippet start: {res['content'][:200]}...")
