"""
Simple Inventory Management System Views
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app import app, db
from models import SimpleInventoryItem, SimpleStockTransaction, SimpleLowStockAlert, TransactionType

@app.route('/simple_inventory')
@login_required
def simple_inventory():
    """Simple inventory management interface"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get filter parameters
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '')

    # Build query
    query = SimpleInventoryItem.query

    if category_filter:
        query = query.filter(SimpleInventoryItem.category == category_filter)

    if status_filter:
        if status_filter == 'low_stock':
            query = query.filter(SimpleInventoryItem.current_stock <= SimpleInventoryItem.minimum_stock)
        elif status_filter == 'out_of_stock':
            query = query.filter(SimpleInventoryItem.current_stock <= 0)
        elif status_filter == 'normal':
            query = query.filter(SimpleInventoryItem.current_stock > SimpleInventoryItem.minimum_stock)

    if search_query:
        query = query.filter(
            db.or_(
                SimpleInventoryItem.name.contains(search_query),
                SimpleInventoryItem.sku.contains(search_query),
                SimpleInventoryItem.description.contains(search_query)
            )
        )

    items = query.filter_by(is_active=True).order_by(SimpleInventoryItem.name).all()

    # Get unique categories for filter dropdown
    categories = db.session.query(SimpleInventoryItem.category).distinct().filter(
        SimpleInventoryItem.category.isnot(None),
        SimpleInventoryItem.is_active == True
    ).all()
    categories = [cat[0] for cat in categories if cat[0]]

    # Get all transaction types from database
    from models import TransactionType
    transaction_types_db = TransactionType.query.filter_by(is_active=True).all()

    # Convert to list format for backward compatibility
    transaction_types = [{'name': tt.name, 'display_name': tt.display_name} for tt in transaction_types_db]

    # Fallback if no transaction types exist
    if not transaction_types:
        transaction_types = [{'name': 'treatment', 'display_name': 'Treatment (Facial/Service)'}]

    # Calculate statistics for template (keep all old functionality)
    total_items = len(items)
    low_stock_count = sum(1 for item in items if item.current_stock <= item.minimum_stock)
    total_stock_value = sum(item.current_stock * item.unit_cost for item in items)

    # Get today's transactions
    today = datetime.now().date()
    todays_transactions = SimpleStockTransaction.query.filter(
        db.func.date(SimpleStockTransaction.date_time) == today
    ).count()

    # Get recent transactions for the consumption tab
    transactions = SimpleStockTransaction.query.order_by(
        SimpleStockTransaction.date_time.desc()
    ).limit(50).all()

    # Additional statistics needed by template
    total_transactions = SimpleStockTransaction.query.count()
    week_ago = datetime.now() - timedelta(days=7)
    weekly_transactions = SimpleStockTransaction.query.filter(
        SimpleStockTransaction.date_time >= week_ago
    ).count()

    items_consumed_today = SimpleStockTransaction.query.filter(
        db.func.date(SimpleStockTransaction.date_time) == today,
        SimpleStockTransaction.quantity_change < 0
    ).count()

    month_ago = datetime.now() - timedelta(days=30)
    monthly_consumption = SimpleStockTransaction.query.filter(
        SimpleStockTransaction.date_time >= month_ago,
        SimpleStockTransaction.quantity_change < 0
    ).count()
    avg_daily_usage = round(monthly_consumption / 30, 1) if monthly_consumption > 0 else 0

    return render_template('simple_inventory.html', 
                         items=items, 
                         categories=categories,
                         transaction_types=transaction_types,
                         transaction_types_db=transaction_types_db,
                         category_filter=category_filter,
                         status_filter=status_filter,
                         search_query=search_query,
                         total_items=total_items,
                         low_stock_count=low_stock_count,
                         total_stock_value=total_stock_value,
                         todays_transactions=todays_transactions,
                         transactions=transactions,
                         total_transactions=total_transactions,
                         weekly_transactions=weekly_transactions,
                         items_consumed_today=items_consumed_today,
                         avg_daily_usage=avg_daily_usage)

@app.route('/add_inventory_item', methods=['POST'])
@login_required
def add_inventory_item():
    """Add new inventory item"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('simple_inventory'))

    try:
        # Generate SKU if not provided
        sku = request.form.get('sku') or f"AUTO-{int(datetime.now().timestamp())}"
        name = request.form.get('name').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        initial_stock = float(request.form.get('initial_stock', 0))
        minimum_stock = float(request.form.get('minimum_stock', 0))
        unit_cost = float(request.form.get('unit_cost', 0))
        supplier = request.form.get('supplier', '').strip()
        location = request.form.get('location', '').strip()
        expiry_date = request.form.get('expiry_date')

        # Validate required fields
        if not name:
            flash('Item name is required', 'warning')
            return redirect(url_for('simple_inventory'))

        # Check if SKU already exists
        existing_item = SimpleInventoryItem.query.filter_by(sku=sku).first()
        if existing_item:
            flash('SKU already exists. Please use a different SKU.', 'warning')
            return redirect(url_for('simple_inventory'))

        # Parse expiry date
        expiry_date_obj = None
        if expiry_date:
            try:
                expiry_date_obj = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid expiry date format', 'warning')
                return redirect(url_for('simple_inventory'))

        # Create new item
        new_item = SimpleInventoryItem(
            sku=sku,
            name=name,
            description=description,
            category=category,
            current_stock=initial_stock,
            minimum_stock=minimum_stock,
            unit_cost=unit_cost,
            supplier=supplier,
            location=location,
            expiry_date=expiry_date_obj
        )

        db.session.add(new_item)
        db.session.flush()  # Get the item ID

        # Create initial stock transaction if initial stock > 0
        if initial_stock > 0:
            transaction = SimpleStockTransaction(
                item_id=new_item.id,
                transaction_type='Purchase',
                quantity_change=initial_stock,
                new_stock_level=initial_stock,
                user_id=current_user.id,
                reason='Initial stock entry',
                reference_number=f'INIT-{new_item.id}'
            )
            db.session.add(transaction)

        db.session.commit()
        flash(f'Item "{name}" added successfully!', 'success')

    except ValueError as e:
        flash(f'Invalid input: {str(e)}', 'danger')
        db.session.rollback()
    except Exception as e:
        flash(f'Error adding item: {str(e)}', 'danger')
        db.session.rollback()

    return redirect(url_for('simple_inventory'))

@app.route('/edit_inventory_item', methods=['POST'])
@login_required
def edit_inventory_item():
    """Edit existing inventory item"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('simple_inventory'))

    try:
        item_id = int(request.form.get('item_id'))
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        minimum_stock = float(request.form.get('minimum_stock', 0))
        unit_cost = float(request.form.get('unit_cost', 0))
        supplier = request.form.get('supplier', '').strip()
        location = request.form.get('location', '').strip()
        expiry_date = request.form.get('expiry_date')

        item = SimpleInventoryItem.query.get(item_id)
        if not item:
            flash('Item not found', 'danger')
            return redirect(url_for('simple_inventory'))

        if not name:
            flash('Item name is required', 'warning')
            return redirect(url_for('simple_inventory'))

        # Parse expiry date
        expiry_date_obj = None
        if expiry_date:
            try:
                expiry_date_obj = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid expiry date format', 'warning')
                return redirect(url_for('simple_inventory'))

        # Update item
        item.name = name
        item.description = description
        item.category = category
        item.minimum_stock = minimum_stock
        item.unit_cost = unit_cost
        item.supplier = supplier
        item.location = location
        item.expiry_date = expiry_date_obj

        db.session.commit()
        flash(f'Item "{name}" updated successfully!', 'success')

    except ValueError:
        flash('Invalid item ID or input', 'danger')
    except Exception as e:
        flash(f'Error updating item: {str(e)}', 'danger')
        db.session.rollback()

    return redirect(url_for('simple_inventory'))

@app.route('/update_stock', methods=['POST'])
@login_required
def update_stock():
    """Update stock levels for an item"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('simple_inventory'))

    try:
        item_id = int(request.form.get('item_id'))
        transaction_type = request.form.get('transaction_type')
        quantity_change = float(request.form.get('quantity_change'))
        reason = request.form.get('reason', '').strip()
        reference_number = request.form.get('reference_number', '').strip()

        item = SimpleInventoryItem.query.get(item_id)
        if not item:
            flash('Item not found', 'danger')
            return redirect(url_for('simple_inventory'))

        if quantity_change == 0:
            flash('Quantity change cannot be zero', 'warning')
            return redirect(url_for('simple_inventory'))

        # Determine the actual quantity change based on transaction type
        if transaction_type in ['Sale', 'Transfer', 'Adjustment']:
            quantity_change = -abs(quantity_change)  # Ensure negative for removals
        elif transaction_type in ['Purchase', 'Return']:
            quantity_change = abs(quantity_change)  # Ensure positive for additions

        # Calculate new stock level
        new_stock = item.current_stock + quantity_change

        # Check for negative stock
        if new_stock < 0:
            flash(f'Insufficient stock. Current stock: {item.current_stock}', 'danger')
            return redirect(url_for('simple_inventory'))

        # Update item stock
        item.current_stock = new_stock

        # Create transaction record
        transaction = SimpleStockTransaction(
            item_id=item_id,
            transaction_type=transaction_type,
            quantity_change=quantity_change,
            new_stock_level=new_stock,
            user_id=current_user.id,
            reason=reason or f'{transaction_type} transaction',
            reference_number=reference_number
        )
        db.session.add(transaction)

        # Check for low stock alert
        if new_stock <= item.minimum_stock:
            # Check if there's already an active alert for this item
            existing_alert = SimpleLowStockAlert.query.filter_by(
                item_id=item_id,
                is_acknowledged=False
            ).first()

            if not existing_alert:
                alert = SimpleLowStockAlert(
                    item_id=item_id,
                    current_stock=new_stock,
                    minimum_stock=item.minimum_stock
                )
                db.session.add(alert)

        db.session.commit()

        status = 'added to' if quantity_change > 0 else 'removed from'
        flash(f'{abs(quantity_change)} units {status} {item.name}. New stock: {new_stock}', 'success')

    except ValueError:
        flash('Invalid input values', 'danger')
    except Exception as e:
        flash(f'Error updating stock: {str(e)}', 'danger')
        db.session.rollback()

    return redirect(url_for('simple_inventory'))

@app.route('/record_transaction', methods=['POST'])
@login_required
def record_transaction():
    """Record a transaction (consumption/usage)"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('simple_inventory'))

    try:
        item_id = int(request.form.get('item_id'))
        transaction_type = request.form.get('transaction_type')
        quantity = float(request.form.get('quantity'))
        reason = request.form.get('reason', '').strip()
        reference_number = request.form.get('reference_number', '').strip()

        item = SimpleInventoryItem.query.get(item_id)
        if not item:
            flash('Item not found', 'danger')
            return redirect(url_for('simple_inventory'))

        if quantity <= 0:
            flash('Quantity must be greater than zero', 'warning')
            return redirect(url_for('simple_inventory'))

        # For consumption tracking, quantity is always negative
        if transaction_type == 'Treatment':
            quantity_change = -quantity
        else:
            # For other types, keep as is
            quantity_change = quantity

        # Calculate new stock level
        new_stock = item.current_stock + quantity_change

        # Check for negative stock (but allow negative for tracking)
        if new_stock < 0:
            flash('⚠️ Warning: This will result in negative stock. Current: {item.current_stock}, Requested: {quantity}', 'warning')

        # Update item stock
        item.current_stock = new_stock

        # Create transaction record
        transaction = SimpleStockTransaction(
            item_id=item_id,
            transaction_type=transaction_type,
            quantity_change=quantity_change,
            new_stock_level=new_stock,
            user_id=current_user.id,
            reason=reason or f'{transaction_type} - used {quantity} units',
            reference_number=reference_number
        )
        db.session.add(transaction)

        db.session.commit()

        flash(f'{quantity} units of {item.name} recorded for {transaction_type}. New stock: {new_stock}', 'success')

    except ValueError:
        flash('Invalid input values', 'danger')
    except Exception as e:
        flash(f'Error recording transaction: {str(e)}', 'danger')
        db.session.rollback()

    return redirect(url_for('simple_inventory'))

@app.route('/get_inventory_item/<int:item_id>')
@login_required
def get_inventory_item(item_id):
    """Get inventory item details for editing"""
    if not current_user.can_access('inventory'):
        return jsonify({'success': False, 'message': 'Access denied'})

    try:
        item = SimpleInventoryItem.query.get(item_id)
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'})

        item_data = {
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'category': item.category,
            'current_stock': item.current_stock,
            'minimum_stock': item.minimum_stock,
            'unit_cost': item.unit_cost,
            'supplier': item.supplier,
            'location': item.location,
            'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None,
            'sku': item.sku
        }

        return jsonify({'success': True, 'item': item_data})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete_inventory_item/<int:item_id>', methods=['POST'])
@login_required
def delete_inventory_item(item_id):
    """Delete an inventory item"""
    if not current_user.can_access('inventory'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    try:
        item = SimpleInventoryItem.query.get(item_id)
        if not item:
            return jsonify({'success': False, 'error': 'Item not found'}), 404

        # Check if item has transactions
        transactions_count = SimpleStockTransaction.query.filter_by(item_id=item_id).count()
        if transactions_count > 0:
            return jsonify({
                'success': False,
                'error': f'Cannot delete "{item.name}" - it has {transactions_count} transaction(s). Consider marking as inactive instead.'
            }), 400

        # Check if item has low stock alerts
        alerts_count = SimpleLowStockAlert.query.filter_by(item_id=item_id).count()
        if alerts_count > 0:
            # Delete associated alerts first
            SimpleLowStockAlert.query.filter_by(item_id=item_id).delete()

        item_name = item.name
        item_sku = item.sku

        # Soft delete by marking as inactive instead of hard delete
        item.is_active = False
        item.name = f"[DELETED] {item.name}"
        item.sku = f"DEL_{item.sku}"

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Item "{item_name}" deleted successfully'
        })

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting inventory item {item_id}: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Database error occurred while deleting item: {str(e)}'
        }), 500

@app.route('/record_bulk_transaction', methods=['POST'])
@login_required
def record_bulk_transaction():
    """Record bulk transaction for multiple items (e.g., facial treatment)"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('simple_inventory'))

    try:
        # Get form data
        treatment_type = request.form.get('treatment_type', '').strip()
        client_name = request.form.get('client_name', '').strip()
        treatment_notes = request.form.get('treatment_notes', '').strip()

        # Get arrays of item data
        item_ids = request.form.getlist('item_id[]')
        quantities = request.form.getlist('quantity[]')
        item_notes = request.form.getlist('item_notes[]')

        if not treatment_type:
            flash('Treatment type is required', 'warning')
            return redirect(url_for('simple_inventory'))

        if not item_ids or not quantities:
            flash('At least one item must be selected', 'warning')
            return redirect(url_for('simple_inventory'))

        # Build reason string
        reason = f'{treatment_type} treatment'
        if client_name:
            reason += f' for {client_name}'
        if treatment_notes:
            reason += f' - {treatment_notes}'

        # Generate reference number for this bulk transaction
        reference_number = f'BULK-{int(datetime.now().timestamp())}'

        processed_items = []
        insufficient_stock_items = []

        # Process each item
        for i, item_id in enumerate(item_ids):
            if not item_id or not quantities[i]:
                continue

            item_id = int(item_id)
            quantity = float(quantities[i])
            individual_notes = item_notes[i] if i < len(item_notes) and item_notes[i] else ''

            if quantity <= 0:
                continue

            item = SimpleInventoryItem.query.get(item_id)
            if not item:
                continue

            # Calculate new stock (negative for consumption)
            new_stock = item.current_stock - quantity

            # Track insufficient stock but still process
            if new_stock < 0:
                insufficient_stock_items.append({
                    'name': item.name,
                    'requested': quantity,
                    'available': item.current_stock
                })

            # Update stock
            item.current_stock = new_stock

            # Create individual reason for this item
            item_reason = reason
            if individual_notes:
                item_reason += f' (Notes: {individual_notes})'

            # Create transaction record
            transaction = SimpleStockTransaction(
                item_id=item_id,
                transaction_type=treatment_type,
                quantity_change=-quantity,  # Negative for consumption
                new_stock_level=new_stock,
                user_id=current_user.id,
                reason=item_reason,
                reference_number=reference_number
            )
            db.session.add(transaction)

            processed_items.append(item.name)

            # Check for low stock alert
            if new_stock <= item.minimum_stock:
                existing_alert = SimpleLowStockAlert.query.filter_by(
                    item_id=item_id,
                    is_acknowledged=False
                ).first()

                if not existing_alert:
                    alert = SimpleLowStockAlert(
                        item_id=item_id,
                        current_stock=new_stock,
                        minimum_stock=item.minimum_stock
                    )
                    db.session.add(alert)

        if not processed_items:
            flash('No items were processed. Please check your selections.', 'warning')
            return redirect(url_for('simple_inventory'))

        db.session.commit()

        # Build success message
        success_msg = f'✅ {treatment_type} treatment recorded successfully!'
        success_msg += f' Processed {len(processed_items)} products'
        if client_name:
            success_msg += f' for {client_name}'

        flash(success_msg, 'success')

        # Show warnings for insufficient stock items
        if insufficient_stock_items:
            warning_msg = '⚠️ Some items had insufficient stock: '
            warning_items = [f'{item["name"]} (needed: {item["requested"]}, available: {item["available"]})' for item in insufficient_stock_items]
            flash(warning_msg + ', '.join(warning_items), 'warning')

    except ValueError as e:
        flash(f'Invalid input: {str(e)}', 'danger')
        db.session.rollback()
    except Exception as e:
        flash(f'Error recording bulk transaction: {str(e)}', 'danger')
        db.session.rollback()

    return redirect(url_for('simple_inventory'))

# Transaction Type Management Routes
@app.route('/add_transaction_type', methods=['POST'])
@login_required
def add_transaction_type():
    """Add a new transaction type"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('simple_inventory'))

    try:
        name = request.form.get('name', '').strip()
        display_name = request.form.get('display_name', '').strip()
        description = request.form.get('description', '').strip()

        if not name or not display_name:
            flash('Name and Display Name are required', 'warning')
            return redirect(url_for('simple_inventory'))

        # Check if name already exists
        existing_type = TransactionType.query.filter_by(name=name).first()
        if existing_type:
            flash('Transaction type with this name already exists', 'warning')
            return redirect(url_for('simple_inventory'))

        # Create new transaction type
        transaction_type = TransactionType(
            name=name,
            display_name=display_name,
            description=description if description else None
        )

        db.session.add(transaction_type)
        db.session.commit()

        flash(f'Transaction type "{display_name}" added successfully', 'success')

    except Exception as e:
        flash(f'Error adding transaction type: {str(e)}', 'danger')
        db.session.rollback()

    return redirect(url_for('simple_inventory'))

@app.route('/edit_transaction_type', methods=['POST'])
@login_required
def edit_transaction_type():
    """Edit an existing transaction type"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('simple_inventory'))

    try:
        type_id = int(request.form.get('type_id'))
        name = request.form.get('name', '').strip()
        display_name = request.form.get('display_name', '').strip()
        description = request.form.get('description', '').strip()

        transaction_type = TransactionType.query.get(type_id)
        if not transaction_type:
            flash('Transaction type not found', 'danger')
            return redirect(url_for('simple_inventory'))

        if not name or not display_name:
            flash('Name and Display Name are required', 'warning')
            return redirect(url_for('simple_inventory'))

        # Check if name already exists (excluding current type)
        existing_type = TransactionType.query.filter(
            TransactionType.name == name,
            TransactionType.id != type_id
        ).first()
        if existing_type:
            flash('Transaction type with this name already exists', 'warning')
            return redirect(url_for('simple_inventory'))

        # Update transaction type
        transaction_type.name = name
        transaction_type.display_name = display_name
        transaction_type.description = description if description else None

        db.session.commit()

        flash(f'Transaction type "{display_name}" updated successfully', 'success')

    except ValueError:
        flash('Invalid transaction type ID', 'danger')
    except Exception as e:
        flash(f'Error updating transaction type: {str(e)}', 'danger')
        db.session.rollback()

    return redirect(url_for('simple_inventory'))

@app.route('/toggle_transaction_type/<int:type_id>/<is_active>', methods=['POST'])
@login_required
def toggle_transaction_type(type_id, is_active):
    """Toggle transaction type active status"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        transaction_type = TransactionType.query.get(type_id)
        if not transaction_type:
            return jsonify({'error': 'Transaction type not found'}), 404

        active = is_active.lower() == 'true'
        transaction_type.is_active = active

        db.session.commit()

        status = 'activated' if active else 'deactivated'
        return jsonify({
            'success': True,
            'message': f'Transaction type "{transaction_type.display_name}" {status} successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/delete_transaction_type/<int:type_id>', methods=['POST'])
@login_required
def delete_transaction_type(type_id):
    """Delete a transaction type"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        transaction_type = TransactionType.query.get(type_id)
        if not transaction_type:
            return jsonify({'error': 'Transaction type not found'}), 404

        # Check if transaction type is used in any transactions
        used_count = SimpleStockTransaction.query.filter_by(transaction_type=transaction_type.name).count()
        if used_count > 0:
            return jsonify({
                'error': f'Cannot delete transaction type "{transaction_type.display_name}". It is used in {used_count} transaction(s).'
            }), 400

        display_name = transaction_type.display_name
        db.session.delete(transaction_type)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Transaction type "{display_name}" deleted successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Create default transaction types
def create_default_transaction_types():
    """Create default transaction types if they don't exist"""
    default_types = [
        {'name': 'Treatment', 'display_name': 'Treatment', 'description': 'Used for spa and salon treatments'},
        {'name': 'Sale', 'display_name': 'Sale', 'description': 'Products sold to customers'},
        {'name': 'Purchase', 'display_name': 'Purchase', 'description': 'New inventory purchased'},
        {'name': 'Return', 'display_name': 'Return', 'description': 'Items returned from customers'},
        {'name': 'Adjustment', 'display_name': 'Adjustment', 'description': 'Inventory adjustments'},
        {'name': 'Transfer', 'display_name': 'Transfer', 'description': 'Stock transfers between locations'},
    ]

    for type_data in default_types:
        existing_type = TransactionType.query.filter_by(name=type_data['name']).first()
        if not existing_type:
            transaction_type = TransactionType(**type_data)
            db.session.add(transaction_type)

    try:
        db.session.commit()
        print("Default transaction types created successfully!")
    except Exception as e:
        print(f"Error creating default transaction types: {e}")
        db.session.rollback()

# Call this when the app starts
try:
    create_default_transaction_types()
except Exception as e:
    print(f"Failed to create default transaction types: {e}")