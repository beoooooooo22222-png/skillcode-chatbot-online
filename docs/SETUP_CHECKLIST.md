# SkillCode GPT - Environment Setup Checklist

## ✅ Pre-Installation Checklist

Before running the application, ensure you have:

### System Requirements
- [ ] Windows 10+ / Linux / macOS
- [ ] Python 3.8 or higher installed
- [ ] Oracle Database (XE or higher) running
- [ ] Oracle Instant Client 23.0 installed
- [ ] Internet connection (for Grok API)
- [ ] At least 2GB RAM available
- [ ] 500MB free disk space

### Verify Python Installation
```bash
python --version
# Should show Python 3.8 or higher
```

### Verify Oracle Database
```bash
# Windows: Check Services app
# Linux: systemctl status oracle-database
# The service should show as "Running"
```

---

## 📦 Installation Checklist

### Step 1: Navigate to Project
- [ ] Open Command Prompt/Terminal
- [ ] Navigate to: `d:\Work\chatbot with oracle`
  ```bash
  cd "d:\Work\chatbot with oracle"
  ```

### Step 2: Create Virtual Environment
- [ ] Create venv (Windows):
  ```bash
  python -m venv venv
  ```
- [ ] Or venv (Linux/Mac):
  ```bash
  python3 -m venv venv
  ```

### Step 3: Activate Virtual Environment
- [ ] Windows:
  ```bash
  venv\Scripts\activate
  ```
- [ ] Linux/Mac:
  ```bash
  source venv/bin/activate
  ```
- [ ] Verify activation (should see `(venv)` in prompt)

### Step 4: Install Requirements
- [ ] Run installation:
  ```bash
  pip install -r requirements.txt
  ```
- [ ] Verify no errors occurred
- [ ] Check main packages installed:
  ```bash
  pip list | grep -E "flask|oracledb|requests|apscheduler"
  ```

---

## ⚙️ Configuration Checklist

### Step 1: Database Configuration
File: `config.py`

- [ ] Set Oracle username:
  ```python
  DB_USER = "help_me"  # or your Oracle username
  ```

- [ ] Set Oracle password:
  ```python
  DB_PASSWORD = "password"  # your Oracle password
  ```

- [ ] Set Oracle DSN:
  ```python
  DB_DSN = "localhost:1521/xe"  # your Oracle connection string
  ```

- [ ] Set Oracle client path:
  ```python
  DB_CLIENT_DIR = r"C:\oraclexe\app\oracle\instantclient_23_0"
  # or your Instant Client installation path
  ```

### Step 2: API Configuration
File: `config.py`

- [ ] Verify Grok API key:
  ```python
  GROK_API_KEY = "[YOUR_GROK_API_KEY]"
  ```

- [ ] Keep other API settings as default

### Step 3: Book Management
File: `config.py`

- [ ] Verify books folder:
  ```python
  BOOKS_FOLDER = r"D:\Work\books"
  ```

- [ ] Create the books folder:
  ```bash
  # Windows
  mkdir D:\Work\books
  
  # Linux/Mac
  mkdir -p ~/Work/books
  ```

- [ ] Add some PDF files to test (optional)

### Step 4: Scheduler Configuration
File: `book_scheduler.py`

- [ ] Verify upload schedule:
  ```python
  hour=2,   # Daily at 2:00 AM
  minute=0,
  ```

- [ ] Change if needed (hour should be 0-23)

---

## 🧪 Pre-Launch Tests

### Test 1: Oracle Connection
```bash
# In Python interactive shell:
python -c "import oracledb; print('✓ Oracle client OK')"
```

### Test 2: Python Packages
```bash
python -c "import flask, requests, apscheduler; print('✓ All packages OK')"
```

### Test 3: Database Access
```bash
python -c "
from database import Database
try:
    db = Database()
    print('✓ Database connection OK')
except Exception as e:
    print(f'✗ Database error: {e}')
"
```

### Test 4: Books Folder
```bash
# Verify folder exists
# Windows
dir D:\Work\books

# Linux/Mac
ls -la ~/Work/books
```

### Test 5: Configuration
```bash
python -c "
import config
print(f'App: {config.APP_NAME}')
print(f'DB User: {config.DB_USER}')
print(f'Books: {config.BOOKS_FOLDER}')
print('✓ Configuration loaded')
"
```

---

## 🚀 Launch Checklist

### Method 1: Using Startup Script (Easiest)

#### Windows
- [ ] Double-click `run.bat` in project folder
- [ ] Or from command prompt:
  ```bash
  run.bat
  ```

#### Linux/Mac
- [ ] Make script executable:
  ```bash
  chmod +x run.sh
  ```
- [ ] Run script:
  ```bash
  ./run.sh
  ```

### Method 2: Manual Launch

- [ ] Ensure venv is activated (see `(venv)` in prompt)
- [ ] Run application:
  ```bash
  python app.py
  ```
- [ ] Wait for startup message

### What You Should See
```
Running on http://127.0.0.1:5000
✅ Book upload scheduler started (runs daily at 2:00 AM)
```

---

## 🌐 Access Application

### Open Browser
- [ ] Type in address bar: `http://localhost:5000`
- [ ] Press Enter
- [ ] You should see the SkillCode GPT login page

### Create First User
- [ ] Enter your email address
- [ ] Click "Login"
- [ ] You'll be redirected to dashboard

### Test Features
- [ ] Click "General Assistant"
- [ ] Type a test question
- [ ] Verify response appears
- [ ] Repeat with other assistants

---

## 🛑 Stopping the Application

### Stop Server
- [ ] In terminal, press `Ctrl + C`
- [ ] Wait for shutdown message
- [ ] Terminal prompt should reappear

### Deactivate Virtual Environment
```bash
deactivate
```

---

## 📚 Using the Application

### Login
- [ ] Email-only login (no password)
- [ ] Auto-creates user on first login
- [ ] Session lasts 7 days

### Assistants Available
- [ ] General Assistant - Q&A
- [ ] Homework Assistant - Problem solving
- [ ] Exam Preparation - Test generator
- [ ] Study Planner - Schedule maker
- [ ] Tutor Assistant - Personal tutoring
- [ ] Mind Mapper - Concept visualization

### Adding Books
- [ ] Add PDF files to `D:\Work\books`
- [ ] They auto-upload daily at 2:00 AM
- [ ] Or use original `upload_manager.py` for manual upload

---

## 🔧 Troubleshooting Checklist

### If Oracle Connection Fails
- [ ] Verify Oracle service is running
- [ ] Check username and password in config.py
- [ ] Test connection: `sqlplus [user]@[host]:[port]/[db]`
- [ ] Check firewall isn't blocking port 1521

### If Python Packages Fail
- [ ] Ensure venv is activated
- [ ] Reinstall: `pip install -r requirements.txt --force-reinstall`
- [ ] Update pip: `pip install --upgrade pip`
- [ ] Check Python version: `python --version`

### If App Won't Start
- [ ] Check for syntax errors in config.py
- [ ] Verify port 5000 isn't in use
- [ ] Check all required packages installed
- [ ] Look at error message in console

### If Books Don't Upload
- [ ] Verify folder path is correct
- [ ] Check PDF files are readable
- [ ] Check folder has write permissions
- [ ] Check scheduler message at startup

### If API Calls Fail
- [ ] Verify internet connection
- [ ] Check Grok API key is valid
- [ ] Verify API isn't rate-limited
- [ ] Check request format in api calls

---

## 📋 Quick Reference

### Important Paths
```
Project: d:\Work\chatbot with oracle
Books:   D:\Work\books
Config:  d:\Work\chatbot with oracle\config.py
```

### Important Commands
```bash
# Activate venv
venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Run app
python app.py

# Stop app
Ctrl + C

# Deactivate venv
deactivate
```

### Important Credentials
```
Oracle User: help_me
Oracle Pass: password
Grok Key: [YOUR_GROK_API_KEY]
```

### Access Points
```
Web:     http://localhost:5000
API:     http://localhost:5000/api/*
```

---

## ✨ You're Ready!

Once all checkboxes are complete, your SkillCode GPT application is ready to use!

### Next Steps
1. ✅ Complete this checklist
2. ✅ Launch the application
3. ✅ Test with your email login
4. ✅ Add PDF books to library
5. ✅ Start using the assistants

### Need Help?
- Read README.md for overview
- Read SETUP.md for detailed guide
- Check console for error messages
- Review config.py settings

---

**Status**: Ready to Launch 🚀  
**Last Updated**: February 2024  
**Support**: Refer to documentation files
