"""
Inventory Reports Views and Routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app import app
from .inventory_reports_queries import (
    get_stock_summary_report, get_stock_level_report, get_expiry_report,
    get_location_wise_report, get_consumption_report, get_adjustment_report,
    get_category_wise_report, get_low_stock_report, get_batch_movement_report
)
from models import Product # Added import for Product model
from sqlalchemy import func # Added import for SQLAlchemy functions
from app import db # Added import for db session

@app.route('/inventory/reports', methods=['GET', 'POST'])
@login_required
def inventory_reports():
    """Main inventory reports dashboard"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get quick stats for display
    total_products = Product.query.count()
    low_stock_count = Product.query.filter(Product.current_stock <= Product.min_stock_level).count()

    # Count expiring products (within 30 days)
    thirty_days_from_now = datetime.utcnow() + timedelta(days=30)
    expiring_count = Product.query.filter(
        Product.expiry_date.isnot(None),
        Product.expiry_date <= thirty_days_from_now
    ).count()

    # Calculate total stock value
    total_stock_value = db.session.query(
        func.sum(Product.current_stock * Product.unit_price)
    ).scalar() or 0

    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format', 'danger')

        summary = get_stock_summary_report()
        stock_levels = get_stock_level_report()
        expiring_items = get_expiry_report(days_threshold=30)
        low_stock_items = get_low_stock_report(threshold=10)
        location_summary = get_location_wise_report()
        category_summary = get_category_wise_report()
        consumption_data = get_consumption_report(start_date, end_date)
        adjustment_data = get_adjustment_report(start_date, end_date)

        return render_template('inventory_reports.html',
                             summary=summary,
                             stock_levels=stock_levels,
                             expiring_items=expiring_items,
                             low_stock_items=low_stock_items,
                             location_summary=location_summary,
                             category_summary=category_summary,
                             consumption_data=consumption_data,
                             adjustment_data=adjustment_data,
                             start_date=start_date,
                             end_date=end_date,
                             total_products=total_products,
                             low_stock_count=low_stock_count,
                             expiring_count=expiring_count,
                             total_stock_value=round(total_stock_value, 2))

    except Exception as e:
        print(f"Inventory reports error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading inventory reports. Please try again.', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/api/inventory/reports/stock-levels')
@login_required
def api_stock_levels_report():
    """API endpoint for stock levels report"""
    try:
        stock_data = get_stock_level_report()
        return jsonify({'success': True, 'data': stock_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/inventory/reports/expiry')
@login_required
def api_expiry_report():
    """API endpoint for expiry report"""
    try:
        days = request.args.get('days', 30, type=int)
        expiry_data = get_expiry_report(days_threshold=days)
        return jsonify({'success': True, 'data': expiry_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/inventory/reports/low-stock')
@login_required
def api_low_stock_report():
    """API endpoint for low stock report"""
    try:
        threshold = request.args.get('threshold', 10, type=int)
        low_stock_data = get_low_stock_report(threshold=threshold)
        return jsonify({'success': True, 'data': low_stock_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/inventory/reports/consumption')
@login_required
def api_consumption_report():
    """API endpoint for consumption report"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)

        consumption_data = get_consumption_report(start_date, end_date)
        return jsonify({'success': True, 'data': consumption_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/inventory/reports/batch-movement')
@login_required
def api_batch_movement_report():
    """API endpoint for batch movement report"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)

        movement_data = get_batch_movement_report(start_date, end_date)
        return jsonify({'success': True, 'data': movement_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

print("✅ Inventory reports views imported")