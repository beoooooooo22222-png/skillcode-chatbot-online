@echo off
echo ========================================
echo   SkillCode GPT - Quick Deploy Setup
echo ========================================
echo.
echo OPTION 1: Ngrok (Fastest - Temporary URL)
echo -------------------------------------------
echo 1. Download ngrok from: https://ngrok.com/download
echo 2. Extract ngrok.exe to this folder
echo 3. Sign up at: https://dashboard.ngrok.com/signup
echo 4. Run: ngrok config add-authtoken YOUR_TOKEN
echo 5. Start app: python app.py
echo 6. In new terminal: ngrok http 5000
echo.
echo You'll get: https://xxxxx.ngrok-free.app
echo.
echo ========================================
echo.
echo OPTION 2: Render.com (Permanent Free URL)
echo -------------------------------------------
echo 1. Create GitHub account: https://github.com/signup
echo 2. Install Git: https://git-scm.com/download/win
echo 3. Push code to GitHub:
echo    git init
echo    git add .
echo    git commit -m "Initial commit"
echo    git remote add origin YOUR_REPO_URL
echo    git push -u origin main
echo.
echo 4. Go to: https://render.com
echo 5. Sign up with GitHub
echo 6. New Web Service -^> Connect repo
echo 7. Deploy!
echo.
echo You'll get: https://skillcode-chatbot.onrender.com
echo.
echo Note: Render needs PostgreSQL (not Oracle)
echo.
echo ========================================
echo.
pause
