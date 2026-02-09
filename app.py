"""
SkillCode GPT - Educational AI Chatbot
Main Flask Application
"""

from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
from functools import wraps
import os
from datetime import datetime, timedelta
import secrets
from src.database import Database
from src.grok_service import GrokService
from src.book_scheduler import start_book_scheduler
from src import config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Use configured secret key to persist sessions across restarts
app.secret_key = config.SECRET_KEY

# Compatibility fix for Flask 2.3+ and Flask-Session
# Modern Flask moved this to config, but older Flask-Session still looks for the attribute
app.session_cookie_name = 'skillcode_session'

# Configure session - Flask-Session filesystem backend
app.config.update(
    SESSION_TYPE='filesystem',
    SESSION_PERMANENT=False,
    SESSION_USE_SIGNER=True,
    SESSION_KEY_PREFIX='skillcode:',
    PERMANENT_SESSION_LIFETIME=timedelta(days=7)
)
# Explicitly set the session cookie name if needed via SESSION_COOKIE_NAME
app.config['SESSION_COOKIE_NAME'] = 'skillcode_session'
Session(app)

# Initialize services globally but lazily
db = None
grok = None

def get_db():
    global db
    if db is None:
        try:
            from src.database import Database
            db = Database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            # Return a dummy or handle gracefully to prevent crash
            return None
    return db

# Start book auto-upload scheduler (once)
with app.app_context():
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        try:
            _db = get_db()
            if _db:
                start_book_scheduler(_db)
            grok = get_grok()
        except Exception as e:
            logger.warning(f"Startup task failed: {e}")

@app.context_processor
def inject_user():
    """Make user object available in all templates"""
    if 'user_id' in session:
        try:
            user = get_db().get_user_by_id(session['user_id'])
            return dict(user=user)
        except:
            pass
    return dict(user=None)

# === AUTHENTICATION ===

from werkzeug.security import generate_password_hash, check_password_hash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Redirect to dashboard if logged in, else to login"""
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Email and password based login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or '@' not in email:
            return render_template('login.html', error='Invalid email format'), 400
        
        if not password:
            return render_template('login.html', error='Password is required'), 400
        
        try:
            # Check if user exists (with password hash)
            user = get_db().get_user_with_password(email)
            
            if not user:
                return render_template('login.html', error='Email not found. Please sign up.'), 401

            # Verify password
            if not check_password_hash(user['password_hash'], password):
                return render_template('login.html', error='Incorrect password.'), 401
            
            # Set session
            session['user_id'] = user['id']
            session['email'] = user['email']
            session.permanent = True
            
            logger.info(f"User logged in: {email}")
            return redirect('/dashboard')
        except Exception as e:
            logger.error(f"Login error: {e}")
            return render_template('login.html', error='Server error. Please try again.'), 500
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Email and password based registration"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Validation
        if not email or '@' not in email:
            return render_template('signup.html', error='Invalid email format'), 400

        if len(password) < 6:
            return render_template('signup.html', error='Password must be at least 6 characters long'), 400
        
        try:
            # Check if email already exists
            if get_db().email_exists(email):
                return render_template('signup.html', error='This email is already registered. Please login.'), 400
            
            # Hash password and create user
            password_hash = generate_password_hash(password)
            user_id = get_db().create_user(email, password_hash)
            
            # Auto-login after signup
            session['user_id'] = user_id
            session['email'] = email
            session.permanent = True
            
            logger.info(f"New user registered: {email}")
            return redirect('/dashboard')
        except Exception as e:
            logger.error(f"Signup error: {e}")
            return render_template('signup.html', error='Server error. Please try again.'), 500
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect('/login')

# === DASHBOARD ===

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    try:
        user_id = session.get('user_id')
        stats = get_db().get_user_stats(user_id)
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render_template('error.html', error='Failed to load dashboard'), 500

# === ASSISTANT PAGES ===

@app.route('/general-assistant')
@login_required
def general_assistant():
    """General Purpose Assistant"""
    return render_template('general_assistant.html')

@app.route('/homework-assistant')
@login_required
def homework_assistant():
    """Homework Solver with Customization"""
    return render_template('homework_assistant.html')

@app.route('/exam-preparation')
@login_required
def exam_preparation():
    """Exam & Quiz Generator"""
    return render_template('exam_preparation.html')

@app.route('/study-planner')
@login_required
def study_planner():
    """Curriculum & Study Scheduler"""
    return render_template('study_planner.html')

@app.route('/tutor-assistant')
@login_required
def tutor_assistant():
    """Personal Tutor with Lesson Refs"""
    return render_template('tutor_assistant.html')

@app.route('/mind-mapper')
@login_required
def mind_mapper():
    """Visual Concept Mapping"""
    return render_template('mind_mapper.html')

# === API ENDPOINTS ===

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """Handle chat requests from all assistants"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        assistant_type = data.get('assistant_type', 'general')
        custom_params = data.get('params', {})
        
        if not message:
            return jsonify({'error': 'Empty message'}), 400
        
        logger.info(f"Chat request - User: {session['user_id']}, Type: {assistant_type}, Message: {message[:50]}")
        
        # Get recent chat history for this user (fetch early for context)
        chat_history = get_db().get_conversations(user_id=session['user_id'], assistant_type=assistant_type, limit=config.CONVERSATION_LIMIT)
        # Reverse to get chronological order (oldest first)
        chat_history.reverse()

        # Contextual Search: If the message is short or a follow-up, use previous context for search
        search_query = message
        follow_up_phrases = ['ابحث اكتر', 'زيدني', 'اكمل', 'توسع', 'تفاصيل اكثر', 'more', 'continue', 'tell me more', 'expand', 'details']
        if any(p in message.lower() for p in follow_up_phrases) or len(message.split()) <= 2:
            if chat_history:
                last_msg = chat_history[-1]['user_message']
                # Prepend previous message to current search to keep context in DB search
                search_query = f"{last_msg} {message}"
                logger.info(f"Contextual follow-up search: '{search_query}'")

        # Get relevant books from database
        subject_filter = custom_params.get('subject')
        books_context = get_db().search_relevant_books(search_query, limit=config.MAX_BOOKS_PER_SEARCH, subject_filter=subject_filter)
        logger.info(f"Found {len(books_context)} relevant books")
        
        # Get list of all available books (titles only) for context
        all_books = get_db().get_all_books()
        available_books_titles = [b['title'] for b in all_books]
        
        # Get response from Grok API
        response = get_grok().get_response(
            message=message,
            assistant_type=assistant_type,
            books_context=books_context,
            custom_params=custom_params,
            available_books_titles=available_books_titles,
            chat_history=chat_history
        )
        
        logger.info(f"Got response from Grok: {response[:100]}")
        
        # Save conversation
        get_db().save_conversation(
            user_id=session['user_id'],
            assistant_type=assistant_type,
            user_message=message,
            ai_response=response
        )
        
        return jsonify({
            'success': True,
            'response': response,
            'sources': [b['title'] for b in books_context]
        })
    
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-exam', methods=['POST'])
@login_required
def generate_exam():
    """Generate exam/quiz based on parameters"""
    try:
        data = request.get_json()
        params = {
            'num_questions': data.get('num_questions', 10),
            'difficulty': data.get('difficulty', 'medium'),
            'question_type': data.get('question_type', 'mixed'),
            'subject': data.get('subject', ''),
            'topic': data.get('topic', '')
        }
        
        subject_filter = params['subject']
        books_context = get_db().search_relevant_books(params['subject'], limit=3, subject_filter=subject_filter)
        
        exam = get_grok().generate_exam(params, books_context)
        
        return jsonify({
            'success': True,
            'exam': exam
        })
    
    except Exception as e:
        logger.error(f"Exam generation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-study-plan', methods=['POST'])
@login_required
def generate_study_plan():
    """Generate personalized study plan"""
    try:
        data = request.get_json()
        params = {
            'subject': data.get('subject', ''),
            'daily_hours': data.get('daily_hours', 2),
            'sleep_time': data.get('sleep_time', '8'),
            'duration_days': data.get('duration_days', 30)
        }
        
        subject_filter = params['subject']
        books_context = get_db().search_relevant_books(params['subject'], limit=3, subject_filter=subject_filter)
        
        plan = get_grok().generate_study_plan(params, books_context)
        
        return jsonify({
            'success': True,
            'plan': plan
        })
    
    except Exception as e:
        logger.error(f"Study plan error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-books', methods=['GET'])
@login_required
def get_books():
    """Get list of available books"""
    try:
        books = get_db().get_all_books()
        return jsonify({
            'success': True,
            'books': books
        })
    except Exception as e:
        logger.error(f"Get books error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation-history', methods=['GET'])
@login_required
def conversation_history():
    """Get user's conversation history"""
    try:
        assistant_type = request.args.get('type', 'all')
        limit = request.args.get('limit', 100, type=int)
        
        conversations = get_db().get_conversations(
            user_id=session['user_id'],
            assistant_type=assistant_type,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'conversations': conversations
        })
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({'error': str(e)}), 500

# === ERROR HANDLERS ===

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('error.html', error='Server error'), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, host='0.0.0.0', port=5000)
