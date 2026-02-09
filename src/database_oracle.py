import oracledb
import logging
import os
from datetime import datetime
from src.config import DB_USER, DB_PASSWORD, DB_DSN, DB_CLIENT_DIR

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        """Initialize Oracle connection and ensure tables exist"""
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.dsn = DB_DSN
        self.client_dir = DB_CLIENT_DIR
        
        try:
            # Initialize Oracle client if lib_dir is provided
            if self.client_dir and os.path.exists(self.client_dir):
                oracledb.init_oracle_client(lib_dir=self.client_dir)
            
            # Test connection
            self.test_connection()
            # Initialize schema
            self.init_db()
        except Exception as e:
            logger.error(f"Database initialization error: {e}")

    def get_connection(self):
        """Get a fresh connection to Oracle"""
        return oracledb.connect(
            user=self.user,
            password=self.password,
            dsn=self.dsn
        )

    def test_connection(self):
        """Simple test to verify connection"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT sysdate FROM dual")
            logger.info("✅ Oracle Connection Verified")
        finally:
            conn.close()

    def init_db(self):
        """Ensure all required tables and sequences exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # 1. MY_LIBRARY table (Books)
            try:
                cursor.execute("SELECT 1 FROM MY_LIBRARY WHERE ROWNUM = 1")
                logger.info("✅ Table MY_LIBRARY exists")
            except oracledb.DatabaseError:
                logger.info("Creating table MY_LIBRARY...")
                cursor.execute("""
                    CREATE TABLE MY_LIBRARY (
                        BOOK_ID NUMBER PRIMARY KEY,
                        BOOK_TITLE VARCHAR2(500),
                        FILE_PATH VARCHAR2(1000),
                        BOOK_CONTENT CLOB,
                        CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Create sequence for library
                try:
                    cursor.execute("CREATE SEQUENCE library_seq START WITH 1 INCREMENT BY 1")
                except: pass

            # 2. USERS table
            try:
                cursor.execute("SELECT 1 FROM USERS WHERE ROWNUM = 1")
                logger.info("✅ Table USERS exists")
                # Check if PASSWORD_HASH column exists, add if not
                try:
                    cursor.execute("SELECT PASSWORD_HASH FROM USERS WHERE ROWNUM = 1")
                except oracledb.DatabaseError:
                    logger.info("Adding PASSWORD_HASH column to USERS table...")
                    cursor.execute("ALTER TABLE USERS ADD PASSWORD_HASH VARCHAR2(255)")
                    conn.commit()
            except oracledb.DatabaseError:
                logger.info("Creating table USERS...")
                cursor.execute("""
                    CREATE TABLE USERS (
                        ID NUMBER PRIMARY KEY,
                        EMAIL VARCHAR2(255) UNIQUE,
                        PASSWORD_HASH VARCHAR2(255),
                        CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Create sequence for users
                try:
                    cursor.execute("CREATE SEQUENCE users_seq START WITH 1 INCREMENT BY 1")
                except: pass

            # 3. CONVERSATIONS table
            try:
                cursor.execute("SELECT 1 FROM CONVERSATIONS WHERE ROWNUM = 1")
                logger.info("✅ Table CONVERSATIONS exists")
            except oracledb.DatabaseError:
                logger.info("Creating table CONVERSATIONS...")
                cursor.execute("""
                    CREATE TABLE CONVERSATIONS (
                        ID NUMBER PRIMARY KEY,
                        USER_ID NUMBER REFERENCES USERS(ID),
                        ASSISTANT_TYPE VARCHAR2(50),
                        USER_MESSAGE CLOB,
                        AI_RESPONSE CLOB,
                        CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Create sequence for conversations
                try:
                    cursor.execute("CREATE SEQUENCE CONVERSATION_SEQ START WITH 1 INCREMENT BY 1")
                except: pass

            conn.commit()
            logger.info("✅ Database schema initialized")
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")
        finally:
            conn.close()

    # --- USER MANAGEMENT ---

    def get_user_by_email(self, email):
        """Fetch user by email (without password for general lookups)"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ID, EMAIL FROM USERS WHERE LOWER(EMAIL) = LOWER(:1)", (email,))
            row = cursor.fetchone()
            if row:
                return {'id': row[0], 'email': row[1]}
            return None
        finally:
            conn.close()

    def get_user_with_password(self, email):
        """Fetch user by email including password hash for authentication"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ID, EMAIL, PASSWORD_HASH FROM USERS WHERE LOWER(EMAIL) = LOWER(:1)", (email,))
            row = cursor.fetchone()
            if row:
                return {'id': row[0], 'email': row[1], 'password_hash': row[2]}
            return None
        finally:
            conn.close()

    def get_user_by_id(self, user_id):
        """Fetch user by ID"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ID, EMAIL FROM USERS WHERE ID = :1", (user_id,))
            row = cursor.fetchone()
            if row:
                return {'id': row[0], 'email': row[1]}
            return None
        finally:
            conn.close()

    def create_user(self, email, password_hash=None):
        """Register a new user with optional hashed password"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            next_id = cursor.execute("SELECT users_seq.NEXTVAL FROM dual").fetchone()[0]
            cursor.execute(
                "INSERT INTO USERS (ID, EMAIL, PASSWORD_HASH) VALUES (:1, :2, :3)",
                (next_id, email, password_hash)
            )
            conn.commit()
            return next_id
        finally:
            conn.close()

    def email_exists(self, email):
        """Check if an email is already registered"""
        return self.get_user_by_email(email) is not None

    # --- BOOK MANAGEMENT ---

    def add_book(self, title, file_path, content):
        """Add or update a book in the library"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check for duplicate
            cursor.execute("SELECT count(*) FROM MY_LIBRARY WHERE BOOK_TITLE = :1", (title,))
            if cursor.fetchone()[0] > 0:
                # Update existing
                text_clob = cursor.var(oracledb.DB_TYPE_CLOB)
                text_clob.setvalue(0, content)
                cursor.execute(
                    "UPDATE MY_LIBRARY SET BOOK_CONTENT = :1, FILE_PATH = :2 WHERE BOOK_TITLE = :3",
                    (text_clob, file_path, title)
                )
                conn.commit()
                return False  # Existing
            
            # Insert new
            text_clob = cursor.var(oracledb.DB_TYPE_CLOB)
            text_clob.setvalue(0, content)
            cursor.execute(
                "INSERT INTO MY_LIBRARY (BOOK_ID, BOOK_TITLE, FILE_PATH, BOOK_CONTENT) VALUES (library_seq.NEXTVAL, :1, :2, :3)",
                (title, file_path, text_clob)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def get_all_books(self):
        """Fetch all books metadata"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT BOOK_ID, BOOK_TITLE FROM MY_LIBRARY ORDER BY BOOK_TITLE")
            return [{'id': row[0], 'title': row[1]} for row in cursor.fetchall()]
        finally:
            conn.close()

    def search_relevant_books(self, query, limit=5, subject_filter=None):
        """Search for relevant books using smart keyword matching and snippet extraction"""
        from src.ocr_utils import normalize_arabic
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Normalize query to match ingestion (important for Arabic)
            norm_query = normalize_arabic(query.lower())
            
            # Clean and split query into keywords (ignore very short words)
            keywords = [w.strip() for w in norm_query.split() if len(w) > 2]
            if not keywords:
                keywords = [norm_query]
            
            # Use the longest keyword for the SQL LIKE filter
            main_keyword = sorted(keywords, key=len, reverse=True)[0]
            sql_filter = f"%{main_keyword}%"
            
            # Define subject keywords - EXHAUSTIVE LIST
            subjects = {
                'Arabic': ['عربي', 'لغة', 'نحو', 'صرف', 'بلاء', 'arabic', 'قصة', 'نصوص', 'اسم', 'فعل', 'حرف', 'اعراب', 'كان', 'ان ', 'مبتدأ', 'خبر'],
                'Math': ['رياضيات', 'حساب', 'جبر', 'هندسة', 'مثلثات', 'تفاضل', 'تكامل', 'احصاء', 'math', 'algebra', 'geometry', 'calc', 'shapes', 'numbers'],
                'Science': ['علوم', 'فيزياء', 'كيمياء', 'احياء', 'ذرة', 'خلية', 'كون', 'نبات', 'حيوان', 'science', 'physics', 'chemistry', 'biology', 'matter', 'energy'],
                'English': ['english', 'grammar', 'vocabulary', 'connect', 'hello', 'letters', 'alphabet'],
                'Islamic': ['دين', 'اسلام', 'قرآن', 'حديث', 'فقيه', 'صحابة', 'سيرة', 'islamic', 'religion'],
                'Social': ['دراسات', 'تاريخ', 'جغرافيا', 'مصر', 'خريطة', 'ثورة', 'مناخ', 'social', 'history', 'geography']
            }

            # Map detected subject to mandatory title patterns and exclusion patterns
            subject_constraints = {
                'Arabic': {
                    'include': ["%arabic%", "%عربي%"],
                    'exclude': ["%math%", "%رياضيات%", "%english%", "%science%", "%social%", "%دراسات%", "%علوم%", "%islamic%", "%دين%"]
                },
                'Math': {
                    'include': ["%math%", "%رياضيات%"],
                    'exclude': ["%arabic%", "%عربي%", "%english%", "%science%", "%social%", "%دراسات%", "%علوم%", "%islamic%", "%دين%"]
                },
                'Science': {
                    'include': ["%science%", "%علوم%"],
                    'exclude': ["%math%", "%رياضيات%", "%arabic%", "%عربي%", "%english%", "%islamic%"]
                },
                'English': {
                    'include': ["%english%"],
                    'exclude': ["%arabic%", "%عربي%", "%math%", "%رياضيات%", "%science%", "%social%", "%islamic%"]
                },
                'Social': {
                    'include': ["%social%", "%دراسات%", "%geography%", "%history%", "%جغرافيا%", "%تاريخ%"],
                    'exclude': ["%math%", "%رياضيات%", "%arabic%", "%عربي%"]
                },
                'Islamic': {
                    'include': ["%islamic%", "%دين%", "%اسلام%"],
                    'exclude': ["%math%", "%رياضيات%", "%science%", "%social%", "%english%"]
                }
            }

            # Detect subject priority from query or filter
            detected_subjects = []
            
            # Split filter if it's multiple (comma separated)
            filters = [f.strip() for f in subject_filter.split(',')] if subject_filter else []
            
            # 1. Check if filters are specific file/book titles
            pdf_filters = [f for f in filters if f.lower().endswith('.pdf')]
            
            if pdf_filters:
                # Handle specific books search (potentially multiple)
                placeholders = ', '.join([f':f{i}' for i in range(len(pdf_filters))])
                params = {f'f{i}': f for i, f in enumerate(pdf_filters)}
                params['q'] = sql_filter
                params['l'] = limit
                
                sql = f"""
                    SELECT * FROM (
                        SELECT BOOK_TITLE, BOOK_CONTENT
                        FROM MY_LIBRARY 
                        WHERE BOOK_TITLE IN ({placeholders})
                          AND (LOWER(BOOK_TITLE) LIKE :q OR LOWER(BOOK_CONTENT) LIKE :q OR :q IS NULL)
                    ) WHERE ROWNUM <= :l
                """
                cursor.execute(sql, params)
            else:
                # 2. Detect subjects from multiple filters or query
                search_terms = filters if filters else [norm_query]
                
                for term in search_terms:
                    term_norm = term.lower()
                    if any(k in term_norm for k in ['مصر', 'دراسات', 'جغرافيا', 'تاريخ', 'ثورة', 'social', 'studies']):
                        if 'Social' not in detected_subjects: detected_subjects.append('Social')
                    
                    for subj, keywords_list in subjects.items():
                        if any(k in term_norm for k in keywords_list) or subj.lower() in term_norm:
                            if subj not in detected_subjects: detected_subjects.append(subj)
                
                # Build SQL based on strict mutations (Aggregated for all detected subjects)
                if detected_subjects:
                    total_inc_part = []
                    total_exc_part = []
                    
                    for subj in detected_subjects:
                        if subj in subject_constraints:
                            constraints = subject_constraints[subj]
                            total_inc_part.extend([f"LOWER(BOOK_TITLE) LIKE '{p}'" for p in constraints['include']])
                            total_exc_part.extend([f"LOWER(BOOK_TITLE) NOT LIKE '{p}'" for p in constraints['exclude']])
                    
                    inc_clause = "(" + " OR ".join(total_inc_part) + ")" if total_inc_part else "(1=1)"
                    exc_clause = "(" + " AND ".join(total_exc_part) + ")" if total_exc_part else "(1=1)"
                    
                    title_filter = f"{inc_clause} AND {exc_clause}"
                    
                    # Apply grade level filter if present in any filter term
                    level_clause = ""
                    for term in search_terms:
                        if 'primary' in term.lower():
                            level_num = ''.join(filter(str.isdigit, term))
                            if level_num:
                                level_clause = f" AND LOWER(BOOK_TITLE) LIKE '%prim{level_num}%'"
                                break
                    
                    title_filter += level_clause

                    sql = f"""
                        SELECT * FROM (
                            SELECT BOOK_TITLE, BOOK_CONTENT
                            FROM MY_LIBRARY 
                            WHERE ({title_filter})
                              AND (LOWER(BOOK_TITLE) LIKE :q 
                               OR LOWER(BOOK_CONTENT) LIKE :q)
                            ORDER BY 
                                CASE WHEN LOWER(BOOK_TITLE) LIKE :q THEN 0 ELSE 1 END,
                                BOOK_TITLE DESC
                        ) WHERE ROWNUM <= :l
                    """
                    cursor.execute(sql, q=sql_filter, l=limit)
                    
                else:
                    # FALLBACK: General Search with optional level filter
                    title_part = "1=1"
                    if subject_filter:
                        # Extract level if present
                        if 'primary' in subject_filter.lower():
                            level_num = ''.join(filter(str.isdigit, subject_filter))
                            if level_num:
                                title_part = f"LOWER(BOOK_TITLE) LIKE '%prim{level_num}%'"
                        elif 'preparatory' in subject_filter.lower() or 'prep' in subject_filter.lower():
                            level_num = ''.join(filter(str.isdigit, subject_filter))
                            if level_num:
                                title_part = f"LOWER(BOOK_TITLE) LIKE '%prep{level_num}%' OR LOWER(BOOK_TITLE) LIKE '%prp{level_num}%'"

                    sql = f"""
                        SELECT * FROM (
                            SELECT BOOK_TITLE, BOOK_CONTENT
                            FROM MY_LIBRARY 
                            WHERE ({title_part})
                              AND (LOWER(BOOK_TITLE) LIKE :q 
                               OR LOWER(BOOK_CONTENT) LIKE :q)
                        ) WHERE ROWNUM <= :l
                    """
                    cursor.execute(sql, q=sql_filter, l=limit)
            
            results = []
            for row in cursor.fetchall():
                title = row[0]
                # Read CLOB efficiently
                content_clob = row[1]
                content = content_clob.read() if hasattr(content_clob, 'read') else str(content_clob)
                
                if not content:
                    results.append({'title': title, 'content': ""})
                    continue

                # Find the best snippet and identify the page
                content_lower = content.lower()
                match_idx = -1
                
                # Look for the first keyword match in the content
                for kw in keywords:
                    match_idx = content_lower.find(kw)
                    if match_idx != -1:
                        break
                
                if match_idx == -1:
                    # Fallback to beginning if no match
                    snippet = content[:2500]
                else:
                    # 1. Find the nearest preceding page marker to ensure accurate citation
                    marker_pos = content_lower.rfind("--- page", 0, match_idx)
                    page_header = ""
                    if marker_pos != -1:
                        # Extract the full page marker line (e.g., --- Page 5 ---)
                        line_end = content.find("\n", marker_pos)
                        if line_end != -1:
                            page_header = content[marker_pos:line_end].strip()
                    
                    # 2. Take a 2500 char window from the match
                    best_start = max(0, match_idx - 500)
                    snippet = content[best_start : best_start + 2500]
                    
                    # 3. Prepend page header if found and not already in snippet
                    if page_header and page_header not in snippet:
                        snippet = f"{page_header}\n... [CONVERSATION CONTEXT] ...\n{snippet}"
                    elif not page_header:
                        # If no marker before match, check if there's any marker at all
                        first_marker = content_lower.find("--- page")
                        if first_marker != -1 and first_marker > match_idx:
                             # We are before Page 1? Unlikely, but possible
                             snippet = "--- Page 1 (Likely) ---\n" + snippet
                
                results.append({'title': title, 'content': snippet})
            
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
        finally:
            conn.close()

    # --- CONVERSATION MANAGEMENT ---

    def save_conversation(self, user_id, assistant_type, user_message, ai_response):
        """Save a chat turn"""
        conn = None
        try:
            logger.info(f"Saving conversation for User {user_id}, Type: {assistant_type}")
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Using simple parameters for better compatibility with some Oracle versions
            # CLOBs can be passed as strings directly in most modern oracledb versions
            cursor.execute(
                """INSERT INTO CONVERSATIONS (ID, USER_ID, ASSISTANT_TYPE, USER_MESSAGE, AI_RESPONSE) 
                   VALUES (CONVERSATION_SEQ.NEXTVAL, :u, :a, :m, :r)""",
                u=user_id, a=assistant_type, m=user_message, r=ai_response
            )
            conn.commit()
            logger.info("Successfully saved conversation to DB")
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}", exc_info=True)
        finally:
            if conn:
                conn.close()

    def get_conversations(self, user_id, assistant_type='all', limit=20):
        """Fetch recent history for a user (Max compatibility)"""
        conn = None
        try:
            logger.info(f"Fetching history for User {user_id}, Type: {assistant_type}, Limit: {limit}")
            conn = self.get_connection()
            cursor = conn.cursor()
            
            sql_inner = "SELECT USER_MESSAGE, AI_RESPONSE, TO_CHAR(CREATED_AT, 'YYYY-MM-DD HH24:MI') FROM CONVERSATIONS WHERE USER_ID = :u"
            params = {'u': user_id, 'l': limit}
            
            if assistant_type != 'all' and assistant_type is not None:
                sql_inner += " AND ASSISTANT_TYPE = :a"
                params['a'] = assistant_type
            
            sql_inner += " ORDER BY CREATED_AT DESC"
            sql = f"SELECT * FROM ({sql_inner}) WHERE ROWNUM <= :l"
            
            cursor.execute(sql, **params)
            results = []
            for row in cursor.fetchall():
                user_msg = row[0].read() if hasattr(row[0], 'read') else str(row[0])
                ai_resp = row[1].read() if hasattr(row[1], 'read') else str(row[1])
                created_at = row[2]
                results.append({
                    'user_message': user_msg,
                    'ai_response': ai_resp,
                    'created_at': created_at
                })
            
            logger.info(f"Found {len(results)} previous conversations")
            return results
        except Exception as e:
            logger.error(f"Error fetching conversations: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()

    def get_user_stats(self, user_id):
        """Get user statistics for dashboard"""
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
            cursor.execute("SELECT COUNT(*) FROM CONVERSATIONS WHERE USER_ID = :1", (user_id,))
            res = cursor.fetchone()
            if res:
                stats['conversations'] = res[0]
            
            # 2. Estimated Study Hours (Assume 15 mins per conversation)
            # Use float arithmetic for precision
            hours = float(stats['conversations']) * 0.25
            stats['study_hours'] = round(hours, 1)
            
            # 3. Topics Mastered (Count unique assistant types used)
            cursor.execute("SELECT COUNT(DISTINCT ASSISTANT_TYPE) FROM CONVERSATIONS WHERE USER_ID = :1", (user_id,))
            res = cursor.fetchone()
            if res:
                stats['topics_mastered'] = res[0]
            
            # 4. Exams Completed (Count 'exam' type conversations)
            cursor.execute("SELECT COUNT(*) FROM CONVERSATIONS WHERE ASSISTANT_TYPE = 'exam' AND USER_ID = :1", (user_id,))
            res = cursor.fetchone()
            if res:
                stats['exams_completed'] = res[0]
            
            return stats
        except Exception as e:
            logger.error(f"Error fetching user stats: {e}")
            return stats
        finally:
            if conn:
                conn.close()
