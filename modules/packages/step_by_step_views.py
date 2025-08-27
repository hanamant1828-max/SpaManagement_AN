"""
Step-by-Step Package Creation Views
Implements a guided multi-step process for creating packages
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from app import app, db
from models import Package, PackageService, Service, Category, Customer, CustomerPackage
from .packages_queries import create_package_with_services
import json
from datetime import datetime, timedelta

@app.route('/packages/create-step-by-step')
@login_required
def package_creation_start():
    """Start the step-by-step package creation process"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Clear any existing package creation session
    session.pop('package_creation', None)
    
    # Initialize the package creation session
    session['package_creation'] = {
        'step': 1,
        'data': {}
    }
    
    return redirect(url_for('package_creation_step', step=1))

@app.route('/packages/create-step/<int:step>')
@login_required
def package_creation_step(step):
    """Display specific step of package creation"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if we have a package creation session
    if 'package_creation' not in session:
        return redirect(url_for('package_creation_start'))
    
    # Validate step number
    if step < 1 or step > 4:
        flash('Invalid step number', 'danger')
        return redirect(url_for('package_creation_start'))
    
    # Update current step
    session['package_creation']['step'] = step
    session.modified = True
    
    # Get data for current step
    creation_data = session['package_creation']['data']
    
    if step == 1:
        # Step 1: Basic package information
        return render_template('packages/step1_basic_info.html',
                             creation_data=creation_data,
                             current_step=step)
    
    elif step == 2:
        # Step 2: Service selection
        services = Service.query.filter_by(is_active=True).all()
        categories = Category.query.filter_by(category_type='service', is_active=True).all()
        return render_template('packages/step2_service_selection.html',
                             services=services,
                             categories=categories,
                             creation_data=creation_data,
                             current_step=step)
    
    elif step == 3:
        # Step 3: Pricing and discounts
        services = Service.query.filter_by(is_active=True).all()
        return render_template('packages/step3_pricing.html',
                             services=services,
                             creation_data=creation_data,
                             current_step=step)
    
    elif step == 4:
        # Step 4: Review and save
        # Calculate totals and prepare summary
        selected_services = creation_data.get('services', [])
        total_sessions = sum(service.get('sessions', 0) for service in selected_services)
        
        # Get full service details for display
        service_details = []
        total_original_price = 0
        
        for service_data in selected_services:
            service = Service.query.get(service_data['service_id'])
            if service:
                sessions = service_data['sessions']
                discount = service_data.get('service_discount', 0)
                original_price = service.price * sessions
                discounted_price = original_price * (1 - discount / 100)
                
                service_details.append({
                    'service': service,
                    'sessions': sessions,
                    'discount': discount,
                    'original_price': original_price,
                    'discounted_price': discounted_price
                })
                total_original_price += original_price
        
        return render_template('packages/step4_review.html',
                             creation_data=creation_data,
                             service_details=service_details,
                             total_sessions=total_sessions,
                             total_original_price=total_original_price,
                             current_step=step)

@app.route('/packages/create-step/<int:step>', methods=['POST'])
@login_required
def package_creation_step_submit(step):
    """Handle form submission for each step"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    if 'package_creation' not in session:
        return redirect(url_for('package_creation_start'))
    
    creation_data = session['package_creation']['data']
    
    try:
        if step == 1:
            # Process Step 1: Basic package information
            creation_data['name'] = request.form.get('name', '').strip()
            creation_data['description'] = request.form.get('description', '').strip()
            creation_data['package_type'] = request.form.get('package_type', 'regular')
            creation_data['validity_days'] = int(request.form.get('validity_days', 90))
            
            # Validation
            if not creation_data['name']:
                flash('Package name is required', 'danger')
                return redirect(url_for('package_creation_step', step=1))
            
            # Move to next step
            session['package_creation']['data'] = creation_data
            session.modified = True
            return redirect(url_for('package_creation_step', step=2))
        
        elif step == 2:
            # Process Step 2: Service selection
            services = []
            
            # Get selected services and their sessions
            selected_service_ids = request.form.getlist('service_ids')
            
            for service_id in selected_service_ids:
                sessions = request.form.get(f'sessions_{service_id}')
                if sessions and int(sessions) > 0:
                    services.append({
                        'service_id': int(service_id),
                        'sessions': int(sessions),
                        'service_discount': 0  # Will be set in step 3
                    })
            
            if not services:
                flash('Please select at least one service', 'danger')
                return redirect(url_for('package_creation_step', step=2))
            
            creation_data['services'] = services
            session['package_creation']['data'] = creation_data
            session.modified = True
            return redirect(url_for('package_creation_step', step=3))
        
        elif step == 3:
            # Process Step 3: Pricing and discounts
            services = creation_data.get('services', [])
            
            # Update service discounts
            for i, service_data in enumerate(services):
                service_id = service_data['service_id']
                discount = request.form.get(f'service_discount_{service_id}', 0)
                services[i]['service_discount'] = float(discount)
            
            # Get package-level pricing
            creation_data['total_price'] = float(request.form.get('total_price', 0))
            creation_data['discount_percentage'] = float(request.form.get('discount_percentage', 0))
            creation_data['is_active'] = request.form.get('is_active') == 'on'
            
            session['package_creation']['data'] = creation_data
            session.modified = True
            return redirect(url_for('package_creation_step', step=4))
        
        elif step == 4:
            # Process Step 4: Final save
            package = create_package_with_services(
                name=creation_data['name'],
                description=creation_data['description'],
                package_type=creation_data['package_type'],
                validity_days=creation_data['validity_days'],
                total_price=creation_data['total_price'],
                discount_percentage=creation_data['discount_percentage'],
                is_active=creation_data.get('is_active', True),
                services_data=creation_data['services']
            )
            
            if package:
                # Clear the session
                session.pop('package_creation', None)
                flash('Package created successfully!', 'success')
                return redirect(url_for('packages'))
            else:
                flash('Failed to create package', 'danger')
                return redirect(url_for('package_creation_step', step=4))
    
    except Exception as e:
        flash(f'Error processing step: {str(e)}', 'danger')
        return redirect(url_for('package_creation_step', step=step))

@app.route('/packages/create-step/<int:step>/back')
@login_required
def package_creation_step_back(step):
    """Go back to previous step"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    if 'package_creation' not in session:
        return redirect(url_for('package_creation_start'))
    
    previous_step = max(1, step - 1)
    return redirect(url_for('package_creation_step', step=previous_step))

@app.route('/packages/create-step/cancel')
@login_required
def package_creation_cancel():
    """Cancel package creation and clear session"""
    session.pop('package_creation', None)
    flash('Package creation cancelled', 'info')
    return redirect(url_for('packages'))

@app.route('/api/service-price/<int:service_id>')
@login_required
def get_service_price(service_id):
    """Get service price for JavaScript calculations"""
    service = Service.query.get_or_404(service_id)
    return jsonify({
        'price': service.price,
        'name': service.name
    })