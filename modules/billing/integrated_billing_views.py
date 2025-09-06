"""
Integrated Billing Views - New Enhanced Billing System
Supports services, packages, subscriptions, and inventory items
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import (Customer, Service, Appointment, InventoryProduct, 
                   Package, CustomerPackage, CustomerPackageSession)
from datetime import datetime
import json

# Import enhanced billing models and engine
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from enhanced_billing_models import EnhancedInvoice, InvoiceItem, InvoicePayment, BillingEngine

@app.route('/integrated-billing')
@login_required
def integrated_billing():
    """New integrated billing dashboard"""
    if not current_user.can_access('billing'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get data for billing interface
    customers = Customer.query.filter_by(is_active=True).all()
    services = Service.query.filter_by(is_active=True).all()
    inventory_items = InventoryProduct.query.filter_by(is_active=True).all()
    
    # Get recent invoices
    recent_invoices = EnhancedInvoice.query.order_by(EnhancedInvoice.created_at.desc()).limit(10).all()
    
    # Calculate dashboard stats
    total_revenue = db.session.query(db.func.sum(EnhancedInvoice.total_amount)).filter(
        EnhancedInvoice.payment_status == 'paid'
    ).scalar() or 0
    
    pending_amount = db.session.query(db.func.sum(EnhancedInvoice.balance_due)).filter(
        EnhancedInvoice.payment_status.in_(['pending', 'partial'])
    ).scalar() or 0
    
    today_revenue = db.session.query(db.func.sum(EnhancedInvoice.total_amount)).filter(
        EnhancedInvoice.payment_status == 'paid',
        db.func.date(EnhancedInvoice.invoice_date) == datetime.now().date()
    ).scalar() or 0
    
    return render_template('integrated_billing.html',
                         customers=customers,
                         services=services,
                         inventory_items=inventory_items,
                         recent_invoices=recent_invoices,
                         total_revenue=total_revenue,
                         pending_amount=pending_amount,
                         today_revenue=today_revenue)

@app.route('/integrated-billing/create', methods=['POST'])
@login_required
def create_integrated_invoice():
    """Create new integrated invoice"""
    if not current_user.can_access('billing'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Parse form data
        client_id = request.form.get('client_id')
        if not client_id:
            return jsonify({'success': False, 'message': 'Client is required'})
        
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
        
        # Parse inventory data
        inventory_data = []
        inventory_ids = request.form.getlist('inventory_ids[]')
        inventory_quantities = request.form.getlist('inventory_quantities[]')
        
        for i, inventory_id in enumerate(inventory_ids):
            if inventory_id:
                inventory_data.append({
                    'product_id': int(inventory_id),
                    'quantity': float(inventory_quantities[i]) if i < len(inventory_quantities) else 1
                })
        
        # Other billing parameters
        billing_data = {
            'services': services_data,
            'inventory_items': inventory_data,
            'tax_rate': float(request.form.get('tax_rate', 0.18)),
            'discount_amount': float(request.form.get('discount_amount', 0)),
            'tips_amount': float(request.form.get('tips_amount', 0)),
            'notes': request.form.get('notes', '')
        }
        
        # Create invoice using billing engine
        result = BillingEngine.create_comprehensive_invoice(client_id, billing_data)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result['message'],
                'invoice_id': result['invoice'].id,
                'total_amount': result['total_amount'],
                'deductions_applied': result['deductions_applied']
            })
        else:
            return jsonify({'success': False, 'message': result.get('error', 'Unknown error')})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creating invoice: {str(e)}'})

@app.route('/integrated-billing/customer-packages/<int:client_id>')
@login_required
def get_customer_packages(client_id):
    """Get customer's active packages and available sessions"""
    if not current_user.can_access('billing'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get active packages
        packages = CustomerPackage.query.filter_by(
            client_id=client_id,
            is_active=True
        ).all()
        
        package_data = []
        for pkg in packages:
            # Get session details
            sessions = CustomerPackageSession.query.filter_by(
                client_package_id=pkg.id
            ).all()
            
            session_details = []
            for session in sessions:
                session_details.append({
                    'service_id': session.service_id,
                    'service_name': session.service.name,
                    'sessions_total': session.sessions_total,
                    'sessions_used': session.sessions_used,
                    'sessions_remaining': session.sessions_remaining,
                    'is_unlimited': session.is_unlimited
                })
            
            package_data.append({
                'id': pkg.id,
                'package_name': pkg.package.name,
                'expiry_date': pkg.expiry_date.strftime('%Y-%m-%d'),
                'sessions': session_details
            })
        
        return jsonify({'packages': package_data})
        
    except Exception as e:
        return jsonify({'error': f'Error fetching packages: {str(e)}'})

@app.route('/integrated-billing/payment/<int:invoice_id>', methods=['POST'])
@login_required
def process_payment(invoice_id):
    """Process payment for invoice (supports multiple payment methods)"""
    if not current_user.can_access('billing'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
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
        for payment_data in payments_data:
            payment = InvoicePayment(
                invoice_id=invoice_id,
                processed_by=current_user.id,
                **payment_data
            )
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

# Legacy billing compatibility route
@app.route('/billing/integrated')
@login_required
def billing_integrated_redirect():
    """Redirect old billing to new integrated billing"""
    return redirect(url_for('integrated_billing'))