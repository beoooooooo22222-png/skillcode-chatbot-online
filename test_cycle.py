from src.database import Database
import oracledb

db = Database()
user_id = 41 # From our earlier check
type_ = 'general'

print(f"Testing save/fetch for User {user_id}...")

# 1. Save
db.save_conversation(user_id, type_, "Test Question", "Test Answer")
print("Save call finished.")

# 2. Fetch
history = db.get_conversations(user_id, type_, limit=5)
found = False
for h in history:
    if h['user_message'] == "Test Question":
        found = True
        break

if found:
    print("✅ TEST PASSED: Conversation saved and retrieved correctly.")
else:
    print("❌ TEST FAILED: Could not find the saved conversation.")
