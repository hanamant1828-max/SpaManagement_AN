from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import User, Role, Permission, RolePermission, Department
from werkzeug.security import generate_password_hash
from datetime import datetime
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        
        if (current_user.has_role('admin') or 
            current_user.has_role('super_admin') or 
            current_user.role == 'admin'):
            return f(*args, **kwargs)
        
        if current_user.role_id:
            try:
                user_role = Role.query.get(current_user.role_id)
                if user_role:
                    for role_perm in user_role.permissions:
                        if role_perm.permission.name == 'user_management_access':
                            return f(*args, **kwargs)
            except:
                pass
        
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    return decorated_function

@app.route('/user-management')
@login_required
@admin_required
def user_management_dashboard():
    users = User.query.all()
    roles = Role.query.all()
    permissions = Permission.query.all()
    departments = Department.query.all()
    
    stats = {
        'total_users': len(users),
        'active_users': len([u for u in users if u.is_active]),
        'total_roles': len(roles),
        'total_permissions': len(permissions)
    }
    
    return render_template('user_management/dashboard.html',
                         users=users,
                         roles=roles,
                         permissions=permissions,
                         departments=departments,
                         stats=stats)

@app.route('/user-management/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    roles = Role.query.filter_by(is_active=True).all()
    departments = Department.query.filter_by(is_active=True).all()
    return render_template('user_management/users.html',
                         users=users,
                         roles=roles,
                         departments=departments)

@app.route('/user-management/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            role_id = request.form.get('role_id')
            role = request.form.get('role', 'staff')
            phone = request.form.get('phone')
            department_id = request.form.get('department_id')
            employee_id = request.form.get('employee_id')
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'danger')
                return redirect(url_for('create_user'))
            
            user = User(
                username=username,
                email=email or None,
                first_name=first_name,
                last_name=last_name,
                role_id=int(role_id) if role_id else None,
                role=role,
                phone=phone,
                department_id=int(department_id) if department_id else None,
                employee_id=employee_id,
                is_active=True,
                created_at=datetime.utcnow()
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'User {username} created successfully!', 'success')
            return redirect(url_for('manage_users'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'danger')
            return redirect(url_for('create_user'))
    
    roles = Role.query.filter_by(is_active=True).all()
    departments = Department.query.filter_by(is_active=True).all()
    return render_template('user_management/create_user.html',
                         roles=roles,
                         departments=departments)

@app.route('/user-management/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            user.username = request.form.get('username')
            user.email = request.form.get('email') or None
            user.first_name = request.form.get('first_name')
            user.last_name = request.form.get('last_name')
            user.phone = request.form.get('phone')
            user.employee_id = request.form.get('employee_id')
            
            role_id = request.form.get('role_id')
            user.role_id = int(role_id) if role_id else None
            user.role = request.form.get('role', 'staff')
            
            department_id = request.form.get('department_id')
            user.department_id = int(department_id) if department_id else None
            
            user.is_active = request.form.get('is_active') == 'on'
            
            password = request.form.get('password')
            if password:
                user.set_password(password)
            
            db.session.commit()
            flash(f'User {user.username} updated successfully!', 'success')
            return redirect(url_for('manage_users'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'danger')
    
    roles = Role.query.filter_by(is_active=True).all()
    departments = Department.query.filter_by(is_active=True).all()
    return render_template('user_management/edit_user.html',
                         user=user,
                         roles=roles,
                         departments=departments)

@app.route('/user-management/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        if user.id == current_user.id:
            flash('Cannot delete your own account', 'danger')
            return redirect(url_for('manage_users'))
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        flash(f'User {username} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
    
    return redirect(url_for('manage_users'))

@app.route('/user-management/roles')
@login_required
@admin_required
def manage_roles():
    roles = Role.query.all()
    permissions = Permission.query.filter_by(is_active=True).all()
    
    permissions_by_module = {}
    for perm in permissions:
        if perm.module not in permissions_by_module:
            permissions_by_module[perm.module] = []
        permissions_by_module[perm.module].append(perm)
    
    return render_template('user_management/roles.html',
                         roles=roles,
                         permissions=permissions,
                         permissions_by_module=permissions_by_module)

@app.route('/user-management/roles/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_role():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            display_name = request.form.get('display_name')
            description = request.form.get('description')
            permission_ids = request.form.getlist('permissions')
            
            if Role.query.filter_by(name=name).first():
                flash('Role name already exists', 'danger')
                return redirect(url_for('create_role'))
            
            role = Role(
                name=name,
                display_name=display_name,
                description=description,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(role)
            db.session.flush()
            
            for perm_id in permission_ids:
                role_perm = RolePermission(
                    role_id=role.id,
                    permission_id=int(perm_id)
                )
                db.session.add(role_perm)
            
            db.session.commit()
            flash(f'Role {display_name} created successfully!', 'success')
            return redirect(url_for('manage_roles'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating role: {str(e)}', 'danger')
    
    permissions = Permission.query.filter_by(is_active=True).all()
    permissions_by_module = {}
    for perm in permissions:
        if perm.module not in permissions_by_module:
            permissions_by_module[perm.module] = []
        permissions_by_module[perm.module].append(perm)
    
    return render_template('user_management/create_role.html',
                         permissions_by_module=permissions_by_module)

@app.route('/user-management/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_role(role_id):
    role = Role.query.get_or_404(role_id)
    
    if request.method == 'POST':
        try:
            role.name = request.form.get('name')
            role.display_name = request.form.get('display_name')
            role.description = request.form.get('description')
            role.is_active = request.form.get('is_active') == 'on'
            
            permission_ids = request.form.getlist('permissions')
            
            RolePermission.query.filter_by(role_id=role.id).delete()
            
            for perm_id in permission_ids:
                role_perm = RolePermission(
                    role_id=role.id,
                    permission_id=int(perm_id)
                )
                db.session.add(role_perm)
            
            db.session.commit()
            flash(f'Role {role.display_name} updated successfully!', 'success')
            return redirect(url_for('manage_roles'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating role: {str(e)}', 'danger')
    
    permissions = Permission.query.filter_by(is_active=True).all()
    permissions_by_module = {}
    for perm in permissions:
        if perm.module not in permissions_by_module:
            permissions_by_module[perm.module] = []
        permissions_by_module[perm.module].append(perm)
    
    role_permission_ids = [rp.permission_id for rp in role.permissions]
    
    return render_template('user_management/edit_role.html',
                         role=role,
                         permissions_by_module=permissions_by_module,
                         role_permission_ids=role_permission_ids)

@app.route('/user-management/roles/<int:role_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_role(role_id):
    try:
        role = Role.query.get_or_404(role_id)
        
        users_count = User.query.filter_by(role_id=role_id).count()
        if users_count > 0:
            flash(f'Cannot delete role. {users_count} users are assigned to this role.', 'danger')
            return redirect(url_for('manage_roles'))
        
        role_name = role.display_name
        db.session.delete(role)
        db.session.commit()
        
        flash(f'Role {role_name} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting role: {str(e)}', 'danger')
    
    return redirect(url_for('manage_roles'))

@app.route('/user-management/permissions')
@login_required
@admin_required
def manage_permissions():
    permissions = Permission.query.all()
    permissions_by_module = {}
    for perm in permissions:
        if perm.module not in permissions_by_module:
            permissions_by_module[perm.module] = []
        permissions_by_module[perm.module].append(perm)
    
    return render_template('user_management/permissions.html',
                         permissions=permissions,
                         permissions_by_module=permissions_by_module)

@app.route('/user-management/permissions/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_permission():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            display_name = request.form.get('display_name')
            description = request.form.get('description')
            module = request.form.get('module')
            
            if Permission.query.filter_by(name=name).first():
                flash('Permission name already exists', 'danger')
                return redirect(url_for('create_permission'))
            
            permission = Permission(
                name=name,
                display_name=display_name,
                description=description,
                module=module,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(permission)
            db.session.commit()
            
            flash(f'Permission {display_name} created successfully!', 'success')
            return redirect(url_for('manage_permissions'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating permission: {str(e)}', 'danger')
    
    modules = ['dashboard', 'clients', 'staff', 'services', 'packages', 
               'appointments', 'billing', 'reports', 'expenses', 'inventory', 'settings']
    return render_template('user_management/create_permission.html', modules=modules)

@app.route('/user-management/access-control')
@login_required
@admin_required
def access_control():
    users = User.query.filter_by(is_active=True).all()
    roles = Role.query.filter_by(is_active=True).all()
    permissions = Permission.query.filter_by(is_active=True).all()
    
    permissions_by_module = {}
    for perm in permissions:
        if perm.module not in permissions_by_module:
            permissions_by_module[perm.module] = []
        permissions_by_module[perm.module].append(perm)
    
    return render_template('user_management/access_control.html',
                         users=users,
                         roles=roles,
                         permissions_by_module=permissions_by_module)
