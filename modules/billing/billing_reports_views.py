
"""
Billing Reports Views - Dedicated reporting for billing and invoices
"""
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from app import app, db
from models import EnhancedInvoice, InvoiceItem, InvoicePayment, Customer, User, Service

@app.route('/billing/reports')
@login_required
def billing_reports():
    """Main billing reports dashboard"""
    if not current_user.is_active:
        return redirect(url_for('dashboard'))
    
    # Default to last 30 days
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Get date range from request
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Revenue by date
    revenue_by_date_raw = db.session.query(
        func.date(EnhancedInvoice.invoice_date).label('date'),
        func.sum(EnhancedInvoice.total_amount).label('total_revenue'),
        func.count(EnhancedInvoice.id).label('invoice_count')
    ).filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid'
    ).group_by(func.date(EnhancedInvoice.invoice_date)).all()
    
    # Convert string dates to date objects
    from datetime import datetime
    revenue_by_date = []
    for item in revenue_by_date_raw:
        if isinstance(item.date, str):
            date_obj = datetime.strptime(item.date, '%Y-%m-%d').date()
        else:
            date_obj = item.date
        
        # Create a new named tuple-like object with converted date
        from collections import namedtuple
        RevenueItem = namedtuple('RevenueItem', ['date', 'total_revenue', 'invoice_count'])
        revenue_by_date.append(RevenueItem(date_obj, item.total_revenue, item.invoice_count))
    
    # Revenue by payment method
    revenue_by_method = db.session.query(
        InvoicePayment.payment_method,
        func.sum(InvoicePayment.amount).label('total'),
        func.count(InvoicePayment.id).label('count')
    ).join(EnhancedInvoice, InvoicePayment.invoice_id == EnhancedInvoice.id).filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid'
    ).group_by(InvoicePayment.payment_method).all()
    
    # Top customers by revenue
    top_customers = db.session.query(
        Customer.id,
        Customer.first_name,
        Customer.last_name,
        func.sum(EnhancedInvoice.total_amount).label('total_spent'),
        func.count(EnhancedInvoice.id).label('invoice_count')
    ).join(EnhancedInvoice, Customer.id == EnhancedInvoice.client_id).filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid'
    ).group_by(Customer.id).order_by(func.sum(EnhancedInvoice.total_amount).desc()).limit(10).all()
    
    # Top services by revenue
    top_services = db.session.query(
        Service.id,
        Service.name,
        func.sum(InvoiceItem.final_amount).label('total_revenue'),
        func.sum(InvoiceItem.quantity).label('total_quantity')
    ).join(InvoiceItem, Service.id == InvoiceItem.item_id).join(
        EnhancedInvoice, InvoiceItem.invoice_id == EnhancedInvoice.id
    ).filter(
        InvoiceItem.item_type == 'service',
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid'
    ).group_by(Service.id).order_by(func.sum(InvoiceItem.final_amount).desc()).limit(10).all()
    
    # Staff performance by revenue
    staff_performance = db.session.query(
        User.id,
        User.first_name,
        User.last_name,
        func.sum(InvoiceItem.staff_revenue_price).label('total_revenue'),
        func.count(InvoiceItem.id).label('item_count')
    ).join(InvoiceItem, User.id == InvoiceItem.staff_id).join(
        EnhancedInvoice, InvoiceItem.invoice_id == EnhancedInvoice.id
    ).filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid',
        InvoiceItem.staff_id.isnot(None)
    ).group_by(User.id).order_by(func.sum(InvoiceItem.staff_revenue_price).desc()).all()
    
    # Calculate summary stats
    total_revenue = db.session.query(func.sum(EnhancedInvoice.total_amount)).filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid'
    ).scalar() or 0
    
    total_invoices = db.session.query(func.count(EnhancedInvoice.id)).filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date)
    ).scalar() or 0
    
    pending_amount = db.session.query(func.sum(EnhancedInvoice.balance_due)).filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status.in_(['pending', 'partial'])
    ).scalar() or 0
    
    avg_invoice_value = total_revenue / total_invoices if total_invoices > 0 else 0
    
    # Tax collected
    total_tax = db.session.query(func.sum(EnhancedInvoice.tax_amount)).filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid'
    ).scalar() or 0
    
    # Package deductions
    total_package_deductions = db.session.query(func.sum(InvoiceItem.deduction_amount)).join(
        EnhancedInvoice, InvoiceItem.invoice_id == EnhancedInvoice.id
    ).filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        InvoiceItem.is_package_deduction == True
    ).scalar() or 0
    
    return render_template('billing_reports.html',
                         start_date=start_date,
                         end_date=end_date,
                         revenue_by_date=revenue_by_date,
                         revenue_by_method=revenue_by_method,
                         top_customers=top_customers,
                         top_services=top_services,
                         staff_performance=staff_performance,
                         total_revenue=total_revenue,
                         total_invoices=total_invoices,
                         pending_amount=pending_amount,
                         avg_invoice_value=avg_invoice_value,
                         total_tax=total_tax,
                         total_package_deductions=total_package_deductions)

@app.route('/api/billing/revenue-chart')
@login_required
def billing_revenue_chart():
    """API endpoint for revenue chart data"""
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
    
    revenue_data = db.session.query(
        func.date(EnhancedInvoice.invoice_date).label('date'),
        func.sum(EnhancedInvoice.total_amount).label('revenue')
    ).filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid'
    ).group_by(func.date(EnhancedInvoice.invoice_date)).all()
    
    return jsonify({
        'labels': [item.date.strftime('%Y-%m-%d') for item in revenue_data],
        'data': [float(item.revenue or 0) for item in revenue_data]
    })

@app.route('/billing/reports/service-revenue-only')
@login_required
def service_revenue_only_report():
    """Detailed service revenue report (services only, no products)"""
    if not current_user.is_active:
        return redirect(url_for('dashboard'))
    
    # Default to last 30 days
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Get date range from request
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Service revenue summary
    service_revenue_summary = db.session.query(
        Service.id,
        Service.name,
        Service.price,
        func.count(InvoiceItem.id).label('total_bookings'),
        func.sum(InvoiceItem.quantity).label('total_quantity'),
        func.sum(InvoiceItem.final_amount).label('total_revenue'),
        func.avg(InvoiceItem.final_amount).label('avg_revenue')
    ).join(InvoiceItem, Service.id == InvoiceItem.item_id)\
    .join(EnhancedInvoice, InvoiceItem.invoice_id == EnhancedInvoice.id)\
    .filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid',
        InvoiceItem.item_type == 'service'
    ).group_by(Service.id).order_by(func.sum(InvoiceItem.final_amount).desc()).all()
    
    # Service revenue by date
    service_revenue_by_date = db.session.query(
        func.date(EnhancedInvoice.invoice_date).label('date'),
        func.sum(InvoiceItem.final_amount).label('revenue'),
        func.count(InvoiceItem.id).label('bookings')
    ).join(EnhancedInvoice, InvoiceItem.invoice_id == EnhancedInvoice.id)\
    .filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid',
        InvoiceItem.item_type == 'service'
    ).group_by(func.date(EnhancedInvoice.invoice_date)).all()
    
    # Calculate totals
    total_service_revenue = sum([item.total_revenue or 0 for item in service_revenue_summary])
    total_service_bookings = sum([item.total_bookings or 0 for item in service_revenue_summary])
    
    return render_template('reports/service_revenue_only.html',
                         start_date=start_date,
                         end_date=end_date,
                         service_revenue_summary=service_revenue_summary,
                         service_revenue_by_date=service_revenue_by_date,
                         total_service_revenue=total_service_revenue,
                         total_service_bookings=total_service_bookings)

@app.route('/billing/reports/product-revenue-only')
@login_required
def product_revenue_only_report():
    """Detailed product revenue report (inventory/products only, no services)"""
    if not current_user.is_active:
        return redirect(url_for('dashboard'))
    
    # Default to last 30 days
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Get date range from request
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Import inventory models
    try:
        from modules.inventory.models import InventoryProduct
        
        # Product revenue summary
        product_revenue_summary = db.session.query(
            InventoryProduct.id,
            InventoryProduct.name,
            InvoiceItem.batch_name,
            func.sum(InvoiceItem.quantity).label('total_quantity'),
            func.avg(InvoiceItem.unit_price).label('avg_price'),
            func.sum(InvoiceItem.final_amount).label('total_revenue'),
            func.count(InvoiceItem.id).label('total_sales')
        ).join(InvoiceItem, InventoryProduct.id == InvoiceItem.product_id)\
        .join(EnhancedInvoice, InvoiceItem.invoice_id == EnhancedInvoice.id)\
        .filter(
            EnhancedInvoice.invoice_date.between(start_date, end_date),
            EnhancedInvoice.payment_status == 'paid',
            InvoiceItem.item_type == 'inventory'
        ).group_by(InventoryProduct.id, InvoiceItem.batch_name)\
        .order_by(func.sum(InvoiceItem.final_amount).desc()).all()
        
        # Product revenue by date
        product_revenue_by_date = db.session.query(
            func.date(EnhancedInvoice.invoice_date).label('date'),
            func.sum(InvoiceItem.final_amount).label('revenue'),
            func.sum(InvoiceItem.quantity).label('quantity_sold')
        ).join(EnhancedInvoice, InvoiceItem.invoice_id == EnhancedInvoice.id)\
        .filter(
            EnhancedInvoice.invoice_date.between(start_date, end_date),
            EnhancedInvoice.payment_status == 'paid',
            InvoiceItem.item_type == 'inventory'
        ).group_by(func.date(EnhancedInvoice.invoice_date)).all()
        
    except ImportError:
        product_revenue_summary = []
        product_revenue_by_date = []
    
    # Calculate totals
    total_product_revenue = sum([item.total_revenue or 0 for item in product_revenue_summary])
    total_product_sales = sum([item.total_sales or 0 for item in product_revenue_summary])
    total_quantity_sold = sum([item.total_quantity or 0 for item in product_revenue_summary])
    
    return render_template('reports/product_revenue_only.html',
                         start_date=start_date,
                         end_date=end_date,
                         product_revenue_summary=product_revenue_summary,
                         product_revenue_by_date=product_revenue_by_date,
                         total_product_revenue=total_product_revenue,
                         total_product_sales=total_product_sales,
                         total_quantity_sold=total_quantity_sold)

@app.route('/billing/reports/payment-audit')
@login_required
def payment_audit_report():
    """Daily payment audit report by payment method"""
    from models import InvoicePayment
    
    # Get date from request or default to today
    audit_date_str = request.args.get('audit_date')
    if audit_date_str:
        try:
            audit_date = datetime.strptime(audit_date_str, '%Y-%m-%d').date()
        except ValueError:
            audit_date = date.today()
    else:
        audit_date = date.today()
    
    # Get all payments for the selected date
    # CRITICAL: Query payments where the DATE portion matches audit_date
    # This handles both naive datetimes and timezone-aware datetimes
    payments = InvoicePayment.query.filter(
        func.date(InvoicePayment.payment_date) == audit_date
    ).order_by(InvoicePayment.payment_date.desc()).all()
    
    print(f"🔍 Payment Audit Debug:")
    print(f"  Audit date: {audit_date}")
    print(f"  Total payments found: {len(payments)}")
    if payments:
        for p in payments[:3]:  # Show first 3 for debugging
            print(f"    Payment ID {p.id}: {p.payment_method} - ₹{p.amount} on {p.payment_date}")
    
    # Calculate totals by payment method
    cash_payments = [p for p in payments if p.payment_method == 'cash']
    card_payments = [p for p in payments if p.payment_method == 'card']
    upi_payments = [p for p in payments if p.payment_method == 'upi']
    cheque_payments = [p for p in payments if p.payment_method == 'cheque']
    
    print(f"  Cash: {len(cash_payments)}, Card: {len(card_payments)}, UPI: {len(upi_payments)}, Cheque: {len(cheque_payments)}")
    
    cash_total = sum(p.amount for p in cash_payments)
    card_total = sum(p.amount for p in card_payments)
    upi_total = sum(p.amount for p in upi_payments)
    cheque_total = sum(p.amount for p in cheque_payments)
    
    total_collection = cash_total + card_total + upi_total + cheque_total
    
    return render_template('payment_audit_report.html',
                         audit_date=audit_date,
                         payments=payments,
                         cash_total=cash_total,
                         card_total=card_total,
                         upi_total=upi_total,
                         cheque_total=cheque_total,
                         cash_count=len(cash_payments),
                         card_count=len(card_payments),
                         upi_count=len(upi_payments),
                         cheque_count=len(cheque_payments),
                         total_collection=total_collection,
                         total_transactions=len(payments))

print("✅ Billing reports views imported")
