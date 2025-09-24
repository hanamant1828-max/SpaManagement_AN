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

# Student Offers API routes (global fallback)
@app.route('/api/student-offers', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/api/student-offers/<int:offer_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def student_offers_api_fallback(offer_id=None):
    """Fallback API routes for student offers"""
    try:
        # Import the packages blueprint functions
        from modules.packages.routes import (
            api_get_student_offers, api_create_student_offer, 
            api_get_student_offer, api_update_student_offer, api_delete_student_offer
        )

        # Route to appropriate function based on method and parameters
        if request.method == 'GET':
            if offer_id:
                return api_get_student_offer(offer_id)
            else:
                return api_get_student_offers()
        elif request.method == 'POST':
            return api_create_student_offer()
        elif request.method == 'PUT' and offer_id:
            return api_update_student_offer(offer_id)
        elif request.method == 'DELETE' and offer_id:
            return api_delete_student_offer(offer_id)
        else:
            return jsonify({'success': False, 'error': 'Invalid request'}), 400

    except Exception as e:
        print(f"API fallback error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Import module views individually to avoid conflicts
try:
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
    # Unaki Booking System API Routes imports
    from modules.unaki_booking.routes import *

    print("All modules imported successfully")
except ImportError as e:
    print(f"Module import error: {e}")
    print("Some modules may not be available")


# utility_processor moved to app.py to avoid conflicts

# Removed duplicate create_default_data function - using the one at the top of the file

# Root route is handled in app.py - removed duplicate to avoid conflicts

# Health check route for deployment  
@app.route('/health')
def health_check():
    return {
        'status': 'ok', 
        'service': 'spa_management',
        'version': '1.0.0'
    }, 200

# Backward compatibility route
@app.route('/clients')
def clients_redirect():
    return redirect(url_for('customers'))

# Package Assignment API
@app.route('/packages/api/assign', methods=['POST'])
@login_required
def assign_package():
    """API endpoint to assign package to customer"""
    try:
        print("Package assignment API called")
        data = request.get_json()
        print(f"Received data: {data}")

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # Handle both client_id and customer_id for compatibility
        customer_id = data.get('customer_id') or data.get('client_id')
        package_id = data.get('package_id')
        package_type = data.get('package_type', 'membership')

        print(f"Package ID: {package_id}, Customer ID: {customer_id}, Package Type: {package_type}")

        if not package_id or not customer_id:
            return jsonify({'success': False, 'error': 'Package ID and Customer ID are required'}), 400

        # Import models
        from models import Customer, ServicePackageAssignment, Membership, PrepaidPackage, ServicePackage
        from datetime import datetime, timedelta

        # Verify customer exists  
        customer = Customer.query.get(customer_id)
        if not customer:
            print(f"Customer {customer_id} not found")
            return jsonify({'success': False, 'error': 'Customer not found'}), 404

        print(f"Found customer: {customer.full_name}")

        # Get package details based on type
        package_template = None
        if package_type == 'membership':
            package_template = Membership.query.get(package_id)
        elif package_type == 'prepaid':
            package_template = PrepaidPackage.query.get(package_id)
        elif package_type == 'service_package':
            package_template = ServicePackage.query.get(package_id)

        if not package_template:
            return jsonify({'success': False, 'error': f'{package_type.title()} package not found'}), 404

        print(f"Found package template: {package_template.name}")

        # Calculate assignment details
        price_paid = data.get('price_paid')
        if price_paid is None:
            if hasattr(package_template, 'price'):
                price_paid = float(package_template.price)
            elif hasattr(package_template, 'actual_price'):
                price_paid = float(package_template.actual_price)
            else:
                price_paid = 0.0
        else:
            price_paid = float(price_paid)

        discount = float(data.get('discount', 0))

        print(f"Price paid: {price_paid}, discount: {discount}")

        # Calculate expiry date
        expiry_date = None
        if data.get('expiry_date'):
            expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d')
        else:
            # Use package validity
            if hasattr(package_template, 'validity_months') and package_template.validity_months:
                expiry_date = datetime.utcnow() + timedelta(days=package_template.validity_months * 30)
            else:
                expiry_date = datetime.utcnow() + timedelta(days=365)  # Default 1 year

        print(f"Expiry date: {expiry_date}")

        # Create assignment using ServicePackageAssignment model
        assignment = ServicePackageAssignment(
            customer_id=customer_id,
            package_type=package_type,
            package_reference_id=package_id,
            service_id=data.get('service_id'),  # Optional, for service packages
            expires_on=expiry_date,
            price_paid=price_paid,
            discount=discount,
            notes=data.get('notes', ''),
            status='active'
        )

        # Set package-specific fields
        if package_type == 'service_package' and hasattr(package_template, 'total_services'):
            assignment.total_sessions = package_template.total_services
            assignment.remaining_sessions = package_template.total_services
        elif package_type == 'prepaid' and hasattr(package_template, 'after_value'):
            assignment.credit_amount = package_template.after_value
            assignment.remaining_credit = package_template.after_value

        print("Creating assignment...")
        db.session.add(assignment)
        db.session.commit()
        print("Assignment created successfully")

        return jsonify({
            'success': True,
            'message': f'Package "{package_template.name}" assigned successfully to {customer.full_name}',
            'assignment_id': assignment.id
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error assigning package: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Failed to assign package: {str(e)}'}), 500

# Additional routes that don't fit in modules yet
# alerts route is now handled in dashboard module

@app.route('/test_navigation')

def test_navigation():
    """Navigation testing page"""
    return render_template('test_navigation.html')

@app.route('/unaki-booking')
@login_required
def unaki_booking():
    """Unaki Appointment Booking page"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('unaki_booking.html')

@app.route('/billing')
def billing():
    """Redirect to integrated billing"""
    return redirect(url_for('integrated_billing'))

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
@login_required
def role_management():
    """Role management page"""
    if not current_user.can_access('settings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('settings.html')

@app.route('/student-offers/add')
@login_required
def student_offers_add():
    """Add student offer page"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('packages/add_student_offer.html')


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
        if role.name == 'admin':
            return {'error': 'Cannot delete admin role'}, 400
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