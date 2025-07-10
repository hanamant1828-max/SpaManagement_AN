from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from app import app, db
from models import User, Client, Service, Appointment, Inventory, Expense, Invoice, Package, StaffSchedule, ClientPackage, PackageService
from forms import LoginForm, UserForm, ClientForm, ServiceForm, AppointmentForm, InventoryForm, ExpenseForm, PackageForm, StaffScheduleForm
import utils

@app.context_processor
def utility_processor():
    return dict(utils=utils)

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user)
            next_page = request.args.get('next')
            if not next_page:
                next_page = url_for('dashboard')
            return redirect(next_page)
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))

# Dashboard
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.can_access('dashboard'):
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    
    today = date.today()
    
    # Get dashboard statistics
    stats = {
        'todays_appointments': Appointment.query.filter(
            func.date(Appointment.appointment_date) == today
        ).count(),
        'total_clients': Client.query.filter_by(is_active=True).count(),
        'total_revenue_today': db.session.query(func.sum(Appointment.amount)).filter(
            func.date(Appointment.appointment_date) == today,
            Appointment.is_paid == True
        ).scalar() or 0,
        'total_revenue_month': db.session.query(func.sum(Appointment.amount)).filter(
            func.extract('month', Appointment.appointment_date) == today.month,
            func.extract('year', Appointment.appointment_date) == today.year,
            Appointment.is_paid == True
        ).scalar() or 0
    }
    
    # Get recent appointments
    recent_appointments = Appointment.query.filter(
        Appointment.appointment_date >= datetime.now() - timedelta(days=7)
    ).order_by(Appointment.appointment_date.desc()).limit(10).all()
    
    # Get low stock items
    low_stock_items = Inventory.query.filter(
        Inventory.current_stock <= Inventory.min_stock_level,
        Inventory.is_active == True
    ).limit(5).all()
    
    # Get expiring items
    expiring_items = Inventory.query.filter(
        Inventory.expiry_date <= today + timedelta(days=30),
        Inventory.expiry_date > today,
        Inventory.is_active == True
    ).limit(5).all()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_appointments=recent_appointments,
                         low_stock_items=low_stock_items,
                         expiring_items=expiring_items)

# Bookings & Calendar
@app.route('/bookings')
@login_required
def bookings():
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get date filter from query params
    filter_date = request.args.get('date')
    if filter_date:
        try:
            filter_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
        except ValueError:
            filter_date = date.today()
    else:
        filter_date = date.today()
    
    appointments = Appointment.query.filter(
        func.date(Appointment.appointment_date) == filter_date
    ).order_by(Appointment.appointment_date).all()
    
    # Get data for form dropdowns
    clients = Client.query.filter_by(is_active=True).order_by(Client.first_name).all()
    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
    staff = User.query.filter(User.role.in_(['staff', 'manager', 'admin']), User.is_active == True).order_by(User.first_name).all()
    
    form = AppointmentForm()
    form.client_id.choices = [(c.id, c.full_name) for c in clients]
    form.service_id.choices = [(s.id, f"{s.name} - ${s.price}") for s in services]
    form.staff_id.choices = [(s.id, s.full_name) for s in staff]
    
    return render_template('bookings.html', 
                         appointments=appointments, 
                         form=form, 
                         filter_date=filter_date,
                         clients=clients,
                         services=services,
                         staff=staff,
                         timedelta=timedelta,
                         date=date)

@app.route('/bookings/add', methods=['POST'])
@login_required
def add_appointment():
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = AppointmentForm()
    
    # Populate choices
    clients = Client.query.filter_by(is_active=True).all()
    services = Service.query.filter_by(is_active=True).all()
    staff = User.query.filter(User.role.in_(['staff', 'manager', 'admin']), User.is_active == True).all()
    
    form.client_id.choices = [(c.id, c.full_name) for c in clients]
    form.service_id.choices = [(s.id, s.name) for s in services]
    form.staff_id.choices = [(s.id, s.full_name) for s in staff]
    
    if form.validate_on_submit():
        service = Service.query.get(form.service_id.data)
        end_time = form.appointment_date.data + timedelta(minutes=service.duration)
        
        appointment = Appointment(
            client_id=form.client_id.data,
            service_id=form.service_id.data,
            staff_id=form.staff_id.data,
            appointment_date=form.appointment_date.data,
            end_time=end_time,
            notes=form.notes.data,
            amount=form.amount.data or service.price,
            discount=form.discount.data or 0.0
        )
        
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment created successfully', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('bookings'))

# Staff Management
@app.route('/staff')
@login_required
def staff():
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    staff_members = User.query.filter_by(is_active=True).order_by(User.first_name).all()
    form = UserForm()
    
    return render_template('staff.html', staff_members=staff_members, form=form)

@app.route('/staff/add', methods=['POST'])
@login_required
def add_staff():
    if not current_user.can_access('staff') or not current_user.has_role('admin'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = UserForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter(
            or_(User.username == form.username.data, User.email == form.email.data)
        ).first()
        
        if existing_user:
            flash('Username or email already exists', 'danger')
            return redirect(url_for('staff'))
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            role=form.role.data,
            commission_rate=form.commission_rate.data or 0.0,
            hourly_rate=form.hourly_rate.data or 0.0,
            is_active=form.is_active.data
        )
        
        # Set default password
        user.set_password('password123')
        
        db.session.add(user)
        db.session.commit()
        flash('Staff member added successfully. Default password: password123', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('staff'))

# Clients
@app.route('/clients')
@login_required
def clients():
    if not current_user.can_access('clients'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    search = request.args.get('search', '')
    if search:
        clients_list = Client.query.filter(
            or_(
                Client.first_name.ilike(f'%{search}%'),
                Client.last_name.ilike(f'%{search}%'),
                Client.phone.ilike(f'%{search}%'),
                Client.email.ilike(f'%{search}%')
            )
        ).order_by(Client.first_name).all()
    else:
        clients_list = Client.query.filter_by(is_active=True).order_by(Client.first_name).all()
    
    form = ClientForm()
    
    return render_template('clients.html', clients=clients_list, form=form, search=search)

@app.route('/clients/add', methods=['POST'])
@login_required
def add_client():
    if not current_user.can_access('clients'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = ClientForm()
    if form.validate_on_submit():
        # Check if email already exists (if provided)
        if form.email.data:
            existing_client = Client.query.filter_by(email=form.email.data).first()
            if existing_client:
                flash('Email already exists', 'danger')
                return redirect(url_for('clients'))
        
        client = Client(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            address=form.address.data,
            preferences=form.preferences.data,
            allergies=form.allergies.data,
            notes=form.notes.data
        )
        
        db.session.add(client)
        db.session.commit()
        flash('Client added successfully', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('clients'))

# Billing
@app.route('/billing')
@login_required
def billing():
    if not current_user.can_access('billing'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get pending payments
    pending_appointments = Appointment.query.filter_by(
        is_paid=False, 
        status='completed'
    ).order_by(Appointment.appointment_date.desc()).all()
    
    # Get recent invoices
    recent_invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(20).all()
    
    return render_template('billing.html', 
                         pending_appointments=pending_appointments,
                         recent_invoices=recent_invoices)

@app.route('/billing/mark_paid/<int:appointment_id>')
@login_required
def mark_paid(appointment_id):
    if not current_user.can_access('billing'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.is_paid = True
    
    # Update client statistics
    client = appointment.client
    client.total_spent += appointment.amount
    client.total_visits += 1
    client.last_visit = appointment.appointment_date
    
    db.session.commit()
    flash('Payment marked as received', 'success')
    
    return redirect(url_for('billing'))

# Inventory
@app.route('/inventory')
@login_required
def inventory():
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    items = Inventory.query.filter_by(is_active=True).order_by(Inventory.name).all()
    form = InventoryForm()
    
    return render_template('inventory.html', items=items, form=form)

@app.route('/inventory/add', methods=['POST'])
@login_required
def add_inventory():
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = InventoryForm()
    if form.validate_on_submit():
        item = Inventory(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            current_stock=form.current_stock.data,
            min_stock_level=form.min_stock_level.data,
            unit_price=form.unit_price.data or 0.0,
            supplier_name=form.supplier_name.data,
            supplier_contact=form.supplier_contact.data,
            expiry_date=form.expiry_date.data
        )
        
        db.session.add(item)
        db.session.commit()
        flash('Inventory item added successfully', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('inventory'))

# Expenses
@app.route('/expenses')
@login_required
def expenses():
    if not current_user.can_access('expenses'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get filter parameters
    month = request.args.get('month', str(date.today().month))
    year = request.args.get('year', str(date.today().year))
    
    try:
        month = int(month)
        year = int(year)
    except ValueError:
        month = date.today().month
        year = date.today().year
    
    expense_list = Expense.query.filter(
        func.extract('month', Expense.expense_date) == month,
        func.extract('year', Expense.expense_date) == year
    ).order_by(Expense.expense_date.desc()).all()
    
    # Calculate total expenses
    total_expenses = sum(expense.amount for expense in expense_list)
    
    form = ExpenseForm()
    
    return render_template('expenses.html', 
                         expenses=expense_list, 
                         form=form, 
                         total_expenses=total_expenses,
                         current_month=month,
                         current_year=year)

@app.route('/expenses/add', methods=['POST'])
@login_required
def add_expense():
    if not current_user.can_access('expenses'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(
            description=form.description.data,
            amount=form.amount.data,
            category=form.category.data,
            expense_date=form.expense_date.data,
            receipt_number=form.receipt_number.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('expenses'))

# Reports
@app.route('/reports')
@login_required
def reports():
    if not current_user.can_access('reports'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get report parameters
    start_date = request.args.get('start_date', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
    
    # Revenue report
    revenue_data = db.session.query(
        func.date(Appointment.appointment_date).label('date'),
        func.sum(Appointment.amount).label('total')
    ).filter(
        func.date(Appointment.appointment_date).between(start_date, end_date),
        Appointment.is_paid == True
    ).group_by(func.date(Appointment.appointment_date)).all()
    
    # Staff performance
    staff_performance = db.session.query(
        User.first_name,
        User.last_name,
        func.count(Appointment.id).label('appointments'),
        func.sum(Appointment.amount).label('revenue')
    ).join(Appointment).filter(
        func.date(Appointment.appointment_date).between(start_date, end_date),
        Appointment.is_paid == True
    ).group_by(User.id).all()
    
    # Service popularity
    service_stats = db.session.query(
        Service.name,
        func.count(Appointment.id).label('bookings'),
        func.sum(Appointment.amount).label('revenue')
    ).join(Appointment).filter(
        func.date(Appointment.appointment_date).between(start_date, end_date)
    ).group_by(Service.id).all()
    
    return render_template('reports.html',
                         revenue_data=revenue_data,
                         staff_performance=staff_performance,
                         service_stats=service_stats,
                         start_date=start_date,
                         end_date=end_date)

# Settings
@app.route('/settings')
@login_required
def settings():
    if not current_user.can_access('all') and not current_user.has_role('admin'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    services = Service.query.order_by(Service.name).all()
    packages = Package.query.order_by(Package.name).all()
    
    service_form = ServiceForm()
    package_form = PackageForm()
    
    return render_template('settings.html', 
                         services=services, 
                         packages=packages,
                         service_form=service_form,
                         package_form=package_form)

@app.route('/settings/services/add', methods=['POST'])
@login_required
def add_service():
    if not current_user.has_role('admin') and not current_user.has_role('manager'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(
            name=form.name.data,
            description=form.description.data,
            duration=form.duration.data,
            price=form.price.data,
            category=form.category.data,
            is_active=form.is_active.data
        )
        
        db.session.add(service)
        db.session.commit()
        flash('Service added successfully', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('settings'))

# Subscription Packages Management
@app.route('/packages')
@login_required
def packages():
    packages = Package.query.all()
    client_packages = ClientPackage.query.filter_by(is_active=True).all()
    return render_template('packages.html', packages=packages, client_packages=client_packages)

@app.route('/packages/add', methods=['POST'])
@login_required
def add_package():
    form = PackageForm()
    if form.validate_on_submit():
        package = Package(
            name=form.name.data,
            description=form.description.data,
            duration_months=form.duration_months.data,
            total_price=form.total_price.data,
            discount_percentage=form.discount_percentage.data or 0.0
        )
        db.session.add(package)
        db.session.commit()
        flash('Package added successfully', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    return redirect(url_for('packages'))

# WhatsApp Notification System
@app.route('/notifications')
@login_required
def notifications():
    # Get upcoming appointments for notifications
    tomorrow = datetime.now() + timedelta(days=1)
    upcoming_appointments = Appointment.query.filter(
        Appointment.appointment_date >= datetime.now(),
        Appointment.appointment_date <= tomorrow,
        Appointment.status == 'scheduled'
    ).all()
    
    # Get clients with expiring packages
    expiring_packages = ClientPackage.query.filter(
        ClientPackage.expiry_date <= datetime.now() + timedelta(days=7),
        ClientPackage.is_active == True
    ).all()
    
    return render_template('notifications.html', 
                         upcoming_appointments=upcoming_appointments,
                         expiring_packages=expiring_packages)

# Face Recognition Check-In
@app.route('/checkin')
@login_required
def checkin():
    # Get today's appointments for check-in
    today = datetime.now().date()
    todays_appointments = Appointment.query.filter(
        func.date(Appointment.appointment_date) == today,
        Appointment.status.in_(['scheduled', 'confirmed'])
    ).all()
    
    return render_template('checkin.html', appointments=todays_appointments)

@app.route('/checkin/<int:appointment_id>')
@login_required
def process_checkin(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'in_progress'
    db.session.commit()
    flash(f'Checked in {appointment.client.full_name} for {appointment.service.name}', 'success')
    return redirect(url_for('checkin'))

# Expiring Product Alerts
@app.route('/alerts')
@login_required
def alerts():
    # Get low stock items
    low_stock_items = Inventory.query.filter(
        Inventory.current_stock <= Inventory.min_stock_level,
        Inventory.is_active == True
    ).all()
    
    # Get expiring items (within 30 days)
    expiring_soon = Inventory.query.filter(
        Inventory.expiry_date <= datetime.now().date() + timedelta(days=30),
        Inventory.expiry_date > datetime.now().date(),
        Inventory.is_active == True
    ).all()
    
    # Get expired items
    expired_items = Inventory.query.filter(
        Inventory.expiry_date <= datetime.now().date(),
        Inventory.is_active == True
    ).all()
    
    return render_template('alerts.html', 
                         low_stock_items=low_stock_items,
                         expiring_soon=expiring_soon,
                         expired_items=expired_items)

# API endpoints for AJAX requests
@app.route('/api/appointments/<date>')
@login_required
def api_appointments(date):
    try:
        appointment_date = datetime.strptime(date, '%Y-%m-%d').date()
        appointments = Appointment.query.filter(
            func.date(Appointment.appointment_date) == appointment_date
        ).all()
        
        return jsonify([{
            'id': apt.id,
            'title': f"{apt.client.full_name} - {apt.service.name}",
            'start': apt.appointment_date.isoformat(),
            'end': apt.end_time.isoformat(),
            'staff': apt.assigned_staff.full_name,
            'status': apt.status
        } for apt in appointments])
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

@app.route('/api/staff_schedule/<int:staff_id>')
@login_required
def api_staff_schedule(staff_id):
    schedules = StaffSchedule.query.filter_by(staff_id=staff_id).all()
    return jsonify([{
        'day': schedule.day_of_week,
        'start_time': schedule.start_time.strftime('%H:%M'),
        'end_time': schedule.end_time.strftime('%H:%M'),
        'available': schedule.is_available
    } for schedule in schedules])

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Initialize default data if running for the first time
def create_default_data():
    # Create default admin user if no users exist
    if User.query.count() == 0:
        admin = User(
            username='admin',
            email='admin@spa.com',
            first_name='System',
            last_name='Administrator',
            role='admin'
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        
        # Add some default services
        services = [
            Service(name='Basic Haircut', duration=30, price=25.00, category='hair'),
            Service(name='Hair Wash & Blow Dry', duration=45, price=35.00, category='hair'),
            Service(name='Facial Treatment', duration=60, price=60.00, category='facial'),
            Service(name='Relaxing Massage', duration=90, price=80.00, category='massage'),
            Service(name='Manicure', duration=45, price=30.00, category='nails'),
            Service(name='Pedicure', duration=60, price=40.00, category='nails'),
        ]
        
        for service in services:
            db.session.add(service)
        
        db.session.commit()
