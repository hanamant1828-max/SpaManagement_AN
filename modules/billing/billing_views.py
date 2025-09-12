
"""
Billing Views Module
Main billing functionality for the spa management system
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import *
from datetime import datetime, timedelta
import logging

# Create billing blueprint
billing_bp = Blueprint('billing', __name__, url_prefix='/billing')

@app.route('/billing')
def billing():
    """Main billing dashboard"""
    try:
        # Get recent invoices and billing data
        recent_invoices = []
        pending_payments = []
        
        return render_template('billing.html',
                             recent_invoices=recent_invoices,
                             pending_payments=pending_payments)
    except Exception as e:
        logging.error(f"Error in billing dashboard: {e}")
        flash('Error loading billing dashboard', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/billing/invoices')
def billing_invoices():
    """View all invoices"""
    try:
        invoices = []
        return render_template('billing.html', invoices=invoices)
    except Exception as e:
        logging.error(f"Error loading invoices: {e}")
        flash('Error loading invoices', 'danger')
        return redirect(url_for('billing'))

@app.route('/billing/payments')
def billing_payments():
    """View all payments"""
    try:
        payments = []
        return render_template('billing.html', payments=payments)
    except Exception as e:
        logging.error(f"Error loading payments: {e}")
        flash('Error loading payments', 'danger')
        return redirect(url_for('billing'))

# Register the blueprint
app.register_blueprint(billing_bp)

print("Billing views loaded successfully")
