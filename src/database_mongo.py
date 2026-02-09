
import pymongo
import logging
import os
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT, ReturnDocument
from src.config import MONGO_URI, MONGO_DB_NAME

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        """Initialize MongoDB connection"""
        self.uri = MONGO_URI
        self.db_name = MONGO_DB_NAME
        
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            # Test connection
            self.client.server_info()
            logger.info("✅ MongoDB Connection Verified")
            
            # Initialize schema (indexes)
            self.init_db()
        except Exception as e:
            logger.error(f"Database initialization error: {e}")

    def init_db(self):
        """Ensure collections and indexes exist"""
        try:
            # 1. Users
            self.db.users.create_index([("email", ASCENDING)], unique=True)
            self.db.users.create_index([("id", ASCENDING)], unique=True)

            # 2. Library (Books)
            self.db.library.create_index([("book_title", ASCENDING)])
            self.db.library.create_index([("book_content", TEXT)]) # Text index for search
            self.db.library.create_index([("id", ASCENDING)], unique=True)

            # 3. Conversations
            self.db.conversations.create_index([("user_id", ASCENDING)])
            self.db.conversations.create_index([("created_at", DESCENDING)])
            self.db.conversations.create_index([("id", ASCENDING)], unique=True)

            # 4. Counters (for sequences compatibility)
            # Ensure counters exist for each sequence we need
            for seq_name in ['users_seq', 'library_seq', 'conversation_seq']:
                if not self.db.counters.find_one({'_id': seq_name}):
                    self.db.counters.insert_one({'_id': seq_name, 'seq': 0})

            logger.info("✅ MongoDB indexes initialized")
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")

    def get_next_sequence(self, name):
        """Get next integer ID for compatibility with Oracle sequences"""
        ret = self.db.counters.find_one_and_update(
            {'_id': name},
            {'$inc': {'seq': 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return ret['seq']

    # --- USER MANAGEMENT ---

    def get_user_by_email(self, email):
        """Fetch user by email (without password for general lookups)"""
        try:
            user = self.db.users.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}})
            if user:
                return {'id': user['id'], 'email': user['email']}
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    def get_user_with_password(self, email):
        """Fetch user by email including password hash for authentication"""
        try:
            user = self.db.users.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}})
            if user:
                return {'id': user['id'], 'email': user['email'], 'password_hash': user.get('password_hash')}
            return None
        except Exception as e:
            logger.error(f"Error getting user with password: {e}")
            return None

    def get_user_by_id(self, user_id):
        """Fetch user by ID"""
        try:
            # Assuming user_id is passed as integer
            user = self.db.users.find_one({"id": user_id})
            if user:
                return {'id': user['id'], 'email': user['email']}
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    def create_user(self, email, password_hash=None):
        """Register a new user with optional hashed password"""
        try:
            next_id = self.get_next_sequence('users_seq')
            self.db.users.insert_one({
                "id": next_id,
                "email": email,
                "password_hash": password_hash,
                "created_at": datetime.utcnow()
            })
            return next_id
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise e

    def email_exists(self, email):
        """Check if an email is already registered"""
        return self.get_user_by_email(email) is not None

    # --- BOOK MANAGEMENT ---

    def add_book(self, title, file_path, content):
        """Add or update a book in the library"""
        try:
            # Check for duplicate
            existing = self.db.library.find_one({"book_title": title})
            
            if existing:
                # Update existing
                self.db.library.update_one(
                    {"book_title": title},
                    {"$set": {
                        "book_content": content,
                        "file_path": file_path,
                        "updated_at": datetime.utcnow()
                    }}
                )
                return False  # Existing
            
            # Insert new
            next_id = self.get_next_sequence('library_seq')
            self.db.library.insert_one({
                "id": next_id, # using 'id' to map to BOOK_ID
                "book_title": title,
                "file_path": file_path,
                "book_content": content,
                "created_at": datetime.utcnow()
            })
            return True
        except Exception as e:
            logger.error(f"Error adding book: {e}")
            raise e

    def get_all_books(self):
        """Fetch all books metadata"""
        try:
            books = self.db.library.find({}, {"id": 1, "book_title": 1}).sort("book_title", 1)
            return [{'id': b['id'], 'title': b['book_title']} for b in books]
        except Exception as e:
            logger.error(f"Error getting all books: {e}")
            return []

    def search_relevant_books(self, query, limit=5, subject_filter=None):
        """Search for relevant books using manual filtering logic ported from Oracle implementation"""
        from src.ocr_utils import normalize_arabic
        import re
        
        try:
            # Normalize query
            norm_query = normalize_arabic(query.lower())
            
            # Clean and split query
            keywords = [w.strip() for w in norm_query.split() if len(w) > 2]
            if not keywords:
                keywords = [norm_query]
            
            # Main keyword for primary filter
            main_keyword = sorted(keywords, key=len, reverse=True)[0]
            
            # --- Porting the Subject Logic ---
            subjects = {
                'Arabic': ['عربي', 'لغة', 'نحو', 'صرف', 'بلاء', 'arabic', 'قصة', 'نصوص', 'اسم', 'فعل', 'حرف', 'اعراب', 'كان', 'ان ', 'مبتدأ', 'خبر'],
                'Math': ['رياضيات', 'حساب', 'جبر', 'هندسة', 'مثلثات', 'تفاضل', 'تكامل', 'احصاء', 'math', 'algebra', 'geometry', 'calc', 'shapes', 'numbers'],
                'Science': ['علوم', 'فيزياء', 'كيمياء', 'احياء', 'ذرة', 'خلية', 'كون', 'نبات', 'حيوان', 'science', 'physics', 'chemistry', 'biology', 'matter', 'energy'],
                'English': ['english', 'grammar', 'vocabulary', 'connect', 'hello', 'letters', 'alphabet'],
                'Islamic': ['دين', 'اسلام', 'قرآن', 'حديث', 'فقيه', 'صحابة', 'سيرة', 'islamic', 'religion'],
                'Social': ['دراسات', 'تاريخ', 'جغرافيا', 'مصر', 'خريطة', 'ثورة', 'مناخ', 'social', 'history', 'geography']
            }

            subject_constraints = {
                'Arabic': {
                    'include': ["arabic", "عربي"],
                    'exclude': ["math", "رياضيات", "english", "science", "social", "دراسات", "علوم", "islamic", "دين"]
                },
                'Math': {
                    'include': ["math", "رياضيات"],
                    'exclude': ["arabic", "عربي", "english", "science", "social", "دراسات", "علوم", "islamic", "دين"]
                },
                'Science': {
                    'include': ["science", "علوم"],
                    'exclude': ["math", "رياضيات", "arabic", "عربي", "english", "islamic"]
                },
                'English': {
                    'include': ["english"],
                    'exclude': ["arabic", "عربي", "math", "رياضيات", "science", "social", "islamic"]
                },
                'Social': {
                    'include': ["social", "دراسات", "geography", "history", "جغرافيا", "تاريخ"],
                    'exclude': ["math", "رياضيات", "arabic", "عربي"]
                },
                'Islamic': {
                    'include': ["islamic", "دين", "اسلام"],
                    'exclude': ["math", "رياضيات", "science", "social", "english"]
                }
            }

            detected_subjects = []
            
            # Split filter if it's multiple (comma separated)
            filters = [f.strip() for f in subject_filter.split(',')] if subject_filter else []
            
            # 1. Check if filters are specific file/book titles (PDFs)
            pdf_filters = [f for f in filters if f.lower().endswith('.pdf')]
            
            query_filter = {}
            
            if pdf_filters:
                # Filter by specific book titles
                query_filter["book_title"] = {"$in": pdf_filters}
                # And also match query content/title
                query_filter["$or"] = [
                    {"book_title": {"$regex": main_keyword, "$options": "i"}},
                    {"book_content": {"$regex": main_keyword, "$options": "i"}}
                ]
            else:
                # 2. Detect subjects
                search_terms = filters if filters else [norm_query]
                
                for term in search_terms:
                    term_norm = term.lower()
                    if any(k in term_norm for k in ['مصر', 'دراسات', 'جغرافيا', 'تاريخ', 'ثورة', 'social', 'studies']):
                        if 'Social' not in detected_subjects: detected_subjects.append('Social')
                    
                    for subj, keywords_list in subjects.items():
                        if any(k in term_norm for k in keywords_list) or subj.lower() in term_norm:
                            if subj not in detected_subjects: detected_subjects.append(subj)
                
                # Build MongoDB query based on constraints
                if detected_subjects:
                    total_inc_part = []
                    total_exc_part = []
                    
                    for subj in detected_subjects:
                        if subj in subject_constraints:
                            constraints = subject_constraints[subj]
                            total_inc_part.extend([{"book_title": {"$regex": p, "$options": "i"}} for p in constraints['include']])
                            total_exc_part.extend([{"book_title": {"$not": {"$regex": p, "$options": "i"}}} for p in constraints['exclude']])
                    
                    # Logic: (Include1 OR Include2 ...) AND (Exclude1 AND Exclude2 ...)
                    
                    and_clauses = [{"$and": total_exc_part}] if total_exc_part else []
                    
                    if total_inc_part:
                         and_clauses.append({"$or": total_inc_part})
                    
                    # Apply grade level filter
                    for term in search_terms:
                        if 'primary' in term.lower():
                            level_num = ''.join(filter(str.isdigit, term))
                            if level_num:
                                and_clauses.append({"book_title": {"$regex": f"prim{level_num}", "$options": "i"}})
                                break
                    
                    # Combine all
                    if and_clauses:
                        query_filter["$and"] = and_clauses

                    # Add the main query matching
                    # (Title LIKE q OR Content LIKE q)
                    content_match = {
                        "$or": [
                            {"book_title": {"$regex": main_keyword, "$options": "i"}},
                            {"book_content": {"$regex": main_keyword, "$options": "i"}}
                        ]
                    }
                    if "$and" in query_filter:
                        query_filter["$and"].append(content_match)
                    else:
                        query_filter = content_match

                else:
                    # FALLBACK: General Search with optional level filter
                    and_clauses = []
                    if subject_filter:
                         if 'primary' in subject_filter.lower():
                            level_num = ''.join(filter(str.isdigit, subject_filter))
                            if level_num:
                                and_clauses.append({"book_title": {"$regex": f"prim{level_num}", "$options": "i"}})
                         elif 'preparatory' in subject_filter.lower() or 'prep' in subject_filter.lower():
                             level_num = ''.join(filter(str.isdigit, subject_filter))
                             if level_num:
                                  and_clauses.append({
                                      "$or": [
                                          {"book_title": {"$regex": f"prep{level_num}", "$options": "i"}},
                                          {"book_title": {"$regex": f"prp{level_num}", "$options": "i"}}
                                      ]
                                  })

                    # Add content match
                    and_clauses.append({
                        "$or": [
                            {"book_title": {"$regex": main_keyword, "$options": "i"}},
                            {"book_content": {"$regex": main_keyword, "$options": "i"}}
                        ]
                    })
                    
                    if len(and_clauses) == 1:
                        query_filter = and_clauses[0]
                    else:
                        query_filter = {"$and": and_clauses}

            # Execute Query
            # Using find instead of aggregation for simplicity, matching the logic
            cursor = self.db.library.find(query_filter).limit(limit)
            
            results = []
            for row in cursor:
                title = row['book_title']
                content = row.get('book_content', '')
                
                if not content:
                    results.append({'title': title, 'content': ""})
                    continue

                # Snippet extraction logic (Copied from Oracle version)
                content_lower = content.lower()
                match_idx = -1
                
                for kw in keywords:
                    match_idx = content_lower.find(kw)
                    if match_idx != -1:
                        break
                
                if match_idx == -1:
                    snippet = content[:2500]
                else:
                    marker_pos = content_lower.rfind("--- page", 0, match_idx)
                    page_header = ""
                    if marker_pos != -1:
                        line_end = content.find("\n", marker_pos)
                        if line_end != -1:
                            page_header = content[marker_pos:line_end].strip()
                    
                    best_start = max(0, match_idx - 500)
                    snippet = content[best_start : best_start + 2500]
                    
                    if page_header and page_header not in snippet:
                        snippet = f"{page_header}\n... [CONVERSATION CONTEXT] ...\n{snippet}"
                    elif not page_header:
                        first_marker = content_lower.find("--- page")
                        if first_marker != -1 and first_marker > match_idx:
                             snippet = "--- Page 1 (Likely) ---\n" + snippet
                
                results.append({'title': title, 'content': snippet})
            
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    # --- CONVERSATION MANAGEMENT ---

    def save_conversation(self, user_id, assistant_type, user_message, ai_response):
        """Save a chat turn"""
        try:
            logger.info(f"Saving conversation for User {user_id}, Type: {assistant_type}")
            next_id = self.get_next_sequence('conversation_seq')
            self.db.conversations.insert_one({
                "id": next_id,
                "user_id": user_id,
                "assistant_type": assistant_type,
                "user_message": user_message,
                "ai_response": ai_response,
                "created_at": datetime.utcnow()
            })
            logger.info("Successfully saved conversation to DB")
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}", exc_info=True)

    def get_conversations(self, user_id, assistant_type='all', limit=20):
        """Fetch recent history for a user"""
        try:
            logger.info(f"Fetching history for User {user_id}, Type: {assistant_type}, Limit: {limit}")
            
            query = {"user_id": user_id}
            if assistant_type != 'all' and assistant_type is not None:
                query["assistant_type"] = assistant_type
            
            cursor = self.db.conversations.find(query).sort("created_at", DESCENDING).limit(limit)
            
            results = []
            for row in cursor:
                results.append({
                    'user_message': row['user_message'],
                    'ai_response': row['ai_response'],
                    'created_at': row['created_at'].strftime("%Y-%m-%d %H:%M") if row.get('created_at') else ""
                })
            
            logger.info(f"Found {len(results)} previous conversations")
            return results
        except Exception as e:
            logger.error(f"Error fetching conversations: {e}", exc_info=True)
            return []

    def get_user_stats(self, user_id):
        """Get user statistics for dashboard"""
        stats = {
            'conversations': 0,
            'study_hours': 0,
            'topics_mastered': 0,
            'exams_completed': 0
        }
        try:
            # 1. Total Conversations
            stats['conversations'] = self.db.conversations.count_documents({"user_id": user_id})
            
            # 2. Estimated Study Hours
            hours = float(stats['conversations']) * 0.25
            stats['study_hours'] = round(hours, 1)
            
            # 3. Topics Mastered (Count unique assistant types)
            topics = self.db.conversations.distinct("assistant_type", {"user_id": user_id})
            stats['topics_mastered'] = len(topics)
            
            # 4. Exams Completed
            stats['exams_completed'] = self.db.conversations.count_documents({
                "user_id": user_id, 
                "assistant_type": "exam"
            })
            
            return stats
        except Exception as e:
            logger.error(f"Error fetching user stats: {e}")
            return stats
