@echo off
echo.
echo ==================================================
echo      SKILLCODE GPT - SYNC ORACLE TO VECTOR
echo ==================================================
echo.
echo 1. Checking connection to Oracle...
python -c "from src.database_oracle import Database; Database()" > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Could not connect to Oracle. Make sure Oracle XE is running.
    pause
    exit /b %errorlevel%
)

echo 2. Running Verification...
python verify_oracle_sync.py
echo.
set /p choice="Do you want to run the full sync now? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo 3. Migrating new books and data...
    python migrate_oracle_to_vector.py
    echo.
    echo Sync Complete!
) else (
    echo Sync cancelled.
)
pause
