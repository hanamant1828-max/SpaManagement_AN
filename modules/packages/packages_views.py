"""
Enhanced Package Management Views with proper service selection
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import Package, PackageService, Service, Category, Client, ClientPackage
from .packages_queries import *
import json
from datetime import datetime, timedelta

@app.route('/packages')
@login_required
def packages():
    """Enhanced Package Management with service selection"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    packages_list = get_all_packages()
    services = Service.query.filter_by(is_active=True).all()
    categories = Category.query.filter_by(category_type='service', is_active=True).all()
    client_packages = ClientPackage.query.filter_by(is_active=True).limit(10).all()
    clients = Client.query.filter_by(is_active=True).all()

    return render_template('enhanced_packages.html', 
                         packages=packages_list,
                         services=services,
                         categories=categories,
                         client_packages=client_packages,
                         clients=clients)

@app.route('/packages/create', methods=['POST'])
@login_required
def create_package():
    """Create a new package with selected services and configurations"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('packages'))

    try:
        # Handle form data
        name = request.form.get('name')
        description = request.form.get('description', '')
        package_type = request.form.get('package_type')
        validity_days = int(request.form.get('validity_days'))
        total_price = float(request.form.get('total_price'))
        discount_percentage = float(request.form.get('discount_percentage', 0))
        is_active = request.form.get('is_active') == 'on'

        # Extract services data from form
        services_data = []
        services_dict = {}

        # Group services data by index
        for key in request.form.keys():
            if key.startswith('services['):
                # Extract index and field name
                import re
                match = re.match(r'services\[(\d+)\]\[(\w+)\]', key)
                if match:
                    index = int(match.group(1))
                    field = match.group(2)
                    value = request.form[key]

                    if index not in services_dict:
                        services_dict[index] = {}
                    services_dict[index][field] = value

        # Convert to list format
        for index in sorted(services_dict.keys()):
            service_data = services_dict[index]
            services_data.append({
                'service_id': int(service_data['service_id']),
                'sessions': int(service_data['sessions']),
                'service_discount': float(service_data.get('service_discount', 0))
            })

        # Create the package
        package = create_package_with_services(
            name=name,
            description=description,
            package_type=package_type,
            validity_days=validity_days,
            total_price=total_price,
            discount_percentage=discount_percentage,
            is_active=is_active,
            services_data=services_data
        )

        if package:
            flash('Package created successfully!', 'success')
        else:
            flash('Failed to create package', 'danger')

    except Exception as e:
        flash(f'Error creating package: {str(e)}', 'danger')

    return redirect(url_for('packages'))

@app.route('/packages/<int:package_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_package(package_id):
    """Edit existing package"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('packages'))

    package = Package.query.get_or_404(package_id)

    if request.method == 'POST':
        try:
            # Update package details
            package.name = request.form.get('name', '').strip()
            package.description = request.form.get('description', '').strip()
            package.package_type = request.form.get('package_type', 'regular')
            package.validity_days = int(request.form.get('validity_days', 90))
            package.duration_months = package.validity_days // 30
            package.discount_percentage = float(request.form.get('discount_percentage', 0))

            # Update services
            selected_services = request.form.getlist('services[]')

            # Remove existing services
            PackageService.query.filter_by(package_id=package_id).delete()

            # Add new services
            total_original_price = 0
            total_sessions = 0

            for service_id in selected_services:
                service = Service.query.get(service_id)
                if service:
                    sessions = int(request.form.get(f'service_sessions_{service_id}', 1))
                    service_discount = float(request.form.get(f'service_discount_{service_id}', 0))

                    original_price = service.price * sessions
                    service_discount_amount = (original_price * service_discount) / 100
                    discounted_price = original_price - service_discount_amount

                    package_service = PackageService(
                        package_id=package_id,
                        service_id=int(service_id),
                        sessions_included=sessions,
                        service_discount=service_discount,
                        original_price=original_price,
                        discounted_price=discounted_price
                    )
                    db.session.add(package_service)

                    total_original_price += original_price
                    total_sessions += sessions

            # Recalculate package price
            total_discount_amount = (total_original_price * package.discount_percentage) / 100
            package.total_price = total_original_price - total_discount_amount
            package.total_sessions = total_sessions

            db.session.commit()
            flash(f'Package "{package.name}" updated successfully', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating package: {str(e)}', 'danger')

    services = Service.query.filter_by(is_active=True).all()
    categories = Category.query.filter_by(category_type='service', is_active=True).all()

    return render_template('enhanced_packages.html', 
                         package=package,
                         services=services,
                         categories=categories,
                         edit_mode=True)

@app.route('/packages/<int:package_id>/delete', methods=['POST'])
@login_required
def delete_package(package_id):
    """Delete package"""
    if not current_user.can_access('packages'):
        return jsonify({'success': False, 'message': 'Access denied'})

    try:
        package = Package.query.get_or_404(package_id)

        # Check if package is being used by clients
        client_packages = ClientPackage.query.filter_by(package_id=package_id, is_active=True).count()
        if client_packages > 0:
            return jsonify({
                'success': False, 
                'message': f'Cannot delete package. {client_packages} client(s) have active subscriptions.'
            })

        # Delete package services first
        PackageService.query.filter_by(package_id=package_id).delete()

        # Delete package
        db.session.delete(package)
        db.session.commit()

        return jsonify({
            'success': True, 
            'message': f'Package "{package.name}" deleted successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error deleting package: {str(e)}'})

@app.route('/api/services/<int:service_id>/details')
@login_required
def get_service_details(service_id):
    """Get service details for AJAX calls"""
    service = Service.query.get_or_404(service_id)
    return jsonify({
        'id': service.id,
        'name': service.name,
        'price': service.price,
        'duration': service.duration,
        'description': service.description
    })

@app.route('/api/packages/<int:package_id>/details')
@login_required
def get_package_details(package_id):
    """Get package details with services for editing"""
    package = Package.query.get_or_404(package_id)

    services = []
    for ps in package.services:
        services.append({
            'service_id': ps.service_id,
            'service_name': ps.service.name,
            'sessions_included': ps.sessions_included,
            'service_discount': ps.service_discount,
            'original_price': ps.original_price,
            'discounted_price': ps.discounted_price
        })

    return jsonify({
        'id': package.id,
        'name': package.name,
        'description': package.description,
        'package_type': package.package_type,
        'validity_days': package.validity_days,
        'total_price': package.total_price,
        'discount_percentage': package.discount_percentage,
        'services': services
    })

@app.route('/packages/<int:package_id>/toggle', methods=['POST'])
@login_required
def toggle_package(package_id):
    """Toggle package active status"""
    if not current_user.can_access('packages'):
        return jsonify({'success': False, 'message': 'Access denied'})

    try:
        package = Package.query.get_or_404(package_id)
        package.is_active = not package.is_active
        db.session.commit()

        status = 'activated' if package.is_active else 'deactivated'
        return jsonify({
            'success': True, 
            'message': f'Package {status} successfully',
            'is_active': package.is_active
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/packages/export')
@login_required
def export_packages():
    """Export packages to CSV"""
    from flask import make_response
    import csv
    from io import StringIO

    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('packages'))

    try:
        packages = get_all_packages()

        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Package Name', 'Description', 'Package Type', 'Total Sessions', 
            'Validity Days', 'Total Price', 'Discount %', 'Status'
        ])

        # Write package data
        for package in packages:
            writer.writerow([
                package.name,
                package.description or '',
                package.package_type,
                package.total_sessions,
                package.validity_days,
                package.total_price,
                package.discount_percentage,
                'Active' if package.is_active else 'Inactive'
            ])

        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=packages.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response

    except Exception as e:
        flash(f'Error exporting packages: {str(e)}', 'danger')
        return redirect(url_for('packages'))

@app.route('/packages/add', methods=['POST'])
@login_required
def add_package():
    """Alternative route name for package creation"""
    return create_package()

@app.route('/packages/<int:package_id>/delete', methods=['POST'])
@login_required
def delete_package_route(package_id):
    """Delete package route"""
    return delete_package(package_id)