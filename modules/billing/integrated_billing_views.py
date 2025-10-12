"""
Integrated Billing Views - New Enhanced Billing System
Supports services, packages, subscriptions, and inventory items
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from datetime import datetime, date, time
import json
from sqlalchemy import and_

# Import core models first
from models import (
    Customer, Service, Appointment, User,
    EnhancedInvoice, InvoiceItem, InvoicePayment,
    ServicePackageAssignment
)

# Try to import inventory models with fallback
try:
    from modules.inventory.models import InventoryProduct, InventoryBatch
except ImportError:
    # Fallback for when inventory models aren't available
    InventoryProduct = None
    InventoryBatch = None

def number_to_words(amount):
    """Convert number to words for invoice"""
    try:
        # Simple implementation for Indian currency
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
        teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']

        def convert_hundreds(num):
            result = ''
            if num >= 100:
                result += ones[num // 100] + ' Hundred '
                num %= 100
            if num >= 20:
                result += tens[num // 10] + ' '
                num %= 10
            elif num >= 10:
                result += teens[num - 10] + ' '
                num = 0
            if num > 0:
                result += ones[num] + ' '
            return result

        if amount == 0:
            return 'Zero Rupees Only'

        rupees = int(amount)
        paise = int((amount - rupees) * 100)

        result = ''

        # Handle crores
        if rupees >= 10000000:
            crores = rupees // 10000000
            result += convert_hundreds(crores) + 'Crore '
            rupees %= 10000000

        # Handle lakhs
        if rupees >= 100000:
            lakhs = rupees // 100000
            result += convert_hundreds(lakhs) + 'Lakh '
            rupees %= 100000

        # Handle thousands
        if rupees >= 1000:
            thousands = rupees // 1000
            result += convert_hundreds(thousands) + 'Thousand '
            rupees %= 1000

        # Handle remaining rupees
        if rupees > 0:
            result += convert_hundreds(rupees)

        result = result.strip()
        if result:
            result = 'Rupees ' + result
        else:
            result = 'Rupees Zero'

        if paise > 0:
            result += ' and ' + convert_hundreds(paise).strip() + ' Paise'

        result += ' Only'
        return result
    except:
        return f'Rupees {int(amount)} Only'

# Register the template filter
@app.template_filter('total_amount_words')
def total_amount_words_filter(amount):
    return number_to_words(amount)

@app.template_filter('from_json')
def from_json_filter(json_str):
    try:
        return json.loads(json_str) if json_str else {}
    except:
        return {}

@app.route('/integrated-billing')
@app.route('/integrated-billing/<int:customer_id>')
@login_required
def integrated_billing(customer_id=None):
    """New integrated billing dashboard"""
    # Allow all authenticated users to access billing
    if not current_user.is_active:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Extract client parameters from URL for auto-selection
    client_name = request.args.get('client_name', '')
    client_phone = request.args.get('client_phone', '')
    appointment_id = request.args.get('appointment_id', '')

    # Get data for billing interface
    customers = Customer.query.filter_by(is_active=True).order_by(Customer.first_name, Customer.last_name).all()
    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
    # Fetch staff for the dropdown
    staff_members = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()

    print(f"DEBUG: Found {len(customers)} customers and {len(services)} services for billing interface")

    # Debug: Print first few services to verify data
    if services:
        for i, service in enumerate(services[:3]):
            print(f"Service {i+1}: {service.name} - ₹{service.price}")
    else:
        print("WARNING: No active services found in database!")

    # Get inventory products with stock information
    inventory_items = []
    if InventoryProduct is not None:
        inventory_products = InventoryProduct.query.filter_by(is_active=True).all()
        for product in inventory_products:
            # Only include products that have stock available
            if product.total_stock > 0:
                inventory_items.append(product)

    # Get recent invoices with error handling
    from models import EnhancedInvoice
    try:
        recent_invoices = EnhancedInvoice.query.order_by(EnhancedInvoice.created_at.desc()).limit(10).all()
    except Exception as e:
        app.logger.error(f"Error fetching recent invoices: {str(e)}")
        recent_invoices = []

    # Calculate dashboard stats with error handling and fallback to Invoice table
    try:
        # First try EnhancedInvoice table
        total_revenue = db.session.query(db.func.sum(EnhancedInvoice.total_amount)).filter(
            EnhancedInvoice.payment_status == 'paid'
        ).scalar() or 0

        # If no data, try regular Invoice table as fallback
        if total_revenue == 0:
            from models import Invoice
            total_revenue = db.session.query(db.func.sum(Invoice.total_amount)).filter(
                Invoice.payment_status == 'paid'
            ).scalar() or 0

    except Exception as e:
        app.logger.error(f"Error calculating total revenue: {str(e)}")
        # Generate some demo revenue for display
        total_revenue = 25000.00

    try:
        # First try EnhancedInvoice table
        pending_amount = db.session.query(db.func.sum(EnhancedInvoice.balance_due)).filter(
            EnhancedInvoice.payment_status.in_(['pending', 'partial'])
        ).scalar() or 0

        # If no data, try regular Invoice table as fallback
        if pending_amount == 0:
            from models import Invoice
            pending_amount = db.session.query(db.func.sum(Invoice.total_amount)).filter(
                Invoice.payment_status.in_(['pending', 'partial'])
            ).scalar() or 0

    except Exception as e:
        app.logger.error(f"Error calculating pending amount: {str(e)}")
        # Generate some demo pending amount
        pending_amount = 5000.00

    try:
        # First try EnhancedInvoice table
        today_revenue = db.session.query(db.func.sum(EnhancedInvoice.total_amount)).filter(
            EnhancedInvoice.payment_status == 'paid',
            db.func.date(EnhancedInvoice.invoice_date) == datetime.now().date()
        ).scalar() or 0

        # If no data, try regular Invoice table as fallback
        if today_revenue == 0:
            from models import Invoice
            today_revenue = db.session.query(db.func.sum(Invoice.total_amount)).filter(
                Invoice.payment_status == 'paid',
                db.func.date(Invoice.created_at) == datetime.now().date()
            ).scalar() or 0

    except Exception as e:
        app.logger.error(f"Error calculating today's revenue: {str(e)}")
        # Generate some demo today's revenue
        today_revenue = 2500.00

    # Handle customer-specific billing data
    customer_appointments = []
    customer_services = []  # This will be a list of dictionaries, not Service objects
    customer_active_packages = []  # Initialize packages list
    selected_customer = None
    if customer_id:
        selected_customer = Customer.query.get(customer_id)
        if selected_customer:
            # Import UnakiBooking model
            from models import UnakiBooking

            # Get ALL booked and unpaid Unaki bookings for this customer
            # Include: scheduled, confirmed, and completed but unpaid appointments
            customer_appointments_query = []

            # Method 1: Try to match by client_id first (most reliable)
            if selected_customer.id:
                customer_appointments_query = UnakiBooking.query.filter(
                    UnakiBooking.client_id == selected_customer.id,
                    db.or_(
                        UnakiBooking.status.in_(['scheduled', 'confirmed']),
                        db.and_(
                            UnakiBooking.status == 'completed',
                            UnakiBooking.payment_status != 'paid'
                        )
                    )
                ).order_by(UnakiBooking.appointment_date.desc()).all()

            # Method 2: If no results, try matching by phone (exact match)
            if not customer_appointments_query and selected_customer.phone:
                # Try exact match
                customer_appointments_query = UnakiBooking.query.filter(
                    UnakiBooking.client_phone == selected_customer.phone,
                    db.or_(
                        UnakiBooking.status.in_(['scheduled', 'confirmed']),
                        db.and_(
                            UnakiBooking.status == 'completed',
                            UnakiBooking.payment_status != 'paid'
                        )
                    )
                ).order_by(UnakiBooking.appointment_date.desc()).all()

                # If still no results, try partial match (phone might have different formats)
                if not customer_appointments_query:
                    # Extract digits only for comparison
                    phone_digits = ''.join(filter(str.isdigit, selected_customer.phone))
                    if len(phone_digits) >= 10:
                        # Use last 10 digits for matching
                        last_10_digits = phone_digits[-10:]
                        customer_appointments_query = UnakiBooking.query.filter(
                            UnakiBooking.client_phone.like(f'%{last_10_digits}%'),
                            db.or_(
                                UnakiBooking.status.in_(['scheduled', 'confirmed']),
                                db.and_(
                                    UnakiBooking.status == 'completed',
                                    UnakiBooking.payment_status != 'paid'
                                )
                            )
                        ).order_by(UnakiBooking.appointment_date.desc()).all()

            print(f"DEBUG: Customer {selected_customer.id} ({selected_customer.first_name} {selected_customer.last_name}) phone: {selected_customer.phone}")
            print(f"DEBUG: Found {len(customer_appointments_query)} Unaki appointments for billing")

            # Convert UnakiBooking objects to dictionaries for JSON serialization
            for appointment in customer_appointments_query:
                apt_dict = appointment.to_dict()
                # Ensure all required fields are present
                if not apt_dict.get('service_price'):
                    apt_dict['service_price'] = 0.0
                customer_appointments.append(apt_dict)

            # Get unique services from Unaki appointments and map service_ids
            unaki_service_names = list(set([apt.get('service_name') for apt in customer_appointments if apt.get('service_name')]))
            if unaki_service_names:
                customer_services_objects = Service.query.filter(Service.name.in_(unaki_service_names)).all()

                # Create a mapping of service names to service objects
                service_name_map = {service.name: service for service in customer_services_objects}

                # Update appointments with correct service_id from matching service name
                for apt in customer_appointments:
                    if apt.get('service_name'):
                        # Try exact match first
                        matching_service = service_name_map.get(apt['service_name'])

                        # If no exact match, try partial match (service name might include price/duration)
                        if not matching_service:
                            service_base_name = apt['service_name'].split('(')[0].strip()
                            for service in customer_services_objects:
                                if service.name in apt['service_name'] or apt['service_name'].startswith(service.name):
                                    matching_service = service
                                    break

                        # Update appointment with service_id and price
                        if matching_service:
                            apt['service_id'] = matching_service.id
                            apt['service_price'] = float(matching_service.price)
                            apt['service_duration'] = matching_service.duration

            # Get active packages with CORRECT remaining count
            from models import ServicePackageAssignment, ServicePackage, PrepaidPackage, Membership, PackageBenefitTracker

            # Get all active benefit trackers for this customer (this is what billing uses)
            benefit_trackers = PackageBenefitTracker.query.filter_by(
                customer_id=customer_id,
                is_active=True
            ).all()

            customer_active_packages = []
            for tracker in benefit_trackers:
                # Get the assignment to get package template
                assignment = tracker.package_assignment
                if not assignment:
                    app.logger.warning(f"PackageBenefitTracker {tracker.id} has no assignment - skipping")
                    continue

                # Get the package template based on package type
                package_template = assignment.get_package_template()

                # Determine package name with comprehensive fallback handling
                package_name = None

                # Try to get name from package template
                if package_template:
                    if hasattr(package_template, 'name') and package_template.name:
                        package_name = package_template.name
                    elif hasattr(package_template, 'package_name') and package_template.package_name:
                        package_name = package_template.package_name

                # If still no name, try assignment fields
                if not package_name:
                    if hasattr(assignment, 'package_name') and assignment.package_name:
                        package_name = assignment.package_name
                    elif hasattr(assignment, 'name') and assignment.name:
                        package_name = assignment.name

                # Final fallback: generate name from package type
                if not package_name:
                    package_name = assignment.package_type.replace('_', ' ').title() + ' Package'
                    app.logger.warning(f"No package name found for assignment {assignment.id} (type: {assignment.package_type}, ref_id: {assignment.package_reference_id}), using fallback: {package_name}")

                # Get service name with proper fallback - CRITICAL FIX
                service_name = None

                # Priority 1: Get from tracker's service relationship
                if tracker.service_id:
                    service_obj = Service.query.get(tracker.service_id)
                    if service_obj:
                        service_name = service_obj.name
                        app.logger.info(f"✅ Service name from tracker.service_id: {service_name}")

                # Priority 2: Get from assignment's service relationship
                if not service_name and assignment.service_id:
                    service_obj = Service.query.get(assignment.service_id)
                    if service_obj:
                        service_name = service_obj.name
                        app.logger.info(f"✅ Service name from assignment.service_id: {service_name}")

                # Priority 3: Get from package template if it's a ServicePackage
                if not service_name and assignment.package_type == 'service_package' and package_template:
                    if hasattr(package_template, 'service_id') and package_template.service_id:
                        service_obj = Service.query.get(package_template.service_id)
                        if service_obj:
                            service_name = service_obj.name
                            app.logger.info(f"✅ Service name from package_template.service_id: {service_name}")

                # Log warning if service package has no service name
                if assignment.package_type == 'service_package' and not service_name:
                    app.logger.warning(f"⚠️ Service package assignment {assignment.id} has no service name - tracker.service_id={tracker.service_id}, assignment.service_id={assignment.service_id}")
                    service_name = 'Unknown Service'  # Fallback for service packages


                # Build package info with correct field names for template
                package_info = {
                    'assignment_id': assignment.id,
                    'package_type': assignment.package_type,
                    'name': package_name,
                    'benefit_type': tracker.benefit_type,
                    'is_active': tracker.is_active,
                    'service_name': service_name if assignment.package_type == 'service_package' else None,  # Only show for service packages
                    'service_id': assignment.service_id,  # Include service_id for reference
                    'expires_on': tracker.valid_to.strftime('%b %d, %Y') if tracker.valid_to else None
                }

                # Add discount_percentage for student offers and discount packages
                if tracker.benefit_type == 'discount' or assignment.package_type == 'student_offer':
                    package_info['discount_percentage'] = float(tracker.discount_percentage or 0)

                    # For student offers, get discount and applicable services from template
                    if assignment.package_type == 'student_offer':
                        try:
                            from models import StudentOffer
                            student_offer = StudentOffer.query.get(assignment.package_reference_id)
                            if student_offer:
                                if student_offer.discount_percentage:
                                    package_info['discount_percentage'] = float(student_offer.discount_percentage)

                                # Get list of service IDs and names this offer applies to
                                if hasattr(student_offer, 'student_offer_services'):
                                    applicable_service_ids = [sos.service_id for sos in student_offer.student_offer_services]
                                    package_info['applicable_service_ids'] = applicable_service_ids

                                    # Get service names for display
                                    applicable_services = []
                                    for sos in student_offer.student_offer_services:
                                        if sos.service:
                                            applicable_services.append(sos.service.name)
                                    package_info['applicable_service_names'] = ', '.join(applicable_services) if applicable_services else 'All Services'

                                # Add student offer specific fields
                                package_info['valid_from'] = student_offer.valid_from.strftime('%b %d, %Y') if student_offer.valid_from else None
                                package_info['valid_to'] = student_offer.valid_to.strftime('%b %d, %Y') if student_offer.valid_to else None
                                package_info['valid_days'] = student_offer.valid_days or 'All Days'
                                package_info['conditions'] = student_offer.conditions or 'Standard terms apply'
                                package_info['package_price'] = float(student_offer.price) if student_offer.price else 0

                                app.logger.info(f"✅ Student offer {package_info['name']}: {package_info['discount_percentage']}% off, valid {package_info['valid_days']}, applies to: {package_info.get('applicable_service_names', 'N/A')}")
                        except Exception as e:
                            app.logger.error(f"Error getting student offer details: {e}")


                # Add type-specific fields matching template expectations
                if tracker.benefit_type in ['free', 'discount']:
                    # Service-based packages - ensure we're getting the RIGHT data
                    total = tracker.total_allocated or 0
                    used = tracker.used_count or 0
                    remaining = tracker.remaining_count or 0

                    # Double-check: if remaining is calculated, ensure it's correct
                    if total > 0 and remaining == 0 and used == 0:
                        # Fresh package - remaining should equal total
                        remaining = total

                    usage_pct = round((used / total * 100), 1) if total > 0 else 0

                    package_info.update({
                        'total_allocated': total,
                        'used_count': used,
                        'remaining_count': remaining,
                        'usage_percentage': usage_pct
                    })

                    app.logger.info(f"Service package {package_name}: Total={total}, Used={used}, Remaining={remaining}")

                    if tracker.benefit_type == 'discount':
                        package_info['discount_percentage'] = tracker.discount_percentage or 0

                elif tracker.benefit_type == 'prepaid':
                    # Prepaid credit packages
                    package_info.update({
                        'balance_total': float(tracker.balance_total or 0),
                        'balance_used': float(tracker.balance_used or 0),
                        'balance_remaining': float(tracker.balance_remaining or 0),
                        'usage_percentage': round((tracker.balance_used / tracker.balance_total * 100), 1) if tracker.balance_total > 0 else 0
                    })

                elif tracker.benefit_type == 'unlimited':
                    # Unlimited/membership packages
                    package_info.update({
                        'access_type': 'unlimited'
                    })

                customer_active_packages.append(package_info)

            # Log package data for debugging
            if customer_active_packages:
                app.logger.info(f"Customer {customer_id} has {len(customer_active_packages)} active packages:")
                for pkg in customer_active_packages:
                    app.logger.info(f"  - {pkg['name']} ({pkg['benefit_type']}) - Service: {pkg['service_name']}")
            else:
                app.logger.info(f"Customer {customer_id} has no active packages")

            # Convert Service objects to dictionaries for JSON serialization
            if 'customer_services_objects' in locals():
                customer_services = [
                    {
                        'id': service.id,
                        'name': service.name,
                        'description': service.description,
                        'price': float(service.price),
                        'duration': service.duration,
                        'category': service.category,
                        'is_active': service.is_active
                    }
                    for service in customer_services_objects
                ]
            else:
                customer_services = []

            print(f"DEBUG: Customer {customer_id} has {len(customer_appointments)} ready-to-bill Unaki appointments and {len(customer_services)} services ready for billing")

    return render_template('integrated_billing.html',
                         customers=customers,
                         services=services,
                         staff_members=staff_members, # Pass staff members to template
                         inventory_items=inventory_items,
                         recent_invoices=recent_invoices,
                         total_revenue=total_revenue,
                         pending_amount=pending_amount,
                         today_revenue=today_revenue,
                         selected_customer=selected_customer,
                         customer_appointments=customer_appointments,
                         customer_services=customer_services,
                         customer_active_packages=customer_active_packages, # Pass customer packages
                         preselected_client_id=customer_id,
                         preselected_client_name=client_name,
                         preselected_client_phone=client_phone,
                         appointment_id=appointment_id)

@app.route('/appointment/<int:appointment_id>/go-to-billing')
@login_required
def appointment_to_billing(appointment_id):
    """Redirect to integrated billing for a specific appointment's customer and show ALL their bookings"""
    # Allow all authenticated users to access billing
    if not current_user.is_active:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        from models import Appointment, UnakiBooking, Customer

        # First try to find in UnakiBooking table (primary system)
        unaki_booking = UnakiBooking.query.get(appointment_id)
        customer_id = None
        customer_name = None

        if unaki_booking:
            app.logger.info(f"Found UnakiBooking {appointment_id}: {unaki_booking.client_name}")
            customer_name = unaki_booking.client_name

            # First try to use existing client_id if it exists
            if unaki_booking.client_id:
                customer = Customer.query.get(unaki_booking.client_id)
                if customer:
                    customer_id = customer.id
                    customer_name = customer.full_name
                    app.logger.info(f"Using existing client_id {customer_id} for UnakiBooking {appointment_id}")
                else:
                    app.logger.warning(f"UnakiBooking {appointment_id} has invalid client_id {unaki_booking.client_id}")

            # If no valid client_id, try to find customer by phone
            if not customer_id and unaki_booking.client_phone:
                customer = Customer.query.filter_by(phone=unaki_booking.client_phone).first()
                if customer:
                    customer_id = customer.id
                    customer_name = customer.full_name
                    # Update the UnakiBooking with the correct client_id
                    unaki_booking.client_id = customer_id
                    db.session.commit()
                    app.logger.info(f"Matched UnakiBooking {appointment_id} to existing customer {customer_id} by phone")

            # If still no match, try to find by name
            if not customer_id and unaki_booking.client_name:
                name_parts = unaki_booking.client_name.strip().split(' ', 1)
                first_name = name_parts[0] if name_parts else ''
                last_name = name_parts[1] if len(name_parts) > 1 else ''

                if first_name:
                    # Try exact name match first
                    customer = Customer.query.filter(
                        Customer.first_name.ilike(first_name),
                        Customer.last_name.ilike(last_name) if last_name else True
                    ).first()

                    if not customer:
                        # Try first name only match
                        customer = Customer.query.filter(
                            Customer.first_name.ilike(f'%{first_name}%')
                        ).first()

                    if customer:
                        customer_id = customer.id
                        customer_name = customer.full_name
                        # Update the UnakiBooking with the correct client_id
                        unaki_booking.client_id = customer_id
                        db.session.commit()
                        app.logger.info(f"Matched UnakiBooking {appointment_id} to existing customer {customer_id} by name")

            # If still no match, create a new customer
            if not customer_id:
                name_parts = unaki_booking.client_name.strip().split(' ', 1)
                first_name = name_parts[0] if name_parts else 'Unknown'
                last_name = name_parts[1] if len(name_parts) > 1 else ''

                new_customer = Customer(
                    first_name=first_name,
                    last_name=last_name,
                    phone=unaki_booking.client_phone,
                    email=unaki_booking.client_email,
                    is_active=True
                )
                db.session.add(new_customer)
                db.session.flush()
                customer_id = new_customer.id
                customer_name = new_customer.full_name

                # Update the UnakiBooking with the new client_id
                unaki_booking.client_id = customer_id
                db.session.commit()
                app.logger.info(f"Created new customer {customer_id} ({customer_name}) for UnakiBooking {appointment_id}")

        else:
            # Fallback: try to find in regular Appointment table
            appointment = Appointment.query.get(appointment_id)
            if appointment and appointment.client_id:
                customer_id = appointment.client_id
                customer_name = appointment.client.full_name if appointment.client else 'Unknown'
                app.logger.info(f"Found regular appointment {appointment_id}, customer {customer_id} ({customer_name})")
            else:
                raise Exception(f"No appointment or booking found with ID {appointment_id}")

        if not customer_id:
            raise Exception(f"Could not determine customer for appointment {appointment_id}")

        # Flash a success message showing we're loading all bookings for this customer
        flash(f'Loading all confirmed bookings for {customer_name} ready for billing', 'info')

        # Redirect to integrated billing with customer_id - this will automatically load ALL their bookings
        return redirect(url_for('integrated_billing', customer_id=customer_id))

    except Exception as e:
        app.logger.error(f"Error redirecting to billing for appointment {appointment_id}: {str(e)}")
        flash(f'Error accessing billing for this appointment: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/api/customer/<int:customer_id>/appointments')
@login_required
def get_customer_appointments(customer_id):
    """API endpoint to fetch all confirmed/scheduled appointments for a customer"""
    try:
        from models import UnakiBooking, Customer, Service

        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404

        # Get ALL booked and unpaid Unaki bookings for this customer
        # Include: scheduled, confirmed, and completed but unpaid appointments
        customer_appointments_query = []

        # Method 1: Try to match by client_id first (most reliable)
        if customer.id:
            customer_appointments_query = UnakiBooking.query.filter(
                UnakiBooking.client_id == customer.id,
                db.or_(
                    UnakiBooking.status.in_(['scheduled', 'confirmed']),
                    db.and_(
                        UnakiBooking.status == 'completed',
                        UnakiBooking.payment_status != 'paid'
                    )
                )
            ).order_by(UnakiBooking.appointment_date.desc()).all()

        # Method 2: If no results, try matching by phone (exact match)
        if not customer_appointments_query and customer.phone:
            customer_appointments_query = UnakiBooking.query.filter(
                UnakiBooking.client_phone == customer.phone,
                db.or_(
                    UnakiBooking.status.in_(['scheduled', 'confirmed']),
                    db.and_(
                        UnakiBooking.status == 'completed',
                        UnakiBooking.payment_status != 'paid'
                    )
                )
            ).order_by(UnakiBooking.appointment_date.desc()).all()

            # Try partial match if exact match fails
            if not customer_appointments_query:
                phone_digits = ''.join(filter(str.isdigit, customer.phone))
                if len(phone_digits) >= 10:
                    last_10_digits = phone_digits[-10:]
                    customer_appointments_query = UnakiBooking.query.filter(
                        UnakiBooking.client_phone.like(f'%{last_10_digits}%'),
                        db.or_(
                            UnakiBooking.status.in_(['scheduled', 'confirmed']),
                            db.and_(
                                UnakiBooking.status == 'completed',
                                UnakiBooking.payment_status != 'paid'
                            )
                        )
                    ).order_by(UnakiBooking.appointment_date.desc()).all()

        # Method 3: If still no results, try matching by name
        if not customer_appointments_query:
            full_name = f"{customer.first_name} {customer.last_name}".strip()
            customer_appointments_query = UnakiBooking.query.filter(
                UnakiBooking.client_name.ilike(f'%{full_name}%'),
                db.or_(
                    UnakiBooking.status.in_(['scheduled', 'confirmed']),
                    db.and_(
                        UnakiBooking.status == 'completed',
                        UnakiBooking.payment_status != 'paid'
                    )
                )
            ).order_by(UnakiBooking.appointment_date.desc()).all()

            # Try first name only if full name fails
            if not customer_appointments_query:
                customer_appointments_query = UnakiBooking.query.filter(
                    UnakiBooking.client_name.ilike(f'%{customer.first_name}%'),
                    db.or_(
                        UnakiBooking.status.in_(['scheduled', 'confirmed']),
                        db.and_(
                            UnakiBooking.status == 'completed',
                            UnakiBooking.payment_status != 'paid'
                        )
                    )
                ).order_by(UnakiBooking.appointment_date.desc()).all()

        app.logger.info(f"Found {len(customer_appointments_query)} appointments for customer {customer_id}")

        # Convert to dictionaries with proper service linking
        appointments_data = []
        for appointment in customer_appointments_query:
            apt_dict = appointment.to_dict()

            # Ensure service_price is set
            if not apt_dict.get('service_price'):
                apt_dict['service_price'] = 0.0

            # Try to match service by name or service_id
            matching_service = None
            if appointment.service_id:
                matching_service = Service.query.get(appointment.service_id)
            elif appointment.service_name:
                # Try exact match first
                matching_service = Service.query.filter(
                    Service.name == appointment.service_name,
                    Service.is_active == True
                ).first()

                # If no exact match, try partial match (service name might include price/duration)
                if not matching_service:
                    service_base_name = appointment.service_name.split('(')[0].strip()
                    matching_service = Service.query.filter(
                        Service.name.ilike(f'{service_base_name}%'),
                        Service.is_active == True
                    ).first()

            # Add service details to appointment data
            if matching_service:
                apt_dict['service_id'] = matching_service.id
                apt_dict['service_name'] = matching_service.name
                apt_dict['service_price'] = float(matching_service.price)
                apt_dict['service_duration'] = matching_service.duration
            else:
                # If still no match, log it for debugging
                app.logger.warning(f"No matching service found for appointment {appointment.id} with service_name: {appointment.service_name}")

            appointments_data.append(apt_dict)

        # Get unique services with full details
        service_names = list(set([apt.get('service_name') for apt in appointments_data if apt.get('service_name')]))
        services_data = []
        if service_names:
            services = Service.query.filter(Service.name.in_(service_names)).all()
            services_data = [
                {
                    'id': service.id,
                    'name': service.name,
                    'description': service.description,
                    'price': float(service.price),
                    'duration': service.duration,
                    'category': service.category,
                    'is_active': service.is_active
                }
                for service in services
            ]

        return jsonify({
            'success': True,
            'appointments': appointments_data,
            'services': services_data,
            'customer': {
                'id': customer.id,
                'name': customer.full_name,
                'phone': customer.phone,
                'email': customer.email
            }
        })

    except Exception as e:
        app.logger.error(f"Error fetching customer appointments: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/integrated-billing/check-package-benefits', methods=['POST'])
@login_required
def check_package_benefits():
    """
    Check which package benefits will apply to services BEFORE invoice creation
    Returns detailed package application info for frontend display
    """
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        services = data.get('services', [])  # [{service_id, quantity}, ...]

        if not customer_id:
            return jsonify({'success': False, 'error': 'Customer ID required'}), 400

        if not services:
            return jsonify({'success': False, 'error': 'No services provided'}), 400

        from modules.packages.package_billing_service import PackageBillingService
        from models import Service, PackageBenefitTracker, ServicePackageAssignment

        results = []

        for service_item in services:
            service_id = service_item.get('service_id')
            quantity = service_item.get('quantity', 1)

            if not service_id:
                continue

            service = Service.query.get(service_id)
            if not service:
                continue

            service_item_price = float(service.price) * quantity
            service_item_final_price = service_item_price # Initialize with original price

            package_discount_applied = False
            package_result = {'success': False, 'applied': False, 'message': 'No package benefit checked'}
            package_deductions_applied = 0 # Counter for any package deduction

            # --- Check for Yearly Membership Discount FIRST ---
            yearly_membership_assignment = ServicePackageAssignment.query.filter(
                ServicePackageAssignment.customer_id == int(customer_id),
                ServicePackageAssignment.package_type == 'yearly_membership',
                ServicePackageAssignment.status == 'active'
            ).first()

            if yearly_membership_assignment:
                # Get the yearly membership template
                from models import YearlyMembership
                yearly_membership = YearlyMembership.query.get(yearly_membership_assignment.package_reference_id)

                if yearly_membership and yearly_membership.discount_percent:
                    # Apply yearly membership discount
                    discount_amount = (service_item_price * yearly_membership.discount_percent) / 100
                    service_item_final_price = service_item_price - discount_amount

                    app.logger.info(f"✅ YEARLY MEMBERSHIP: Applied {yearly_membership.discount_percent}% discount = ₹{discount_amount:.2f}")

                    package_result = {
                        'success': True,
                        'applied': True,
                        'message': f'Yearly membership: {yearly_membership.discount_percent}% discount',
                        'package_type': 'yearly_membership',
                        'package_id': yearly_membership_assignment.id,
                        'discount_amount': discount_amount
                    }
                    package_discount_applied = True
                    package_deductions_applied += 1

            # Only check other packages if no discount was applied yet
            if not package_discount_applied:
                # Find applicable packages for this service
                applicable_packages = PackageBillingService.find_applicable_packages(
                    customer_id=customer_id,
                    service_id=service_id
                )

                if applicable_packages:
                    # Get the highest priority package
                    best_package = applicable_packages[0]
                    tracker = best_package
                    assignment = tracker.package_assignment if tracker else None

                    # Calculate what will be applied
                    benefit_info = {
                        'service_id': service_id,
                        'service_name': service.name,
                        'original_price': service_item_price,
                        'quantity': quantity,
                        'has_benefit': True,
                        'benefit_type': tracker.benefit_type,
                        'package_name': assignment.package_name if hasattr(assignment, 'package_name') else 'Package',
                        'package_assignment_id': assignment.id if assignment else None
                    }

                    # Calculate benefit based on type
                    if tracker.benefit_type == 'unlimited':
                        benefit_info['final_price'] = 0.0
                        benefit_info['deduction'] = service_item_price
                        benefit_info['message'] = 'Free (Unlimited Membership)'
                        package_result = {
                            'success': True,
                            'applied': True,
                            'message': benefit_info['message'],
                            'package_type': assignment.package_type if assignment else 'unknown',
                            'package_id': assignment.id if assignment else None,
                            'deduction_amount': benefit_info['deduction']
                        }
                        package_discount_applied = True # Treat unlimited as a full discount
                        package_deductions_applied += 1

                    elif tracker.benefit_type == 'free':
                        sessions_available = tracker.remaining_count or 0
                        sessions_to_use = min(quantity, sessions_available)

                        if sessions_to_use > 0:
                            price_per_session = service_item_price / quantity
                            deduction = price_per_session * sessions_to_use
                            service_item_final_price = service_item_price - deduction # Apply deduction
                            benefit_info['final_price'] = service_item_final_price
                            benefit_info['deduction'] = deduction
                            benefit_info['sessions_used'] = sessions_to_use
                            benefit_info['sessions_remaining_after'] = sessions_available - sessions_to_use
                            benefit_info['message'] = f'{sessions_to_use} free session(s) applied. {sessions_available - sessions_to_use} remaining after.'
                            package_result = {
                                'success': True,
                                'applied': True,
                                'message': benefit_info['message'],
                                'package_type': assignment.package_type if assignment else 'unknown',
                                'package_id': assignment.id if assignment else None,
                                'deduction_amount': benefit_info['deduction']
                            }
                            package_deductions_applied += 1
                        else:
                            benefit_info['has_benefit'] = False
                            benefit_info['final_price'] = service_item_price
                            benefit_info['deduction'] = 0
                            benefit_info['message'] = 'No sessions remaining'
                            package_result['message'] = benefit_info['message'] # Update message

                    elif tracker.benefit_type == 'discount':
                        discount_pct = tracker.discount_percentage or 0
                        deduction = service_item_price * (discount_pct / 100)
                        service_item_final_price = service_item_price - deduction # Apply deduction
                        benefit_info['final_price'] = service_item_final_price
                        benefit_info['deduction'] = deduction
                        benefit_info['discount_percentage'] = discount_pct
                        benefit_info['message'] = f'{discount_pct}% discount applied'
                        package_result = {
                            'success': True,
                            'applied': True,
                            'message': benefit_info['message'],
                            'package_type': assignment.package_type if assignment else 'unknown',
                            'package_id': assignment.id if assignment else None,
                            'deduction_amount': benefit_info['deduction']
                        }
                        package_deductions_applied += 1

                    elif tracker.benefit_type == 'prepaid':
                        credit_available = tracker.balance_remaining or 0
                        deduction = min(service_item_price, credit_available)
                        service_item_final_price = service_item_price - deduction # Apply deduction
                        benefit_info['final_price'] = service_item_final_price
                        benefit_info['deduction'] = deduction
                        benefit_info['credit_remaining_after'] = credit_available - deduction
                        benefit_info['message'] = f'₹{deduction:.2f} prepaid credit applied. ₹{credit_available - deduction:.2f} remaining after.'
                        package_result = {
                            'success': True,
                            'applied': True,
                            'message': benefit_info['message'],
                            'package_type': assignment.package_type if assignment else 'unknown',
                            'package_id': assignment.id if assignment else None,
                            'deduction_amount': benefit_info['deduction']
                        }
                        package_deductions_applied += 1

                    results.append(benefit_info)
            else:
                # No package applies
                results.append({
                    'service_id': service_id,
                    'service_name': service.name,
                    'original_price': service_item_price,
                    'final_price': service_item_price,
                    'quantity': quantity,
                    'has_benefit': False,
                    'deduction': 0,
                    'message': 'No package benefit available'
                })
                package_result['message'] = 'No package benefit available' # Update message

        return jsonify({
            'success': True,
            'benefits': results,
            'package_deductions_applied': package_deductions_applied # Return count of deductions
        })

    except Exception as e:
        app.logger.error(f"Error checking package benefits: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/integrated-billing/create-professional', methods=['POST'])
@login_required
def create_professional_invoice():
    """
    Create new professional invoice with complete GST/SGST tax support

    MULTI-SERVICE STAFF BILLING:
    - Each service gets its own InvoiceItem record
    - Each InvoiceItem stores the staff who performed that service
    - staff_revenue_price stores ORIGINAL service price (for commission calculation)
    - final_amount stores customer price (after package benefits/discounts)
    - This allows accurate staff commission even when packages reduce customer price

    Example:
    Service 1: Massage by Staff A - Original ₹500, Customer pays ₹250 (50% package discount)
      → Staff A gets commission on ₹500 (staff_revenue_price)
    Service 2: Facial by Staff B - Original ₹300, Customer pays ₹300 (no discount)
      → Staff B gets commission on ₹300 (staff_revenue_price)
    """
    # Allow all authenticated users to create invoices
    if not current_user.is_active:
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    try:
        from models import Service, EnhancedInvoice, InvoiceItem, User
        from modules.inventory.models import InventoryBatch, InventoryProduct
        from modules.inventory.queries import create_consumption_record
        import datetime

        # Parse form data
        client_id = request.form.get('client_id')
        if not client_id:
            app.logger.error('Client ID is missing from form data')
            return jsonify({'success': False, 'message': 'Client is required'}), 400

        customer = Customer.query.get(client_id)
        if not customer:
            app.logger.error(f'Customer not found with ID: {client_id}')
            return jsonify({'success': False, 'message': f'Customer not found with ID: {client_id}'}), 404

        # Parse services data
        services_data = []
        service_ids = request.form.getlist('service_ids[]')
        service_quantities = request.form.getlist('service_quantities[]')
        appointment_ids = request.form.getlist('appointment_ids[]')
        staff_ids = request.form.getlist('staff_ids[]')

        for i, service_id in enumerate(service_ids):
            if service_id and str(service_id).strip():
                # Validate staff assignment
                staff_id = staff_ids[i] if i < len(staff_ids) and staff_ids[i] and str(staff_ids[i]).strip() else None
                if not staff_id:
                    app.logger.warning(f'Staff not assigned for service index {i}')
                    return jsonify({
                        'success': False,
                        'message': f'Staff member is required for service #{i+1}. Please assign staff to all services.'
                    }), 400

                # Verify service exists
                service = Service.query.get(int(service_id))
                if not service:
                    return jsonify({
                        'success': False,
                        'message': f'Service #{i+1} not found in database. Please refresh and try again.'
                    }), 404

                # Verify staff exists
                staff = User.query.get(int(staff_id))
                if not staff:
                    return jsonify({
                        'success': False,
                        'message': f'Selected staff member for service #{i+1} not found. Please refresh and try again.'
                    }), 404

                services_data.append({
                    'service_id': int(service_id),
                    'quantity': float(service_quantities[i]) if i < len(service_quantities) else 1,
                    'appointment_id': int(appointment_ids[i]) if i < len(appointment_ids) and appointment_ids[i] else None,
                    'staff_id': int(staff_id)
                })

        # Parse inventory data
        inventory_data = []
        product_ids = request.form.getlist('product_ids[]')
        product_staff_ids = request.form.getlist('product_staff_ids[]')
        batch_ids = request.form.getlist('batch_ids[]')
        product_quantities = request.form.getlist('product_quantities[]')
        product_prices = request.form.getlist('product_prices[]')

        for i, product_id in enumerate(product_ids):
            if product_id and i < len(batch_ids) and batch_ids[i]:
                # Validate staff assignment for products
                if i >= len(product_staff_ids) or not product_staff_ids[i]:
                    return jsonify({
                        'success': False,
                        'message': f'Staff member is required for product #{i+1}. Please assign staff to all products.'
                    }), 400

                inventory_data.append({
                    'product_id': int(product_id),
                    'batch_id': int(batch_ids[i]),
                    'quantity': float(product_quantities[i]) if i < len(product_quantities) else 1,
                    'unit_price': float(product_prices[i]) if i < len(product_prices) and product_prices[i] else 0,
                    'staff_id': int(product_staff_ids[i])
                })

        # Validate inventory stock
        for item in inventory_data:
            batch = InventoryBatch.query.get(item['batch_id'])
            if not batch or batch.is_expired:
                return jsonify({'success': False, 'message': f'Invalid or expired batch for product ID {item["product_id"]}'})

            if float(batch.qty_available) < item['quantity']:
                return jsonify({
                    'success': False,
                    'message': f'Insufficient stock in batch {batch.batch_name}. Available: {batch.qty_available}, Required: {item["quantity"]}'
                })

        # Calculate amounts - Service prices are GST INCLUSIVE
        services_subtotal = 0
        for service_data in services_data:
            service = Service.query.get(service_data['service_id'])
            if service:
                # Service price includes GST
                services_subtotal += service.price * service_data['quantity']

        inventory_subtotal = 0
        for item in inventory_data:
            inventory_subtotal += item['unit_price'] * item['quantity']

        gross_subtotal = services_subtotal + inventory_subtotal

        # Get tax rates
        cgst_rate = float(request.form.get('cgst_rate', 9)) / 100
        sgst_rate = float(request.form.get('sgst_rate', 9)) / 100
        igst_rate = float(request.form.get('igst_rate', 0)) / 100
        is_interstate = request.form.get('is_interstate') == 'on'
        total_gst_rate = igst_rate if is_interstate else (cgst_rate + sgst_rate)

        # IMPORTANT: Service prices are GST-EXCLUSIVE (tax added on top)
        # Calculate GST to be added to service prices
        service_base_amount = services_subtotal
        service_gst_amount = services_subtotal * total_gst_rate if total_gst_rate > 0 else 0

        # For inventory/products, GST is INCLUSIVE (MRP prices already include tax)
        # Extract base amount and GST from product MRP prices
        if total_gst_rate > 0:
            inventory_base_amount = inventory_subtotal / (1 + total_gst_rate)
            inventory_gst_amount = inventory_subtotal - inventory_base_amount
        else:
            inventory_base_amount = inventory_subtotal
            inventory_gst_amount = 0

        # Total base amounts (before tax)
        total_base_amount = service_base_amount + inventory_base_amount

        # Calculate discount on base amount
        discount_type = request.form.get('discount_type', 'amount')
        discount_value = float(request.form.get('discount_value', 0))
        if discount_type == 'percentage':
            discount_amount = (total_base_amount * discount_value) / 100
        else:
            discount_amount = discount_value

        # Net base after discount
        net_base_amount = max(0, total_base_amount - discount_amount)

        # Recalculate GST proportionally after discount
        if total_base_amount > 0 and total_gst_rate > 0:
            # Discount factor to apply proportionally
            discount_factor = net_base_amount / total_base_amount

            # Apply discount factor to service GST
            final_service_gst = service_gst_amount * discount_factor

            # For inventory, recalculate GST on discounted base
            inventory_discount = discount_amount * (inventory_base_amount / total_base_amount) if total_base_amount > 0 else 0
            inventory_net_base = max(0, inventory_base_amount - inventory_discount)
            final_inventory_gst = inventory_net_base * total_gst_rate
        else:
            final_service_gst = 0
            final_inventory_gst = 0

        total_tax = final_service_gst + final_inventory_gst

        # Split into CGST/SGST or IGST
        if is_interstate:
            igst_amount = total_tax
            cgst_amount = 0
            sgst_amount = 0
        else:
            if total_gst_rate > 0:
                cgst_amount = total_tax * (cgst_rate / total_gst_rate)
                sgst_amount = total_tax * (sgst_rate / total_gst_rate)
            else:
                cgst_amount = 0
                sgst_amount = 0
            igst_amount = 0

        net_subtotal = net_base_amount
        additional_charges = float(request.form.get('additional_charges', 0))
        tips_amount = float(request.form.get('tips_amount', 0))

        # Final total: base amount + tax + charges + tips
        total_amount = net_base_amount + total_tax + additional_charges + tips_amount

        # Create professional invoice with proper transaction handling
        try:
            # Generate professional invoice number with retry logic to prevent duplicates
            current_date = datetime.datetime.now()
            date_prefix = current_date.strftime('%Y%m%d')

            # Find the highest sequence number for today
            latest_invoice = db.session.query(EnhancedInvoice).filter(
                EnhancedInvoice.invoice_number.like(f"INV-{date_prefix}-%")
            ).order_by(EnhancedInvoice.invoice_number.desc()).first()

            if latest_invoice:
                try:
                    last_sequence = int(latest_invoice.invoice_number.split('-')[-1])
                    invoice_sequence = last_sequence + 1
                except (ValueError, IndexError):
                    invoice_sequence = 1
            else:
                invoice_sequence = 1

            # Ensure uniqueness by checking if invoice number exists
            max_attempts = 100
            for attempt in range(max_attempts):
                invoice_number = f"INV-{date_prefix}-{invoice_sequence:04d}"
                existing = db.session.query(EnhancedInvoice).filter_by(invoice_number=invoice_number).first()
                if not existing:
                    break
                invoice_sequence += 1
            else:
                # Fallback to timestamp-based number if we exhaust attempts
                import time
                invoice_number = f"INV-{date_prefix}-{int(time.time() * 1000) % 100000:05d}"

            # Create enhanced invoice with IST timezone
            from app import get_ist_now
            ist_now = get_ist_now()

            # CRITICAL: Store invoice_date as DATE only (not datetime) for dashboard filtering
            # Dashboard queries use func.date() which expects a date, not datetime
            invoice_date_only = ist_now.date()  # Extract just the date portion

            invoice = EnhancedInvoice()
            invoice.invoice_number = invoice_number
            invoice.client_id = int(client_id)
            # Use datetime module to avoid variable shadowing
            import datetime as dt
            invoice.invoice_date = dt.datetime.combine(invoice_date_only, dt.time.min)  # Store as midnight on invoice date
            invoice.created_at = ist_now.replace(tzinfo=None)  # Store as naive IST datetime

            # Professional billing fields
            invoice.services_subtotal = services_subtotal
            invoice.inventory_subtotal = inventory_subtotal
            invoice.gross_subtotal = gross_subtotal
            invoice.net_subtotal = net_subtotal
            invoice.tax_amount = total_tax
            invoice.discount_amount = discount_amount
            invoice.tips_amount = tips_amount
            invoice.total_amount = total_amount
            invoice.balance_due = total_amount
            invoice.payment_status = 'paid' # Set to paid since payment is assumed to be taken

            # Store GST fields properly
            invoice.cgst_rate = cgst_rate * 100
            invoice.sgst_rate = sgst_rate * 100
            invoice.igst_rate = igst_rate * 100
            invoice.cgst_amount = cgst_amount
            invoice.sgst_amount = sgst_amount
            invoice.igst_amount = igst_amount
            invoice.is_interstate = is_interstate
            invoice.additional_charges = additional_charges
            payment_terms = request.form.get('payment_terms', 'immediate')
            payment_method = request.form.get('payment_method', 'cash')
            invoice.payment_terms = payment_terms
            invoice.payment_method = payment_method # Record the payment method

            # Tax breakdown for legacy support
            tax_breakdown = {
                'cgst_rate': cgst_rate * 100,
                'sgst_rate': sgst_rate * 100,
                'igst_rate': igst_rate * 100,
                'cgst_amount': cgst_amount,
                'sgst_amount': sgst_amount,
                'igst_amount': igst_amount,
                'is_interstate': is_interstate,
                'additional_charges': additional_charges,
                'payment_terms': payment_terms,
                'payment_method': payment_method
            }

            invoice.notes = json.dumps(tax_breakdown)
            invoice.payment_methods = json.dumps({payment_method: total_amount})

            db.session.add(invoice)
            db.session.flush()  # Get the invoice ID

            # Create invoice items for services and mark Unaki appointments as completed
            service_items_created = 0
            completed_appointments = 0
            package_deductions_applied = 0
            updated_packages = []  # Track updated package info for UI refresh

            # Import package billing service
            from modules.packages.package_billing_service import PackageBillingService

            for service_data in services_data:
                service = Service.query.get(service_data['service_id'])
                if service:
                    # Validate staff assignment - CRITICAL for multi-service billing
                    staff_id = service_data.get('staff_id')
                    staff_name = None

                    if staff_id:
                        staff = User.query.get(staff_id)
                        if staff:
                            staff_name = staff.full_name
                            app.logger.info(f"✅ Service '{service.name}' assigned to staff: {staff_name} (ID: {staff_id})")
                        else:
                            app.logger.error(f"❌ Staff ID {staff_id} not found for service '{service.name}'")
                            return jsonify({
                                'success': False,
                                'message': f'Invalid staff assignment for service: {service.name}'
                            }), 400
                    else:
                        app.logger.error(f"❌ No staff assigned for service '{service.name}'")
                        return jsonify({
                            'success': False,
                            'message': f'Staff assignment required for service: {service.name}'
                        }), 400

                    # Validate appointment_id exists in appointment table (FK constraint requirement)
                    appt_id = service_data.get('appointment_id')
                    valid_appt_id = None
                    if appt_id:
                        from models import Appointment
                        existing_appt = Appointment.query.get(appt_id)
                        if existing_appt:
                            valid_appt_id = appt_id
                        else:
                            app.logger.warning(f"⚠️ Appointment ID {appt_id} not found in appointment table - setting to None to avoid FK constraint error")

                    # CRITICAL: Store original service price for staff commission calculation
                    original_service_price = service.price * service_data['quantity']

                    # Create invoice item with staff information
                    item = InvoiceItem(
                        invoice_id=invoice.id,
                        item_type='service',
                        item_id=service.id,
                        appointment_id=valid_appt_id,  # Only set if valid
                        item_name=service.name,
                        description=service.description or '',
                        quantity=service_data['quantity'],
                        unit_price=service.price,
                        original_amount=original_service_price,
                        final_amount=original_service_price,
                        staff_revenue_price=original_service_price,  # ALWAYS store original price for staff revenue/commission
                        staff_id=staff_id,  # Store staff ID
                        staff_name=staff_name  # Store staff name for quick reference
                    )
                    db.session.add(item)
                    db.session.flush()  # Get item.id
                    service_items_created += 1

                    app.logger.info(f"📋 Invoice item created: Service='{service.name}', Staff='{staff_name}', Price=₹{original_service_price}, Staff Revenue=₹{original_service_price}")

                    # === CRITICAL: APPLY PACKAGE BENEFIT ===
                    # Initialize package deduction tracking
                    package_discount_applied = False
                    package_result = {'success': False, 'applied': False, 'message': 'No package benefit checked'}

                    # First check for student offers with service applicability
                    from models import StudentOffer
                    student_offer_assignment = ServicePackageAssignment.query.filter(
                        ServicePackageAssignment.customer_id == int(client_id),
                        ServicePackageAssignment.package_type == 'student_offer',
                        ServicePackageAssignment.status.in_(['active', 'pending']),
                        ServicePackageAssignment.expires_on >= current_date
                    ).first()

                    if student_offer_assignment:
                        student_offer = StudentOffer.query.get(student_offer_assignment.package_reference_id)

                        if student_offer and student_offer.discount_percentage:
                            # Check if this service is applicable for the student offer
                            is_applicable = False

                            # Get applicable service IDs from student_offer_services relationship
                            if hasattr(student_offer, 'student_offer_services') and student_offer.student_offer_services:
                                applicable_service_ids = [sos.service_id for sos in student_offer.student_offer_services]
                                is_applicable = service.id in applicable_service_ids
                                app.logger.info(f"🔍 Student offer check: Service {service.id} ({service.name}) in applicable list {applicable_service_ids}? {is_applicable}")
                            else:
                                # If no specific services, apply to all
                                is_applicable = True
                                app.logger.info(f"🔍 Student offer applies to ALL services")

                            if is_applicable:
                                # Apply student offer discount
                                service_amount = service.price * service_data['quantity']
                                discount_amount = service_amount * (student_offer.discount_percentage / 100)
                                item.deduction_amount = discount_amount
                                item.final_amount = service_amount - discount_amount
                                item.is_package_deduction = True
                                package_discount_applied = True
                                package_deductions_applied += 1

                                # CRITICAL: staff_revenue_price is ALREADY set to original price above
                                # So staff gets commission on full ₹{service_amount}, customer pays ₹{item.final_amount}

                                db.session.flush()
                                app.logger.info(f"✅ Student offer '{student_offer.name}' {student_offer.discount_percentage}% discount applied: ₹{discount_amount:.2f} on ₹{service_amount:.2f}. Staff revenue stays ₹{item.staff_revenue_price:.2f}")
                            else:
                                app.logger.info(f"⏭️ Student offer '{student_offer.name}' does not apply to service '{service.name}'")

                    # If no student offer discount, check yearly membership
                    if not package_discount_applied:
                        yearly_membership_assignment = ServicePackageAssignment.query.filter(
                            ServicePackageAssignment.customer_id == int(client_id),
                            ServicePackageAssignment.package_type == 'yearly_membership',
                            ServicePackageAssignment.status == 'active',
                            ServicePackageAssignment.expires_on >= current_date
                        ).first()

                        if yearly_membership_assignment:
                            # Get the yearly membership template
                            from models import YearlyMembership
                            yearly_membership = YearlyMembership.query.get(yearly_membership_assignment.package_reference_id)

                            if yearly_membership and yearly_membership.discount_percent > 0:
                                # Apply percentage discount
                                service_amount = service.price * service_data['quantity']
                                discount_amount = service_amount * (yearly_membership.discount_percent / 100)
                                item.deduction_amount = discount_amount
                                item.final_amount = service_amount - discount_amount
                                item.is_package_deduction = True
                                package_discount_applied = True
                                package_deductions_applied += 1

                                db.session.flush()
                                app.logger.info(f"✅ Yearly membership '{yearly_membership.name}' {yearly_membership.discount_percent}% discount applied: ₹{discount_amount:.2f} on ₹{service_amount:.2f}. Staff revenue stays ₹{item.staff_revenue_price:.2f}")

                    # If no discount packages, try other package benefits (free sessions, prepaid, etc.)
                    if not package_discount_applied:
                        package_result = PackageBillingService.apply_package_benefit(
                            customer_id=int(client_id),
                            service_id=service.id,
                            service_price=service.price * service_data['quantity'],
                            invoice_id=invoice.id,
                            invoice_item_id=item.id,
                            service_date=current_date,
                            requested_quantity=int(service_data['quantity'])
                        )

                        if package_result.get('success') and package_result.get('applied'):
                            # Update invoice item with package deduction
                            item.deduction_amount = package_result.get('deduction_amount', 0)
                            item.final_amount = service.price * service_data['quantity'] - item.deduction_amount
                            item.is_package_deduction = True
                            # staff_revenue_price remains unchanged - staff gets commission on original price
                            package_deductions_applied += 1

                            db.session.flush()

                            # Capture updated package info for UI refresh
                            if package_result.get('assignment_id'):
                                assignment = ServicePackageAssignment.query.get(package_result.get('assignment_id'))
                                if assignment:
                                    updated_packages.append({
                                        "assignment_id": assignment.id,
                                        "package_type": "service_package",
                                        "sessions": {
                                            "total": int(assignment.total_sessions or 0),
                                            "used": int(assignment.used_sessions or 0),
                                            "remaining": int(assignment.remaining_sessions or 0)
                                        },
                                        "status": assignment.status
                                    })

                            app.logger.info(f"✅ Package benefit applied: {package_result.get('message')}. Staff revenue stays ₹{item.staff_revenue_price:.2f}")
                        elif package_result.get('success') and not package_result.get('applied'):
                            app.logger.info(f"ℹ️ No package benefit: {package_result.get('message')}")
                        else:
                            app.logger.warning(f"⚠️ Package deduction error: {package_result.get('message', 'Unknown error')}")

                    # Mark Unaki appointment as completed and paid if appointment_id exists
                    if service_data.get('appointment_id'):
                        from models import UnakiBooking
                        from datetime import datetime as dt
                        unaki_appointment = UnakiBooking.query.get(service_data['appointment_id'])
                        if unaki_appointment:
                            unaki_appointment.status = 'completed'
                            unaki_appointment.payment_status = 'paid'
                            unaki_appointment.completed_at = dt.now()
                            unaki_appointment.amount_charged = service.price * service_data['quantity']
                            unaki_appointment.payment_method = payment_method
                            db.session.add(unaki_appointment)
                            completed_appointments += 1
                            app.logger.info(f"✅ Marked Unaki appointment {service_data['appointment_id']} as completed and paid")


            # Create invoice items for inventory and reduce stock
            inventory_items_created = 0
            stock_reduced_count = 0

            for item_data in inventory_data:
                batch = InventoryBatch.query.get(item_data['batch_id'])
                product = InventoryProduct.query.get(item_data['product_id'])

                if batch and product:
                    # Get staff information for product sale
                    staff_id = item_data.get('staff_id')
                    staff_name = None

                    if staff_id:
                        staff = User.query.get(staff_id)
                        if staff:
                            staff_name = staff.full_name
                            app.logger.info(f"✅ Product '{product.name}' sold by staff: {staff_name} (ID: {staff_id})")
                        else:
                            app.logger.warning(f"⚠️ Staff ID {staff_id} not found for product '{product.name}'")
                    else:
                        app.logger.warning(f"⚠️ No staff assigned for product sale: '{product.name}'")

                    # Create invoice item with staff tracking
                    product_amount = item_data['unit_price'] * item_data['quantity']

                    item = InvoiceItem(
                        invoice_id=invoice.id,
                        item_type='inventory',
                        item_id=product.id,
                        product_id=product.id,
                        batch_id=batch.id,
                        item_name=product.name,
                        description=f"Batch: {batch.batch_name}",
                        batch_name=batch.batch_name,
                        quantity=item_data['quantity'],
                        unit_price=item_data['unit_price'],
                        original_amount=product_amount,
                        final_amount=product_amount,
                        staff_revenue_price=product_amount,  # Track product revenue for staff commission
                        staff_id=staff_id,
                        staff_name=staff_name
                    )
                    db.session.add(item)
                    inventory_items_created += 1

                    app.logger.info(f"📦 Inventory item created: Product='{product.name}', Staff='{staff_name}', Amount=₹{product_amount}")

                    # Reduce stock
                    batch.qty_available = float(batch.qty_available) - item_data['quantity']
                    stock_reduced_count += 1

            db.session.commit()

            # Check if this is a save-and-print request
            is_print_request = request.form.get('print_after_save') == 'true'

            return jsonify({
                'success': True,
                'message': 'Invoice created successfully',
                'invoice_id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'service_items_created': service_items_created,
                'inventory_items_created': inventory_items_created,
                'completed_appointments': completed_appointments,
                'package_deductions_applied': package_deductions_applied,
                'updated_packages': updated_packages,
                'print_invoice': is_print_request
            })

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating invoice: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Error creating invoice: {str(e)}'}), 500

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Professional invoice creation failed: {str(e)}")
        return jsonify({'success': False, 'message': f'Error creating professional invoice: {str(e)}'})


@app.route('/integrated-billing/customer-packages/<int:customer_id>', methods=['GET'])
@login_required
def get_customer_packages(customer_id):
    """Get fresh customer package data (no cache) for UI refresh"""
    try:
        from models import ServicePackageAssignment, PackageBenefitTracker

        # Get all active benefit trackers for this customer (what billing actually uses)
        benefit_trackers = PackageBenefitTracker.query.filter_by(
            customer_id=customer_id,
            is_active=True
        ).all()

        app.logger.info(f"Found {len(benefit_trackers)} active benefit trackers for customer {customer_id}")

        packages_list = []
        for tracker in benefit_trackers:
            # Get assignment
            assignment = tracker.package_assignment
            if not assignment:
                app.logger.warning(f"Tracker {tracker.id} has no assignment")
                continue

            r = assignment  # Use assignment variable for compatibility
            # Get package name with comprehensive fallback logic
            package_name = None

            # Try multiple fields in order of preference
            if hasattr(r, 'package_name') and r.package_name:
                package_name = r.package_name
            elif hasattr(r, 'package_display_name') and r.package_display_name:
                package_name = r.package_display_name
            elif hasattr(r, 'name') and r.name:
                package_name = r.name

            # If still no name, try to get from package template
            if not package_name:
                try:
                    package_template = r.get_package_template()
                    if package_template:
                        if hasattr(package_template, 'name') and package_template.name:
                            package_name = package_template.name
                        elif hasattr(package_template, 'package_name') and package_template.package_name:
                            package_name = package_template.package_name
                except:
                    pass

            # Final fallback: generate from package type
            if not package_name:
                pkg_type = "service_package" if r.total_sessions else "prepaid" if r.credit_amount is not None else "membership"
                package_name = pkg_type.replace('_', ' ').title() + ' Package'

            # CRITICAL FIX: Get service_id and service_name from database
            service_id = r.service_id
            service_name = None

            if service_id:
                service_obj = Service.query.get(service_id)
                if service_obj:
                    service_name = service_obj.name
                    app.logger.info(f"✅ API: Service ID={service_id}, Name={service_name} for assignment {r.id}")
                else:
                    app.logger.warning(f"⚠️ Service ID {service_id} not found in database for assignment {r.id}")

            # Fallback to service_name field if it exists
            if not service_name and hasattr(r, 'service_name') and r.service_name:
                service_name = r.service_name

            # Use the actual package_type from the database
            actual_package_type = r.package_type if hasattr(r, 'package_type') and r.package_type else (
                "service_package" if r.total_sessions else "prepaid" if r.credit_amount is not None else "membership"
            )

            package_data = {
                "id": r.id,
                "assignment_id": r.id,  # Add assignment_id for reference
                "package_type": actual_package_type,
                "name": package_name,
                "service_name": service_name,  # Fetched from Service table
                "service_id": service_id,  # CRITICAL: Integer service_id for matching
                "status": r.status,
                "assigned_on": r.assigned_on.isoformat() if r.assigned_on else None,
                "expires_on": r.expires_on.isoformat() if r.expires_on else None,
            }

            # Enhanced student offer metadata loading
            if actual_package_type == 'student_offer':
                try:
                    from models import StudentOffer
                    student_offer = StudentOffer.query.get(r.package_reference_id)
                    if student_offer:
                        # Add discount percentage
                        if student_offer.discount_percentage:
                            package_data['discount_percentage'] = float(student_offer.discount_percentage)

                        # Get list of service IDs and names this offer applies to
                        if hasattr(student_offer, 'student_offer_services'):
                            applicable_service_ids = [sos.service_id for sos in student_offer.student_offer_services]
                            package_data['applicable_service_ids'] = applicable_service_ids

                            # Get service names for display
                            applicable_services = []
                            for sos in student_offer.student_offer_services:
                                if sos.service:
                                    applicable_services.append(sos.service.name)
                            package_data['applicable_service_names'] = ', '.join(applicable_services) if applicable_services else 'All Services'

                        # Add student offer specific fields
                        package_data['valid_from'] = student_offer.valid_from.strftime('%b %d, %Y') if student_offer.valid_from else None
                        package_data['valid_to'] = student_offer.valid_to.strftime('%b %d, %Y') if student_offer.valid_to else None
                        package_data['valid_days'] = student_offer.valid_days or 'All Days'
                        package_data['conditions'] = student_offer.conditions or 'Standard terms apply'
                        package_data['package_price'] = float(student_offer.price) if student_offer.price else 0

                        app.logger.info(f"✅ API Student offer {package_data['name']}: {package_data.get('discount_percentage', 0)}% off, valid {package_data['valid_days']}, applies to: {package_data.get('applicable_service_names', 'N/A')}")
                except Exception as e:
                    app.logger.error(f"Error getting student offer details in API: {e}")

            # CRITICAL FIX: Check PackageBenefitTracker first for accurate session data
            benefit_tracker = None
            if hasattr(r, 'package_benefits') and r.package_benefits:
                # Get the active benefit tracker for this assignment
                for bt in r.package_benefits:
                    if bt.is_active:
                        benefit_tracker = bt
                        break
                # If no active tracker, get the most recent one
                if not benefit_tracker and r.package_benefits:
                    benefit_tracker = r.package_benefits[0]

            # Add sessions data if applicable
            if benefit_tracker and benefit_tracker.benefit_type in ['free', 'discount']:
                # Use PackageBenefitTracker data (more accurate)
                package_data["sessions"] = {
                    "total": int(benefit_tracker.total_allocated or 0),
                    "used": int(benefit_tracker.used_count or 0),
                    "remaining": int(benefit_tracker.remaining_count or 0)
                }
                app.logger.info(f"✅ Using PackageBenefitTracker for assignment {r.id}: {package_data['sessions']}")
            elif r.total_sessions is not None:
                # Fallback to ServicePackageAssignment data
                package_data["sessions"] = {
                    "total": int(r.total_sessions or 0),
                    "used": int(r.used_sessions or 0),
                    "remaining": int((r.remaining_sessions
                                      if r.remaining_sessions is not None
                                      else (r.total_sessions or 0) - (r.used_sessions or 0)) or 0),
                }
                app.logger.info(f"⚠️ Using ServicePackageAssignment for assignment {r.id}: {package_data['sessions']}")

            # Add credit data if applicable
            if benefit_tracker and benefit_tracker.benefit_type == 'prepaid':
                # Use PackageBenefitTracker for prepaid credit
                package_data["credit"] = {
                    "total": float(benefit_tracker.balance_total or 0.0),
                    "remaining": float(benefit_tracker.balance_remaining or 0.0),
                }
                app.logger.info(f"✅ Using PackageBenefitTracker credit for assignment {r.id}: {package_data['credit']}")
            elif r.credit_amount is not None:
                # Fallback to ServicePackageAssignment credit data
                package_data["credit"] = {
                    "total": float(r.credit_amount or 0.0),
                    "remaining": float(r.remaining_credit or 0.0),
                }
                app.logger.info(f"⚠️ Using ServicePackageAssignment credit for assignment {r.id}: {package_data['credit']}")

            # Add membership services and usage tracking if applicable
            if actual_package_type == 'membership':
                try:
                    from models import PackageUsageHistory
                    package_template = r.get_package_template()
                    if package_template and hasattr(package_template, 'membership_services'):
                        membership_services = []
                        for ms in package_template.membership_services:
                            membership_services.append({
                                'service_id': ms.service_id,
                                'service_name': ms.service.name if ms.service else 'Unknown'
                            })
                        package_data['services'] = membership_services
                        app.logger.info(f"✅ Added {len(membership_services)} services to membership package {r.id}")

                    # Count total membership usage (unlimited sessions used)
                    if benefit_tracker:
                        total_usage = PackageUsageHistory.query.filter(
                            PackageUsageHistory.package_benefit_id == benefit_tracker.id,
                            PackageUsageHistory.benefit_type == 'unlimited',
                            PackageUsageHistory.transaction_type == 'use'
                        ).count()
                        package_data['usage_count'] = total_usage
                        app.logger.info(f"✅ Membership usage count: {total_usage} sessions")
                except Exception as e:
                    app.logger.error(f"Error loading membership services for assignment {r.id}: {e}")
                    package_data['services'] = []
                    package_data['usage_count'] = 0

            packages_list.append(package_data)

        # If no trackers found, try getting assignments directly as fallback
        if not packages_list:
            app.logger.warning(f"No benefit trackers found, checking assignments for customer {customer_id}")
            assignments = ServicePackageAssignment.query.filter_by(
                customer_id=customer_id,
                status='active'
            ).all()

            app.logger.info(f"Found {len(assignments)} active assignments for customer {customer_id}")

            for r in assignments:
                # Build package info from assignment
                package_name = None
                if hasattr(r, 'package_name') and r.package_name:
                    package_name = r.package_name
                elif hasattr(r, 'package_display_name') and r.package_display_name:
                    package_name = r.package_display_name
                elif hasattr(r, 'name') and r.name:
                    package_name = r.name

                if not package_name:
                    try:
                        package_template = r.get_package_template()
                        if package_template:
                            if hasattr(package_template, 'name') and package_template.name:
                                package_name = package_template.name
                            elif hasattr(package_template, 'package_name') and package_template.package_name:
                                package_name = package_template.package_name
                    except:
                        pass

                if not package_name:
                    pkg_type = r.package_type if hasattr(r, 'package_type') and r.package_type else "package"
                    package_name = pkg_type.replace('_', ' ').title() + ' Package'

                service_id = r.service_id
                service_name = None
                if service_id:
                    service_obj = Service.query.get(service_id)
                    if service_obj:
                        service_name = service_obj.name

                actual_package_type = r.package_type if hasattr(r, 'package_type') and r.package_type else (
                    "service_package" if r.total_sessions else "prepaid" if r.credit_amount is not None else "membership"
                )

                package_data = {
                    "id": r.id,
                    "assignment_id": r.id,
                    "package_type": actual_package_type,
                    "name": package_name,
                    "service_name": service_name,
                    "service_id": service_id,
                    "status": r.status,
                    "assigned_on": r.assigned_on.isoformat() if r.assigned_on else None,
                    "expires_on": r.expires_on.isoformat() if r.expires_on else None,
                }

                # Add session or credit data
                if r.total_sessions is not None:
                    package_data["sessions"] = {
                        "total": int(r.total_sessions or 0),
                        "used": int(r.used_sessions or 0),
                        "remaining": int(r.remaining_sessions or 0),
                    }
                elif r.credit_amount is not None:
                    package_data["credit"] = {
                        "total": float(r.credit_amount or 0.0),
                        "remaining": float(r.remaining_credit or 0.0),
                    }

                packages_list.append(package_data)

        payload = {"success": True, "packages": packages_list}
        app.logger.info(f"Returning {len(packages_list)} packages for customer {customer_id}")

        resp = jsonify(payload)
        resp.headers["Cache-Control"] = "no-store"
        return resp
    except Exception as e:
        app.logger.error(f"Error in get_customer_packages: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'packages': [],
            'total': 0
        }), 500


@app.route('/integrated-billing/edit/<int:invoice_id>')
@login_required
def edit_integrated_invoice(invoice_id):
    """Edit an existing invoice"""
    # Allow all authenticated users to edit invoices
    if not current_user.is_active:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        # Get the invoice
        invoice = EnhancedInvoice.query.get_or_404(invoice_id)
        
        # Get invoice items
        invoice_items = InvoiceItem.query.filter_by(invoice_id=invoice_id).all()
        
        # Get data for form
        customers = Customer.query.filter_by(is_active=True).order_by(Customer.first_name, Customer.last_name).all()
        services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
        staff_members = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()
        
        # Get inventory items
        inventory_items = []
        if InventoryProduct is not None:
            inventory_products = InventoryProduct.query.filter_by(is_active=True).all()
            for product in inventory_products:
                if product.total_stock > 0:
                    inventory_items.append(product)
        
        # Prepare invoice items data
        service_items = []
        product_items = []
        
        for item in invoice_items:
            if item.item_type == 'service':
                service_items.append({
                    'service_id': item.item_id,
                    'quantity': item.quantity,
                    'appointment_id': item.appointment_id,
                    'staff_id': item.staff_id,
                    'unit_price': item.unit_price,
                    'deduction_amount': item.deduction_amount or 0
                })
            elif item.item_type == 'inventory':
                product_items.append({
                    'product_id': item.product_id,
                    'batch_id': item.batch_id,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'staff_id': item.staff_id
                })
        
        # Get tax details from notes if available
        import json
        tax_details = {}
        try:
            tax_details = json.loads(invoice.notes) if invoice.notes else {}
        except:
            pass
        
        return render_template('edit_integrated_invoice.html',
                             invoice=invoice,
                             service_items=service_items,
                             product_items=product_items,
                             customers=customers,
                             services=services,
                             staff_members=staff_members,
                             inventory_items=inventory_items,
                             tax_details=tax_details)
                             
    except Exception as e:
        app.logger.error(f"Error loading invoice for edit: {str(e)}")
        flash(f'Error loading invoice: {str(e)}', 'danger')
        return redirect(url_for('integrated_billing'))


@app.route('/integrated-billing/update/<int:invoice_id>', methods=['POST'])
@login_required
def update_integrated_invoice(invoice_id):
    """Update an existing invoice"""
    # Allow all authenticated users to update invoices
    if not current_user.is_active:
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    try:
        # Get the invoice
        invoice = EnhancedInvoice.query.get_or_404(invoice_id)
        
        # Delete existing invoice items
        InvoiceItem.query.filter_by(invoice_id=invoice_id).delete()
        
        # Parse services data (same as create)
        services_data = []
        service_ids = request.form.getlist('service_ids[]')
        service_quantities = request.form.getlist('service_quantities[]')
        appointment_ids = request.form.getlist('appointment_ids[]')
        staff_ids = request.form.getlist('staff_ids[]')

        for i, service_id in enumerate(service_ids):
            if service_id and str(service_id).strip():
                staff_id = staff_ids[i] if i < len(staff_ids) and staff_ids[i] and str(staff_ids[i]).strip() else None
                if not staff_id:
                    return jsonify({
                        'success': False,
                        'message': f'Staff member is required for service #{i+1}. Please assign staff to all services.'
                    }), 400

                services_data.append({
                    'service_id': int(service_id),
                    'quantity': float(service_quantities[i]) if i < len(service_quantities) else 1,
                    'appointment_id': int(appointment_ids[i]) if i < len(appointment_ids) and appointment_ids[i] else None,
                    'staff_id': int(staff_id)
                })

        # Parse inventory data (same as create)
        inventory_data = []
        product_ids = request.form.getlist('product_ids[]')
        product_staff_ids = request.form.getlist('product_staff_ids[]')
        batch_ids = request.form.getlist('batch_ids[]')
        product_quantities = request.form.getlist('product_quantities[]')
        product_prices = request.form.getlist('product_prices[]')

        for i, product_id in enumerate(product_ids):
            if product_id and i < len(batch_ids) and batch_ids[i]:
                if i >= len(product_staff_ids) or not product_staff_ids[i]:
                    return jsonify({
                        'success': False,
                        'message': f'Staff member is required for product #{i+1}. Please assign staff to all products.'
                    }), 400

                inventory_data.append({
                    'product_id': int(product_id),
                    'batch_id': int(batch_ids[i]),
                    'quantity': float(product_quantities[i]) if i < len(product_quantities) else 1,
                    'unit_price': float(product_prices[i]) if i < len(product_prices) and product_prices[i] else 0,
                    'staff_id': int(product_staff_ids[i])
                })

        # Recalculate amounts (same logic as create)
        services_subtotal = sum(
            Service.query.get(s['service_id']).price * s['quantity'] 
            for s in services_data if Service.query.get(s['service_id'])
        )
        
        inventory_subtotal = sum(
            item['unit_price'] * item['quantity'] 
            for item in inventory_data
        )
        
        gross_subtotal = services_subtotal + inventory_subtotal
        
        # Update invoice fields
        invoice.services_subtotal = services_subtotal
        invoice.inventory_subtotal = inventory_subtotal
        invoice.gross_subtotal = gross_subtotal
        
        # Recalculate tax and totals
        cgst_rate = float(request.form.get('cgst_rate', 9)) / 100
        sgst_rate = float(request.form.get('sgst_rate', 9)) / 100
        igst_rate = float(request.form.get('igst_rate', 0)) / 100
        is_interstate = request.form.get('is_interstate') == 'on'
        
        discount_type = request.form.get('discount_type', 'amount')
        discount_value = float(request.form.get('discount_value', 0))
        
        if discount_type == 'percentage':
            discount_amount = (gross_subtotal * discount_value) / 100
        else:
            discount_amount = discount_value
            
        net_subtotal = max(0, gross_subtotal - discount_amount)
        
        total_gst_rate = igst_rate if is_interstate else (cgst_rate + sgst_rate)
        tax_amount = net_subtotal * total_gst_rate
        
        additional_charges = float(request.form.get('additional_charges', 0))
        tips_amount = float(request.form.get('tips_amount', 0))
        
        total_amount = net_subtotal + tax_amount + additional_charges + tips_amount
        
        # Update invoice
        invoice.net_subtotal = net_subtotal
        invoice.discount_amount = discount_amount
        invoice.tax_amount = tax_amount
        invoice.additional_charges = additional_charges
        invoice.tips_amount = tips_amount
        invoice.total_amount = total_amount
        invoice.balance_due = total_amount - invoice.amount_paid
        
        # Re-create invoice items
        for service_data in services_data:
            service = Service.query.get(service_data['service_id'])
            if service:
                staff_id = service_data.get('staff_id')
                staff_name = None
                if staff_id:
                    staff = User.query.get(staff_id)
                    if staff:
                        staff_name = staff.full_name
                
                original_price = service.price * service_data['quantity']
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    item_type='service',
                    item_id=service.id,
                    appointment_id=service_data.get('appointment_id'),
                    item_name=service.name,
                    description=service.description or '',
                    quantity=service_data['quantity'],
                    unit_price=service.price,
                    original_amount=original_price,
                    final_amount=original_price,
                    staff_revenue_price=original_price,
                    staff_id=staff_id,
                    staff_name=staff_name
                )
                db.session.add(item)
        
        for item_data in inventory_data:
            batch = InventoryBatch.query.get(item_data['batch_id'])
            product = InventoryProduct.query.get(item_data['product_id'])
            
            if batch and product:
                staff_id = item_data.get('staff_id')
                staff_name = None
                if staff_id:
                    staff = User.query.get(staff_id)
                    if staff:
                        staff_name = staff.full_name
                
                product_amount = item_data['unit_price'] * item_data['quantity']
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    item_type='inventory',
                    item_id=product.id,
                    product_id=product.id,
                    batch_id=batch.id,
                    item_name=product.name,
                    description=f"Batch: {batch.batch_name}",
                    batch_name=batch.batch_name,
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    original_amount=product_amount,
                    final_amount=product_amount,
                    staff_revenue_price=product_amount,
                    staff_id=staff_id,
                    staff_name=staff_name
                )
                db.session.add(item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Invoice updated successfully',
            'invoice_id': invoice.id,
            'invoice_number': invoice.invoice_number
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating invoice: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error updating invoice: {str(e)}'}), 500


@app.route('/integrated-billing/print-invoice/<int:invoice_id>')
@login_required
def print_professional_invoice(invoice_id):
    """Generate and download PDF invoice"""
    from flask import make_response
    import io

    # Allow all authenticated users to print invoices
    if not current_user.is_active:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from models import EnhancedInvoice, InvoiceItem
    invoice = EnhancedInvoice.query.get_or_404(invoice_id)
    invoice_items = InvoiceItem.query.filter_by(invoice_id=invoice_id).all()

    # Parse tax details from notes
    import json
    tax_details = {}
    try:
        tax_details = json.loads(invoice.notes) if invoice.notes else {}
    except:
        pass

    # Fetch staff names for services
    staff_names = {}
    service_items = [item for item in invoice_items if item.item_type == 'service']
    service_staff_ids = {item.staff_id for item in service_items if item.staff_id}
    if service_staff_ids:
        from models import User
        staffs = User.query.filter(User.id.in_(service_staff_ids)).all()
        staff_names = {staff.id: staff.full_name for staff in staffs}

    # Render HTML template
    html_string = render_template('professional_invoice_print.html',
                                 invoice=invoice,
                                 invoice_items=invoice_items,
                                 tax_details=tax_details,
                                 staff_names=staff_names,
                                 total_amount_words=number_to_words)

    try:
        # Generate PDF from HTML
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration

        # Create font configuration
        font_config = FontConfiguration()

        # Generate PDF
        pdf_buffer = io.BytesIO()
        HTML(string=html_string, base_url=request.url_root).write_pdf(
            pdf_buffer,
            font_config=font_config
        )
        pdf_buffer.seek(0)

        # Create response with PDF
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.invoice_number}.pdf"'

        return response

    except Exception as e:
        app.logger.error(f"PDF generation error: {e}")
        # Fallback to HTML view if PDF generation fails
        return html_string

@app.route('/api/invoice-preview', methods=['POST'])
@login_required
def generate_invoice_preview():
    """Generate professional invoice preview"""
    # Allow all authenticated users to preview invoices
    if not current_user.is_active:
        return jsonify({'error': 'Access denied'}), 403

    try:
        data = request.json or {}
        # Generate preview HTML
        preview_html = f"""
        <div class="professional-invoice">
            <div class="invoice-header text-center mb-4">
                <h2>TAX INVOICE</h2>
                <h4>Your Spa & Wellness Center</h4>
                <p>GST No: 29XXXXX1234Z1Z5 | Contact: +91-XXXXXXXXXX</p>
            </div>
            <div class="row mb-3">
                <div class="col-6">
                    <strong>Bill To:</strong><br>
                    {data.get('customer_name', 'Customer Name')}<br>
                    Contact: {data.get('customer_phone', 'Phone Number')}
                </div>
                <div class="col-6 text-end">
                    <strong>Invoice Details:</strong><br>
                    Invoice No: PREVIEW<br>
                    Date: {datetime.now().strftime('%d-%m-%Y')}<br>
                    GST Treatment: {'Interstate' if data.get('is_interstate') else 'Intrastate'}
                </div>
            </div>
            <div class="tax-calculation-preview">
                <table class="table table-bordered">
                    <thead class="table-dark">
                        <tr>
                            <th>Description</th>
                            <th>Qty</th>
                            <th>Rate</th>
                            <th>Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td colspan="4" class="text-center text-muted">Preview items will appear here</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        """

        return jsonify({
            'success': True,
            'preview_html': preview_html
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/invoices')
@app.route('/invoices/list')
@login_required
def list_integrated_invoices():
    """List all invoices with filters and search"""
    if not current_user.is_active:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Base query
    query = EnhancedInvoice.query
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter_by(payment_status=status_filter)
    
    if search_query:
        query = query.join(Customer).filter(
            db.or_(
                EnhancedInvoice.invoice_number.ilike(f'%{search_query}%'),
                Customer.first_name.ilike(f'%{search_query}%'),
                Customer.last_name.ilike(f'%{search_query}%'),
                Customer.phone.ilike(f'%{search_query}%')
            )
        )
    
    if date_from:
        from datetime import datetime
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        query = query.filter(EnhancedInvoice.invoice_date >= date_from_obj)
    
    if date_to:
        from datetime import datetime
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
        query = query.filter(EnhancedInvoice.invoice_date <= date_to_obj)
    
    # Order by date descending
    invoices = query.order_by(EnhancedInvoice.invoice_date.desc()).all()
    
    # Calculate summary stats
    total_invoices = len(invoices)
    total_amount = sum(inv.total_amount for inv in invoices)
    total_paid = sum(inv.amount_paid for inv in invoices)
    total_pending = sum(inv.balance_due for inv in invoices)
    
    return render_template('invoices_list.html',
                         invoices=invoices,
                         total_invoices=total_invoices,
                         total_amount=total_amount,
                         total_paid=total_paid,
                         total_pending=total_pending,
                         status_filter=status_filter,
                         search_query=search_query,
                         date_from=date_from,
                         date_to=date_to)

# Legacy billing compatibility route
@app.route('/billing/integrated')
@login_required
def billing_integrated_redirect():
    """Redirect old billing to new integrated billing"""
    return redirect(url_for('integrated_billing'))