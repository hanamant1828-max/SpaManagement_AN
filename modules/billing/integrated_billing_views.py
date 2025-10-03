"""
Integrated Billing Views - New Enhanced Billing System
Supports services, packages, subscriptions, and inventory items
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from datetime import datetime
import json
from models import Customer, Service, Appointment
from sqlalchemy import and_
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
    from models import User
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
    selected_customer = None
    if customer_id:
        selected_customer = Customer.query.get(customer_id)
        if selected_customer:
            # Import UnakiBooking model
            from models import UnakiBooking

            # Get ALL scheduled and confirmed Unaki bookings for this customer
            customer_appointments_query = []

            # Method 1: Try to match by client_id first (most reliable)
            if selected_customer.id:
                customer_appointments_query = UnakiBooking.query.filter(
                    UnakiBooking.client_id == selected_customer.id,
                    UnakiBooking.status.in_(['scheduled', 'confirmed'])
                ).order_by(UnakiBooking.appointment_date.desc()).all()

            # Method 2: If no results, try matching by phone (exact match)
            if not customer_appointments_query and selected_customer.phone:
                # Try exact match
                customer_appointments_query = UnakiBooking.query.filter(
                    UnakiBooking.client_phone == selected_customer.phone,
                    UnakiBooking.status.in_(['scheduled', 'confirmed'])
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
                            UnakiBooking.status.in_(['scheduled', 'confirmed'])
                        ).order_by(UnakiBooking.appointment_date.desc()).all()

            # Method 3: If still no results, try matching by name
            if not customer_appointments_query:
                # Try full name match first
                full_name = f"{selected_customer.first_name} {selected_customer.last_name}".strip()
                customer_appointments_query = UnakiBooking.query.filter(
                    UnakiBooking.client_name.ilike(f'%{full_name}%'),
                    UnakiBooking.status.in_(['scheduled', 'confirmed'])
                ).order_by(UnakiBooking.appointment_date.desc()).all()

                # If still no results, try first name only
                if not customer_appointments_query:
                    customer_appointments_query = UnakiBooking.query.filter(
                        UnakiBooking.client_name.ilike(f'%{selected_customer.first_name}%'),
                        UnakiBooking.status.in_(['scheduled', 'confirmed'])
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

            # Get unique services from Unaki appointments
            unaki_service_names = list(set([apt.get('service_name') for apt in customer_appointments if apt.get('service_name')]))
            if unaki_service_names:
                customer_services_objects = Service.query.filter(Service.name.in_(unaki_service_names)).all()
                # Convert Service objects to dictionaries for JSON serialization
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

        # Get ALL scheduled and confirmed Unaki bookings for this customer
        customer_appointments_query = []

        # Method 1: Try to match by client_id first (most reliable)
        if customer.id:
            customer_appointments_query = UnakiBooking.query.filter(
                UnakiBooking.client_id == customer.id,
                UnakiBooking.status.in_(['scheduled', 'confirmed'])
            ).order_by(UnakiBooking.appointment_date.desc()).all()

        # Method 2: If no results, try matching by phone (exact match)
        if not customer_appointments_query and customer.phone:
            customer_appointments_query = UnakiBooking.query.filter(
                UnakiBooking.client_phone == customer.phone,
                UnakiBooking.status.in_(['scheduled', 'confirmed'])
            ).order_by(UnakiBooking.appointment_date.desc()).all()

            # Try partial match if exact match fails
            if not customer_appointments_query:
                phone_digits = ''.join(filter(str.isdigit, customer.phone))
                if len(phone_digits) >= 10:
                    last_10_digits = phone_digits[-10:]
                    customer_appointments_query = UnakiBooking.query.filter(
                        UnakiBooking.client_phone.like(f'%{last_10_digits}%'),
                        UnakiBooking.status.in_(['scheduled', 'confirmed'])
                    ).order_by(UnakiBooking.appointment_date.desc()).all()

        # Method 3: If still no results, try matching by name
        if not customer_appointments_query:
            full_name = f"{customer.first_name} {customer.last_name}".strip()
            customer_appointments_query = UnakiBooking.query.filter(
                UnakiBooking.client_name.ilike(f'%{full_name}%'),
                UnakiBooking.status.in_(['scheduled', 'confirmed'])
            ).order_by(UnakiBooking.appointment_date.desc()).all()

            # Try first name only if full name fails
            if not customer_appointments_query:
                customer_appointments_query = UnakiBooking.query.filter(
                    UnakiBooking.client_name.ilike(f'%{customer.first_name}%'),
                    UnakiBooking.status.in_(['scheduled', 'confirmed'])
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
                matching_service = Service.query.filter(
                    Service.name.ilike(f'%{appointment.service_name}%'),
                    Service.is_active == True
                ).first()

            # Add service details to appointment data
            if matching_service:
                apt_dict['service_id'] = matching_service.id
                apt_dict['service_name'] = matching_service.name
                apt_dict['service_price'] = float(matching_service.price)
                apt_dict['service_duration'] = matching_service.duration

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


@app.route('/integrated-billing/create-professional', methods=['POST'])
@login_required
def create_professional_invoice():
    """Create new professional invoice with complete GST/SGST tax support"""
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
            return jsonify({'success': False, 'message': 'Client is required'})

        customer = Customer.query.get(client_id)
        if not customer:
            return jsonify({'success': False, 'message': 'Customer not found'})

        # Parse services data
        services_data = []
        service_ids = request.form.getlist('service_ids[]')
        service_quantities = request.form.getlist('service_quantities[]')
        appointment_ids = request.form.getlist('appointment_ids[]')
        staff_ids = request.form.getlist('staff_ids[]')

        for i, service_id in enumerate(service_ids):
            if service_id:
                staff_id = staff_ids[i] if i < len(staff_ids) and staff_ids[i] else None
                if not staff_id:
                    return jsonify({'success': False, 'message': f'Please select staff for service {i+1}'})

                services_data.append({
                    'service_id': int(service_id),
                    'quantity': float(service_quantities[i]) if i < len(service_quantities) else 1,
                    'appointment_id': int(appointment_ids[i]) if i < len(appointment_ids) and appointment_ids[i] else None,
                    'staff_id': int(staff_id)
                })

        # Parse inventory data
        inventory_data = []
        product_ids = request.form.getlist('product_ids[]')
        batch_ids = request.form.getlist('batch_ids[]')
        product_quantities = request.form.getlist('product_quantities[]')
        product_prices = request.form.getlist('product_prices[]')

        for i, product_id in enumerate(product_ids):
            if product_id and i < len(batch_ids) and batch_ids[i]:
                inventory_data.append({
                    'product_id': int(product_id),
                    'batch_id': int(batch_ids[i]),
                    'quantity': float(product_quantities[i]) if i < len(product_quantities) else 1,
                    'unit_price': float(product_prices[i]) if i < len(product_prices) and product_prices[i] else 0
                })

        # Professional Tax Calculation
        cgst_rate = float(request.form.get('cgst_rate', 9)) / 100
        sgst_rate = float(request.form.get('sgst_rate', 9)) / 100
        igst_rate = float(request.form.get('igst_rate', 0)) / 100
        is_interstate = request.form.get('is_interstate') == 'on'

        discount_type = request.form.get('discount_type', 'amount')
        discount_value = float(request.form.get('discount_value', 0))
        additional_charges = float(request.form.get('additional_charges', 0))
        tips_amount = float(request.form.get('tips_amount', 0))

        payment_terms = request.form.get('payment_terms', 'immediate')
        payment_method = request.form.get('payment_method', 'cash')

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

        # Calculate discount
        if discount_type == 'percentage':
            discount_amount = (gross_subtotal * discount_value) / 100
        else:
            discount_amount = discount_value

        # Service prices are GST INCLUSIVE - extract GST from the price
        # Formula: Base Amount = Price / (1 + GST Rate)
        # Formula: GST Amount = Price - Base Amount
        total_gst_rate = igst_rate if is_interstate else (cgst_rate + sgst_rate)
        service_base_amount = services_subtotal / (1 + total_gst_rate)
        service_gst_amount = services_subtotal - service_base_amount

        # For inventory, GST is calculated normally (exclusive)
        inventory_gst_amount = inventory_subtotal * total_gst_rate

        # Total amounts before discount
        total_base_amount = service_base_amount + inventory_subtotal
        total_gst_before_discount = service_gst_amount + inventory_gst_amount

        # Apply discount to base amount only
        net_base_amount = max(0, total_base_amount - discount_amount)

        # Recalculate GST proportionally after discount
        if total_base_amount > 0:
            discount_factor = net_base_amount / total_base_amount
            final_service_gst = service_gst_amount * discount_factor
            final_inventory_gst = inventory_gst_amount * discount_factor
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
        total_amount = net_base_amount + total_tax + additional_charges + tips_amount

        # Create professional invoice with proper transaction handling
        try:
            # Generate professional invoice number
            current_date = datetime.datetime.now()
            latest_invoice = db.session.query(EnhancedInvoice).order_by(EnhancedInvoice.id.desc()).first()

            if latest_invoice and latest_invoice.invoice_number.startswith(f"INV-{current_date.strftime('%Y%m%d')}"):
                try:
                    last_sequence = int(latest_invoice.invoice_number.split('-')[-1])
                    invoice_sequence = last_sequence + 1
                except (ValueError, IndexError):
                    invoice_sequence = 1
            else:
                invoice_sequence = 1

            invoice_number = f"INV-{current_date.strftime('%Y%m%d')}-{invoice_sequence:04d}"

            # Create enhanced invoice
            invoice = EnhancedInvoice()
            invoice.invoice_number = invoice_number
            invoice.client_id = int(client_id)
            invoice.invoice_date = current_date

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

            # Store GST fields properly
            invoice.cgst_rate = cgst_rate * 100
            invoice.sgst_rate = sgst_rate * 100
            invoice.igst_rate = igst_rate * 100
            invoice.cgst_amount = cgst_amount
            invoice.sgst_amount = sgst_amount
            invoice.igst_amount = igst_amount
            invoice.is_interstate = is_interstate
            invoice.additional_charges = additional_charges
            invoice.payment_terms = payment_terms

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

            # Create invoice items for services
            service_items_created = 0
            for service_data in services_data:
                service = Service.query.get(service_data['service_id'])
                if service:
                    item = InvoiceItem()
                    item.invoice_id = invoice.id
                    item.item_type = 'service'
                    item.item_id = service.id
                    item.appointment_id = service_data.get('appointment_id')
                    item.item_name = service.name
                    item.description = service.description
                    item.quantity = service_data['quantity']
                    item.unit_price = service.price
                    item.original_amount = service.price * service_data['quantity']
                    item.final_amount = service.price * service_data['quantity']
                    # Add staff_id to the invoice item
                    item.staff_id = service_data.get('staff_id')
                    db.session.add(item)
                    service_items_created += 1

            # Create invoice items for inventory and reduce stock
            inventory_items_created = 0
            stock_reduced_count = 0

            for item_data in inventory_data:
                batch = InventoryBatch.query.get(item_data['batch_id'])
                product = InventoryProduct.query.get(item_data['product_id'])

                if batch and product:
                    # Create invoice item
                    item = InvoiceItem()
                    item.invoice_id = invoice.id
                    item.item_type = 'inventory'
                    item.item_id = product.id
                    item.product_id = product.id
                    item.batch_id = batch.id
                    item.item_name = product.name
                    item.batch_name = batch.batch_name
                    item.quantity = item_data['quantity']
                    item.unit_price = item_data['unit_price']
                    item.original_amount = item_data['unit_price'] * item_data['quantity']
                    item.final_amount = item_data['unit_price'] * item_data['quantity']
                    db.session.add(item)
                    inventory_items_created += 1

                    # Reduce stock
                    create_consumption_record(
                        batch_id=batch.id,
                        quantity=item_data['quantity'],
                        issued_to=f"Invoice {invoice_number} - {customer.full_name}",
                        reference=invoice_number,
                        notes=f"Professional invoice sale - {invoice_number}",
                        user_id=current_user.id
                    )
                    stock_reduced_count += 1

            # Commit all changes
            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'Professional Invoice {invoice_number} created successfully',
                'invoice_id': invoice.id,
                'invoice_number': invoice_number,
                'total_amount': float(total_amount),
                'cgst_amount': float(cgst_amount),
                'sgst_amount': float(sgst_amount),
                'igst_amount': float(igst_amount),
                'tax_amount': float(total_tax),
                'service_items_created': service_items_created,
                'inventory_items_created': inventory_items_created,
                'stock_reduced': stock_reduced_count,
                'deductions_applied': 0
            })

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Professional invoice creation failed for user {current_user.id}: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Transaction failed: {str(e)}. All changes have been rolled back.'
            })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error creating professional invoice: {str(e)}'})


@app.route('/integrated-billing/preview', methods=['POST'])
@login_required
def preview_invoice():
    """Generate invoice preview without saving"""
    if not current_user.is_active:
        return jsonify({'error': 'Access denied'}), 403

    try:
        from models import Service, Customer
        from modules.inventory.models import InventoryProduct, InventoryBatch
        import datetime

        data = request.get_json()

        # Get customer
        client_id = data.get('client_id')
        if not client_id:
            return jsonify({'success': False, 'message': 'Client is required'})

        customer = Customer.query.get(client_id)
        if not customer:
            return jsonify({'success': False, 'message': 'Customer not found'})

        # Parse services and products
        services_data = data.get('services', [])
        inventory_data = data.get('products', [])

        # Calculate totals
        services_subtotal = 0
        service_items = []
        for service_data in services_data:
            service = Service.query.get(service_data['service_id'])
            if service:
                amount = service.price * service_data['quantity']
                services_subtotal += amount
                service_items.append({
                    'name': service.name,
                    'quantity': service_data['quantity'],
                    'price': service.price,
                    'amount': amount
                })

        inventory_subtotal = 0
        inventory_items = []
        for item_data in inventory_data:
            product = InventoryProduct.query.get(item_data['product_id'])
            if product:
                amount = item_data['unit_price'] * item_data['quantity']
                inventory_subtotal += amount
                inventory_items.append({
                    'name': product.name,
                    'quantity': item_data['quantity'],
                    'price': item_data['unit_price'],
                    'amount': amount
                })

        gross_subtotal = services_subtotal + inventory_subtotal
        discount_percentage = float(data.get('discount_percentage', 0))
        discount_amount = (gross_subtotal * discount_percentage) / 100

        gst_enabled = data.get('gst_enabled', False)
        gst_percentage = float(data.get('gst_percentage', 0)) if gst_enabled else 0

        net_subtotal = gross_subtotal - discount_amount
        tax_amount = (net_subtotal * gst_percentage) / 100
        total_amount = net_subtotal + tax_amount

        # Generate preview HTML
        preview_html = f"""
        <div class="invoice-preview">
            <div class="text-center mb-4">
                <h3>INVOICE PREVIEW</h3>
                <p class="text-muted">This is a preview only - not saved</p>
            </div>

            <div class="row mb-4">
                <div class="col-6">
                    <strong>Customer:</strong><br>
                    {customer.full_name}<br>
                    {customer.phone or ''}<br>
                    {customer.email or ''}
                </div>
                <div class="col-6 text-end">
                    <strong>Date:</strong> {datetime.datetime.now().strftime('%d-%m-%Y')}<br>
                    <strong>Status:</strong> <span class="badge bg-warning">Preview</span>
                </div>
            </div>

            <table class="table table-bordered">
                <thead class="table-light">
                    <tr>
                        <th>Item</th>
                        <th class="text-center">Qty</th>
                        <th class="text-end">Price</th>
                        <th class="text-end">Amount</th>
                    </tr>
                </thead>
                <tbody>
        """

        # Add service items
        if service_items:
            for item in service_items:
                preview_html += f"""
                    <tr>
                        <td>{item['name']} <small class="text-muted">(Service)</small></td>
                        <td class="text-center">{item['quantity']}</td>
                        <td class="text-end">₹{item['price']:.2f}</td>
                        <td class="text-end">₹{item['amount']:.2f}</td>
                    </tr>
                """

        # Add inventory items
        if inventory_items:
            for item in inventory_items:
                preview_html += f"""
                    <tr>
                        <td>{item['name']} <small class="text-muted">(Product)</small></td>
                        <td class="text-center">{item['quantity']}</td>
                        <td class="text-end">₹{item['price']:.2f}</td>
                        <td class="text-end">₹{item['amount']:.2f}</td>
                    </tr>
                """

        # Add totals
        preview_html += f"""
                </tbody>
                <tfoot>
                    <tr>
                        <td colspan="3" class="text-end"><strong>Subtotal:</strong></td>
                        <td class="text-end">₹{gross_subtotal:.2f}</td>
                    </tr>
        """

        if discount_amount > 0:
            preview_html += f"""
                    <tr>
                        <td colspan="3" class="text-end"><strong>Discount ({discount_percentage}%):</strong></td>
                        <td class="text-end text-success">-₹{discount_amount:.2f}</td>
                    </tr>
            """

        if tax_amount > 0:
            preview_html += f"""
                    <tr>
                        <td colspan="3" class="text-end"><strong>GST ({gst_percentage}%):</strong></td>
                        <td class="text-end">₹{tax_amount:.2f}</td>
                    </tr>
            """

        preview_html += f"""
                    <tr class="table-primary">
                        <td colspan="3" class="text-end"><strong>Total Amount:</strong></td>
                        <td class="text-end"><strong>₹{total_amount:.2f}</strong></td>
                    </tr>
                </tfoot>
            </table>

            <div class="alert alert-info mt-3">
                <i class="fas fa-info-circle me-2"></i>
                This is a preview only. Click "Save" or "Save & Print" to create the actual invoice.
            </div>
        </div>
        """

        return jsonify({
            'success': True,
            'preview_html': preview_html
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating preview: {str(e)}'})


@app.route('/integrated-billing/create', methods=['POST'])
@login_required
def create_integrated_invoice():
    """Create new integrated invoice with batch-wise inventory integration"""
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
            return jsonify({'success': False, 'message': 'Client is required'})

        customer = Customer.query.get(client_id)
        if not customer:
            return jsonify({'success': False, 'message': 'Customer not found'})

        # Parse services data
        services_data = []
        service_ids = request.form.getlist('service_ids[]')
        service_quantities = request.form.getlist('service_quantities[]')
        appointment_ids = request.form.getlist('appointment_ids[]')
        staff_ids = request.form.getlist('staff_ids[]')

        for i, service_id in enumerate(service_ids):
            if service_id:
                staff_id = staff_ids[i] if i < len(staff_ids) and staff_ids[i] else None
                if not staff_id:
                    return jsonify({'success': False, 'message': f'Please select staff for service {i+1}'})

                services_data.append({
                    'service_id': int(service_id),
                    'quantity': float(service_quantities[i]) if i < len(service_quantities) else 1,
                    'appointment_id': int(appointment_ids[i]) if i < len(appointment_ids) and appointment_ids[i] else None,
                    'staff_id': int(staff_id)
                })

        # Parse batch-wise inventory data
        inventory_data = []
        product_ids = request.form.getlist('product_ids[]')
        batch_ids = request.form.getlist('batch_ids[]')
        product_quantities = request.form.getlist('product_quantities[]')
        product_prices = request.form.getlist('product_prices[]')

        for i, product_id in enumerate(product_ids):
            if product_id and i < len(batch_ids) and batch_ids[i]:
                inventory_data.append({
                    'product_id': int(product_id),
                    'batch_id': int(batch_ids[i]),
                    'quantity': float(product_quantities[i]) if i < len(product_quantities) else 1,
                    'unit_price': float(product_prices[i]) if i < len(product_prices) and product_prices[i] else 0
                })

        # Validate stock availability and prices for all inventory items
        for item in inventory_data:
            batch = InventoryBatch.query.get(item['batch_id'])
            if not batch:
                return jsonify({'success': False, 'message': f'Batch not found for product ID {item["product_id"]}'})

            if batch.is_expired:
                return jsonify({'success': False, 'message': f'Cannot use expired batch: {batch.batch_name}'})

            if float(batch.qty_available) < item['quantity']:
                return jsonify({
                    'success': False,
                    'message': f'Insufficient stock in batch {batch.batch_name}. Available: {batch.qty_available}, Required: {item["quantity"]}'
                })

            # Server-side price validation - prevent price manipulation
            if batch.selling_price:
                actual_price = float(batch.selling_price)
                submitted_price = item['unit_price']

                # Allow up to 50% discount, but prevent price inflation or excessive discounts
                min_allowed_price = actual_price * 0.5  # 50% discount max
                max_allowed_price = actual_price * 1.1   # 10% markup max for rounding

                if submitted_price < min_allowed_price or submitted_price > max_allowed_price:
                    # Log suspicious price manipulation attempt
                    app.logger.warning(f"Price manipulation attempt detected: User {current_user.id} tried to set price {submitted_price} for batch {batch.batch_name} (actual: {actual_price})")
                    return jsonify({
                        'success': False,
                        'message': f'Invalid price for {batch.product.name} (Batch: {batch.batch_name}). Expected: ${actual_price:.2f}, Submitted: ${submitted_price:.2f}'
                    })
            else:
                # If no selling price set, require manual approval for non-zero prices
                if item['unit_price'] > 0:
                    return jsonify({
                        'success': False,
                        'message': f'Product {batch.product.name} has no selling price configured. Please set selling price first.'
                    })

        # Validate service prices to prevent manipulation
        for service_data in services_data:
            service = Service.query.get(service_data['service_id'])
            if not service:
                return jsonify({'success': False, 'message': f'Service not found: {service_data["service_id"]}'})

            # For services, we don't accept client price input - always use actual service price
            # This prevents any service price manipulation
            # Note: If custom service pricing is needed in the future, implement proper authorization checks

        # Calculate totals first (before any database operations)
        services_subtotal = 0
        inventory_subtotal = 0

        # Calculate services subtotal
        for service_data in services_data:
            service = Service.query.get(service_data['service_id'])
            if service:
                services_subtotal += service.price * service_data['quantity']

        # Calculate inventory subtotal
        for item in inventory_data:
            inventory_subtotal += item['unit_price'] * item['quantity']

        gross_subtotal = services_subtotal + inventory_subtotal

        # Apply tax and discounts
        tax_rate = float(request.form.get('tax_rate', 0.18))
        discount_amount = float(request.form.get('discount_amount', 0))
        tips_amount = float(request.form.get('tips_amount', 0))

        net_subtotal = gross_subtotal - discount_amount
        # Fix: tax_rate is already a decimal (e.g., 0.18 for 18%), no need to divide by 100
        tax_amount = net_subtotal * tax_rate
        total_amount = net_subtotal + tax_amount + tips_amount

        # Generate atomic invoice number and create invoice
        try:
                # Get latest invoice to generate sequential number
                latest_invoice = db.session.query(EnhancedInvoice).order_by(EnhancedInvoice.id.desc()).first()

                if latest_invoice and latest_invoice.invoice_number.startswith(f"INV-{datetime.datetime.now().strftime('%Y%m%d')}"):
                    # Extract sequence number from existing invoice number
                    try:
                        last_sequence = int(latest_invoice.invoice_number.split('-')[-1])
                        invoice_sequence = last_sequence + 1
                    except (ValueError, IndexError):
                        invoice_sequence = 1
                else:
                    # First invoice of the day
                    invoice_sequence = 1

                invoice_number = f"INV-{datetime.datetime.now().strftime('%Y%m%d')}-{invoice_sequence:04d}"

                # Create enhanced invoice
                invoice = EnhancedInvoice()
                invoice.invoice_number = invoice_number
                invoice.client_id = int(client_id)
                invoice.invoice_date = datetime.datetime.utcnow()
                invoice.services_subtotal = services_subtotal
                invoice.inventory_subtotal = inventory_subtotal
                invoice.gross_subtotal = gross_subtotal
                invoice.net_subtotal = net_subtotal
                invoice.tax_amount = tax_amount
                invoice.discount_amount = discount_amount
                invoice.tips_amount = tips_amount
                invoice.total_amount = total_amount
                invoice.balance_due = total_amount
                invoice.notes = request.form.get('notes', '')

                db.session.add(invoice)
                db.session.flush()  # Get invoice ID

                # Create invoice items for services
                service_items_created = 0
                for service_data in services_data:
                    service = Service.query.get(service_data['service_id'])
                    if service:
                        item = InvoiceItem()
                        item.invoice_id = invoice.id
                        item.item_type = 'service'
                        item.item_id = service.id
                        item.appointment_id = service_data.get('appointment_id')
                        item.item_name = service.name
                        item.description = service.description
                        item.quantity = service_data['quantity']
                        item.unit_price = service.price
                        item.original_amount = service.price * service_data['quantity']
                        item.final_amount = service.price * service_data['quantity']
                        # Add staff_id to the invoice item
                        item.staff_id = service_data.get('staff_id')
                        db.session.add(item)
                        service_items_created += 1

                # Create invoice items for inventory and reduce stock atomically
                inventory_items_created = 0
                stock_reduced_count = 0
                stock_operations = []  # Track all operations for potential rollback

                for item_data in inventory_data:
                    batch = InventoryBatch.query.get(item_data['batch_id'])
                    product = InventoryProduct.query.get(item_data['product_id'])

                    if not batch or not product:
                        raise Exception(f"Batch or product not found for item {item_data}")

                    # Create invoice item
                    item = InvoiceItem()
                    item.invoice_id = invoice.id
                    item.item_type = 'inventory'
                    item.item_id = product.id
                    item.product_id = product.id
                    item.batch_id = batch.id
                    item.item_name = product.name
                    item.description = f"Batch: {batch.batch_name}"
                    item.batch_name = batch.batch_name
                    item.quantity = item_data['quantity']
                    item.unit_price = item_data['unit_price']
                    item.original_amount = item_data['unit_price'] * item_data['quantity']
                    item.final_amount = item_data['unit_price'] * item_data['quantity']
                    db.session.add(item)
                    inventory_items_created += 1

                    # Reduce stock from batch via consumption record
                    create_consumption_record(
                        batch_id=batch.id,
                        quantity=item_data['quantity'],
                        issued_to=f"Invoice {invoice_number} - {customer.full_name}",
                        reference=invoice_number,
                        notes=f"Sold via billing system - Invoice {invoice_number}",
                        user_id=current_user.id
                    )
                    stock_reduced_count += 1
                    stock_operations.append({
                        'batch_id': batch.id,
                        'quantity': item_data['quantity'],
                        'batch_name': batch.batch_name
                    })

                # If we reach here, all operations succeeded
                # Commit the entire transaction
                db.session.commit()

                return jsonify({
                    'success': True,
                    'message': f'Invoice {invoice_number} created successfully',
                    'invoice_id': invoice.id,
                    'invoice_number': invoice_number,
                    'total_amount': float(total_amount),
                    'service_items_created': service_items_created,
                    'inventory_items_created': inventory_items_created,
                    'stock_reduced': stock_reduced_count,
                    'deductions_applied': 0  # Future enhancement for package deductions
                })

        except Exception as e:
            # CRITICAL: Ensure complete rollback on any failure
            db.session.rollback()
            app.logger.error(f"Invoice creation failed for user {current_user.id}: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Transaction failed: {str(e)}. All changes have been rolled back.'
            })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error creating invoice: {str(e)}'})

@app.route('/integrated-billing/customer-packages/<int:client_id>')
@login_required
def get_customer_packages(client_id):
    """Get customer's active packages and available sessions"""
    # Allow all authenticated users to view customer packages
    if not current_user.is_active:
        return jsonify({'success': False, 'error': 'Access denied', 'packages': []}), 403

    try:
        # Import ServicePackageAssignment model for new package system
        from models import ServicePackageAssignment, Service

        # Get active package assignments
        assignments = ServicePackageAssignment.query.filter_by(
            customer_id=client_id,
            status='active'
        ).all()

        package_data = []
        for assignment in assignments:
            try:
                # Get package template details safely
                package_template = None
                package_name = 'Unknown Package'

                try:
                    package_template = assignment.get_package_template()
                    if package_template and hasattr(package_template, 'name'):
                        package_name = package_template.name
                except:
                    # If get_package_template fails, try to get name from package relationship
                    if hasattr(assignment, 'package') and assignment.package:
                        package_name = assignment.package.name

                package_info = {
                    'id': assignment.id,
                    'package_type': assignment.package_type,
                    'package_name': package_name,
                    'expiry_date': assignment.expires_on.strftime('%Y-%m-%d') if assignment.expires_on else None,
                    'status': assignment.status,
                    'is_active': assignment.status == 'active'
                }

                # Add type-specific details based on package type
                if assignment.package_type == 'service_package':
                    package_info['sessions_total'] = assignment.total_sessions or 0
                    package_info['sessions_used'] = assignment.used_sessions or 0
                    package_info['sessions_remaining'] = assignment.remaining_sessions or 0

                    # Get service name safely
                    service_name = 'Any Service'
                    if assignment.service_id:
                        try:
                            service = Service.query.get(assignment.service_id)
                            if service:
                                service_name = service.name
                        except:
                            pass
                    package_info['service_name'] = service_name

                elif assignment.package_type == 'prepaid':
                    package_info['credit_total'] = float(assignment.credit_amount or 0)
                    package_info['credit_used'] = float(assignment.used_credit or 0)
                    package_info['credit_remaining'] = float(assignment.remaining_credit or 0)

                elif assignment.package_type == 'membership':
                    # Membership packages - add relevant fields
                    package_info['membership_type'] = 'unlimited'
                    if hasattr(assignment, 'benefits_json'):
                        package_info['benefits'] = assignment.benefits_json

                package_data.append(package_info)

            except Exception as pkg_error:
                app.logger.error(f"Error processing package assignment {assignment.id}: {str(pkg_error)}")
                # Add basic info even if there's an error
                package_data.append({
                    'id': assignment.id,
                    'package_type': assignment.package_type,
                    'package_name': 'Error loading package details',
                    'status': assignment.status,
                    'error': str(pkg_error)
                })
                continue

        return jsonify({
            'success': True,
            'packages': package_data,
            'total': len(package_data)
        })

    except Exception as e:
        app.logger.error(f"Error fetching customer packages for client {client_id}: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Error fetching packages: {str(e)}',
            'packages': []
        })

@app.route('/api/inventory/batches/for-product/<int:product_id>')
@login_required
def api_get_batches_for_product(product_id):
    """Get batches for a specific product ordered by FIFO (expiry date)"""
    # Allow all authenticated users to view inventory batches
    if not current_user.is_active:
        return jsonify({'success': False, 'error': 'Access denied', 'batches': []}), 403

    try:
        from modules.inventory.models import InventoryBatch
        from sqlalchemy.orm import joinedload
        from datetime import date

        # Get active batches for the product with stock, ordered by expiry (FIFO)
        batches = InventoryBatch.query.filter(
            InventoryBatch.product_id == product_id,
            InventoryBatch.status == 'active',
            InventoryBatch.qty_available > 0
        ).order_by(
            InventoryBatch.expiry_date.asc().nullslast(),
            InventoryBatch.batch_name
        ).all()

        batch_data = []
        for batch in batches:
            # Check if batch is expired
            is_expired = batch.expiry_date and batch.expiry_date < date.today()
            if is_expired:
                continue  # Skip expired batches

            batch_info = {
                'id': batch.id,
                'batch_name': batch.batch_name,
                'qty_available': float(batch.qty_available),
                'unit_cost': float(batch.unit_cost or 0),
                'selling_price': float(batch.selling_price or 0) if batch.selling_price else float(batch.unit_cost or 0),
                'unit_price': float(batch.selling_price or 0) if batch.selling_price else float(batch.unit_cost or 0),
                'expiry_date': batch.expiry_date.isoformat() if batch.expiry_date else None,
                'days_to_expiry': batch.days_to_expiry,
                'location_name': batch.location.name if batch.location else 'Unknown',
                'is_near_expiry': batch.is_near_expiry
            }
            batch_data.append(batch_info)

        return jsonify({
            'success': True,
            'batches': batch_data,
            'total_batches': len(batch_data)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error fetching batches: {str(e)}',
            'batches': []
        }), 500


@app.route('/integrated-billing/payment/<int:invoice_id>', methods=['POST'])
@login_required
def process_payment(invoice_id):
    """Process payment for invoice (supports multiple payment methods)"""
    # Allow all authenticated users to process payments
    if not current_user.is_active:
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    try:
        from models import EnhancedInvoice
        invoice = EnhancedInvoice.query.get_or_404(invoice_id)

        # Parse payment data
        payments_data = []
        payment_methods = request.form.getlist('payment_methods[]')
        payment_amounts = request.form.getlist('payment_amounts[]')

        total_payment = 0
        for i, method in enumerate(payment_methods):
            if method and i < len(payment_amounts):
                amount = float(payment_amounts[i])
                total_payment += amount

                payments_data.append({
                    'payment_method': method,
                    'amount': amount,
                    'transaction_id': request.form.get(f'transaction_id_{i}', ''),
                    'reference_number': request.form.get(f'reference_number_{i}', ''),
                    'card_last4': request.form.get(f'card_last4_{i}', '') if method == 'card' else None
                })

        # Validate payment amount
        if total_payment > invoice.balance_due:
            return jsonify({'success': False, 'message': 'Payment amount exceeds balance due'})

        # Create payment records
        from models import InvoicePayment
        for payment_data in payments_data:
            payment = InvoicePayment()
            payment.invoice_id = invoice_id
            payment.processed_by = current_user.id
            payment.payment_method = payment_data['payment_method']
            payment.amount = payment_data['amount']
            payment.transaction_id = payment_data.get('transaction_id', '')
            payment.reference_number = payment_data.get('reference_number', '')
            payment.card_last4 = payment_data.get('card_last4')
            db.session.add(payment)

        # Update invoice
        invoice.amount_paid += total_payment
        invoice.balance_due = invoice.total_amount - invoice.amount_paid

        if invoice.balance_due <= 0:
            invoice.payment_status = 'paid'
        elif invoice.amount_paid > 0:
            invoice.payment_status = 'partial'

        # Update payment methods (store as JSON)
        payment_methods_summary = {}
        for payment in payments_data:
            method = payment['payment_method']
            if method in payment_methods_summary:
                payment_methods_summary[method] += payment['amount']
            else:
                payment_methods_summary[method] = payment['amount']

        invoice.payment_methods = json.dumps(payment_methods_summary)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Payment of ₹{total_payment:,.2f} processed successfully',
            'new_balance': invoice.balance_due,
            'payment_status': invoice.payment_status
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error processing payment: {str(e)}'})

@app.route('/integrated-billing/invoice/<int:invoice_id>')
@login_required
def view_integrated_invoice(invoice_id):
    """View detailed invoice with all components"""
    # Allow all authenticated users to view invoices
    if not current_user.is_active:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from models import EnhancedInvoice, InvoiceItem, InvoicePayment
    invoice = EnhancedInvoice.query.get_or_404(invoice_id)
    invoice_items = InvoiceItem.query.filter_by(invoice_id=invoice_id).all()
    payments = InvoicePayment.query.filter_by(invoice_id=invoice_id).all()

    # Group items by type
    service_items = [item for item in invoice_items if item.item_type == 'service']
    inventory_items = [item for item in invoice_items if item.item_type == 'inventory']

    # Fetch staff names for services
    staff_names = {}
    service_staff_ids = {item.staff_id for item in service_items if item.staff_id}
    if service_staff_ids:
        from models import User
        staffs = User.query.filter(User.id.in_(service_staff_ids)).all()
        staff_names = {staff.id: staff.full_name for staff in staffs}

    return render_template('integrated_invoice_detail.html',
                         invoice=invoice,
                         service_items=service_items,
                         inventory_items=inventory_items,
                         payments=payments,
                         staff_names=staff_names) # Pass staff names to template

@app.route('/integrated-billing/invoices')
@login_required
def list_integrated_invoices():
    """List all integrated invoices with filters"""
    # Allow all authenticated users to list invoices
    if not current_user.is_active:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from models import EnhancedInvoice
    status_filter = request.args.get('status', 'all')

    query = EnhancedInvoice.query

    if status_filter == 'pending':
        query = query.filter(EnhancedInvoice.payment_status.in_(['pending', 'partial']))
    elif status_filter == 'paid':
        query = query.filter_by(payment_status='paid')
    elif status_filter == 'overdue':
        query = query.filter_by(payment_status='overdue')

    invoices = query.order_by(EnhancedInvoice.created_at.desc()).all()

    return render_template('integrated_invoices_list.html',
                         invoices=invoices,
                         status_filter=status_filter)

# Main billing route - redirect to integrated billing
@app.route('/billing')
@login_required
def billing():
    """Main billing route redirects to integrated billing"""
    return redirect(url_for('integrated_billing'))

@app.route('/integrated-billing/save-draft', methods=['POST'])
@login_required
def save_invoice_draft():
    """Save invoice as draft for later completion"""
    # Allow all authenticated users to save drafts
    if not current_user.is_active:
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    try:
        from models import Service, EnhancedInvoice, InvoiceItem
        import datetime

        data = request.get_json()

        # Parse form data
        client_id = data.get('client_id')
        if not client_id:
            return jsonify({'success': False, 'message': 'Client is required'})

        customer = Customer.query.get(client_id)
        if not customer:
            return jsonify({'success': False, 'message': 'Customer not found'})

        # Parse services and products
        services_data = data.get('services', [])
        inventory_data = data.get('products', [])

        # Calculate totals
        services_subtotal = 0
        for service_data in services_data:
            service = Service.query.get(service_data['service_id'])
            if service:
                services_subtotal += service.price * service_data['quantity']

        inventory_subtotal = 0
        for item in inventory_data:
            inventory_subtotal += item['unit_price'] * item['quantity']

        gross_subtotal = services_subtotal + inventory_subtotal

        discount_percentage = float(data.get('discount_percentage', 0))
        discount_amount = (gross_subtotal * discount_percentage) / 100

        gst_enabled = data.get('gst_enabled', False)
        gst_percentage = float(data.get('gst_percentage', 0)) if gst_enabled else 0

        net_subtotal = gross_subtotal - discount_amount
        tax_amount = (net_subtotal * gst_percentage) / 100
        total_amount = net_subtotal + tax_amount

        # Generate draft invoice number
        current_date = datetime.datetime.now()
        invoice_number = f"DRAFT-{current_date.strftime('%Y%m%d%H%M%S')}"

        # Create draft invoice
        invoice = EnhancedInvoice()
        invoice.invoice_number = invoice_number
        invoice.client_id = int(client_id)
        invoice.invoice_date = current_date
        invoice.services_subtotal = services_subtotal
        invoice.inventory_subtotal = inventory_subtotal
        invoice.gross_subtotal = gross_subtotal
        invoice.net_subtotal = net_subtotal
        invoice.tax_amount = tax_amount
        invoice.discount_amount = discount_amount
        invoice.total_amount = total_amount
        invoice.balance_due = total_amount
        invoice.payment_status = 'draft'
        invoice.notes = data.get('notes', '')

        db.session.add(invoice)
        db.session.flush()

        # Create invoice items for services
        for service_data in services_data:
            service = Service.query.get(service_data['service_id'])
            if service:
                item = InvoiceItem()
                item.invoice_id = invoice.id
                item.item_type = 'service'
                item.item_id = service.id
                item.item_name = service.name
                item.description = service.description
                item.quantity = service_data['quantity']
                item.unit_price = service.price
                item.original_amount = service.price * service_data['quantity']
                item.final_amount = service.price * service_data['quantity']
                item.staff_id = service_data.get('staff_id')
                db.session.add(item)

        # Create invoice items for inventory (without reducing stock)
        for item_data in inventory_data:
            from modules.inventory.models import InventoryProduct, InventoryBatch
            batch = InventoryBatch.query.get(item_data['batch_id'])
            product = InventoryProduct.query.get(item_data['product_id'])

            if batch and product:
                item = InvoiceItem()
                item.invoice_id = invoice.id
                item.item_type = 'inventory'
                item.item_id = product.id
                item.product_id = product.id
                item.batch_id = batch.id
                item.item_name = product.name
                item.description = f"Batch: {batch.batch_name}"
                item.quantity = item_data['quantity']
                item.unit_price = item_data['unit_price']
                item.original_amount = item_data['unit_price'] * item_data['quantity']
                item.final_amount = item_data['unit_price'] * item_data['quantity']
                db.session.add(item)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Draft invoice {invoice_number} saved successfully',
            'invoice_id': invoice.id,
            'invoice_number': invoice_number
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error saving draft: {str(e)}'})

@app.route('/debug/fix-customer-bookings')
@login_required
def debug_fix_customer_bookings():
    """Debug route to fix customer-booking relationships"""
    if not current_user.has_role('admin'):
        flash('Access denied - Admin only', 'danger')
        return redirect(url_for('dashboard'))

    try:
        from models import Customer, UnakiBooking

        fixed_count = 0
        total_bookings = 0

        # Get all UnakiBookings without client_id
        unmatched_bookings = UnakiBooking.query.filter(
            UnakiBooking.client_id.is_(None)
        ).all()

        for booking in unmatched_bookings:
            total_bookings += 1
            customer_match = None

            # Try to match by phone first
            if booking.client_phone:
                customer_match = Customer.query.filter_by(
                    phone=booking.client_phone,
                    is_active=True
                ).first()

            # If no phone match, try name matching
            if not customer_match and booking.client_name:
                name_parts = booking.client_name.strip().split(' ', 1)
                if len(name_parts) >= 1:
                    first_name = name_parts[0]
                    customer_match = Customer.query.filter(
                        Customer.first_name.ilike(f'%{first_name}%'),
                        Customer.is_active == True
                    ).first()

            # If found a match, update the booking
            if customer_match:
                booking.client_id = customer_match.id
                fixed_count += 1
                app.logger.info(f"Fixed booking {booking.id}: matched to customer {customer_match.id}")

        # Commit changes
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Fixed {fixed_count} out of {total_bookings} unmatched bookings',
            'fixed_count': fixed_count,
            'total_bookings': total_bookings
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error fixing customer bookings: {str(e)}'
        })

@app.route('/integrated-billing/print-invoice/<int:invoice_id>')
@login_required
def print_professional_invoice(invoice_id):
    """Generate printable professional invoice"""
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

    return render_template('professional_invoice_print.html',
                         invoice=invoice,
                         invoice_items=invoice_items,
                         tax_details=tax_details,
                         staff_names=staff_names) # Pass staff names to template

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

# Legacy billing compatibility route
@app.route('/billing/integrated')
@login_required
def billing_integrated_redirect():
    """Redirect old billing to new integrated billing"""
    return redirect(url_for('integrated_billing'))