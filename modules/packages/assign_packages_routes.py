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
    YearlyMembership, KittyParty, PackageBenefitTracker
)
import json
import uuid

assign_packages_bp = Blueprint('assign_packages', __name__, url_prefix='/assign-packages')

# The original code for assign_packages_page was replaced by the changes provided.
# The following is the updated version from the changes.
@assign_packages_bp.route('/')
@login_required
def assign_packages():
    """Render assign packages page"""
    try:
        # Get customer_id from query parameter if provided
        selected_customer_id = request.args.get('customer_id', type=int)

        print(f"📋 Assign Packages Route - customer_id from URL: {selected_customer_id}")

        # Fetch all customers for dropdown
        # Note: The original code used `Customer.query` but the changes use `Client.query`.
        # Assuming `Client` is the correct model name based on the provided changes.
        customers = Customer.query.filter_by(is_active=True).order_by(Customer.first_name).all() # Changed from Client.query based on original code's model usage

        # If customer_id provided, verify it exists
        if selected_customer_id:
            customer_exists = any(c.id == selected_customer_id for c in customers)
            print(f"📋 Customer {selected_customer_id} exists: {customer_exists}")
            if not customer_exists:
                print(f"⚠️ Customer {selected_customer_id} not found in database")
                selected_customer_id = None

        # Fetch all package types
        prepaid_packages = PrepaidPackage.query.filter_by(is_active=True).all()
        service_packages = ServicePackage.query.filter_by(is_active=True).all()
        memberships = Membership.query.filter_by(is_active=True).all()
        student_offers = StudentOffer.query.filter_by(is_active=True).all()
        yearly_memberships = YearlyMembership.query.filter_by(is_active=True).all()
        kitty_parties = KittyParty.query.filter_by(is_active=True).all()

        # Fetch all services for service package assignment
        services = Service.query.filter_by(is_active=True).all()

        # Convert package objects to dictionaries for JSON serialization
        prepaid_packages_data = [{
            'id': p.id,
            'name': p.name,
            'price': p.actual_price,
            'actual_price': p.actual_price,
            'after_value': p.after_value,
            'benefit_percent': p.benefit_percent
        } for p in prepaid_packages]

        service_packages_data = [{
            'id': p.id,
            'name': p.name if hasattr(p, 'name') else p.package_name,
            'price': p.price if hasattr(p, 'price') else 0,
            'total_services': p.total_services if hasattr(p, 'total_services') else 0,
            'pay_for': p.pay_for if hasattr(p, 'pay_for') else 0,
            'freeServices': p.free_services if hasattr(p, 'free_services') else 0,
            'payFor': p.pay_for if hasattr(p, 'pay_for') else 0
        } for p in service_packages]

        memberships_data = [{
            'id': m.id,
            'name': m.name,
            'price': m.price if hasattr(m, 'price') else 0
        } for m in memberships]

        student_offers_data = [{
            'id': s.id,
            'name': s.name,
            'price': s.price if hasattr(s, 'price') else 0,
            'discount_percentage': s.discount_percentage if hasattr(s, 'discount_percentage') else 0
        } for s in student_offers]

        yearly_memberships_data = [{
            'id': y.id,
            'name': y.name,
            'price': y.price if hasattr(y, 'price') else 0
        } for y in yearly_memberships]

        kitty_parties_data = [{
            'id': k.id,
            'name': k.name,
            'price': k.price if hasattr(k, 'price') else 0
        } for k in kitty_parties]

        print(f"📋 Rendering template with {len(customers)} customers, selected_customer_id={selected_customer_id}")

        return render_template(
            'assign_packages.html',
            customers=customers,
            selected_customer_id=selected_customer_id,
            prepaid_packages=prepaid_packages_data,
            service_packages=service_packages_data,
            memberships=memberships_data,
            student_offers=student_offers_data,
            yearly_memberships=yearly_memberships_data,
            kitty_parties=kitty_parties_data,
            services=services
        )
    except Exception as e:
        print(f"Error loading assign packages page: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Error loading assign packages page', 'error')
        return redirect(url_for('dashboard'))


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
            app.logger.error(f"Package not found: type={package_type}, id={package_id}")
            return jsonify({'success': False, 'error': f'Package not found: {package_type} with ID {package_id}'}), 404

        # Log package details for debugging
        app.logger.info(f"📦 Retrieved package: {package.name} (type={package_type}, id={package_id})")
        if package_type == 'service_package':
            app.logger.info(f"   - Total services: {getattr(package, 'total_services', 'NOT SET')}")
            app.logger.info(f"   - Pay for: {getattr(package, 'pay_for', 'NOT SET')}")
        elif package_type == 'prepaid':
            app.logger.info(f"   - After value: {getattr(package, 'after_value', 'NOT SET')}")
            app.logger.info(f"   - Actual price: {getattr(package, 'actual_price', 'NOT SET')}")

        # Calculate pricing with consistent GST logic
        subtotal = float(assignment_data.get('price_paid', 0))
        discount = float(assignment_data.get('discount', 0))

        # Calculate taxable amount (subtotal - discount)
        taxable_amount = max(subtotal - discount, 0)

        # GST Application Rules:
        # 1. Service Packages: 18% GST (9% CGST + 9% SGST) on net amount
        # 2. All Other Packages: NO GST (price is final)
        if package_type == 'service_package':
            tax_rate = 0.18  # 18% total GST
            tax_amount = taxable_amount * tax_rate
            cgst_amount = tax_amount / 2  # 9% CGST
            sgst_amount = tax_amount / 2  # 9% SGST
            grand_total = taxable_amount + tax_amount

            app.logger.info(f"✅ Service Package GST Applied:")
            app.logger.info(f"   - Base Amount: ₹{taxable_amount:.2f}")
            app.logger.info(f"   - CGST (9%): ₹{cgst_amount:.2f}")
            app.logger.info(f"   - SGST (9%): ₹{sgst_amount:.2f}")
            app.logger.info(f"   - Total GST: ₹{tax_amount:.2f}")
            app.logger.info(f"   - Grand Total: ₹{grand_total:.2f}")
        else:
            # NO GST for: prepaid, membership, student_offer, yearly_membership, kitty_party
            tax_rate = 0
            tax_amount = 0
            cgst_amount = 0
            sgst_amount = 0
            grand_total = taxable_amount  # Price is final, no tax added

            app.logger.info(f"✅ No GST for {package_type.upper()}:")
            app.logger.info(f"   - Net Amount: ₹{taxable_amount:.2f}")
            app.logger.info(f"   - Grand Total: ₹{grand_total:.2f} (No GST)")

        # Create package assignment
        expires_on = None
        if assignment_data.get('expires_on'):
            expires_on = datetime.fromisoformat(assignment_data['expires_on'].replace('Z', '+00:00'))

        # Determine status based on payment
        payment_amount = float(payment_data.get('amount', 0))
        assignment_status = 'active'  # Default to active if payment is being collected

        if not payment_data.get('collect'):
            assignment_status = 'pending'
        elif payment_amount < (grand_total - 0.01):  # Allow 1 paisa tolerance for floating-point
            assignment_status = 'pending'  # Partial payment

        assignment = ServicePackageAssignment(
            customer_id=customer.id,
            package_type=package_type,
            package_reference_id=package_id,
            service_id=assignment_data.get('service_id'),
            assigned_on=datetime.utcnow(),
            expires_on=expires_on,
            price_paid=grand_total,
            discount=discount,
            status=assignment_status,
            notes=assignment_data.get('notes', '')
        )

        # Set package-specific fields with proper initialization
        if package_type == 'service_package':
            # Get total sessions from ServicePackage model
            total_sessions = getattr(package, 'total_services', 0)
            if total_sessions == 0:
                # Fallback: try total_sessions attribute
                total_sessions = getattr(package, 'total_sessions', 0)

            # Ensure we have a valid number
            if total_sessions == 0:
                app.logger.error(f"Service package {package.id} has 0 total_sessions - this is invalid!")
                return jsonify({'success': False, 'error': f'Service package "{package.name}" has no sessions configured. Please configure the package first.'}), 400

            # Initialize session tracking - ALWAYS start with 0 used sessions
            assignment.total_sessions = int(total_sessions)
            assignment.used_sessions = 0  # Always start at 0 for new assignments
            assignment.remaining_sessions = int(total_sessions)  # All sessions available initially

            # Initialize credit fields to 0 for service packages
            assignment.credit_amount = 0
            assignment.remaining_credit = 0
            assignment.used_credit = 0

            # Log for debugging with detailed session info
            app.logger.info(f"✅ Service Package assigned: {total_sessions} total sessions for package {package.name} (ID: {package.id})")
            app.logger.info(f"   Session breakdown - Total: {assignment.total_sessions}, Used: {assignment.used_sessions}, Remaining: {assignment.remaining_sessions}")

        elif package_type == 'prepaid':
            # Get credit amount from PrepaidPackage model
            credit_amount = getattr(package, 'after_value', 0)
            if credit_amount == 0:
                # Fallback: try credit_amount attribute
                credit_amount = getattr(package, 'credit_amount', 0)

            # Ensure we have a valid amount
            if credit_amount == 0:
                app.logger.error(f"Prepaid package {package.id} has 0 credit - this is invalid!")
                return jsonify({'success': False, 'error': f'Prepaid package "{package.name}" has no credit configured. Please configure the package first.'}), 400

            assignment.credit_amount = float(credit_amount)
            assignment.remaining_credit = float(credit_amount)
            assignment.used_credit = 0

            # Initialize session fields to 0 for prepaid packages
            assignment.total_sessions = 0
            assignment.remaining_sessions = 0
            assignment.used_sessions = 0

            # Log for debugging
            app.logger.info(f"✅ Prepaid Package assigned: ₹{credit_amount} credit for package {package.name} (ID: {package.id})")
        else:
            # For other package types (membership, student_offer, etc.), initialize all fields to 0
            assignment.total_sessions = 0
            assignment.remaining_sessions = 0
            assignment.used_sessions = 0
            assignment.credit_amount = 0
            assignment.remaining_credit = 0
            assignment.used_credit = 0

        db.session.add(assignment)
        db.session.flush()  # Get assignment ID

        # === CRITICAL: Create PackageBenefitTracker for billing integration ===
        from models import PackageBenefitTracker

        benefit_tracker = None

        if package_type == 'prepaid':
            # Prepaid package - track credit balance
            credit_amount = getattr(package, 'after_value', 0)
            benefit_tracker = PackageBenefitTracker(
                customer_id=customer.id,
                package_assignment_id=assignment.id,
                service_id=None,  # Prepaid works for all services
                benefit_type='prepaid',
                balance_total=credit_amount,
                balance_used=0,
                balance_remaining=credit_amount,
                valid_from=datetime.utcnow(),
                valid_to=expires_on or (datetime.utcnow() + timedelta(days=365)),
                is_active=True
            )

        elif package_type == 'service_package':
            # Service package - track free sessions
            total_sessions = getattr(package, 'total_services', 0)
            if total_sessions == 0:
                # Fallback: try total_sessions attribute
                total_sessions = getattr(package, 'total_sessions', 0)

            # Calculate free sessions (benefit)
            paid_sessions = getattr(package, 'pay_for', 0)
            free_sessions = total_sessions - paid_sessions if total_sessions > paid_sessions else 0

            # CRITICAL: Ensure total_allocated is set correctly
            if total_sessions == 0:
                app.logger.error(f"Service package {package.name} has 0 total sessions - this is invalid!")
                return jsonify({
                    'success': False,
                    'error': f'Service package "{package.name}" has no sessions configured. Please configure the package first.'
                }), 400

            benefit_tracker = PackageBenefitTracker(
                customer_id=customer.id,
                package_assignment_id=assignment.id,
                service_id=assignment_data.get('service_id'),
                benefit_type='free',
                total_allocated=total_sessions,  # This is the TOTAL sessions customer can use
                used_count=0,
                remaining_count=total_sessions,  # Initially, all sessions are available
                valid_from=datetime.utcnow(),
                valid_to=expires_on or (datetime.utcnow() + timedelta(days=365)),
                is_active=True
            )

            # Log for debugging with detailed session info
            app.logger.info(f"✅ Benefit tracker created: TOTAL={total_sessions} sessions, REMAINING={total_sessions}, USED=0 (Package had {paid_sessions} paid + {free_sessions} free)")

        elif package_type == 'membership':
            # Membership - unlimited access
            benefit_tracker = PackageBenefitTracker(
                customer_id=customer.id,
                package_assignment_id=assignment.id,
                service_id=None,  # Membership covers specific services (checked via membership_services)
                benefit_type='unlimited',
                total_allocated=999999,
                used_count=0,
                remaining_count=999999,
                valid_from=datetime.utcnow(),
                valid_to=expires_on or (datetime.utcnow() + timedelta(days=365)),
                is_active=True
            )

        elif package_type == 'student_offer':
            # Student offer - discount percentage
            discount_percent = getattr(package, 'discount_percentage', 0)
            benefit_tracker = PackageBenefitTracker(
                customer_id=customer.id,
                package_assignment_id=assignment.id,
                service_id=None,  # Student offer covers specific services (checked via student_offer_services)
                benefit_type='discount',
                discount_percentage=discount_percent,
                total_allocated=999,  # High number for discount uses
                used_count=0,
                remaining_count=999,
                valid_from=datetime.utcnow(),
                valid_to=expires_on or (datetime.utcnow() + timedelta(days=365)),
                is_active=True
            )

        if benefit_tracker:
            db.session.add(benefit_tracker)
            db.session.flush()

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


@app.route('/packages/api/assignments', methods=['GET'])
@login_required
def api_get_assignments():
    """Get all package assignments with filtering, search, and pagination"""
    try:
        # Get query parameters
        q = request.args.get('q', '').strip()
        status = request.args.get('status', '').strip()
        expiring_in = request.args.get('expiring_in', '').strip()
        package_type = request.args.get('package_type', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        sort = request.args.get('sort', 'assigned_on:desc')

        # Base query
        query = ServicePackageAssignment.query

        # Apply package type filter
        if package_type:
            query = query.filter(ServicePackageAssignment.package_type == package_type)

        # Apply status filter
        if status:
            query = query.filter(ServicePackageAssignment.status == status)

        # Expiring soon filter
        if expiring_in:
            days = int(expiring_in)
            expiry_date = datetime.utcnow() + timedelta(days=days)
            query = query.filter(
                ServicePackageAssignment.expires_on.isnot(None),
                ServicePackageAssignment.expires_on <= expiry_date,
                ServicePackageAssignment.expires_on >= datetime.utcnow(),
                ServicePackageAssignment.status == 'active'
            )

        # Search filter
        if q:
            query = query.join(Customer).filter(
                or_(
                    Customer.first_name.ilike(f'%{q}%'),
                    Customer.last_name.ilike(f'%{q}%'),
                    Customer.phone.ilike(f'%{q}%')
                )
            )

        # Apply sorting
        if ':' in sort:
            field, direction = sort.split(':')
            if field == 'expires_on':
                query = query.order_by(
                    ServicePackageAssignment.expires_on.desc() if direction == 'desc'
                    else ServicePackageAssignment.expires_on.asc()
                )
            elif field == 'assigned_on':
                query = query.order_by(
                    ServicePackageAssignment.assigned_on.desc() if direction == 'desc'
                    else ServicePackageAssignment.assigned_on.asc()
                )

        # Pagination
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        # Build response
        items = []
        for assignment in paginated.items:
            customer = assignment.customer
            package = assignment.get_package_template()
            service = assignment.service

            # Calculate expiring days
            expiring_days = None
            if assignment.expires_on:
                delta = assignment.expires_on - datetime.utcnow()
                expiring_days = delta.days

            # Get last usage
            from models import PackageAssignmentUsage
            last_usage = PackageAssignmentUsage.query.filter_by(
                assignment_id=assignment.id
            ).order_by(PackageAssignmentUsage.usage_date.desc()).first()

            # Calculate savings
            savings = 0
            if assignment.package_type == 'service_package' and package:
                benefit_percent = getattr(package, 'benefit_percent', 0)
                if benefit_percent > 0:
                    savings = (assignment.price_paid * benefit_percent) / 100

            item = {
                'id': assignment.id,
                'customer': {
                    'id': customer.id,
                    'name': f"{customer.first_name} {customer.last_name}",
                    'phone': customer.phone or ''
                },
                'package': {
                    'name': package.name if package else 'Unknown',
                    'type': assignment.package_type,
                    'service_name': service.name if service else None
                },
                'assigned_on': assignment.assigned_on.isoformat() if assignment.assigned_on else None,
                'expires_on': assignment.expires_on.strftime('%Y-%m-%d') if assignment.expires_on else None,
                'expiring_in_days': expiring_days,
                'status': assignment.status,
                'price_paid': float(assignment.price_paid) if assignment.price_paid else 0,
                'savings_to_date': float(savings),
                'last_used_at': last_usage.usage_date.isoformat() if last_usage else None,
                'sessions': {
                    'total': assignment.total_sessions or 0,
                    'used': assignment.used_sessions or 0,
                    'remaining': assignment.remaining_sessions or assignment.total_sessions or 0
                } if assignment.package_type == 'service_package' else None,
                'credit': {
                    'total': float(assignment.credit_amount or 0),
                    'used': float(assignment.used_credit or 0),
                    'remaining': float(assignment.remaining_credit or assignment.credit_amount or 0)
                } if assignment.package_type == 'prepaid' else None
            }
            items.append(item)

        return jsonify({
            'success': True,
            'items': items,
            'page': page,
            'per_page': per_page,
            'total': paginated.total,
            'pages': paginated.pages
        })

    except Exception as e:
        print(f"Error fetching assignments: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/packages/api/assignments/<int:assignment_id>/usage', methods=['GET'])
@login_required
def api_get_assignment_usage(assignment_id):
    """Get usage history for a specific assignment"""
    try:
        assignment = ServicePackageAssignment.query.get_or_404(assignment_id)

        # Get usage logs
        from models import PackageAssignmentUsage
        usage_logs = PackageAssignmentUsage.query.filter_by(
            assignment_id=assignment_id
        ).order_by(PackageAssignmentUsage.usage_date.desc()).all()

        # Build usage history
        usage_history = []
        for log in usage_logs:
            from models import User
            user = User.query.get(log.staff_id) if log.staff_id else None
            service = log.service

            usage_history.append({
                'id': log.id,
                'date': log.usage_date.isoformat() if log.usage_date else None,
                'service': service.name if service else 'N/A',
                'type': log.change_type or 'use',
                'sessions': log.sessions_used or 0,
                'amount': float(log.credit_used) if log.credit_used else 0,
                'invoice_id': log.appointment_id or '',
                'user': f"{user.username}" if user else 'System',
                'notes': log.notes or ''
            })

        # Summary
        summary = {
            'total_sessions': assignment.total_sessions,
            'sessions_used': assignment.used_sessions,
            'sessions_remaining': assignment.remaining_sessions,
            'total_credit': float(assignment.credit_amount) if assignment.credit_amount else 0,
            'credit_used': float(assignment.used_credit) if assignment.used_credit else 0,
            'credit_remaining': float(assignment.remaining_credit) if assignment.remaining_credit else 0,
            'total_value': float(assignment.price_paid) if assignment.price_paid else 0
        }

        return jsonify({
            'success': True,
            'summary': summary,
            'usage': usage_history
        })

    except Exception as e:
        print(f"Error fetching usage: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


print("✅ Assign packages routes loaded")