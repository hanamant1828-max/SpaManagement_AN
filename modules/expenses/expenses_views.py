"""
Expenses views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from app import app
from forms import ExpenseForm
from .expenses_queries import (
    get_all_expenses, get_expenses_by_date_range, get_expenses_by_category,
    get_expense_by_id, get_expense_categories, create_expense, 
    update_expense, delete_expense, get_expense_stats
)

@app.route('/expenses')
@login_required
def expenses():
    if not current_user.can_access('expenses'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get filters from query params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category_id = request.args.get('category_id', type=int)
    
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            expenses_list = get_expenses_by_date_range(start_date, end_date)
        except ValueError:
            expenses_list = get_all_expenses()
    elif category_id:
        expenses_list = get_expenses_by_category(category_id)
    else:
        expenses_list = get_all_expenses()
    
    categories = get_expense_categories()
    stats = get_expense_stats()
    
    form = ExpenseForm()
    form.category_id.choices = [(c.id, c.display_name) for c in categories]
    
    # Add current month and year for template filters
    from datetime import datetime
    current_date = datetime.now()
    
    return render_template('expenses.html', 
                         expenses=expenses_list,
                         categories=categories,
                         stats=stats,
                         form=form,
                         current_month=current_date.month,
                         current_year=current_date.year)

@app.route('/expenses/create', methods=['POST'])
@login_required
def create_expense_route():
    if not current_user.can_access('expenses'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = ExpenseForm()
    categories = get_expense_categories()
    form.category_id.choices = [(c.id, c.display_name) for c in categories]
    
    if form.validate_on_submit():
        # Defensive coding for expense data with validation
        try:
            amount = float(form.amount.data or 0)
            if amount <= 0:
                flash('Expense amount must be greater than 0. Please enter a valid amount.', 'danger')
                return redirect(url_for('expenses'))
        except (ValueError, TypeError):
            flash('Invalid expense amount. Please enter a valid number.', 'danger')
            return redirect(url_for('expenses'))
        
        description = (form.description.data or '').strip()
        if not description:
            flash('Expense description is required. Please provide details about the expense.', 'danger')
            return redirect(url_for('expenses'))
        
        # Handle time field
        expense_time = None
        time_str = request.form.get('expense_time')
        if time_str:
            try:
                from datetime import time
                hour, minute = map(int, time_str.split(':'))
                expense_time = time(hour, minute)
            except (ValueError, AttributeError):
                expense_time = None

        expense_data = {
            'amount': amount,
            'description': description,
            'category_id': form.category_id.data if form.category_id.data else None,
            'category': request.form.get('category', 'general'),  # Fallback category
            'expense_date': form.expense_date.data or date.today(),
            'expense_time': expense_time,
            'payment_method': request.form.get('payment_method', 'cash'),
            'receipt_path': (form.receipt_path.data or '').strip(),
            'notes': (form.notes.data or '').strip(),
            'created_by': current_user.id
        }
        
        create_expense(expense_data)
        flash('Expense created successfully!', 'success')
    else:
        flash('Error creating expense. Please check your input.', 'danger')
    
    return redirect(url_for('expenses'))

@app.route('/expenses/update/<int:id>', methods=['POST'])
@login_required
def update_expense_route(id):
    if not current_user.can_access('expenses'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    expense = get_expense_by_id(id)
    if not expense:
        flash('Expense not found', 'danger')
        return redirect(url_for('expenses'))
    
    form = ExpenseForm()
    categories = get_expense_categories()
    form.category_id.choices = [(c.id, c.display_name) for c in categories]
    
    if form.validate_on_submit():
        expense_data = {
            'amount': form.amount.data,
            'description': form.description.data,
            'category_id': form.category_id.data,
            'expense_date': form.expense_date.data,
            'receipt_path': form.receipt_path.data or ''
        }
        
        update_expense(id, expense_data)
        flash('Expense updated successfully!', 'success')
    else:
        flash('Error updating expense. Please check your input.', 'danger')
    
    return redirect(url_for('expenses'))

@app.route('/expenses/delete/<int:id>', methods=['POST'])
@login_required
def delete_expense_route(id):
    if not current_user.can_access('expenses'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    if delete_expense(id):
        flash('Expense deleted successfully!', 'success')
    else:
        flash('Error deleting expense', 'danger')
    
    return redirect(url_for('expenses'))

@app.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    if not current_user.can_access('expenses'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = ExpenseForm()
    if form.validate_on_submit():
        expense_data = {
            'description': form.description.data,
            'amount': form.amount.data,
            'category': form.category.data,
            'expense_date': form.expense_date.data,
            'receipt_number': form.receipt_number.data,
            'notes': form.notes.data
        }
        
        expense = create_expense(expense_data)
        if expense:
            flash('Expense added successfully', 'success')
        else:
            flash('Failed to add expense', 'danger')
    
    return redirect(url_for('expenses'))