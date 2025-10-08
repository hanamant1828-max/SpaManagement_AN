
"""
Dashboard-related database queries
"""
from datetime import date, datetime, timedelta
from sqlalchemy import func
from app import db, get_ist_now, IST
from models import Appointment, Customer, User, Service
from modules.inventory.models import InventoryProduct

def get_dashboard_stats():
    """Get dashboard statistics with IST timezone"""
    try:
        from datetime import date, timedelta
        from sqlalchemy import func
        from models import Appointment, Customer, Service, User
        from app import db, get_ist_now, IST

        # Get current IST date (not UTC)
        ist_now = get_ist_now()
        today = ist_now.date()
        first_day_of_month = date(today.year, today.month, 1)

        print(f"DEBUG Dashboard Stats (IST):")
        print(f"  IST Now: {ist_now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"  Today (IST): {today}")
        print(f"  Month filter: {today.strftime('%Y-%m')}")

        # Today's appointments count
        todays_appointments = Appointment.query.filter(
            func.date(Appointment.appointment_date) == today
        ).count()

        # Total clients
        total_clients = Customer.query.filter_by(is_active=True).count()

        # Total services
        total_services = Service.query.filter_by(is_active=True).count()

        # Total active staff
        total_staff = User.query.filter_by(is_active=True, role='staff').count()

        # Today's revenue from Appointments
        todays_appointment_revenue = db.session.query(func.sum(Appointment.amount)).filter(
            func.date(Appointment.appointment_date) == today,
            Appointment.status == 'completed',
            Appointment.is_paid == True
        ).scalar() or 0.0

        # This month's revenue from Appointments
        monthly_appointment_revenue = db.session.query(func.sum(Appointment.amount)).filter(
            Appointment.appointment_date >= first_day_of_month,
            Appointment.status == 'completed',
            Appointment.is_paid == True
        ).scalar() or 0.0

        # Today's revenue from Invoice table (Legacy billing system)
        from models import Invoice
        todays_invoice_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
            func.date(Invoice.created_at) == today,
            Invoice.payment_status == 'paid'
        ).scalar() or 0.0

        # This month's revenue from Invoice table (Legacy billing system)
        monthly_invoice_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
            Invoice.created_at >= first_day_of_month,
            Invoice.payment_status == 'paid'
        ).scalar() or 0.0

        # Today's revenue from EnhancedInvoice table (Primary billing system)
        from models import EnhancedInvoice
        
        # Query using date extraction to handle IST datetimes properly
        todays_enhanced_invoice_revenue = db.session.query(func.sum(EnhancedInvoice.total_amount)).filter(
            func.date(EnhancedInvoice.invoice_date) == today,
            EnhancedInvoice.payment_status == 'paid'
        ).scalar() or 0.0

        # This month's revenue from EnhancedInvoice table (Primary billing system)
        monthly_enhanced_invoice_revenue = db.session.query(func.sum(EnhancedInvoice.total_amount)).filter(
            func.strftime('%Y-%m', EnhancedInvoice.invoice_date) == today.strftime('%Y-%m'),
            EnhancedInvoice.payment_status == 'paid'
        ).scalar() or 0.0

        # Combine all revenue sources
        total_revenue_today = float(todays_appointment_revenue) + float(todays_invoice_revenue) + float(todays_enhanced_invoice_revenue)
        total_revenue_month = float(monthly_appointment_revenue) + float(monthly_invoice_revenue) + float(monthly_enhanced_invoice_revenue)

        print(f"  Today's appointments: {todays_appointments}")
        print(f"  Total clients: {total_clients}")
        print(f"  Today's revenue: ₹{total_revenue_today}")
        print(f"    - From appointments: ₹{todays_appointment_revenue}")
        print(f"    - From invoices: ₹{todays_invoice_revenue}")
        print(f"    - From enhanced invoices: ₹{todays_enhanced_invoice_revenue}")
        print(f"  Month's revenue: ₹{total_revenue_month}")

        return {
            'todays_appointments': todays_appointments,
            'total_clients': total_clients,
            'total_services': total_services,
            'total_staff': total_staff,
            'total_revenue_today': total_revenue_today,
            'total_revenue_month': total_revenue_month
        }
    except Exception as e:
        print(f"Error in get_dashboard_stats: {e}")
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

def get_recent_appointments(limit=5):
    """Get recent appointments with IST timezone"""
    try:
        from app import get_ist_now
        
        ist_now = get_ist_now()
        today = ist_now.date()
        
        return Appointment.query.filter(
            func.date(Appointment.appointment_date) >= today
        ).order_by(Appointment.appointment_date.desc()).limit(limit).all()
    except Exception as e:
        print(f"Error in get_recent_appointments: {e}")
        return []

def get_low_stock_items(threshold=10):
    """Get low stock inventory items"""
    try:
        low_stock_items = []
        products = InventoryProduct.query.filter(InventoryProduct.is_active == True).all()
        
        for product in products:
            total_stock = sum(float(batch.qty_available or 0) 
                            for batch in product.batches 
                            if batch.status == 'active')
            
            if 0 < total_stock <= threshold:
                low_stock_items.append({
                    'product': product,
                    'current_stock': total_stock
                })
        
        return low_stock_items[:5]
    except Exception as e:
        print(f"Error in get_low_stock_items: {e}")
        return []

def get_expiring_items(days_threshold=30):
    """Get items expiring soon with IST timezone"""
    try:
        from modules.inventory.models import InventoryBatch
        from sqlalchemy.orm import joinedload
        from app import get_ist_now
        
        ist_now = get_ist_now()
        today = ist_now.date()
        expiry_threshold = today + timedelta(days=days_threshold)
        
        return InventoryBatch.query.options(
            joinedload(InventoryBatch.product),
            joinedload(InventoryBatch.location)
        ).filter(
            InventoryBatch.expiry_date <= expiry_threshold,
            InventoryBatch.expiry_date >= today,
            InventoryBatch.status == 'active',
            InventoryBatch.qty_available > 0
        ).order_by(InventoryBatch.expiry_date.asc()).limit(5).all()
    except Exception as e:
        print(f"Error in get_expiring_items: {e}")
        return []
