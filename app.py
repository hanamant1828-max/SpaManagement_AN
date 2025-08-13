import os
import logging
import secrets
from flask import Flask
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
app.config['WTF_CSRF_ENABLED'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Allow non-HTTPS for development
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///spa_management.db")

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_timeout": 20,  # Connection timeout
    "max_overflow": 0,  # Don't allow connections beyond pool_size
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

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models here so their tables will be created
    import models  # noqa: F401

    try:
        db.create_all()
        logging.info("Database tables created")

        # Initialize default data
        from routes import create_default_data
        create_default_data()
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        logging.info("Attempting database migration...")
        try:
            import subprocess
            subprocess.run(['python', 'migrate_database.py'], check=True)
            logging.info("Migration completed, retrying initialization...")
            db.create_all()
            from routes import create_default_data
            create_default_data()
        except Exception as migration_error:
            logging.error(f"Migration failed: {migration_error}")
            logging.warning("Application starting with limited functionality")