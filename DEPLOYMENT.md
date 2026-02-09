# SkillCode GPT - Free Hosting Options

## Important Note About Oracle Database Dependency

Your application uses Oracle Database, which is **NOT supported** by most free hosting platforms. You have a few options:

---

## Option 1: **Render.com** (RECOMMENDED - Easiest)

**⚠️ Requires migrating from Oracle to PostgreSQL**

### Steps:
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub account (you'll need to push your code to GitHub first)
4. Select this repository
5. Render will auto-detect the `render.yaml` configuration
6. Add environment variables in the Render dashboard:
   - `GROK_API_KEY`: Your Grok API key
7. Click "Create Web Service"
8. Your app will be live at: `https://skillcode-chatbot-XXXX.onrender.com`

**Free Tier Limitations:**
- App sleeps after 15 minutes of inactivity
- 750 hours/month free
- PostgreSQL database (500MB free)

---

## Option 2: **Railway.app** (Better Oracle Support)

Railway provides $5 free trial credits and has better support for Oracle client libraries.

### Steps:
1. Go to [railway.app](https://railway.app) and sign up with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect it's a Python app
5. Add environment variables:
   - `GROK_API_KEY`: Your API key
   - All database credentials
6. Deploy
7. You'll get a URL like: `https://skillcode-chatbot-production.up.railway.app`

**Note:** Free trial gives you $5 credits (usually enough for 1-2 months of light usage)

---

## Option 3: **PythonAnywhere** (Oracle Compatible)

PythonAnywhere supports custom Python packages and Oracle clients.

### Steps:
1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your files using the Files tab
3. Set up a virtual environment:
   ```bash
   mkvirtualenv my-env --python=python3.10
   pip install -r requirements.txt
   ```
4. Configure Oracle Instant Client (you'll need to download and set paths)
5. Create a new Web app → Manual configuration → Python 3.10
6. Configure WSGI file to point to your Flask app
7. Your app will be at: `http://yourusername.pythonanywhere.com`

**Free Tier:**
- 1 web app
- 512MB storage
- Limited CPU/bandwidth

---

## Option 4: **Replit** (EASIEST - No GitHub needed)

Replit is the fastest way to get a live URL without any deployment complexity.

### Steps:
1. Go to [replit.com](https://replit.com) and sign up
2. Create a new Repl → Import from GitHub OR upload files
3. Replit will auto-detect Python and the `.replit` file
4. Install dependencies: `pip install -r requirements.txt`
5. Click "Run"
6. Your app will be live at: `https://skillcode-chatbot.yourusername.repl.co`

**⚠️ Issues with Oracle:**
- Oracle Instant Client is difficult to set up on Replit
- You may need to migrate to SQLite/PostgreSQL

---

## Option 5: **Fly.io** (Advanced)

Fly.io offers generous free tier and supports Docker, which makes Oracle client easier.

### Steps:
1. Install Fly CLI: https://fly.io/docs/hands-on/install-flyctl/
2. Run `flyctl auth signup`
3. Run `flyctl launch` in your project directory
4. Configure environment variables
5. Run `flyctl deploy`
6. Your app: `https://skillcode-chatbot.fly.dev`

---

## 🚀 FASTEST SOLUTION: Ngrok (Temporary Public URL)

If you just need a quick public URL for testing/sharing (not permanent):

1. Download ngrok: https://ngrok.com/download
2. Sign up for free account (get auth token)
3. Run your Flask app locally: `python app.py`
4. In another terminal: `ngrok http 5000`
5. You'll get a URL like: `https://abc123.ngrok.io`

**Limitations:**
- Temporary URL (changes when you restart ngrok)
- Requires your computer to be running
- Free tier has connection limits

---

## Recommendation

**For immediate demo/testing:** Use **Ngrok** (option 6)
**For permanent free hosting:** Use **Render.com** (option 1) but migrate to PostgreSQL

Would you like help with:
1. Migrating from Oracle to PostgreSQL/SQLite?
2. Deploying to a specific platform?
3. Setting up ngrok for quick testing?
