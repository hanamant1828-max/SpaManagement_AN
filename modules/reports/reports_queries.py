"""
Reports related database queries
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, extract
from app import db
# Late imports to avoid circular dependency
from modules.inventory.models import InventoryProduct as Inventory
from models import Customer, Appointment, Expense

def get_revenue_report(start_date, end_date):
    """Get revenue report for date range"""
    from models import Appointment
    revenue_data = db.session.query(
        func.date(Appointment.appointment_date).label('date'),
        func.sum(Appointment.amount).label('total_revenue'),
        func.count(Appointment.id).label('appointment_count')
    ).filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date,
        Appointment.is_paid == True
    ).group_by(func.date(Appointment.appointment_date)).all()
    
    return revenue_data

def get_expense_report(start_date, end_date):
    """Get expense report for date range"""
    from models import Expense
    expense_data = db.session.query(
        func.date(Expense.expense_date).label('date'),
        func.sum(Expense.amount).label('total_expenses'),
        func.count(Expense.id).label('expense_count')
    ).filter(
        Expense.expense_date >= start_date,
        Expense.expense_date <= end_date
    ).group_by(func.date(Expense.expense_date)).all()
    
    return expense_data

def get_staff_performance_report(start_date, end_date):
    """Get staff performance report"""
    from models import User, Appointment
    staff_data = db.session.query(
        User.id,
        User.first_name,
        User.last_name,
        func.count(Appointment.id).label('appointment_count'),
        func.sum(Appointment.amount).label('total_revenue')
    ).join(Appointment, User.id == Appointment.staff_id).filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date,
        Appointment.is_paid == True
    ).group_by(User.id).all()
    
    return staff_data

def get_client_report(start_date, end_date):
    """Get client report"""
    client_data = db.session.query(
        Customer.id,
        Customer.first_name,
        Customer.last_name,
        func.count(Appointment.id).label('appointment_count'),
        func.sum(Appointment.amount).label('total_spent')
    ).join(Appointment, Customer.id == Appointment.client_id).filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date,
        Appointment.is_paid == True
    ).group_by(Customer.id).all()
    
    return client_data

def get_inventory_report():
    """Get inventory report - batch-centric approach"""
    from modules.inventory.models import InventoryBatch
    
    inventory_data = Inventory.query.filter_by(is_active=True).all()
    
    low_stock = []
    expiring_soon = []
    total_value = 0
    
    for item in inventory_data:
        # Calculate total stock from active batches
        total_stock = sum(float(batch.qty_available or 0) for batch in item.batches if batch.status == 'active')
        
        # Check for low stock (threshold of 10)
        if total_stock <= 10 and total_stock > 0:
            low_stock.append(item)
        elif total_stock <= 0:
            low_stock.append(item)
        
        # Calculate total value from batches
        for batch in item.batches:
            if batch.status == 'active' and batch.qty_available and batch.unit_cost:
                total_value += float(batch.qty_available) * float(batch.unit_cost)
    
    # Get expiring batches (within 30 days)
    expiring_batches = InventoryBatch.query.filter(
        InventoryBatch.status == 'active',
        InventoryBatch.expiry_date.isnot(None),
        InventoryBatch.expiry_date <= date.today() + timedelta(days=30)
    ).all()
    
    # Get unique products from expiring batches
    expiring_product_ids = set(batch.product_id for batch in expiring_batches if batch.product_id)
    expiring_soon = [item for item in inventory_data if item.id in expiring_product_ids]
    
    return {
        'total_items': len(inventory_data),
        'low_stock_items': low_stock,
        'expiring_items': expiring_soon,
        'total_value': total_value,
        'expiring_batches': expiring_batches
    }