# SkillCode GPT - Getting Started Guide

Welcome to SkillCode GPT! This file will help you get up and running in minutes.

---

## 🎯 What is SkillCode GPT?

An intelligent educational chatbot with 6 specialized assistants powered by AI, integrated with your Oracle database and PDF books.

**Features:**
- 📚 6 Different assistants for different learning needs
- 💬 Real-time AI conversations powered by Grok API
- 📖 Automatic daily PDF uploads from your library
- 👤 Email-based user accounts
- 🎨 Modern, professional interface

---

## ⚡ Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Update Configuration
Open `config.py` and update:
```python
# Your Oracle credentials
DB_USER = "help_me"
DB_PASSWORD = "password"
DB_DSN = "localhost:1521/xe"
DB_CLIENT_DIR = r"C:\oraclexe\app\oracle\instantclient_23_0"

# Your books folder
BOOKS_FOLDER = r"D:\Work\books"

# Grok API (already configured)
GROK_API_KEY = "[YOUR_GROK_API_KEY]"
```

### 3. Create Books Folder
```bash
mkdir D:\Work\books
```

### 4. Run Application
```bash
# Windows
run.bat

# Linux/Mac
./run.sh

# Or manually
python app.py
```

### 5. Open in Browser
Go to: `http://localhost:5000`

---

## 📚 The 6 Assistants

### 1. 💡 General Assistant
Ask any educational question and get comprehensive answers based on your study materials.

### 2. 📝 Homework Assistant
Get step-by-step solutions with customizable:
- Education level (Elementary → College)
- Subject
- Tone (Formal → Friendly)
- Detail level (Brief → Detailed)

### 3. 📚 Exam Preparation
Generate practice exams:
- Choose number of questions
- Select difficulty level
- Pick question types
- Get answer keys

### 4. 📅 Study Planner
Create personalized study schedules:
- Set daily study hours
- Input your sleep schedule
- Specify study duration
- Get adaptive learning paths

### 5. 👨‍🏫 Tutor Assistant
Your personal AI tutor that:
- Explains concepts clearly
- References your study materials
- Suggests what to review next
- Provides encouragement

### 6. 🧠 Mind Mapper
Visualize complex topics:
- Create concept maps
- Show relationships
- Hierarchical organization
- Study summaries

---

## 📖 Adding Books

### Automatic Method (Easiest)
1. Add PDF files to `D:\Work\books`
2. They automatically upload daily at 2:00 AM
3. AI assistants will use them in responses

### Manual Method
```bash
python upload_manager.py
```

---

## 🔐 First Time Login

1. Go to `http://localhost:5000`
2. Enter your email (no password needed)
3. Click "Login"
4. User account created automatically
5. Access dashboard with all assistants

---

## 📚 Documentation

### For Getting Started
- **This File**: You're reading it!
- **README.md**: Project overview
- **SETUP_CHECKLIST.md**: Detailed checklist

### For Full Details
- **SETUP.md**: Complete installation guide
- **PROJECT_SUMMARY.md**: Features summary

### For Reference
- **config.py**: All settings
- **Source Code**: Well-commented

---

## 🚀 First Steps

### Step 1: Login
```
Email: your@email.com
```

### Step 2: Choose an Assistant
Click any of the 6 options on dashboard

### Step 3: Ask a Question
Type your question and press Send

### Step 4: Get Answer
AI responds using your study materials

---

## 🎓 Example Questions

Try these with different assistants:

**General Assistant:**
- "Explain photosynthesis"
- "What is quantum mechanics?"

**Homework Assistant:**
- "Solve this calculus problem: ∫x² dx"
- "Help me understand this chemistry equation"

**Exam Preparation:**
- "Generate 5 biology questions"
- "Create an exam on history topics"

**Study Planner:**
- "Create a 30-day study plan for mathematics"
- "Plan my studying for physics exam"

**Tutor Assistant:**
- "Explain derivatives step by step"
- "What should I review next?"

**Mind Mapper:**
- "Create a mind map for the solar system"
- "Visualize photosynthesis process"

---

## ⚙️ Configuration Options

### Change Upload Time
Edit `book_scheduler.py`:
```python
hour=2,    # Change to desired hour (0-23)
minute=0,  # Change to desired minute (0-59)
```

### Change Port
Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change port
```

### Change Books Folder
Edit `config.py`:
```python
BOOKS_FOLDER = r"your_folder_path"
```

---

## 🆘 Troubleshooting

### Issue: Can't connect to Oracle
**Solution:**
- Ensure Oracle service is running
- Check credentials in config.py
- Verify Instant Client path

### Issue: Books not uploading
**Solution:**
- Check folder path is correct
- Ensure PDFs are in D:\Work\books
- Check file permissions
- Check scheduler started (look for message in console)

### Issue: API not responding
**Solution:**
- Check internet connection
- Verify Grok API key is valid
- Check API rate limits

### Issue: Port already in use
**Solution:**
- Change port in app.py to 5001, 5002, etc.
- Or kill process using port 5000

---

## 📊 System Requirements

**Minimum:**
- Python 3.8+
- 2GB RAM
- Oracle Database
- 500MB disk space

**Recommended:**
- Python 3.10+
- 4GB+ RAM
- Oracle Database
- Internet connection

---

## 🔑 Key Files

### Configuration
- `config.py` - All settings
- `requirements.txt` - Dependencies

### Core Application
- `app.py` - Main Flask app
- `database.py` - Database operations
- `grok_service.py` - AI integration
- `book_scheduler.py` - Automatic uploads

### Web Interface
- `templates/` - HTML pages
- `static/css/` - Styling
- `static/js/` - Interactions

---

## 📱 Features

✅ Email-based login (no password)
✅ 6 intelligent assistants
✅ AI-powered responses
✅ Automatic book uploads
✅ Conversation history
✅ Professional UI
✅ Mobile responsive
✅ Real-time chat
✅ Customizable responses
✅ Source citations

---

## 🚀 Next Steps

### Immediate
1. ✅ Install dependencies
2. ✅ Update config.py
3. ✅ Run application
4. ✅ Login and test

### Soon
1. Add PDF books to library
2. Test all 6 assistants
3. Customize settings
4. Invite others to use

### Advanced
1. Deploy to production
2. Set up backup systems
3. Monitor usage
4. Add more features

---

## 📞 Need Help?

1. **Check the docs**: README.md, SETUP.md
2. **Review config.py**: Verify all settings
3. **Check console**: Look for error messages
4. **Read comments**: Code is well documented

---

## 🎉 You're All Set!

Everything is configured and ready to use. Just run:

```bash
python app.py
```

Then visit: `http://localhost:5000`

Happy learning! 📚✨

---

**Version**: 1.0.0
**Status**: Ready to Use ✅
**Support**: See documentation files
**Last Updated**: February 2024
