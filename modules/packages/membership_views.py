
"""
Membership Management Views - Separate pages for Add, Edit, View operations
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import Membership, MembershipService, Service
from datetime import datetime

@app.route('/memberships')
@login_required
def memberships_list():
    """List all memberships"""
    if not hasattr(current_user, 'can_access') or not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    memberships = Membership.query.all()
    return render_template('memberships/list.html', memberships=memberships)

@app.route('/memberships/add')
@login_required
def membership_add():
    """Add new membership form"""
    if not hasattr(current_user, 'can_access') or not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    services = Service.query.filter_by(is_active=True).all()
    return render_template('memberships/add.html', services=services)

@app.route('/memberships/add', methods=['POST'])
@login_required
def membership_add_submit():
    """Submit new membership"""
    try:
        # Validate user permissions
        if not hasattr(current_user, 'can_access') or not current_user.can_access('packages'):
            flash('Access denied', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get form data with validation
        name = request.form.get('name', '').strip()
        price_str = request.form.get('price', '0')
        validity_months_str = request.form.get('validity_months', '12')
        services_included = request.form.get('services_included', '').strip()
        description = request.form.get('description', '').strip() if request.form.get('description') else None
        is_active = request.form.get('is_active') == 'on'
        
        # Validate required fields
        if not name:
            flash('Membership name is required', 'error')
            return redirect(url_for('membership_add'))
        
        # Validate price
        try:
            price = float(price_str)
            if price <= 0:
                flash('Price must be greater than 0', 'error')
                return redirect(url_for('membership_add'))
        except (ValueError, TypeError):
            flash('Please enter a valid price', 'error')
            return redirect(url_for('membership_add'))
        
        # Validate validity months
        try:
            validity_months = int(validity_months_str)
            if validity_months <= 0:
                flash('Validity months must be greater than 0', 'error')
                return redirect(url_for('membership_add'))
        except (ValueError, TypeError):
            flash('Please enter valid validity months', 'error')
            return redirect(url_for('membership_add'))
        
        # Get selected services
        selected_services = request.form.getlist('service_ids')
        
        # Create membership
        membership = Membership(
            name=name,
            price=price,
            validity_months=validity_months,
            services_included=services_included,
            description=description,
            is_active=is_active,
            created_at=datetime.utcnow()
        )
        
        db.session.add(membership)
        db.session.flush()
        
        # Add selected services
        for service_id in selected_services:
            if service_id and service_id.strip():
                try:
                    service_id_int = int(service_id)
                    membership_service = MembershipService(
                        membership_id=membership.id,
                        service_id=service_id_int
                    )
                    db.session.add(membership_service)
                except (ValueError, TypeError):
                    print(f"Warning: Invalid service ID: {service_id}")
                    continue
        
        db.session.commit()
        flash(f'Membership "{name}" created successfully!', 'success')
        return redirect(url_for('memberships_list'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating membership: {str(e)}")
        flash(f'Error creating membership: {str(e)}', 'error')
        return redirect(url_for('membership_add'))

@app.route('/memberships/edit/<int:membership_id>')
@login_required
def membership_edit(membership_id):
    """Edit membership form"""
    if not hasattr(current_user, 'can_access') or not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    membership = Membership.query.get_or_404(membership_id)
    services = Service.query.filter_by(is_active=True).all()
    
    # Get currently selected services
    selected_service_ids = [ms.service_id for ms in membership.membership_services]
    
    return render_template('memberships/edit.html', 
                         membership=membership, 
                         services=services,
                         selected_service_ids=selected_service_ids)

@app.route('/memberships/edit/<int:membership_id>', methods=['POST'])
@login_required
def membership_edit_submit(membership_id):
    """Submit membership edit"""
    try:
        membership = Membership.query.get_or_404(membership_id)
        
        membership.name = request.form.get('name', '').strip()
        membership.price = float(request.form.get('price', 0))
        membership.validity_months = int(request.form.get('validity_months', 12))
        membership.services_included = request.form.get('services_included', '').strip()
        membership.description = request.form.get('description', '').strip() if request.form.get('description') else None
        membership.is_active = request.form.get('is_active') == 'on'
        
        if not membership.name or membership.price <= 0:
            flash('Name and valid price are required', 'error')
            return redirect(url_for('membership_edit', membership_id=membership_id))
        
        # Update selected services
        selected_services = request.form.getlist('service_ids')
        
        # Remove existing services
        MembershipService.query.filter_by(membership_id=membership_id).delete()
        
        # Add new selected services
        for service_id in selected_services:
            if service_id:
                membership_service = MembershipService(
                    membership_id=membership_id,
                    service_id=int(service_id)
                )
                db.session.add(membership_service)
        
        db.session.commit()
        flash(f'Membership "{membership.name}" updated successfully!', 'success')
        return redirect(url_for('memberships_list'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating membership: {str(e)}', 'error')
        return redirect(url_for('membership_edit', membership_id=membership_id))

@app.route('/memberships/view/<int:membership_id>')
@login_required
def membership_view(membership_id):
    """View membership details"""
    if not hasattr(current_user, 'can_access') or not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    membership = Membership.query.get_or_404(membership_id)
    return render_template('memberships/view.html', membership=membership)

@app.route('/memberships/delete/<int:membership_id>', methods=['POST'])
@login_required
def membership_delete(membership_id):
    """Delete membership"""
    try:
        membership = Membership.query.get_or_404(membership_id)
        name = membership.name
        
        # Delete related services first
        MembershipService.query.filter_by(membership_id=membership_id).delete()
        
        # Delete membership
        db.session.delete(membership)
        db.session.commit()
        
        flash(f'Membership "{name}" deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting membership: {str(e)}', 'error')
    
    return redirect(url_for('memberships_list'))
