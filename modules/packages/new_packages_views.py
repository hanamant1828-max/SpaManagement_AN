"""
New Package Management Views - Separate endpoints for each package type
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import Service, ServicePackage, ServicePackageAssignment, Customer, PrepaidPackage, Membership # Added missing imports
from .new_packages_queries import (
    # Statistics
    get_all_package_statistics,

    # Prepaid Packages
    get_all_prepaid_packages, get_prepaid_package_by_id, create_prepaid_package, update_prepaid_package, delete_prepaid_package,

    # Service Packages
    get_all_service_packages, get_service_package_by_id, create_service_package, update_service_package, delete_service_package,

    # Memberships
    get_all_memberships, get_membership_by_id, create_membership, update_membership, delete_membership,

    # Student Offers
    get_all_student_offers, get_student_offer_by_id, create_student_offer, update_student_offer, delete_student_offer,

    # Yearly Memberships
    get_all_yearly_memberships, get_yearly_membership_by_id, create_yearly_membership, update_yearly_membership, delete_yearly_membership,

    # Kitty Parties
    get_all_kitty_parties, get_kitty_party_by_id, create_kitty_party, update_kitty_party, delete_kitty_party
)
import logging
from datetime import datetime, timedelta

# Assuming 'packages_blueprint' is defined elsewhere and imported, and logger is configured.
# For the purpose of this example, let's assume they are available.
# If not, these would need to be defined or imported.
# from flask import Blueprint
# packages_blueprint = Blueprint('packages', __name__)
# logger = logging.getLogger(__name__)

# Define packages_blueprint and logger properly
from flask import Blueprint
import logging

# Create and configure logger
logger = logging.getLogger(__name__)

# Note: Blueprint registration handled in app.py to avoid circular imports

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
    from models import Customer, Service
    customers = Customer.query.filter_by(is_active=True).order_by(Customer.first_name, Customer.last_name).all()

    # Get services for dropdowns
    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()

    return render_template('new_packages.html',
                         prepaid_packages=prepaid_packages,
                         service_packages=service_packages,
                         memberships=memberships,
                         student_offers=student_offers,
                         yearly_memberships=yearly_memberships,
                         kitty_parties=kitty_parties,
                         customers=customers,
                         services=services,
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
# STUDENT OFFERS PAGE ROUTES
# ========================================

@app.route('/student-offers/add')
@login_required
def add_student_offer():
    """Add student offer page"""
    if not hasattr(current_user, 'can_access') or not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('packages/add_student_offer.html')

@app.route('/student-offers/edit')
@login_required
def edit_student_offer():
    """Edit student offer page"""
    if not hasattr(current_user, 'can_access') or not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    offer_id = request.args.get('id')
    if not offer_id:
        flash('Student offer ID is required', 'error')
        return redirect(url_for('packages'))

    return render_template('packages/edit_student_offer.html', offer_id=offer_id)

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
            'discount_percentage': o.discount_percentage,
            'valid_from': o.valid_from.isoformat(),
            'valid_to': o.valid_to.isoformat(),
            'valid_days': o.valid_days,
            'conditions': o.conditions,
            'services': [{'id': sos.service.id, 'name': sos.service.name, 'price': sos.service.price}
                        for sos in o.student_offer_services],
            'is_active': o.is_active,
            'created_at': o.created_at.isoformat()
        } for o in offers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# NOTE: Student offer creation endpoint moved to modules/packages/routes.py
# to avoid routing conflicts with the main packages blueprint

@app.route('/packages/student-offers/create', methods=['POST'])
@login_required
def create_student_offer():
    """Create a new student offer package"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('service_ids') or not isinstance(data['service_ids'], list):
            return jsonify({'success': False, 'error': 'At least one service must be selected'}), 400

        if not data.get('discount_percentage'):
            return jsonify({'success': False, 'error': 'Discount percentage is required'}), 400

        # Import models
        from models import StudentOffer, StudentOfferService, Service
        from datetime import datetime

        # Create student offer
        student_offer = StudentOffer(
            discount_percent=float(data['discount_percentage']),
            valid_from=datetime.strptime(data['valid_from'], '%Y-%m-%d').date() if data.get('valid_from') else None,
            valid_to=datetime.strptime(data['valid_to'], '%Y-%m-%d').date() if data.get('valid_to') else None,
            valid_days=data.get('valid_days', 'Mon-Sun'),
            conditions=data.get('conditions', ''),
            is_active=data.get('is_active', True)
        )

        db.session.add(student_offer)
        db.session.flush()

        # Add services to the offer
        for service_id in data['service_ids']:
            service = Service.query.get(service_id)
            if service:
                offer_service = StudentOfferService(
                    student_offer_id=student_offer.id,
                    service_id=service_id
                )
                db.session.add(offer_service)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Student offer created successfully',
            'offer_id': student_offer.id
        })

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating student offer: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/student-offers/<int:offer_id>', methods=['GET'])
@login_required
def api_get_student_offer(offer_id):
    """Get specific student offer by ID"""
    try:
        offer = get_student_offer_by_id(offer_id)
        if not offer:
            return jsonify({'success': False, 'error': 'Student offer not found'}), 404

        return jsonify({
            'success': True,
            'offer': {
                'id': offer.id,
                'discount_percentage': offer.discount_percentage,
                'valid_from': offer.valid_from.isoformat() if offer.valid_from else None,
                'valid_to': offer.valid_to.isoformat() if offer.valid_to else None,
                'valid_days': offer.valid_days,
                'conditions': offer.conditions,
                'services': [{'id': sos.service.id, 'name': sos.service.name, 'price': sos.service.price}
                            for sos in offer.student_offer_services],
                'is_active': offer.is_active
            }
        })
    except Exception as e:
        logging.error(f"Error getting student offer {offer_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/student-offers/<int:offer_id>', methods=['PUT'])
@login_required
def api_update_student_offer(offer_id):
    """Update student offer"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            # Handle multiple service selection from form data
            if 'service_ids' in request.form:
                data['service_ids'] = request.form.getlist('service_ids')

        # Validate required fields (same as create)
        if not data.get('service_ids') or len(data['service_ids']) == 0:
            return jsonify({'success': False, 'error': 'Please select at least one service'}), 400

        if not data.get('discount_percentage'):
            return jsonify({'success': False, 'error': 'Discount percentage is required'}), 400

        # Validate discount percentage range
        try:
            discount = float(data['discount_percentage'])
            if discount < 1 or discount > 100:
                return jsonify({'success': False, 'error': 'Discount percentage must be between 1 and 100'}), 400
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Invalid discount percentage format'}), 400

        if not data.get('valid_from') or not data.get('valid_to'):
            return jsonify({'success': False, 'error': 'Valid from and to dates are required'}), 400

        # Validate date range
        try:
            from datetime import datetime
            valid_from = datetime.strptime(data['valid_from'], '%Y-%m-%d').date()
            valid_to = datetime.strptime(data['valid_to'], '%Y-%m-%d').date()
            if valid_to < valid_from:
                return jsonify({'success': False, 'error': 'Valid To Date must be greater than or equal to Valid From Date'}), 400
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format. Please use YYYY-MM-DD format'}), 400

        offer = update_student_offer(offer_id, data)
        flash('Student offer updated successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Student offer updated successfully'
        })
    except Exception as e:
        logging.error(f"Error updating student offer: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/student-offers/<int:offer_id>', methods=['DELETE'])
@login_required
def api_delete_student_offer(offer_id):
    """Delete student offer"""
    try:
        # Check if student offer exists first by trying to get it
        existing_offer = get_student_offer_by_id(offer_id)
        if not existing_offer:
            return jsonify({
                'success': False,
                'error': 'Student offer not found'
            }), 404

        delete_student_offer(offer_id)
        flash('Student offer deleted successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Student offer deleted successfully'
        })
    except Exception as e:
        logging.error(f"Error deleting student offer: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
    """API endpoint to create kitty party"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            print(f"📥 Received JSON data: {data}")
        else:
            data = request.form.to_dict()
            # Handle service_ids from form
            if 'service_ids' in request.form:
                service_ids = request.form.getlist('service_ids')
                data['service_ids'] = [sid for sid in service_ids if sid]  # Remove empty values
            print(f"📥 Received form data: {data}")

        # Validate required fields
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Package name is required'}), 400

        if not data.get('price'):
            return jsonify({'success': False, 'error': 'Package price is required'}), 400

        # Validate services
        service_ids = data.get('service_ids', [])
        if not service_ids or (isinstance(service_ids, list) and len(service_ids) == 0):
            return jsonify({'success': False, 'error': 'Please select at least one service for this kitty party'}), 400

        print(f"🎯 Creating kitty party: {data.get('name')} with services: {service_ids}")

        # Create the kitty party
        kitty_party = create_kitty_party(data)

        return jsonify({
            'success': True,
            'message': 'Kitty party created successfully!',
            'party_id': kitty_party.id
        })

    except ValueError as e:
        print(f"❌ Validation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        print(f"❌ Error in API create kitty party: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error creating kitty party. Please try again.'}), 500

@app.route('/api/kitty-parties/<int:party_id>', methods=['PUT'])
@login_required
def api_update_kitty_party(party_id):
    """Update existing kitty party"""
    try:
        data = request.get_json()
        # Ensure 'service_ids' is handled correctly if coming from form data
        if not data and request.form:
            data = request.form.to_dict()
            if 'service_ids' not in data:
                data['service_ids'] = request.form.getlist('service_ids')

        party = update_kitty_party(party_id, data)
        flash('Kitty party updated successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Kitty party updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating kitty party: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

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
                'phone': c.phone or ''
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

        service_list = []
        for s in services:
            service_list.append({
                'id': s.id,
                'name': s.name,
                'price': float(s.price) if s.price else 0.0,
                'duration': s.duration if s.duration else 0
            })

        return jsonify({
            'success': True,
            'services': service_list
        })

    except Exception as e:
        logging.error(f"Error fetching services: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/packages/api/templates', methods=['POST'])
@login_required
def api_create_template():
    """Create new package template (membership, etc.)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        template_type = data.get('type')

        if template_type == 'membership':
            # Create membership template
            from models import Membership, MembershipService

            membership = Membership(
                name=data.get('name'),
                price=float(data.get('price', 0)),
                validity_months=12,  # Default validity
                is_active=True
            )

            db.session.add(membership)
            db.session.flush()  # Get the membership ID

            # Add services if provided
            items = data.get('items', [])
            for item in items:
                service_id = item.get('service_id')
                sessions = item.get('sessions', 1)

                if service_id:
                    membership_service = MembershipService(
                        membership_id=membership.id,
                        service_id=int(service_id)
                    )
                    db.session.add(membership_service)

            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'Membership "{membership.name}" created successfully',
                'template_id': membership.id
            })

        else:
            return jsonify({'success': False, 'error': 'Unsupported template type'}), 400

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating template: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/packages/api/assign', methods=['POST'])
@login_required
def assign_package():
    """Assign package to customer via API - ONLY AFTER PAYMENT CONFIRMATION"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # Handle both client_id and customer_id for compatibility
        customer_id = data.get('client_id') or data.get('customer_id')

        # Validate required fields with detailed messages
        if not customer_id:
            return jsonify({'success': False, 'error': 'Please select a customer to assign this package'}), 400

        required_fields = {
            'package_id': 'Please select a package',
            'package_type': 'Package type is missing',
            'price_paid': 'Please enter the price paid'
        }

        for field, message in required_fields.items():
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': message}), 400

        # Get customer
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404

        # PAYMENT VALIDATION - Must be completed before assignment
        payment_method = data.get('payment_method')
        payment_status = data.get('payment_status')

        if not payment_method:
            return jsonify({'success': False, 'error': 'Payment method is required before assignment'}), 400

        if not payment_status:
            return jsonify({'success': False, 'error': 'Payment status is required before assignment'}), 400

        # Only allow assignment if payment is completed (paid or partial)
        if payment_status not in ['paid', 'partial']:
            return jsonify({'success': False, 'error': 'Package can only be assigned after payment is received. Please complete payment first.'}), 400

        # For partial payments, validate amount paid
        if payment_status == 'partial':
            amount_paid = data.get('amount_paid')
            if not amount_paid or float(amount_paid) <= 0:
                return jsonify({'success': False, 'error': 'Please enter the amount paid for partial payment'}), 400

        # Extract payment information
        amount_paid = float(data.get('amount_paid', data.get('price_paid', 0)))
        balance_due = float(data.get('balance_due', 0))
        transaction_ref = data.get('transaction_ref', '')

        # Create package assignment based on type
        package_type = data['package_type']
        package_id = data['package_id'] # Use package_id from data

        if package_type == 'membership':
            # Get membership details
            from models import Membership
            membership = Membership.query.get(package_id)
            if not membership:
                return jsonify({'success': False, 'error': 'Membership not found'}), 404

            # Calculate expiry date (membership validity in months)
            expiry_date = datetime.utcnow() + timedelta(days=membership.validity_months * 30)

            # Create assignment record for membership
            assignment = ServicePackageAssignment(
                customer_id=customer_id,
                package_type='membership',
                package_reference_id=membership.id,
                service_id=data.get('service_id'), # Optional for memberships
                assigned_on=datetime.utcnow(),
                expires_on=expiry_date,
                price_paid=float(data.get('price_paid', membership.price)),
                discount=float(data.get('discount', 0)),
                status='active',
                notes=f"Payment: {payment_method.upper()} | Status: {payment_status.upper()} | Amount Paid: ₹{amount_paid} | Balance: ₹{balance_due}" +
                      (f" | Ref: {transaction_ref}" if transaction_ref else "") +
                      (f"\n{data.get('notes', '')}" if data.get('notes') else ''),
                # Membership tracking
                total_sessions=0,
                used_sessions=0,
                remaining_sessions=0,
                credit_amount=0,
                used_credit=0,
                remaining_credit=0
            )

            logging.info(f"Creating membership assignment: customer_id={customer_id}, membership_id={membership.id}, expires_on={expiry_date}")

        elif package_type == 'prepaid':
            # Get prepaid package template
            prepaid = PrepaidPackage.query.get(data['package_id'])
            if not prepaid:
                return jsonify({'success': False, 'error': 'Prepaid package not found'}), 404

            # Calculate expiry date
            expiry_date = None
            if data.get('expiry_date'):
                expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d')
            else:
                expiry_date = datetime.utcnow() + timedelta(days=prepaid.validity_months * 30)

            # Create assignment record
            assignment = ServicePackageAssignment(
                customer_id=customer_id,
                package_type='prepaid',
                package_reference_id=prepaid.id,
                service_id=None,  # Prepaid packages are service-agnostic
                assigned_on=datetime.utcnow(),
                expires_on=expiry_date,
                price_paid=float(data['price_paid']),
                discount=float(data.get('discount', 0)),
                status='active',
                notes=data.get('notes', ''),
                # Prepaid uses credit tracking
                total_sessions=0,
                used_sessions=0,
                remaining_sessions=0,
                credit_amount=prepaid.after_value,
                used_credit=0,
                remaining_credit=prepaid.after_value
            )

        elif package_type == 'service_package':
            # Get service package template
            service_pkg = ServicePackage.query.get(data['package_id'])
            if not service_pkg:
                return jsonify({'success': False, 'error': 'Service package not found'}), 404

            # Service ID is required for service packages
            if not data.get('service_id'):
                return jsonify({'success': False, 'error': 'Service selection is required for service packages'}), 400

            # Calculate expiry date
            expiry_date = None
            if data.get('expiry_date'):
                expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d')
            elif service_pkg.validity_months:
                expiry_date = datetime.utcnow() + timedelta(days=service_pkg.validity_months * 30)

            # Create assignment record
            assignment = ServicePackageAssignment(
                customer_id=customer_id,
                package_type='service_package',
                package_reference_id=service_pkg.id,
                service_id=data['service_id'],
                assigned_on=datetime.utcnow(),
                expires_on=expiry_date,
                price_paid=float(data['price_paid']),
                discount=float(data.get('discount', 0)),
                status='active',
                notes=data.get('notes', ''),
                # Service package uses session tracking
                total_sessions=service_pkg.total_services,
                used_sessions=0,
                remaining_sessions=service_pkg.total_services,
                credit_amount=0,
                used_credit=0,
                remaining_credit=0
            )

        elif package_type == 'yearly' or package_type == 'yearly_membership':
            # Get yearly membership template
            yearly_membership = get_yearly_membership_by_id(data['package_id'])
            if not yearly_membership:
                return jsonify({'success': False, 'error': 'Yearly membership not found'}), 404

            # Calculate expiry date
            expiry_date = None
            if data.get('expires_on'):
                expiry_date = datetime.strptime(data['expires_on'], '%Y-%m-%d')
            elif yearly_membership.validity_months:
                expiry_date = datetime.utcnow() + timedelta(days=yearly_membership.validity_months * 30)

            # Create assignment record for yearly membership
            assignment = ServicePackageAssignment(
                customer_id=customer_id,
                package_type='yearly_membership',
                package_reference_id=yearly_membership.id,
                service_id=data.get('service_id'), # Optional for yearly memberships
                assigned_on=datetime.utcnow(),
                expires_on=expiry_date,
                price_paid=float(data['price_paid']),
                discount=float(data.get('discount', 0)),
                status='active',
                notes=data.get('notes', ''),
                # Yearly membership tracking
                total_sessions=0,
                used_sessions=0,
                remaining_sessions=0,
                credit_amount=0,
                used_credit=0,
                remaining_credit=0
            )
        elif package_type == 'student_offer':
            # Get student offer template
            student_offer = get_student_offer_by_id(data['package_id'])
            if not student_offer:
                return jsonify({'success': False, 'error': 'Student offer not found'}), 404

            # Calculate expiry date
            expiry_date = None
            if student_offer.valid_to:
                expiry_date = student_offer.valid_to
            elif data.get('expires_on'):
                expiry_date = datetime.strptime(data['expires_on'], '%Y-%m-%d')

            # Create assignment record for student offer
            assignment = ServicePackageAssignment(
                customer_id=customer_id,
                package_type='student_offer',
                package_reference_id=student_offer.id,
                service_id=data.get('service_id'), # Optional for student offers
                assigned_on=datetime.utcnow(),
                expires_on=expiry_date,
                price_paid=float(data['price_paid']),
                discount=float(data.get('discount', 0)),
                status='active',
                notes=data.get('notes', ''),
                # Student offer tracking
                total_sessions=0,
                used_sessions=0,
                remaining_sessions=0,
                credit_amount=0,
                used_credit=0,
                remaining_credit=0
            )
        elif package_type == 'kitty' or package_type == 'kitty_party':
            # Get kitty party template
            kitty_party = get_kitty_party_by_id(data['package_id'])
            if not kitty_party:
                return jsonify({'success': False, 'error': 'Kitty party not found'}), 404

            # Calculate expiry date
            expiry_date = None
            if kitty_party.valid_to:
                expiry_date = kitty_party.valid_to
            elif data.get('expires_on'):
                expiry_date = datetime.strptime(data['expires_on'], '%Y-%m-%d')

            # Create assignment record for kitty party
            assignment = ServicePackageAssignment(
                customer_id=customer_id,
                package_type='kitty_party',
                package_reference_id=kitty_party.id,
                service_id=data.get('service_id'), # Optional for kitty parties
                assigned_on=datetime.utcnow(),
                expires_on=expiry_date,
                price_paid=float(data['price_paid']),
                discount=float(data.get('discount', 0)),
                status='active',
                notes=data.get('notes', ''),
                # Kitty party tracking
                total_sessions=0,
                used_sessions=0,
                remaining_sessions=0,
                credit_amount=0,
                used_credit=0,
                remaining_credit=0
            )
        else:
            return jsonify({'success': False, 'error': f'Package type {package_type} not supported yet'}), 400

        db.session.add(assignment)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'{package_type.title()} assigned successfully to {customer.full_name}',
            'assignment_id': assignment.id
        })

    except Exception as e:
        logging.error(f"Error assigning package: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to assign package'}), 500

@app.route('/packages/api/assigned-customers/<package_type>/<int:package_id>', methods=['GET'])
@login_required
def get_assigned_customers(package_type, package_id):
    """Get list of customers assigned to a specific package"""
    try:
        # Map yearly to yearly_membership for compatibility
        actual_package_type = 'yearly_membership' if package_type == 'yearly' else package_type

        # Get assignments for the specified package
        assignments = ServicePackageAssignment.query.filter_by(
            package_type=actual_package_type,
            package_reference_id=package_id
        ).join(Customer).all()

        customers_list = []
        package_name = "" # Initialize package_name

        if assignments:
            customer = assignments[0].customer
            package_template = assignments[0].get_package_template()
            package_name = package_template.name if package_template else f"{package_type.title()} Package"

            for assignment in assignments:
                customer = assignment.customer # Get customer for each assignment

                customers_list.append({
                    'assignment_id': assignment.id,
                    'customer_id': customer.id,
                    'customer_name': customer.full_name,
                    'customer_phone': customer.phone or '',
                    'assigned_on': assignment.assigned_on.strftime('%Y-%m-%d'),
                    'expires_on': assignment.expires_on.strftime('%Y-%m-%d') if assignment.expires_on else 'No expiry',
                    'status': assignment.status,
                    'price_paid': float(assignment.price_paid),
                    'discount': float(assignment.discount),
                    'remaining_sessions': assignment.remaining_sessions if assignment.package_type == 'service_package' else None,
                    'remaining_credit': float(assignment.remaining_credit) if assignment.package_type == 'prepaid' else None,
                    'notes': assignment.notes or ''
                })
        else:
            # Get package name from template even if no assignments
            if package_type == 'yearly' or package_type == 'yearly_membership':
                yearly_membership = get_yearly_membership_by_id(package_id)
                package_name = yearly_membership.name if yearly_membership else f"{package_type.title()} Package"
            elif package_type == 'membership':
                membership = get_membership_by_id(package_id)
                package_name = membership.name if membership else f"{package_type.title()} Package"
            elif package_type == 'prepaid':
                prepaid = get_prepaid_package_by_id(package_id)
                package_name = prepaid.name if prepaid else f"{package_type.title()} Package"
            elif package_type == 'service_package':
                service_pkg = get_service_package_by_id(package_id)
                package_name = service_pkg.name if service_pkg else f"{package_type.title()} Package"

        return jsonify({
            'success': True,
            'package_name': package_name,
            'package_type': package_type,
            'total_assignments': len(customers_list),
            'customers': customers_list
        })

    except Exception as e:
        logging.error(f"Error getting assigned customers: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/packages/api/all-assignments', methods=['GET'])
@login_required
def get_all_package_assignments():
    """Get all package assignments for the main customer packages view"""
    try:
        # Get all assignments with customer and package details
        assignments = ServicePackageAssignment.query.join(Customer).order_by(
            ServicePackageAssignment.assigned_on.desc()
        ).all()

        assignments_list = []
        for assignment in assignments:
            customer = assignment.customer
            package_template = assignment.get_package_template()
            package_name = package_template.name if package_template else f"{assignment.package_type.title()} Package"

            # Calculate progress based on package type
            progress = 0
            if assignment.package_type == 'service_package' and assignment.total_sessions > 0:
                progress = (assignment.used_sessions / assignment.total_sessions) * 100
            elif assignment.package_type == 'prepaid' and assignment.credit_amount > 0:
                progress = (assignment.used_credit / assignment.credit_amount) * 100

            assignments_list.append({
                'assignment_id': assignment.id,
                'customer_id': customer.id,
                'customer_name': customer.full_name,
                'customer_phone': customer.phone or '',
                'package_id': assignment.package_reference_id,
                'package_name': package_name,
                'package_type': assignment.package_type,
                'assigned_on': assignment.assigned_on.strftime('%Y-%m-%d'),
                'expires_on': assignment.expires_on.strftime('%Y-%m-%d') if assignment.expires_on else 'No expiry',
                'status': assignment.status,
                'price_paid': float(assignment.price_paid),
                'discount': float(assignment.discount),
                'total_sessions': assignment.total_sessions,
                'used_sessions': assignment.used_sessions,
                'remaining_sessions': assignment.remaining_sessions,
                'credit_amount': float(assignment.credit_amount),
                'used_credit': float(assignment.used_credit),
                'remaining_credit': float(assignment.remaining_credit),
                'progress': round(progress, 1),
                'notes': assignment.notes or ''
            })

        return jsonify({
            'success': True,
            'total_assignments': len(assignments_list),
            'assignments': assignments_list
        })

    except Exception as e:
        logging.error(f"Error getting all assignments: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/packages/api/customers/<int:customer_id>', methods=['GET'])
@login_required
def api_get_customer_details(customer_id):
    """Get customer details by ID"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404

        customer_data = {
            'id': customer.id,
            'name': customer.full_name,
            'phone': customer.phone or '',
            'email': customer.email or '',
            'address': customer.address or '',
            'created_at': customer.created_at.strftime('%Y-%m-%d') if customer.created_at else 'N/A'
        }

        return jsonify({
            'success': True,
            'customer': customer_data
        })

    except Exception as e:
        logging.error(f"Error getting customer details: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/packages/api/view-assignment-details/<int:assignment_id>', methods=['GET'])
@login_required
def view_assignment_details(assignment_id):
    """View detailed information about a specific package assignment"""
    try:
        assignment = ServicePackageAssignment.query.get(assignment_id)
        if not assignment:
            return jsonify({'success': False, 'error': 'Assignment not found'}), 404

        customer = assignment.customer
        package_template = assignment.get_package_template()

        assignment_data = {
            'assignment_id': assignment.id,
            'customer': {
                'id': customer.id,
                'name': customer.full_name,
                'phone': customer.phone or '',
                'email': customer.email or ''
            },
            'package': {
                'id': assignment.package_reference_id,
                'name': package_template.name if package_template else f"{assignment.package_type.title()} Package",
                'type': assignment.package_type
            },
            'assignment_details': {
                'assigned_on': assignment.assigned_on.strftime('%Y-%m-%d'),
                'expires_on': assignment.expires_on.strftime('%Y-%m-%d') if assignment.expires_on else 'No expiry',
                'status': assignment.status,
                'price_paid': float(assignment.price_paid),
                'discount': float(assignment.discount),
                'notes': assignment.notes or ''
            },
            'usage_details': {
                'total_sessions': assignment.total_sessions,
                'used_sessions': assignment.used_sessions,
                'remaining_sessions': assignment.remaining_sessions,
                'credit_amount': float(assignment.credit_amount),
                'used_credit': float(assignment.used_credit),
                'remaining_credit': float(assignment.remaining_credit)
            }
        }

        # Render modal content
        from flask import render_template_string
        modal_html = render_template_string('''
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="fas fa-info-circle text-primary me-2"></i>Assignment Details
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Customer:</strong><br>
                        {{ assignment.customer.name }}<br>
                        <small class="text-muted">{{ assignment.customer.phone }}</small>
                    </div>
                    <div class="col-md-6">
                        <strong>Package:</strong><br>
                        {{ assignment.package.name }}<br>
                        <span class="badge bg-secondary">{{ assignment.package.type }}</span>
                    </div>
                </div>

                <div class="row mb-3">
                    <div class="col-md-3">
                        <strong>Assigned:</strong><br>
                        {{ assignment.assignment_details.assigned_on }}
                    </div>
                    <div class="col-md-3">
                        <strong>Expires:</strong><br>
                        {{ assignment.assignment_details.expires_on }}
                    </div>
                    <div class="col-md-3">
                        <strong>Price Paid:</strong><br>
                        ₹{{ "%.2f"|format(assignment.assignment_details.price_paid) }}
                    </div>
                    <div class="col-md-3">
                        <strong>Status:</strong><br>
                        <span class="badge bg-success">{{ assignment.assignment_details.status }}</span>
                    </div>
                </div>

                {% if assignment.usage_details.total_sessions > 0 %}
                <div class="row mb-3">
                    <div class="col-12">
                        <strong>Usage Summary:</strong><br>
                        Sessions: {{ assignment.usage_details.used_sessions }} / {{ assignment.usage_details.total_sessions }}
                        ({{ assignment.usage_details.remaining_sessions }} remaining)
                    </div>
                </div>
                {% endif %}

                {% if assignment.usage_details.credit_amount > 0 %}
                <div class="row mb-3">
                    <div class="col-12">
                        <strong>Credit Summary:</strong><br>
                        Used: ₹{{ "%.2f"|format(assignment.usage_details.used_credit) }} / ₹{{ "%.2f"|format(assignment.usage_details.credit_amount) }}
                        (₹{{ "%.2f"|format(assignment.usage_details.remaining_credit) }} remaining)
                    </div>
                </div>
                {% endif %}

                {% if assignment.assignment_details.notes %}
                <div class="row">
                    <div class="col-12">
                        <strong>Notes:</strong><br>
                        {{ assignment.assignment_details.notes }}
                    </div>
                </div>
                {% endif %}
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        ''', assignment=assignment_data)

        return jsonify({
            'success': True,
            'html': modal_html,
            'assignment': assignment_data
        })

    except Exception as e:
        logging.error(f"Error getting assignment details: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ========================================
# PACKAGE ASSIGNMENT PAGE
# ========================================

@app.route('/packages/assign/<package_type>/<int:package_id>')
@login_required
def assign_package_page(package_type, package_id):
    """New dedicated page for package assignment"""
    if not hasattr(current_user, 'can_access') or not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        # Get package details based on type
        package_data = None
        if package_type == 'membership':
            package_data = get_membership_by_id(package_id)
        elif package_type == 'student':
            package_data = get_student_offer_by_id(package_id)
        elif package_type == 'yearly':
            package_data = get_yearly_membership_by_id(package_id)
        elif package_type == 'kitty':
            package_data = get_kitty_party_by_id(package_id)

        if not package_data:
            flash('Package not found', 'danger')
            return redirect(url_for('packages'))

        # Get all customers for the dropdown
        customers = Customer.query.filter_by(is_active=True).order_by(Customer.first_name, Customer.last_name).all()

        return render_template('packages/assign_package.html',
                             package=package_data,
                             package_type=package_type,
                             customers=customers)

    except Exception as e:
        logger.error(f"Error loading assignment page: {e}")
        flash('Error loading assignment page', 'danger')
        return redirect(url_for('packages'))