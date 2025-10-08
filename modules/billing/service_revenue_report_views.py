
"""
Service Revenue Report - Dedicated detailed reporting
"""
from flask import render_template, request
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func
from app import app, db
from models import EnhancedInvoice, InvoiceItem, Customer, User, Service, ServiceCategory

@app.route('/billing/reports/service-revenue')
@login_required
def service_revenue_report():
    """Detailed service revenue report"""
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
    
    # Service transaction details
    service_transaction_details = db.session.query(
        Service.id.label('service_id'),
        Service.name,
        Service.price,
        ServiceCategory.name.label('category'),
        Customer.first_name.label('client_first_name'),
        Customer.last_name.label('client_last_name'),
        User.first_name.label('staff_first_name'),
        User.last_name.label('staff_last_name'),
        EnhancedInvoice.invoice_number,
        EnhancedInvoice.invoice_date,
        InvoiceItem.quantity,
        InvoiceItem.unit_price,
        InvoiceItem.final_amount
    ).join(InvoiceItem, Service.id == InvoiceItem.item_id)\
    .join(EnhancedInvoice, InvoiceItem.invoice_id == EnhancedInvoice.id)\
    .join(Customer, EnhancedInvoice.client_id == Customer.id)\
    .outerjoin(User, InvoiceItem.staff_id == User.id)\
    .outerjoin(ServiceCategory, Service.category_id == ServiceCategory.id)\
    .filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid',
        InvoiceItem.item_type == 'service'
    ).order_by(Service.name, EnhancedInvoice.invoice_date.desc()).all()
    
    # Service summary statistics
    service_summary = db.session.query(
        Service.id.label('service_id'),
        Service.name,
        Service.price,
        ServiceCategory.name.label('category'),
        func.count(InvoiceItem.id).label('total_bookings'),
        func.sum(InvoiceItem.quantity).label('total_quantity'),
        func.sum(InvoiceItem.final_amount).label('total_revenue'),
        func.avg(InvoiceItem.final_amount).label('avg_revenue_per_booking'),
        func.count(func.distinct(Customer.id)).label('unique_clients')
    ).join(InvoiceItem, Service.id == InvoiceItem.item_id)\
    .join(EnhancedInvoice, InvoiceItem.invoice_id == EnhancedInvoice.id)\
    .join(Customer, EnhancedInvoice.client_id == Customer.id)\
    .outerjoin(ServiceCategory, Service.category_id == ServiceCategory.id)\
    .filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid',
        InvoiceItem.item_type == 'service'
    ).group_by(Service.id, ServiceCategory.id).order_by(func.sum(InvoiceItem.final_amount).desc()).all()
    
    # Category summary
    category_summary = db.session.query(
        ServiceCategory.name.label('category'),
        func.count(func.distinct(Service.id)).label('service_count'),
        func.sum(InvoiceItem.final_amount).label('total_revenue'),
        func.count(InvoiceItem.id).label('total_bookings')
    ).join(Service, ServiceCategory.id == Service.category_id)\
    .join(InvoiceItem, Service.id == InvoiceItem.item_id)\
    .join(EnhancedInvoice, InvoiceItem.invoice_id == EnhancedInvoice.id)\
    .filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid',
        InvoiceItem.item_type == 'service'
    ).group_by(ServiceCategory.id).all()
    
    return render_template('reports/service_revenue_report.html',
                         start_date=start_date,
                         end_date=end_date,
                         service_transaction_details=service_transaction_details,
                         service_summary=service_summary,
                         category_summary=category_summary)

print("✅ Service revenue report views imported")
