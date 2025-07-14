"""
Reports views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app import app
from .reports_queries import (
    get_revenue_report, get_expense_report, get_staff_performance_report,
    get_client_report, get_inventory_report
)

@app.route('/reports')
@login_required
def reports():
    if not current_user.can_access('reports'):
        flash('Access denied', 'danger')
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
            flash('Invalid date format', 'danger')
    
    # Get report data
    revenue_data = get_revenue_report(start_date, end_date)
    expense_data = get_expense_report(start_date, end_date)
    staff_data = get_staff_performance_report(start_date, end_date)
    client_data = get_client_report(start_date, end_date)
    inventory_data = get_inventory_report()
    
    return render_template('reports.html',
                         revenue_data=revenue_data,
                         expense_data=expense_data,
                         staff_data=staff_data,
                         client_data=client_data,
                         inventory_data=inventory_data,
                         start_date=start_date,
                         end_date=end_date)

@app.route('/reports/revenue')
@login_required
def revenue_report():
    if not current_user.can_access('reports'):
        return jsonify({'error': 'Access denied'}), 403
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    else:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
    
    revenue_data = get_revenue_report(start_date, end_date)
    
    return jsonify({
        'data': [
            {
                'date': item.date.strftime('%Y-%m-%d'),
                'revenue': float(item.total_revenue or 0),
                'appointments': item.appointment_count
            }
            for item in revenue_data
        ]
    })