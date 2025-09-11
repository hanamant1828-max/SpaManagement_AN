"""
Billing-related database queries
"""
from datetime import datetime, date
from sqlalchemy import func, and_
from app import db
# Late imports to avoid circular dependency

def get_all_invoices():
    """Get all invoices"""
    from models import Invoice
    return Invoice.query.order_by(Invoice.created_at.desc()).all()

def get_pending_invoices():
    """Get pending invoices"""
    return Invoice.query.filter_by(payment_status='pending').order_by(Invoice.created_at.desc()).all()

def get_paid_invoices():
    """Get paid invoices"""
    return Invoice.query.filter_by(payment_status='paid').order_by(Invoice.created_at.desc()).all()

def get_invoice_by_id(invoice_id):
    """Get invoice by ID"""
    return Invoice.query.get(invoice_id)

def create_invoice(invoice_data):
    """Create a new invoice"""
    from models import Invoice
    invoice = Invoice(**invoice_data)
    db.session.add(invoice)
    db.session.commit()
    return invoice

def update_invoice(invoice_id, invoice_data):
    """Update an existing invoice"""
    invoice = Invoice.query.get(invoice_id)
    if invoice:
        for key, value in invoice_data.items():
            setattr(invoice, key, value)
        db.session.commit()
    return invoice

def mark_invoice_paid(invoice_id):
    """Mark an invoice as paid"""
    invoice = Invoice.query.get(invoice_id)
    if invoice:
        invoice.payment_status = 'paid'
        db.session.commit()
    return invoice

def get_revenue_stats():
    """Get revenue statistics"""
    today = date.today()
    
    stats = {
        'total_revenue': db.session.query(func.sum(Invoice.total_amount)).filter(
            Invoice.payment_status == 'paid'
        ).scalar() or 0,
        'monthly_revenue': db.session.query(func.sum(Invoice.total_amount)).filter(
            Invoice.payment_status == 'paid',
            func.extract('month', Invoice.created_at) == today.month,
            func.extract('year', Invoice.created_at) == today.year
        ).scalar() or 0,
        'pending_amount': db.session.query(func.sum(Invoice.total_amount)).filter(
            Invoice.payment_status == 'pending'
        ).scalar() or 0,
        'invoice_count': Invoice.query.count()
    }
    
    return stats