
"""
Prepaid Package Management Views
Handles credit-based and service-based prepaid packages for spa
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from datetime import datetime, timedelta
from models import PrepaidPackage, ServicePackage, PackageTemplate, Service, Customer, CustomerPackage

@app.route('/packages/prepaid')
@login_required
def prepaid_packages():
    """Prepaid packages management page"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get prepaid packages
    credit_packages = PrepaidPackage.query.filter_by(is_active=True).all()
    service_packages = ServicePackage.query.filter_by(is_active=True).all()
    services = Service.query.filter_by(is_active=True).all()
    customers = Customer.query.filter_by(is_active=True).all()

    return render_template('prepaid_packages.html',
                         credit_packages=credit_packages,
                         service_packages=service_packages,
                         services=services,
                         customers=customers)

@app.route('/packages/prepaid/create-quick', methods=['POST'])
@login_required
def create_quick_prepaid():
    """Quick creation of standard prepaid packages"""
    if not current_user.can_access('packages'):
        return jsonify({'success': False, 'message': 'Access denied'})

    try:
        prepaid_type = request.form.get('prepaid_type')  # 'credit' or 'service'
        
        if prepaid_type == 'credit':
            # Standard credit packages
            packages_data = [
                {'name': 'Prepaid ₹15,000', 'pay': 15000, 'get': 17500, 'bonus': 15, 'validity': 60},
                {'name': 'Prepaid ₹20,000', 'pay': 20000, 'get': 25000, 'bonus': 20, 'validity': 90},
                {'name': 'Prepaid ₹30,000', 'pay': 30000, 'get': 40000, 'bonus': 25, 'validity': 120},
                {'name': 'Prepaid ₹50,000', 'pay': 50000, 'get': 70000, 'bonus': 30, 'validity': 180},
                {'name': 'Prepaid ₹1,00,000', 'pay': 100000, 'get': 150000, 'bonus': 35, 'validity': 365}
            ]
            
            for pkg_data in packages_data:
                existing = PrepaidPackage.query.filter_by(name=pkg_data['name']).first()
                if not existing:
                    package = PrepaidPackage(
                        name=pkg_data['name'],
                        description=f"Pay ₹{pkg_data['pay']:,} and get ₹{pkg_data['get']:,} credit ({pkg_data['bonus']}% bonus)",
                        validity_days=pkg_data['validity'],
                        prepaid_amount=pkg_data['pay'],
                        credit_amount=pkg_data['get'],
                        bonus_percentage=pkg_data['bonus'],
                        is_active=True
                    )
                    db.session.add(package)
            
        elif prepaid_type == 'service':
            # Standard service packages
            packages_data = [
                {'name': 'Pay for 3 Get 4', 'paid': 3, 'free': 1, 'total': 4, 'bonus': 25},
                {'name': 'Pay for 6 Get 9', 'paid': 6, 'free': 3, 'total': 9, 'bonus': 33},
                {'name': 'Pay for 9 Get 15', 'paid': 9, 'free': 6, 'total': 15, 'bonus': 40}
            ]
            
            for pkg_data in packages_data:
                existing = ServicePackage.query.filter_by(name=pkg_data['name']).first()
                if not existing:
                    package = ServicePackage(
                        name=pkg_data['name'],
                        description=f"Pay for {pkg_data['paid']} sessions, get {pkg_data['total']} total ({pkg_data['bonus']}% benefit)",
                        validity_days=90,  # Default 3 months
                        paid_sessions=pkg_data['paid'],
                        free_sessions=pkg_data['free'],
                        total_sessions=pkg_data['total'],
                        bonus_percentage=pkg_data['bonus'],
                        total_price=0,  # Will be calculated based on service selection
                        is_active=True
                    )
                    db.session.add(package)

        db.session.commit()
        return jsonify({'success': True, 'message': f'Standard {prepaid_type} packages created successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error creating packages: {str(e)}'})

@app.route('/packages/prepaid/calculate-credit', methods=['POST'])
@login_required
def calculate_prepaid_credit():
    """Calculate credit amount based on payment and bonus percentage"""
    try:
        pay_amount = float(request.form.get('pay_amount', 0))
        bonus_percentage = float(request.form.get('bonus_percentage', 0))
        
        bonus_amount = (pay_amount * bonus_percentage) / 100
        credit_amount = pay_amount + bonus_amount
        
        return jsonify({
            'success': True,
            'pay_amount': pay_amount,
            'bonus_amount': bonus_amount,
            'credit_amount': credit_amount,
            'bonus_percentage': bonus_percentage
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/packages/prepaid/assign/<int:package_id>', methods=['POST'])
@login_required
def assign_prepaid_package(package_id):
    """Assign prepaid package to customer"""
    if not current_user.can_access('packages'):
        return jsonify({'success': False, 'message': 'Access denied'})

    try:
        package = PackageTemplate.query.get_or_404(package_id)
        customer_id = request.form.get('customer_id')
        custom_amount = request.form.get('custom_amount')
        
        customer = Customer.query.get_or_404(customer_id)
        
        # Calculate expiry date
        expiry_date = datetime.utcnow() + timedelta(days=package.validity_days)
        
        # Determine amount and credit
        if package.package_type == 'prepaid_credit':
            amount_paid = float(custom_amount) if custom_amount else package.prepaid_amount
            credit_balance = package.credit_amount if not custom_amount else amount_paid * (1 + package.bonus_percentage/100)
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
            'message': f'Prepaid package assigned to {customer.full_name}',
            'credit_balance': credit_balance if package.package_type == 'prepaid_credit' else None
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error assigning package: {str(e)}'})
