"""
Quick Start Guide for SkillCode GPT
"""

# BEFORE YOU START:
# 1. Make sure Oracle Database is running
# 2. Create D:\Work\books folder and add PDF files
# 3. Verify your Grok API key in config.py

import os
import sys

def print_header():
    print("\n" + "="*50)
    print("  SkillCode GPT - Quick Start")
    print("="*50 + "\n")

def check_requirements():
    """Check if all requirements are met"""
    print("Checking system requirements...\n")
    
    checks = {
        "Python 3.8+": sys.version_info >= (3, 8),
        "Books folder exists": os.path.exists(r"D:\Work\books"),
        "Flask installed": False,
        "OracleDB installed": False,
    }
    
    # Check installed packages
    try:
        import flask
        checks["Flask installed"] = True
    except ImportError:
        pass
    
    try:
        import oracledb
        checks["OracleDB installed"] = True
    except ImportError:
        pass
    
    # Print results
    for check, result in checks.items():
        status = "✓" if result else "✗"
        print(f"{status} {check}")
    
    print()
    return all(checks.values())

def main():
    print_header()
    
    if not check_requirements():
        print("⚠️  Some requirements are missing!")
        print("\nTo fix:")
        print("1. Install Python 3.8+: https://www.python.org")
        print("2. Create D:\\Work\\books folder")
        print("3. Run: pip install -r requirements.txt")
        print("4. Add your Oracle credentials to config.py")
        return False
    
    print("✓ All requirements met!\n")
    print("Next steps:")
    print("1. Update config.py with your Oracle credentials")
    print("2. Add PDF files to D:\\Work\\books")
    print("3. Run: python app.py")
    print("4. Open http://localhost:5000 in your browser")
    print("\n" + "="*50 + "\n")
    
    return True

if __name__ == "__main__":
    main()
