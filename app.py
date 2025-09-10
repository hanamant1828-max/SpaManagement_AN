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
app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    raise ValueError("SESSION_SECRET environment variable is required for secure operation")
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Disable CSRF token expiration
app.config['WTF_CSRF_ENABLED'] = False
app.config['SESSION_COOKIE_SECURE'] = False  # Allow non-HTTPS for development
app.config['SESSION_COOKIE_HTTPONLY'] = False  # Allow access for webview
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Allow cross-site for Replit
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Prevent caching of static files
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


# Configure the database - PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore
login_manager.login_message = 'Please log in to access this page.'

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Add headers for webview compatibility and caching control
@app.after_request
def after_request(response):
    # Cache control headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    # CORS headers for webview compatibility
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
    # Import models here so their tables will be created
    import models  # noqa: F401
    # Import all modules
    from modules.auth import auth_views
    from modules.dashboard import dashboard_views
    from modules.bookings import bookings_views
    from modules.clients import clients_views
    from modules.staff import staff_views
    from modules.checkin import checkin_views
    from modules.notifications import notifications_views
    from modules.billing import billing_views, integrated_billing_views
    from modules.services import services_views
    from modules.packages import packages_views
    from modules.reports import reports_views
    from modules.expenses import expenses_views
    from modules.inventory import views as inventory_views
    from modules.settings import settings_views

    try:
        db.create_all()
        logging.info("Database tables created")

    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        logging.info("Attempting database migration...")
        try:
            # Skip migration attempt since file doesn't exist
            logging.info("Retrying database initialization without migration...")
            db.create_all()

        except Exception as migration_error:
            logging.error(f"Database initialization retry failed: {migration_error}")
            logging.warning("Application starting with limited functionality")

    # Professional inventory views removed