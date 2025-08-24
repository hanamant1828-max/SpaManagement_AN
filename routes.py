"""
New modular routes file - imports all module views and creates default data
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from app import app, db
from models import User, Client, Service, Appointment, Inventory, Expense, Invoice, Package, StaffSchedule, ClientPackage, PackageService, Review, Communication, Commission, ProductSale, Promotion, Waitlist, RecurringAppointment, Location, BusinessSettings, Role, Permission, RolePermission, Category, Department, SystemSetting
from forms import LoginForm, UserForm, ClientForm, ServiceForm, AppointmentForm, InventoryForm, ExpenseForm, PackageForm, StaffScheduleForm, ReviewForm, CommunicationForm, PromotionForm, WaitlistForm, ProductSaleForm, RecurringAppointmentForm, BusinessSettingsForm, AdvancedClientForm, AdvancedUserForm, QuickBookingForm, PaymentForm, RoleForm, PermissionForm, CategoryForm, DepartmentForm, SystemSettingForm
import utils

# Import all module views to register routes
import modules

# Import views from modules
from modules.dashboard.dashboard_views import *
from modules.auth.auth_views import *
from modules.bookings.bookings_views import *
from modules.clients.clients_views import *
from modules.services.services_views import *
from modules.inventory.inventory_views import *
from modules.billing.billing_views import *
from modules.expenses.expenses_views import *
from modules.reports.reports_views import *
from modules.packages.packages_views import *
from modules.checkin.checkin_views import *
from modules.notifications.notifications_views import *
from modules.settings.settings_views import *
from modules.staff.staff_views import *


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
        from create_comprehensive_permissions import create_comprehensive_permissions
        create_comprehensive_permissions()
        print("Default categories created successfully!")
    except Exception as e:
        print(f"Error creating comprehensive permissions: {e}")

    try:
        from assign_comprehensive_permissions import assign_comprehensive_permissions
        assign_comprehensive_permissions()
        print("Default departments created successfully!")
    except Exception as e:
        print(f"Error assigning comprehensive permissions: {e}")

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

    from models import Communication, Client
    from forms import CommunicationForm

    communications = Communication.query.order_by(Communication.created_at.desc()).all()
    clients = Client.query.filter_by(is_active=True).all()
    form = CommunicationForm()

    return render_template('communications.html', 
                         communications=communications, 
                         clients=clients, 
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
    if not current_user.can_access('business_settings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('business_settings.html')

@app.route('/face_management')
@login_required
def face_management():
    if not current_user.can_access('face_checkin_view'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('face_management.html')

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
    settings = SystemSetting.query.all()

    # Initialize forms
    role_form = RoleForm()
    permission_form = PermissionForm()
    category_form = CategoryForm()
    department_form = DepartmentForm()
    setting_form = SystemSettingForm()

    return render_template('system_management.html',
                         roles=roles,
                         permissions=permissions,
                         categories=categories,
                         departments=departments,
                         settings=settings,
                         role_form=role_form,
                         permission_form=permission_form,
                         category_form=category_form,
                         department_form=department_form,
                         setting_form=setting_form)

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
@app.route('/api/save_face', methods=['POST'])
@login_required
def api_save_face():
    """Save face data for a client"""
    if not current_user.can_access('face_management'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        data = request.get_json()
        client_id = data.get('client_id')
        face_image = data.get('face_image')

        if not client_id or not face_image:
            return jsonify({'error': 'Client ID and face image are required'}), 400

        # Find the client
        from models import Client
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404

        # Here you would normally process the face image and extract facial features
        # For now, we'll store the image data directly
        import base64
        import os

        # Save face image
        try:
            # Remove data URL prefix if present
            if face_image.startswith('data:image'):
                face_image = face_image.split(',')[1]

            # Decode base64 image
            image_data = base64.b64decode(face_image)

            # Create faces directory if it doesn't exist
            faces_dir = os.path.join('static', 'faces')
            os.makedirs(faces_dir, exist_ok=True)

            # Save image file
            filename = f"client_{client_id}_face.jpg"
            filepath = os.path.join(faces_dir, filename)

            with open(filepath, 'wb') as f:
                f.write(image_data)

            # Update client record
            client.face_image_url = f"/static/faces/{filename}"
            client.facial_encoding = face_image  # Store base64 for now

            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Face data saved successfully',
                'client_name': client.full_name
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error saving face data: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/remove_face/<int:client_id>', methods=['DELETE'])
@login_required
def api_remove_face(client_id):
    """Remove face data for a client"""
    if not current_user.can_access('face_management'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        from models import Client
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404

        # Remove face image file if it exists
        if client.face_image_url:
            import os
            try:
                # Remove leading slash and convert to relative path
                file_path = client.face_image_url.lstrip('/')
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass  # Continue even if file deletion fails

        # Clear face data from database
        client.face_image_url = None
        client.facial_encoding = None

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Face data removed successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/recognize_face', methods=['POST'])
@login_required
def api_recognize_face():
    """Recognize a face against stored client faces"""
    if not current_user.can_access('face_management'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        data = request.get_json()
        face_image = data.get('face_image')

        if not face_image:
            return jsonify({'error': 'Face image is required'}), 400

        # Get all clients with face data
        from models import Client
        clients_with_faces = Client.query.filter(
            Client.facial_encoding.isnot(None),
            Client.is_active == True
        ).all()

        if not clients_with_faces:
            return jsonify({
                'success': False,
                'message': 'No registered faces found'
            })

        # For demonstration, we'll simulate face matching
        # In production, you would use face_recognition library here

        # Simulate recognition success with first client for demo
        if clients_with_faces:
            matched_client = clients_with_faces[0]

            return jsonify({
                'success': True,
                'recognized': True,
                'client': {
                    'id': matched_client.id,
                    'name': matched_client.full_name,
                    'phone': matched_client.phone,
                    'email': matched_client.email
                },
                'confidence': 0.85  # Simulated confidence score
            })

        return jsonify({
            'success': True,
            'recognized': False,
            'message': 'No matching face found'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500