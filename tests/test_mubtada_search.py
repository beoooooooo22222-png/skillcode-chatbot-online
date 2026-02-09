from database import Database
db = Database()
# Test with variations
queries = ["المبتدا", "مبتدأ", "شرح المبتدأ"]
for query in queries:
    results = db.search_relevant_books(query)
    print(f"\n--- Results for '{query}' ---")
    if not results:
        print("No results found.")
    for r in results:
        print(f"Book: {r['title']}")
        print(f"Snippet: {r['content'][:300]}...")
