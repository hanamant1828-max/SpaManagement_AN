"""
Customer Packages API - JSON endpoints for customer package management
This file provides additional API utilities and helpers for the packages system
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from models import Customer, Service, PrepaidPackage, ServicePackage, Membership, User, CustomerPackage, StudentOffer, StudentOfferService
import datetime
from sqlalchemy import and_, or_, desc, func
import logging

def format_package_data(package):
    """Format package data for API response"""
    try:
        # Auto-update status
        package.auto_update_status()

        return {
            'id': package.id,
            'customer_id': package.customer_id,
            'customer_name': package.customer.full_name,
            'package_name': package.package_template.name,
            'assigned_on': package.assigned_on.strftime('%Y-%m-%d'),
            'expires_on': package.expires_on.strftime('%Y-%m-%d') if package.expires_on else None,
            'price_paid': float(package.price_paid),
            'discount': float(package.discount),
            'status': package.status,
            'total_services': package.get_total_services(),
            'used_services': package.get_used_services(),
            'remaining_services': package.get_remaining_services(),
            'usage_percentage': package.get_usage_percentage(),
            'notes': package.notes
        }
    except Exception as e:
        logging.error(f"Error formatting package data: {e}")
        return {}

def format_package_item_data(item):
    """Format package item data for API response"""
    try:
        return {
            'id': item.id,
            'service_id': item.service_id,
            'service_name': item.service.name if item.service else '',
            'total_qty': item.total_qty,
            'used_qty': item.used_qty,
            'remaining_qty': item.get_remaining_qty(),
            'can_use': item.get_remaining_qty() > 0
        }
    except Exception as e:
        logging.error(f"Error formatting package item data: {e}")
        return {}

def format_usage_data(usage):
    """Format usage data for API response"""
    try:
        return {
            'id': usage.id,
            'usage_date': usage.usage_date.strftime('%Y-%m-%d %H:%M'),
            'service_name': usage.service.name if usage.service else '',
            'qty': usage.qty,
            'change_type': usage.change_type,
            'staff_name': usage.staff.full_name if usage.staff else '',
            'appointment_id': usage.appointment_id,
            'notes': usage.notes
        }
    except Exception as e:
        logging.error(f"Error formatting usage data: {e}")
        return {}

def validate_package_assignment_data(data):
    """Validate data for package assignment"""
    errors = []

    # Required fields
    required_fields = ['customer_id', 'package_id', 'price_paid']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f'{field} is required')

    # Validate numeric fields
    if 'price_paid' in data:
        try:
            float(data['price_paid'])
        except (ValueError, TypeError):
            errors.append('price_paid must be a valid number')

    if 'discount' in data and data['discount']:
        try:
            float(data['discount'])
        except (ValueError, TypeError):
            errors.append('discount must be a valid number')

    # Validate IDs exist
    if 'customer_id' in data:
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            errors.append('Customer not found')

    if 'package_id' in data:
        template = PackageTemplate.query.get(data['package_id'])
        if not template:
            errors.append('Package template not found')
        elif not template.is_active:
            errors.append('Package template is not active')

    return errors

def validate_usage_data(data):
    """Validate data for package usage"""
    errors = []

    # Required fields
    required_fields = ['service_id', 'qty']
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f'{field} is required')

    # Validate quantity
    if 'qty' in data:
        try:
            qty = int(data['qty'])
            if qty <= 0:
                errors.append('quantity must be greater than 0')
        except (ValueError, TypeError):
            errors.append('quantity must be a valid integer')

    # Validate service exists
    if 'service_id' in data:
        service = Service.query.get(data['service_id'])
        if not service:
            errors.append('Service not found')
        elif not service.is_active:
            errors.append('Service is not active')

    # Validate staff if provided
    if data.get('staff_id'):
        staff = User.query.get(data['staff_id'])
        if not staff:
            errors.append('Staff member not found')
        elif not staff.is_active:
            errors.append('Staff member is not active')

    return errors

def validate_adjustment_data(data):
    """Validate data for package adjustment"""
    errors = []

    # Required fields
    required_fields = ['service_id', 'qty', 'reason', 'change_type']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f'{field} is required')

    # Validate change type
    if 'change_type' in data and data['change_type'] not in ['refund', 'adjust']:
        errors.append('change_type must be either "refund" or "adjust"')

    # Validate quantity
    if 'qty' in data:
        try:
            qty = int(data['qty'])
            if qty <= 0:
                errors.append('quantity must be greater than 0')
        except (ValueError, TypeError):
            errors.append('quantity must be a valid integer')

    # Validate service exists
    if 'service_id' in data:
        service = Service.query.get(data['service_id'])
        if not service:
            errors.append('Service not found')

    return errors

def get_package_statistics():
    """Get package statistics for dashboard"""
    try:
        from app import db

        stats = {
            'total_packages': CustomerPackage.query.count(),
            'active_packages': CustomerPackage.query.filter_by(status='active').count(),
            'completed_packages': CustomerPackage.query.filter_by(status='completed').count(),
            'expired_packages': CustomerPackage.query.filter_by(status='expired').count(),
            'total_revenue': 0,
            'total_services_sold': 0,
            'total_services_used': 0
        }

        # Calculate revenue
        revenue_result = db.session.query(func.sum(CustomerPackage.price_paid)).scalar()
        stats['total_revenue'] = float(revenue_result) if revenue_result else 0

        # Calculate services
        services_result = db.session.query(
            func.sum(CustomerPackageItem.total_qty),
            func.sum(CustomerPackageItem.used_qty)
        ).first()

        if services_result and services_result[0]:
            stats['total_services_sold'] = int(services_result[0])
            stats['total_services_used'] = int(services_result[1]) if services_result[1] else 0

        return stats

    except Exception as e:
        logging.error(f"Error getting package statistics: {e}")
        return {
            'total_packages': 0,
            'active_packages': 0,
            'completed_packages': 0,
            'expired_packages': 0,
            'total_revenue': 0,
            'total_services_sold': 0,
            'total_services_used': 0
        }

def build_package_filters(args):
    """Build database filters from query arguments"""
    filters = []

    # Customer filter
    if args.get('customer_id'):
        filters.append(CustomerPackage.customer_id == args['customer_id'])

    # Status filter
    if args.get('status'):
        filters.append(CustomerPackage.status == args['status'])

    # Date range filters
    if args.get('date_from'):
        try:
            date_from = datetime.strptime(args['date_from'], '%Y-%m-%d')
            filters.append(CustomerPackage.assigned_on >= date_from)
        except ValueError:
            pass

    if args.get('date_to'):
        try:
            date_to = datetime.strptime(args['date_to'], '%Y-%m-%d')
            # Add one day to include the entire day
            date_to = date_to.replace(hour=23, minute=59, second=59)
            filters.append(CustomerPackage.assigned_on <= date_to)
        except ValueError:
            pass

    return filters

def check_package_permissions(user, action, package=None):
    """Check if user has permission for package action"""
    if not hasattr(user, 'can_access'):
        return False

    # Basic package access
    if not user.can_access('packages'):
        return False

    # Action-specific permissions
    if action == 'create':
        return user.has_role('admin') or user.has_role('manager')
    elif action == 'edit':
        return user.has_role('admin') or user.has_role('manager')
    elif action == 'delete':
        return user.has_role('admin')
    elif action == 'use':
        return True  # All package users can record usage
    elif action == 'adjust':
        return user.has_role('admin') or user.has_role('manager')

    return True

def create_success_response(message, data=None):
    """Create standardized success response"""
    response = {'success': True, 'message': message}
    if data:
        response.update(data)
    return jsonify(response)

def create_error_response(error, status_code=400):
    """Create standardized error response"""
    # Map common errors to user-friendly messages
    friendly_messages = {
        'Package not found': 'Package not found.',
        'Customer not found': 'Customer not found.',
        'Service not found': 'Service not found.',
        'Not enough balance': 'Not enough balance for this service.',
        'Invalid quantity': 'Please provide a valid quantity.',
        'Package expired': 'This package has expired.',
        'Package not active': 'This package is not active.'
    }

    friendly_error = friendly_messages.get(error, error)
    return jsonify({'success': False, 'error': friendly_error}), status_code

# Create the blueprint if it doesn't exist
from flask import Blueprint
packages_api = Blueprint('packages_api', __name__, url_prefix='/packages/api')

@packages_api.route('/service-packages', methods=['POST'])
@login_required
def create_service_package():
    """Create a new service package"""
    try:
        # Get form data
        name = request.form.get('name')
        pay_for = int(request.form.get('pay_for', 0))
        total_services = int(request.form.get('total_services', 0))
        free_services = int(request.form.get('free_services', 0))
        benefit_percentage = float(request.form.get('benefit_percentage', 0))
        validity_months = int(request.form.get('validity_months', 12))

        # Validate required fields
        if not name or pay_for <= 0 or total_services <= 0:
            return jsonify({
                'success': False,
                'message': 'Please provide valid package name, pay for amount, and total services'
            }), 400

        # Create service package
        service_package = ServicePackage(
            name=name,
            pay_for=pay_for,
            total_services=total_services,
            free_services=free_services,
            benefit_percentage=benefit_percentage,
            validity_months=validity_months,
            is_active=True,
            created_by=current_user.id,
            created_at=datetime.datetime.now()
        )

        db.session.add(service_package)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Service package created successfully',
            'package_id': service_package.id
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'message': 'Invalid input values provided'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating service package: {str(e)}'
        }), 500

@packages_api.route('/assign', methods=['POST'])
@login_required
def assign_package():
    """Assign a package to a customer"""
    try:
        data = request.get_json()

        customer_id = data.get('customer_id')
        package_id = data.get('package_id')
        package_type = data.get('package_type', 'student_offer')
        price_paid = data.get('price_paid', 0.0)
        notes = data.get('notes', '')

        if not customer_id or not package_id:
            return jsonify({
                'success': False,
                'error': 'Customer ID and Package ID are required'
            }), 400

        # Verify customer exists
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({
                'success': False,
                'error': 'Customer not found'
            }), 404

        # Handle student offer assignment
        if package_type == 'student_offer':
            # Verify student offer exists
            student_offer = StudentOffer.query.get(package_id)
            if not student_offer:
                return jsonify({
                    'success': False,
                    'error': 'Student offer not found'
                }), 404

            # Create customer package assignment
            customer_package = CustomerPackage(
                customer_id=customer_id,
                package_name=f'Student Offer - {student_offer.discount_percentage}% Discount',
                package_type='student_offer',
                package_reference_id=package_id,
                total_amount=price_paid,
                paid_amount=price_paid,
                status='active',
                notes=notes,
                created_by=current_user.id,
                created_at=datetime.utcnow()
            )

            db.session.add(customer_package)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Student offer assigned successfully',
                'assignment_id': customer_package.id
            })

        else:
            return jsonify({
                'success': False,
                'error': 'Unsupported package type'
            }), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Assignment error: {str(e)}'
        }), 500

@packages_api.route('/customers', methods=['GET'])
@login_required
def get_customers():
    """Get all customers for assignment"""
    try:
        customers = Customer.query.filter_by(is_active=True).all()

        customers_data = []
        for customer in customers:
            customers_data.append({
                'id': customer.id,
                'name': f"{customer.first_name} {customer.last_name}".strip(),
                'email': customer.email,
                'phone': customer.phone,
                'created_at': customer.created_at.isoformat() if customer.created_at else None
            })

        return jsonify({
            'success': True,
            'customers': customers_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error loading customers: {str(e)}'
        }), 500