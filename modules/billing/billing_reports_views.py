
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
    revenue_by_date = db.session.query(
        func.date(EnhancedInvoice.invoice_date).label('date'),
        func.sum(EnhancedInvoice.total_amount).label('total_revenue'),
        func.count(EnhancedInvoice.id).label('invoice_count')
    ).filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid'
    ).group_by(func.date(EnhancedInvoice.invoice_date)).all()
    
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

print("✅ Billing reports views imported")
