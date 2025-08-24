
"""
Package management views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import Package, Service, Client, ClientPackage
from forms import PackageForm
from datetime import datetime, timedelta

@app.route('/packages')
@login_required
def packages():
    """Display packages page"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    packages = Package.query.filter_by(is_active=True).all()
    clients = Client.query.filter_by(is_active=True).all()
    services = Service.query.filter_by(is_active=True).all()
    
    package_form = PackageForm()
    
    return render_template('packages.html', 
                         packages=packages,
                         clients=clients,
                         services=services,
                         package_form=package_form)

@app.route('/add_package', methods=['POST'])
@login_required
def add_package():
    """Add new package"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('packages'))

    form = PackageForm()
    if form.validate_on_submit():
        try:
            package = Package(
                name=form.name.data,
                description=form.description.data,
                duration_months=form.duration_months.data,
                total_price=form.total_price.data,
                discount_percentage=form.discount_percentage.data,
                is_active=form.is_active.data
            )
            db.session.add(package)
            db.session.commit()
            flash('Package added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding package: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')

    return redirect(url_for('packages'))

@app.route('/edit_package/<int:package_id>', methods=['POST'])
@login_required
def edit_package(package_id):
    """Edit existing package"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('packages'))

    package = Package.query.get_or_404(package_id)
    
    try:
        package.name = request.form.get('name', package.name)
        package.description = request.form.get('description', package.description)
        package.duration_months = int(request.form.get('duration_months', package.duration_months))
        package.total_price = float(request.form.get('total_price', package.total_price))
        package.discount_percentage = float(request.form.get('discount_percentage', package.discount_percentage))
        package.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('Package updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating package: {str(e)}', 'danger')

    return redirect(url_for('packages'))

@app.route('/delete_package/<int:package_id>', methods=['POST'])
@login_required
def delete_package(package_id):
    """Delete package"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('packages'))

    try:
        package = Package.query.get_or_404(package_id)
        
        # Check if package is assigned to any clients
        client_packages = ClientPackage.query.filter_by(package_id=package_id, is_active=True).count()
        if client_packages > 0:
            flash(f'Cannot delete package - it is assigned to {client_packages} client(s)', 'warning')
        else:
            package.is_active = False  # Soft delete
            db.session.commit()
            flash('Package deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting package: {str(e)}', 'danger')

    return redirect(url_for('packages'))

@app.route('/assign_package', methods=['POST'])
@login_required
def assign_package():
    """Assign package to client"""
    if not current_user.can_access('packages'):
        return jsonify({'success': False, 'message': 'Access denied'})

    try:
        client_id = request.form.get('client_id')
        package_id = request.form.get('package_id')
        
        if not client_id or not package_id:
            return jsonify({'success': False, 'message': 'Client and package required'})

        package = Package.query.get(package_id)
        if not package:
            return jsonify({'success': False, 'message': 'Package not found'})

        # Calculate expiry date
        expiry_date = datetime.utcnow() + timedelta(days=package.duration_months * 30)

        client_package = ClientPackage(
            client_id=client_id,
            package_id=package_id,
            purchase_date=datetime.utcnow(),
            expiry_date=expiry_date,
            amount_paid=package.total_price,
            is_active=True
        )

        db.session.add(client_package)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Package assigned successfully!'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
