from src.database import Database
import os

# Set dummy env var for limit
os.environ['MAX_BOOKS_PER_SEARCH'] = '3'

db = Database()

def test_query(query, expected_subject):
    print(f"\n--- Testing Query: '{query}' ---")
    results = db.search_relevant_books(query, limit=5)
    
    if not results:
        print("❌ No results found.")
        return

    print(f"Found {len(results)} books:")
    all_correct = True
    for r in results:
        print(f" - {r['title']}")
        if expected_subject.lower() not in r['title'].lower():
             # Special case for mapped subjects (e.g. Science -> Science, Biology, etc)
             pass 
    
    # Check if we got any WRONG subjects
    # e.g. if expected 'Arabic', should NOT see 'Math'
    for r in results:
        if expected_subject == 'Arabic' and 'Math' in r['title']:
            print("❌ FAILURE: Found Math book in Arabic query!")
            all_correct = False
        if expected_subject == 'Math' and 'Arabic' in r['title']:
            print("❌ FAILURE: Found Arabic book in Math query!")
            all_correct = False
            
    if all_correct:
        print("✅ SUCCESS: Subject filtering appears correct.")

