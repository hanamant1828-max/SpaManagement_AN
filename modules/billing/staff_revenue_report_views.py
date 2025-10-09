"""
Staff Revenue Report - Dedicated detailed reporting
"""
from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func
from app import app, db
from models import EnhancedInvoice, InvoiceItem, Customer, User, Department, Service

@app.route('/billing/reports/staff-revenue')
@login_required
def staff_revenue_report():
    """Detailed staff revenue report with client details"""
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

    # Detailed staff revenue with client info (includes products and services)
    staff_revenue_details = db.session.query(
        User.id.label('staff_id'),
        User.first_name,
        User.last_name,
        User.staff_code,
        Department.display_name.label('department'),
        Customer.id.label('customer_id'),
        Customer.first_name.label('customer_first_name'),
        Customer.last_name.label('customer_last_name'),
        EnhancedInvoice.invoice_number,
        EnhancedInvoice.invoice_date,
        InvoiceItem.item_type.label('item_type'),
        InvoiceItem.item_name.label('item_name'),
        Service.name.label('service_name'),
        InvoiceItem.quantity,
        InvoiceItem.staff_revenue_price.label('staff_revenue_price'),
        InvoiceItem.final_amount.label('final_amount')
    ).join(InvoiceItem, User.id == InvoiceItem.staff_id)\
    .join(EnhancedInvoice, InvoiceItem.invoice_id == EnhancedInvoice.id)\
    .join(Customer, EnhancedInvoice.client_id == Customer.id)\
    .outerjoin(Department, User.department_id == Department.id)\
    .outerjoin(Service, InvoiceItem.item_id == Service.id)\
    .filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid',
        InvoiceItem.staff_id.isnot(None)
    ).order_by(User.first_name, EnhancedInvoice.invoice_date.desc()).all()

    # Staff summary statistics with service/product breakdown
    staff_summary = db.session.query(
        User.id.label('staff_id'),
        User.first_name,
        User.last_name,
        User.staff_code,
        Department.display_name.label('department'),
        func.count(func.distinct(Customer.id)).label('unique_clients'),
        func.count(InvoiceItem.id).label('total_items'),
        func.sum(InvoiceItem.staff_revenue_price).label('total_revenue'),
        func.sum(
            func.case(
                (InvoiceItem.item_type == 'service', InvoiceItem.staff_revenue_price),
                (InvoiceItem.item_type == 'inventory', InvoiceItem.staff_revenue_price)
            ).else_(0)
        ).label('service_revenue'),
        func.sum(
            func.case(
                (InvoiceItem.item_type == 'inventory', InvoiceItem.staff_revenue_price),
                (InvoiceItem.item_type == 'service', InvoiceItem.staff_revenue_price)
            ).else_(0)
        ).label('product_revenue'),
        func.count(
            func.case(
                (InvoiceItem.item_type == 'service', InvoiceItem.id),
                else_=None
            )
        ).label('service_count'),
        func.count(
            func.case(
                (InvoiceItem.item_type == 'inventory', InvoiceItem.id),
                else_=None
            )
        ).label('product_count')
    ).join(InvoiceItem, User.id == InvoiceItem.staff_id)\
    .join(EnhancedInvoice, InvoiceItem.invoice_id == EnhancedInvoice.id)\
    .join(Customer, EnhancedInvoice.client_id == Customer.id)\
    .outerjoin(Department, User.department_id == Department.id)\
    .filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid',
        InvoiceItem.staff_id.isnot(None)
    ).group_by(User.id, Department.id).order_by(func.sum(InvoiceItem.staff_revenue_price).desc()).all()

    # Department summary
    department_summary = db.session.query(
        Department.display_name.label('department'),
        func.count(func.distinct(User.id)).label('staff_count'),
        func.sum(InvoiceItem.staff_revenue_price).label('total_revenue'),
        func.count(InvoiceItem.id).label('total_services')
    ).join(User, Department.id == User.department_id)\
    .join(InvoiceItem, User.id == InvoiceItem.staff_id)\
    .join(EnhancedInvoice, InvoiceItem.invoice_id == EnhancedInvoice.id)\
    .filter(
        EnhancedInvoice.invoice_date.between(start_date, end_date),
        EnhancedInvoice.payment_status == 'paid'
    ).group_by(Department.id).all()

    return render_template('reports/staff_revenue_report.html',
                         start_date=start_date,
                         end_date=end_date,
                         staff_revenue_details=staff_revenue_details,
                         staff_summary=staff_summary,
                         department_summary=department_summary)

print("✅ Staff revenue report views imported")