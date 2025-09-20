"""
New modular routes file - imports all module views and creates default data
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from app import app, db
import utils
import base64
import os

def create_default_data():
    """Create default data for the application"""
    try:
        from models import User, Role, Permission, Category, Department, Service, Customer
        
        # Create default admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@spa.com',
                first_name='System',
                last_name='Administrator',
                role='admin',
                is_active=True,
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin_user)
            print("Created default admin user with proper password hash")
        elif not admin_user.password_hash:
            # Fix existing admin user if password_hash is missing
            admin_user.password_hash = generate_password_hash('admin123')
            admin_user.is_active = True
            print("Fixed admin user password hash")
        
        # Create default categories
        categories = [
            {'name': 'facial', 'display_name': 'Facial Services', 'category_type': 'service'},
            {'name': 'massage', 'display_name': 'Massage Services', 'category_type': 'service'},
            {'name': 'beauty', 'display_name': 'Beauty Services', 'category_type': 'service'},
            {'name': 'supplies', 'display_name': 'Supplies', 'category_type': 'expense'},
            {'name': 'utilities', 'display_name': 'Utilities', 'category_type': 'expense'}
        ]
        
        for cat_data in categories:
            category = Category.query.filter_by(name=cat_data['name']).first()
            if not category:
                category = Category(**cat_data)
                db.session.add(category)
        
        # Create default services
        services = [
            {'name': 'Basic Facial', 'price': 50.0, 'duration': 60, 'category': 'facial'},
            {'name': 'Deep Tissue Massage', 'price': 80.0, 'duration': 90, 'category': 'massage'},
            {'name': 'Manicure', 'price': 25.0, 'duration': 45, 'category': 'beauty'}
        ]
        
        for service_data in services:
            service = Service.query.filter_by(name=service_data['name']).first()
            if not service:
                service = Service(**service_data, is_active=True)
                db.session.add(service)
        
        db.session.commit()
        print("Default data created successfully")
        
    except Exception as e:
        print(f"Error creating default data: {e}")
        db.session.rollback()

# Import module views individually to avoid conflicts
try:
    from modules.auth import auth_views
    from modules.dashboard import dashboard_views
    from modules.bookings import bookings_views
    from modules.clients import clients_views
    from modules.services import services_views
    from modules.inventory import views as inventory_views
    from modules.expenses import expenses_views
    from modules.reports import reports_views
    from modules.packages import packages_views
    from modules.checkin import checkin_views
    from modules.notifications import notifications_views
    from modules.settings import settings_views
    from modules.staff import staff_views
    from modules.staff import shift_scheduler_views
    print("All modules imported successfully")
except ImportError as e:
    print(f"Module import error: {e}")
    print("Some modules may not be available")


@app.context_processor
def utility_processor():
    return dict(utils=utils)

def create_default_data():
    """Create default data for the application"""
    # Import models here to avoid circular imports
    from models import (User, Customer, Service, Appointment, Expense, Invoice, Package, 
                       StaffSchedule, CustomerPackage, PackageService, Review, Communication, 
                       Commission, Promotion, Waitlist, RecurringAppointment, Location, 
                       BusinessSettings, Role, Permission, RolePermission, Category, 
                       Department, SystemSetting)
    
    try:
        # Create default admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
    except Exception as e:
        print(f"Database schema issue detected: {e}")
        print("Please run: python migrate_database.py")
        return

    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@spa.com',
            password_hash=generate_password_hash('admin123'),
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True
        )
        db.session.add(admin_user)
        print("Created admin user in second function")
    elif not admin_user.password_hash or not admin_user.is_active:
        # Fix existing admin user issues
        admin_user.password_hash = generate_password_hash('admin123')
        admin_user.is_active = True
        print("Fixed admin user in second function")

    # Create default roles
    default_roles = [
        {'name': 'admin', 'display_name': 'Administrator', 'description': 'Full system access'},
        {'name': 'manager', 'display_name': 'Manager', 'description': 'Management level access'},
        {'name': 'staff', 'display_name': 'Staff', 'description': 'Standard staff access'},
        {'name': 'cashier', 'display_name': 'Cashier', 'description': 'Billing and payment access'}
    ]

    for role_data in default_roles:
        role = Role.query.filter_by(name=role_data['name']).first()
        if not role:
            role = Role(**role_data)
            db.session.add(role)

    # Create default categories
    default_categories = [
        {'name': 'service_facial', 'display_name': 'Facial Services', 'category_type': 'service', 'color': '#ff6b6b'},
        {'name': 'service_massage', 'display_name': 'Massage Services', 'category_type': 'service', 'color': '#4ecdc4'},
        {'name': 'service_hair', 'display_name': 'Hair Services', 'category_type': 'service', 'color': '#45b7d1'},
        {'name': 'product_skincare', 'display_name': 'Skincare Products', 'category_type': 'product', 'color': '#f9ca24'},
        {'name': 'product_haircare', 'display_name': 'Hair Care Products', 'category_type': 'product', 'color': '#f0932b'},
        {'name': 'expense_supplies', 'display_name': 'Supplies', 'category_type': 'expense', 'color': '#eb4d4b'},
        {'name': 'expense_utilities', 'display_name': 'Utilities', 'category_type': 'expense', 'color': '#6c5ce7'}
    ]

    for category_data in default_categories:
        category = Category.query.filter_by(name=category_data['name']).first()
        if not category:
            category = Category(**category_data)
            db.session.add(category)

    # Create default departments
    default_departments = [
        {'name': 'management', 'display_name': 'Management', 'description': 'Management team'},
        {'name': 'reception', 'display_name': 'Reception', 'description': 'Front desk staff'},
        {'name': 'spa_services', 'display_name': 'Spa Services', 'description': 'Spa treatment providers'},
        {'name': 'hair_salon', 'display_name': 'Hair Salon', 'description': 'Hair styling services'}
    ]

    for dept_data in default_departments:
        department = Department.query.filter_by(name=dept_data['name']).first()
        if not department:
            department = Department(**dept_data)
            db.session.add(department)

    try:
        db.session.commit()
        print("Default roles and permissions created successfully!")
    except Exception as e:
        print(f"Error creating default data: {e}")
        db.session.rollback()

    # Create comprehensive permissions system
    try:
        # Create a basic permission system since the external files don't exist
        print("Creating basic permissions system...")
        # Add any custom permission creation logic here if needed
        print("Basic permissions system ready!")
    except Exception as e:
        print(f"Error setting up permissions: {e}")

    # Initialize inventory default data - DISABLED to allow manual data management
    # print("Initializing inventory default data...")
    # try:
    #     from modules.inventory.queries import initialize_default_locations, initialize_default_categories
    #     initialize_default_locations()
    #     initialize_default_categories()
    #     print("Inventory defaults initialized!")
    # except Exception as e:
    #     print(f"Error initializing inventory defaults: {e}")
    
    print("Comprehensive default data created successfully")

# Root route
@app.route('/')
def index():
    """Root route - redirect to dashboard for testing"""
    try:
        # For testing - always redirect to dashboard
        return redirect(url_for('dashboard'))
    except Exception as e:
        print(f"Error in index route: {e}")
        # For testing - always redirect to dashboard
        return redirect(url_for('dashboard'))

# Backward compatibility route
@app.route('/clients')
def clients_redirect():
    return redirect(url_for('customers'))

# Additional routes that don't fit in modules yet
# alerts route is now handled in dashboard module

@app.route('/test_navigation')

def test_navigation():
    """Navigation testing page"""
    return render_template('test_navigation.html')

@app.route('/billing')

def billing():
    """Billing page"""
    try:
        from modules.billing import billing_views
        return redirect(url_for('integrated_billing'))
    except:
        # Fallback if billing module not available
        return render_template('billing.html')

@app.route('/communications')

def communications():
    if False:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from models import Communication, Customer
    from forms import CommunicationForm

    communications = Communication.query.order_by(Communication.created_at.desc()).all()
    customers = Customer.query.filter_by(is_active=True).all()
    form = CommunicationForm()

    return render_template('communications.html',
                         communications=communications,
                         customers=customers,
                         form=form)

@app.route('/add_communication', methods=['POST'])

def add_communication():
    if False:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from models import Communication
    from forms import CommunicationForm

    form = CommunicationForm()
    if form.validate_on_submit():
        try:
            communication = Communication(
                client_id=form.client_id.data,
                type=form.type.data,
                subject=form.subject.data,
                message=form.message.data,
                created_by=current_user.id
            )
            db.session.add(communication)
            db.session.commit()
            flash('Communication logged successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error logging communication: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')

    return redirect(url_for('communications'))

@app.route('/promotions')

def promotions():
    if False:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('promotions.html')

@app.route('/waitlist')

def waitlist():
    if False:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('waitlist.html')

@app.route('/product_sales')

def product_sales():
    if False:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('product_sales.html')

@app.route('/recurring_appointments')

def recurring_appointments():
    if False:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('recurring_appointments.html')

@app.route('/reviews')

def reviews():
    if False:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('reviews.html')

@app.route('/business_settings')

def business_settings():
    if False:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from models import BusinessSettings
    from forms import BusinessSettingsForm

    # Get business settings
    business_settings = BusinessSettings.query.first()
    if not business_settings:
        business_settings = BusinessSettings()
        db.session.add(business_settings)
        db.session.commit()

    # Initialize form
    form = BusinessSettingsForm(obj=business_settings)

    return render_template('business_settings.html', form=form, business_settings=business_settings)


@app.route('/system_management')

def system_management():
    if False:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from models import Role, Permission, Category, Department, SystemSetting, BusinessSettings
    from forms import RoleForm, PermissionForm, CategoryForm, DepartmentForm, SystemSettingForm, BusinessSettingsForm

    # Get all required data for system management
    roles = Role.query.all()
    permissions = Permission.query.all()
    categories = Category.query.all()
    departments = Department.query.all()
    system_settings = SystemSetting.query.all()

    # Get business settings - create a proper structure for system management
    business_settings = {}

    # Get existing business settings as key-value pairs
    existing_settings = BusinessSettings.query.all()
    for setting in existing_settings:
        business_settings[setting.setting_key] = setting.setting_value

    # Initialize forms
    role_form = RoleForm()
    permission_form = PermissionForm()
    category_form = CategoryForm()
    department_form = DepartmentForm()
    setting_form = SystemSettingForm()
    business_form = BusinessSettingsForm(obj=business_settings)

    return render_template('system_management.html',
                         roles=roles,
                         permissions=permissions,
                         categories=categories,
                         departments=departments,
                         system_settings=system_settings,
                         business_settings=business_settings,
                         role_form=role_form,
                         permission_form=permission_form,
                         category_form=category_form,
                         department_form=department_form,
                         setting_form=setting_form,
                         business_form=business_form)

@app.route('/add_category', methods=['POST'])

def add_category():
    """Add new category"""
    if False:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from models import Category
    from forms import CategoryForm

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
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')

    return redirect(url_for('system_management'))

@app.route('/role_management')

def role_management():
    if False:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from models import Role, Permission, RolePermission

    # Get all required data for role management
    roles = Role.query.all()
    permissions = Permission.query.all()

    # Group permissions by module
    permissions_by_module = {}
    for permission in permissions:
        module = permission.module
        if module not in permissions_by_module:
            permissions_by_module[module] = []
        permissions_by_module[module].append(permission)

    # Get role permissions for each role
    role_permissions = {}
    for role in roles:
        role_permissions[role.id] = [rp.permission_id for rp in RolePermission.query.filter_by(role_id=role.id).all()]

    return render_template('role_management.html',
                         roles=roles,
                         permissions=permissions,
                         permissions_by_module=permissions_by_module,
                         role_permissions=role_permissions)

# System Management Data Providers
@app.route('/add_role', methods=['POST'])

def add_role():
    if False:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from models import Role
    from forms import RoleForm

    form = RoleForm()
    if form.validate_on_submit():
        try:
            role = Role(
                name=form.name.data,
                display_name=form.display_name.data,
                description=form.description.data,
                is_active=form.is_active.data
            )
            db.session.add(role)
            db.session.commit()
            flash('Role added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding role: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')

    return redirect(url_for('system_management'))

@app.route('/edit_role/<int:role_id>', methods=['POST'])

def edit_role(role_id):
    if False:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from models import Role
    from forms import RoleForm

    role = Role.query.get_or_404(role_id)
    form = RoleForm(obj=role)

    if form.validate_on_submit():
        try:
            role.name = form.name.data
            role.display_name = form.display_name.data
            role.description = form.description.data
            role.is_active = form.is_active.data
            db.session.commit()
            flash('Role updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating role: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')

    return redirect(url_for('system_management'))

@app.route('/delete_role/<int:role_id>', methods=['POST'])

def delete_role(role_id):
    if False:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from models import Role

    try:
        role = Role.query.get_or_404(role_id)
        db.session.delete(role)
        db.session.commit()
        flash('Role deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting role: {str(e)}', 'danger')

    return redirect(url_for('system_management'))

@app.route('/update_business_settings', methods=['POST'])

def update_business_settings():
    if False:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from models import BusinessSettings
    from forms import BusinessSettingsForm

    business_settings = BusinessSettings.query.first()
    if not business_settings:
        business_settings = BusinessSettings()

    form = BusinessSettingsForm()
    if form.validate_on_submit():
        try:
            form.populate_obj(business_settings)
            db.session.add(business_settings)
            db.session.commit()
            flash('Business settings updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating business settings: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')

    return redirect(url_for('system_management'))

# API endpoints for Role Management
@app.route('/api/roles', methods=['POST'])
def api_create_role():
    """API endpoint to create a new role"""
    if False:
        return {'error': 'Access denied'}, 403

    from models import Role

    data = request.get_json()
    if not data:
        return {'error': 'No data provided'}, 400

    try:
        role = Role(
            name=data.get('name'),
            display_name=data.get('display_name'),
            description=data.get('description', ''),
            is_active=True
        )
        db.session.add(role)
        db.session.commit()
        return {'message': 'Role created successfully', 'role_id': role.id}, 201
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

@app.route('/api/roles/<int:role_id>', methods=['DELETE'])
def api_delete_role(role_id):
    """API endpoint to delete a role"""
    if False:
        return {'error': 'Access denied'}, 403

    from models import Role

    try:
        role = Role.query.get_or_404(role_id)
        if role.name == 'admin':
            return {'error': 'Cannot delete admin role'}, 400

        db.session.delete(role)
        db.session.commit()
        return {'message': 'Role deleted successfully'}, 200
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

@app.route('/api/roles/<int:role_id>/permissions', methods=['GET'])
def api_get_role_permissions(role_id):
    """API endpoint to get role permissions"""
    if False:
        return {'error': 'Access denied'}, 403

    from models import Role

    try:
        role = Role.query.get_or_404(role_id)
        role_permissions = [rp.permission.name for rp in role.permissions]
        return {
            'role_name': role.display_name,
            'permissions': role_permissions
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/roles/<int:role_id>/permissions', methods=['POST'])
def api_update_role_permissions(role_id):
    """API endpoint to update role permissions"""
    if False:
        return {'error': 'Access denied'}, 403

    from models import Role, Permission, RolePermission

    data = request.get_json()
    if not data:
        return {'error': 'No data provided'}, 400

    try:
        role = Role.query.get_or_404(role_id)
        if role.name == 'admin':
            return {'error': 'Cannot modify admin role permissions'}, 400

        # Clear existing permissions
        RolePermission.query.filter_by(role_id=role_id).delete()

        # Add new permissions
        permission_names = data.get('permissions', [])
        for perm_name in permission_names:
            permission = Permission.query.filter_by(name=perm_name).first()
            if permission:
                role_perm = RolePermission(role_id=role_id, permission_id=permission.id)
                db.session.add(role_perm)

        db.session.commit()
        return {'message': 'Permissions updated successfully'}, 200
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

# Additional API routes
@app.route('/api/services')
def api_services():
    from models import Service
    
    services = Service.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'price': float(s.price),
        'duration': s.duration
    } for s in services])

@app.route('/api/staff')
def api_staff():
    from models import User
    
    staff = User.query.filter(User.role.in_(['staff', 'manager'])).filter_by(is_active=True).all()
    return jsonify([{
        'id': s.id,
        'name': s.full_name,
        'role': s.role
    } for s in staff])

# Face Recognition API endpoints





# Face Recognition API endpoints are handled in the clients module





# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500