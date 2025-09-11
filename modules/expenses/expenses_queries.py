"""
Expenses-related database queries
"""
from datetime import datetime, date
from sqlalchemy import func, and_
from app import db
# Late imports to avoid circular dependency

def get_all_expenses():
    """Get all expenses"""
    from models import Expense
    return Expense.query.order_by(Expense.expense_date.desc()).all()

def get_expenses_by_date_range(start_date, end_date):
    """Get expenses within date range"""
    return Expense.query.filter(
        Expense.expense_date >= start_date,
        Expense.expense_date <= end_date
    ).order_by(Expense.expense_date.desc()).all()

def get_expenses_by_category(category_id):
    """Get expenses by category"""
    return Expense.query.filter_by(category_id=category_id).order_by(Expense.expense_date.desc()).all()

def get_expense_by_id(expense_id):
    """Get expense by ID"""
    from models import Expense
    return Expense.query.get(expense_id)

def get_expense_categories():
    """Get all expense categories"""
    from models import Category
    return Category.query.filter(
        Category.category_type == 'expense',
        Category.is_active == True
    ).order_by(Category.display_name).all()

def create_expense(expense_data):
    """Create a new expense"""
    from models import Expense
    expense = Expense(**expense_data)
    db.session.add(expense)
    db.session.commit()
    return expense

def update_expense(expense_id, expense_data):
    """Update an existing expense"""
    expense = Expense.query.get(expense_id)
    if expense:
        for key, value in expense_data.items():
            setattr(expense, key, value)
        db.session.commit()
    return expense

def delete_expense(expense_id):
    """Delete an expense"""
    expense = Expense.query.get(expense_id)
    if expense:
        db.session.delete(expense)
        db.session.commit()
        return True
    return False

def get_expense_stats():
    """Get expense statistics"""
    today = date.today()
    
    stats = {
        'total_expenses': db.session.query(func.sum(Expense.amount)).scalar() or 0,
        'monthly_expenses': db.session.query(func.sum(Expense.amount)).filter(
            func.extract('month', Expense.expense_date) == today.month,
            func.extract('year', Expense.expense_date) == today.year
        ).scalar() or 0,
        'expense_count': Expense.query.count(),
        'avg_expense': db.session.query(func.avg(Expense.amount)).scalar() or 0
    }
    
    return stats