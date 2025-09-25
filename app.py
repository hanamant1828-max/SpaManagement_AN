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

            try:
                # Import integrated billing views to register routes
                import modules.billing.integrated_billing_views  # noqa: F401
                print("Billing views registered successfully")
            except Exception as e:
                print(f"Error importing billing routes: {e}")
                print("Billing will not be available")

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
    """Load sample data for Unaki booking system"""
    try:
        from datetime import datetime, date, timedelta, time
        from models import UnakiBooking, User

        # Create sample UnakiBooking entries for today
        today = date.today()

        # Get available staff
        staff_members = User.query.filter_by(is_active=True).limit(5).all()
        if not staff_members:
            return jsonify({
                'success': False,
                'error': 'No active staff members found'
            })

        sample_bookings = [
            {
                'client_name': 'Jessica Williams',
                'client_phone': '+1-555-0101',
                'service_name': 'Deep Cleansing Facial',
                'start_time': '10:00',
                'duration': 90,
                'price': 150.0
            },
            {
                'client_name': 'David Brown', 
                'client_phone': '+1-555-0102',
                'service_name': 'Swedish Massage',
                'start_time': '14:00',
                'duration': 60,
                'price': 120.0
            },
            {
                'client_name': 'Emma Thompson',
                'client_phone': '+1-555-0103',
                'service_name': 'Hair Cut & Style',
                'start_time': '11:00',
                'duration': 75,
                'price': 85.0
            },
            {
                'client_name': 'Michael Johnson',
                'client_phone': '+1-555-0104',
                'service_name': 'Aromatherapy Massage',
                'start_time': '15:30',
                'duration': 90,
                'price': 140.0
            },
            {
                'client_name': 'Sarah Davis',
                'client_phone': '+1-555-0105',
                'service_name': 'Express Facial',
                'start_time': '09:00',
                'duration': 45,
                'price': 75.0
            }
        ]

        created_count = 0
        for i, booking_data in enumerate(sample_bookings):
            staff = staff_members[i % len(staff_members)]

            # Parse times
            start_time_obj = datetime.strptime(booking_data['start_time'], '%H:%M').time()
            start_datetime = datetime.combine(today, start_time_obj)
            end_datetime = start_datetime + timedelta(minutes=booking_data['duration'])

            # Create UnakiBooking entry
            unaki_booking = UnakiBooking(
                client_name=booking_data['client_name'],
                client_phone=booking_data['client_phone'],
                client_email=f"{booking_data['client_name'].lower().replace(' ', '.')}@example.com",
                staff_id=staff.id,
                staff_name=staff.full_name,
                service_name=booking_data['service_name'],
                service_duration=booking_data['duration'],
                service_price=booking_data['price'],
                appointment_date=today,
                start_time=start_time_obj,
                end_time=end_datetime.time(),
                status='confirmed',
                notes='Sample booking from Unaki system',
                booking_source='unaki_system',
                booking_method='quick_book',
                amount_charged=booking_data['price'],
                payment_status='pending',
                created_at=datetime.utcnow()
            )

            db.session.add(unaki_booking)
            created_count += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Sample data loaded successfully! Created {created_count} Unaki bookings.',
            'data': {
                'bookings_created': created_count
            }
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error in unaki_load_sample_data: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to load sample data: {str(e)}'
        })

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

        # Check for time conflicts
        existing_booking = UnakiBooking.query.filter(
            UnakiBooking.staff_id == data['staffId'],
            UnakiBooking.appointment_date == appointment_date,
            UnakiBooking.start_time == start_time_obj,
            UnakiBooking.status.in_(['scheduled', 'confirmed', 'in_progress'])
        ).first()

        if existing_booking:
            return jsonify({
                'success': False,
                'error': f'Time slot already booked for {staff.full_name} at {data["startTime"]}'
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
            client_name=data['clientName'].strip(),
            client_phone=client_phone,
            client_email=client_email,
            staff_id=int(data['staffId']),
            staff_name=staff.full_name,
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

@app.route('/api/unaki/bookings/<int:booking_id>', methods=['DELETE'])
def unaki_cancel_booking(booking_id):
    """Cancel Unaki booking"""
    try:
        from models import UnakiBooking
        from datetime import datetime

        data = request.get_json() or {}
        reason = data.get('reason', 'Cancelled by user')

        booking = UnakiBooking.query.get(booking_id)
        if not booking:
            return jsonify({
                'success': False,
                'error': 'Booking not found'
            }), 404

        if not booking.can_be_cancelled():
            return jsonify({
                'success': False,
                'error': f'Cannot cancel booking with status: {booking.status}'
            }), 400

        # Update booking status to cancelled
        booking.status = 'cancelled'
        booking.updated_at = datetime.utcnow()
        booking.internal_notes = (booking.internal_notes or '') + f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Cancelled: {reason}"

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Booking cancelled successfully',
            'booking': booking.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error in unaki_cancel_booking: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# UNAKI BOOKING VIEW ROUTES
@app.route('/unaki-booking')
@login_required
def unaki_bookings():
    """Display the Unaki booking form with dropdowns populated from database"""
    try:
        from modules.clients.clients_queries import get_all_customers
        from modules.services.services_queries import get_all_services
        from modules.staff.staff_queries import get_staff_members
        from models import UnakiBooking
        from datetime import date

        # Get all required data for dropdowns
        clients = get_all_customers()
        services = get_all_services()
        staff_members = get_staff_members()

        # Get recent bookings for display
        existing_bookings = UnakiBooking.query.order_by(UnakiBooking.created_at.desc()).limit(10).all()

        # Pass today's date
        today = date.today().strftime('%Y-%m-%d')

        return render_template('unaki_bookings.html', 
                             clients=clients,
                             services=services, 
                             staff_members=staff_members,
                             existing_bookings=existing_bookings,
                             today=today)

    except Exception as e:
        print(f"Error in unaki_bookings: {e}")
        flash('Error loading booking form. Please try again.', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/book-appointment', methods=['POST'])
@login_required
def book_appointment():
    """Handle Unaki booking form submission with strict time-overlap conflict checking"""
    try:
        from datetime import datetime, timedelta, time, date
        from models import UnakiBooking, Service, Customer, User

        # Extract form data
        client_id = request.form.get('client_id', type=int)
        staff_id = request.form.get('staff_id', type=int)
        service_ids = request.form.get('service_ids', '')  # Comma-separated IDs
        appointment_date_str = request.form.get('appointment_date')
        start_time_str = request.form.get('start_time')
        notes = request.form.get('notes', '')
        total_duration = request.form.get('duration', type=int)

        # Validate required fields
        if not all([client_id, staff_id, service_ids, appointment_date_str, start_time_str]):
            flash('Missing required booking information', 'danger')
            return redirect(url_for('unaki_bookings'))

        # Parse date and time
        try:
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
        except ValueError:
            flash('Invalid date or time format', 'danger')
            return redirect(url_for('unaki_bookings'))

        # Get service details and calculate total duration and price
        selected_service_ids = [int(id.strip()) for id in service_ids.split(',') if id.strip()]
        services = Service.query.filter(Service.id.in_(selected_service_ids)).all()

        if not services:
            flash('Selected services not found', 'danger')
            return redirect(url_for('unaki_bookings'))

        # Calculate totals
        total_duration_calculated = sum(service.duration for service in services)
        total_price = sum(float(service.price) for service in services)
        service_names = ', '.join(service.name for service in services)

        # Calculate end time
        start_datetime = datetime.combine(appointment_date, start_time_obj)
        end_datetime = start_datetime + timedelta(minutes=total_duration_calculated)
        end_time_obj = end_datetime.time()

        # Validate that appointment is not in the past
        current_datetime = datetime.now()
        if start_datetime < current_datetime:
            flash('Cannot book appointments in the past', 'danger')
            return redirect(url_for('unaki_bookings'))

        # CRITICAL STRICT TIME-OVERLAP CONFLICT CHECK
        # Check if new booking overlaps with any existing booking for the same staff member
        # Overlap logic: Two time ranges overlap if:
        # - New booking starts before existing booking ends AND
        # - New booking ends after existing booking starts
        conflicting_booking = UnakiBooking.query.filter(
            UnakiBooking.staff_id == staff_id,
            UnakiBooking.appointment_date == appointment_date,
            UnakiBooking.status.in_(['scheduled', 'confirmed', 'in_progress']),
            # Time overlap condition using SQLAlchemy and_ operator
            db.and_(
                start_time_obj < UnakiBooking.end_time,    # New start < Existing end
                end_time_obj > UnakiBooking.start_time     # New end > Existing start
            )
        ).first()

        # If ANY conflict found, reject the booking immediately
        if conflicting_booking:
            conflict_time = f"{conflicting_booking.start_time.strftime('%I:%M %p')} - {conflicting_booking.end_time.strftime('%I:%M %p')}"
            conflict_msg = f'This time slot is already booked for this staff member. Conflicting appointment: {conflicting_booking.client_name} at {conflict_time} on {conflicting_booking.appointment_date}'
            flash(conflict_msg, 'danger')
            return redirect(url_for('unaki_bookings'))

        # Get client and staff details for denormalized storage
        client = Customer.query.get(client_id)
        staff = User.query.get(staff_id)

        if not client or not staff:
            flash('Selected client or staff member not found', 'danger')
            return redirect(url_for('unaki_bookings'))

        # NO CONFLICT FOUND - Proceed with booking creation
        unaki_booking = UnakiBooking(
            client_name=client.full_name,
            client_phone=client.phone,
            client_email=client.email,
            staff_id=staff_id,
            staff_name=staff.full_name or f"{staff.first_name} {staff.last_name}",
            service_name=service_names,
            service_duration=total_duration_calculated,
            service_price=total_price,
            appointment_date=appointment_date,
            start_time=start_time_obj,
            end_time=end_time_obj,
            status='scheduled',
            notes=notes,
            booking_source='unaki_system',
            booking_method='form_booking',
            amount_charged=total_price,
            payment_status='pending',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(unaki_booking)
        db.session.commit()

        success_msg = f'Appointment successfully booked! Booking ID: {unaki_booking.id} for {client.full_name} on {appointment_date} at {start_time_str}'
        flash(success_msg, 'success')
        return redirect(url_for('unaki_bookings'))

    except Exception as e:
        db.session.rollback()
        print(f"Critical error creating appointment: {e}")
        flash('Error processing booking. Please try again.', 'danger')
        return redirect(url_for('unaki_bookings'))