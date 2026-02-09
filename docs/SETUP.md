# SkillCode GPT - Complete Installation Guide

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Features](#features)
6. [API Documentation](#api-documentation)
7. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Software
- **Python**: 3.8 or higher
- **Oracle Database**: Oracle XE 11g or higher
- **Oracle Instant Client**: 23.0 or compatible version
- **Browser**: Chrome, Firefox, Safari, or Edge (latest versions)

### Hardware
- **RAM**: Minimum 2GB (4GB recommended)
- **Disk Space**: 500MB minimum
- **Internet**: Required for Grok API

### Ports
- **Port 5000**: Flask development server (configurable)

---

## Installation

### Step 1: Clone/Extract Project
```bash
# Navigate to your project directory
cd d:\Work\chatbot with oracle
```

### Step 2: Set Up Python Environment

#### On Windows:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### On Linux/Mac:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Verify Oracle Installation
```bash
# Test Oracle connection
python -c "import oracledb; print('Oracle client OK')"
```

### Step 4: Create Books Directory
```bash
# Windows
mkdir D:\Work\books

# Linux/Mac
mkdir -p /Users/YourName/Work/books
```

---

## Configuration

### 1. Update Database Credentials

Edit [config.py](config.py):
```python
# Database Configuration
DB_USER = "your_oracle_username"        # Usually "help_me" for local setup
DB_PASSWORD = "your_oracle_password"    # Your Oracle password
DB_DSN = "localhost:1521/xe"            # Your Oracle DSN
DB_CLIENT_DIR = r"C:\oraclexe\app\oracle\instantclient_23_0"  # Oracle client path
```

### 2. Verify Grok API Key

Edit [config.py](config.py):
```python
# Grok API Configuration
GROK_API_KEY = "[YOUR_GROK_API_KEY]"
```

### 3. Configure Books Folder

Edit [config.py](config.py):
```python
# Book Upload Configuration
BOOKS_FOLDER = r"D:\Work\books"  # Change this path if needed
```

### 4. Schedule Settings

Edit [book_scheduler.py](book_scheduler.py):
```python
# Schedule daily book upload at 2:00 AM
scheduler.add_job(
    func=upload_books,
    args=(db,),
    trigger="cron",
    hour=2,          # Change this to your preferred hour (0-23)
    minute=0,        # Change this to your preferred minute (0-59)
    id='book_upload_job',
    name='Daily Book Upload',
    replace_existing=True
)
```

---

## Running the Application

### Quick Start (Windows)
```bash
# Double-click run.bat
# or from command line:
run.bat
```

### Quick Start (Linux/Mac)
```bash
# Make script executable
chmod +x run.sh

# Run the script
./run.sh
```

### Manual Start
```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Run the application
python app.py
```

### Access the Application
Open your browser and go to:
```
http://localhost:5000
```

---

## Features

### 🔐 Authentication System
- **Email-based login** (no password required)
- **Auto user creation** on first login
- **Session management** with 7-day expiration
- **Secure session storage**

### 📚 Six Intelligent Assistants

#### 1. General Assistant
- Answer any educational question
- Database-aware responses
- Source citations
- Instant feedback

#### 2. Homework Assistant
- Step-by-step problem solving
- Customizable parameters:
  - Education level (Elementary, Middle, High School, College)
  - Subject selection
  - Tone (Formal, Casual, Friendly)
  - Detail level (Brief, Medium, Detailed)

#### 3. Exam Preparation
- Auto-generate practice exams
- Customizable questions:
  - Number of questions (1-100)
  - Difficulty level
  - Question types (MCQ, Short Answer, Essay, Mixed)
  - Subject/Topic selection
- Answer keys included
- Difficulty ratings

#### 4. Study Planner
- Personalized study schedules
- Adaptive learning paths
- Parameters:
  - Subject selection
  - Daily study hours
  - Sleep schedule
  - Study duration
- Day-by-day breakdown
- Review checkpoints

#### 5. Tutor Assistant
- Virtual personal tutor
- Concept explanations
- Reference to source materials
- Guidance on next topics
- Encouraging teaching style

#### 6. Mind Mapper
- Visual concept mapping
- Topic summarization
- Hierarchical organization
- Connection visualization
- Study aid generation

### 📖 Database Features
- **Automatic Daily Upload**: PDFs from folder upload at 2:00 AM
- **Full-Text Search**: Content-aware book recommendations
- **User Sessions**: Persistent conversation history
- **Oracle Integration**: Secure data storage

### 🤖 AI Integration
- **Grok API**: Advanced language model
- **Context-Aware**: Uses your study materials
- **Customizable Responses**: Adjust complexity and tone
- **Real-time Processing**: Instant responses

### 📊 User Experience
- **Professional UI**: Modern, clean design
- **Responsive Layout**: Works on desktop & tablets
- **Dark/Light Mode Ready**: Aesthetic consistency
- **Intuitive Navigation**: Easy to learn

---

## API Documentation

### Authentication Endpoints

#### Login
```
POST /login
Content-Type: application/x-www-form-urlencoded

Parameters:
- email (required): User's email address

Response: Redirect to dashboard or login page with error
```

#### Logout
```
GET /logout

Response: Redirect to login page
```

### Page Endpoints

#### Dashboard
```
GET /dashboard
Auth: Required (email session)

Response: HTML dashboard page
```

#### Assistant Pages
```
GET /general-assistant
GET /homework-assistant
GET /exam-preparation
GET /study-planner
GET /tutor-assistant
GET /mind-mapper

Auth: Required (email session)
Response: HTML assistant page
```

### API Endpoints

#### Send Chat Message
```
POST /api/chat
Auth: Required
Content-Type: application/json

Request Body:
{
  "message": "string - user's question",
  "assistant_type": "string - one of: general, homework, exam, study_plan, tutor, mind_map",
  "params": {
    "edu_level": "string - optional",
    "subject": "string - optional",
    "tone": "string - optional",
    "detail_level": "string - optional"
  }
}

Response:
{
  "success": true,
  "response": "string - AI response",
  "sources": ["string - book titles used"]
}
```

#### Generate Exam
```
POST /api/generate-exam
Auth: Required
Content-Type: application/json

Request Body:
{
  "num_questions": number,
  "difficulty": "string - easy/medium/hard/mixed",
  "question_type": "string - mcq/short/essay/mixed",
  "subject": "string",
  "topic": "string"
}

Response:
{
  "success": true,
  "exam": "string - formatted exam with questions and answers"
}
```

#### Generate Study Plan
```
POST /api/generate-study-plan
Auth: Required
Content-Type: application/json

Request Body:
{
  "subject": "string",
  "daily_hours": number,
  "sleep_time": "string - e.g., '8 hours'",
  "duration_days": number
}

Response:
{
  "success": true,
  "plan": "string - formatted study plan"
}
```

#### Get Books
```
GET /api/get-books
Auth: Required

Response:
{
  "success": true,
  "books": [
    {
      "id": number,
      "title": "string",
      "uploaded_at": "timestamp"
    }
  ]
}
```

#### Get Conversation History
```
GET /api/conversation-history?type=string&limit=number
Auth: Required

Parameters:
- type (optional): 'all' or specific assistant type
- limit (optional): number of conversations to return (default: 20)

Response:
{
  "success": true,
  "conversations": [
    {
      "id": number,
      "assistant_type": "string",
      "user_message": "string",
      "ai_response": "string",
      "created_at": "timestamp"
    }
  ]
}
```

---

## Troubleshooting

### Common Issues

#### 1. Oracle Connection Error
**Error**: `ORA-12514: TNS:listener does not currently know of service requested`

**Solutions**:
- Verify Oracle service is running
  ```bash
  # Windows: Check Services
  # Linux: sudo systemctl status oracle-database
  ```
- Check DSN is correct in config.py
- Verify credentials are correct
- Check firewall isn't blocking port 1521

#### 2. Instant Client Not Found
**Error**: `oracle.thick_client_init: Error - DPI-1047`

**Solutions**:
- Download from: https://www.oracle.com/database/technologies/instant-client/downloads.html
- Set correct path in config.py: `DB_CLIENT_DIR`
- Add to PATH environment variable
- Restart Python after installation

#### 3. Books Not Uploading
**Error**: Books folder empty after scheduled time

**Solutions**:
- Check D:\Work\books exists
- Add PDF files to folder
- Check app logs for errors
- Verify scheduler is running: look for "Book upload scheduler started" in logs
- Check file permissions

#### 4. Grok API Errors
**Error**: `401 Unauthorized` or timeout

**Solutions**:
- Verify API key in config.py
- Check internet connection
- Verify API key is valid at: https://console.x.ai
- Check API rate limits
- Review API documentation at: https://docs.x.ai

#### 5. Port Already in Use
**Error**: `Address already in use`

**Solutions**:
- Change port in app.py:
  ```python
  if __name__ == '__main__':
      app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5001
  ```
- Or kill the process using port 5000:
  ```bash
  # Windows
  netstat -ano | findstr :5000
  taskkill /PID <PID> /F
  
  # Linux/Mac
  lsof -i :5000
  kill -9 <PID>
  ```

#### 6. Module Not Found Errors
**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solutions**:
- Ensure virtual environment is activated
- Reinstall requirements:
  ```bash
  pip install -r requirements.txt --force-reinstall
  ```
- Update pip:
  ```bash
  pip install --upgrade pip
  ```

### Getting Help

1. **Check logs**: Look at console output for error messages
2. **Review README.md**: Full project documentation
3. **Check config.py**: Verify all settings are correct
4. **Test components**: Run quick_start.py to check system

---

## File Structure

```
chatbot with oracle/
│
├── app.py                      # Main Flask application
├── database.py                 # Oracle database operations
├── grok_service.py             # Grok API integration
├── book_scheduler.py           # Automatic daily upload
├── config.py                   # Configuration settings
├── quick_start.py              # Quick start checker
│
├── upload_manager.py           # Original upload script
├── requirements.txt            # Python dependencies
├── run.bat                     # Windows startup script
├── run.sh                      # Linux/Mac startup script
├── README.md                   # Project overview
├── SETUP.md                    # This file
│
├── templates/
│   ├── login.html             # Login page
│   ├── dashboard.html         # Main dashboard
│   ├── general_assistant.html
│   ├── homework_assistant.html
│   ├── exam_preparation.html
│   ├── study_planner.html
│   ├── tutor_assistant.html
│   ├── mind_mapper.html
│   └── error.html
│
└── static/
    ├── css/
    │   ├── style.css
    │   └── assistant.css
    └── js/
        └── assistant.js
```

---

## Production Deployment

### Before Going Live:

1. **Security**:
   ```python
   # In config.py:
   DEBUG = False
   SECRET_KEY = secrets.token_hex(32)  # Generate random key
   ```

2. **Use Production Server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Enable HTTPS**:
   - Get SSL certificate from Let's Encrypt
   - Configure nginx as reverse proxy

4. **Environment Variables**:
   ```bash
   # Create .env file
   FLASK_ENV=production
   DB_USER=your_user
   DB_PASSWORD=your_pass
   GROK_API_KEY=your_key
   ```

5. **Database Backup**:
   - Set up regular Oracle backups
   - Test restore procedures

6. **Monitoring**:
   - Set up error logging
   - Monitor database connections
   - Track API usage

7. **Performance**:
   - Enable caching
   - Optimize database queries
   - Use CDN for static files

---

## Version History

- **v1.0.0** (Current)
  - Email-based authentication
  - 6 intelligent assistants
  - Grok API integration
  - Daily book upload scheduler
  - Professional UI/UX
  - Oracle database integration

---

## Support

For issues, questions, or suggestions:
1. Check this documentation
2. Review error messages in console
3. Check application logs
4. Verify configuration settings

---

## License

Created by SkillCode Team
All rights reserved © 2024

---

**Last Updated**: February 2024
**Status**: Production Ready ✅
