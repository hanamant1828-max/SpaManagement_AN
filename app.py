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
    # Only apply to SQLite connections (check if this is actually SQLite)
    if hasattr(dbapi_connection, 'execute') and 'sqlite' in str(type(dbapi_connection)).lower():
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

# Configure the database - use existing SQLite database
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

# Import and register packages blueprint first
try:
    from modules.packages.routes import packages_bp
    app.register_blueprint(packages_bp)
    print("Packages blueprint registered successfully")
except Exception as e:
    print(f"Error registering packages blueprint: {e}")

# Import routes.py removed due to route conflicts
# Adding specific missing routes instead

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

# Routes are imported via module views, avoiding import conflicts

# Unaki Booking API endpoints
@app.route('/api/unaki/services')
@login_required
def unaki_services():
    """Get all active services for Unaki booking"""
    try:
        from modules.services.services_queries import get_active_services
        services = get_active_services()
        services_data = []
        for service in services:
            services_data.append({
                'id': service.id,
                'name': service.name,
                'duration': service.duration,
                'price': float(service.price) if service.price else 0.0,
                'category': getattr(service, 'category', 'General'),
                'description': getattr(service, 'description', '')
            })
        return jsonify(services_data)
    except Exception as e:
        print(f"Error in unaki_services: {e}")
        return jsonify([])

@app.route('/api/unaki/staff')
@login_required
def unaki_staff():
    """Get all active staff for Unaki booking"""
    try:
        from modules.staff.staff_queries import get_staff_members
        staff = get_staff_members()
        staff_data = []
        for member in staff:
            staff_data.append({
                'id': member.id,
                'name': member.full_name or f"{member.first_name} {member.last_name}",
                'role': getattr(member, 'role', 'Staff'),
                'specialty': getattr(member, 'specialization', member.role if hasattr(member, 'role') else 'General'),
                'is_active': member.is_active
            })
        return jsonify(staff_data)
    except Exception as e:
        print(f"Error in unaki_staff: {e}")
        return jsonify([])

@app.route('/api/unaki/schedule')
@login_required
def unaki_schedule():
    """Get schedule data for Unaki booking"""
    try:
        from datetime import datetime, date, timedelta
        from modules.bookings.bookings_queries import get_appointments_by_date, get_staff_members

        # Get date parameter
        date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Get staff and appointments
        staff_members = get_staff_members()
        appointments = get_appointments_by_date(target_date)

        # Format staff data
        staff_data = []
        for staff in staff_members:
            staff_info = {
                'id': staff.id,
                'name': staff.full_name or f"{staff.first_name} {staff.last_name}",
                'specialty': getattr(staff, 'specialization', staff.role if hasattr(staff, 'role') else 'General'),
                'shift_start': '09:00',
                'shift_end': '17:00',
                'is_working': True
            }
            staff_data.append(staff_info)

        # Format appointments data
        appointments_data = []
        for appointment in appointments:
            appointment_info = {
                'id': appointment.id,
                'staffId': appointment.staff_id,
                'clientName': appointment.client.full_name if appointment.client else 'Unknown',
                'clientPhone': appointment.client.phone if appointment.client else '',
                'service': appointment.service.name if appointment.service else 'Service',
                'startTime': appointment.appointment_date.strftime('%H:%M'),
                'endTime': appointment.end_time.strftime('%H:%M') if appointment.end_time else None,
                'duration': appointment.service.duration if appointment.service else 60,
                'status': appointment.status,
                'notes': appointment.notes or ''
            }
            appointments_data.append(appointment_info)

        # Format breaks data (simplified for now)
        breaks_data = []

        return jsonify({
            'success': True,
            'date': date_str,
            'staff': staff_data,
            'appointments': appointments_data,
            'breaks': breaks_data
        })

    except Exception as e:
        print(f"Error in unaki_schedule: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'staff': [],
            'appointments': [],
            'breaks': []
        })

@app.route('/api/unaki/load-sample-data', methods=['POST'])
@login_required
def unaki_load_sample_data():
    """Load sample data for Unaki booking system"""
    try:
        from datetime import datetime, date, timedelta
        from modules.bookings.bookings_queries import create_appointment
        from models import Customer, Service, User

        # Create sample appointments for today
        today = date.today()
        sample_appointments = [
            {
                'client_name': 'Jessica Williams',
                'service_name': 'Deep Cleansing Facial',
                'start_time': '10:00',
                'duration': 90
            },
            {
                'client_name': 'David Brown', 
                'service_name': 'Swedish Massage',
                'start_time': '14:00',
                'duration': 60
            },
            {
                'client_name': 'Emma Thompson',
                'service_name': 'Hair Cut & Style',
                'start_time': '11:00',
                'duration': 75
            }
        ]

        created_count = 0
        for apt_data in sample_appointments:
            # Find or create customer
            customer = Customer.query.filter_by(full_name=apt_data['client_name']).first()
            if not customer:
                names = apt_data['client_name'].split(' ')
                customer = Customer(
                    first_name=names[0],
                    last_name=' '.join(names[1:]) if len(names) > 1 else '',
                    full_name=apt_data['client_name'],
                    phone=f"+1-555-{created_count:04d}",
                    email=f"{apt_data['client_name'].lower().replace(' ', '.')}@example.com"
                )
                db.session.add(customer)
                db.session.flush()

            # Find service
            service = Service.query.filter_by(name=apt_data['service_name']).first()
            if not service:
                service = Service(
                    name=apt_data['service_name'],
                    duration=apt_data['duration'],
                    price=100.0,
                    is_active=True
                )
                db.session.add(service)
                db.session.flush()

            # Get first available staff
            staff = User.query.filter_by(is_active=True).first()
            if staff:
                # Create appointment
                start_datetime = datetime.combine(today, datetime.strptime(apt_data['start_time'], '%H:%M').time())
                end_datetime = start_datetime + timedelta(minutes=apt_data['duration'])

                appointment_data = {
                    'client_id': customer.id,
                    'service_id': service.id,
                    'staff_id': staff.id,
                    'appointment_date': start_datetime,
                    'end_time': end_datetime,
                    'status': 'confirmed',
                    'notes': 'Sample appointment',
                    'amount': service.price
                }

                create_appointment(appointment_data)
                created_count += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Sample data loaded successfully! Created {created_count} appointments.',
            'data': {
                'appointments_created': created_count
            }
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error in unaki_load_sample_data: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to load sample data: {str(e)}'
        })

@app.route('/api/unaki/appointments', methods=['POST'])
@login_required
def unaki_create_appointment():
    """Create appointment for Unaki booking system"""
    try:
        from datetime import datetime, timedelta
        from modules.bookings.bookings_queries import create_appointment
        from models import Customer, Service, User

        data = request.get_json()

        # Validate required fields
        required_fields = ['staffId', 'clientName', 'serviceType', 'startTime', 'endTime']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        # Parse date and times
        appointment_date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
        start_datetime = datetime.combine(appointment_date, datetime.strptime(data['startTime'], '%H:%M').time())
        end_datetime = datetime.combine(appointment_date, datetime.strptime(data['endTime'], '%H:%M').time())

        # Find or create customer
        customer = Customer.query.filter_by(full_name=data['clientName']).first()
        if not customer:
            names = data['clientName'].split(' ')
            customer = Customer(
                first_name=names[0],
                last_name=' '.join(names[1:]) if len(names) > 1 else '',
                full_name=data['clientName'],
                phone=data.get('clientPhone', ''),
                email=f"{data['clientName'].lower().replace(' ', '.')}@customer.spa"
            )
            db.session.add(customer)
            db.session.flush()

        # Find or create service
        service = Service.query.filter_by(name=data['serviceType']).first()
        if not service:
            duration = int((end_datetime - start_datetime).total_seconds() / 60)
            service = Service(
                name=data['serviceType'],
                duration=duration,
                price=100.0,
                is_active=True
            )
            db.session.add(service)
            db.session.flush()

        # Verify staff exists
        staff = User.query.get(data['staffId'])
        if not staff:
            return jsonify({
                'success': False,
                'error': 'Staff member not found'
            }), 400

        # Create appointment
        appointment_data = {
            'client_id': customer.id,
            'service_id': service.id,
            'staff_id': data['staffId'],
            'appointment_date': start_datetime,
            'end_time': end_datetime,
            'status': 'confirmed',
            'notes': data.get('notes', ''),
            'amount': service.price
        }

        appointment = create_appointment(appointment_data)

        return jsonify({
            'success': True,
            'message': 'Appointment created successfully',
            'appointment': {
                'id': appointment.id,
                'staff_id': data['staffId'],
                'client_name': data['clientName'],
                'service_type': data['serviceType'],
                'start_time': data['startTime'],
                'end_time': data['endTime'],
                'date': appointment_date_str,
                'status': 'confirmed',
                'notes': data.get('notes', ''),
                'created_at': appointment.created_at.isoformat()
            }
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error in unaki_create_appointment: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to create appointment: {str(e)}'
        }), 500


@app.route('/unaki-booking')
@login_required
def unaki_booking():
    """Unaki Appointment Booking page"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('unaki_booking.html')

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