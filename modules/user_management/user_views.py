"""
Admin User Management Views and Routes
Provides comprehensive CRUD operations for managing system users
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import app, db
from models import User, Role, Department
from forms import AdminUserForm
from datetime import datetime
from werkzeug.security import generate_password_hash

@app.route('/admin/users')
@login_required
def admin_users():
    """Admin user management interface"""
    if not current_user.can_access('settings'):
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get filter parameters
    role_filter = request.args.get('role')
    department_filter = request.args.get('department')
    status_filter = request.args.get('status')
    search_query = request.args.get('search', '').strip()
    
    # Base query
    query = User.query
    
    # Apply search filter
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            or_(
                User.username.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
    
    # Apply role filter
    if role_filter and role_filter != 'all':
        query = query.filter(User.role_id == int(role_filter))
    
    # Apply department filter
    if department_filter and department_filter != 'all':
        query = query.filter(User.department_id == int(department_filter))
    
    # Apply status filter
    if status_filter:
        if status_filter == 'active':
            query = query.filter(User.is_active == True)
        elif status_filter == 'inactive':
            query = query.filter(User.is_active == False)
    
    # Get users with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get filter options
    roles = Role.query.filter_by(is_active=True).all()
    departments = Department.query.filter_by(is_active=True).all()
    
    return render_template('admin/user_management.html', 
                         users=users,
                         roles=roles,
                         departments=departments,
                         current_filters={
                             'role': role_filter,
                             'department': department_filter,
                             'status': status_filter,
                             'search': search_query
                         })

@app.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
def admin_create_user():
    """Create new user"""
    if not current_user.can_access('settings'):
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = AdminUserForm()
    
    # Populate form choices
    roles = Role.query.filter_by(is_active=True).all()
    departments = Department.query.filter_by(is_active=True).all()
    
    form.role_id.choices = [(0, 'Select Role')] + [(r.id, r.display_name) for r in roles]
    form.department_id.choices = [(0, 'Select Department')] + [(d.id, d.display_name) for d in departments]
    
    if form.validate_on_submit():
        try:
            # Check for existing username
            if User.query.filter_by(username=form.username.data).first():
                flash('Username already exists. Please choose a different username.', 'danger')
                return render_template('admin/user_form.html', form=form, action='Create')
            
            # Check for existing email
            if form.email.data and User.query.filter_by(email=form.email.data).first():
                flash('Email already exists. Please use a different email address.', 'danger')
                return render_template('admin/user_form.html', form=form, action='Create')
            
            # Create new user
            user = User(
                username=form.username.data.lower().strip(),
                email=form.email.data.lower().strip() if form.email.data else None,
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                phone=form.phone.data.strip() if form.phone.data else None,
                role_id=form.role_id.data if form.role_id.data != 0 else None,
                department_id=form.department_id.data if form.department_id.data != 0 else None,
                designation=form.designation.data.strip() if form.designation.data else None,
                is_active=form.is_active.data,
                role='staff',  # Default fallback role
                created_at=datetime.utcnow()
            )
            
            # Set password if provided
            if form.password.data:
                user.password_hash = generate_password_hash(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'User {user.username} created successfully!', 'success')
            return redirect(url_for('admin_users'))
            
        except Exception as e:
            db.session.rollback()
            flash('Failed to create user. Please try again.', 'danger')
            print(f"User creation error: {e}")
    
    return render_template('admin/user_form.html', form=form, action='Create')

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    """Edit existing user"""
    if not current_user.can_access('settings'):
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    form = AdminUserForm(obj=user)
    
    # Populate form choices
    roles = Role.query.filter_by(is_active=True).all()
    departments = Department.query.filter_by(is_active=True).all()
    
    form.role_id.choices = [(0, 'Select Role')] + [(r.id, r.display_name) for r in roles]
    form.department_id.choices = [(0, 'Select Department')] + [(d.id, d.display_name) for d in departments]
    
    # Set current values
    form.role_id.data = user.role_id or 0
    form.department_id.data = user.department_id or 0
    
    if form.validate_on_submit():
        try:
            # Check for existing username (excluding current user)
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user and existing_user.id != user_id:
                flash('Username already exists. Please choose a different username.', 'danger')
                return render_template('admin/user_form.html', form=form, action='Edit', user=user)
            
            # Check for existing email (excluding current user)
            if form.email.data:
                existing_email = User.query.filter_by(email=form.email.data).first()
                if existing_email and existing_email.id != user_id:
                    flash('Email already exists. Please use a different email address.', 'danger')
                    return render_template('admin/user_form.html', form=form, action='Edit', user=user)
            
            # Update user
            user.username = form.username.data.lower().strip()
            user.email = form.email.data.lower().strip() if form.email.data else None
            user.first_name = form.first_name.data.strip()
            user.last_name = form.last_name.data.strip()
            user.phone = form.phone.data.strip() if form.phone.data else None
            user.role_id = form.role_id.data if form.role_id.data != 0 else None
            user.department_id = form.department_id.data if form.department_id.data != 0 else None
            user.designation = form.designation.data.strip() if form.designation.data else None
            user.is_active = form.is_active.data
            
            # Update password if provided
            if form.password.data:
                user.password_hash = generate_password_hash(form.password.data)
            
            db.session.commit()
            
            flash(f'User {user.username} updated successfully!', 'success')
            return redirect(url_for('admin_users'))
            
        except Exception as e:
            db.session.rollback()
            flash('Failed to update user. Please try again.', 'danger')
            print(f"User update error: {e}")
    
    return render_template('admin/user_form.html', form=form, action='Edit', user=user)

@app.route('/admin/users/view/<int:user_id>')
@login_required
def admin_view_user(user_id):
    """View user details"""
    if not current_user.can_access('settings'):
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Get user statistics
    stats = {
        'total_appointments': len(user.appointments) if hasattr(user, 'appointments') and user.appointments else 0,
        'active_appointments': len([a for a in user.appointments if a.status == 'scheduled']) if hasattr(user, 'appointments') and user.appointments else 0,
        'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never',
        'member_since': user.created_at.strftime('%Y-%m-%d') if user.created_at else 'Unknown'
    }
    
    return render_template('admin/user_view.html', user=user, stats=stats)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    """Soft delete user (deactivate)"""
    if not current_user.can_access('settings'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent self-deletion
        if user.id == current_user.id:
            return jsonify({'error': 'You cannot delete your own account'}), 400
        
        # Soft delete (deactivate)
        user.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User {user.username} has been deactivated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user'}), 500

@app.route('/admin/users/activate/<int:user_id>', methods=['POST'])
@login_required
def admin_activate_user(user_id):
    """Activate user"""
    if not current_user.can_access('settings'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        user.is_active = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User {user.username} has been activated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to activate user'}), 500

@app.route('/api/admin/users', methods=['GET'])
@login_required
def api_admin_users():
    """API endpoint for user data (for DataTables, etc.)"""
    if not current_user.can_access('settings'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        users = User.query.all()
        users_data = []
        
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'name': f"{user.first_name} {user.last_name}",
                'email': user.email or '',
                'role': user.dynamic_role.display_name if user.role_id and user.dynamic_role else user.role,
                'department': user.staff_department.display_name if user.department_id and user.staff_department else '',
                'is_active': user.is_active,
                'created_at': user.created_at.strftime('%Y-%m-%d') if user.created_at else '',
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never'
            })
        
        return jsonify({'data': users_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/users/bulk-action', methods=['POST'])
@login_required
def admin_bulk_user_action():
    """Handle bulk actions on users"""
    if not current_user.can_access('settings'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        user_ids = data.get('user_ids', [])
        action = data.get('action')
        
        if not user_ids or not action:
            return jsonify({'error': 'Missing user IDs or action'}), 400
        
        users = User.query.filter(User.id.in_(user_ids)).all()
        
        if action == 'activate':
            for user in users:
                user.is_active = True
            db.session.commit()
            return jsonify({'success': True, 'message': f'{len(users)} users activated'})
            
        elif action == 'deactivate':
            # Prevent self-deactivation
            if current_user.id in user_ids:
                return jsonify({'error': 'You cannot deactivate your own account'}), 400
            
            for user in users:
                user.is_active = False
            db.session.commit()
            return jsonify({'success': True, 'message': f'{len(users)} users deactivated'})
        
        else:
            return jsonify({'error': 'Invalid action'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500