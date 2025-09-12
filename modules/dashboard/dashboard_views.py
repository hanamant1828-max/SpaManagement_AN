"""
Dashboard views and routes
"""
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import app
from .dashboard_queries import get_dashboard_stats, get_recent_appointments, get_low_stock_items, get_expiring_items

@app.route('/dashboard')
  
def dashboard():
    try:
        stats = get_dashboard_stats()
        recent_appointments = get_recent_appointments()
        low_stock_items = get_low_stock_items()
        expiring_items = get_expiring_items()
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             recent_appointments=recent_appointments,
                             low_stock_items=low_stock_items,
                             expiring_items=expiring_items)
    except Exception as e:
        print(f"Dashboard error: {e}")
        flash('Error loading dashboard', 'danger')
        # Provide default stats structure to prevent template errors
        default_stats = {
            'todays_appointments': 0,
            'total_clients': 0,
            'total_services': 0,
            'total_staff': 0,
            'total_revenue_today': 0.0,
            'total_revenue_month': 0.0
        }
        return render_template('dashboard.html', 
                             stats=default_stats, 
                             recent_appointments=[],
                             low_stock_items=[],
                             expiring_items=[])