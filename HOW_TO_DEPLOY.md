# 🚀 How to Host Your SkillCode Chatbot for FREE

## ⚠️ Important: Oracle Database Limitation

Your app uses Oracle Database, which **most free platforms don't support**. You have 3 options:

---

## ✅ **RECOMMENDED: Ngrok (Fastest - Get URL in 5 minutes)**

### What you'll get:
- **URL:** `https://abc123.ngrok-free.app` 
- **Cost:** FREE
- **Uptime:** As long as your computer is on
- **Speed:** ⚡ 5 minutes setup

### Steps:

#### 1. Download Ngrok
- Go to: **https://ngrok.com/download**
- Download **Windows (64-bit)** ZIP file
- Extract `ngrok.exe` to a folder (like `C:\ngrok\`)

#### 2. Create Free Account
- Visit: **https://dashboard.ngrok.com/signup**
- Sign up with email or Google
- You'll get an **authtoken**

#### 3. Configure Ngrok
Open PowerShell/CMD and run:
```bash
C:\ngrok\ngrok.exe config add-authtoken YOUR_AUTH_TOKEN_HERE
```
(Replace `YOUR_AUTH_TOKEN_HERE` with your actual token from step 2)

#### 4. Start Your Flask App
In your project folder:
```bash
python app.py
```

#### 5. Start Ngrok (in a NEW terminal)
```bash
C:\ngrok\ngrok.exe http 5000
```

#### 6. Get Your Link! 🎉
Ngrok will show you a URL like:
```
Forwarding: https://abc-123-xyz.ngrok-free.app -> http://localhost:5000
```

**That's your public link!** Share it with anyone.

### Limitations:
- URL changes every time you restart ngrok (unless you upgrade to paid)
- Your computer must stay on
- Free tier has some connection limits

---

## 🌐 **Option 2: Render.com (Permanent Free Hosting)**

### What you'll get:
- **URL:** `https://skillcode-chatbot.onrender.com`
- **Cost:** FREE (forever)
- **Uptime:** 24/7 (sleeps after 15 min inactivity)
- **Speed:** 📦 30-45 minutes setup

### ⚠️ Catch: You need to migrate from Oracle to PostgreSQL

### Steps:

#### 1. Install Git
- Download: **https://git-scm.com/download/win**
- Install with default settings

#### 2. Create GitHub Account
- Sign up: **https://github.com/signup**

#### 3. Create New Repository
- Go to: **https://github.com/new**
- Name: `skillcode-chatbot`
- Make it **Public**
- Don't initialize with anything
- Click "Create repository"

#### 4. Push Your Code to GitHub
In your project folder, run:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/skillcode-chatbot.git
git push -u origin main
```
(GitHub will ask for login the first time)

#### 5. Deploy to Render
- Go to: **https://render.com/**
- Click "Get Started for Free"
- Sign up with your GitHub account
- Click "New +" → "Web Service"
- Click "Connect Repository" → Find `skillcode-chatbot`
- Render will auto-detect Python
- **Environment Variables** → Add:
  - `GROK_API_KEY` = `[YOUR_GROK_API_KEY]`
- Click "Create Web Service"

#### 6. Wait for Deployment (5-10 minutes)
- Render will build and deploy your app
- You'll get: `https://skillcode-chatbot.onrender.com`

### Note:
You'll need to modify your code to use PostgreSQL instead of Oracle. I can help with this!

---

## 🎯 **Option 3: PythonAnywhere (Supports Oracle!)**

### What you'll get:
- **URL:** `http://yourusername.pythonanywhere.com`
- **Cost:** FREE
- **Uptime:** 24/7 (with limitations)
- **Oracle:** ✅ Supported (with manual setup)

### Steps:

#### 1. Sign Up
- Go to: **https://www.pythonanywhere.com/registration/register/beginner/**
- Create free account

#### 2. Upload Your Files
- Go to "Files" tab
- Upload all your project files
- Or use Git to clone your repo

#### 3. Set Up Virtual Environment
In the PythonAnywhere console:
```bash
mkvirtualenv my-env --python=python3.10
pip install -r requirements.txt
```

#### 4. Configure Oracle (Advanced)
- Download Oracle Instant Client
- Extract to your PythonAnywhere directory
- Set environment variables in WSGI config

#### 5. Create Web App
- Go to "Web" tab
- "Add a new web app"
- Choose "Manual configuration" → Python 3.10
- Configure WSGI file

#### 6. Your URL:
`http://yourusername.pythonanywhere.com`

---

## 📊 **Comparison Table**

| Platform | Speed | Permanence | Oracle Support | URL Quality |
|----------|-------|------------|----------------|-------------|
| **Ngrok** | ⚡ 5 min | Temporary | ✅ Yes | Random subdomain |
| **Render** | 📦 45 min | Permanent | ❌ No (PostgreSQL) | Custom subdomain |
| **PythonAnywhere** | 🐢 1 hour | Permanent | ✅ Yes (manual) | yourusername.pythonanywhere.com |

---

## 🎯 **My Recommendation**

### For Quick Demo (Right Now):
👉 **Use Ngrok** - You'll have a link in 5 minutes

### For Permanent Free Hosting:
👉 **Use Render.com** - But you'll need PostgreSQL instead of Oracle

### To Keep Oracle Database:
👉 **Use PythonAnywhere** - More setup but supports Oracle

---

## 🆘 **Need Help?**

I can help you with:

1. ✅ Setting up Ngrok (fastest)
2. ✅ Migrating from Oracle to PostgreSQL for Render
3. ✅ Configuring PythonAnywhere with Oracle
4. ✅ Any deployment issues

Just tell me which option you want to use!

---

## 🏃 **Quick Start (Ngrok)**

If you want the absolute fastest path:

1. Download: https://ngrok.com/download
2. Sign up: https://dashboard.ngrok.com/signup
3. Run: `ngrok config add-authtoken YOUR_TOKEN`
4. Run: `python app.py`
5. Run (new terminal): `ngrok http 5000`
6. **Get your link!** 🎉

---

**Current Date:** 2026-02-08
