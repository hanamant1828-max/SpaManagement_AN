"""
Simple Package Creation Views
Single-page workflow for creating packages with all required features
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import Package, PackageService, Service, Category, Client, ClientPackage
from .packages_queries import create_package_with_services
import json
from datetime import datetime, timedelta

@app.route('/packages/create-simple')
@login_required
def simple_package_creation():
    """Single-page package creation with all features"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    services = Service.query.filter_by(is_active=True).all()
    categories = Category.query.filter_by(category_type='service', is_active=True).all()
    
    return render_template('packages/simple_creation.html',
                         services=services,
                         categories=categories)

@app.route('/packages/create-simple', methods=['POST'])
@login_required
def simple_package_creation_submit():
    """Handle simple package creation form submission"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('packages'))
    
    try:
        # Basic package information
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        package_type = request.form.get('package_type', 'regular')
        validity_days = int(request.form.get('validity_days', 90))
        total_price = float(request.form.get('total_price', 0))
        discount_percentage = float(request.form.get('discount_percentage', 0))
        is_active = request.form.get('is_active') == 'on'
        
        # Validation
        if not name:
            flash('Package name is required', 'danger')
            return redirect(url_for('simple_package_creation'))
        
        # Service selection and sessions
        selected_services = request.form.getlist('selected_services')
        services_data = []
        
        for service_id in selected_services:
            sessions = request.form.get(f'sessions_{service_id}')
            service_discount = request.form.get(f'service_discount_{service_id}', 0)
            
            if sessions and int(sessions) > 0:
                services_data.append({
                    'service_id': int(service_id),
                    'sessions': int(sessions),
                    'service_discount': float(service_discount)
                })
        
        if not services_data:
            flash('Please select at least one service', 'danger')
            return redirect(url_for('simple_package_creation'))
        
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
            flash(f'Package "{name}" created successfully!', 'success')
            return redirect(url_for('packages'))
        else:
            flash('Failed to create package', 'danger')
            return redirect(url_for('simple_package_creation'))
    
    except Exception as e:
        flash(f'Error creating package: {str(e)}', 'danger')
        return redirect(url_for('simple_package_creation'))