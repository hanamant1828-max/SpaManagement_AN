"""
Staff views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import app
from forms import UserForm, AdvancedUserForm
from .staff_queries import (
    get_all_staff, get_staff_by_id, get_staff_by_role, get_active_roles, 
    get_active_departments, create_staff, update_staff, delete_staff, 
    get_staff_appointments, get_staff_commissions, get_staff_stats
)

@app.route('/staff')
@login_required
def staff():
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    staff_list = get_all_staff()
    roles = get_active_roles()
    departments = get_active_departments()
    
    form = UserForm()
    advanced_form = AdvancedUserForm()
    
    # Set up form choices
    form.role.choices = [(r.name, r.display_name) for r in roles]
    advanced_form.role_id.choices = [(r.id, r.display_name) for r in roles]
    advanced_form.department_id.choices = [(d.id, d.display_name) for d in departments]
    
    return render_template('staff.html', 
                         staff=staff_list,
                         form=form,
                         advanced_form=advanced_form,
                         roles=roles,
                         departments=departments)

@app.route('/staff/create', methods=['POST'])
@login_required
def create_staff_route():
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = UserForm()
    roles = get_active_roles()
    form.role.choices = [(r.name, r.display_name) for r in roles]
    
    if form.validate_on_submit():
        staff_data = {
            'username': form.username.data,
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'role': form.role.data,
            'commission_rate': form.commission_rate.data,
            'hourly_rate': form.hourly_rate.data,
            'password_hash': generate_password_hash(form.password.data),
            'is_active': True
        }
        
        create_staff(staff_data)
        flash('Staff member created successfully!', 'success')
    else:
        flash('Error creating staff member. Please check your input.', 'danger')
    
    return redirect(url_for('staff'))

@app.route('/staff/update/<int:id>', methods=['POST'])
@login_required
def update_staff_route(id):
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    staff_member = get_staff_by_id(id)
    if not staff_member:
        flash('Staff member not found', 'danger')
        return redirect(url_for('staff'))
    
    form = UserForm()
    roles = get_active_roles()
    form.role.choices = [(r.name, r.display_name) for r in roles]
    
    if form.validate_on_submit():
        staff_data = {
            'username': form.username.data,
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'role': form.role.data,
            'commission_rate': form.commission_rate.data,
            'hourly_rate': form.hourly_rate.data
        }
        
        # Only update password if provided
        if form.password.data:
            staff_data['password_hash'] = generate_password_hash(form.password.data)
        
        update_staff(id, staff_data)
        flash('Staff member updated successfully!', 'success')
    else:
        flash('Error updating staff member. Please check your input.', 'danger')
    
    return redirect(url_for('staff'))

@app.route('/staff/delete/<int:id>', methods=['POST'])
@login_required
def delete_staff_route(id):
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    if delete_staff(id):
        flash('Staff member deleted successfully!', 'success')
    else:
        flash('Error deleting staff member', 'danger')
    
    return redirect(url_for('staff'))

@app.route('/staff/<int:id>')
@login_required
def staff_detail(id):
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    staff_member = get_staff_by_id(id)
    if not staff_member:
        flash('Staff member not found', 'danger')
        return redirect(url_for('staff'))
    
    appointments = get_staff_appointments(id)
    commissions = get_staff_commissions(id)
    stats = get_staff_stats(id)
    
    return render_template('staff_detail.html',
                         staff_member=staff_member,
                         appointments=appointments,
                         commissions=commissions,
                         stats=stats)