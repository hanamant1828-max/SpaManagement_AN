import os
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, login_required
# Department will be imported inside functions to avoid circular imports


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

# configure the database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure cache control for Replit webview
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['WTF_CSRF_ENABLED'] = True  # Enable CSRF for production security

# Session configuration for Replit environment
app.config.update(
    SECRET_KEY=os.environ.get("SESSION_SECRET"),  # No fallback for production security
    SESSION_COOKIE_SAMESITE="Strict", 
    SESSION_COOKIE_SECURE=True,   # production mode
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_PERMANENT=False
)

# Initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Basic routes removed to avoid conflicts with main application routes

# Initialize database and routes within app context
def init_app():
    """Initialize the application with proper error handling"""
    with app.app_context():
        try:
            # Make sure to import the models here or their tables won't be created
            import models  # noqa: F401
            # Import inventory models for database creation
            from modules.inventory import models as inventory_models  # noqa: F401
            # Import Department model for database creation
            from models import Department  # noqa: F401

            # Try to create tables, but handle conflicts gracefully
            db.create_all()
            print("Database initialized successfully")
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

# Ensure app is available for gunicorn
if __name__ != '__main__':
    # When imported by gunicorn or other WSGI servers
    print("App imported for WSGI deployment")