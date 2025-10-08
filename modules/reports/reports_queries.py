
"""
Reports related database queries
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, extract
from app import db
from models import UnakiBooking, EnhancedInvoice, InvoiceItem, Expense, Customer, User, Service
from modules.inventory.models import InventoryProduct as Inventory

def get_revenue_report(start_date, end_date):
    """Get revenue report for date range from invoices"""
    try:
        revenue_data = db.session.query(
            func.date(EnhancedInvoice.invoice_date).label('date'),
            func.sum(EnhancedInvoice.total_amount).label('total'),
            func.count(EnhancedInvoice.id).label('appointment_count')
        ).filter(
            EnhancedInvoice.invoice_date >= start_date,
            EnhancedInvoice.invoice_date <= end_date,
            EnhancedInvoice.payment_status == 'paid'
        ).group_by(func.date(EnhancedInvoice.invoice_date)).all()
        
        return revenue_data if revenue_data else []
    except Exception as e:
        print(f"Error in get_revenue_report: {e}")
        return []

def get_expense_report(start_date, end_date):
    """Get expense report for date range"""
    try:
        expense_data = db.session.query(
            func.date(Expense.expense_date).label('date'),
            func.sum(Expense.amount).label('total_expenses'),
            func.count(Expense.id).label('expense_count')
        ).filter(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        ).group_by(func.date(Expense.expense_date)).all()
        
        return expense_data if expense_data else []
    except Exception as e:
        print(f"Error in get_expense_report: {e}")
        return []

def get_staff_performance_report(start_date, end_date):
    """Get staff performance report from invoice items"""
    try:
        staff_data = db.session.query(
            User.id,
            User.first_name,
            User.last_name,
            func.count(InvoiceItem.id).label('appointments'),
            func.sum(InvoiceItem.staff_revenue_price).label('revenue')
        ).join(InvoiceItem, User.id == InvoiceItem.staff_id)\
        .join(EnhancedInvoice, InvoiceItem.invoice_id == EnhancedInvoice.id)\
        .filter(
            EnhancedInvoice.invoice_date >= start_date,
            EnhancedInvoice.invoice_date <= end_date,
            EnhancedInvoice.payment_status == 'paid',
            InvoiceItem.staff_id.isnot(None)
        ).group_by(User.id, User.first_name, User.last_name).all()
        
        return staff_data if staff_data else []
    except Exception as e:
        print(f"Error in get_staff_performance_report: {e}")
        return []

def get_client_report(start_date, end_date):
    """Get client report from invoices"""
    try:
        client_data = db.session.query(
            Customer.id,
            Customer.first_name,
            Customer.last_name,
            func.count(EnhancedInvoice.id).label('bookings'),
            func.sum(EnhancedInvoice.total_amount).label('revenue')
        ).join(EnhancedInvoice, Customer.id == EnhancedInvoice.client_id)\
        .filter(
            EnhancedInvoice.invoice_date >= start_date,
            EnhancedInvoice.invoice_date <= end_date,
            EnhancedInvoice.payment_status == 'paid'
        ).group_by(Customer.id, Customer.first_name, Customer.last_name).all()
        
        return client_data if client_data else []
    except Exception as e:
        print(f"Error in get_client_report: {e}")
        return []

def get_inventory_report():
    """Get inventory report"""
    try:
        inventory_data = Inventory.query.filter_by(is_active=True).all()
        
        low_stock = []
        expiring_soon = []
        total_value = 0
        
        for item in inventory_data:
            # Check low stock
            qty = getattr(item, 'quantity_in_stock', 0) or 0
            min_level = getattr(item, 'min_stock_level', 0) or 0
            if qty <= min_level and min_level > 0:
                low_stock.append(item)
            
            # Check expiring
            if hasattr(item, 'expiry_date') and item.expiry_date:
                if item.expiry_date <= date.today() + timedelta(days=30):
                    expiring_soon.append(item)
            
            # Calculate value
            try:
                current_stock = getattr(item, 'current_stock', 0) or 0
                cost_price = getattr(item, 'cost_price', 0) or 0
                total_value += current_stock * cost_price
            except:
                pass
        
        return {
            'total_items': len(inventory_data),
            'low_stock_items': low_stock,
            'expiring_items': expiring_soon,
            'total_value': total_value
        }
    except Exception as e:
        print(f"Error in get_inventory_report: {e}")
        return {
            'total_items': 0,
            'low_stock_items': [],
            'expiring_items': [],
            'total_value': 0
        }
