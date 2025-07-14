"""
Packages views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app
from forms import PackageForm
from .packages_queries import (
    get_all_packages, get_package_by_id, create_package, update_package,
    delete_package, get_client_packages, assign_package_to_client,
    get_package_services, add_service_to_package, get_available_services
)

@app.route('/packages')
@login_required
def packages():
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    packages_list = get_all_packages()
    services = get_available_services()
    
    form = PackageForm()
    
    return render_template('packages.html',
                         packages=packages_list,
                         services=services,
                         form=form)

@app.route('/packages/create', methods=['POST'])
@login_required
def create_package_route():
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = PackageForm()
    if form.validate_on_submit():
        package_data = {
            'name': form.name.data,
            'description': form.description.data or '',
            'price': form.price.data,
            'sessions_included': form.sessions_included.data,
            'validity_days': form.validity_days.data,
            'is_active': True
        }
        
        create_package(package_data)
        flash('Package created successfully!', 'success')
    else:
        flash('Error creating package. Please check your input.', 'danger')
    
    return redirect(url_for('packages'))

@app.route('/packages/update/<int:id>', methods=['POST'])
@login_required
def update_package_route(id):
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    package = get_package_by_id(id)
    if not package:
        flash('Package not found', 'danger')
        return redirect(url_for('packages'))
    
    form = PackageForm()
    if form.validate_on_submit():
        package_data = {
            'name': form.name.data,
            'description': form.description.data or '',
            'price': form.price.data,
            'sessions_included': form.sessions_included.data,
            'validity_days': form.validity_days.data
        }
        
        update_package(id, package_data)
        flash('Package updated successfully!', 'success')
    else:
        flash('Error updating package. Please check your input.', 'danger')
    
    return redirect(url_for('packages'))

@app.route('/packages/delete/<int:id>', methods=['POST'])
@login_required
def delete_package_route(id):
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    if delete_package(id):
        flash('Package deleted successfully!', 'success')
    else:
        flash('Error deleting package', 'danger')
    
    return redirect(url_for('packages'))

@app.route('/packages/assign/<int:package_id>/<int:client_id>', methods=['POST'])
@login_required
def assign_package_route(package_id, client_id):
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    client_package = assign_package_to_client(client_id, package_id)
    if client_package:
        flash('Package assigned to client successfully!', 'success')
    else:
        flash('Error assigning package', 'danger')
    
    return redirect(url_for('packages'))