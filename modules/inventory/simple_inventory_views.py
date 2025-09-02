"""
Simple Inventory Management System Views
"""

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import app

@app.route('/simple_inventory')
@login_required
def simple_inventory():
    """Placeholder for new inventory implementation"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    flash('Inventory system is being rebuilt. Please implement your fresh plan!', 'info')
    return redirect(url_for('dashboard'))