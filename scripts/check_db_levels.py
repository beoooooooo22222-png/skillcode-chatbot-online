from database import Database
db = Database()
books = db.get_all_books()
print(f"{'Title':<40} | {'Primary Level'}")
print("-" * 60)
for b in books:
    print(f"{b['title']:<40} | {b['primary_level']}")
