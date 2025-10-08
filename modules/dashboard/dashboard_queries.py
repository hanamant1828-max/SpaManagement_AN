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
    try:
        from datetime import date, timedelta
        from sqlalchemy import func
        from models import Appointment, Customer, Service, User
        from app import db

        today = date.today()
        first_day_of_month = date(today.year, today.month, 1)

        # Today's appointments count
        todays_appointments = Appointment.query.filter(
            func.date(Appointment.appointment_date) == today
        ).count()

        # Total clients
        total_clients = Customer.query.filter_by(is_active=True).count()

        # Total services
        total_services = Service.query.filter_by(is_active=True).count()

        # Total staff
        total_staff = User.query.filter_by(is_active=True, user_type='staff').count()

        # Today's revenue from Appointment table
        todays_appointment_revenue = db.session.query(func.sum(Appointment.amount)).filter(
            func.date(Appointment.appointment_date) == today,
            Appointment.status == 'completed',
            Appointment.is_paid == True
        ).scalar() or 0.0

        # Today's revenue from Invoice table
        from models import Invoice
        todays_invoice_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
            func.date(Invoice.invoice_date) == today,
            Invoice.payment_status == 'paid'
        ).scalar() or 0.0

        # Combine both revenue sources
        total_revenue_today = float(todays_appointment_revenue) + float(todays_invoice_revenue)

        # This month's revenue from Appointment table
        monthly_appointment_revenue = db.session.query(func.sum(Appointment.amount)).filter(
            Appointment.appointment_date >= first_day_of_month,
            Appointment.status == 'completed',
            Appointment.is_paid == True
        ).scalar() or 0.0

        # This month's revenue from Invoice table
        monthly_invoice_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
            Invoice.invoice_date >= first_day_of_month,
            Invoice.payment_status == 'paid'
        ).scalar() or 0.0

        # Combine both revenue sources
        total_revenue_month = float(monthly_appointment_revenue) + float(monthly_invoice_revenue)

        print(f"DEBUG Dashboard Stats:")
        print(f"  Today's appointments: {todays_appointments}")
        print(f"  Total clients: {total_clients}")
        print(f"  Today's revenue: ₹{total_revenue_today}")
        print(f"  Monthly revenue: ₹{total_revenue_month}")

        return {
            'todays_appointments': todays_appointments,
            'total_clients': total_clients,
            'total_services': total_services,
            'total_staff': total_staff,
            'total_revenue_today': float(total_revenue_today),
            'total_revenue_month': float(total_revenue_month)
        }
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        import traceback
        traceback.print_exc()
        return {
            'todays_appointments': 0,
            'total_clients': 0,
            'total_services': 0,
            'total_staff': 0,
            'total_revenue_today': 0.0,
            'total_revenue_month': 0.0
        }

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