
"""
Billing Views Module - Redirects to Integrated Billing
All billing functionality is now handled by integrated_billing_views.py
"""

from flask import Blueprint, redirect, url_for
from app import app

# Create billing blueprint for backward compatibility
billing_bp = Blueprint('billing', __name__, url_prefix='/billing')

@app.route('/billing/invoices')
def billing_invoices():
    """Redirect to integrated billing invoices"""
    return redirect(url_for('list_integrated_invoices'))

@app.route('/billing/payments')
def billing_payments():
    """Redirect to integrated billing"""
    return redirect(url_for('integrated_billing'))

# Register the blueprint
app.register_blueprint(billing_bp)

print("Billing views redirecting to integrated billing system")
