import os
import re
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, login_required, current_user
# Department will be imported inside functions to avoid circular imports


def compute_sqlite_uri():
    """Compute SQLite database URI for the current instance"""
    # Create base directory for databases
    base_dir = os.path.join(os.getcwd(), 'hanamantdatabase')
    os.makedirs(base_dir, exist_ok=True)

    # Determine instance identifier
    instance = os.environ.get('SPA_DB_INSTANCE') or os.environ.get('REPL_SLUG') or 'default'

    # Sanitize instance name to prevent path traversal
    instance = re.sub(r'[^A-Za-z0-9_-]', '_', instance)

    # Create absolute path to database file
    db_path = os.path.abspath(os.path.join(base_dir, f'{instance}.db'))

    # Return SQLite URI with absolute path
    return f'sqlite:///{db_path}'


def configure_sqlite_pragmas(dbapi_connection, connection_record):
    """Configure SQLite-specific PRAGMA settings"""
    # Only apply to SQLite connections
    if hasattr(dbapi_connection, 'execute'):
        cursor = dbapi_connection.cursor()
        # Enable foreign key constraints
        cursor.execute('PRAGMA foreign_keys=ON')
        # Use WAL mode for better concurrency
        cursor.execute('PRAGMA journal_mode=WAL')
        # Set synchronous mode for balance of safety and performance
        cursor.execute('PRAGMA synchronous=NORMAL')
        cursor.close()


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
# Validate required environment variables
if not os.environ.get("SESSION_SECRET"):
    raise RuntimeError("SESSION_SECRET environment variable is required for production")
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1) # needed for url_for to generate with https

# Handle trailing slash variations
app.url_map.strict_slashes = False

# Configure the database - always use SQLite with hanamantdatabase folder for each clone
app.config["SQLALCHEMY_DATABASE_URI"] = compute_sqlite_uri()
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {
        "check_same_thread": False  # Allow SQLite to be used across threads
    }
}
print(f"Using SQLite database: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Configure cache control for Replit webview
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for API endpoints in development

# Session configuration for Replit environment (relaxed for development)
app.config.update(
    SECRET_KEY=os.environ.get("SESSION_SECRET"),  # No fallback for production security
    SESSION_COOKIE_SAMESITE="Lax",  # Less strict for development
    SESSION_COOKIE_SECURE=False,   # Allow non-HTTPS in development
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_PERMANENT=False
)

# Initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

# Initialize CSRF protection (disabled for development)
# csrf = CSRFProtect(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    # Import inside function to avoid circular imports
    from models import User
    return User.query.get(int(user_id))

# Make utils available in all templates
@app.context_processor
def utility_processor():
    import utils
    return dict(utils=utils)

# Add ping route for health check
@app.route('/ping')
def ping():
    """Simple health check endpoint"""
    return 'OK'

# Add favicon route to prevent 404 errors
@app.route('/favicon.ico')
def favicon():
    """Return favicon response to prevent 404 errors"""
    return '', 204

# Add response headers for Replit Preview compatibility
@app.after_request
def after_request(response):
    """Add headers for Replit Preview and CORS"""
    # Allow embedding in Replit Preview
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'

    # CORS headers for Replit environment
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'

    # Cache control for development
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

# Basic routes removed to avoid conflicts with main application routes

# Initialize database and routes within app context
def init_app():
    """Initialize the application with proper error handling"""
    with app.app_context():
        try:
            # Add SQLite PRAGMA event listener for SQLite connections (inside app context)
            event.listen(db.engine, 'connect', configure_sqlite_pragmas)
            print(f"SQLite PRAGMAs configured for: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print(f"Instance identifier: {os.environ.get('SPA_DB_INSTANCE') or os.environ.get('REPL_SLUG') or 'default'}")

            # Make sure to import the models here or their tables won't be created
            import models  # noqa: F401
            # Import inventory models for database creation
            from modules.inventory import models as inventory_models  # noqa: F401
            # Import Department model for database creation
            from models import Department  # noqa: F401

            # Try to create tables, but handle conflicts gracefully
            db.create_all()
            print("SQLite database tables created successfully")
            print(f"Database file location: {app.config['SQLALCHEMY_DATABASE_URI']}")
        except Exception as e:
            print(f"SQLite database initialization warning: {e}")
            print("Continuing with existing SQLite database...")

        try:
            # Import and register blueprints
            try:
                # Import staff blueprint from staff_views
                from modules.staff.staff_views import staff_bp
                app.register_blueprint(staff_bp)
                print("Staff Management routes registered successfully")
            except Exception as e:
                print(f"Error importing staff routes: {e}")
                print("Staff Management will not be available")

            try:
                # Import and register shift scheduler blueprint
                from modules.staff.shift_scheduler_views import shift_scheduler_bp
                app.register_blueprint(shift_scheduler_bp)
                print("Shift Scheduler routes registered successfully")
            except Exception as e:
                print(f"Error importing shift scheduler routes: {e}")
                print("Shift Scheduler will not be available")
            print("Routes imported successfully")
        except Exception as e:
            print(f"Warning: Could not import all routes: {e}")
            print("Application will continue with basic functionality")

# Initialize the app
init_app()

# Import all views to register routes
from modules.auth.auth_views import *
from modules.dashboard.dashboard_views import *
from modules.clients.clients_views import *
from modules.services.services_views import *
from modules.bookings.bookings_views import *
from modules.staff.staff_views import *
from modules.expenses.expenses_views import *
from modules.reports.reports_views import *
from modules.settings.settings_views import *
from modules.notifications.notifications_views import *
from modules.checkin.checkin_views import *
from modules.billing.billing_views import *
from modules.billing.integrated_billing_views import *
from modules.inventory.views import *
from modules.packages.new_packages_views import *
from modules.packages.membership_views import *
from modules.packages.professional_packages_views import *

# Missing route endpoints to fix template BuildErrors
@app.route('/system_management')
@login_required
def system_management():
    """System management page"""
    if not current_user.can_access('settings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('system_management.html')

@app.route('/role_management')
@login_required
def role_management():
    """Role management page"""
    if not current_user.can_access('settings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('settings.html')

# Department Management Routes moved to routes.py to avoid conflicts

@app.route('/')
def index():
    """Root route - redirect to dashboard if authenticated, otherwise to login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Ensure app is available for gunicorn
if __name__ != '__main__':
    # When imported by gunicorn or other WSGI servers
    print("App imported for WSGI deployment")