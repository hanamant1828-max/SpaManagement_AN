"""
Customer Packages API - JSON endpoints for customer package management
This file provides additional API utilities and helpers for the packages system
"""
from flask import jsonify
from models import PackageTemplate, CustomerPackage, CustomerPackageItem, PackageUsage
from models import Service, Customer, User
from datetime import datetime
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