# SkillCode GPT - Installation and Setup Guide

## Project Structure
```
chatbot with oracle/
├── app.py                 # Main Flask application
├── database.py           # Oracle database operations
├── grok_service.py       # Grok API integration
├── book_scheduler.py     # Automatic book upload scheduler
├── upload_manager.py     # Original book upload script
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── login.html       # Login page
│   ├── dashboard.html   # Main dashboard
│   ├── general_assistant.html
│   ├── homework_assistant.html
│   ├── exam_preparation.html
│   ├── study_planner.html
│   ├── tutor_assistant.html
│   ├── mind_mapper.html
│   └── error.html
└── static/              # Static files
    ├── css/
    │   ├── style.css    # Global styles
    │   └── assistant.css # Assistant page styles
    └── js/
        └── assistant.js  # Chat functionality
```

## Installation Steps

### 1. Prerequisites
- Python 3.8+ installed
- MongoDB installed (Community Server)
- Git (optional)

### 2. Clone/Setup Project
```bash
cd d:\Work\chatbot with oracle
```

### 3. Create Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Database
The application now uses **SQLite** (local file) and **FAISS** (local vector store).
No external database installation is required!

Just ensure `skillcode.db` and the `vector_store/` folder are preserved if you redeploy.

### 6. Create Books Folder
```bash
mkdir D:\Work\books
```
Add your PDF files to this folder.

### 7. Data Migration (Optional)
If you are migrating from MongoDB/Oracle, run:
```bash
python migrate_mongo_to_vector.py
```

### 8. Run the Application
```bash
python app.py
```

Access the app at: `http://localhost:5000`

## Features Overview

### 🔐 Email Authentication
- No password required
- Auto-creates user on first login
- Session management

### 📚 6 Intelligent Assistants
1. **General Assistant** - Educational Q&A
2. **Homework Assistant** - Step-by-step problem solving
3. **Exam Preparation** - Practice exam generation
4. **Study Planner** - Adaptive study schedules
5. **Tutor Assistant** - Personal tutoring with references
6. **Mind Mapper** - Visual concept mapping

### 📖 Smart Database Integration
- Automatic daily book uploads at 2:00 AM
- Full-text search of PDF content
- Session persistence

### 🤖 Grok API Integration
- Advanced AI responses
- Customizable parameters
- Source citations

## API Endpoints

### Authentication
- `GET/POST /login` - Email-based login
- `GET /logout` - User logout

### Main Pages
- `GET /` - Home redirect
- `GET /dashboard` - Main dashboard
- `GET /general-assistant` - General assistant
- `GET /homework-assistant` - Homework solver
- `GET /exam-preparation` - Exam prep
- `GET /study-planner` - Study planner
- `GET /tutor-assistant` - Tutor
- `GET /mind-mapper` - Mind mapper

### API Calls
- `POST /api/chat` - Send message to AI
- `POST /api/generate-exam` - Generate exam questions
- `POST /api/generate-study-plan` - Create study plan
- `GET /api/get-books` - Get available books
- `GET /api/conversation-history` - Get chat history

## Customization

### Change Schedule
Edit `book_scheduler.py`:
```python
scheduler.add_job(
    ...
    hour=2,  # Change hour here
    minute=0,
    ...
)
```

### Change Books Folder
Edit `config.py`:
```python
BOOKS_FOLDER = r"your_path_here"
```

### Change API Key
Edit `config.py`:
```python
GROK_API_KEY = "your_key_here"
```

## Troubleshooting

### Oracle Connection Error
- Check Oracle service is running
- Verify credentials in config.py
- Ensure Instant Client is installed

### Book Upload Not Working
- Check D:\Work\books folder exists
- Verify PDF files are readable
- Check scheduler is running (check app logs)

### Chat Not Responding
- Verify Grok API key is valid
- Check internet connection
- Review app logs for errors

## Support & Maintenance

### View Logs
Logs are printed to console when running with `debug=True`

### Update Books
Simply add PDFs to D:\Work\books folder, they'll upload automatically

### Reset Database
Delete all entries with Oracle SQL or restart database

## Production Deployment

Before deploying:
1. Change `DEBUG = False` in config.py
2. Generate secure `SECRET_KEY`
3. Set up proper environment variables
4. Use production WSGI server (Gunicorn, etc.)
5. Configure HTTPS
6. Set up proper logging

## License
Created by SkillCode Team

## Version History
- v1.0.0 - Initial release with 6 assistants
