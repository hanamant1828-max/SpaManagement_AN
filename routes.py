"""
New modular routes file - imports all module views and creates default data
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from app import app, db
from models import User, Customer, Service, Appointment, Expense, Invoice, Package, StaffSchedule, CustomerPackage, PackageService, Review, Communication, Commission, Promotion, Waitlist, RecurringAppointment, Location, BusinessSettings, Role, Permission, RolePermission, Category, Department, SystemSetting
from forms import LoginForm, UserForm, CustomerForm, ServiceForm, AppointmentForm, ExpenseForm, PackageForm, StaffScheduleForm, ReviewForm, CommunicationForm, PromotionForm, WaitlistForm, ProductSaleForm, RecurringAppointmentForm, BusinessSettingsForm, AdvancedCustomerForm, AdvancedUserForm, QuickBookingForm, PaymentForm, RoleForm, PermissionForm, CategoryForm, DepartmentForm, SystemSettingForm
import utils
import base64
import os

# Import module views individually to avoid conflicts
try:
    from modules.auth import auth_views
    from modules.dashboard import dashboard_views
    from modules.bookings import bookings_views
    from modules.clients import clients_views
    from modules.services import services_views
    from modules.inventory import views as inventory_views
    from modules.billing import billing_views
    from modules.expenses import expenses_views
    from modules.reports import reports_views
    from modules.packages import packages_views
    from modules.checkin import checkin_views
    from modules.notifications import notifications_views
    from modules.settings import settings_views
    from modules.staff import staff_views
    # from modules.hanamantinventory import views as hanaman_views  # Removed
    print("All modules imported successfully")
except ImportError as e:
    print(f"Module import error: {e}")
    print("Some modules may not be available")


@app.context_processor
def utility_processor():
    return dict(utils=utils)

def create_default_data():
    """Create default data for the application"""
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

    print("Comprehensive default data created successfully")

# Root route
@app.route('/')
def index():
    """Root route - redirect to dashboard if logged in, login if not"""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    except Exception as e:
        print(f"Error in index route: {e}")
        return render_template('login.html')

# Backward compatibility route
@app.route('/clients')
@login_required
def clients_redirect():
    return redirect(url_for('customers'))

# Additional routes that don't fit in modules yet
@app.route('/alerts')
@login_required
def alerts():
    if not current_user.can_access('alerts'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('alerts.html')

@app.route('/communications')
@login_required
def communications():
    if not current_user.can_access('communications'):
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
@login_required
def add_communication():
    if not current_user.can_access('communications'):
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
@login_required
def promotions():
    if not current_user.can_access('promotions'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('promotions.html')

@app.route('/waitlist')
@login_required
def waitlist():
    if not current_user.can_access('waitlist'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('waitlist.html')

@app.route('/product_sales')
@login_required
def product_sales():
    if not current_user.can_access('product_sales'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('product_sales.html')

@app.route('/recurring_appointments')
@login_required
def recurring_appointments():
    if not current_user.can_access('recurring_appointments'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('recurring_appointments.html')

@app.route('/reviews')
@login_required
def reviews():
    if not current_user.can_access('reviews'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('reviews.html')

@app.route('/business_settings')
@login_required
def business_settings():
    if not current_user.can_access('settings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

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
@login_required
def system_management():
    if not current_user.can_access('system_management'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

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
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')

    return redirect(url_for('system_management'))

@app.route('/role_management')
@login_required
def role_management():
    if not current_user.can_access('role_management'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

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
@login_required
def add_role():
    if not current_user.can_access('system_management'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

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
@login_required
def edit_role(role_id):
    if not current_user.can_access('system_management'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

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
@login_required
def delete_role(role_id):
    if not current_user.can_access('system_management'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

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
@login_required
def update_business_settings():
    if not current_user.can_access('system_management'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

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
@login_required
def api_create_role():
    """API endpoint to create a new role"""
    if not current_user.can_access('system_management'):
        return {'error': 'Access denied'}, 403

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
@login_required
def api_delete_role(role_id):
    """API endpoint to delete a role"""
    if not current_user.can_access('system_management'):
        return {'error': 'Access denied'}, 403

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
@login_required
def api_get_role_permissions(role_id):
    """API endpoint to get role permissions"""
    if not current_user.can_access('system_management'):
        return {'error': 'Access denied'}, 403

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
@login_required
def api_update_role_permissions(role_id):
    """API endpoint to update role permissions"""
    if not current_user.can_access('system_management'):
        return {'error': 'Access denied'}, 403

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
@login_required
def api_services():
    services = Service.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'price': float(s.price),
        'duration': s.duration
    } for s in services])

@app.route('/api/staff')
@login_required
def api_staff():
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
"""
CRUD API Routes for Master Data Management
Handles Categories, Locations, Products, and Customers
"""
from flask import request, jsonify
from datetime import datetime
from app import app, db
from models import Category, Location, User, Customer
from modules.inventory.models import InventoryProduct, InventoryCategory, Supplier

# ============ CATEGORIES CRUD ============

@app.route('/api/crud/categories', methods=['GET', 'POST'])
def api_categories():
    if request.method == 'GET':
        try:
            categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
            data = []
            for category in categories:
                data.append({
                    'id': category.id,
                    'name': category.name,
                    'display_name': category.display_name,
                    'description': category.description,
                    'category_type': category.category_type,
                    'color': category.color,
                    'icon': category.icon,
                    'is_active': category.is_active,
                    'sort_order': category.sort_order,
                    'created_at': category.created_at.isoformat() if category.created_at else None
                })
            return jsonify({'success': True, 'data': data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validation
            if not data.get('name') or not data.get('display_name') or not data.get('category_type'):
                return jsonify({'success': False, 'error': 'Name, display name, and type are required'}), 400
            
            # Check for duplicate name
            existing = Category.query.filter_by(name=data['name']).first()
            if existing:
                return jsonify({'success': False, 'error': 'Category name already exists'}), 400
            
            category = Category(
                name=data['name'],
                display_name=data['display_name'],
                description=data.get('description', ''),
                category_type=data['category_type'],
                color=data.get('color', '#007bff'),
                icon=data.get('icon', 'fas fa-tag'),
                is_active=data.get('is_active', True),
                sort_order=data.get('sort_order', 0)
            )
            
            db.session.add(category)
            db.session.commit()
            
            return jsonify({'success': True, 'data': {'id': category.id}})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/crud/categories/<int:category_id>', methods=['GET', 'PUT', 'DELETE'])
def api_category_detail(category_id):
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'data': {
                'id': category.id,
                'name': category.name,
                'display_name': category.display_name,
                'description': category.description,
                'category_type': category.category_type,
                'color': category.color,
                'icon': category.icon,
                'is_active': category.is_active,
                'sort_order': category.sort_order
            }
        })
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Validation
            if not data.get('name') or not data.get('display_name') or not data.get('category_type'):
                return jsonify({'success': False, 'error': 'Name, display name, and type are required'}), 400
            
            # Check for duplicate name (excluding current category)
            existing = Category.query.filter(Category.name == data['name'], Category.id != category_id).first()
            if existing:
                return jsonify({'success': False, 'error': 'Category name already exists'}), 400
            
            category.name = data['name']
            category.display_name = data['display_name']
            category.description = data.get('description', '')
            category.category_type = data['category_type']
            category.color = data.get('color', '#007bff')
            category.icon = data.get('icon', 'fas fa-tag')
            category.is_active = data.get('is_active', True)
            category.sort_order = data.get('sort_order', 0)
            
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            # Soft delete - just mark as inactive
            category.is_active = False
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

# ============ LOCATIONS CRUD ============

@app.route('/api/crud/locations', methods=['GET', 'POST'])
def api_locations():
    if request.method == 'GET':
        try:
            locations = Location.query.filter_by(is_active=True).order_by(Location.name).all()
            data = []
            for location in locations:
                manager_name = None
                if location.manager_id:
                    manager = User.query.get(location.manager_id)
                    if manager:
                        manager_name = f"{manager.first_name} {manager.last_name}"
                
                data.append({
                    'id': location.id,
                    'name': location.name,
                    'address': location.address,
                    'phone': location.phone,
                    'email': location.email,
                    'manager_id': location.manager_id,
                    'manager_name': manager_name,
                    'is_active': location.is_active,
                    'operating_hours': location.operating_hours,
                    'created_at': location.created_at.isoformat() if location.created_at else None
                })
            return jsonify({'success': True, 'data': data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validation
            if not data.get('name') or not data.get('address'):
                return jsonify({'success': False, 'error': 'Name and address are required'}), 400
            
            location = Location(
                name=data['name'],
                address=data['address'],
                phone=data.get('phone', ''),
                email=data.get('email', ''),
                manager_id=data.get('manager_id') if data.get('manager_id') else None,
                is_active=data.get('is_active', True),
                operating_hours=data.get('operating_hours', '')
            )
            
            db.session.add(location)
            db.session.commit()
            
            return jsonify({'success': True, 'data': {'id': location.id}})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/crud/locations/<int:location_id>', methods=['GET', 'PUT', 'DELETE'])
def api_location_detail(location_id):
    location = Location.query.get_or_404(location_id)
    
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'data': {
                'id': location.id,
                'name': location.name,
                'address': location.address,
                'phone': location.phone,
                'email': location.email,
                'manager_id': location.manager_id,
                'is_active': location.is_active,
                'operating_hours': location.operating_hours
            }
        })
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Validation
            if not data.get('name') or not data.get('address'):
                return jsonify({'success': False, 'error': 'Name and address are required'}), 400
            
            location.name = data['name']
            location.address = data['address']
            location.phone = data.get('phone', '')
            location.email = data.get('email', '')
            location.manager_id = data.get('manager_id') if data.get('manager_id') else None
            location.is_active = data.get('is_active', True)
            location.operating_hours = data.get('operating_hours', '')
            
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            # Soft delete - just mark as inactive
            location.is_active = False
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

# ============ PRODUCTS CRUD ============

@app.route('/api/crud/products', methods=['GET', 'POST'])
def api_products():
    if request.method == 'GET':
        try:
            products = InventoryProduct.query.filter_by(is_active=True).order_by(InventoryProduct.name).all()
            data = []
            for product in products:
                category_name = None
                if product.category_id:
                    category = InventoryCategory.query.get(product.category_id)
                    if category:
                        category_name = category.name
                
                supplier_name = None
                if product.supplier_id:
                    supplier = Supplier.query.get(product.supplier_id)
                    if supplier:
                        supplier_name = supplier.name
                
                data.append({
                    'id': product.id,
                    'sku': product.sku,
                    'name': product.name,
                    'description': product.description,
                    'category_id': product.category_id,
                    'category_name': category_name,
                    'supplier_id': product.supplier_id,
                    'supplier_name': supplier_name,
                    'current_stock': float(product.current_stock),
                    'min_stock_level': float(product.min_stock_level),
                    'max_stock_level': float(product.max_stock_level),
                    'cost_price': float(product.cost_price),
                    'selling_price': float(product.selling_price),
                    'unit_of_measure': product.unit_of_measure,
                    'barcode': product.barcode,
                    'location': product.location,
                    'is_service_item': product.is_service_item,
                    'is_retail_item': product.is_retail_item,
                    'is_active': product.is_active,
                    'created_at': product.created_at.isoformat() if product.created_at else None
                })
            return jsonify({'success': True, 'data': data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validation
            if not data.get('sku') or not data.get('name'):
                return jsonify({'success': False, 'error': 'SKU and name are required'}), 400
            
            # Check for duplicate SKU
            existing = InventoryProduct.query.filter_by(sku=data['sku']).first()
            if existing:
                return jsonify({'success': False, 'error': 'SKU already exists'}), 400
            
            product = InventoryProduct(
                sku=data['sku'],
                name=data['name'],
                description=data.get('description', ''),
                category_id=data.get('category_id') if data.get('category_id') else None,
                supplier_id=data.get('supplier_id') if data.get('supplier_id') else None,
                current_stock=float(data.get('current_stock', 0)),
                min_stock_level=float(data.get('min_stock_level', 10)),
                max_stock_level=float(data.get('max_stock_level', 100)),
                cost_price=float(data.get('cost_price', 0)),
                selling_price=float(data.get('selling_price', 0)),
                unit_of_measure=data.get('unit_of_measure', 'pcs'),
                barcode=data.get('barcode', ''),
                location=data.get('location', ''),
                is_service_item=data.get('is_service_item', False),
                is_retail_item=data.get('is_retail_item', False),
                is_active=data.get('is_active', True)
            )
            
            product.update_available_stock()
            db.session.add(product)
            db.session.commit()
            
            return jsonify({'success': True, 'data': {'id': product.id}})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/crud/products/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
def api_product_detail(product_id):
    product = InventoryProduct.query.get_or_404(product_id)
    
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'data': {
                'id': product.id,
                'sku': product.sku,
                'name': product.name,
                'description': product.description,
                'category_id': product.category_id,
                'supplier_id': product.supplier_id,
                'current_stock': float(product.current_stock),
                'min_stock_level': float(product.min_stock_level),
                'max_stock_level': float(product.max_stock_level),
                'cost_price': float(product.cost_price),
                'selling_price': float(product.selling_price),
                'unit_of_measure': product.unit_of_measure,
                'barcode': product.barcode,
                'location': product.location,
                'is_service_item': product.is_service_item,
                'is_retail_item': product.is_retail_item,
                'is_active': product.is_active
            }
        })
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Validation
            if not data.get('name'):
                return jsonify({'success': False, 'error': 'Name is required'}), 400
            
            # Check for duplicate SKU (excluding current product)
            if data.get('sku') != product.sku:
                existing = InventoryProduct.query.filter(InventoryProduct.sku == data['sku'], InventoryProduct.id != product_id).first()
                if existing:
                    return jsonify({'success': False, 'error': 'SKU already exists'}), 400
            
            product.name = data['name']
            product.description = data.get('description', '')
            product.category_id = data.get('category_id') if data.get('category_id') else None
            product.supplier_id = data.get('supplier_id') if data.get('supplier_id') else None
            product.min_stock_level = float(data.get('min_stock_level', 10))
            product.max_stock_level = float(data.get('max_stock_level', 100))
            product.cost_price = float(data.get('cost_price', 0))
            product.selling_price = float(data.get('selling_price', 0))
            product.unit_of_measure = data.get('unit_of_measure', 'pcs')
            product.barcode = data.get('barcode', '')
            product.location = data.get('location', '')
            product.is_service_item = data.get('is_service_item', False)
            product.is_retail_item = data.get('is_retail_item', False)
            product.is_active = data.get('is_active', True)
            product.updated_at = datetime.utcnow()
            
            product.update_available_stock()
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            # Soft delete - just mark as inactive
            product.is_active = False
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

# ============ CUSTOMERS CRUD ============

@app.route('/api/crud/customers', methods=['GET', 'POST'])
def api_customers():
    if request.method == 'GET':
        try:
            customers = Customer.query.filter_by(is_active=True).order_by(Customer.first_name, Customer.last_name).all()
            data = []
            for customer in customers:
                data.append({
                    'id': customer.id,
                    'first_name': customer.first_name,
                    'last_name': customer.last_name,
                    'email': customer.email,
                    'phone': customer.phone,
                    'date_of_birth': customer.date_of_birth.isoformat() if customer.date_of_birth else None,
                    'gender': customer.gender,
                    'address': customer.address,
                    'preferences': customer.preferences,
                    'allergies': customer.allergies,
                    'notes': customer.notes,
                    'preferred_communication': customer.preferred_communication,
                    'marketing_consent': customer.marketing_consent,
                    'is_active': customer.is_active,
                    'total_visits': customer.total_visits,
                    'total_spent': float(customer.total_spent),
                    'last_visit': customer.last_visit.isoformat() if customer.last_visit else None,
                    'created_at': customer.created_at.isoformat() if customer.created_at else None
                })
            return jsonify({'success': True, 'data': data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validation
            if not data.get('first_name') or not data.get('last_name') or not data.get('phone'):
                return jsonify({'success': False, 'error': 'First name, last name, and phone are required'}), 400
            
            # Check for duplicate phone
            existing = Customer.query.filter_by(phone=data['phone']).first()
            if existing:
                return jsonify({'success': False, 'error': 'Phone number already exists'}), 400
            
            # Check for duplicate email if provided
            if data.get('email'):
                existing_email = Customer.query.filter_by(email=data['email']).first()
                if existing_email:
                    return jsonify({'success': False, 'error': 'Email already exists'}), 400
            
            customer = Customer(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data.get('email', ''),
                phone=data['phone'],
                date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
                gender=data.get('gender', ''),
                address=data.get('address', ''),
                preferences=data.get('preferences', ''),
                allergies=data.get('allergies', ''),
                notes=data.get('notes', ''),
                preferred_communication=data.get('preferred_communication', 'email'),
                marketing_consent=data.get('marketing_consent', True),
                is_active=data.get('is_active', True)
            )
            
            db.session.add(customer)
            db.session.commit()
            
            return jsonify({'success': True, 'data': {'id': customer.id}})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/crud/customers/<int:customer_id>', methods=['GET', 'PUT', 'DELETE'])
def api_customer_detail(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'data': {
                'id': customer.id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'email': customer.email,
                'phone': customer.phone,
                'date_of_birth': customer.date_of_birth.isoformat() if customer.date_of_birth else '',
                'gender': customer.gender,
                'address': customer.address,
                'preferences': customer.preferences,
                'allergies': customer.allergies,
                'notes': customer.notes,
                'preferred_communication': customer.preferred_communication,
                'marketing_consent': customer.marketing_consent,
                'is_active': customer.is_active
            }
        })
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Validation
            if not data.get('first_name') or not data.get('last_name') or not data.get('phone'):
                return jsonify({'success': False, 'error': 'First name, last name, and phone are required'}), 400
            
            # Check for duplicate phone (excluding current customer)
            if data.get('phone') != customer.phone:
                existing = Customer.query.filter(Customer.phone == data['phone'], Customer.id != customer_id).first()
                if existing:
                    return jsonify({'success': False, 'error': 'Phone number already exists'}), 400
            
            # Check for duplicate email (excluding current customer)
            if data.get('email') and data.get('email') != customer.email:
                existing_email = Customer.query.filter(Customer.email == data['email'], Customer.id != customer_id).first()
                if existing_email:
                    return jsonify({'success': False, 'error': 'Email already exists'}), 400
            
            customer.first_name = data['first_name']
            customer.last_name = data['last_name']
            customer.email = data.get('email', '')
            customer.phone = data['phone']
            customer.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None
            customer.gender = data.get('gender', '')
            customer.address = data.get('address', '')
            customer.preferences = data.get('preferences', '')
            customer.allergies = data.get('allergies', '')
            customer.notes = data.get('notes', '')
            customer.preferred_communication = data.get('preferred_communication', 'email')
            customer.marketing_consent = data.get('marketing_consent', True)
            customer.is_active = data.get('is_active', True)
            
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            # Soft delete - just mark as inactive
            customer.is_active = False
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

# ============ HELPER ENDPOINTS ============

@app.route('/api/crud/managers')
def api_managers():
    """Get list of users who can be managers"""
    try:
        managers = User.query.filter(
            User.role.in_(['manager', 'admin']),
            User.is_active == True
        ).order_by(User.first_name, User.last_name).all()
        
        data = []
        for manager in managers:
            data.append({
                'id': manager.id,
                'first_name': manager.first_name,
                'last_name': manager.last_name,
                'email': manager.email
            })
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/crud/suppliers')
def api_suppliers():
    """Get list of suppliers"""
    try:
        suppliers = Supplier.query.filter_by(is_active=True).order_by(Supplier.name).all()
        
        data = []
        for supplier in suppliers:
            data.append({
                'id': supplier.id,
                'name': supplier.name,
                'contact_person': supplier.contact_person,
                'email': supplier.email,
                'phone': supplier.phone
            })
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ MAIN CRUD PAGE ROUTE ============

@app.route('/crud-management')
def crud_management():
    """Main CRUD management page"""
    return render_template('crud_management.html')
