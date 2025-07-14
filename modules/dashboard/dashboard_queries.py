"""
Dashboard-related database queries
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func
from app import db
from models import Appointment, Client, Inventory

def get_dashboard_stats():
    """Get dashboard statistics"""
    today = date.today()
    
    stats = {
        'todays_appointments': Appointment.query.filter(
            func.date(Appointment.appointment_date) == today
        ).count(),
        'total_clients': Client.query.filter_by(is_active=True).count(),
        'total_revenue_today': db.session.query(func.sum(Appointment.amount)).filter(
            func.date(Appointment.appointment_date) == today,
            Appointment.is_paid == True
        ).scalar() or 0,
        'total_revenue_month': db.session.query(func.sum(Appointment.amount)).filter(
            func.extract('month', Appointment.appointment_date) == today.month,
            func.extract('year', Appointment.appointment_date) == today.year,
            Appointment.is_paid == True
        ).scalar() or 0
    }
    
    return stats

def get_recent_appointments(limit=10):
    """Get recent appointments"""
    return Appointment.query.filter(
        Appointment.appointment_date >= datetime.now() - timedelta(days=7)
    ).order_by(Appointment.appointment_date.desc()).limit(limit).all()

def get_low_stock_items(limit=5):
    """Get low stock items"""
    return Inventory.query.filter(
        Inventory.current_stock <= Inventory.min_stock_level,
        Inventory.is_active == True
    ).limit(limit).all()

def get_expiring_items(limit=5):
    """Get items expiring soon"""
    today = date.today()
    return Inventory.query.filter(
        Inventory.expiry_date <= today + timedelta(days=30),
        Inventory.expiry_date > today,
        Inventory.is_active == True
    ).limit(limit).all()