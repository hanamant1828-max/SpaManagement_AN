from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from app import app, db
from models import User, Client, Service, Appointment, Inventory, Expense, Invoice, Package, StaffSchedule, ClientPackage, PackageService, Review, Communication, Commission, ProductSale, Promotion, Waitlist, RecurringAppointment, Location, BusinessSettings, Role, Permission, RolePermission, Category, Department, SystemSetting
from forms import LoginForm, UserForm, ClientForm, ServiceForm, AppointmentForm, InventoryForm, ExpenseForm, PackageForm, StaffScheduleForm, ReviewForm, CommunicationForm, PromotionForm, WaitlistForm, ProductSaleForm, RecurringAppointmentForm, BusinessSettingsForm, AdvancedClientForm, AdvancedUserForm, QuickBookingForm, PaymentForm, RoleForm, PermissionForm, CategoryForm, DepartmentForm, SystemSettingForm
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

# Initialize comprehensive default data for real-world operations
def create_default_data():
    """Create default data for the application"""
    # Create default roles and permissions first
    if Role.query.count() == 0:
        # Create default permissions
        permissions = [
            Permission(name='all', display_name='All Permissions', description='Full system access', module='system'),
            Permission(name='dashboard', display_name='Dashboard Access', description='View dashboard', module='dashboard'),
            Permission(name='bookings', display_name='Booking Management', description='Manage appointments', module='bookings'),
            Permission(name='clients', display_name='Client Management', description='Manage clients', module='clients'),
            Permission(name='staff', display_name='Staff Management', description='Manage staff', module='staff'),
            Permission(name='billing', display_name='Billing & Payments', description='Handle billing', module='billing'),
            Permission(name='inventory', display_name='Inventory Management', description='Manage inventory', module='inventory'),
            Permission(name='expenses', display_name='Expense Tracking', description='Track expenses', module='expenses'),
            Permission(name='reports', display_name='Reports & Analytics', description='View reports', module='reports'),
            Permission(name='system_management', display_name='System Management', description='System configuration', module='system'),
        ]
        
        for permission in permissions:
            db.session.add(permission)
        
        db.session.flush()  # Get IDs
        
        # Create default roles
        roles = [
            Role(name='admin', display_name='Administrator', description='Full system access', is_active=True),
            Role(name='manager', display_name='Manager', description='Management access', is_active=True),
            Role(name='staff', display_name='Staff Member', description='Basic staff access', is_active=True),
            Role(name='cashier', display_name='Cashier', description='Billing and payments', is_active=True),
        ]
        
        for role in roles:
            db.session.add(role)
        
        db.session.flush()  # Get IDs
        
        # Assign permissions to roles
        admin_role = Role.query.filter_by(name='admin').first()
        manager_role = Role.query.filter_by(name='manager').first()
        staff_role = Role.query.filter_by(name='staff').first()
        cashier_role = Role.query.filter_by(name='cashier').first()
        
        # Admin gets all permissions
        all_permission = Permission.query.filter_by(name='all').first()
        db.session.add(RolePermission(role_id=admin_role.id, permission_id=all_permission.id))
        
        # Manager permissions
        manager_permissions = ['dashboard', 'bookings', 'clients', 'staff', 'billing', 'inventory', 'expenses', 'reports']
        for perm_name in manager_permissions:
            perm = Permission.query.filter_by(name=perm_name).first()
            db.session.add(RolePermission(role_id=manager_role.id, permission_id=perm.id))
        
        # Staff permissions
        staff_permissions = ['dashboard', 'bookings', 'clients']
        for perm_name in staff_permissions:
            perm = Permission.query.filter_by(name=perm_name).first()
            db.session.add(RolePermission(role_id=staff_role.id, permission_id=perm.id))
        
        # Cashier permissions
        cashier_permissions = ['dashboard', 'bookings', 'billing']
        for perm_name in cashier_permissions:
            perm = Permission.query.filter_by(name=perm_name).first()
            db.session.add(RolePermission(role_id=cashier_role.id, permission_id=perm.id))
        
        db.session.commit()
        print("Default roles and permissions created successfully!")
    
    # Create default categories
    if Category.query.count() == 0:
        categories = [
            Category(name='face', display_name='Face', category_type='service', color='#ff6b6b', icon='fas fa-smile'),
            Category(name='body', display_name='Body', category_type='service', color='#4ecdc4', icon='fas fa-user'),
            Category(name='nails', display_name='Nails', category_type='service', color='#45b7d1', icon='fas fa-hand-sparkles'),
            Category(name='hair', display_name='Hair', category_type='service', color='#f9ca24', icon='fas fa-cut'),
            Category(name='skincare', display_name='Skincare', category_type='product', color='#6c5ce7', icon='fas fa-leaf'),
            Category(name='cosmetics', display_name='Cosmetics', category_type='product', color='#fd79a8', icon='fas fa-palette'),
            Category(name='supplies', display_name='Supplies', category_type='expense', color='#74b9ff', icon='fas fa-box'),
            Category(name='utilities', display_name='Utilities', category_type='expense', color='#00b894', icon='fas fa-bolt'),
        ]
        
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
        print("Default categories created successfully!")
    
    # Create default departments
    if Department.query.count() == 0:
        departments = [
            Department(name='spa', display_name='Spa Services', description='Facial and body treatments'),
            Department(name='salon', display_name='Salon Services', description='Hair and beauty services'),
            Department(name='nails', display_name='Nail Services', description='Manicure and pedicure'),
            Department(name='management', display_name='Management', description='Administrative staff'),
        ]
        
        for department in departments:
            db.session.add(department)
        
        db.session.commit()
        print("Default departments created successfully!")
    
    # Create default users
    if User.query.count() == 0:
        # Get the roles we just created
        admin_role = Role.query.filter_by(name='admin').first()
        manager_role = Role.query.filter_by(name='manager').first()
        staff_role = Role.query.filter_by(name='staff').first()
        
        # Create default admin user
        admin = User(
            username='admin',
            email='admin@spa.com',
            first_name='System',
            last_name='Administrator',
            role='admin',
            role_id=admin_role.id if admin_role else None,
            employee_id='EMP001',
            department='management',
            hire_date=date.today()
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create sample staff members
        staff_members = [
            User(
                username='sarah_stylist',
                email='sarah@spa.com',
                first_name='Sarah',
                last_name='Johnson',
                role='staff',
                role_id=staff_role.id if staff_role else None,
                commission_rate=15.0,
                hourly_rate=25.0,
                employee_id='EMP003',
                department='massage',
                hire_date=date.today(),
                specialties='Swedish massage, deep tissue, aromatherapy'
            )
        ]
        
        for staff in staff_members:
            staff.set_password('staff123')
            db.session.add(staff)
        
        # Create sample clients with advanced fields
        clients = [
            Client(
                first_name='Emma',
                last_name='Wilson',
                email='emma@example.com',
                phone='555-1234',
                preferences='Prefers morning appointments',
                allergies='None known',
                preferred_communication='email',
                referral_source='google',
                marketing_consent=True,
                total_visits=5,
                total_spent=375.00
            ),
            Client(
                first_name='Lisa',
                last_name='Martinez',
                email='lisa@example.com',
                phone='555-5678',
                preferences='Regular facials',
                allergies='Sensitive to fragrances',
                preferred_communication='sms',
                referral_source='friend_referral',
                marketing_consent=True,
                total_visits=12,
                total_spent=890.00,
                is_vip=True
            )
        ]
        
        db.session.add_all(clients)
        
        # Create comprehensive services
        services = [
            Service(name='Hair Cut & Style', duration=60, price=45.00, category='hair', description='Professional haircut with styling'),
            Service(name='Hair Color & Highlights', duration=120, price=95.00, category='hair', description='Full color service with highlights'),
            Service(name='Deep Cleansing Facial', duration=90, price=75.00, category='facial', description='Deep pore cleansing facial treatment'),
            Service(name='Anti-Aging Facial', duration=75, price=85.00, category='facial', description='Advanced anti-aging treatment'),
            Service(name='Swedish Massage', duration=60, price=80.00, category='massage', description='Relaxing full-body Swedish massage'),
            Service(name='Deep Tissue Massage', duration=90, price=110.00, category='massage', description='Therapeutic deep tissue massage'),
            Service(name='Manicure', duration=45, price=35.00, category='nails', description='Classic manicure with polish'),
            Service(name='Gel Manicure', duration=60, price=45.00, category='nails', description='Long-lasting gel manicure'),
            Service(name='Pedicure', duration=60, price=45.00, category='nails', description='Relaxing pedicure with massage'),
            Service(name='Body Wrap', duration=75, price=95.00, category='body', description='Detoxifying body wrap treatment')
        ]
        
        db.session.add_all(services)
        
        # Create comprehensive inventory
        inventory_items = [
            Inventory(name='Professional Shampoo', category='consumables', current_stock=15, min_stock_level=5, unit_price=12.99, supplier_name='Beauty Supply Co'),
            Inventory(name='Organic Facial Cleanser', category='consumables', current_stock=8, min_stock_level=3, unit_price=24.99, supplier_name='Natural Beauty'),
            Inventory(name='Premium Massage Oil', category='consumables', current_stock=12, min_stock_level=4, unit_price=18.50, supplier_name='Wellness Products'),
            Inventory(name='Luxury Nail Polish Set', category='retail', current_stock=25, min_stock_level=10, unit_price=8.99, supplier_name='Nail Care Ltd'),
            Inventory(name='Hair Styling Tools', category='equipment', current_stock=5, min_stock_level=2, unit_price=125.00, supplier_name='Pro Tools Inc'),
            Inventory(name='Disposable Towels', category='cleaning', current_stock=200, min_stock_level=50, unit_price=0.25, supplier_name='Hygiene Supply'),
            Inventory(name='Aromatherapy Candles', category='retail', current_stock=30, min_stock_level=15, unit_price=12.99, supplier_name='Scent Works')
        ]
        
        db.session.add_all(inventory_items)
        
        # Create business settings
        settings = [
            BusinessSettings(setting_key='business_name', setting_value='Elite Spa & Wellness', description='Business name'),
            BusinessSettings(setting_key='business_phone', setting_value='555-SPA-RELAX', description='Main business phone'),
            BusinessSettings(setting_key='business_email', setting_value='info@elitespa.com', description='Business email'),
            BusinessSettings(setting_key='tax_rate', setting_value='8.5', data_type='float', description='Tax rate percentage'),
            BusinessSettings(setting_key='currency_symbol', setting_value='$', description='Currency symbol'),
            BusinessSettings(setting_key='appointment_buffer', setting_value='15', data_type='integer', description='Buffer time between appointments'),
            BusinessSettings(setting_key='booking_advance_days', setting_value='60', data_type='integer', description='Maximum days to book in advance'),
            BusinessSettings(setting_key='cancellation_hours', setting_value='24', data_type='integer', description='Cancellation notice required in hours'),
            BusinessSettings(setting_key='no_show_fee', setting_value='25.00', data_type='float', description='No-show fee amount')
        ]
        
        db.session.add_all(settings)
        
        try:
            db.session.commit()
            print("Comprehensive default data created successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating default data: {e}")

# Advanced Routes for Real-World Operations

@app.route('/communications')
@login_required
def communications():
    """Client communication management"""
    if not current_user.can_access('communications'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    communications = Communication.query.order_by(Communication.created_at.desc()).limit(50).all()
    clients = Client.query.filter_by(is_active=True).all()
    form = CommunicationForm()
    form.client_id.choices = [(c.id, c.full_name) for c in clients]
    
    return render_template('communications.html', 
                         communications=communications, 
                         form=form,
                         clients=clients)

@app.route('/communications/add', methods=['POST'])
@login_required
def add_communication():
    """Add new communication record"""
    form = CommunicationForm()
    clients = Client.query.filter_by(is_active=True).all()
    form.client_id.choices = [(c.id, c.full_name) for c in clients]
    
    if form.validate_on_submit():
        communication = Communication(
            client_id=form.client_id.data,
            type=form.type.data,
            subject=form.subject.data,
            message=form.message.data,
            created_by=current_user.id,
            status='sent'
        )
        
        db.session.add(communication)
        db.session.commit()
        flash('Communication logged successfully', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('communications'))

@app.route('/promotions')
@login_required
def promotions():
    """Marketing promotions management"""
    if not current_user.can_access('promotions'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    active_promotions = Promotion.query.filter_by(is_active=True).all()
    expired_promotions = Promotion.query.filter_by(is_active=False).all()
    form = PromotionForm()
    
    return render_template('promotions.html', 
                         active_promotions=active_promotions,
                         expired_promotions=expired_promotions,
                         form=form)

@app.route('/promotions/add', methods=['POST'])
@login_required
def add_promotion():
    """Add new promotion"""
    form = PromotionForm()
    
    if form.validate_on_submit():
        promotion = Promotion(
            name=form.name.data,
            description=form.description.data,
            discount_type=form.discount_type.data,
            discount_value=form.discount_value.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            usage_limit=form.usage_limit.data,
            is_active=form.is_active.data
        )
        
        db.session.add(promotion)
        db.session.commit()
        flash('Promotion created successfully', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('promotions'))

@app.route('/waitlist')
@login_required
def waitlist():
    """Client waitlist management"""
    if not current_user.can_access('waitlist'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    waiting_clients = Waitlist.query.filter_by(status='waiting').all()
    contacted_clients = Waitlist.query.filter_by(status='contacted').all()
    
    form = WaitlistForm()
    clients = Client.query.filter_by(is_active=True).all()
    services = Service.query.filter_by(is_active=True).all()
    staff = User.query.filter(User.role.in_(['staff', 'manager']), User.is_active == True).all()
    
    form.client_id.choices = [(c.id, c.full_name) for c in clients]
    form.service_id.choices = [(s.id, s.name) for s in services]
    form.staff_id.choices = [(0, 'Any Staff')] + [(s.id, s.full_name) for s in staff]
    
    return render_template('waitlist.html',
                         waiting_clients=waiting_clients,
                         contacted_clients=contacted_clients,
                         form=form)

@app.route('/waitlist/add', methods=['POST'])
@login_required
def add_waitlist():
    """Add client to waitlist"""
    form = WaitlistForm()
    clients = Client.query.filter_by(is_active=True).all()
    services = Service.query.filter_by(is_active=True).all()
    staff = User.query.filter(User.role.in_(['staff', 'manager']), User.is_active == True).all()
    
    form.client_id.choices = [(c.id, c.full_name) for c in clients]
    form.service_id.choices = [(s.id, s.name) for s in services]
    form.staff_id.choices = [(0, 'Any Staff')] + [(s.id, s.full_name) for s in staff]
    
    if form.validate_on_submit():
        waitlist_entry = Waitlist(
            client_id=form.client_id.data,
            service_id=form.service_id.data,
            staff_id=form.staff_id.data if form.staff_id.data != 0 else None,
            preferred_date=form.preferred_date.data,
            preferred_time=form.preferred_time.data,
            is_flexible=form.is_flexible.data,
            expires_at=form.expires_at.data
        )
        
        db.session.add(waitlist_entry)
        db.session.commit()
        flash('Client added to waitlist successfully', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('waitlist'))

@app.route('/product-sales')
@login_required
def product_sales():
    """Retail product sales management"""
    if not current_user.can_access('sales'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    recent_sales = ProductSale.query.order_by(ProductSale.sale_date.desc()).limit(20).all()
    
    form = ProductSaleForm()
    products = Inventory.query.filter_by(category='retail', is_active=True).all()
    clients = Client.query.filter_by(is_active=True).all()
    
    form.inventory_id.choices = [(p.id, f"{p.name} - ${p.unit_price}") for p in products]
    form.client_id.choices = [(0, 'Walk-in Customer')] + [(c.id, c.full_name) for c in clients]
    
    return render_template('product_sales.html',
                         recent_sales=recent_sales,
                         form=form)

@app.route('/product-sales/add', methods=['POST'])
@login_required
def add_product_sale():
    """Process product sale"""
    form = ProductSaleForm()
    products = Inventory.query.filter_by(category='retail', is_active=True).all()
    clients = Client.query.filter_by(is_active=True).all()
    
    form.inventory_id.choices = [(p.id, f"{p.name} - ${p.unit_price}") for p in products]
    form.client_id.choices = [(0, 'Walk-in Customer')] + [(c.id, c.full_name) for c in clients]
    
    if form.validate_on_submit():
        product = Inventory.query.get(form.inventory_id.data)
        
        if product.current_stock >= form.quantity.data:
            sale = ProductSale(
                inventory_id=form.inventory_id.data,
                client_id=form.client_id.data if form.client_id.data != 0 else None,
                staff_id=current_user.id,
                quantity=form.quantity.data,
                unit_price=form.unit_price.data,
                total_amount=form.quantity.data * form.unit_price.data,
                payment_method=form.payment_method.data
            )
            
            # Update inventory
            product.current_stock -= form.quantity.data
            
            # Update client spending if applicable
            if form.client_id.data != 0:
                client = Client.query.get(form.client_id.data)
                client.total_spent += sale.total_amount
            
            # Update staff sales
            current_user.total_sales += sale.total_amount
            
            db.session.add(sale)
            db.session.commit()
            flash('Product sale recorded successfully', 'success')
        else:
            flash('Insufficient stock for this sale', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('product_sales'))

# Face Recognition Management Routes
@app.route('/face_management')
@login_required
def face_management():
    if not current_user.can_access('clients') or not current_user.has_role('admin'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get all clients for face registration
    clients = Client.query.filter_by(is_active=True).order_by(Client.first_name).all()
    
    # Get clients who already have face data
    clients_with_faces = Client.query.filter(
        Client.face_encoding.isnot(None),
        Client.is_active == True
    ).order_by(Client.first_name).all()
    
    return render_template('face_management.html', 
                         clients=clients, 
                         clients_with_faces=clients_with_faces)

@app.route('/api/save_face', methods=['POST'])
@login_required
def save_face():
    if not current_user.can_access('clients') or not current_user.has_role('admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    client_id = data.get('client_id')
    face_image = data.get('face_image')
    
    if not client_id or not face_image:
        return jsonify({'error': 'Missing client_id or face_image'}), 400
    
    client = Client.query.get_or_404(client_id)
    
    try:
        import base64
        import os
        from datetime import datetime
        
        # Save the image (remove data:image/jpeg;base64, prefix)
        if face_image.startswith('data:image'):
            face_image = face_image.split(',')[1]
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join('static', 'uploads', 'faces')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save image file
        filename = f"face_{client_id}_{int(datetime.timestamp(datetime.now()))}.jpg"
        filepath = os.path.join(upload_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(face_image))
        
        # Update client with face data
        client.face_image_url = f"/static/uploads/faces/{filename}"
        client.face_encoding = "simulated_encoding_data"  # In real app, this would be actual face encoding
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Face data saved successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/remove_face/<int:client_id>', methods=['DELETE'])
@login_required
def remove_face(client_id):
    if not current_user.can_access('clients') or not current_user.has_role('admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    client = Client.query.get_or_404(client_id)
    
    try:
        # Remove face image file if it exists
        if client.face_image_url:
            import os
            image_path = client.face_image_url.replace('/static/', 'static/')
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Clear face data from database
        client.face_encoding = None
        client.face_image_url = None
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Face data removed successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/recurring-appointments')
@login_required
def recurring_appointments():
    """Recurring appointment management"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    active_recurring = RecurringAppointment.query.filter_by(is_active=True).all()
    form = RecurringAppointmentForm()
    
    clients = Client.query.filter_by(is_active=True).all()
    services = Service.query.filter_by(is_active=True).all()
    staff = User.query.filter(User.role.in_(['staff', 'manager']), User.is_active == True).all()
    
    form.client_id.choices = [(c.id, c.full_name) for c in clients]
    form.service_id.choices = [(s.id, s.name) for s in services]
    form.staff_id.choices = [(s.id, s.full_name) for s in staff]
    
    return render_template('recurring_appointments.html',
                         active_recurring=active_recurring,
                         form=form)

@app.route('/business-settings')
@login_required
def business_settings():
    """Business configuration settings"""
    if not current_user.has_role('admin'):
        flash('Access denied - Admin only', 'danger')
        return redirect(url_for('dashboard'))
    
    settings = {s.setting_key: s.setting_value for s in BusinessSettings.query.all()}
    form = BusinessSettingsForm()
    
    # Populate form with current settings
    if settings:
        form.business_name.data = settings.get('business_name', '')
        form.business_phone.data = settings.get('business_phone', '')
        form.business_email.data = settings.get('business_email', '')
        form.business_address.data = settings.get('business_address', '')
        form.tax_rate.data = float(settings.get('tax_rate', 0))
        form.currency_symbol.data = settings.get('currency_symbol', '$')
        form.appointment_buffer.data = int(settings.get('appointment_buffer', 15))
        form.booking_advance_days.data = int(settings.get('booking_advance_days', 60))
        form.cancellation_hours.data = int(settings.get('cancellation_hours', 24))
        form.no_show_fee.data = float(settings.get('no_show_fee', 0))
    
    return render_template('business_settings.html', form=form, settings=settings)

@app.route('/reviews')
@login_required
def reviews():
    """Customer reviews management"""
    if not current_user.can_access('reviews'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(20).all()
    avg_rating = db.session.query(func.avg(Review.rating)).scalar() or 0
    
    return render_template('reviews.html',
                         recent_reviews=recent_reviews,
                         avg_rating=round(avg_rating, 1))

# CRUD Routes for Dynamic System Management

@app.route('/system-management')
@login_required
def system_management():
    """System management dashboard"""
    if not current_user.can_access('system_management'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get all data for the system management page
    roles = Role.query.all()
    permissions = Permission.query.all()
    categories = Category.query.all()
    departments = Department.query.all()
    system_settings = SystemSetting.query.all()
    
    # Initialize forms
    role_form = RoleForm()
    permission_form = PermissionForm()
    category_form = CategoryForm()
    department_form = DepartmentForm()
    setting_form = SystemSettingForm()
    
    # Populate form choices
    role_form.permissions.choices = [(p.id, p.display_name) for p in permissions]
    department_form.manager_id.choices = [(0, 'No Manager')] + [(u.id, u.full_name) for u in User.query.filter_by(is_active=True).all()]
    
    return render_template('system_management.html',
                         roles=roles,
                         permissions=permissions,
                         categories=categories,
                         departments=departments,
                         system_settings=system_settings,
                         role_form=role_form,
                         permission_form=permission_form,
                         category_form=category_form,
                         department_form=department_form,
                         setting_form=setting_form)

@app.route('/add-role', methods=['POST'])
@login_required
def add_role():
    """Add new role"""
    if not current_user.can_access('system_management'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = RoleForm()
    form.permissions.choices = [(p.id, p.display_name) for p in Permission.query.all()]
    
    if form.validate_on_submit():
        try:
            role = Role(
                name=form.name.data,
                display_name=form.display_name.data,
                description=form.description.data,
                is_active=form.is_active.data
            )
            db.session.add(role)
            db.session.flush()  # Get the ID
            
            # Add permissions
            for permission_id in form.permissions.data:
                role_permission = RolePermission(
                    role_id=role.id,
                    permission_id=permission_id
                )
                db.session.add(role_permission)
            
            db.session.commit()
            flash('Role added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding role: {str(e)}', 'danger')
    else:
        flash('Please fix the form errors', 'danger')
    
    return redirect(url_for('system_management'))

@app.route('/add-permission', methods=['POST'])
@login_required
def add_permission():
    """Add new permission"""
    if not current_user.can_access('system_management'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = PermissionForm()
    
    if form.validate_on_submit():
        try:
            permission = Permission(
                name=form.name.data,
                display_name=form.display_name.data,
                description=form.description.data,
                module=form.module.data,
                is_active=form.is_active.data
            )
            db.session.add(permission)
            db.session.commit()
            flash('Permission added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding permission: {str(e)}', 'danger')
    else:
        flash('Please fix the form errors', 'danger')
    
    return redirect(url_for('system_management'))

@app.route('/add-category', methods=['POST'])
@login_required
def add_category():
    """Add new category"""
    if not current_user.can_access('system_management'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = CategoryForm()
    
    if form.validate_on_submit():
        try:
            category = Category(
                name=form.name.data,
                display_name=form.display_name.data,
                description=form.description.data,
                category_type=form.category_type.data,
                color=form.color.data or '#007bff',
                icon=form.icon.data or 'fas fa-tag',
                is_active=form.is_active.data,
                sort_order=form.sort_order.data or 0
            )
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding category: {str(e)}', 'danger')
    else:
        flash('Please fix the form errors', 'danger')
    
    return redirect(url_for('system_management'))

@app.route('/add-department', methods=['POST'])
@login_required
def add_department():
    """Add new department"""
    if not current_user.can_access('system_management'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = DepartmentForm()
    form.manager_id.choices = [(0, 'No Manager')] + [(u.id, u.full_name) for u in User.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        try:
            department = Department(
                name=form.name.data,
                display_name=form.display_name.data,
                description=form.description.data,
                manager_id=form.manager_id.data if form.manager_id.data != 0 else None,
                is_active=form.is_active.data
            )
            db.session.add(department)
            db.session.commit()
            flash('Department added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding department: {str(e)}', 'danger')
    else:
        flash('Please fix the form errors', 'danger')
    
    return redirect(url_for('system_management'))

@app.route('/add-setting', methods=['POST'])
@login_required
def add_setting():
    """Add new system setting"""
    if not current_user.can_access('system_management'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = SystemSettingForm()
    
    if form.validate_on_submit():
        try:
            setting = SystemSetting(
                key=form.key.data,
                value=form.value.data,
                data_type=form.data_type.data,
                category=form.category.data,
                display_name=form.display_name.data,
                description=form.description.data,
                is_public=form.is_public.data
            )
            db.session.add(setting)
            db.session.commit()
            flash('Setting added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding setting: {str(e)}', 'danger')
    else:
        flash('Please fix the form errors', 'danger')
    
    return redirect(url_for('system_management'))
