import os
import sys

# Add the parent directory to sys.path so we can import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the properly configured Flask app
from app import app

# The app is now fully configured in app.py with:
# - Production vs development detection
# - Proper database configuration (SQLite for dev, PostgreSQL for prod)
# - Security headers and CSRF protection
# - Serverless-safe initialization

# Export the app for Vercel
if __name__ == "__main__":
    app.run(debug=False)
    
# Vercel will import this file and use the 'app' variable