
"""
Settings and Department Management Views
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import Department, User

# Department Management API Routes
@app.route('/api/departments', methods=['GET'])
@login_required
def api_get_departments():
    """Get all departments"""
    try:
        departments = Department.query.order_by(Department.name).all()
        return jsonify({
            'success': True,
            'departments': [{
                'id': dept.id,
                'name': dept.name,
                'display_name': dept.display_name,
                'description': dept.description,
                'is_active': dept.is_active,
                'created_at': dept.created_at.isoformat() if dept.created_at else None
            } for dept in departments]
        })
    except Exception as e:
        print(f"Error loading departments: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/departments/<int:department_id>', methods=['GET'])
@login_required
def api_get_department(department_id):
    """Get single department by ID"""
    try:
        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'success': False,
                'error': 'Department not found'
            }), 404
        
        return jsonify({
            'id': department.id,
            'name': department.name,
            'display_name': department.display_name,
            'description': department.description,
            'is_active': department.is_active,
            'created_at': department.created_at.isoformat() if department.created_at else None
        })
    except Exception as e:
        print(f"Error loading department {department_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/departments', methods=['POST'])
@login_required
def api_create_department():
    """Create new department"""
    try:
        if not current_user.can_access('settings'):
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        # Get form data
        name = request.form.get('name', '').strip()
        display_name = request.form.get('display_name', '').strip()
        description = request.form.get('description', '').strip()
        is_active = request.form.get('is_active') == 'on'
        
        # Validate required fields
        if not name or not display_name:
            return jsonify({
                'success': False,
                'message': 'Name and display name are required'
            }), 400
        
        # Check for duplicate name
        existing = Department.query.filter_by(name=name).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'Department with this name already exists'
            }), 400
        
        # Create department
        department = Department(
            name=name,
            display_name=display_name,
            description=description,
            is_active=is_active
        )
        
        db.session.add(department)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Department created successfully',
            'department_id': department.id
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error creating department: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/departments/<int:department_id>', methods=['PUT'])
@login_required
def api_update_department(department_id):
    """Update existing department"""
    try:
        if not current_user.can_access('settings'):
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'success': False,
                'message': 'Department not found'
            }), 404
        
        # Get form data
        name = request.form.get('name', '').strip()
        display_name = request.form.get('display_name', '').strip()
        description = request.form.get('description', '').strip()
        is_active = request.form.get('is_active') == 'on'
        
        # Validate required fields
        if not name or not display_name:
            return jsonify({
                'success': False,
                'message': 'Name and display name are required'
            }), 400
        
        # Check for duplicate name (excluding current department)
        existing = Department.query.filter(
            Department.name == name,
            Department.id != department_id
        ).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'Department with this name already exists'
            }), 400
        
        # Update department
        department.name = name
        department.display_name = display_name
        department.description = description
        department.is_active = is_active
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Department updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error updating department {department_id}: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/departments/<int:department_id>', methods=['DELETE'])
@login_required
def api_delete_department(department_id):
    """Delete department"""
    try:
        if not current_user.can_access('settings'):
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'success': False,
                'message': 'Department not found'
            }), 404
        
        # Check if department has staff members
        staff_count = User.query.filter_by(department_id=department_id).count()
        if staff_count > 0:
            return jsonify({
                'success': False,
                'message': f'Cannot delete department with {staff_count} staff member(s)'
            }), 400
        
        db.session.delete(department)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Department deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting department {department_id}: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/settings')
@login_required
def settings():
    """Settings page"""
    if not current_user.can_access('settings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('settings.html')

@app.route('/system_management')
@login_required
def system_management():
    """System management page"""
    if not current_user.can_access('settings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('system_management.html')

"""
Settings views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import SystemSetting, Department
from .settings_queries import get_all_settings, update_setting

# Import settings queries with error handling
try:
    from .settings_queries import (
        get_system_settings, get_setting_by_key, update_setting,
        get_business_settings, update_business_settings
    )
except ImportError as e:
    print(f"Warning: Settings queries import error: {e}")
    # Provide fallback functions
    def get_system_settings():
        return {}
    def get_setting_by_key(key):
        return None
    def update_setting(key, value):
        return True
    def get_business_settings():
        return {}
    def update_business_settings(data):
        return True

@app.route('/settings')
@login_required
def settings():
    if not current_user.can_access('settings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    system_settings = get_system_settings()
    business_settings = get_business_settings()

    business_form = BusinessSettingsForm()
    system_form = SystemSettingForm()

    # Fetch departments for table view
    try:
        departments = Department.query.filter_by(is_active=True).all()
    except Exception as e:
        flash(f"Error fetching departments: {e}", "danger")
        departments = []

    return render_template('settings.html',
                         system_settings=system_settings,
                         business_settings=business_settings,
                         business_form=business_form,
                         system_form=system_form,
                         departments=departments)


@app.route('/settings/business', methods=['POST'])
@login_required
def update_business_settings_route():
    if not current_user.can_access('settings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    form = BusinessSettingsForm()
    if form.validate_on_submit():
        settings_data = {
            'business_name': form.business_name.data,
            'business_phone': form.business_phone.data,
            'business_email': form.business_email.data,
            'business_address': form.business_address.data,
            'tax_rate': form.tax_rate.data,
            'currency': form.currency.data,
            'timezone': form.timezone.data
        }

        update_business_settings(settings_data)
        flash('Business settings updated successfully!', 'success')
    else:
        flash('Error updating business settings. Please check your input.', 'danger')

    return redirect(url_for('settings'))

@app.route('/settings/system', methods=['POST'])
@login_required
def update_system_setting_route():
    if not current_user.can_access('settings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    setting_key = request.form.get('key')
    setting_value = request.form.get('value')

    if setting_key and setting_value is not None:
        update_setting(setting_key, setting_value)
        flash('System setting updated successfully!', 'success')
    else:
        flash('Invalid setting data', 'danger')

    return redirect(url_for('settings'))

@app.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    if not current_user.has_permission('settings_edit'):
        flash('You do not have permission to update settings', 'danger')
        return redirect(url_for('settings'))

    try:
        for key in request.form.keys():
            if key != 'csrf_token':
                value = request.form.get(key)
                update_setting(key, value)

        flash('Settings updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating settings: {str(e)}', 'danger')

    return redirect(url_for('settings'))

# Department API endpoints
@app.route('/api/departments', methods=['GET'])
@login_required
def get_departments_api():
    """Get all departments"""
    try:
        departments = Department.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'departments': [{
                'id': dept.id,
                'name': dept.name,
                'display_name': dept.display_name,
                'description': dept.description,
                'is_active': dept.is_active
            } for dept in departments]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/departments/<int:department_id>', methods=['GET'])
@login_required
def get_department_api(department_id):
    """Get single department"""
    try:
        dept = Department.query.get_or_404(department_id)
        return jsonify({
            'id': dept.id,
            'name': dept.name,
            'display_name': dept.display_name,
            'description': dept.description,
            'is_active': dept.is_active
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/departments', methods=['POST'])
@login_required
def create_department_api():
    """Create new department"""
    try:
        name = request.form.get('name')
        display_name = request.form.get('display_name')
        description = request.form.get('description', '')
        is_active = request.form.get('is_active') == 'on'

        department = Department(
            name=name,
            display_name=display_name,
            description=description,
            is_active=is_active
        )

        db.session.add(department)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Department created successfully',
            'department': {
                'id': department.id,
                'name': department.name,
                'display_name': department.display_name
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/departments/<int:department_id>', methods=['PUT'])
@login_required
def update_department_api(department_id):
    """Update department"""
    try:
        dept = Department.query.get_or_404(department_id)

        dept.name = request.form.get('name', dept.name)
        dept.display_name = request.form.get('display_name', dept.display_name)
        dept.description = request.form.get('description', dept.description)
        dept.is_active = request.form.get('is_active') == 'on'

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Department updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/departments/<int:department_id>', methods=['DELETE'])
@login_required
def delete_department_api(department_id):
    """Delete department"""
    try:
        dept = Department.query.get_or_404(department_id)

        # Check if department has staff assigned
        from models import User
        staff_count = User.query.filter_by(department_id=department_id).count()

        if staff_count > 0:
            return jsonify({
                'success': False,
                'message': f'Cannot delete department with {staff_count} staff members assigned'
            }), 400

        db.session.delete(dept)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Department deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500