"""
Create demo accounts for testing
Run this script to add demo users to the database
"""

from werkzeug.security import generate_password_hash
from src.database import Database

def create_demo_accounts():
    db = Database()
    
    demo_accounts = [
        {"email": "user1@skillcode.com", "password": "password123"},
        {"email": "user2@skillcode.com", "password": "password123"},
        {"email": "user3@skillcode.com", "password": "password123"},
        {"email": "user4@skillcode.com", "password": "password123"},
    ]
    
    for account in demo_accounts:
        email = account["email"]
        password = account["password"]
        
        # Check if account already exists
        if db.email_exists(email):
            print(f"⚠️  Account already exists: {email}")
        else:
            password_hash = generate_password_hash(password)
            user_id = db.create_user(email, password_hash)
            print(f"✅ Created account: {email} (ID: {user_id})")
    
    print("\n" + "="*50)
    print("Demo Accounts Created!")
    print("="*50)
    print("\nYou can login with any of these credentials:\n")
    for account in demo_accounts:
        print(f"  Email: {account['email']}")
        print(f"  Password: {account['password']}")
        print()

if __name__ == "__main__":
    create_demo_accounts()
