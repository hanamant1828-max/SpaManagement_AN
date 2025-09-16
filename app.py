import os
import sys
import logging
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
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
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Disable CSRF token expiration
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Prevent caching of static files
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database - SQLite
sqlite_path = os.path.join(os.path.dirname(__file__), 'instance', 'spa_management.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{sqlite_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Add headers for webview compatibility and caching control
@app.after_request
def after_request(response):
    # Cache control headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    # Security headers
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'  # Prevent clickjacking
    response.headers['X-Content-Type-Options'] = 'nosniff'  # Prevent MIME sniffing
    response.headers['X-XSS-Protection'] = '1; mode=block'  # Enable XSS protection
    # Restrict CORS for security
    origin = request.headers.get('Origin')
    if origin and ('replit.dev' in origin or 'replit.co' in origin or origin.startswith('http://localhost')):
        response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken'
    return response

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Inject user and CSRF token into template context
@app.context_processor
def inject_user():
    from models import User
    from flask_wtf.csrf import generate_csrf
    import utils
    return dict(
        current_user=current_user,
        User=User,
        utils=utils,
        csrf_token=generate_csrf
    )

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
    from modules.billing import integrated_billing_views
    from modules.services import services_views
    from modules.packages import packages_views
    from modules.reports import reports_views
    from modules.expenses import expenses_views
    from modules.inventory import views as inventory_views
    from modules.settings import settings_views
    
    # Register shift scheduler blueprint
    from modules.staff.shift_scheduler_views import shift_scheduler_bp
    app.register_blueprint(shift_scheduler_bp)

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

    # Import routes.py to register root routes and error handlers
    try:
        import routes  # registers root, system, error routes
        print("routes.py imported successfully")
    except Exception as e:
        logging.exception(f"Failed importing routes.py: {e}")
        print("Running without core routes - some pages may not work")

    # Log registered routes for debugging
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")

# Run the Flask app when called directly
if __name__ == "__main__":
    # Fix: Prevent double Flask instance creation from circular imports
    sys.modules['app'] = sys.modules[__name__]
    print("Starting Flask development server on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)