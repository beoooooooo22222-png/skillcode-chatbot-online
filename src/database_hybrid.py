
import os
import logging
from src.database_sqlite import Database as SQLiteDB
from src.vector_db import VectorDB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedDatabase:
    """
    Unified Database Interface
    Combines SQLite (Users, Chats) and FAISS (Books Vector Search)
    """
    def __init__(self):
        self.sql_db = SQLiteDB()
        self.vector_db = VectorDB()
        
    # --- PROXY METHODS TO SQLITE ---
    
    def get_user_by_email(self, email):
        return self.sql_db.get_user_by_email(email)

    def get_user_with_password(self, email):
        return self.sql_db.get_user_with_password(email)

    def get_user_by_id(self, user_id):
        return self.sql_db.get_user_by_id(user_id)

    def create_user(self, email, password_hash=None):
        return self.sql_db.create_user(email, password_hash)

    def email_exists(self, email):
        return self.sql_db.email_exists(email)

    def save_conversation(self, user_id, assistant_type, user_message, ai_response):
        return self.sql_db.save_conversation(user_id, assistant_type, user_message, ai_response)

    def get_conversations(self, user_id, assistant_type='all', limit=20):
        return self.sql_db.get_conversations(user_id, assistant_type, limit)

    def get_user_stats(self, user_id):
        return self.sql_db.get_user_stats(user_id)
        
    def get_all_books(self):
        return self.sql_db.get_all_books()

    # --- BOOK MANAGEMENT (HYBRID) ---

    def add_book(self, title, file_path, content):
        """Add to SQLite (Metadata) AND Vector DB (Chunks)"""
        # 1. Add Metadata to SQLite
        self.sql_db.add_book_metadata(title, file_path)
        
        # 2. Add Content to Vector Store
        return self.vector_db.add_book(title, content)

    def search_relevant_books(self, query, limit=5, subject_filter=None):
        """Search using Vector Store"""
        return self.vector_db.search(query, limit, subject_filter)

# Use this class as the singleton 'Database'
Database = UnifiedDatabase
