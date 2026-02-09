from database import Database
db = Database()
query = "التضحية الوطن"
results = db.search_relevant_books(query)
print(f"Results for '{query}':")
for r in results:
    print(f"Book: {r['title']}")
    print(f"Content length: {len(r['content'])}")
    print(f"Snippet: {r['content'][:500]}")
