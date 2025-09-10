"""
Dashboard-related database queries
"""
from datetime import date, datetime, timedelta
from sqlalchemy import func
from app import db
from models import Appointment, Customer, User, Service
from modules.inventory.models import InventoryProduct

def get_dashboard_stats():
    """Get dashboard statistics"""
    today = date.today()

    # Calculate today's revenue
    todays_revenue = db.session.query(func.sum(Appointment.amount)).filter(
        func.date(Appointment.appointment_date) == today,
        Appointment.status == 'completed',
        Appointment.is_paid == True
    ).scalar() or 0.0

    # Calculate monthly revenue
    month_start = today.replace(day=1)
    monthly_revenue = db.session.query(func.sum(Appointment.amount)).filter(
        Appointment.appointment_date >= month_start,
        Appointment.status == 'completed',
        Appointment.is_paid == True
    ).scalar() or 0.0

    stats = {
        'todays_appointments': Appointment.query.filter(
            func.date(Appointment.appointment_date) == today
        ).count() or 0,
        'total_clients': Customer.query.filter_by(is_active=True).count() or 0,
        'total_services': Service.query.filter_by(is_active=True).count() or 0,
        'total_staff': User.query.filter(User.role.in_(['staff', 'manager'])).count() or 0,
        'total_revenue_today': todays_revenue,
        'total_revenue_month': monthly_revenue
    }

    return stats

def get_recent_appointments(limit=10):
    """Get recent appointments"""
    return Appointment.query.filter(
        Appointment.appointment_date >= datetime.now() - timedelta(days=7)
    ).order_by(Appointment.appointment_date.desc()).limit(limit).all()

def get_low_stock_items(limit=5):
    """Get low stock items - BATCH-CENTRIC"""
    try:
        from modules.inventory.queries import get_low_stock_products
        products = get_low_stock_products()
        return products[:limit]  # Return only the first 'limit' items
    except Exception as e:
        print(f"Error getting low stock items: {e}")
        return []

def get_expiring_items(limit=5):
    """Get items expiring soon - BATCH-CENTRIC"""
    try:
        from modules.inventory.queries import get_expiring_batches
        batches = get_expiring_batches(days=30)
        return batches[:limit]  # Return only the first 'limit' items
    except Exception as e:
        print(f"Error getting expiring items: {e}")
        return []