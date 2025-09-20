"""
New Package Management Views - Separate endpoints for each package type
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import Service, ServicePackage # Added ServicePackage to imports
from .new_packages_queries import *
import logging

# ========================================
# MAIN PACKAGES PAGE WITH TABS
# ========================================

@app.route('/packages')
@login_required
def packages():
    """Main packages page with tabbed interface"""
    if not hasattr(current_user, 'can_access') or not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get all package data for tabs
    stats = get_all_package_statistics()

    # Get data for each tab
    prepaid_packages = get_all_prepaid_packages()
    service_packages = get_all_service_packages()
    memberships = get_all_memberships()
    student_offers = get_all_student_offers()
    yearly_memberships = get_all_yearly_memberships()
    kitty_parties = get_all_kitty_parties()

    # Get customers for assignment dropdowns
    from models import Customer
    customers = Customer.query.filter_by(is_active=True).order_by(Customer.first_name, Customer.last_name).all()

    return render_template('new_packages.html',
                         prepaid_packages=prepaid_packages,
                         service_packages=service_packages,
                         memberships=memberships,
                         student_offers=student_offers,
                         yearly_memberships=yearly_memberships,
                         kitty_parties=kitty_parties,
                         customers=customers,
                         stats=stats)

# ========================================
# PREPAID PACKAGES ENDPOINTS
# ========================================

@app.route('/api/prepaid-packages', methods=['GET'])
@login_required
def api_get_prepaid_packages():
    """Get all prepaid packages"""
    try:
        packages = get_all_prepaid_packages()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'actual_price': p.actual_price,
            'after_value': p.after_value,
            'benefit_percent': p.benefit_percent,
            'validity_months': p.validity_months,
            'money_saved': p.money_saved,
            'is_active': p.is_active,
            'created_at': p.created_at.isoformat()
        } for p in packages])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prepaid-packages', methods=['POST'])
@login_required
def api_create_prepaid_package():
    """Create new prepaid package"""
    try:
        # Handle both JSON and form data properly
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        package = create_prepaid_package(data)
        flash('Prepaid package created successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Prepaid package created successfully',
            'package_id': package.id
        })
    except Exception as e:
        logging.error(f"Error creating prepaid package: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/prepaid-packages/<int:package_id>', methods=['PUT'])
@login_required
def api_update_prepaid_package(package_id):
    """Update prepaid package"""
    try:
        # Handle both JSON and form data properly
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        package = update_prepaid_package(package_id, data)
        flash('Prepaid package updated successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Prepaid package updated successfully'
        })
    except Exception as e:
        logging.error(f"Error updating prepaid package: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/prepaid-packages/<int:package_id>', methods=['DELETE'])
@login_required
def api_delete_prepaid_package(package_id):
    """Delete prepaid package"""
    try:
        delete_prepaid_package(package_id)
        flash('Prepaid package deleted successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Prepaid package deleted successfully'
        })
    except Exception as e:
        logging.error(f"Error deleting prepaid package: {e}")
        return jsonify({'error': str(e)}), 500

# ========================================
# SERVICE PACKAGES ENDPOINTS
# ========================================

@app.route('/api/service-packages', methods=['GET'])
@login_required
def api_get_service_packages():
    """Get all service packages"""
    try:
        packages = get_all_service_packages()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'pay_for': p.pay_for,
            'total_services': p.total_services,
            'free_services': p.free_services,
            'benefit_percent': p.benefit_percent,
            'validity_months': p.validity_months,
            'is_active': p.is_active,
            'created_at': p.created_at.isoformat()
        } for p in packages])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/service-packages', methods=['POST'])
@login_required
def api_create_service_package():
    """Create new service package"""
    try:
        # Handle both JSON and form data properly
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        package = create_service_package(data)
        flash('Service package created successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Service package created successfully',
            'package_id': package.id
        })
    except Exception as e:
        logging.error(f"Error creating service package: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/service-packages/<int:package_id>', methods=['PUT'])
@login_required
def api_update_service_package(package_id):
    """Update service package"""
    try:
        data = request.get_json() or request.form.to_dict()
        package = update_service_package(package_id, data)
        flash('Service package updated successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Service package updated successfully'
        })
    except Exception as e:
        logging.error(f"Error updating service package: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/service-packages/<int:package_id>', methods=['DELETE'])
@login_required
def api_delete_service_package(package_id):
    """Delete service package"""
    try:
        delete_service_package(package_id)
        flash('Service package deleted successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Service package deleted successfully'
        })
    except Exception as e:
        logging.error(f"Error deleting service package: {e}")
        return jsonify({'error': str(e)}), 500

# ========================================
# MEMBERSHIPS ENDPOINTS
# ========================================

@app.route('/api/memberships', methods=['GET'])
@login_required
def api_get_memberships():
    """Get all memberships"""
    try:
        memberships = get_all_memberships()
        return jsonify([{
            'id': m.id,
            'name': m.name,
            'price': m.price,
            'validity_months': m.validity_months,
            'services_included': m.services_included,
            'selected_services': [{'id': ms.service.id, 'name': ms.service.name, 'price': ms.service.price} 
                                for ms in m.membership_services] if hasattr(m, 'membership_services') else [],
            'is_active': m.is_active,
            'created_at': m.created_at.isoformat()
        } for m in memberships])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memberships', methods=['POST'])
@login_required
def api_create_membership():
    """Create new membership"""
    try:
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            # Handle multiple service selections from form
            if 'service_ids' not in data:
                data['service_ids'] = request.form.getlist('service_ids')

        membership = create_membership(data)
        flash('Membership created successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Membership created successfully',
            'membership_id': membership.id
        })
    except Exception as e:
        logging.error(f"Error creating membership: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/memberships/<int:membership_id>', methods=['PUT'])
@login_required
def api_update_membership(membership_id):
    """Update membership"""
    try:
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            # Handle multiple service selections from form
            if 'service_ids' not in data:
                data['service_ids'] = request.form.getlist('service_ids')

        membership = update_membership(membership_id, data)
        flash('Membership updated successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Membership updated successfully'
        })
    except Exception as e:
        logging.error(f"Error updating membership: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/memberships/<int:membership_id>', methods=['DELETE'])
@login_required
def api_delete_membership(membership_id):
    """Delete membership"""
    try:
        delete_membership(membership_id)
        flash('Membership deleted successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Membership deleted successfully'
        })
    except Exception as e:
        logging.error(f"Error deleting membership: {e}")
        return jsonify({'error': str(e)}), 500

# ========================================
# STUDENT OFFERS ENDPOINTS
# ========================================

@app.route('/api/student-offers', methods=['GET'])
@login_required
def api_get_student_offers():
    """Get all student offers"""
    try:
        offers = get_all_student_offers()
        return jsonify([{
            'id': o.id,
            'service_id': o.service_id,
            'service_name': o.service.name if o.service else o.service_name,
            'actual_price': o.actual_price,
            'discount_percent': o.discount_percent,
            'after_price': o.after_price,
            'money_saved': o.money_saved,
            'valid_days': o.valid_days,
            'is_active': o.is_active,
            'created_at': o.created_at.isoformat()
        } for o in offers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/student-offers', methods=['POST'])
@login_required
def api_create_student_offer():
    """Create new student offer"""
    try:
        data = request.get_json() or request.form.to_dict()
        offer = create_student_offer(data)
        flash('Student offer created successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Student offer created successfully',
            'offer_id': offer.id
        })
    except Exception as e:
        logging.error(f"Error creating student offer: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/student-offers/<int:offer_id>', methods=['PUT'])
@login_required
def api_update_student_offer(offer_id):
    """Update student offer"""
    try:
        data = request.get_json() or request.form.to_dict()
        offer = update_student_offer(offer_id, data)
        flash('Student offer updated successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Student offer updated successfully'
        })
    except Exception as e:
        logging.error(f"Error updating student offer: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/student-offers/<int:offer_id>', methods=['DELETE'])
@login_required
def api_delete_student_offer(offer_id):
    """Delete student offer"""
    try:
        delete_student_offer(offer_id)
        flash('Student offer deleted successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Student offer deleted successfully'
        })
    except Exception as e:
        logging.error(f"Error deleting student offer: {e}")
        return jsonify({'error': str(e)}), 500

# ========================================
# YEARLY MEMBERSHIPS ENDPOINTS
# ========================================

@app.route('/api/yearly-memberships', methods=['GET'])
@login_required
def api_get_yearly_memberships():
    """Get all yearly memberships"""
    try:
        memberships = get_all_yearly_memberships()
        return jsonify([{
            'id': m.id,
            'name': m.name,
            'price': m.price,
            'discount_percent': m.discount_percent,
            'validity_months': m.validity_months,
            'extra_benefits': m.extra_benefits,
            'is_active': m.is_active,
            'created_at': m.created_at.isoformat()
        } for m in memberships])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/yearly-memberships', methods=['POST'])
@login_required
def api_create_yearly_membership():
    """Create new yearly membership"""
    try:
        data = request.get_json() or request.form.to_dict()
        membership = create_yearly_membership(data)
        flash('Yearly membership created successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Yearly membership created successfully',
            'membership_id': membership.id
        })
    except Exception as e:
        logging.error(f"Error creating yearly membership: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/yearly-memberships/<int:membership_id>', methods=['PUT'])
@login_required
def api_update_yearly_membership(membership_id):
    """Update yearly membership"""
    try:
        data = request.get_json() or request.form.to_dict()
        membership = update_yearly_membership(membership_id, data)
        flash('Yearly membership updated successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Yearly membership updated successfully'
        })
    except Exception as e:
        logging.error(f"Error updating yearly membership: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/yearly-memberships/<int:membership_id>', methods=['DELETE'])
@login_required
def api_delete_yearly_membership(membership_id):
    """Delete yearly membership"""
    try:
        delete_yearly_membership(membership_id)
        flash('Yearly membership deleted successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Yearly membership deleted successfully'
        })
    except Exception as e:
        logging.error(f"Error deleting yearly membership: {e}")
        return jsonify({'error': str(e)}), 500

# ========================================
# KITTY PARTIES ENDPOINTS
# ========================================

@app.route('/api/kitty-parties', methods=['GET'])
@login_required
def api_get_kitty_parties():
    """Get all kitty parties"""
    try:
        parties = get_all_kitty_parties()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'after_value': p.after_value,
            'min_guests': p.min_guests,
            'services_included': p.services_included,
            'selected_services': [{'id': kps.service.id, 'name': kps.service.name, 'price': kps.service.price} 
                                for kps in p.kittyparty_services] if hasattr(p, 'kittyparty_services') else [],
            'is_active': p.is_active,
            'created_at': p.created_at.isoformat()
        } for p in parties])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/kitty-parties', methods=['POST'])
@login_required
def api_create_kitty_party():
    """Create new kitty party"""
    try:
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            # Handle multiple service selections from form
            if 'service_ids' not in data:
                data['service_ids'] = request.form.getlist('service_ids')

        party = create_kitty_party(data)
        flash('Kitty party created successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Kitty party created successfully',
            'party_id': party.id
        })
    except Exception as e:
        logging.error(f"Error creating kitty party: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/kitty-parties/<int:party_id>', methods=['PUT'])
@login_required
def api_update_kitty_party(party_id):
    """Update kitty party"""
    try:
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            # Handle multiple service selections from form
            if 'service_ids' not in data:
                data['service_ids'] = request.form.getlist('service_ids')

        party = update_kitty_party(party_id, data)
        flash('Kitty party updated successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Kitty party updated successfully'
        })
    except Exception as e:
        logging.error(f"Error updating kitty party: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/kitty-parties/<int:party_id>', methods=['DELETE'])
@login_required
def api_delete_kitty_party(party_id):
    """Delete kitty party"""
    try:
        delete_kitty_party(party_id)
        flash('Kitty party deleted successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Kitty party deleted successfully'
        })
    except Exception as e:
        logging.error(f"Error deleting kitty party: {e}")
        return jsonify({'error': str(e)}), 500

# ========================================
# STATISTICS ENDPOINT
# ========================================

@app.route('/api/package-statistics', methods=['GET'])
@login_required
def api_get_package_statistics():
    """Get package statistics"""
    try:
        stats = get_all_package_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route for adding a new service package template
@app.route('/packages/service-packages/add', methods=['POST'])
@login_required
def add_service_package():
    try:
        name = request.form.get('name', '').strip()
        pay_for = int(request.form.get('pay_for', 0))
        total_services = int(request.form.get('total_services', 0))
        validity_months = int(request.form.get('validity_months', 0))

        if not all([name, pay_for > 0, total_services > 0, validity_months > 0]):
            flash('All fields are required and must be valid.', 'error')
            return redirect(url_for('new_packages'))

        # Calculate benefit percentage
        free_services = total_services - pay_for
        benefit_percent = (free_services / pay_for) * 100 if pay_for > 0 else 0

        # Create service package template without service_id (will be chosen during assignment)
        service_package = ServicePackage(
            name=name,
            service_id=None,  # Service will be chosen when assigning to customer
            pay_for=pay_for,
            total_services=total_services,
            benefit_percent=benefit_percent,
            validity_months=validity_months
        )

        db.session.add(service_package)
        db.session.commit()

        flash(f'Service package template "{name}" created successfully! Service will be selected during customer assignment.', 'success')
        return redirect(url_for('new_packages'))

    except Exception as e:
        flash(f'Error creating service package: {str(e)}', 'error')
        return redirect(url_for('new_packages'))

# ========================================
# NEW API ENDPOINTS FOR PREPAID ASSIGNMENT
# ========================================

@app.route('/packages/api/templates/<int:template_id>', methods=['GET'])
@login_required
def api_get_package_template(template_id):
    """Get specific package template details"""
    try:
        from .new_packages_queries import get_prepaid_package_by_id, get_service_package_by_id
        
        # Try to get as prepaid package first
        template = get_prepaid_package_by_id(template_id)
        if template:
            return jsonify({
                'success': True,
                'template': {
                    'id': template.id,
                    'name': template.name,
                    'pay_amount': template.actual_price,
                    'actual_price': template.actual_price,
                    'get_value': template.after_value,
                    'after_value': template.after_value,
                    'benefit_percent': template.benefit_percent,
                    'validity_months': template.validity_months,
                    'package_type': 'prepaid'
                }
            })
            
        # Try service package
        template = get_service_package_by_id(template_id)
        if template:
            # Calculate benefit percentage if not set
            benefit_percent = template.benefit_percent
            if not benefit_percent and template.pay_for > 0:
                benefit_percent = (template.free_services / template.pay_for) * 100
                
            return jsonify({
                'success': True,
                'template': {
                    'id': template.id,
                    'name': template.name,
                    'pay_for': template.pay_for,
                    'total_services': template.total_services,
                    'free_services': template.free_services,
                    'benefit_percent': round(benefit_percent, 1) if benefit_percent else 0,
                    'validity_months': template.validity_months,
                    'package_type': 'service_package',
                    'service_id': template.service_id,
                    'choose_on_assign': template.choose_on_assign
                }
            })
            
        return jsonify({'success': False, 'error': 'Template not found'}), 404
        
    except Exception as e:
        logging.error(f"Error fetching template {template_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/packages/api/customers', methods=['GET'])
@login_required
def api_get_customers():
    """Get customers with optional search"""
    try:
        from models import Customer
        
        query = request.args.get('q', '').strip()
        
        if query:
            # Search by name or phone
            customers = Customer.query.filter(
                (Customer.first_name.ilike(f'%{query}%')) |
                (Customer.last_name.ilike(f'%{query}%')) |
                (Customer.phone.ilike(f'%{query}%'))
            ).order_by(Customer.first_name, Customer.last_name).limit(50).all()
        else:
            # Get all customers (limit for performance)
            customers = Customer.query.order_by(Customer.first_name, Customer.last_name).limit(100).all()
            
        return jsonify({
            'success': True,
            'customers': [{
                'id': c.id,
                'name': c.full_name,
                'phone': c.phone or '',
                'email': c.email or ''
            } for c in customers]
        })
        
    except Exception as e:
        logging.error(f"Error fetching customers: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/packages/api/services', methods=['GET'])
@login_required 
def api_get_services():
    """Get available services"""
    try:
        services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
        
        return jsonify({
            'success': True,
            'services': [{
                'id': s.id,
                'name': s.name,
                'price': float(s.price),
                'duration': s.duration
            } for s in services]
        })
        
    except Exception as e:
        logging.error(f"Error fetching services: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/packages/api/assign', methods=['POST'])
@login_required
def api_assign_package():
    """Assign package to customer"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        package_type = data.get('package_type')
        package_id = data.get('package_id')
        customer_id = data.get('customer_id')
        service_id = data.get('service_id')
        price_paid = data.get('price_paid')
        expires_on = data.get('expires_on')
        notes = data.get('notes', '')
        
        # Validate required fields
        if not all([package_type, package_id, customer_id, service_id]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
        if price_paid is None or price_paid < 0:
            return jsonify({'success': False, 'error': 'Invalid price paid'}), 400
            
        # Import models
        from models import Customer, CustomerPackage
        from datetime import datetime, timedelta
        
        # Verify customer exists
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
            
        # Verify service exists
        service = Service.query.get(service_id)
        if not service:
            return jsonify({'success': False, 'error': 'Service not found'}), 404
        
        # Handle prepaid package assignment
        if package_type == 'prepaid':
            from .new_packages_queries import get_prepaid_package_by_id
            
            template = get_prepaid_package_by_id(package_id)
            if not template:
                return jsonify({'success': False, 'error': 'Prepaid package template not found'}), 404
                
            # Calculate expiry date
            if expires_on:
                expiry_date = datetime.strptime(expires_on, '%Y-%m-%d').date()
            else:
                expiry_date = datetime.now().date() + timedelta(days=template.validity_months * 30)
                
            # Create customer package assignment
            customer_package = CustomerPackage(
                customer_id=customer_id,
                package_id=package_id,
                price_paid=price_paid,
                expires_on=datetime.combine(expiry_date, datetime.min.time()),
                notes=notes,
                status='active'
            )
            
            db.session.add(customer_package)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Prepaid package assigned successfully to {customer.full_name}',
                'id': customer_package.id
            })
            
        # Handle service package assignment
        elif package_type == 'service_package':
            from .new_packages_queries import get_service_package_by_id
            
            template = get_service_package_by_id(package_id)
            if not template:
                return jsonify({'success': False, 'error': 'Service package template not found'}), 404
                
            # Calculate expiry date
            if expires_on:
                expiry_date = datetime.strptime(expires_on, '%Y-%m-%d').date()
            else:
                expiry_date = datetime.now().date() + timedelta(days=template.validity_months * 30) if template.validity_months else None
                
            # Use service price for package price if not provided
            if price_paid == 0:
                service_price = service.price * template.pay_for
                price_paid = service_price
                
            # Create customer package assignment for service package
            customer_package = CustomerPackage(
                customer_id=customer_id,
                package_id=package_id,
                price_paid=price_paid,
                expires_on=datetime.combine(expiry_date, datetime.min.time()) if expiry_date else None,
                notes=notes,
                status='active'
            )
            
            db.session.add(customer_package)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Service package "{template.name}" assigned successfully to {customer.full_name} for {service.name}',
                'id': customer_package.id
            })
            
        else:
            return jsonify({'success': False, 'error': 'Package type not supported yet'}), 400
            
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error assigning package: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500