
"""
Client Revenue Report - Dedicated detailed reporting
"""
from flask import render_template, request
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func
from app import app, db
from models import EnhancedInvoice, InvoiceItem, Customer, User, Service

@app.route('/billing/reports/client-revenue')
@login_required
def client_revenue_report():
    """Detailed client revenue report"""
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
    
    # Client transaction details
    client_transaction_details = db.session.query(
        Customer.id.label('client_id'),
        Customer.first_name,
        Customer.last_name,
        Customer.phone,
        Customer.email,
        EnhancedInvoice.invoice_number,
        EnhancedInvoice.invoice_date,
        User.first_name.label('staff_first_name'),
        User.last_name.label('staff_last_name'),
        Service.name.label('service_name'),
        InvoiceItem.quantity,
        InvoiceItem.unit_price,
        InvoiceItem.final_amount,
        EnhancedInvoice.payment_status
    ).join(EnhancedInvoice, Customer.id == EnhancedInvoice.client_id)\
    .join(InvoiceItem, EnhancedInvoice.id == InvoiceItem.invoice_id)\
    .outerjoin(User, InvoiceItem.staff_id == User.id)\
    .outerjoin(Service, InvoiceItem.item_id == Service.id)\
    .filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date)
    ).order_by(Customer.first_name, EnhancedInvoice.invoice_date.desc()).all()
    
    # Client summary statistics
    client_summary = db.session.query(
        Customer.id.label('client_id'),
        Customer.first_name,
        Customer.last_name,
        Customer.phone,
        func.count(func.distinct(EnhancedInvoice.id)).label('total_invoices'),
        func.sum(EnhancedInvoice.total_amount).label('total_spent'),
        func.avg(EnhancedInvoice.total_amount).label('avg_invoice_value'),
        func.max(EnhancedInvoice.invoice_date).label('last_visit')
    ).join(EnhancedInvoice, Customer.id == EnhancedInvoice.client_id)\
    .filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid'
    ).group_by(Customer.id).order_by(func.sum(EnhancedInvoice.total_amount).desc()).all()
    
    # Top services by client
    top_services_by_client = db.session.query(
        Customer.id.label('client_id'),
        Customer.first_name,
        Customer.last_name,
        Service.name.label('service_name'),
        func.count(InvoiceItem.id).label('service_count'),
        func.sum(InvoiceItem.final_amount).label('service_revenue')
    ).join(EnhancedInvoice, Customer.id == EnhancedInvoice.client_id)\
    .join(InvoiceItem, EnhancedInvoice.id == InvoiceItem.invoice_id)\
    .join(Service, InvoiceItem.item_id == Service.id)\
    .filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid',
        InvoiceItem.item_type == 'service'
    ).group_by(Customer.id, Service.id).order_by(Customer.first_name, func.count(InvoiceItem.id).desc()).all()
    
    return render_template('reports/client_revenue_report.html',
                         start_date=start_date,
                         end_date=end_date,
                         client_transaction_details=client_transaction_details,
                         client_summary=client_summary,
                         top_services_by_client=top_services_by_client)

print("✅ Client revenue report views imported")
