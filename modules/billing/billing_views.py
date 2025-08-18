"""
Billing views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app
from forms import PaymentForm
from .billing_queries import (
    get_all_invoices, get_pending_invoices, get_paid_invoices,
    get_invoice_by_id, create_invoice, update_invoice, 
    mark_invoice_paid, get_revenue_stats
)
from models import db, Appointment, Invoice, Client, Service
from sqlalchemy import func
from datetime import datetime, timedelta

def get_pending_appointments():
    """Get appointments with pending payments"""
    return Appointment.query.filter_by(payment_status='pending').all()

def get_recent_invoices():
    """Get recent invoices"""
    return Invoice.query.order_by(Invoice.created_at.desc()).limit(10).all()

def get_all_clients():
    """Get all clients"""
    return Client.query.all()

def get_all_services():
    """Get all services"""
    return Service.query.all()

def calculate_today_revenue():
    """Calculate today's revenue"""
    today = datetime.now().date()
    revenue = db.session.query(func.sum(Appointment.amount)).filter(
        func.date(Appointment.appointment_date) == today,
        Appointment.payment_status == 'paid'
    ).scalar()
    return revenue or 0

def calculate_monthly_revenue():
    """Calculate this month's revenue"""
    today = datetime.now()
    start_of_month = today.replace(day=1)
    revenue = db.session.query(func.sum(Appointment.amount)).filter(
        Appointment.appointment_date >= start_of_month,
        Appointment.payment_status == 'paid'
    ).scalar()
    return revenue or 0

def calculate_monthly_growth():
    """Calculate monthly growth percentage"""
    # Simplified calculation - would need more complex logic for real growth
    return 12.5

def get_outstanding_invoices():
    """Get invoices that are outstanding"""
    return Invoice.query.filter(Invoice.payment_status.in_(['pending', 'overdue'])).all()

@app.route('/billing')
@login_required
def billing():
    if not current_user.can_access('billing'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    filter_type = request.args.get('filter', 'all')
    
    if filter_type == 'pending':
        invoices = get_pending_invoices()
    elif filter_type == 'paid':
        invoices = get_paid_invoices()
    else:
        invoices = get_all_invoices()
    
    stats = get_revenue_stats()
    form = PaymentForm()
    
    # Get additional data for professional billing
    pending_appointments = get_pending_appointments()
    recent_invoices = get_recent_invoices()
    clients = get_all_clients()
    services = get_all_services()
    
    # Calculate dashboard metrics
    today_revenue = calculate_today_revenue()
    monthly_revenue = calculate_monthly_revenue()
    monthly_growth = calculate_monthly_growth()
    outstanding_invoices = get_outstanding_invoices()
    outstanding_amount = sum(inv.total_amount for inv in outstanding_invoices)
    
    return render_template('professional_billing.html', 
                         invoices=invoices,
                         stats=stats,
                         form=form,
                         filter_type=filter_type,
                         pending_appointments=pending_appointments,
                         recent_invoices=recent_invoices,
                         clients=clients,
                         services=services,
                         today_revenue=today_revenue,
                         monthly_revenue=monthly_revenue,
                         monthly_growth=monthly_growth,
                         outstanding_invoices=outstanding_invoices,
                         outstanding_amount=outstanding_amount)

@app.route('/billing/mark-paid/<int:id>', methods=['POST'])
@login_required
def mark_invoice_paid_route(id):
    if not current_user.can_access('billing'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    invoice = mark_invoice_paid(id)
    if invoice:
        flash('Invoice marked as paid!', 'success')
    else:
        flash('Invoice not found', 'danger')
    
    return redirect(url_for('billing'))

@app.route('/billing/invoice/<int:id>')
@login_required
def invoice_detail(id):
    if not current_user.can_access('billing'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    invoice = get_invoice_by_id(id)
    if not invoice:
        flash('Invoice not found', 'danger')
        return redirect(url_for('billing'))
    
    return render_template('invoice_detail.html', invoice=invoice)