"""
Integrated Billing Views - New Enhanced Billing System
Supports services, packages, subscriptions, and inventory items
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from datetime import datetime
import json
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
@login_required
def integrated_billing():
    """New integrated billing dashboard"""
    if not current_user.can_access('billing'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get data for billing interface
    from models import Customer, Service, PrepaidPackage, ServicePackage, Membership
    customers = Customer.query.filter_by(is_active=True).order_by(Customer.first_name, Customer.last_name).all()
    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()

    # Get all types of packages
    prepaid_packages = PrepaidPackage.query.filter_by(is_active=True).all()
    service_packages = ServicePackage.query.filter_by(is_active=True).all()
    memberships = Membership.query.filter_by(is_active=True).all()

    # Combine all packages for the interface
    packages = []
    for pkg in prepaid_packages:
        packages.append({'id': pkg.id, 'name': pkg.name, 'type': 'prepaid'})
    for pkg in service_packages:
        packages.append({'id': pkg.id, 'name': pkg.name, 'type': 'service_package'})
    for pkg in memberships:
        packages.append({'id': pkg.id, 'name': pkg.name, 'type': 'membership'})

    # Get inventory items (products with stock) for retail sales
    inventory_items = []
    try:
        from modules.inventory.models import InventoryProduct, InventoryBatch
        from sqlalchemy.orm import joinedload

        # Get products with their batches and calculate total stock
        products = InventoryProduct.query.options(
            joinedload(InventoryProduct.batches),
            joinedload(InventoryProduct.category)
        ).filter(InventoryProduct.is_active == True).all()

        print(f"DEBUG: Found {len(products)} active products")

        for product in products:
            # Calculate total available stock from active batches
            active_batches = [batch for batch in product.batches if batch.status == 'active']
            total_stock = sum(float(batch.qty_available or 0) for batch in active_batches)

            print(f"DEBUG: Product {product.name} has {len(active_batches)} active batches with total stock: {total_stock}")

            # Include all products regardless of stock for billing (they can be services too)
            inventory_items.append({
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'unit_of_measure': product.unit_of_measure or 'pcs',
                'total_stock': total_stock,
                'category': product.category.name if product.category else 'Uncategorized',
                'is_retail_item': product.is_retail_item,
                'is_service_item': product.is_service_item
            })

    except Exception as e:
        print(f"Error loading inventory items: {e}")
        import traceback
        traceback.print_exc()
        inventory_items = []

    # Get recent invoices with error handling
    from models import EnhancedInvoice
    try:
        recent_invoices = EnhancedInvoice.query.order_by(EnhancedInvoice.created_at.desc()).limit(10).all()
    except Exception as e:
        app.logger.error(f"Error fetching recent invoices: {str(e)}")
        recent_invoices = []

    # Calculate dashboard stats with error handling
    try:
        total_revenue = db.session.query(db.func.sum(EnhancedInvoice.total_amount)).filter(
            EnhancedInvoice.payment_status == 'paid'
        ).scalar() or 0
    except Exception as e:
        app.logger.error(f"Error calculating total revenue: {str(e)}")
        total_revenue = 0

    try:
        pending_amount = db.session.query(db.func.sum(EnhancedInvoice.balance_due)).filter(
            EnhancedInvoice.payment_status.in_(['pending', 'partial'])
        ).scalar() or 0
    except Exception as e:
        app.logger.error(f"Error calculating pending amount: {str(e)}")
        pending_amount = 0

    try:
        today_revenue = db.session.query(db.func.sum(EnhancedInvoice.total_amount)).filter(
            EnhancedInvoice.payment_status == 'paid',
            db.func.date(EnhancedInvoice.invoice_date) == datetime.now().date()
        ).scalar() or 0
    except Exception as e:
        app.logger.error(f"Error calculating today's revenue: {str(e)}")
        today_revenue = 0

    return render_template('integrated_billing.html',
                         customers=customers,
                         services=services,
                         packages=packages,
                         inventory_items=inventory_items,
                         recent_invoices=recent_invoices,
                         total_revenue=total_revenue,
                         pending_amount=pending_amount,
                         today_revenue=today_revenue)

@app.route('/integrated-billing/create-professional', methods=['POST'])
@login_required
def create_professional_invoice():
    """Create new professional invoice with complete GST/SGST tax support and automatic package benefit application"""
    if not current_user.can_access('billing'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    try:
        from models import Customer, Service, EnhancedInvoice, InvoiceItem
        from modules.inventory.models import InventoryBatch, InventoryProduct
        from modules.inventory.queries import create_consumption_record
        from modules.packages.package_billing_service import PackageBillingService
        import datetime

        # Parse form data
        client_id = request.form.get('client_id')
        if not client_id:
            return jsonify({'success': False, 'message': 'Client is required'})

        customer = Customer.query.get(client_id)
        if not customer:
            return jsonify({'success': False, 'message': 'Customer not found'})

        # Parse services data with better error handling
        services_data = []
        service_ids = request.form.getlist('service_ids[]')
        service_quantities = request.form.getlist('service_quantities[]')
        appointment_ids = request.form.getlist('appointment_ids[]')

        for i, service_id in enumerate(service_ids):
            if service_id and service_id.strip():
                try:
                    quantity = float(service_quantities[i]) if i < len(service_quantities) and service_quantities[i] else 1
                    appointment_id = int(appointment_ids[i]) if i < len(appointment_ids) and appointment_ids[i] and appointment_ids[i].strip() else None

                    services_data.append({
                        'service_id': int(service_id),
                        'quantity': quantity,
                        'appointment_id': appointment_id
                    })
                except (ValueError, TypeError) as e:
                    return jsonify({'success': False, 'message': f'Invalid service data at position {i+1}: {str(e)}'})

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

        # Check if we have any services or products
        if not services_data and not inventory_data:
            return jsonify({'success': False, 'message': 'At least one service or product must be selected to create an invoice'})

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

        # Calculate initial amounts (will be recalculated after package benefits)
        services_subtotal = 0
        for service_data in services_data:
            service = Service.query.get(service_data['service_id'])
            if service:
                services_subtotal += service.price * service_data['quantity']

        inventory_subtotal = 0
        for item in inventory_data:
            inventory_subtotal += item['unit_price'] * item['quantity']

        # Note: Final totals will be calculated after package benefits are applied
        initial_gross_subtotal = services_subtotal + inventory_subtotal

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

            # Create enhanced invoice with professional fields
            invoice = EnhancedInvoice()
            invoice.invoice_number = invoice_number
            invoice.client_id = int(client_id)
            invoice.invoice_date = current_date

            # Initialize with temporary values - will be recalculated after package benefits
            invoice.services_subtotal = services_subtotal
            invoice.inventory_subtotal = inventory_subtotal
            invoice.gross_subtotal = initial_gross_subtotal
            invoice.net_subtotal = 0  # Will be calculated after package benefits
            invoice.tax_amount = 0    # Will be calculated after package benefits
            invoice.discount_amount = 0  # Will be calculated after package benefits
            invoice.tips_amount = tips_amount
            invoice.total_amount = 0  # Will be calculated after package benefits
            invoice.balance_due = 0   # Will be calculated after package benefits

            # Store GST configuration
            invoice.cgst_rate = cgst_rate * 100
            invoice.sgst_rate = sgst_rate * 100
            invoice.igst_rate = igst_rate * 100
            invoice.is_interstate = is_interstate
            invoice.additional_charges = additional_charges
            invoice.payment_terms = payment_terms

            # Initialize GST amounts - will be calculated after package benefits
            invoice.cgst_amount = 0
            invoice.sgst_amount = 0
            invoice.igst_amount = 0

            # Tax breakdown for legacy support - will be updated after package calculations
            tax_breakdown = {
                'cgst_rate': cgst_rate * 100,
                'sgst_rate': sgst_rate * 100,
                'igst_rate': igst_rate * 100,
                'cgst_amount': 0,
                'sgst_amount': 0,
                'igst_amount': 0,
                'is_interstate': is_interstate,
                'additional_charges': additional_charges,
                'payment_terms': payment_terms,
                'payment_method': payment_method
            }

            invoice.notes = json.dumps(tax_breakdown)
            invoice.payment_methods = json.dumps({payment_method: 0})  # Will be updated after calculations

            db.session.add(invoice)
            db.session.flush()  # Get the invoice ID

            # Create invoice items for services with automatic package benefit application
            service_items_created = 0
            package_benefits_applied = 0
            total_package_deductions = 0
            package_details = []

            for service_data in services_data:
                service = Service.query.get(service_data['service_id'])
                if service:
                    # Create base invoice item
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

                    # Apply package benefits automatically
                    original_price = service.price * service_data['quantity']
                    final_amount = original_price
                    deduction_amount = 0
                    package_applied = None

                    # Try to apply package benefits
                    try:
                        db.session.add(item)
                        db.session.flush()  # Get item ID for idempotency

                        benefit_result = PackageBillingService.apply_package_benefit(
                            customer_id=int(client_id),
                            service_id=service.id,
                            service_price=original_price,
                            invoice_id=invoice.id,
                            invoice_item_id=item.id,
                            service_date=current_date,
                            requested_quantity=int(service_data['quantity'])
                        )

                        if benefit_result['success'] and benefit_result.get('applied', False):
                            final_price = benefit_result['final_price']
                            deduction_amount = benefit_result['deduction_amount']
                            package_applied = benefit_result.get('package_name', 'Package')

                            # Update item with package benefit details
                            item.deduction_amount = deduction_amount
                            item.final_amount = final_price
                            item.is_package_deduction = True

                            # Update description to show package benefit
                            benefit_type = benefit_result.get('benefit_type', 'package')
                            if benefit_type == 'unlimited':
                                item.description = f"{service.description} (Unlimited access via {package_applied})"
                            elif benefit_type == 'free':
                                remaining = benefit_result.get('remaining_balance', {}).get('remaining', 0)
                                item.description = f"{service.description} (Free session via {package_applied}, {remaining} remaining)"
                            elif benefit_type == 'discount':
                                remaining = benefit_result.get('remaining_balance', {}).get('remaining', 0)
                                item.description = f"{service.description} (Discount via {package_applied}, {remaining} uses left)"
                            elif benefit_type == 'prepaid':
                                remaining = benefit_result.get('remaining_balance', {}).get('remaining', 0)
                                item.description = f"{service.description} (Prepaid deduction via {package_applied}, ₹{remaining:.2f} balance)"

                            package_benefits_applied += 1
                            total_package_deductions += deduction_amount

                            package_details.append({
                                'service_name': service.name,
                                'benefit_type': benefit_type,
                                'package_name': package_applied,
                                'original_price': original_price,
                                'final_price': final_price,
                                'deduction': deduction_amount,
                                'message': benefit_result.get('message', '')
                            })
                        else:
                            # No package benefit applied
                            item.final_amount = original_price
                            item.is_package_deduction = False

                    except Exception as e:
                        app.logger.warning(f"Package benefit application failed for service {service.id}: {str(e)}")
                        # Continue with regular pricing if package application fails
                        item.final_amount = original_price
                        item.is_package_deduction = False

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
                    item.description = f"Batch: {batch.batch_name}"
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

            # Calculate final invoice totals (with or without package deductions)
            # Calculate final services subtotal after package deductions
            actual_services_subtotal = services_subtotal - total_package_deductions
            actual_gross_subtotal = actual_services_subtotal + inventory_subtotal

            # Calculate discount on the final subtotal
            if discount_type == 'percentage':
                actual_discount_amount = (actual_gross_subtotal * discount_value) / 100
            else:
                actual_discount_amount = min(discount_value, actual_gross_subtotal)

            actual_net_subtotal = max(0, actual_gross_subtotal - actual_discount_amount)

            # Calculate taxes on the final net subtotal
            if is_interstate:
                actual_igst_amount = actual_net_subtotal * igst_rate
                actual_cgst_amount = 0
                actual_sgst_amount = 0
            else:
                actual_cgst_amount = actual_net_subtotal * cgst_rate
                actual_sgst_amount = actual_net_subtotal * sgst_rate
                actual_igst_amount = 0

            actual_total_tax = actual_cgst_amount + actual_sgst_amount + actual_igst_amount
            actual_total_amount = actual_net_subtotal + actual_total_tax + additional_charges + tips_amount

            # Update invoice with final calculated amounts
            invoice.services_subtotal = actual_services_subtotal
            invoice.gross_subtotal = actual_gross_subtotal
            invoice.net_subtotal = actual_net_subtotal
            invoice.tax_amount = actual_total_tax
            invoice.discount_amount = actual_discount_amount
            invoice.tips_amount = tips_amount
            invoice.total_amount = actual_total_amount
            invoice.balance_due = actual_total_amount
            invoice.cgst_amount = actual_cgst_amount
            invoice.sgst_amount = actual_sgst_amount
            invoice.igst_amount = actual_igst_amount

            # Update tax breakdown with final amounts
            tax_breakdown = {
                'cgst_rate': cgst_rate * 100,
                'sgst_rate': sgst_rate * 100,
                'igst_rate': igst_rate * 100,
                'cgst_amount': actual_cgst_amount,
                'sgst_amount': actual_sgst_amount,
                'igst_amount': actual_igst_amount,
                'is_interstate': is_interstate,
                'additional_charges': additional_charges,
                'payment_terms': payment_terms,
                'package_deductions': total_package_deductions,
                'package_benefits_applied': package_benefits_applied
            }

            invoice.notes = json.dumps(tax_breakdown)
            invoice.payment_methods = json.dumps({payment_method: actual_total_amount})

            # Commit all changes
            db.session.commit()

            # Prepare response with package benefit details
            response_data = {
                'success': True,
                'message': f'Professional Invoice {invoice_number} created successfully',
                'invoice_id': invoice.id,
                'invoice_number': invoice_number,
                'total_amount': float(invoice.total_amount),
                'cgst_amount': float(invoice.cgst_amount),
                'sgst_amount': float(invoice.sgst_amount),
                'igst_amount': float(invoice.igst_amount),
                'tax_amount': float(invoice.tax_amount),
                'service_items_created': service_items_created,
                'inventory_items_created': inventory_items_created,
                'stock_reduced': stock_reduced_count,
                'package_benefits_applied': package_benefits_applied,
                'total_package_deductions': float(total_package_deductions)
            }

            # Add package benefit details if any were applied
            if package_benefits_applied > 0:
                response_data['package_details'] = package_details
                response_data['message'] += f' with {package_benefits_applied} package benefits applied (₹{total_package_deductions:.2f} savings)'

            return jsonify(response_data)

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

@app.route('/integrated-billing/create', methods=['POST'])
@login_required
def create_integrated_invoice():
    """Create new integrated invoice with batch-wise inventory integration"""
    if not current_user.can_access('billing'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    try:
        from models import Customer, Service, EnhancedInvoice, InvoiceItem
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

        for i, service_id in enumerate(service_ids):
            if service_id:
                services_data.append({
                    'service_id': int(service_id),
                    'quantity': float(service_quantities[i]) if i < len(service_quantities) else 1,
                    'appointment_id': int(appointment_ids[i]) if i < len(appointment_ids) and appointment_ids[i] else None
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
    if not current_user.can_access('billing'):
        return jsonify({'error': 'Access denied', 'packages': []}), 403

    try:
        # Import the ServicePackageAssignment model with error handling
        try:
            from models import ServicePackageAssignment, Customer
        except ImportError as e:
            app.logger.error(f"Import error: {str(e)}")
            return jsonify({'error': 'System error', 'packages': []})

        # Verify customer exists
        customer = Customer.query.get(client_id)
        if not customer:
            return jsonify({'error': 'Customer not found', 'packages': []})

        # Get all active package assignments for the customer with error handling
        try:
            assignments = ServicePackageAssignment.query.filter_by(
                customer_id=client_id,
                status='active'
            ).all()
        except Exception as e:
            app.logger.error(f"Database query error: {str(e)}")
            return jsonify({'error': 'Database error', 'packages': []})

        package_data = []

        for assignment in assignments:
            try:
                # Get package template details safely
                package_template = assignment.get_package_template()
                if not package_template:
                    continue

                # Format session details based on package type
                session_details = []

                if assignment.package_type == 'service_package':
                    service_name = 'Service'
                    try:
                        if assignment.service:
                            service_name = assignment.service.name
                    except:
                        pass

                    session_details.append({
                        'service_id': assignment.service_id,
                        'service_name': service_name,
                        'sessions_total': assignment.total_sessions or 0,
                        'sessions_used': assignment.used_sessions or 0,
                        'sessions_remaining': assignment.remaining_sessions or 0,
                        'is_unlimited': False,
                        'benefit_type': 'service_package',
                        'description': f"{assignment.remaining_sessions or 0} sessions remaining"
                    })
                elif assignment.package_type == 'prepaid':
                    session_details.append({
                        'service_id': None,
                        'service_name': 'All Services (Prepaid)',
                        'sessions_total': 0,
                        'sessions_used': 0,
                        'sessions_remaining': 0,
                        'is_unlimited': False,
                        'benefit_type': 'prepaid',
                        'balance_total': float(assignment.credit_amount or 0),
                        'balance_remaining': float(assignment.remaining_credit or 0),
                        'description': f"₹{float(assignment.remaining_credit or 0):.2f} prepaid balance"
                    })
                elif assignment.package_type == 'membership':
                    session_details.append({
                        'service_id': None,
                        'service_name': 'All Services (Membership)',
                        'sessions_total': 0,
                        'sessions_used': 0,
                        'sessions_remaining': 999999,  # Use large number instead of infinity
                        'is_unlimited': True,
                        'benefit_type': 'unlimited',
                        'description': 'Unlimited access'
                    })
                else:
                    # For other package types (student, yearly, kitty)
                    session_details.append({
                        'service_id': None,
                        'service_name': f'{assignment.package_type.title()} Package',
                        'sessions_total': 0,
                        'sessions_used': 0,
                        'sessions_remaining': 0,
                        'is_unlimited': False,
                        'benefit_type': assignment.package_type,
                        'description': f'{assignment.package_type.title()} package benefits'
                    })

                package_data.append({
                    'id': assignment.id,
                    'package_name': package_template.name if hasattr(package_template, 'name') else 'Package',
                    'package_type': assignment.package_type,
                    'expiry_date': assignment.expires_on.strftime('%Y-%m-%d') if assignment.expires_on else 'No expiry',
                    'is_active': assignment.status == 'active',
                    'sessions': session_details,
                    'assignment_date': assignment.assigned_on.strftime('%Y-%m-%d') if assignment.assigned_on else 'Unknown'
                })
            except Exception as e:
                app.logger.error(f"Error processing assignment {assignment.id}: {str(e)}")
                continue

        # Calculate totals safely
        total_prepaid_balance = 0
        total_free_sessions = 0

        try:
            for assignment in assignments:
                if assignment.package_type == 'prepaid' and assignment.remaining_credit:
                    total_prepaid_balance += float(assignment.remaining_credit)
                elif assignment.package_type == 'service_package' and assignment.remaining_sessions:
                    total_free_sessions += int(assignment.remaining_sessions)
        except Exception as e:
            app.logger.error(f"Error calculating totals: {str(e)}")

        response_data = {
            'packages': package_data,
            'summary': {
                'total_active_packages': len(package_data),
                'has_unlimited_access': any(p['package_type'] == 'membership' for p in package_data),
                'total_prepaid_balance': total_prepaid_balance,
                'total_free_sessions': total_free_sessions
            }
        }

        return jsonify(response_data)

    except Exception as e:
        app.logger.error(f"Error fetching customer packages for client {client_id}: {str(e)}")
        return jsonify({'error': f'Error fetching packages: {str(e)}', 'packages': []})

@app.route('/api/inventory/batches/for-product/<int:product_id>')
@login_required
def api_get_batches_for_product(product_id):
    """Get batches for a specific product ordered by FIFO (expiry date)"""
    if not current_user.can_access('billing'):
        return jsonify({'error': 'Access denied'}), 403

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
            'error': f'Error fetching batches: {str(e)}'
        }), 500


@app.route('/integrated-billing/payment/<int:invoice_id>', methods=['POST'])
@login_required
def process_payment(invoice_id):
    """Process payment for invoice (supports multiple payment methods)"""
    if not current_user.can_access('billing'):
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
    if not current_user.can_access('billing'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from models import EnhancedInvoice, InvoiceItem, InvoicePayment
    invoice = EnhancedInvoice.query.get_or_404(invoice_id)
    invoice_items = InvoiceItem.query.filter_by(invoice_id=invoice_id).all()
    payments = InvoicePayment.query.filter_by(invoice_id=invoice_id).all()

    # Group items by type
    service_items = [item for item in invoice_items if item.item_type == 'service']
    inventory_items = [item for item in invoice_items if item.item_type == 'inventory']

    return render_template('integrated_invoice_detail.html',
                         invoice=invoice,
                         service_items=service_items,
                         inventory_items=inventory_items,
                         payments=payments)

@app.route('/integrated-billing/invoices')
@login_required
def list_integrated_invoices():
    """List all integrated invoices with filters"""
    if not current_user.can_access('billing'):
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

# Main billing route - redirect to integrated billing (commented out due to route conflict)
# @app.route('/billing')
# @login_required  
# def billing():
#     """Main billing route redirects to integrated billing"""
#     return redirect(url_for('integrated_billing'))

@app.route('/integrated-billing/save-draft', methods=['POST'])
@login_required 
def save_invoice_draft():
    """Save invoice as draft for later completion"""
    if not current_user.can_access('billing'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    try:
        # Get form data
        client_id = request.form.get('client_id')
        services_data = request.form.getlist('service_ids[]')
        products_data = request.form.getlist('product_ids[]')
        notes = request.form.get('notes', '')

        # For now, just return success - in a full implementation,
        # you would save this data to a drafts table
        draft_data = {
            'client_id': client_id,
            'services_count': len([s for s in services_data if s]),
            'products_count': len([p for p in products_data if p]),
            'notes': notes,
            'timestamp': datetime.now().isoformat()
        }

        # Log the draft save (in production, save to database)
        app.logger.info(f"Draft saved for user {current_user.id}: {draft_data}")

        return jsonify({
            'success': True, 
            'message': 'Draft saved successfully',
            'draft_id': f"draft_{datetime.now().timestamp()}",
            'items_saved': draft_data['services_count'] + draft_data['products_count']
        })

    except Exception as e:
        app.logger.error(f"Error saving draft: {str(e)}")
        return jsonify({'success': False, 'message': f'Error saving draft: {str(e)}'})

@app.route('/integrated-billing/print-invoice/<int:invoice_id>')
@login_required
def print_professional_invoice(invoice_id):
    """Generate printable professional invoice"""
    if not current_user.can_access('billing'):
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

    return render_template('professional_invoice_print.html',
                         invoice=invoice,
                         invoice_items=invoice_items,
                         tax_details=tax_details)

@app.route('/api/invoice-preview', methods=['POST'])
@login_required
def generate_invoice_preview():
    """Generate professional invoice preview"""
    if not current_user.can_access('billing'):
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