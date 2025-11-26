import os
import re
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event, func
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, login_required, current_user
from datetime import datetime, date, timedelta, time
import pytz
from utils import format_currency

# Department will be imported inside functions to avoid circular imports

# IST Timezone Configuration
# NOTE: All datetimes in the database are stored as NAIVE datetimes in IST timezone
# This avoids SQLAlchemy timezone errors while maintaining IST consistency
IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    """Get current datetime in IST timezone (aware)"""
    return datetime.now(IST)

def convert_to_ist(dt):
    """Convert a datetime object to IST timezone

    WARNING: This function assumes naive datetimes are in UTC.
    Since our database stores naive IST datetimes, do NOT use this
    on database timestamps - they are already in IST!
    """
    if dt is None:
        return None

    # If datetime is naive (no timezone), assume it's UTC
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)

    # Convert to IST
    return dt.astimezone(IST)

def get_ist_date_today():
    """Get today's date in IST timezone"""
    return get_ist_now().date()

def ist_time_to_string(time_obj):
    """Convert time object to IST time string"""
    if time_obj is None:
        return None
    return time_obj.strftime('%H:%M')

def naive_ist_to_string(dt, format_str='%H:%M'):
    """Convert naive IST datetime to string (assumes datetime is already in IST)"""
    if dt is None:
        return None
    return dt.strftime(format_str)


def compute_sqlite_uri():
    """Compute SQLite database URI for the current instance"""
    import shutil

    # Create base directory for databases
    base_dir = os.path.join(os.getcwd(), 'hanamantdatabase')
    os.makedirs(base_dir, exist_ok=True)

    # Determine instance identifier
    instance = os.environ.get('SPA_DB_INSTANCE') or os.environ.get('REPL_SLUG') or 'workspace'

    # Sanitize instance name to prevent path traversal
    instance = re.sub(r'[^A-Za-z0-9_-]', '_', instance)

    # Create absolute path to database file
    db_path = os.path.abspath(os.path.join(base_dir, f'{instance}.db'))

    # Auto-restore from default.db if workspace.db doesn't exist
    if instance == 'workspace' and not os.path.exists(db_path):
        default_db = os.path.join(base_dir, 'default.db')
        if os.path.exists(default_db):
            print(f"📦 First run detected - restoring from default.db")
            shutil.copy2(default_db, db_path)
            print(f"✅ Database restored to {db_path}")

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


def run_automatic_migrations():
    """
    Automatic migration function to fix database schema issues.
    This runs on every startup to ensure cloned projects have the correct schema.
    """
    import sqlite3

    # Get database path from SQLAlchemy URI
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if not db_uri or 'sqlite' not in db_uri:
        return

    # Extract database path from URI (sqlite:///path/to/db.db)
    db_path = db_uri.replace('sqlite:///', '')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        migrations_applied = False

        # Migration 1: shift_logs table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shift_logs'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(shift_logs)")
            shift_columns = [row[1] for row in cursor.fetchall()]

            if 'out_of_office_start' not in shift_columns:
                print("  → Adding column: shift_logs.out_of_office_start")
                cursor.execute("ALTER TABLE shift_logs ADD COLUMN out_of_office_start TIME")
                migrations_applied = True

            if 'out_of_office_end' not in shift_columns:
                print("  → Adding column: shift_logs.out_of_office_end")
                cursor.execute("ALTER TABLE shift_logs ADD COLUMN out_of_office_end TIME")
                migrations_applied = True

            if 'out_of_office_reason' not in shift_columns:
                print("  → Adding column: shift_logs.out_of_office_reason")
                cursor.execute("ALTER TABLE shift_logs ADD COLUMN out_of_office_reason VARCHAR(200)")
                migrations_applied = True

        # Migration 2: student_offers table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='student_offers'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(student_offers)")
            student_columns = [row[1] for row in cursor.fetchall()]

            if 'name' not in student_columns:
                print("  → Adding column: student_offers.name")
                cursor.execute("ALTER TABLE student_offers ADD COLUMN name VARCHAR(200)")
                migrations_applied = True

            if 'discount_percentage' not in student_columns:
                print("  → Adding column: student_offers.discount_percentage")
                cursor.execute("ALTER TABLE student_offers ADD COLUMN discount_percentage FLOAT")
                migrations_applied = True

        # Migration 3: service_packages table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='service_packages'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(service_packages)")
            service_package_columns = [row[1] for row in cursor.fetchall()]

            if 'package_name' not in service_package_columns:
                print("  → Adding column: service_packages.package_name")
                cursor.execute("ALTER TABLE service_packages ADD COLUMN package_name VARCHAR(255)")
                migrations_applied = True

            if 'description' not in service_package_columns:
                print("  → Adding column: service_packages.description")
                cursor.execute("ALTER TABLE service_packages ADD COLUMN description TEXT")
                migrations_applied = True

            if 'free_services' not in service_package_columns:
                print("  → Adding column: service_packages.free_services")
                cursor.execute("ALTER TABLE service_packages ADD COLUMN free_services INTEGER DEFAULT 0")
                migrations_applied = True

            if 'sessions' not in service_package_columns:
                print("  → Adding column: service_packages.sessions")
                cursor.execute("ALTER TABLE service_packages ADD COLUMN sessions INTEGER DEFAULT 1")
                migrations_applied = True

            if 'price' not in service_package_columns:
                print("  → Adding column: service_packages.price")
                cursor.execute("ALTER TABLE service_packages ADD COLUMN price FLOAT DEFAULT 0")
                migrations_applied = True

            if 'validity_days' not in service_package_columns:
                print("  → Adding column: service_packages.validity_days")
                cursor.execute("ALTER TABLE service_packages ADD COLUMN validity_days INTEGER")
                migrations_applied = True

        if migrations_applied:
            conn.commit()
            print("  ✅ Database schema updated successfully")
        else:
            print("  ✅ Database schema is up to date")

        conn.close()

    except Exception as e:
        print(f"  ⚠️ Migration error: {e}")
        if 'conn' in locals():
            conn.close()


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

# Configure the database - Use SQLite database from project structure
app.config["SQLALCHEMY_DATABASE_URI"] = compute_sqlite_uri()
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {
        "check_same_thread": False
    }
}
print(f"✅ Using SQLite database: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Configure cache control for Replit environment
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for API endpoints in development

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True  # Persistent sessions
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'spa_session:'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_NAME'] = 'spa_session'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to False for development
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow cookies on all subdomains
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# Additional Flask-Login configuration
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
app.config['REMEMBER_COOKIE_SECURE'] = False
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SAMESITE'] = 'Lax'

# Initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

# Initialize CSRF protection (disabled for development)
# csrf = CSRFProtect(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'  # Protect against session hijacking
login_manager.refresh_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    # Import inside function to avoid circular imports
    from models import User
    print(f"🔍 Loading user with ID: {user_id}")
    user = User.query.get(int(user_id))
    if user:
        print(f"✅ User loaded: {user.username}, Active: {user.is_active}")
    else:
        print(f"❌ User with ID {user_id} not found")
    return user

@login_manager.unauthorized_handler
def unauthorized():
    # Return JSON for AJAX requests - check multiple indicators
    content_type = request.headers.get('Content-Type', '')
    accept = request.headers.get('Accept', '')

    if (request.is_json or
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
        'application/json' in content_type or
        'application/json' in accept or
        request.path.startswith('/api/')):
        return jsonify({'success': False, 'error': 'Please log in to access this feature'}), 401

    # Redirect to login page for regular requests
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('login', next=request.url))

# Make utils available in all templates
@app.context_processor
def utility_processor():
    """Add utility functions to Jinja context"""
    from utils import format_currency, format_datetime

    def get_month_name(month_num):
        """Get month name from number"""
        months = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        try:
            return months[int(month_num)]
        except (IndexError, ValueError):
            return ''

    def format_date(date_obj):
        """Format date object"""
        if not date_obj:
            return 'N/A'
        try:
            return date_obj.strftime('%d %b %Y')
        except:
            return str(date_obj)

    def truncate_text(text, length=50):
        """Truncate text to specified length"""
        if not text:
            return ''
        text = str(text)
        return text[:length] + '...' if len(text) > length else text

    def calculate_age(date_of_birth):
        """Calculate age from date of birth"""
        if not date_of_birth:
            return 'N/A'
        try:
            from datetime import date
            today = date.today()
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            return age
        except:
            return 'N/A'

    def get_status_badge_class(status):
        """Get Bootstrap badge class for status"""
        status_map = {
            'new_customer': 'primary',
            'regular_customer': 'info',
            'loyal_customer': 'success',
            'inactive_customer': 'warning',
            'inactive': 'secondary',
            'active': 'success',
            'pending': 'warning',
            'completed': 'success',
            'cancelled': 'danger'
        }
        return status_map.get(str(status).lower(), 'secondary')

    def check_permission(module, action):
        """Template helper to check permissions"""
        from flask_login import current_user
        if not current_user or not current_user.is_authenticated:
            return False
        permission_name = f"{module}_{action}"
        return current_user.has_permission(permission_name)

    return dict(
        utils=dict(
            get_month_name=get_month_name,
            format_date=format_date,
            truncate_text=truncate_text,
            format_currency=format_currency,
            format_datetime=format_datetime,
            calculate_age=calculate_age,
            get_status_badge_class=get_status_badge_class
        ),
        check_permission=check_permission
    )

# Add root route
@app.route('/')
def index():
    """Root route - redirect based on authentication"""
    from flask_login import current_user
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Add ping route for health check
@app.route('/ping')
def ping():
    """Simple health check endpoint"""
    return 'OK'

@app.route('/debug-routes')
def debug_routes():
    """Debug route to check registered routes"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    return {'routes': routes}

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

# Initialize database and routes within app context
def init_app():
    """Initialize the application with proper error handling"""
    with app.app_context():
        try:
            # Configure SQLite pragmas only if using SQLite
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            if db_uri and 'sqlite' in db_uri:
                event.listen(db.engine, "connect", configure_sqlite_pragmas)
                print(f"SQLite database configured: {db_uri}")
            else:
                print(f"PostgreSQL database configured: {db_uri}")

            # Make sure to import the models here or their tables won't be created
            import models  # noqa: F401
            # Import inventory models for database creation
            from modules.inventory import models as inventory_models  # noqa: F401
            # Import Department model for database creation
            from models import Department  # noqa: F401

            # Try to create tables, but handle conflicts gracefully
            db.create_all()
            print("Database tables created successfully")
            print(f"Database connection: {db_uri}")

            # Auto-initialize database if it's empty (first run after clone)
            from models import User
            if User.query.count() == 0:
                print("\n📦 First run detected - initializing database with default data...")
                try:
                    from init_database import init_database
                    init_database()
                except Exception as init_error:
                    print(f"⚠️ Auto-initialization warning: {init_error}")
                    print("💡 You can manually run: python init_database.py")

            # Run automatic database migrations for missing columns
            if db_uri and 'sqlite' in db_uri:
                try:
                    print("Checking for required database schema updates...")
                    run_automatic_migrations()
                    print("Database schema check completed")
                except Exception as migration_error:
                    print(f"Migration warning: {migration_error}")

        except Exception as e:
            print(f"Database initialization warning: {e}")
            print("Continuing with existing database...")

        print("Database initialization completed")

# Initialize the app
init_app()

# Packages blueprint will be imported later if needed

# Import routes.py removed to avoid route conflicts
# Adding specific missing routes instead

# Import views selectively to avoid route conflicts
try:
    from modules.auth.auth_views import *
    print("✅ Auth views imported")
except Exception as e:
    print(f"⚠️ Auth views import error: {e}")

try:
    from modules.dashboard.dashboard_views import *
    print("✅ Dashboard views imported")
except Exception as e:
    print(f"⚠️ Dashboard views import error: {e}")

try:
    from modules.clients.clients_views import *
    print("✅ Clients views imported")
except Exception as e:
    print(f"⚠️ Clients views import error: {e}")

try:
    from modules.services.services_views import *
    print("✅ Services views imported")
except Exception as e:
    print(f"⚠️ Services views import error: {e}")

try:
    from modules.expenses.expenses_views import *
    print("✅ Expenses views imported")
except Exception as e:
    print(f"⚠️ Expenses views import error: {e}")

try:
    from modules.reports.reports_views import *
    print("✅ Reports views imported")
except Exception as e:
    print(f"⚠️ Reports views import error: {e}")

try:
    from modules.settings.settings_views import *
    print("✅ Settings views imported - Department API routes loaded")
except Exception as e:
    print(f"⚠️ Settings views import error: {e}")
    import traceback
    traceback.print_exc()

try:
    from modules.checkin.checkin_views import *
    print("✅ Checkin views imported")
    # Register face recognition blueprint
    from modules.checkin.face_recognition_api import face_recognition_bp
    app.register_blueprint(face_recognition_bp)
    print("✅ Face recognition API registered")
except Exception as e:
    print(f"⚠️ Checkin views import error: {e}")

try:
    from modules.inventory.views import *
    print("✅ Inventory views imported")
except Exception as e:
    print(f"⚠️ Inventory views import error: {e}")

try:
    from modules.inventory.inventory_reports_views import *
    print("✅ Inventory reports views imported")
except Exception as e:
    print(f"⚠️ Inventory reports views import error: {e}")

# Import bookings views last to ensure no conflicts
try:
    from modules.bookings.bookings_views import *
    print("✅ Bookings views imported")
except Exception as e:
    print(f"⚠️ Bookings views import error: {e}")

# Import specific modules referenced in base.html navigation
try:
    from modules.staff.shift_scheduler_views import shift_scheduler_bp
    app.register_blueprint(shift_scheduler_bp)
    print("✅ Shift scheduler views imported")
except Exception as e:
    print(f"⚠️ Shift scheduler views import error: {e}")

try:
    from modules.billing.integrated_billing_views import *
    print("✅ Integrated billing views imported")
except Exception as e:
    print(f"⚠️ Integrated billing views import error: {e}")

# Import packages blueprint first
try:
    from modules.packages.routes import packages_bp
    app.register_blueprint(packages_bp)
    print("✅ Packages blueprint registered")
except Exception as e:
    print(f"⚠️ Packages blueprint import error: {e}")

# Import packages views
try:
    from modules.packages.new_packages_views import *
    print("✅ New packages views imported")
except Exception as e:
    print(f"⚠️ New packages views import error: {e}")

try:
    from modules.packages.membership_views import *
    print("✅ Membership views imported")
except Exception as e:
    print(f"⚠️ Membership views import error: {e}")

try:
    from modules.packages.prepaid_views import *
    print("✅ Prepaid views imported")
except Exception as e:
    print(f"⚠️ Prepaid views import error: {e}")

try:
    from modules.packages.assign_packages_routes import assign_packages_bp
    app.register_blueprint(assign_packages_bp)
    print("✅ Assign packages blueprint registered")
except Exception as e:
    print(f"⚠️ Assign packages blueprint import error: {e}")

# Student offer views module doesn't exist yet - commented out to prevent errors
# try:
#     from modules.packages.student_offer_views import *
#     print("✅ Student offer views imported")
# except Exception as e:
#     print(f"⚠️ Student offer views import error: {e}")

# Import staff views (routes use @app.route directly)
try:
    from modules.staff.staff_views import *
    print("✅ Staff views imported")
except Exception as e:
    print(f"⚠️ Staff views import error: {e}")

# Import notifications views
try:
    from modules.notifications.notifications_views import *
    print("✅ Notifications views imported")
except Exception as e:
    print(f"⚠️ Notifications views import error: {e}")

# Import user management views
try:
    from modules.user_management.user_management_views import *
    print("✅ User management views imported")
except Exception as e:
    print(f"⚠️ User management views import error: {e}")

# Routes are imported via module views, avoiding import conflicts

# Unaki Booking API endpoints
@app.route('/api/unaki/services')
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

@app.route('/api/unaki/clients')
def unaki_clients():
    """Get all active clients for Unaki booking"""
    try:
        from modules.clients.clients_queries import get_all_customers
        clients = get_all_customers()
        clients_data = []
        for client in clients:
            clients_data.append({
                'id': client.id,
                'name': client.full_name or f"{client.first_name} {client.last_name}",
                'phone': client.phone,
                'email': client.email,
                'is_active': client.is_active
            })
        return jsonify(clients_data)
    except Exception as e:
        print(f"Error in unaki_clients: {e}")
        return jsonify([])

@app.route('/api/unaki/schedule')
def unaki_schedule():
    """Get schedule data for Unaki booking with shift logs integration"""
    try:
        from datetime import datetime, date, timedelta
        from models import UnakiBooking, ShiftManagement, ShiftLogs
        from models import User # Import User model here

        # Get date parameter and clean it
        date_str = request.args.get('date', date.today().strftime('%Y-%m-%d')).strip()

        # Validate date format
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date format',
                'staff': [],
                'appointments': [],
                'breaks': []
            }), 400

        # Debug: Log the date we're querying for
        print(f"🗓️  Querying Unaki bookings for date: {target_date} (from parameter: {date_str})")

        # Get active staff using User model
        try:
            staff_members = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()
        except Exception as e:
            print(f"Error getting staff members: {e}")
            staff_members = []

        # Get Unaki bookings for the target date
        bookings = UnakiBooking.query.filter_by(appointment_date=target_date).all()

        print(f"📋 Loading {len(bookings)} bookings for {target_date}")

        bookings_list = []
        for booking in bookings:
            print(f"  📌 Booking {booking.id}: source='{booking.booking_source}', method='{booking.booking_method}'")

        # Enhanced shift logs integration for staff data
        staff_data = []
        for staff in staff_members:
            try:
                # Get shift management for this staff member
                shift_management = ShiftManagement.query.filter(
                    ShiftManagement.staff_id == staff.id,
                    ShiftManagement.from_date <= target_date,
                    ShiftManagement.to_date >= target_date
                ).first()

                # Get specific shift log for this date
                shift_log = None
                if shift_management:
                    shift_log = ShiftLogs.query.filter(
                        ShiftLogs.shift_management_id == shift_management.id,
                        ShiftLogs.individual_date == target_date
                    ).first()

                # Enhanced staff availability logic based on shift logs with validation
                if shift_log:
                    shift_start = shift_log.shift_start_time.strftime('%H:%M') if shift_log.shift_start_time else '09:00'
                    shift_end = shift_log.shift_end_time.strftime('%H:%M') if shift_log.shift_end_time else '17:00'

                    # Safely format break times with proper validation
                    break_start = None
                    break_end = None
                    try:
                        if shift_log.break_start_time:
                            break_start = shift_log.break_start_time.strftime('%H:%M')
                        if shift_log.break_end_time:
                            break_end = shift_log.break_end_time.strftime('%H:%M')
                    except Exception as time_error:
                        print(f"Error formatting break times for staff {staff.id}: {time_error}")
                        break_start = None
                        break_end = None

                    # Safely format out-of-office times with proper validation
                    ooo_start = None
                    ooo_end = None
                    ooo_reason = None
                    try:
                        if shift_log.out_of_office_start:
                            ooo_start = shift_log.out_of_office_start.strftime('%H:%M')
                        if shift_log.out_of_office_end:
                            ooo_end = shift_log.out_of_office_end.strftime('%H:%M')
                        if shift_log.out_of_office_reason:
                            ooo_reason = shift_log.out_of_office_reason
                    except Exception as ooo_error:
                        print(f"Error formatting out-of-office times for staff {staff.id}: {ooo_error}")
                        ooo_start = None
                        ooo_end = None
                        ooo_reason = None

                    shift_status = shift_log.status

                    # Define holiday and off-day status sets
                    HOLIDAY_STATUSES = {'holiday'}
                    OFFDAY_STATUSES = {'absent', 'leave', 'weekoff', 'off', 'not_scheduled'}

                    # Determine working status and day_status based on shift log status
                    status_raw = (shift_status or '').strip().lower()
                    day_status = "scheduled"

                    if status_raw in HOLIDAY_STATUSES:
                        is_working = False
                        shift_start, shift_end = None, None
                        day_status = "holiday"
                        availability_status = 'Holiday'
                    elif status_raw in OFFDAY_STATUSES:
                        is_working = False
                        shift_start, shift_end = None, None
                        day_status = "off"
                        availability_status = 'Off Day'
                    else:
                        is_working = status_raw in ['scheduled', 'completed']
                        day_status = "scheduled" if is_working else "off"
                        availability_status = {
                            'scheduled': 'Working',
                            'completed': 'Completed Shift'
                        }.get(status_raw, 'Unknown')

                    # Calculate break duration if break times exist
                    break_duration = None
                    break_display = 'No Break'
                    if break_start and break_end:
                        try:
                            break_display = shift_log.get_break_time_display()
                            # Calculate minutes for duration
                            break_start_mins = int(break_start.split(':')[0]) * 60 + int(break_start.split(':')[1])
                            break_end_mins = int(break_end.split(':')[0]) * 60 + int(break_end.split(':')[1])
                            break_duration = break_end_mins - break_start_mins
                        except Exception as break_error:
                            print(f"Break calculation error for staff {staff.id}: {break_error}")
                            break_display = 'Break Error'

                    # Shift display with duration
                    try:
                        shift_start_mins = int(shift_start.split(':')[0]) * 60 + int(shift_start.split(':')[1])
                        shift_end_mins = int(shift_end.split(':')[0]) * 60 + int(shift_end.split(':')[1])
                        total_shift_mins = shift_end_mins - shift_start_mins
                        shift_hours = total_shift_mins // 60
                        shift_mins = total_shift_mins % 60
                        shift_display = f"{shift_start} - {shift_end} ({shift_hours}h {shift_mins}m)"
                    except Exception as shift_error:
                        print(f"Shift calculation error for staff {staff.id}: {shift_error}")
                        shift_display = f"{shift_start} - {shift_end}"

                else:
                    # No shift log found - check if it's an off day or no schedule
                    if shift_management:
                        # Shift management exists but no log for this date = OFF DAY (like Sunday)
                        shift_start = None
                        shift_end = None
                        is_working = False
                        availability_status = 'Off Day'
                        shift_status = 'offday'
                        day_status = 'offday'
                    else:
                        # No shift management at all
                        shift_start = None
                        shift_end = None
                        is_working = False
                        availability_status = 'Not Scheduled'
                        shift_status = 'not_scheduled'
                        day_status = 'not_scheduled'

                    break_start = None
                    break_end = None
                    break_duration = None
                    break_display = 'No Break'
                    shift_display = 'OFF DAY' if shift_management else 'Not Scheduled'
                    ooo_start = None
                    ooo_end = None
                    ooo_reason = None

                # Build breaks array for frontend rendering
                breaks = []
                if break_start and break_end:
                    breaks.append({
                        "start": break_start,
                        "end": break_end
                    })
                    print(f"    ☕ Break added: {break_start} - {break_end}")

                # Build out-of-office array for frontend rendering
                ooo = []
                if ooo_start and ooo_end:
                    ooo.append({
                        "start": ooo_start,
                        "end": ooo_end,
                        "reason": ooo_reason or "Out of Office"
                    })
                    print(f"    🚫 OOO added: {ooo_start} - {ooo_end}, reason: {ooo_reason or 'N/A'}")

                staff_info = {
                    'id': staff.id,
                    'name': staff.full_name or f"{staff.first_name} {staff.last_name}",
                    'specialty': getattr(staff, 'specialization', staff.role if hasattr(staff, 'role') else 'General'),
                    'role': getattr(staff, 'role', 'Staff'),
                    'shift_start': shift_start,
                    'shift_end': shift_end,
                    'break_start': break_start,
                    'break_end': break_end,
                    'break_duration': break_duration,
                    'break_display': break_display,
                    'breaks': breaks,
                    'ooo': ooo,
                    'is_working': is_working,
                    'shift_status': shift_status,
                    'day_status': day_status,
                    'availability_status': availability_status,
                    'shift_display': shift_display,
                    'has_shift_log': shift_log is not None,
                    'has_shift_management': shift_management is not None,
                    'shift_management_id': shift_management.id if shift_management else None,
                    'shift_log_id': shift_log.id if shift_log else None,
                    'is_active': staff.is_active
                }
                staff_data.append(staff_info)

            except Exception as staff_error:
                print(f"Error processing staff {staff.id}: {staff_error}")
                # Add basic staff info even if shift processing fails
                staff_info = {
                    'id': staff.id,
                    'name': staff.full_name or f"{staff.first_name} {staff.last_name}",
                    'specialty': getattr(staff, 'role', 'Staff'),
                    'role': getattr(staff, 'role', 'Staff'),
                    'shift_start': '09:00',
                    'shift_end': '17:00',
                    'break_start': None,
                    'break_end': None,
                    'break_duration': None,
                    'break_display': 'No Break',
                    'breaks': [],
                    'ooo': [],
                    'is_working': staff.is_active,
                    'shift_status': 'error',
                    'day_status': 'scheduled',
                    'availability_status': 'Error Loading',
                    'shift_display': '09:00 - 17:00 (Error)',
                    'has_shift_log': False,
                    'has_shift_management': False,
                    'shift_management_id': None,
                    'shift_log_id': None,
                    'is_active': staff.is_active
                }
                staff_data.append(staff_info)

        # Format Unaki bookings data with proper IST time handling
        # Filter out completed and paid appointments - they are already billed
        appointments_data = []
        for booking in bookings:
            # Skip appointments that are completed AND paid (already billed)
            if booking.status == 'completed' and booking.payment_status == 'paid':
                print(f"🚫 Hiding paid appointment: {booking.id} - {booking.client_name} - Status: {booking.status}, Payment: {booking.payment_status}")
                continue

            print(f"✅ Showing appointment: {booking.id} - {booking.client_name} - Status: {booking.status}, Payment: {booking.payment_status}")

            # Ensure end_time is properly formatted
            end_time_str = booking.end_time.strftime('%H:%M') if booking.end_time else None

            appointment_info = {
                'id': booking.id,
                'staffId': booking.staff_id,
                'clientName': booking.client_name,
                'clientPhone': booking.client_phone or '',
                'service': booking.service_name,
                'startTime': booking.start_time.strftime('%H:%M'),
                'endTime': end_time_str,
                'duration': booking.service_duration,
                'status': booking.status,
                'notes': booking.notes or '',
                'amount': float(booking.service_price) if booking.service_price else 0.0,
                'payment_status': booking.payment_status,
                'booking_source': booking.booking_source or 'manual'  # Default to manual if not set
            }
            appointments_data.append(appointment_info)

        # Format breaks data from shift logs
        breaks_data = []
        for staff in staff_members:
            # Get shift management for this staff member
            shift_management = ShiftManagement.query.filter(
                ShiftManagement.staff_id == staff.id,
                ShiftManagement.from_date <= target_date,
                ShiftManagement.to_date >= target_date
            ).first()

            if shift_management:
                shift_log = ShiftLogs.query.filter(
                    ShiftLogs.shift_management_id == shift_management.id,
                    ShiftLogs.individual_date == target_date
                ).first()

                # Add break data if available with proper validation
                if shift_log and shift_log.break_start_time and shift_log.break_end_time:
                    try:
                        break_start_str = shift_log.break_start_time.strftime('%H:%M') if shift_log.break_start_time else None
                        break_end_str = shift_log.break_end_time.strftime('%H:%M') if shift_log.break_end_time else None

                        if break_start_str and break_end_str:
                            break_info = {
                                'id': f'break_{staff.id}_{target_date}',
                                'staff_id': staff.id,
                                'start_time': break_start_str,
                                'end_time': break_end_str,
                                'type': 'break',
                                'title': 'Break Time'
                            }
                            breaks_data.append(break_info)
                    except Exception as break_error:
                        print(f"Error formatting break time for staff {staff.id}: {break_error}")

        # Debug: Log appointments by staff ID
        staff_appointment_counts = {}
        for apt in appointments_data:
            staff_id = apt['staffId']
            if staff_id not in staff_appointment_counts:
                staff_appointment_counts[staff_id] = []
            staff_appointment_counts[staff_id].append(apt)

        print(f"🔍 Appointments distribution by staff:")
        for staff_id, staff_appointments in staff_appointment_counts.items():
            staff_name = next((s['name'] for s in staff_data if s['id'] == staff_id), f'Staff {staff_id}')
            print(f"   Staff {staff_id} ({staff_name}): {len(staff_appointments)} appointments")
            for apt in staff_appointments:
                print(f"     - {apt['clientName']} - {apt['service']} ({apt['startTime']} - {apt['endTime']})")

        if not appointments_data:
            print("🔍 No appointments found for this date")

        # Get current IST time for frontend
        ist_now = get_ist_now()

        return jsonify({
            'success': True,
            'date': date_str,
            'timezone': 'Asia/Kolkata',
            'timezone_offset': '+05:30',
            'current_ist_time': ist_now.strftime('%H:%M'),
            'current_ist_time_full': ist_now.strftime('%H:%M:%S'),
            'current_ist_datetime': ist_now.isoformat(),
            'current_ist_date': ist_now.strftime('%Y-%m-%d'),
            'staff': staff_data,
            'appointments': appointments_data,
            'breaks': breaks_data
        })

    except Exception as e:
        import traceback
        print(f"Error in unaki_schedule: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while loading schedule data',
            'staff': [],
            'appointments': [],
            'breaks': []
        }), 500

@app.route('/api/unaki/load-sample-data', methods=['POST'])
def unaki_load_sample_data():
    """Load sample data for Unaki booking system - clears existing data first"""
    try:
        from datetime import datetime, date, time
        from models import UnakiBooking

        # First, clear ALL existing UnakiBooking records for today to ensure clean state
        target_date = date.today()
        existing_bookings = UnakiBooking.query.filter_by(appointment_date=target_date).all()

        print(f"🧹 Clearing {len(existing_bookings)} existing bookings for {target_date}")
        for booking in existing_bookings:
            db.session.delete(booking)

        # Force commit to ensure data is cleared
        db.session.commit()
        print(f"✅ Cleared all existing bookings")

        # Verify the clear worked
        remaining_count = UnakiBooking.query.filter_by(appointment_date=target_date).count()
        if remaining_count > 0:
            print(f"⚠️ Warning: {remaining_count} bookings still remain, clearing again...")
            UnakiBooking.query.filter_by(appointment_date=target_date).delete()
            db.session.commit()

        # Get today's date
        today_str = date.today().strftime('%Y-%m-%d')

        # Get all active staff members for proper distribution
        from models import User
        active_staff = User.query.filter_by(is_active=True).all()

        if not active_staff:
            return jsonify({
                'success': False,
                'error': 'No active staff members found. Please add staff members first.'
            }), 400

        print(f"👥 Found {len(active_staff)} active staff members for sample data")

        # Find Emily Davis ID specifically for consecutive bookings
        emily_davis = None
        for staff in active_staff:
            if staff.id == 3 or (hasattr(staff, 'first_name') and staff.first_name == 'Emily' and hasattr(staff, 'last_name') and staff.last_name == 'Davis'):
                emily_davis = staff
                break

        if not emily_davis:
            emily_davis = active_staff[min(2, len(active_staff)-1)]  # Use third staff as fallback

        # Sample booking data with variety - Adding comprehensive bookings for Admin User (ID: 11)
        sample_bookings = [
            # Admin User (ID: 11) - Complete day with various durations
            {
                'client_name': 'Emma Watson',
                'client_phone': '+1-555-1001',
                'service_name': 'Quick Touch-up',
                'duration': 5,
                'price': 25.0,
                'staff_id': 11,
                'start_time': '08:00',
                'end_time': '08:05',
                'date': today_str,
                'notes': '5-minute quick service for Admin'
            },
            {
                'client_name': 'Scarlett Johansson',
                'client_phone': '+1-555-1002',
                'service_name': 'Express Consultation',
                'duration': 10,
                'price': 35.0,
                'staff_id': 11,
                'start_time': '08:10',
                'end_time': '08:20',
                'date': today_str,
                'notes': '10-minute consultation with Admin'
            },
            {
                'client_name': 'Jennifer Lawrence',
                'client_phone': '+1-555-1003',
                'service_name': 'Quick Eyebrow Trim',
                'duration': 15,
                'price': 45.0,
                'staff_id': 11,
                'start_time': '08:25',
                'end_time': '08:40',
                'date': today_str,
                'notes': '15-minute eyebrow service'
            },
            {
                'client_name': 'Anne Hathaway',
                'client_phone': '+1-555-1004',
                'service_name': 'Mini Facial Express',
                'duration': 25,
                'price': 65.0,
                'staff_id': 11,
                'start_time': '08:45',
                'end_time': '09:10',
                'date': today_str,
                'notes': '25-minute express facial treatment'
            },
            {
                'client_name': 'Natalie Portman',
                'client_phone': '+1-555-1005',
                'service_name': 'Premium Face Treatment',
                'duration': 45,
                'price': 95.0,
                'staff_id': 11,
                'start_time': '09:15',
                'end_time': '10:00',
                'date': today_str,
                'notes': '45-minute premium facial service'
            },
            {
                'client_name': 'Reese Witherspoon',
                'client_phone': '+1-555-1006',
                'service_name': 'Standard Massage',
                'duration': 60,
                'price': 120.0,
                'staff_id': 11,
                'start_time': '10:05',
                'end_time': '11:05',
                'date': today_str,
                'notes': 'Classic 60-minute massage therapy'
            },
            {
                'client_name': 'Cameron Diaz',
                'client_phone': '+1-555-1007',
                'service_name': 'Luxury Spa Package',
                'duration': 75,
                'price': 150.0,
                'staff_id': 11,
                'start_time': '11:10',
                'end_time': '12:25',
                'date': today_str,
                'notes': '75-minute luxury spa treatment'
            },
            {
                'client_name': 'Julia Roberts',
                'client_phone': '+1-555-1008',
                'service_name': 'Extended Wellness Session',
                'duration': 90,
                'price': 180.0,
                'staff_id': 11,
                'start_time': '12:30',
                'end_time': '14:00',
                'date': today_str,
                'notes': '90-minute comprehensive wellness treatment'
            },
            {
                'client_name': 'Sandra Bullock',
                'client_phone': '+1-555-1009',
                'service_name': 'Afternoon Rejuvenation',
                'duration': 60,
                'price': 125.0,
                'staff_id': 11,
                'start_time': '14:05',
                'end_time': '15:05',
                'date': today_str,
                'notes': 'Afternoon renewal session'
            },
            {
                'client_name': 'Angelina Jolie',
                'client_phone': '+1-555-1010',
                'service_name': 'Celebrity Premium Treatment',
                'duration': 75,
                'price': 200.0,
                'staff_id': 11,
                'start_time': '15:10',
                'end_time': '16:25',
                'date': today_str,
                'notes': 'VIP treatment for celebrity client'
            },
            {
                'client_name': 'Charlize Theron',
                'client_phone': '+1-555-1011',
                'service_name': 'Evening Relaxation Package',
                'duration': 45,
                'price': 110.0,
                'staff_id': 11,
                'start_time': '16:30',
                'end_time': '17:15',
                'date': today_str,
                'notes': 'End-of-day relaxation treatment'
            },

            # Other staff bookings (reduced to make room for admin)
            {
                'client_name': 'Rachel Green',
                'client_phone': '+1-555-0201',
                'service_name': 'Morning Facial Treatment',
                'duration': 60,
                'price': 85.0,
                'staff_id': 3,
                'start_time': '09:00',
                'end_time': '10:00',
                'date': today_str,
                'notes': 'Fresh morning glow treatment'
            },
            {
                'client_name': 'Monica Geller',
                'client_phone': '+1-555-0202',
                'service_name': 'Deep Cleansing Facial',
                'duration': 60,
                'price': 95.0,
                'staff_id': 3,
                'start_time': '10:30',
                'end_time': '11:30',
                'date': today_str,
                'notes': 'Perfectionist client - attention to detail'
            },
            {
                'client_name': 'Phoebe Buffay',
                'client_phone': '+1-555-0203',
                'service_name': 'Relaxation Massage',
                'duration': 60,
                'price': 80.0,
                'staff_id': 3,
                'start_time': '13:00',
                'end_time': '14:00',
                'date': today_str,
                'notes': 'Loves essential oils and crystals'
            },
            {
                'client_name': 'Jessica Williams',
                'client_phone': '+1-555-0101',
                'service_name': 'Hair Styling Session',
                'duration': 90,
                'price': 125.0,
                'staff_id': 1,
                'start_time': '10:00',
                'end_time': '11:30',
                'date': today_str,
                'notes': 'Special event styling'
            },
            {
                'client_name': 'David Brown',
                'client_phone': '+1-555-0102',
                'service_name': 'Manicure & Pedicure',
                'duration': 60,
                'price': 65.0,
                'staff_id': 2,
                'start_time': '14:00',
                'end_time': '15:00',
                'date': today_str,
                'notes': 'Businessman grooming session'
            },
            {
                'client_name': 'Sarah Johnson',
                'client_phone': '+1-555-0103',
                'service_name': 'Body Scrub Treatment',
                'duration': 60,
                'price': 75.0,
                'staff_id': 2,
                'start_time': '09:30',
                'end_time': '10:30',
                'date': today_str,
                'notes': 'Exfoliating body treatment'
            }
        ]

        created_bookings = 0
        print(f"🚀 Creating {len(sample_bookings)} fresh sample bookings...")

        for booking_data in sample_bookings:
            # Parse date and times
            appointment_date = datetime.strptime(booking_data['date'], '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(booking_data['start_time'], '%H:%M').time()
            end_time_obj = datetime.strptime(booking_data['end_time'], '%H:%M').time()

            # Create UnakiBooking record
            unaki_booking = UnakiBooking(
                client_name=booking_data['client_name'],
                client_phone=booking_data['client_phone'],
                client_email=f"{booking_data['client_name'].lower().replace(' ', '.')}@example.com",
                staff_id=booking_data['staff_id'],
                staff_name=f'Staff {booking_data["staff_id"]}',
                service_name=booking_data['service_name'],
                service_duration=booking_data['duration'],
                service_price=booking_data['price'],
                appointment_date=appointment_date,
                start_time=start_time_obj,
                end_time=end_time_obj,
                status='confirmed',
                notes=booking_data['notes'],
                booking_source='unaki_system',
                booking_method='sample_data',
                amount_charged=booking_data['price'],
                payment_status='pending',
                created_at=datetime.utcnow()
            )

            db.session.add(unaki_booking)
            created_bookings += 1
            print(f"   ✅ Created: {booking_data['client_name']} - {booking_data['service_name']} at {booking_data['start_time']} for Staff ID {booking_data['staff_id']}")

        db.session.commit()
        print(f"🎉 Successfully created {created_bookings} fresh sample bookings")

        return jsonify({
            'success': True,
            'message': f'Sample data loaded successfully! Created {created_bookings} Unaki bookings.',
            'data': {
                'bookings_created': created_bookings,
                'bookings_cleared': len(existing_bookings)
            }
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error loading sample data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to load sample data: {str(e)}'
        }), 500

@app.route('/api/unaki/create-appointment', methods=['POST'])
@app.route('/api/unaki/appointments', methods=['POST'])
def unaki_create_appointment():
    """Create appointment for Unaki booking system using UnakiBooking table"""
    try:
        from datetime import datetime, timedelta, time
        from models import UnakiBooking, User, Service, Customer

        data = request.get_json()
        print(f"Received booking data: {data}")

        # Handle both old and new field names for flexibility
        staff_id = data.get('staff_id') or data.get('staffId')
        client_name = data.get('client_name') or data.get('clientName')
        service_type = data.get('service_name') or data.get('serviceType') or data.get('service')
        start_time = data.get('start_time') or data.get('startTime')
        end_time = data.get('end_time') or data.get('endTime')
        appointment_date_str = data.get('appointment_date') or data.get('date') or data.get('appointmentDate')

        # Validate required fields and collect missing ones
        missing_fields = []

        if not staff_id:
            missing_fields.append('staff_id')
        if not client_name or not str(client_name).strip():
            missing_fields.append('client_name')
        if not service_type or not str(service_type).strip():
            missing_fields.append('service_name')
        if not appointment_date_str:
            missing_fields.append('appointment_date')
        if not start_time:
            missing_fields.append('start_time')
        if not end_time:
            missing_fields.append('end_time')

        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}',
                'received_data': {k: v for k, v in data.items() if k not in ['service_id', 'client_id']}
            }), 400

        # Parse date and times with better error handling
        if not appointment_date_str:
            appointment_date_str = datetime.now().strftime('%Y-%m-%d')

        try:
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Please use YYYY-MM-DD format.'
            }), 400

        try:
            start_time_obj = datetime.strptime(str(start_time), '%H:%M').time()
            end_time_obj = datetime.strptime(str(end_time), '%H:%M').time()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid time format. Please use HH:MM format (24-hour).'
            }), 400

        # Calculate duration
        start_datetime = datetime.combine(appointment_date, start_time_obj)
        end_datetime = datetime.combine(appointment_date, end_time_obj)
        duration = int((end_datetime - start_datetime).total_seconds() / 60)

        if duration <= 0:
            return jsonify({
                'success': False,
                'error': 'End time must be after start time. Please check your time selection.'
            }), 400

        if duration < 15:
            return jsonify({
                'success': False,
                'error': 'Appointment duration must be at least 15 minutes.'
            }), 400

        # Verify staff exists and is active
        try:
            staff_id_int = int(staff_id)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid staff ID format.'
            }), 400

        staff = User.query.filter_by(id=staff_id_int, is_active=True).first()
        if not staff:
            return jsonify({
                'success': False,
                'error': 'Selected staff member not found or inactive. Please refresh and try again.'
            }), 400

        # Look up service details for pricing
        service = Service.query.filter_by(name=str(service_type).strip(), is_active=True).first()
        if not service:
            # Try to find service by similar name (case insensitive)
            service = Service.query.filter(
                Service.name.ilike(f'%{str(service_type).strip()}%'),
                Service.is_active == True
            ).first()

        service_price = float(service.price) if service and service.price else 100.0
        service_id = service.id if service else None

        # Check for time conflicts with improved validation
        conflicting_bookings = UnakiBooking.query.filter(
            UnakiBooking.staff_id == staff_id_int,
            UnakiBooking.appointment_date == appointment_date,
            UnakiBooking.status.in_(['scheduled', 'confirmed', 'in_progress']),
            # Proper overlap detection
            UnakiBooking.end_time > start_time_obj,
            UnakiBooking.start_time < end_time_obj
        ).all()

        if conflicting_bookings:
            conflict_details = []
            for booking in conflicting_bookings:
                try:
                    time_range = f"{booking.start_time.strftime('%H:%M')} - {booking.end_time.strftime('%H:%M')}"
                    conflict_details.append(f"{time_range} - {booking.service_name}")
                except:
                    conflict_details.append(f"{booking.service_name}")

            return jsonify({
                'success': False,
                'error': f'Time slot conflicts with existing appointment(s) for {staff.full_name}: {", ".join(conflict_details)}'
            }), 400

        # Handle customer data - ALWAYS create customer if not exists
        customer = None
        client_phone = data.get('clientPhone', '').strip() or data.get('client_phone', '').strip()
        client_email = data.get('clientEmail', '').strip() or data.get('client_email', '').strip()
        client_id = data.get('clientId') or data.get('client_id')

        # Try to find existing customer
        if client_id:
            try:
                customer = Customer.query.get(int(client_id))
            except (ValueError, TypeError):
                pass

        if not customer and client_phone:
            customer = Customer.query.filter_by(phone=client_phone).first()

        if not customer and client_email:
            customer = Customer.query.filter_by(email=client_email).first()

        # ALWAYS create customer if not found - this ensures visibility in Customer Management
        if not customer:
            try:
                name_parts = str(client_name).strip().split(' ', 1)
                first_name = name_parts[0] if name_parts else 'Unknown'
                last_name = name_parts[1] if len(name_parts) > 1 else ''

                # Extract gender from client_name or use default
                gender = data.get('gender', 'other').lower()

                customer = Customer(
                    first_name=first_name,
                    last_name=last_name,
                    phone=client_phone if client_phone else None,
                    email=client_email if client_email else None,
                    gender=gender if gender in ['male', 'female', 'other'] else 'other',
                    is_active=True,
                    total_visits=0,
                    total_spent=0.0
                )
                db.session.add(customer)
                db.session.flush()
                print(f"✅ Created new customer: {customer.full_name} (ID: {customer.id}, Phone: {customer.phone})")
            except Exception as ce:
                print(f"❌ Error creating customer: {ce}")
                # Don't fail the booking if customer creation fails
                import traceback
                traceback.print_exc()

        # Create UnakiBooking entry (timestamps will use IST from model defaults)
        unaki_booking = UnakiBooking(
            client_id=customer.id if customer else None,
            client_name=str(client_name).strip(),
            client_phone=client_phone or None,
            client_email=client_email or None,
            staff_id=staff_id_int,
            staff_name=staff.full_name,
            service_id=service_id,
            service_name=str(service_type).strip(),
            service_duration=duration,
            service_price=service_price,
            appointment_date=appointment_date,
            start_time=start_time_obj,
            end_time=end_time_obj,
            status='confirmed',
            notes=data.get('notes', '').strip(),
            booking_source='unaki_system',
            booking_method='form_booking',
            amount_charged=service_price,
            payment_status='pending',
            confirmed_at=get_ist_now().replace(tzinfo=None)  # Store as naive IST datetime
        )

        db.session.add(unaki_booking)
        db.session.commit()

        print(f"Successfully created booking ID: {unaki_booking.id}")

        # Return success response
        return jsonify({
            'success': True,
            'message': f'Appointment booked successfully for {client_name} with {staff.full_name}',
            'appointmentId': unaki_booking.id,
            'booking': {
                'id': unaki_booking.id,
                'client_name': unaki_booking.client_name,
                'staff_name': unaki_booking.staff_name,
                'service_name': unaki_booking.service_name,
                'appointment_date': unaki_booking.appointment_date.isoformat(),
                'start_time': unaki_booking.start_time.strftime('%H:%M'),
                'end_time': unaki_booking.end_time.strftime('%H:%M'),
                'duration': unaki_booking.service_duration,
                'price': unaki_booking.service_price,
                'status': unaki_booking.status
            }
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error in unaki_create_appointment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Unable to create appointment. Please check all fields and try again.'
        }), 500


@app.route('/unaki-booking')
@app.route('/unaki_booking')
@login_required
def unaki_booking():
    """Enhanced Unaki Appointment Booking System - Professional spa booking interface"""
    from datetime import date, datetime

    # Get current date parameter and convert to date object
    selected_date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))

    try:
        # Convert string to date object for template
        selected_date_obj = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        # Fallback to today if invalid date format
        selected_date_obj = date.today()
        selected_date_str = selected_date_obj.strftime('%Y-%m-%d')

    try:
        from modules.staff.staff_queries import get_staff_members
        from modules.services.services_queries import get_all_services
        from modules.clients.clients_queries import get_all_customers

        # Get data for the booking form
        staff_members = get_staff_members()
        services = get_all_services()
        clients = get_all_customers()
        today = date.today().strftime('%Y-%m-%d')

        print(f"🗓️  Querying Unaki bookings for date: {selected_date_str} (from parameter: {request.args.get('date', 'not provided')})")
        print(f"📊 Loaded {len(staff_members)} staff, {len(services)} services, {len(clients)} clients")

        return render_template('unaki_booking.html',
                             staff_members=staff_members,
                             services=services,
                             clients=clients,
                             today=today,
                             today_date=selected_date_obj)
    except Exception as e:
        print(f"Error in unaki_booking route: {e}")
        import traceback
        traceback.print_exc()
        return render_template('unaki_booking.html',
                             staff_members=[],
                             services=[],
                             clients=[],
                             today=date.today().strftime('%Y-%m-%d'),
                             today_date=date.today())

@app.route('/api/unaki/get-bookings')
@login_required
def api_unaki_get_bookings():
    """API endpoint to get Unaki bookings for a specific date"""
    try:
        from models import UnakiBooking, User
        from datetime import datetime

        date_str = request.args.get('date')
        if not date_str:
            return jsonify({'success': False, 'error': 'Date parameter required'}), 400

        try:
            booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format'}), 400

        # Get today's date for comparison
        today = date.today()

        # Get all bookings for the date (including paid ones)
        bookings = UnakiBooking.query.filter(
            UnakiBooking.appointment_date == booking_date
        ).all()


        bookings_data = []
        for booking in bookings:
            # Calculate position data
            start_hour = booking.start_time.hour
            start_minute = booking.start_time.minute

            # Determine service type for coloring
            service_type = 'default'
            if booking.service_name:
                service_lower = booking.service_name.lower()
                if 'massage' in service_lower:
                    service_type = 'massage'
                elif 'facial' in service_lower:
                    service_type = 'facial'
                elif 'manicure' in service_lower:
                    service_type = 'manicure'
                elif 'pedicure' in service_lower:
                    service_type = 'pedicure'
                elif 'hair' in service_lower or 'cut' in service_lower:
                    service_type = 'haircut'
                elif 'wax' in service_lower:
                    service_type = 'waxing'

            bookings_data.append({
                'id': booking.id,
                'staff_id': booking.staff_id,
                'client_id': booking.client_id,
                'client_name': booking.client_name,
                'service_names': booking.service_name,
                'service_type': service_type,
                'start_time': booking.start_time.strftime('%I:%M %p'),
                'start_hour': start_hour,
                'start_minute': start_minute,
                'duration': booking.service_duration,
                'status': booking.status,
                'payment_status': booking.payment_status,
                'checked_in': booking.checked_in,
                'checked_in_at': booking.checked_in_at.isoformat() if booking.checked_in_at else None,
                'booking_source': booking.booking_source
            })

        return jsonify({'success': True, 'bookings': bookings_data})

    except Exception as e:
        print(f"Error getting Unaki bookings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Department Management Routes are in settings_views.py

@app.route('/admin')
@login_required
def admin_index():
    """Admin route - redirect to dashboard"""
    return redirect(url_for('dashboard'))

@app.route('/zenoti-booking')
@app.route('/zenoti_booking')
@login_required
def zenoti_booking():
    """Zenoti-style appointment booking interface"""
    from models import User, Customer, Appointment
    from datetime import datetime, date

    # Get today's data for the interface
    today = date.today()
    staff_members = User.query.filter_by(is_active=True, role='staff').all()
    customers = Customer.query.filter_by(is_active=True).all()

    # For now, use static services data since Service model might not exist
    services = [
        {'id': 1, 'name': 'Deep Tissue Massage', 'duration': 60, 'price': 120},
        {'id': 2, 'name': 'Anti-Aging Facial', 'duration': 60, 'price': 100},
        {'id': 3, 'name': 'Gel Manicure', 'duration': 45, 'price': 65},
        {'id': 4, 'name': 'Spa Pedicure', 'duration': 60, 'price': 80},
    ]

    # Get today's appointments
    today_appointments = Appointment.query.filter(
        db.func.date(Appointment.appointment_date) == today
    ).all()

    return render_template('zenoti_booking.html',
                         appointments=today_appointments,
                         staff_members=staff_members,
                         services=services,
                         customers=customers)

@app.route('/api/create-booking', methods=['POST'])
@login_required
def zenoti_create_booking():
    """API endpoint to create new booking with multiple services"""
    try:
        from models import Appointment, Customer, User
        from datetime import datetime, timedelta

        data = request.get_json()

        # Validate required fields
        if not data.get('client_id') or not data.get('services') or not data.get('date') or not data.get('time'):
            return jsonify({'error': 'Missing required fields'}), 400

        # Parse date and time
        appointment_datetime = datetime.strptime(f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M")

        created_appointments = []

        # Create appointment for each service
        for service_data in data['services']:
            # Use service data directly since we're using static services for now
            if not service_data.get('service_id'):
                continue

            # Calculate end time based on service duration
            duration_minutes = service_data.get('duration', 60)
            end_time = appointment_datetime + timedelta(minutes=duration_minutes)

            appointment = Appointment(
                client_id=data['client_id'],
                service_id=service_data['service_id'],
                staff_id=data.get('staff_id'),
                appointment_date=appointment_datetime,
                end_time=end_time,
                status='scheduled',
                amount=service_data.get('price', 0),
                notes=data.get('notes', '')
            )

            db.session.add(appointment)
            created_appointments.append(appointment)

            # Move start time for next service
            appointment_datetime = end_time

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'{len(created_appointments)} appointments created successfully',
            'appointments': [{'id': apt.id, 'date': apt.appointment_date.isoformat()} for apt in created_appointments]
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-availability/<staff_id>/<date>')
@login_required
def get_staff_availability(staff_id, date):
    """Get staff availability for a specific date"""
    try:
        from models import Appointment
        from datetime import datetime, timedelta

        target_date = datetime.strptime(date, "%Y-%m-%d").date()

        # Get existing appointments for the staff on this date
        existing_appointments = Appointment.query.filter(
            Appointment.staff_id == staff_id,
            db.func.date(Appointment.appointment_date) == target_date
        ).all()

        # Generate available time slots (9 AM to 6 PM, 30-minute intervals)
        available_slots = []
        start_time = datetime.combine(target_date, datetime.min.time().replace(hour=9))
        end_time = datetime.combine(target_date, datetime.min.time().replace(hour=18))

        current_time = start_time
        while current_time < end_time:
            slot_end = current_time + timedelta(minutes=30)

            # Check if this slot conflicts with existing appointments
            conflict = False
            for apt in existing_appointments:
                if (current_time < apt.end_time and slot_end > apt.appointment_date):
                    conflict = True
                    break

            if not conflict:
                available_slots.append(current_time.strftime("%H:%M"))

            current_time += timedelta(minutes=30)

        return jsonify({'available_slots': available_slots})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ensure app is available for gunicorn
if __name__ != '__main__':
    # When imported by gunicorn or other WSGI servers
    print("App imported for WSGI deployment")


# Additional UnakiBooking API endpoints
@app.route('/api/unaki/bookings')
def unaki_get_bookings():
    """Get all Unaki bookings with optional filters"""
    try:
        from models import UnakiBooking

        # Get filter parameters
        date_filter = request.args.get('date')
        staff_id = request.args.get('staff_id', type=int)
        status = request.args.get('status')

        # Base query
        query = UnakiBooking.query

        # Apply filters
        if date_filter:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(UnakiBooking.appointment_date == filter_date)

        if staff_id:
            query = query.filter(UnakiBooking.staff_id == staff_id)

        if status:
            query = query.filter(UnakiBooking.status == status)

        bookings = query.order_by(UnakiBooking.appointment_date, UnakiBooking.start_time).all()

        return jsonify({
            'success': True,
            'bookings': [booking.to_dict() for booking in bookings],
            'total': len(bookings)
        })

    except Exception as e:
        print(f"Error in unaki_get_bookings: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'bookings': []
        })

@app.route('/api/unaki/book', methods=['POST'])
def unaki_create_booking():
    """Create a new Unaki booking"""
    try:
        from models import UnakiBooking, User, Service, Customer
        from datetime import datetime, time

        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        client_id = data.get('client_id')
        client_name = data.get('client_name')
        client_phone = data.get('client_phone')
        client_email = data.get('client_email')
        staff_id = data.get('staff_id')
        service_id = data.get('service_id')
        service_name = data.get('service_name')
        appointment_date_str = data.get('appointment_date')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        service_duration = data.get('service_duration', 60)
        service_price = data.get('service_price', 0.0)
        notes = data.get('notes', '')

        if not all([client_name, staff_id, service_name, appointment_date_str, start_time_str, end_time_str]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: client_name, staff_id, service_name, appointment_date, start_time, end_time'
            }), 400

        staff = User.query.get(staff_id)
        if not staff:
            return jsonify({
                'success': False,
                'error': f'Staff member with ID {staff_id} not found'
            }), 404

        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()

        new_booking = UnakiBooking(
            client_id=client_id,
            client_name=client_name,
            client_phone=client_phone or '',
            client_email=client_email or '',
            staff_id=staff_id,
            staff_name=f"{staff.first_name} {staff.last_name}",
            service_id=service_id,
            service_name=service_name,
            service_duration=int(service_duration),
            service_price=float(service_price),
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_time,
            status='scheduled',
            notes=notes,
            booking_source='unaki_system',
            booking_method=data.get('booking_method', 'manual'),
            payment_status='pending',
            created_at=datetime.utcnow()
        )

        db.session.add(new_booking)
        db.session.commit()

        print(f"✅ Created booking: {new_booking.id} - {client_name} with {staff.first_name} for {service_name}")

        return jsonify({
            'success': True,
            'booking': new_booking.to_dict(),
            'message': 'Booking created successfully'
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid date/time format: {str(e)}'
        }), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error in unaki_create_booking: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/unaki/bookings/<int:booking_id>')
def unaki_get_booking(booking_id):
    """Get specific Unaki booking by ID"""
    try:
        from models import UnakiBooking

        booking = UnakiBooking.query.get(booking_id)
        if not booking:
            return jsonify({
                'success': False,
                'error': 'Booking not found'
            }), 404

        return jsonify({
            'success': True,
            'booking': booking.to_dict()
        })

    except Exception as e:
        print(f"Error in unaki_get_booking: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/unaki/bookings/<int:booking_id>/update-status', methods=['PUT'])
def unaki_update_booking_status(booking_id):
    """Update Unaki booking status"""
    try:
        from models import UnakiBooking
        from datetime import datetime

        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        new_status = data.get('status')

        if not new_status:
            return jsonify({
                'success': False,
                'error': 'Status is required'
            }), 400

        valid_statuses = ['scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show']
        if new_status not in valid_statuses:
            return jsonify({
                'success': False,
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400

        booking = UnakiBooking.query.get(booking_id)
        if not booking:
            return jsonify({
                'success': False,
                'error': 'Booking not found'
            }), 404

        # Update status and relevant timestamps
        old_status = booking.status
        booking.status = new_status
        booking.updated_at = datetime.utcnow()

        if new_status == 'confirmed':
            booking.confirmed_at = datetime.utcnow()
        elif new_status == 'completed':
            booking.completed_at = datetime.utcnow()

        # Update notes if provided
        if data.get('notes'):
            booking.internal_notes = (booking.internal_notes or '') + f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Status changed from {old_status} to {new_status}: {data['notes']}"

        db.session.commit()

        print(f"✅ Booking {booking_id} status updated from {old_status} to {new_status}")

        return jsonify({
            'success': True,
            'message': f'Booking status updated to {new_status}',
            'booking': booking.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in unaki_update_booking_status: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/unaki/clear-all-data', methods=['POST'])
def unaki_clear_all_data():
    """Clear all Unaki booking data"""
    try:
        from models import UnakiBooking

        # Delete all bookings
        deleted_count = UnakiBooking.query.delete()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} appointments successfully',
            'deleted_count': deleted_count
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error clearing all data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/unaki/bookings/<int:booking_id>', methods=['PUT'])
def unaki_update_booking(booking_id):
    """Update Unaki booking"""
    try:
        from models import UnakiBooking, User, Service
        from datetime import datetime, time

        data = request.get_json()

        booking = UnakiBooking.query.get(booking_id)
        if not booking:
            return jsonify({
                'success': False,
                'error': 'Booking not found'
            }), 404

        # Validate required fields
        required_fields = ['clientName', 'serviceName', 'staffId', 'startTime', 'endTime']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        # Parse date and times
        appointment_date = datetime.strptime(data.get('date', booking.appointment_date.strftime('%Y-%m-%d')), '%Y-%m-%d').date()
        start_time_obj = datetime.strptime(data['startTime'], '%H:%M').time()
        end_time_obj = datetime.strptime(data['endTime'], '%H:%M').time()

        # Calculate duration
        start_datetime = datetime.combine(appointment_date, start_time_obj)
        end_datetime = datetime.combine(appointment_date, end_time_obj)
        duration = int((end_datetime - start_datetime).total_seconds() / 60)

        if duration <= 0:
            return jsonify({
                'success': False,
                'error': 'End time must be after start time'
            }), 400

        # Verify staff exists and is active
        staff = User.query.filter_by(id=data['staffId'], is_active=True).first()
        if not staff:
            return jsonify({
                'success': False,
                'error': 'Staff member not found or inactive'
            }), 400

        # Check for time conflicts (excluding current booking)
        conflicting_bookings = UnakiBooking.query.filter(
            UnakiBooking.staff_id == data['staffId'],
            UnakiBooking.appointment_date == appointment_date,
            UnakiBooking.status.in_(['scheduled', 'confirmed', 'in_progress']),
            UnakiBooking.id != booking_id,  # Exclude current booking
            UnakiBooking.end_time > start_time_obj,
            UnakiBooking.start_time < end_time_obj
        ).all()

        if conflicting_bookings:
            conflict_details = []
            for conflict in conflicting_bookings:
                conflict_details.append(f"{conflict.get_time_range_display()} - {conflict.service_name}")

            return jsonify({
                'success': False,
                'error': f'Time slot conflicts with existing booking(s) for {staff.full_name}: {", ".join(conflict_details)}'
            }), 400

        # Update booking fields
        booking.client_name = data['clientName'].strip()
        booking.client_phone = data.get('clientPhone', '').strip()
        booking.service_name = data['serviceName'].strip()
        booking.service_duration = duration
        booking.staff_id = int(data['staffId'])
        booking.staff_name = staff.full_name
        booking.appointment_date = appointment_date
        booking.start_time = start_time_obj
        booking.end_time = end_time_obj
        booking.notes = data.get('notes', '').strip()
        booking.updated_at = datetime.utcnow()

        # Update service price and service_id if available
        service = Service.query.filter_by(name=data['serviceName'], is_active=True).first()
        if service:
            booking.service_id = service.id
            booking.service_price = float(service.price)
            booking.amount_charged = float(service.price)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Booking updated successfully',
            'booking': booking.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error in unaki_update_booking: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/unaki/staff/<int:staff_id>/shift-logs/<date_str>')
def unaki_get_staff_shift_logs(staff_id, date_str):
    """Get detailed shift logs for specific staff and date"""
    try:
        from datetime import datetime
        from models import User, ShiftManagement, ShiftLogs

        # Parse date
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Get staff member
        staff = User.query.get(staff_id)
        if not staff:
            return jsonify({
                'success': False,
                'error': 'Staff member not found'
            }), 404

        # Get shift management
        shift_management = ShiftManagement.query.filter(
            ShiftManagement.staff_id == staff_id,
            ShiftManagement.from_date <= target_date,
            ShiftManagement.to_date >= target_date
        ).first()

        # Get shift log
        shift_log = None
        if shift_management:
            shift_log = ShiftLogs.query.filter(
                ShiftLogs.shift_management_id == shift_management.id,
                ShiftLogs.individual_date == target_date
            ).first()

        # Determine if this is an off day
        # If there's shift management but no shift log, it's an off day
        is_off_day = shift_management is not None and shift_log is None

        # Prepare response
        response_data = {
            'success': True,
            'staff_id': staff_id,
            'staff_name': staff.full_name or f"{staff.first_name} {staff.last_name}",
            'date': date_str,
            'has_shift_management': shift_management is not None,
            'has_shift_log': shift_log is not None,
            'is_off_day': is_off_day,
            'status': 'off_day' if is_off_day else ('working' if shift_log else 'no_schedule')
        }

        if shift_management:
            response_data['shift_management'] = {
                'id': shift_management.id,
                'from_date': shift_management.from_date.strftime('%Y-%m-%d'),
                'to_date': shift_management.to_date.strftime('%Y-%m-%d'),
                'created_at': shift_management.created_at.isoformat(),
                'updated_at': shift_management.updated_at.isoformat()
            }

        if shift_log:
            response_data['shift_log'] = {
                'id': shift_log.id,
                'individual_date': shift_log.individual_date.strftime('%Y-%m-%d'),
                'shift_start_time': shift_log.shift_start_time.strftime('%H:%M') if shift_log.shift_start_time else None,
                'shift_end_time': shift_log.shift_end_time.strftime('%H:%M') if shift_log.shift_end_time else None,
                'break_start_time': shift_log.break_start_time.strftime('%H:%M') if shift_log.break_start_time else None,
                'break_end_time': shift_log.break_end_time.strftime('%H:%M') if shift_log.break_end_time else None,
                'break_display': shift_log.get_break_time_display(),
                'status': shift_log.status,
                'created_at': shift_log.created_at.isoformat()
            }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error getting staff shift logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/unaki/appointments/<int:appointment_id>', methods=['DELETE'])
def unaki_delete_appointment(appointment_id):
    """Delete appointment in Unaki system"""
    try:
        from models import UnakiBooking
        from datetime import datetime

        # Handle both JSON and non-JSON requests
        data = {}
        if request.is_json:
            data = request.get_json() or {}
        elif request.form:
            data = request.form.to_dict()

        reason = data.get('reason', 'Deleted by user')

        booking = UnakiBooking.query.get(appointment_id)
        if not booking:
            return jsonify({
                'success': False,
                'error': 'Appointment not found'
            }), 404

        # Store info for response
        client_name = booking.client_name
        service_name = booking.service_name
        appointment_time = booking.start_time.strftime('%I:%M %p')

        # Delete the booking
        db.session.delete(booking)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Appointment for {client_name} ({service_name} at {appointment_time}) deleted successfully',
            'deleted_appointment': {
                'id': appointment_id,
                'client_name': client_name,
                'service_name': service_name,
                'time': appointment_time
            }
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error in unaki_delete_appointment: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to delete appointment: {str(e)}'
        }), 500


# Department API routes are handled in modules/settings/settings_views.py

# Import public website module
try:
    from modules.website import website_views
    print("✅ Website module imported successfully")
except Exception as e:
    print(f"⚠️ Website module import error: {e}")