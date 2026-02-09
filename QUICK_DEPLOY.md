# Quick Deployment Script for SkillCode GPT

## 🚀 Fastest Option: LocalTunnel (No Installation Needed!)

LocalTunnel is an npm package that gives you a public URL instantly without any signup.

### Steps:

1. **First, start your Flask app** (in one terminal):
```bash
python app.py
```

2. **Then, in another terminal, run** (make sure you have Node.js installed):
```bash
npx localtunnel --port 5000
```

You'll get a URL like: `https://famous-elephant-12.loca.lt`

**That's it!** Share that URL with anyone.

⚠️ Note: The URL changes each time you restart. Your computer must stay on.

---

## Alternative: Use Ngrok (Requires one-time setup)

1. **Download ngrok:**
   - Visit: https://ngrok.com/download
   - Or run: `choco install ngrok` (if you have Chocolatey)
   - Or run: `scoop install ngrok` (if you have Scoop)

2. **Sign up for free:**
   - Visit: https://dashboard.ngrok.com/signup
   - Copy your authtoken

3. **Configure ngrok:**
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

4. **Start your app:**
```bash
python app.py
```

5. **In another terminal, run:**
```bash
ngrok http 5000
```

You'll get a URL like: `https://abc123.ngrok-free.app`

---

## ✅ Recommended: Deploy to Render.com (Permanent Free Hosting)

For a permanent, always-on URL:

1. **Create a free GitHub account** (if you don't have one): https://github.com/signup

2. **Create a new repository:**
   - Go to: https://github.com/new
   - Name it: `skillcode-chatbot`
   - Make it Public
   - Don't initialize with README

3. **Push your code to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/skillcode-chatbot.git
git push -u origin main
```

4. **Deploy to Render:**
   - Go to: https://render.com/
   - Sign up with your GitHub account
   - Click "New +" → "Web Service"
   - Connect your `skillcode-chatbot` repository
   - Render will auto-detect settings
   - Click "Create Web Service"

5. **Your app will be live at:**
   `https://skillcode-chatbot.onrender.com`

**Note:** Render's free tier requires PostgreSQL, not Oracle. You'll need to migrate the database or use it for demo purposes.

---

## 🎯 Which One Should You Choose?

| Option | Speed | Permanence | Limitations |
|--------|-------|------------|-------------|
| **LocalTunnel** | ⚡ Instant | Temporary | Requires computer on |
| **Ngrok** | 🚀 Fast | Temporary | Requires signup, computer on |
| **Render.com** | 🐢 30 mins | Permanent | Needs PostgreSQL (no Oracle) |

---

## Need Help?

I can help you with:
1. Installing and running LocalTunnel (fastest)
2. Setting up ngrok
3. Migrating from Oracle to PostgreSQL for permanent hosting
4. Deploying to Render.com

Just let me know which option you prefer!
