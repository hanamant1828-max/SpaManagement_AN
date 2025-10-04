"""
Routes for package assignment with payment collection and receipt generation
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from app import db, app
from models import (
    Customer, Service, ServicePackageAssignment, Payment, Receipt,
    PrepaidPackage, ServicePackage, Membership, StudentOffer, 
    YearlyMembership, KittyParty
)
import json
import uuid

assign_packages_bp = Blueprint('assign_packages', __name__, url_prefix='/assign-packages')

@app.route('/assign-packages')
@login_required
def assign_packages_page():
    """Main page for assigning packages with payment collection"""
    customers = Customer.query.filter_by(is_active=True).order_by(Customer.first_name).all()
    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
    
    # Get all active packages and convert to dicts
    prepaid_packages = [{
        'id': p.id,
        'name': p.name,
        'actual_price': p.actual_price,
        'after_value': p.after_value,
        'benefit_percent': p.benefit_percent,
        'validity_months': p.validity_months
    } for p in PrepaidPackage.query.filter_by(is_active=True).all()]
    
    service_packages = [{
        'id': p.id,
        'name': p.name,
        'service_id': p.service_id,
        'pay_for': p.pay_for,
        'total_services': p.total_services,
        'benefit_percent': p.benefit_percent,
        'validity_months': p.validity_months
    } for p in ServicePackage.query.filter_by(is_active=True).all()]
    
    memberships = [{
        'id': m.id,
        'name': m.name,
        'price': m.price,
        'validity_months': m.validity_months,
        'description': m.description
    } for m in Membership.query.filter_by(is_active=True).all()]
    
    student_offers = [{
        'id': s.id,
        'discount_percentage': s.discount_percentage,
        'valid_from': s.valid_from.isoformat() if s.valid_from else None,
        'valid_to': s.valid_to.isoformat() if s.valid_to else None,
        'valid_days': s.valid_days,
        'conditions': s.conditions
    } for s in StudentOffer.query.filter_by(is_active=True).all()]
    
    yearly_memberships = [{
        'id': y.id,
        'name': y.name,
        'price': y.price,
        'discount_percent': y.discount_percent,
        'validity_months': y.validity_months,
        'extra_benefits': y.extra_benefits
    } for y in YearlyMembership.query.filter_by(is_active=True).all()]
    
    kitty_parties = [{
        'id': k.id,
        'name': k.name,
        'price': k.price,
        'after_value': k.after_value,
        'min_guests': k.min_guests,
        'valid_from': k.valid_from.isoformat() if k.valid_from else None,
        'valid_to': k.valid_to.isoformat() if k.valid_to else None,
        'conditions': k.conditions
    } for k in KittyParty.query.filter_by(is_active=True).all()]
    
    return render_template('assign_packages.html',
                         customers=customers,
                         services=services,
                         prepaid_packages=prepaid_packages,
                         service_packages=service_packages,
                         memberships=memberships,
                         student_offers=student_offers,
                         yearly_memberships=yearly_memberships,
                         kitty_parties=kitty_parties)


@app.route('/packages/api/assign-and-pay', methods=['POST'])
@login_required
def api_assign_and_pay():
    """
    Atomic endpoint to assign package, collect payment, and generate receipt
    All-or-nothing transaction with idempotency support
    """
    try:
        data = request.get_json()
        
        # Check idempotency
        idempotency_key = request.headers.get('Idempotency-Key')
        if idempotency_key:
            # Check if this request was already processed (within last 5 minutes)
            existing_payment = Payment.query.filter(
                Payment.notes.like(f'%{idempotency_key}%'),
                Payment.created_at >= datetime.utcnow() - timedelta(minutes=5)
            ).first()
            
            if existing_payment and existing_payment.assignment:
                receipt = Receipt.query.filter_by(payment_id=existing_payment.id).first()
                return jsonify({
                    'success': True,
                    'assignment_id': existing_payment.assignment_id,
                    'payment_id': existing_payment.id,
                    'receipt_id': receipt.id if receipt else None,
                    'receipt_number': receipt.receipt_number if receipt else None,
                    'receipt_url': url_for('view_receipt', receipt_id=receipt.id) if receipt else None,
                    'receipt_pdf_url': url_for('download_receipt', receipt_id=receipt.id) if receipt else None,
                    'message': 'Request already processed (idempotent)'
                })
        
        assignment_data = data.get('assignment', {})
        payment_data = data.get('payment', {})
        invoice_config = data.get('invoice', {})
        receipt_config = data.get('receipt', {})
        
        # Validate required fields
        if not assignment_data.get('customer_id'):
            return jsonify({'success': False, 'error': 'Customer is required'}), 400
        
        if not assignment_data.get('package_id') or not assignment_data.get('package_type'):
            return jsonify({'success': False, 'error': 'Package selection is required'}), 400
        
        # Start transaction
        customer = Customer.query.get(assignment_data['customer_id'])
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
        
        # Get package details
        package_type = assignment_data['package_type']
        package_id = assignment_data['package_id']
        package = get_package_by_type(package_type, package_id)
        
        if not package:
            return jsonify({'success': False, 'error': 'Package not found'}), 404
        
        # Calculate pricing
        subtotal = float(assignment_data.get('price_paid', 0))
        discount = float(assignment_data.get('discount', 0))
        
        # Tax calculation if invoice creation is enabled
        tax_rate = float(invoice_config.get('tax_rate', 0))
        taxable_amount = max(subtotal - discount, 0)
        tax_amount = (taxable_amount * tax_rate / 100) if tax_rate > 0 else 0
        
        # Calculate CGST/SGST (split tax 50/50 for intra-state)
        cgst_amount = tax_amount / 2
        sgst_amount = tax_amount / 2
        
        grand_total = taxable_amount + tax_amount
        
        # Create package assignment
        expires_on = None
        if assignment_data.get('expires_on'):
            expires_on = datetime.fromisoformat(assignment_data['expires_on'].replace('Z', '+00:00'))
        
        assignment = ServicePackageAssignment(
            customer_id=customer.id,
            package_type=package_type,
            package_reference_id=package_id,
            service_id=assignment_data.get('service_id'),
            assigned_on=datetime.utcnow(),
            expires_on=expires_on,
            price_paid=grand_total,
            discount=discount,
            status='active' if payment_data.get('amount', 0) >= grand_total else 'pending',
            notes=assignment_data.get('notes', '')
        )
        
        # Set package-specific fields
        if package_type == 'service_package':
            total_sessions = getattr(package, 'total_sessions', 0)
            assignment.total_sessions = total_sessions
            assignment.remaining_sessions = total_sessions
            assignment.used_sessions = 0
        elif package_type == 'prepaid':
            credit_amount = getattr(package, 'after_value', 0)
            assignment.credit_amount = credit_amount
            assignment.remaining_credit = credit_amount
            assignment.used_credit = 0
        
        db.session.add(assignment)
        db.session.flush()  # Get assignment ID
        
        # Create payment record if payment is being collected
        payment = None
        if payment_data.get('collect') and payment_data.get('amount', 0) > 0:
            payment = Payment(
                customer_id=customer.id,
                assignment_id=assignment.id,
                amount=float(payment_data['amount']),
                payment_method=payment_data.get('method', 'cash'),
                reference=payment_data.get('reference', ''),
                collected_by=current_user.id,
                collected_at=datetime.utcnow(),
                notes=f"Package assignment payment. Idempotency-Key: {idempotency_key}" if idempotency_key else "Package assignment payment"
            )
            db.session.add(payment)
            db.session.flush()  # Get payment ID
        
        # Create receipt if requested
        receipt = None
        if receipt_config.get('generate'):
            receipt_number = Receipt.generate_receipt_number()
            receipt = Receipt(
                receipt_number=receipt_number,
                customer_id=customer.id,
                assignment_id=assignment.id,
                payment_id=payment.id if payment else None,
                amount=grand_total,
                currency='INR',
                subtotal=subtotal,
                discount=discount,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                cgst_amount=cgst_amount,
                sgst_amount=sgst_amount,
                payment_method=payment_data.get('method') if payment else None,
                issued_by=current_user.id,
                created_at=datetime.utcnow()
            )
            db.session.add(receipt)
            db.session.flush()
        
        # Commit transaction
        db.session.commit()
        
        return jsonify({
            'success': True,
            'assignment_id': assignment.id,
            'payment_id': payment.id if payment else None,
            'receipt_id': receipt.id if receipt else None,
            'receipt_number': receipt.receipt_number if receipt else None,
            'receipt_url': url_for('view_receipt', receipt_id=receipt.id) if receipt else None,
            'receipt_pdf_url': url_for('download_receipt', receipt_id=receipt.id) if receipt else None
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in assign-and-pay: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/receipts/<int:receipt_id>')
@login_required
def view_receipt(receipt_id):
    """View receipt in HTML format (printable)"""
    receipt = Receipt.query.get_or_404(receipt_id)
    customer = receipt.customer
    assignment = receipt.assignment
    package = assignment.get_package_template() if assignment else None
    
    return render_template('receipt.html',
                         receipt=receipt,
                         customer=customer,
                         assignment=assignment,
                         package=package,
                         issuer=receipt.issuer)


@app.route('/receipts/<int:receipt_id>/download')
@login_required
def download_receipt(receipt_id):
    """Download receipt as PDF"""
    receipt = Receipt.query.get_or_404(receipt_id)
    customer = receipt.customer
    assignment = receipt.assignment
    package = assignment.get_package_template() if assignment else None
    
    # For now, redirect to HTML view
    # In production, you could use WeasyPrint or wkhtmltopdf to generate PDF
    return redirect(url_for('view_receipt', receipt_id=receipt_id))


def get_package_by_type(package_type, package_id):
    """Helper to get package by type and ID"""
    if package_type == 'prepaid':
        return PrepaidPackage.query.get(package_id)
    elif package_type == 'service_package':
        return ServicePackage.query.get(package_id)
    elif package_type == 'membership':
        return Membership.query.get(package_id)
    elif package_type == 'student_offer':
        return StudentOffer.query.get(package_id)
    elif package_type == 'yearly':
        return YearlyMembership.query.get(package_id)
    elif package_type == 'kitty':
        return KittyParty.query.get(package_id)
    return None


print("✅ Assign packages routes loaded")
