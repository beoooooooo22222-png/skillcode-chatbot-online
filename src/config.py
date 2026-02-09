"""
Configuration file for SkillCode GPT
"""

import os
from datetime import timedelta

# Flask Configuration
DEBUG = True
SECRET_KEY = 'your-secret-key-change-in-production'

# Session Configuration
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = False
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# Database Configuration
DB_USER = os.environ.get("DB_USER", "help_me")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
DB_DSN = os.environ.get("DB_DSN", "localhost:1521/xe")
DB_CLIENT_DIR = os.environ.get("DB_CLIENT_DIR", r"C:\oraclexe\app\oracle\instantclient_23_0")

# MongoDB Configuration
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "skillcode_db")

# Book Upload Configuration
BOOKS_FOLDER = os.environ.get("BOOKS_FOLDER", os.path.join(os.getcwd(), "books"))
UPLOAD_SCHEDULE_HOUR = 2  # 2:00 AM daily

# Grok API Configuration
GROK_API_KEY = os.environ.get("GROK_API_KEY", "your-key-here")
GROK_BASE_URL = "https://api.groq.com/openai/v1"
GROK_MODEL = "llama-3.1-8b-instant"

# App Settings
APP_NAME = "SkillCode GPT"
APP_VERSION = "1.0.0"
MAX_BOOKS_PER_SEARCH = 3
CONVERSATION_LIMIT = 3
