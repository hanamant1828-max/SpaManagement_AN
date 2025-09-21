import os
import re
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
from sqlalchemy.pool import NullPool
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, login_required
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

# Detect production vs development environment  
IS_PRODUCTION = bool(os.environ.get("DATABASE_URL")) or bool(os.environ.get("VERCEL"))

# Fail fast if on Vercel without DATABASE_URL
if os.environ.get("VERCEL") and not os.environ.get("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL environment variable is required when deploying to Vercel")

# create the app
app = Flask(__name__)
# Validate required environment variables
if not os.environ.get("SESSION_SECRET"):
    raise RuntimeError("SESSION_SECRET environment variable is required for production")
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1) # needed for url_for to generate with https

# Handle trailing slash variations
app.url_map.strict_slashes = False

# Configure the database - use DATABASE_URL if available (production), otherwise SQLite (development)
database_url = os.environ.get("DATABASE_URL")
if database_url:
    # Production database configuration
    # Fix postgres:// to postgresql:// for SQLAlchemy 2.x compatibility
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "poolclass": NullPool,  # Serverless-safe connection pooling
    }
    print(f"Using production database: {database_url[:50]}...")
else:
    # Development SQLite configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = compute_sqlite_uri()
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {
            "check_same_thread": False  # Allow SQLite to be used across threads
        }
    }
    print(f"Using SQLite database: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Configure for production vs development
if IS_PRODUCTION:
    # Production configuration
    app.config.update(
        WTF_CSRF_ENABLED=True,  # Enable CSRF protection in production
        SEND_FILE_MAX_AGE_DEFAULT=31536000,  # 1 year cache for static files in production
        SESSION_COOKIE_SECURE=True,   # Require HTTPS for cookies
        SESSION_COOKIE_SAMESITE="Strict",  # Strict CSRF protection
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_PERMANENT=False
    )
else:
    # Development configuration
    app.config.update(
        WTF_CSRF_ENABLED=False,  # Disable CSRF for API endpoints in development
        SEND_FILE_MAX_AGE_DEFAULT=0,  # No caching in development
        SESSION_COOKIE_SECURE=False,   # Allow non-HTTPS in development
        SESSION_COOKIE_SAMESITE="Lax",  # Less strict for development
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_PERMANENT=False
    )

# Initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

# Initialize CSRF protection 
csrf = None
if IS_PRODUCTION:
    csrf = CSRFProtect(app)
    print("CSRF protection enabled for production")
else:
    print("CSRF protection disabled for development")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Add ping route for health check
@app.route('/ping')
def ping():
    """Simple health check endpoint"""
    return 'OK'

# Add response headers for Replit Preview compatibility
@app.after_request
def after_request(response):
    """Add headers for environment compatibility"""
    # Security headers
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    if IS_PRODUCTION:
        # Production headers - secure
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        # No CORS in production for security
    else:
        # Development headers - allow CORS for Replit environment
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
            # Import models first
            import models  # noqa: F401
            from modules.inventory import models as inventory_models  # noqa: F401
            from models import Department  # noqa: F401
            
            if IS_PRODUCTION:
                # Production: Skip table creation and SQLite-specific configuration
                print("Production mode: Skipping database table creation (use migrations)")
            else:
                # Development: Configure SQLite and create tables
                event.listen(db.engine, 'connect', configure_sqlite_pragmas)
                print(f"SQLite PRAGMAs configured for: {app.config['SQLALCHEMY_DATABASE_URI']}")
                print(f"Instance identifier: {os.environ.get('SPA_DB_INSTANCE') or os.environ.get('REPL_SLUG') or 'default'}")
                
                # Create tables for development
                db.create_all()
                print("SQLite database tables created successfully")
                print(f"Database file location: {app.config['SQLALCHEMY_DATABASE_URI']}")
                
        except Exception as e:
            print(f"Database initialization warning: {e}")
            print("Continuing with existing database...")

        try:
            # Import and register basic routes
            import routes
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

# Department Management Routes
@app.route('/api/departments', methods=['GET'])
@login_required
def api_get_departments():
    """Get all departments"""
    try:
        departments = Department.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'departments': [{'id': d.id, 'name': d.name, 'display_name': d.display_name, 'description': d.description} for d in departments]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/departments', methods=['POST'])
@login_required
def api_create_department():
    """Create new department"""
    try:
        data = request.get_json()
        if not data or not data.get('name') or not data.get('display_name'):
            return jsonify({'success': False, 'error': 'Name and display name are required'}), 400

        # Check if department already exists
        existing = Department.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'success': False, 'error': 'Department already exists'}), 400

        department = Department(
            name=data['name'],
            display_name=data['display_name'],
            description=data.get('description', ''),
            is_active=True
        )

        db.session.add(department)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Department created successfully',
            'department': {
                'id': department.id,
                'name': department.name,
                'display_name': department.display_name,
                'description': department.description
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/departments/<int:dept_id>', methods=['PUT'])
@login_required
def api_update_department(dept_id):
    """Update department"""
    try:
        department = Department.query.get_or_404(dept_id)
        data = request.get_json()

        if data.get('name'):
            department.name = data['name']
        if data.get('display_name'):
            department.display_name = data['display_name']
        if data.get('description'):
            department.description = data['description']

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Department updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/departments/<int:dept_id>', methods=['DELETE'])
@login_required
def api_delete_department(dept_id):
    """Delete department"""
    try:
        department = Department.query.get_or_404(dept_id)
        department.is_active = False
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Department deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Exempt API routes from CSRF protection in production
if IS_PRODUCTION and csrf:
    # Exempt all view functions for routes that start with /api/
    exempted_count = 0
    for rule in app.url_map.iter_rules():
        if rule.rule.startswith('/api/') and rule.endpoint in app.view_functions:
            csrf.exempt(app.view_functions[rule.endpoint])
            exempted_count += 1
    
    print(f"Exempted {exempted_count} API view functions from CSRF protection")

# Ensure app is available for gunicorn
if __name__ != '__main__':
    # When imported by gunicorn or other WSGI servers
    print("App imported for WSGI deployment")