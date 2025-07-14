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
    
    return render_template('billing.html', 
                         invoices=invoices,
                         stats=stats,
                         form=form,
                         filter_type=filter_type)

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