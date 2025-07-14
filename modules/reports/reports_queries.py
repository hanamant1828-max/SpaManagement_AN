"""
Reports related database queries
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, extract
from app import db
from models import Appointment, Invoice, Expense, Client, User, Inventory

def get_revenue_report(start_date, end_date):
    """Get revenue report for date range"""
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
        Client.id,
        Client.first_name,
        Client.last_name,
        func.count(Appointment.id).label('appointment_count'),
        func.sum(Appointment.amount).label('total_spent')
    ).join(Appointment, Client.id == Appointment.client_id).filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date,
        Appointment.is_paid == True
    ).group_by(Client.id).all()
    
    return client_data

def get_inventory_report():
    """Get inventory report"""
    inventory_data = Inventory.query.filter_by(is_active=True).all()
    
    low_stock = [item for item in inventory_data if item.current_stock <= item.min_stock_level]
    expiring_soon = [item for item in inventory_data if item.expiry_date and item.expiry_date <= date.today() + timedelta(days=30)]
    
    return {
        'total_items': len(inventory_data),
        'low_stock_items': low_stock,
        'expiring_items': expiring_soon,
        'total_value': sum(item.current_stock * item.cost_price for item in inventory_data)
    }