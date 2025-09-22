"""
Customer Packages Routes - Blueprint for package assignment, usage tracking, and management
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from models import Service, Customer, User, Appointment
from models import PackageTemplate, PackageTemplateItem, CustomerPackage, CustomerPackageItem, PackageUsage
from datetime import datetime
from sqlalchemy import and_, or_, desc
from sqlalchemy.exc import IntegrityError
import logging

# Create blueprint
packages_bp = Blueprint("packages", __name__, url_prefix="/packages")

# ========================================
# MAIN PAGE ROUTE
# ========================================

@packages_bp.route("/", endpoint="index")
@login_required
def index():
    """Main customer packages page"""
    if hasattr(current_user, 'can_access') and not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    return render_template("packages/customer_packages.html")


@packages_bp.route("/student-offers/add", endpoint="add_student_offer")
@login_required
def add_student_offer():
    """Add student offer page"""
    if hasattr(current_user, 'can_access') and not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    return render_template("packages/add_student_offer.html")


@packages_bp.route("/student-offers/edit", endpoint="edit_student_offer")
@login_required
def edit_student_offer():
    """Edit student offer page"""
    if hasattr(current_user, 'can_access') and not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    return render_template("packages/edit_student_offer.html")


# ========================================
# PACKAGE TEMPLATES API
# ========================================

@packages_bp.route("/api/templates", methods=['GET'])
@login_required
def api_get_templates():
    """Get all package templates with items"""
    try:
        templates = PackageTemplate.query.filter_by(is_active=True).all()

        result = []
        for template in templates:
            template_data = {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'pkg_type': template.pkg_type,
                'price': float(template.price),
                'is_active': template.is_active,
                'created_at': template.created_at.isoformat(),
                'items': []
            }

            # Add template items
            for item in template.template_items:
                template_data['items'].append({
                    'id': item.id,
                    'service_id': item.service_id,
                    'service_name': item.service.name if item.service else '',
                    'qty': item.qty
                })

            result.append(template_data)

        return jsonify({'success': True, 'templates': result})

    except Exception as e:
        logging.error(f"Error getting package templates: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ========================================
# CUSTOMER PACKAGES API
# ========================================

@packages_bp.route("/api/assign", methods=['POST'])
@login_required
def api_assign_package():
    """Assign package to customer"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['customer_id', 'package_id', 'price_paid']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400

        # Check if customer exists
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404

        # Check if package template exists
        template = PackageTemplate.query.get(data['package_id'])
        if not template:
            return jsonify({'success': False, 'error': 'Package template not found'}), 404

        # Parse expires_on if provided
        expires_on = None
        if data.get('expires_on'):
            try:
                expires_on = datetime.fromisoformat(data['expires_on'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid expires_on date format'}), 400

        # Create customer package
        customer_package = CustomerPackage(
            customer_id=data['customer_id'],
            package_id=data['package_id'],
            price_paid=data['price_paid'],
            discount=data.get('discount', 0),
            expires_on=expires_on,
            notes=data.get('notes', '')
        )

        db.session.add(customer_package)
        db.session.flush()  # To get the ID

        # Create customer package items from template items
        for template_item in template.template_items:
            package_item = CustomerPackageItem(
                customer_package_id=customer_package.id,
                service_id=template_item.service_id,
                total_qty=template_item.qty,
                used_qty=0
            )
            db.session.add(package_item)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Package assigned successfully',
            'customer_package_id': customer_package.id
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error assigning package: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@packages_bp.route("/api/customer-packages", methods=['GET'])
@login_required
def api_get_customer_packages():
    """Get customer packages with filters"""
    try:
        # Get query parameters
        customer_id = request.args.get('customer_id', type=int)
        status = request.args.get('status')
        q = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Build query
        query = CustomerPackage.query.join(Customer).join(PackageTemplate)

        # Apply filters
        if customer_id:
            query = query.filter(CustomerPackage.customer_id == customer_id)

        if status:
            query = query.filter(CustomerPackage.status == status)

        if q:
            query = query.filter(
                or_(
                    Customer.first_name.ilike(f'%{q}%'),
                    Customer.last_name.ilike(f'%{q}%'),
                    PackageTemplate.name.ilike(f'%{q}%')
                )
            )

        # Order by assigned date (newest first)
        query = query.order_by(desc(CustomerPackage.assigned_on))

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        packages = pagination.items

        # Format results
        result = []
        for pkg in packages:
            # Auto-update status
            pkg.auto_update_status()

            result.append({
                'id': pkg.id,
                'customer_id': pkg.customer_id,
                'customer_name': pkg.customer.full_name,
                'package_name': pkg.package_template.name,
                'assigned_on': pkg.assigned_on.strftime('%Y-%m-%d'),
                'expires_on': pkg.expires_on.strftime('%Y-%m-%d') if pkg.expires_on else None,
                'price_paid': float(pkg.price_paid),
                'discount': float(pkg.discount),
                'status': pkg.status,
                'total_services': pkg.get_total_services(),
                'used_services': pkg.get_used_services(),
                'remaining_services': pkg.get_remaining_services(),
                'usage_percentage': pkg.get_usage_percentage(),
                'notes': pkg.notes
            })

        # Commit any status updates
        db.session.commit()

        return jsonify({
            'success': True,
            'packages': result,
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })

    except Exception as e:
        logging.error(f"Error getting customer packages: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@packages_bp.route("/api/customer-packages/<int:package_id>", methods=['GET'])
@login_required
def api_get_package_details(package_id):
    """Get package details with items and recent usage"""
    try:
        package = CustomerPackage.query.get(package_id)
        if not package:
            return jsonify({'success': False, 'error': 'Package not found'}), 404

        # Auto-update status
        package.auto_update_status()
        db.session.commit()

        # Get package items
        items = []
        for item in package.package_items:
            items.append({
                'id': item.id,
                'service_id': item.service_id,
                'service_name': item.service.name if item.service else '',
                'total_qty': item.total_qty,
                'used_qty': item.used_qty,
                'remaining_qty': item.get_remaining_qty()
            })

        # Get recent usage (last 10)
        recent_usage = PackageUsage.query.filter_by(customer_package_id=package_id)\
            .order_by(desc(PackageUsage.usage_date)).limit(10).all()

        usage_list = []
        for usage in recent_usage:
            usage_list.append({
                'id': usage.id,
                'usage_date': usage.usage_date.strftime('%Y-%m-%d %H:%M'),
                'service_name': usage.service.name if usage.service else '',
                'qty': usage.qty,
                'change_type': usage.change_type,
                'staff_name': usage.staff.full_name if usage.staff else '',
                'notes': usage.notes
            })

        result = {
            'id': package.id,
            'customer_id': package.customer_id,
            'customer_name': package.customer.full_name,
            'package_name': package.package_template.name,
            'assigned_on': package.assigned_on.strftime('%Y-%m-%d'),
            'expires_on': package.expires_on.strftime('%Y-%m-%d') if package.expires_on else None,
            'price_paid': float(package.price_paid),
            'discount': float(package.discount),
            'status': package.status,
            'notes': package.notes,
            'total_services': package.get_total_services(),
            'used_services': package.get_used_services(),
            'remaining_services': package.get_remaining_services(),
            'usage_percentage': package.get_usage_percentage(),
            'items': items,
            'recent_usage': usage_list
        }

        return jsonify({'success': True, 'package': result})

    except Exception as e:
        logging.error(f"Error getting package details: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@packages_bp.route("/api/customer-packages/<int:package_id>/usage", methods=['GET'])
@login_required
def api_get_package_usage(package_id):
    """Get paged usage list for package"""
    try:
        package = CustomerPackage.query.get(package_id)
        if not package:
            return jsonify({'success': False, 'error': 'Package not found'}), 404

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Get usage with pagination
        pagination = PackageUsage.query.filter_by(customer_package_id=package_id)\
            .order_by(desc(PackageUsage.usage_date))\
            .paginate(page=page, per_page=per_page, error_out=False)

        usage_list = []
        for usage in pagination.items:
            usage_list.append({
                'id': usage.id,
                'usage_date': usage.usage_date.strftime('%Y-%m-%d %H:%M'),
                'service_name': usage.service.name if usage.service else '',
                'qty': usage.qty,
                'change_type': usage.change_type,
                'staff_name': usage.staff.full_name if usage.staff else '',
                'appointment_id': usage.appointment_id,
                'notes': usage.notes
            })

        return jsonify({
            'success': True,
            'usage': usage_list,
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })

    except Exception as e:
        logging.error(f"Error getting package usage: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@packages_bp.route("/api/customer-packages/<int:package_id>/use", methods=['POST'])
@login_required
def api_use_package(package_id):
    """Record package usage"""
    try:
        package = CustomerPackage.query.get(package_id)
        if not package:
            return jsonify({'success': False, 'error': 'Package not found'}), 404

        data = request.get_json()

        # Validate required fields
        required_fields = ['service_id', 'qty']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400

        if data['qty'] <= 0:
            return jsonify({'success': False, 'error': 'Please provide a valid quantity'}), 400

        # Check package is active
        if package.status != 'active':
            return jsonify({'success': False, 'error': 'Package is not active'}), 409

        # Check if expired
        if package.is_expired():
            package.status = 'expired'
            db.session.commit()
            return jsonify({'success': False, 'error': 'Package has expired'}), 409

        # Find package item for service
        package_item = CustomerPackageItem.query.filter_by(
            customer_package_id=package_id,
            service_id=data['service_id']
        ).first()

        if not package_item:
            return jsonify({'success': False, 'error': 'Service not included in package'}), 404

        # Check if enough balance
        if not package_item.can_use(data['qty']):
            return jsonify({'success': False, 'error': 'Not enough balance for this service'}), 409

        # Parse usage date
        usage_date = datetime.utcnow()
        if data.get('usage_date'):
            try:
                usage_date = datetime.fromisoformat(data['usage_date'].replace('Z', '+00:00'))
            except ValueError:
                pass  # Use current time if invalid format

        # Record usage
        package_item.use_services(data['qty'])

        # Create usage log
        usage_log = PackageUsage(
            customer_package_id=package_id,
            customer_package_item_id=package_item.id,
            usage_date=usage_date,
            service_id=data['service_id'],
            qty=data['qty'],
            change_type='use',
            staff_id=data.get('staff_id'),
            appointment_id=data.get('appointment_id'),
            notes=data.get('notes', '')
        )

        db.session.add(usage_log)

        # Auto-update package status
        package.auto_update_status()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Usage recorded successfully',
            'remaining_qty': package_item.get_remaining_qty()
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error recording package usage: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@packages_bp.route("/api/customer-packages/<int:package_id>/adjust", methods=['POST'])
@login_required
def api_adjust_package(package_id):
    """Adjust or refund package"""
    try:
        package = CustomerPackage.query.get(package_id)
        if not package:
            return jsonify({'success': False, 'error': 'Package not found'}), 404

        data = request.get_json()

        # Validate required fields
        required_fields = ['service_id', 'qty', 'reason', 'change_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400

        if data['qty'] <= 0:
            return jsonify({'success': False, 'error': 'Please provide a valid quantity'}), 400

        if data['change_type'] not in ['refund', 'adjust']:
            return jsonify({'success': False, 'error': 'Invalid change type'}), 400

        # Find package item for service
        package_item = CustomerPackageItem.query.filter_by(
            customer_package_id=package_id,
            service_id=data['service_id']
        ).first()

        if not package_item:
            return jsonify({'success': False, 'error': 'Service not included in package'}), 404

        # Perform adjustment
        success = False
        if data['change_type'] == 'refund':
            # Refund: add back qty to available services
            success = package_item.refund_services(data['qty'])
            if not success:
                return jsonify({'success': False, 'error': 'Cannot refund more than used'}), 409
        else:  # adjust
            # Adjust: modify total quantity (can be positive or negative)
            qty_change = data['qty'] if data.get('positive_adjustment', True) else -data['qty']
            success = package_item.adjust_services(qty_change)
            if not success:
                return jsonify({'success': False, 'error': 'Adjustment would result in negative remaining balance'}), 409

        # Create usage log
        usage_log = PackageUsage(
            customer_package_id=package_id,
            customer_package_item_id=package_item.id,
            usage_date=datetime.utcnow(),
            service_id=data['service_id'],
            qty=data['qty'],
            change_type=data['change_type'],
            staff_id=current_user.id,
            notes=f"{data['change_type'].title()}: {data['reason']}"
        )

        db.session.add(usage_log)

        # Auto-update package status
        package.auto_update_status()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'{data["change_type"].title()} processed successfully',
            'new_remaining_qty': package_item.get_remaining_qty()
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adjusting package: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ========================================
# UTILITY ENDPOINTS
# ========================================

@packages_bp.route("/api/customers", methods=['GET'])
@login_required
def api_get_customers():
    """Get all customers for assignment"""
    try:
        customers = Customer.query.filter_by(is_active=True).order_by(Customer.first_name).all()

        result = []
        for customer in customers:
            result.append({
                'id': customer.id,
                'name': customer.full_name,
                'phone': customer.phone,
                'email': customer.email
            })

        return jsonify({'success': True, 'customers': result})

    except Exception as e:
        logging.error(f"Error getting customers: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@packages_bp.route("/api/services", methods=['GET'])
@login_required
def api_get_services():
    """Get all services for usage tracking"""
    try:
        services = Service.query.filter_by(is_active=True).order_by(Service.name).all()

        result = []
        for service in services:
            result.append({
                'id': service.id,
                'name': service.name,
                'price': float(service.price)
            })

        return jsonify({'success': True, 'services': result})

    except Exception as e:
        logging.error(f"Error getting services: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@packages_bp.route("/api/staff", methods=['GET'])
@login_required
def api_get_staff():
    """Get all staff for usage tracking"""
    try:
        staff = User.query.filter_by(is_active=True).order_by(User.first_name).all()

        result = []
        for member in staff:
            result.append({
                'id': member.id,
                'name': member.full_name,
                'role': member.role.name if member.role else 'Staff'
            })

        return jsonify({'success': True, 'staff': result})

    except Exception as e:
        logging.error(f"Error getting staff: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500