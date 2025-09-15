"""
Professional Unified Package Management System
Handles all package types: Regular, Prepaid Credit, Prepaid Service, Memberships, Student Offers, etc.
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from app import app, db
from .packages_queries import *
import json
import csv
import io
from datetime import datetime, timedelta

# Import models
from models import Package, Service, Category, Customer, CustomerPackage, PackageService

@app.route('/packages')
@login_required
def packages():
    """Unified Professional Package Management System"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get all packages and data
    packages_list = Package.query.filter_by(is_active=True).order_by(Package.package_type, Package.name).all()
    services = Service.query.filter_by(is_active=True).all()
    categories = Category.query.filter_by(category_type='service', is_active=True).all()
    client_packages = CustomerPackage.query.filter_by(is_active=True).limit(10).all()
    clients = Customer.query.filter_by(is_active=True).all()

    # Get package statistics by type
    stats = {
        'total_packages': len(packages_list),
        'active_packages': len([p for p in packages_list if p.is_active]),
        'client_assignments': len(client_packages),
        'available_services': len(services),
        'regular_packages': len([p for p in packages_list if p.package_type == 'regular']),
        'prepaid_credit_packages': len([p for p in packages_list if p.package_type == 'prepaid_credit']),
        'prepaid_service_packages': len([p for p in packages_list if p.package_type == 'prepaid_service']),
        'membership_packages': len([p for p in packages_list if p.package_type == 'membership']),
        'student_offers': len([p for p in packages_list if p.package_type == 'student_offer']),
        'kitty_party_packages': len([p for p in packages_list if p.package_type == 'kitty_party'])
    }

    return render_template('professional_packages.html', 
                         packages=packages_list,
                         services=services,
                         categories=categories,
                         client_packages=client_packages,
                         clients=clients,
                         stats=stats)

@app.route('/packages/create', methods=['POST'])
@login_required
def create_package():
    """Create any type of package with unified form handling"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('packages'))

    try:
        # Basic package information
        name = request.form.get('name')
        description = request.form.get('description', '')
        package_type = request.form.get('package_type')
        validity_days = int(request.form.get('validity_days'))
        total_price = float(request.form.get('total_price', 0))
        discount_percentage = float(request.form.get('discount_percentage', 0))
        is_active = request.form.get('is_active') == 'on'

        # Prepaid Credit Package Fields
        prepaid_amount = float(request.form.get('prepaid_amount', 0))
        credit_amount = float(request.form.get('credit_amount', 0))
        bonus_percentage = float(request.form.get('bonus_percentage', 0))

        # Prepaid Service Package Fields
        paid_sessions = int(request.form.get('paid_sessions', 0))
        free_sessions = int(request.form.get('free_sessions', 0))

        # Membership Fields
        min_guests = int(request.form.get('min_guests', 1))
        student_discount = float(request.form.get('student_discount', 0))
        membership_benefits = request.form.get('membership_benefits', '')

        # Unlimited and date range fields
        has_unlimited_sessions = request.form.get('has_unlimited_sessions') == 'on'
        start_date = None
        end_date = None

        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Calculate derived values
        duration_months = max(1, validity_days // 30)

        if package_type == 'prepaid_credit':
            # For credit packages, calculate bonus
            bonus_amount = (prepaid_amount * bonus_percentage) / 100
            credit_amount = prepaid_amount + bonus_amount
            total_sessions = 0  # Credit-based, not session-based
        elif package_type == 'prepaid_service':
            # For service packages, calculate total sessions
            total_sessions = paid_sessions + free_sessions
            bonus_amount = 0
        else:
            # Regular packages
            bonus_amount = 0
            total_sessions = int(request.form.get('total_sessions', 1))

        # Extract services data
        services_data = []
        services_dict = {}

        # Group services data by index
        for key in request.form.keys():
            if key.startswith('services['):
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
            if 'service_id' in service_data:
                is_unlimited = service_data.get('unlimited') == 'on'
                sessions = 999 if is_unlimited else int(service_data.get('sessions', 1))

                services_data.append({
                    'service_id': int(service_data['service_id']),
                    'sessions': sessions,
                    'service_discount': float(service_data.get('service_discount', 0)),
                    'is_unlimited': is_unlimited
                })

        # Create the package
        package = Package(
            name=name,
            description=description,
            package_type=package_type,
            validity_days=validity_days,
            duration_months=duration_months,
            total_sessions=total_sessions,
            total_price=total_price,
            discount_percentage=discount_percentage,
            is_active=is_active,

            # Prepaid credit fields
            prepaid_amount=prepaid_amount,
            credit_amount=credit_amount,
            bonus_percentage=bonus_percentage,
            bonus_amount=bonus_amount,

            # Prepaid service fields
            paid_sessions=paid_sessions,
            free_sessions=free_sessions,

            # Membership fields
            min_guests=min_guests,
            student_discount=student_discount,
            membership_benefits=membership_benefits,

            # Advanced fields
            has_unlimited_sessions=has_unlimited_sessions,
            start_date=start_date,
            end_date=end_date
        )

        db.session.add(package)
        db.session.flush()  # Get package ID

        # Add package services
        total_original_price = 0
        for service_data in services_data:
            service = Service.query.get(service_data['service_id'])
            if service:
                sessions = service_data['sessions']
                service_discount = service_data['service_discount']
                is_unlimited = service_data['is_unlimited']

                original_price = service.price * sessions if not is_unlimited else 0
                service_discount_amount = (original_price * service_discount) / 100
                discounted_price = original_price - service_discount_amount

                package_service = PackageService(
                    package_id=package.id,
                    service_id=service.id,
                    sessions_included=sessions,
                    service_discount=service_discount,
                    original_price=original_price,
                    discounted_price=discounted_price,
                    is_unlimited=is_unlimited
                )
                db.session.add(package_service)
                total_original_price += original_price

        # Update package total sessions if not set
        if package_type not in ['prepaid_credit'] and total_sessions == 0:
            package.total_sessions = sum([s['sessions'] for s in services_data if not s.get('is_unlimited')])

        db.session.commit()
        flash(f'Package "{name}" created successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error creating package: {str(e)}', 'danger')

    return redirect(url_for('packages'))

@app.route('/packages/create-quick-templates', methods=['POST'])
@login_required
def create_quick_templates():
    """Create standard package templates for all types"""
    if not current_user.can_access('packages'):
        return jsonify({'success': False, 'message': 'Access denied'})

    try:
        template_type = request.form.get('template_type')

        if template_type == 'prepaid_credit':
            # Standard prepaid credit packages
            packages_data = [
                {'name': 'Prepaid ₹15,000', 'pay': 15000, 'get': 17500, 'bonus': 15, 'validity': 60},
                {'name': 'Prepaid ₹20,000', 'pay': 20000, 'get': 25000, 'bonus': 20, 'validity': 90},
                {'name': 'Prepaid ₹30,000', 'pay': 30000, 'get': 40000, 'bonus': 25, 'validity': 120},
                {'name': 'Prepaid ₹50,000', 'pay': 50000, 'get': 70000, 'bonus': 30, 'validity': 180},
                {'name': 'Prepaid ₹1,00,000', 'pay': 100000, 'get': 150000, 'bonus': 35, 'validity': 365}
            ]

            for pkg_data in packages_data:
                existing = Package.query.filter_by(name=pkg_data['name']).first()
                if not existing:
                    package = Package(
                        name=pkg_data['name'],
                        description=f"Pay ₹{pkg_data['pay']:,} and get ₹{pkg_data['get']:,} credit ({pkg_data['bonus']}% bonus)",
                        package_type='prepaid_credit',
                        validity_days=pkg_data['validity'],
                        prepaid_amount=pkg_data['pay'],
                        credit_amount=pkg_data['get'],
                        bonus_percentage=pkg_data['bonus'],
                        bonus_amount=pkg_data['get'] - pkg_data['pay'],
                        total_price=pkg_data['pay'],
                        total_sessions=0,
                        is_active=True
                    )
                    db.session.add(package)

        elif template_type == 'prepaid_service':
            # Standard service packages
            packages_data = [
                {'name': 'Pay for 3 Get 4', 'paid': 3, 'free': 1, 'total': 4, 'bonus': 25},
                {'name': 'Pay for 6 Get 9', 'paid': 6, 'free': 3, 'total': 9, 'bonus': 33},
                {'name': 'Pay for 9 Get 15', 'paid': 9, 'free': 6, 'total': 15, 'bonus': 40}
            ]

            for pkg_data in packages_data:
                existing = Package.query.filter_by(name=pkg_data['name']).first()
                if not existing:
                    package = Package(
                        name=pkg_data['name'],
                        description=f"Pay for {pkg_data['paid']} sessions, get {pkg_data['total']} total ({pkg_data['bonus']}% benefit)",
                        package_type='prepaid_service',
                        validity_days=90,
                        paid_sessions=pkg_data['paid'],
                        free_sessions=pkg_data['free'],
                        total_sessions=pkg_data['total'],
                        bonus_percentage=pkg_data['bonus'],
                        total_price=0,
                        is_active=True
                    )
                    db.session.add(package)

        elif template_type == 'membership':
            # Standard membership packages
            packages_data = [
                {'name': 'Silver Membership', 'months': 6, 'discount': 10, 'price': 5000},
                {'name': 'Gold Membership', 'months': 12, 'discount': 15, 'price': 8000},
                {'name': 'Platinum Membership', 'months': 12, 'discount': 20, 'price': 12000}
            ]

            for pkg_data in packages_data:
                existing = Package.query.filter_by(name=pkg_data['name']).first()
                if not existing:
                    package = Package(
                        name=pkg_data['name'],
                        description=f"{pkg_data['months']} months membership with {pkg_data['discount']}% discount on all services",
                        package_type='membership',
                        validity_days=pkg_data['months'] * 30,
                        duration_months=pkg_data['months'],
                        total_price=pkg_data['price'],
                        discount_percentage=pkg_data['discount'],
                        total_sessions=0,
                        is_active=True
                    )
                    db.session.add(package)

        db.session.commit()
        return jsonify({'success': True, 'message': f'Standard {template_type} packages created successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error creating packages: {str(e)}'})

@app.route('/packages/<int:package_id>/assign', methods=['POST'])
@login_required
def assign_package(package_id):
    """Assign any type of package to customer"""
    if not current_user.can_access('packages'):
        return jsonify({'success': False, 'message': 'Access denied'})

    try:
        package = Package.query.get_or_404(package_id)
        customer_id = request.form.get('customer_id')
        custom_amount = request.form.get('custom_amount')

        customer = Customer.query.get_or_404(customer_id)

        # Calculate expiry date
        expiry_date = datetime.utcnow() + timedelta(days=package.validity_days)

        # Determine amount and credit based on package type
        if package.package_type == 'prepaid_credit':
            amount_paid = float(custom_amount) if custom_amount else package.prepaid_amount
            if custom_amount:
                # Recalculate credit for custom amount
                custom_bonus = amount_paid * (package.bonus_percentage / 100)
                credit_balance = amount_paid + custom_bonus
            else:
                credit_balance = package.credit_amount
        else:
            amount_paid = float(custom_amount) if custom_amount else package.total_price
            credit_balance = 0

        # Create customer package
        customer_package = CustomerPackage(
            client_id=customer_id,
            package_id=package_id,
            purchase_date=datetime.utcnow(),
            expiry_date=expiry_date,
            amount_paid=amount_paid,
            sessions_used=0,
            total_sessions=package.total_sessions,
            is_active=True
        )

        db.session.add(customer_package)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Package "{package.name}" assigned to {customer.full_name}',
            'package_type': package.package_type,
            'credit_balance': credit_balance if package.package_type == 'prepaid_credit' else None
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error assigning package: {str(e)}'})

# Keep all existing routes from the original packages_views.py
@app.route('/packages/<int:package_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_package(package_id):
    """Edit existing package - handles all package types"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('packages'))

    package = Package.query.get_or_404(package_id)

    if request.method == 'POST':
        try:
            # Update package details based on type
            package.name = request.form.get('name', '').strip()
            package.description = request.form.get('description', '').strip()
            package.package_type = request.form.get('package_type', 'regular')
            package.validity_days = int(request.form.get('validity_days', 90))
            package.duration_months = max(1, package.validity_days // 30)
            package.discount_percentage = float(request.form.get('discount_percentage', 0))
            package.is_active = request.form.get('is_active') == 'on'

            # Update type-specific fields
            if package.package_type == 'prepaid_credit':
                package.prepaid_amount = float(request.form.get('prepaid_amount', 0))
                package.bonus_percentage = float(request.form.get('bonus_percentage', 0))
                package.bonus_amount = (package.prepaid_amount * package.bonus_percentage) / 100
                package.credit_amount = package.prepaid_amount + package.bonus_amount
            elif package.package_type == 'prepaid_service':
                package.paid_sessions = int(request.form.get('paid_sessions', 0))
                package.free_sessions = int(request.form.get('free_sessions', 0))
                package.total_sessions = package.paid_sessions + package.free_sessions
            elif package.package_type == 'membership':
                package.min_guests = int(request.form.get('min_guests', 1))
                package.student_discount = float(request.form.get('student_discount', 0))
                package.membership_benefits = request.form.get('membership_benefits', '')

            package.total_price = float(request.form.get('total_price', package.total_price))

            # Handle services update
            selected_services_json = request.form.get('selected_services')
            if selected_services_json:
                try:
                    import json
                    services_data = json.loads(selected_services_json)
                    
                    # Remove existing package services
                    PackageService.query.filter_by(package_id=package_id).delete()
                    
                    # Add updated services
                    total_sessions = 0
                    for service_data in services_data:
                        service = Service.query.get(service_data['service_id'])
                        if service:
                            sessions = service_data['sessions']
                            service_discount = service_data['discount']
                            
                            original_price = service.price * sessions
                            service_discount_amount = (original_price * service_discount) / 100
                            discounted_price = original_price - service_discount_amount
                            
                            package_service = PackageService(
                                package_id=package_id,
                                service_id=service.id,
                                sessions_included=sessions,
                                service_discount=service_discount,
                                original_price=original_price,
                                discounted_price=discounted_price
                            )
                            db.session.add(package_service)
                            total_sessions += sessions
                    
                    # Update total sessions if not prepaid credit
                    if package.package_type != 'prepaid_credit':
                        package.total_sessions = total_sessions
                        
                except json.JSONDecodeError:
                    flash('Invalid services data format', 'warning')

            db.session.commit()
            flash(f'Package "{package.name}" updated successfully', 'success')
            return redirect(url_for('packages'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating package: {str(e)}', 'danger')

    return redirect(url_for('packages'))

# Keep all other existing routes...
@app.route('/packages/<int:package_id>/delete', methods=['POST'])
@login_required
def delete_package(package_id):
    """Delete package"""
    if not current_user.can_access('packages'):
        return jsonify({'success': False, 'message': 'Access denied'})

    try:
        package = Package.query.get_or_404(package_id)

        # Check if package is being used by clients
        client_packages = CustomerPackage.query.filter_by(package_id=package_id, is_active=True).count()
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
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('packages'))

    try:
        packages = Package.query.all()

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Package Name', 'Description', 'Package Type', 'Total Sessions', 
            'Validity Days', 'Total Price', 'Discount %', 'Status',
            'Prepaid Amount', 'Credit Amount', 'Bonus %'
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
                'Active' if package.is_active else 'Inactive',
                package.prepaid_amount or '',
                package.credit_amount or '',
                package.bonus_percentage or ''
            ])

        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=packages_export.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response

    except Exception as e:
        flash(f'Error exporting packages: {str(e)}', 'danger')
        return redirect(url_for('packages'))