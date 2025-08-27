import os
import logging
import secrets
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or "dev-secret-key-for-spa-management-system" or secrets.token_hex(32)
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Disable CSRF token expiration
app.config['WTF_CSRF_ENABLED'] = False
app.config['SESSION_COOKIE_SECURE'] = False  # Allow non-HTTPS for development
app.config['SESSION_COOKIE_HTTPONLY'] = False  # Allow access for webview
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Allow cross-site for Replit
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database - Using SQLite for simplicity
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///spa_management.db"

# SQLite doesn't need complex pooling configuration
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Add CORS headers for webview compatibility
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    return response

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models here for ORM mapping
    import models  # noqa: F401
    
    # Check if database exists and has our new schema
    import os
    if not os.path.exists("spa_management.db"):
        logging.info("Creating new database with updated schema...")
        try:
            import subprocess
            subprocess.run(['python', 'create_new_db.py'], check=True)
            logging.info("New database created successfully")
        except Exception as e:
            logging.error(f"Failed to create new database: {e}")
            # Fallback to creating tables normally
            db.create_all()
            logging.info("Database tables created")
    else:
        logging.info("Using existing database")