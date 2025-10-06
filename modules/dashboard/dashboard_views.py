"""
Dashboard views and routes
"""
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import app, get_ist_now
from .dashboard_queries import get_dashboard_stats, get_recent_appointments, get_low_stock_items, get_expiring_items

@app.route('/dashboard')

def dashboard():
    try:
        # Get current IST time
        ist_now = get_ist_now()
        
        stats = get_dashboard_stats()
        recent_appointments = get_recent_appointments()
        low_stock_items = get_low_stock_items()
        expiring_items = get_expiring_items()

        return render_template('dashboard.html', 
                             stats=stats, 
                             recent_appointments=recent_appointments,
                             low_stock_items=low_stock_items,
                             expiring_items=expiring_items,
                             current_date=ist_now.strftime('%A, %B %d, %Y'),
                             current_time=ist_now.strftime('%I:%M %p IST'))
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

@app.route('/alerts')
def alerts():
    """Product alerts and notifications page"""
    try:
        # Get inventory alerts
        from modules.inventory.models import InventoryBatch, InventoryProduct
        from sqlalchemy.orm import joinedload
        from datetime import date, timedelta

        today = date.today()

        # Get expired batches
        expired_batches = InventoryBatch.query.options(
            joinedload(InventoryBatch.product),
            joinedload(InventoryBatch.location)
        ).filter(
            InventoryBatch.expiry_date < today,
            InventoryBatch.status == 'active',
            InventoryBatch.qty_available > 0
        ).order_by(InventoryBatch.expiry_date.desc()).all()

        # Get items expiring within 2 months (60 days)
        expiry_threshold = today + timedelta(days=60)
        expiring_soon = InventoryBatch.query.options(
            joinedload(InventoryBatch.product),
            joinedload(InventoryBatch.location)
        ).filter(
            InventoryBatch.expiry_date <= expiry_threshold,
            InventoryBatch.expiry_date >= today,
            InventoryBatch.status == 'active',
            InventoryBatch.qty_available > 0
        ).order_by(InventoryBatch.expiry_date.asc()).all()

        # Get low stock items (product-wise)
        low_stock_items = []
        products = InventoryProduct.query.filter(InventoryProduct.is_active == True).all()
        for product in products:
            total_stock = sum(float(batch.qty_available or 0) for batch in product.batches if batch.status == 'active')
            if total_stock <= 10 and total_stock > 0:  # Low stock threshold
                low_stock_items.append({
                    'product': product,
                    'current_stock': total_stock
                })

        return render_template('alerts.html', 
                             expired_items=expired_batches,
                             expiring_soon=expiring_soon,
                             low_stock_items=low_stock_items)
    except Exception as e:
        print(f"Alerts error: {e}")
        flash('Error loading alerts', 'danger')
        return redirect(url_for('dashboard'))