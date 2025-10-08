"""
Reports views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app import app, db
from models import Service, InvoiceItem, EnhancedInvoice
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
    
    try:
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
        
        # Get report data with error handling
        try:
            revenue_data = get_revenue_report(start_date, end_date)
        except Exception as e:
            print(f"Error getting revenue data: {e}")
            revenue_data = []
        
        try:
            expense_data = get_expense_report(start_date, end_date)
        except Exception as e:
            print(f"Error getting expense data: {e}")
            expense_data = []
        
        try:
            staff_data = get_staff_performance_report(start_date, end_date)
        except Exception as e:
            print(f"Error getting staff performance data: {e}")
            staff_data = []
        
        try:
            client_data = get_client_report(start_date, end_date)
        except Exception as e:
            print(f"Error getting client data: {e}")
            client_data = []
        
        try:
            inventory_data = get_inventory_report()
        except Exception as e:
            print(f"Error getting inventory data: {e}")
            inventory_data = {
                'total_items': 0,
                'low_stock_items': [],
                'expiring_items': [],
                'total_value': 0
            }
        
        # Add staff performance and service stats for template
        staff_performance = staff_data if staff_data else []
        
        # Get service statistics
        try:
            service_stats = db.session.query(
                Service.id,
                Service.name,
                func.count(InvoiceItem.id).label('bookings'),
                func.sum(InvoiceItem.final_amount).label('revenue')
            ).join(InvoiceItem, Service.id == InvoiceItem.item_id)\
            .join(EnhancedInvoice, InvoiceItem.invoice_id == EnhancedInvoice.id)\
            .filter(
                EnhancedInvoice.invoice_date >= start_date,
                EnhancedInvoice.invoice_date <= end_date,
                EnhancedInvoice.payment_status == 'paid',
                InvoiceItem.item_type == 'service'
            ).group_by(Service.id, Service.name)\
            .order_by(func.sum(InvoiceItem.final_amount).desc()).all()
        except Exception as e:
            print(f"Error getting service stats: {e}")
            service_stats = []
        
        return render_template('reports.html',
                             revenue_data=revenue_data,
                             expense_data=expense_data,
                             staff_data=staff_data,
                             staff_performance=staff_performance,
                             client_data=client_data,
                             inventory_data=inventory_data,
                             service_stats=service_stats,
                             start_date=start_date,
                             end_date=end_date)
    
    except Exception as e:
        print(f"Reports view error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading reports. Please try again.', 'danger')
        return redirect(url_for('dashboard'))

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