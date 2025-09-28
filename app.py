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

# Configure the database - use PostgreSQL in Replit environment, SQLite otherwise
if os.environ.get("DATABASE_URL"):
    # Use PostgreSQL database in Replit environment
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    print(f"Using PostgreSQL database: {app.config['SQLALCHEMY_DATABASE_URI']}")
else:
    # Fallback to SQLite for local development
    app.config["SQLALCHEMY_DATABASE_URI"] = compute_sqlite_uri()
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
    }
    print(f"Using SQLite database: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Configure cache control for Replit environment
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
            # Configure SQLite pragmas only for SQLite connections
            if not os.environ.get("DATABASE_URL"):
                event.listen(db.engine, "connect", configure_sqlite_pragmas)
                print(f"SQLite database configured: {app.config['SQLALCHEMY_DATABASE_URI']}")
            else:
                print(f"PostgreSQL database configured: {app.config['SQLALCHEMY_DATABASE_URI']}")

            # Make sure to import the models here or their tables won't be created
            import models  # noqa: F401
            # Import inventory models for database creation
            from modules.inventory import models as inventory_models  # noqa: F401
            # Import Department model for database creation
            from models import Department  # noqa: F401

            # Try to create tables, but handle conflicts gracefully
            db.create_all()
            print("Database tables created successfully")
            print(f"Database connection: {app.config['SQLALCHEMY_DATABASE_URI']}")
        except Exception as e:
            print(f"Database initialization warning: {e}")
            print("Continuing with existing database...")

        print("Basic routes imported successfully")

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
    print("✅ Settings views imported")
except Exception as e:
    print(f"⚠️ Settings views import error: {e}")

try:
    from modules.checkin.checkin_views import *
    print("✅ Checkin views imported")
except Exception as e:
    print(f"⚠️ Checkin views import error: {e}")

try:
    from modules.inventory.views import *
    print("✅ Inventory views imported")
except Exception as e:
    print(f"⚠️ Inventory views import error: {e}")

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
    # Verify that the appointment_to_billing route is registered
    from flask import current_app
    with app.app_context():
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        if '/appointment/<int:appointment_id>/go-to-billing' in rules:
            print("✅ Appointment billing route registered successfully")
        else:
            print("⚠️ Appointment billing route not found in URL map")
except Exception as e:
    print(f"⚠️ Integrated billing views import error: {e}")

# Skip other problematic imports that cause route conflicts
print("⚠️ Skipping other staff, notifications, and packages views to avoid conflicts")

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
    """Get schedule data for Unaki booking"""
    try:
        from datetime import datetime, date, timedelta
        from modules.staff.staff_queries import get_staff_members
        from models import UnakiBooking

        # Get date parameter
        date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Debug: Log the date we're querying for
        print(f"🗓️  Querying Unaki bookings for date: {target_date} (from parameter: {date_str})")

        # Get staff members
        staff_members = get_staff_members()

        # Get Unaki bookings for the target date
        unaki_bookings = UnakiBooking.query.filter_by(appointment_date=target_date).all()

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

        # Format Unaki bookings data
        appointments_data = []
        for booking in unaki_bookings:
            appointment_info = {
                'id': booking.id,
                'staffId': booking.staff_id,
                'clientName': booking.client_name,
                'clientPhone': booking.client_phone or '',
                'service': booking.service_name,
                'startTime': booking.start_time.strftime('%H:%M'),
                'endTime': booking.end_time.strftime('%H:%M'),
                'duration': booking.service_duration,
                'status': booking.status,
                'notes': booking.notes or '',
                'amount': booking.service_price,
                'payment_status': booking.payment_status,
                'booking_source': booking.booking_source
            }
            appointments_data.append(appointment_info)

        # Format breaks data (simplified for now)
        breaks_data = []

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
def unaki_create_appointment():
    """Create appointment for Unaki booking system using UnakiBooking table"""
    try:
        from datetime import datetime, timedelta, time
        from models import UnakiBooking, User, Service, Customer

        data = request.get_json()
        print(f"Received booking data: {data}")

        # Validate required fields
        required_fields = ['staffId', 'clientName', 'serviceType', 'startTime', 'endTime']
        missing_fields = []

        for field in required_fields:
            if field not in data or not data[field] or str(data[field]).strip() == '':
                missing_fields.append(field)

        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Parse date and times
        appointment_date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        try:
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(data['startTime'], '%H:%M').time()
            end_time_obj = datetime.strptime(data['endTime'], '%H:%M').time()
        except ValueError as ve:
            return jsonify({
                'success': False,
                'error': f'Invalid date/time format: {str(ve)}'
            }), 400

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

        # Look up service details for pricing
        service = Service.query.filter_by(name=data['serviceType'], is_active=True).first()
        service_price = float(service.price) if service else 100.0

        # Check for time conflicts - proper overlap detection
        # Two appointments overlap if: new_start < existing_end AND existing_start < new_end
        conflicting_bookings = UnakiBooking.query.filter(
            UnakiBooking.staff_id == data['staffId'],
            UnakiBooking.appointment_date == appointment_date,
            UnakiBooking.status.in_(['scheduled', 'confirmed', 'in_progress']),
            # Check for overlap: new appointment overlaps if new_start < existing_end AND existing_start < new_end
            UnakiBooking.end_time > start_time_obj,  # existing ends after new starts
            UnakiBooking.start_time < end_time_obj   # existing starts before new ends
        ).all()

        if conflicting_bookings:
            conflict_details = []
            for booking in conflicting_bookings:
                conflict_details.append(f"{booking.get_time_range_display()} - {booking.service_name}")

            return jsonify({
                'success': False,
                'error': f'Time slot conflicts with existing booking(s) for {staff.full_name}: {", ".join(conflict_details)}'
            }), 400

        # Try to find or create customer record
        customer = None
        client_phone = data.get('clientPhone', '').strip()
        client_email = data.get('clientEmail', '').strip()

        if client_phone:
            customer = Customer.query.filter_by(phone=client_phone).first()
        elif client_email:
            customer = Customer.query.filter_by(email=client_email).first()

        # If customer doesn't exist, create a basic record
        if not customer and (client_phone or client_email):
            try:
                # Split name into first and last
                name_parts = data['clientName'].strip().split(' ', 1)
                first_name = name_parts[0] if name_parts else 'Unknown'
                last_name = name_parts[1] if len(name_parts) > 1 else ''

                customer = Customer(
                    first_name=first_name,
                    last_name=last_name,
                    phone=client_phone if client_phone else None,
                    email=client_email if client_email else None,
                    is_active=True
                )
                db.session.add(customer)
                db.session.flush()  # Get the ID without committing
                print(f"Created new customer: {customer.full_name}")
            except Exception as ce:
                print(f"Warning: Could not create customer record: {ce}")
                # Continue without customer record

        # Create UnakiBooking entry
        unaki_booking = UnakiBooking(
            client_id=int(data['clientId']) if data.get('clientId') else None,
            client_name=data['clientName'].strip(),
            client_phone=client_phone,
            client_email=client_email,
            staff_id=int(data['staffId']),
            staff_name=staff.full_name,
            service_id=service.id if service else None,
            service_name=data['serviceType'].strip(),
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
            created_at=datetime.utcnow()
        )

        db.session.add(unaki_booking)
        db.session.commit()

        print(f"Successfully created booking ID: {unaki_booking.id}")

        return jsonify({
            'success': True,
            'message': 'Appointment booked successfully',
            'appointmentId': unaki_booking.id,
            'booking': unaki_booking.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error in unaki_create_appointment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to create booking: {str(e)}'
        }), 500


@app.route('/unaki-booking')
@login_required
def unaki_booking():
    """Unaki Appointment Booking page"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        from modules.services.services_queries import get_active_services
        from modules.staff.staff_queries import get_staff_members
        from datetime import date

        # Get services and staff for initial page load
        services = get_active_services()
        staff_members = get_staff_members()
        today = date.today().strftime('%Y-%m-%d')

        return render_template('unaki_booking.html',
                             services=services,
                             staff_members=staff_members,
                             today=today)
    except Exception as e:
        print(f"Error loading Unaki booking page: {e}")
        flash('Error loading booking form. Please try again.', 'danger')
        return redirect(url_for('dashboard'))

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

@app.route('/zenoti-booking')
@login_required
def zenoti_booking():
    """Zenoti-style appointment booking interface"""
    from models import User, Customer, Appointment
    from datetime import datetime, date

    # Get today's data for the interface


@app.route('/api/unaki/appointment/<int:appointment_id>/client-data')
def get_appointment_client_data(appointment_id):
    """Get client data for a specific appointment for billing integration"""
    try:
        from models import UnakiBooking
        
        appointment = UnakiBooking.query.get(appointment_id)
        if not appointment:
            return jsonify({
                'success': False,
                'error': 'Appointment not found'
            }), 404
        
        return jsonify({
            'success': True,
            'client_id': appointment.client_id,
            'client_name': appointment.client_name,
            'client_phone': appointment.client_phone,
            'service_name': appointment.service_name,
            'service_price': appointment.service_price,
            'payment_status': appointment.payment_status,
            'status': appointment.status,
            'appointment_date': appointment.appointment_date.strftime('%Y-%m-%d'),
            'start_time': appointment.start_time.strftime('%H:%M'),
            'end_time': appointment.end_time.strftime('%H:%M')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
        from datetime import datetime, date

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
        booking.status = new_status
        booking.updated_at = datetime.utcnow()

        if new_status == 'confirmed':
            booking.confirmed_at = datetime.utcnow()
        elif new_status == 'completed':
            booking.completed_at = datetime.utcnow()

        # Update notes if provided
        if data.get('notes'):
            booking.internal_notes = (booking.internal_notes or '') + f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Status changed to {new_status}: {data['notes']}"

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Booking status updated to {new_status}',
            'booking': booking.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error in unaki_update_booking_status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
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