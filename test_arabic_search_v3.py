from src.database import Database
import logging

logging.basicConfig(level=logging.INFO)
db = Database()

query = "كان و اخواتها"
print(f"Testing search for '{query}':")
results = db.search_relevant_books(query)
print(f"Found {len(results)} results.")
for res in results:
    print(f"- {res['title']}")
