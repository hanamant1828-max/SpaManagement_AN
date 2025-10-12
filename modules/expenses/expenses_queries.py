"""
Expenses-related database queries
"""
from datetime import datetime, date
from sqlalchemy import func, and_
from app import db
from models import Expense, Category, PettyCashAccount, PettyCashTransaction

def get_all_expenses():
    """Get all expenses"""
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
    return Expense.query.get(expense_id)

def get_expense_categories():
    """Get all expense categories"""
    return Category.query.filter(
        Category.category_type == 'expense',
        Category.is_active == True
    ).order_by(Category.display_name).all()

def create_expense(expense_data):
    """Create a new expense with auto-approval logic"""
    from models import User
    
    amount = expense_data.get('amount', 0)
    
    # Auto-approval rules based on amount
    if amount < 500:
        expense_data['approval_status'] = 'auto_approved'
        expense_data['approved_at'] = datetime.utcnow()
        # Auto-deduct from petty cash for small amounts
        expense_data['deducted_from_account'] = False  # Will be handled separately
    else:
        expense_data['approval_status'] = 'pending'
    
    expense = Expense(**expense_data)
    db.session.add(expense)
    db.session.commit()
    
    # Auto-deduct if approved
    if expense.approval_status == 'auto_approved':
        try:
            deduct_expense_from_account(expense)
        except Exception as e:
            print(f"Auto-deduction failed: {e}")
    
    return expense

def approve_expense(expense_id, approver_id):
    """Approve an expense"""
    expense = Expense.query.get(expense_id)
    if not expense:
        return None
    
    expense.approval_status = 'approved'
    expense.approved_by = approver_id
    expense.approved_at = datetime.utcnow()
    db.session.commit()
    
    # Deduct from account after approval
    if not expense.deducted_from_account:
        try:
            deduct_expense_from_account(expense)
        except Exception as e:
            print(f"Deduction failed after approval: {e}")
    
    return expense

def reject_expense(expense_id, approver_id, reason):
    """Reject an expense"""
    expense = Expense.query.get(expense_id)
    if not expense:
        return None
    
    expense.approval_status = 'rejected'
    expense.approved_by = approver_id
    expense.approved_at = datetime.utcnow()
    expense.rejection_reason = reason
    db.session.commit()
    return expense

def get_pending_approvals(user_role=None, amount_range=None):
    """Get pending expenses for approval"""
    query = Expense.query.filter_by(approval_status='pending')
    
    # Filter by amount range based on user role
    if user_role == 'manager':
        query = query.filter(Expense.amount.between(500, 2000))
    elif user_role == 'admin':
        query = query.filter(Expense.amount > 2000)
    
    return query.order_by(Expense.expense_date.desc()).all()

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
def get_or_create_main_account():
    """Get or create the main petty cash account"""
    account = PettyCashAccount.query.filter_by(account_name='Main Account').first()
    if not account:
        account = PettyCashAccount(
            account_name='Main Account',
            current_balance=0.0,
            total_added=0.0,
            total_spent=0.0
        )
        db.session.add(account)
        db.session.commit()
    return account

def add_money_to_account(amount, description, user_id, notes=None):
    """Add money to petty cash account"""
    account = get_or_create_main_account()
    
    balance_before = account.current_balance
    balance_after = balance_before + amount
    
    # Create transaction record
    transaction = PettyCashTransaction(
        account_id=account.id,
        transaction_type='deposit',
        amount=amount,
        balance_before=balance_before,
        balance_after=balance_after,
        description=description,
        created_by=user_id,
        notes=notes
    )
    
    # Update account balance
    account.current_balance = balance_after
    account.total_added += amount
    
    db.session.add(transaction)
    db.session.commit()
    
    return transaction

def deduct_expense_from_account(expense):
    """Deduct expense amount from petty cash account"""
    if expense.deducted_from_account:
        return None  # Already deducted
    
    account = get_or_create_main_account()
    
    if account.current_balance < expense.amount:
        raise ValueError(f"Insufficient balance. Available: ₹{account.current_balance}, Required: ₹{expense.amount}")
    
    balance_before = account.current_balance
    balance_after = balance_before - expense.amount
    
    # Create transaction record
    transaction = PettyCashTransaction(
        account_id=account.id,
        transaction_type='expense',
        amount=expense.amount,
        balance_before=balance_before,
        balance_after=balance_after,
        description=expense.description,
        expense_id=expense.id,
        created_by=expense.created_by
    )
    
    # Update account balance
    account.current_balance = balance_after
    account.total_spent += expense.amount
    expense.deducted_from_account = True
    
    db.session.add(transaction)
    db.session.commit()
    
    return transaction

def get_account_balance():
    """Get current account balance"""
    account = get_or_create_main_account()
    return account.current_balance

def get_all_transactions():
    """Get all petty cash transactions"""
    return PettyCashTransaction.query.order_by(PettyCashTransaction.transaction_date.desc()).all()

def get_account_summary():
    """Get account summary"""
    account = get_or_create_main_account()
    return {
        'current_balance': account.current_balance,
        'total_added': account.total_added,
        'total_spent': account.total_spent,
        'account_name': account.account_name
    }



def create_daily_reconciliation(account_id, actual_counted, reconciled_by, notes=None):
    """Create daily reconciliation record"""
    from models import DailyReconciliation
    
    account = get_or_create_main_account()
    system_balance = account.current_balance
    difference = actual_counted - system_balance
    
    # Determine status
    if difference == 0:
        status = 'balanced'
    elif difference < 0:
        status = 'shortage'
    else:
        status = 'excess'
    
    reconciliation = DailyReconciliation(
        account_id=account_id,
        reconciliation_date=date.today(),
        system_balance=system_balance,
        actual_counted=actual_counted,
        difference=difference,
        status=status,
        reconciled_by=reconciled_by,
        notes=notes
    )
    
    db.session.add(reconciliation)
    db.session.commit()
    
    return reconciliation

def get_reconciliations(start_date=None, end_date=None):
    """Get reconciliation records"""
    from models import DailyReconciliation
    
    query = DailyReconciliation.query
    
    if start_date:
        query = query.filter(DailyReconciliation.reconciliation_date >= start_date)
    if end_date:
        query = query.filter(DailyReconciliation.reconciliation_date <= end_date)
    
    return query.order_by(DailyReconciliation.reconciliation_date.desc()).all()
