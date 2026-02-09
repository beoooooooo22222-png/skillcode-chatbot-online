
import logging
import os
import sqlite3
from datetime import datetime
from threading import Lock

logger = logging.getLogger(__name__)

class Database:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Database, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized: return
        self._initialized = True
        
        """Initialize SQLite connection"""
        self.db_path = os.path.join(os.getcwd(), 'skillcode.db')
        
        # Initialize schema
        self.init_db()

    def get_connection(self):
        """Get a fresh connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Ensure tables exist"""
        logger.info(f"Initializing SQLite database at {self.db_path}")
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # 1. Users
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2. Library (Metadata for vector store link)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS library (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_title TEXT UNIQUE NOT NULL,
                    file_path TEXT,
                    md5_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 3. Conversations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    assistant_type TEXT,
                    user_message TEXT,
                    ai_response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)
            
            conn.commit()
            logger.info("✅ SQLite schema initialized")
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")
        finally:
            conn.close()

    # --- USER MANAGEMENT ---

    def get_user_by_email(self, email):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email FROM users WHERE LOWER(email) = LOWER(?)", (email,))
            row = cursor.fetchone()
            if row:
                return {'id': row['id'], 'email': row['email']}
            return None
        finally:
            conn.close()

    def get_user_with_password(self, email):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, password_hash FROM users WHERE LOWER(email) = LOWER(?)", (email,))
            row = cursor.fetchone()
            if row:
                return {'id': row['id'], 'email': row['email'], 'password_hash': row['password_hash']}
            return None
        finally:
            conn.close()

    def get_user_by_id(self, user_id):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return {'id': row['id'], 'email': row['email']}
            return None
        finally:
            conn.close()

    def create_user(self, email, password_hash=None):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, password_hash)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise e
        finally:
            conn.close()

    def email_exists(self, email):
        return self.get_user_by_email(email) is not None

    # --- BOOK METADATA MANAGEMENT ---
    # Actual content will be in Vector Store, but we keep metadata here to list books

    def add_book_metadata(self, title, file_path):
        """Add book metadata only"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO library (book_title, file_path) VALUES (?, ?)", (title, file_path))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding book metadata: {e}")
            return False
        finally:
            conn.close()

    def get_all_books(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, book_title FROM library ORDER BY book_title")
            return [{'id': row['id'], 'title': row['book_title']} for row in cursor.fetchall()]
        finally:
            conn.close()

    # --- CONVERSATION MANAGEMENT ---

    def save_conversation(self, user_id, assistant_type, user_message, ai_response):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (user_id, assistant_type, user_message, ai_response) VALUES (?, ?, ?, ?)",
                (user_id, assistant_type, user_message, ai_response)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
        finally:
            conn.close()

    def get_conversations(self, user_id, assistant_type='all', limit=20):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT user_message, ai_response, created_at FROM conversations WHERE user_id = ?"
            params = [user_id]
            
            if assistant_type != 'all' and assistant_type is not None:
                query += " AND assistant_type = ?"
                params.append(assistant_type)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'user_message': row['user_message'],
                    'ai_response': row['ai_response'],
                    'created_at': row['created_at']
                })
            return results
        except Exception as e:
            logger.error(f"Error fetching conversations: {e}")
            return []
        finally:
            conn.close()

    def get_user_stats(self, user_id):
        conn = self.get_connection()
        stats = {
            'conversations': 0,
            'study_hours': 0,
            'topics_mastered': 0,
            'exams_completed': 0
        }
        try:
            cursor = conn.cursor()
            
            # 1. Total Conversations
            cursor.execute("SELECT COUNT(*) FROM conversations WHERE user_id = ?", (user_id,))
            stats['conversations'] = cursor.fetchone()[0]
            
            # 2. Estimated Study Hours
            stats['study_hours'] = round(stats['conversations'] * 0.25, 1)
            
            # 3. Topics Mastered
            cursor.execute("SELECT COUNT(DISTINCT assistant_type) FROM conversations WHERE user_id = ?", (user_id,))
            stats['topics_mastered'] = cursor.fetchone()[0]
            
            # 4. Exams Completed
            cursor.execute("SELECT COUNT(*) FROM conversations WHERE assistant_type = 'exam' AND user_id = ?", (user_id,))
            stats['exams_completed'] = cursor.fetchone()[0]
            
            return stats
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return stats
        finally:
            conn.close()
