"""
Dashboard views and routes
"""
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import app
from .dashboard_queries import get_dashboard_stats, get_recent_appointments, get_low_stock_items, get_expiring_items

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.can_access('dashboard'):
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    
    stats = get_dashboard_stats()
    recent_appointments = get_recent_appointments()
    low_stock_items = get_low_stock_items()
    expiring_items = get_expiring_items()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_appointments=recent_appointments,
                         low_stock_items=low_stock_items,
                         expiring_items=expiring_items)