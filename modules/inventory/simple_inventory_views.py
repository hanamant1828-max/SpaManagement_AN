"""
Simple Inventory Management Views
Two main modules: CRUD Operations and Consumption Tracking
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app import app, db
from models import SimpleInventoryItem, SimpleStockTransaction, SimpleLowStockAlert

@app.route('/simple_inventory')
@login_required
def simple_inventory():
    """Main inventory page with two tabs"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get all inventory items
    items = SimpleInventoryItem.query.filter_by(is_active=True).all()
    
    # Get recent transactions (last 50)
    transactions = SimpleStockTransaction.query.order_by(SimpleStockTransaction.date_time.desc()).limit(50).all()
    
    # Calculate statistics
    total_items = len(items)
    low_stock_count = len([item for item in items if item.is_low_stock])
    total_stock_value = sum(item.stock_value for item in items)
    
    # Today's transactions
    today = date.today()
    todays_transactions = SimpleStockTransaction.query.filter(
        db.func.date(SimpleStockTransaction.date_time) == today
    ).count()
    
    # Weekly transactions
    week_ago = today - timedelta(days=7)
    weekly_transactions = SimpleStockTransaction.query.filter(
        SimpleStockTransaction.date_time >= week_ago
    ).count()
    
    # Items consumed today
    items_consumed_today = SimpleStockTransaction.query.filter(
        db.func.date(SimpleStockTransaction.date_time) == today,
        SimpleStockTransaction.quantity_changed < 0
    ).count()
    
    # Average daily usage (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    total_monthly_transactions = SimpleStockTransaction.query.filter(
        SimpleStockTransaction.date_time >= thirty_days_ago
    ).count()
    avg_daily_usage = total_monthly_transactions / 30 if total_monthly_transactions > 0 else 0
    
    # Get unique categories
    categories = db.session.query(SimpleInventoryItem.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('simple_inventory.html',
                         items=items,
                         transactions=transactions,
                         total_items=total_items,
                         low_stock_count=low_stock_count,
                         total_stock_value=total_stock_value,
                         todays_transactions=todays_transactions,
                         weekly_transactions=weekly_transactions,
                         items_consumed_today=items_consumed_today,
                         avg_daily_usage=round(avg_daily_usage, 1),
                         total_transactions=len(transactions),
                         categories=categories)

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
        
        # Check if SKU already exists
        existing_item = SimpleInventoryItem.query.filter_by(sku=sku).first()
        if existing_item:
            flash(f'SKU "{sku}" already exists. Please use a different SKU.', 'danger')
            return redirect(url_for('simple_inventory'))
        
        new_item = SimpleInventoryItem(
            name=request.form.get('name').strip(),
            sku=sku,
            description=request.form.get('description', '').strip(),
            category=request.form.get('category'),
            brand=request.form.get('brand', '').strip(),
            current_stock=float(request.form.get('current_stock', 0)),
            reorder_level=float(request.form.get('reorder_level', 10)),
            maximum_stock=float(request.form.get('maximum_stock', 100)),
            unit_price=float(request.form.get('unit_price', 0)),
            cost_price=float(request.form.get('cost_price', 0)),
            supplier_name=request.form.get('supplier_name', '').strip(),
            supplier_contact=request.form.get('supplier_contact', '').strip(),
            location=request.form.get('location', '').strip(),
            warehouse_section=request.form.get('warehouse_section', '').strip()
        )
        
        db.session.add(new_item)
        db.session.commit()
        
        # Create initial stock transaction
        if new_item.current_stock > 0:
            initial_transaction = SimpleStockTransaction(
                item_id=new_item.id,
                transaction_type='Purchase',
                quantity_changed=new_item.current_stock,
                remaining_balance=new_item.current_stock,
                user_id=current_user.id,
                reason='Initial stock entry',
                reference_number=f'INITIAL-{new_item.id}'
            )
            db.session.add(initial_transaction)
            db.session.commit()
        
        flash(f'Inventory item "{new_item.name}" added successfully!', 'success')
        
    except ValueError as e:
        flash(f'Invalid input: {str(e)}', 'danger')
    except Exception as e:
        flash(f'Error adding item: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('simple_inventory'))

@app.route('/update_item_stock', methods=['POST'])
@login_required
def update_item_stock():
    """Update item stock and record transaction"""
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
        
        # For certain transaction types, make quantity negative
        if transaction_type in ['Sale', 'Transfer'] and quantity_change > 0:
            quantity_change = -quantity_change
        elif transaction_type in ['Purchase', 'Return'] and quantity_change < 0:
            quantity_change = abs(quantity_change)
        
        # Calculate new stock level
        new_stock = item.current_stock + quantity_change
        
        if new_stock < 0:
            flash(f'Cannot reduce stock below zero. Current stock: {item.current_stock}', 'danger')
            return redirect(url_for('simple_inventory'))
        
        # Update item stock
        item.current_stock = new_stock
        item.last_updated = datetime.utcnow()
        
        # Create transaction record
        transaction = SimpleStockTransaction(
            item_id=item_id,
            transaction_type=transaction_type,
            quantity_changed=quantity_change,
            remaining_balance=new_stock,
            user_id=current_user.id,
            reason=reason or f'{transaction_type} transaction',
            reference_number=reference_number
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Check for low stock alert
        if item.is_low_stock:
            # Create low stock alert if not already exists
            existing_alert = SimpleLowStockAlert.query.filter_by(
                item_id=item_id, 
                is_acknowledged=False
            ).first()
            
            if not existing_alert:
                alert = SimpleLowStockAlert(
                    item_id=item_id,
                    current_stock=item.current_stock,
                    reorder_level=item.reorder_level
                )
                db.session.add(alert)
                db.session.commit()
        
        flash(f'Stock updated successfully. New stock level: {new_stock}', 'success')
        
    except ValueError as e:
        flash(f'Invalid input: {str(e)}', 'danger')
    except Exception as e:
        flash(f'Error updating stock: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('simple_inventory'))

@app.route('/record_transaction', methods=['POST'])
@login_required
def record_transaction():
    """Record a consumption tracking transaction"""
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
        
        # Determine quantity change based on transaction type
        if transaction_type in ['Sale', 'Transfer']:
            quantity_change = -abs(quantity)  # Remove from stock
        elif transaction_type in ['Purchase', 'Return']:
            quantity_change = abs(quantity)   # Add to stock
        else:  # Adjustment
            # For adjustments, use the quantity as-is (can be positive or negative)
            quantity_change = quantity
        
        # Calculate new stock level
        new_stock = item.current_stock + quantity_change
        
        if new_stock < 0:
            flash(f'Insufficient stock. Current stock: {item.current_stock}, Requested: {abs(quantity_change)}', 'danger')
            return redirect(url_for('simple_inventory'))
        
        # Update item stock
        item.current_stock = new_stock
        item.last_updated = datetime.utcnow()
        
        # Create transaction record
        transaction = SimpleStockTransaction(
            item_id=item_id,
            transaction_type=transaction_type,
            quantity_changed=quantity_change,
            remaining_balance=new_stock,
            user_id=current_user.id,
            reason=reason or f'{transaction_type} transaction',
            reference_number=reference_number
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Transaction recorded successfully. New stock level: {new_stock}', 'success')
        
    except ValueError as e:
        flash(f'Invalid input: {str(e)}', 'danger')
    except Exception as e:
        flash(f'Error recording transaction: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('simple_inventory'))

@app.route('/delete_inventory_item/<int:item_id>', methods=['POST'])
@login_required
def delete_inventory_item(item_id):
    """Delete inventory item (soft delete)"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        item = SimpleInventoryItem.query.get(item_id)
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        # Soft delete - just mark as inactive
        item.is_active = False
        item.last_updated = datetime.utcnow()
        
        # Record transaction
        transaction = SimpleStockTransaction(
            item_id=item_id,
            transaction_type='Adjustment',
            quantity_changed=-item.current_stock,
            remaining_balance=0,
            user_id=current_user.id,
            reason='Item deleted'
        )
        
        item.current_stock = 0
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API Endpoints for AJAX functionality

@app.route('/api/inventory/search')
@login_required
def api_inventory_search():
    """Search inventory items via API"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403
    
    search_term = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    
    query = SimpleInventoryItem.query.filter_by(is_active=True)
    
    if search_term:
        query = query.filter(
            db.or_(
                SimpleInventoryItem.name.ilike(f'%{search_term}%'),
                SimpleInventoryItem.sku.ilike(f'%{search_term}%'),
                SimpleInventoryItem.description.ilike(f'%{search_term}%')
            )
        )
    
    if category:
        query = query.filter(SimpleInventoryItem.category == category)
    
    items = query.all()
    
    # Filter by status
    if status == 'low_stock':
        items = [item for item in items if item.is_low_stock]
    elif status == 'out_of_stock':
        items = [item for item in items if item.is_out_of_stock]
    elif status == 'normal':
        items = [item for item in items if not item.is_low_stock and not item.is_out_of_stock]
    
    return jsonify({
        'items': [{
            'id': item.id,
            'name': item.name,
            'sku': item.sku,
            'category': item.category,
            'current_stock': item.current_stock,
            'reorder_level': item.reorder_level,
            'unit_price': item.unit_price,
            'stock_value': item.stock_value,
            'supplier_name': item.supplier_name,
            'is_low_stock': item.is_low_stock,
            'is_out_of_stock': item.is_out_of_stock
        } for item in items]
    })

@app.route('/api/inventory/low_stock_alerts')
@login_required
def api_low_stock_alerts():
    """Get current low stock alerts"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403
    
    alerts = db.session.query(SimpleLowStockAlert, SimpleInventoryItem).join(
        SimpleInventoryItem, SimpleLowStockAlert.item_id == SimpleInventoryItem.id
    ).filter(
        SimpleLowStockAlert.is_acknowledged == False,
        SimpleInventoryItem.is_active == True
    ).all()
    
    return jsonify({
        'alerts': [{
            'id': alert.id,
            'item_name': item.name,
            'current_stock': alert.current_stock,
            'reorder_level': alert.reorder_level,
            'alert_date': alert.alert_date.isoformat()
        } for alert, item in alerts]
    })

@app.route('/api/inventory/usage_report')
@login_required
def api_usage_report():
    """Generate usage analytics report"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403
    
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now() - timedelta(days=days)
    
    # Get transaction summary
    transactions = SimpleStockTransaction.query.filter(
        SimpleStockTransaction.date_time >= start_date
    ).all()
    
    # Calculate usage patterns
    usage_by_item = {}
    usage_by_type = {}
    
    for txn in transactions:
        # By item
        if txn.item.name not in usage_by_item:
            usage_by_item[txn.item.name] = 0
        if txn.quantity_changed < 0:  # Only count outgoing transactions
            usage_by_item[txn.item.name] += abs(txn.quantity_changed)
        
        # By transaction type
        if txn.transaction_type not in usage_by_type:
            usage_by_type[txn.transaction_type] = 0
        usage_by_type[txn.transaction_type] += 1
    
    # Top 10 most used items
    top_items = sorted(usage_by_item.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return jsonify({
        'period_days': days,
        'total_transactions': len(transactions),
        'top_consumed_items': top_items,
        'transaction_types': usage_by_type,
        'total_items_tracked': len(usage_by_item)
    })

@app.route('/record_bulk_transaction', methods=['POST'])
@login_required
def record_bulk_transaction():
    """Record multiple inventory items consumed in one treatment/transaction"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('simple_inventory'))

    try:
        treatment_type = request.form.get('treatment_type')
        client_name = request.form.get('client_name', '').strip()
        reason = request.form.get('reason', '').strip()
        
        item_ids = request.form.getlist('item_ids[]')
        quantities = request.form.getlist('quantities[]')
        item_notes = request.form.getlist('item_notes[]')
        
        if not item_ids or not quantities:
            flash('Please select at least one product with quantity', 'warning')
            return redirect(url_for('simple_inventory'))
        
        if len(item_ids) != len(quantities):
            flash('Mismatch between products and quantities', 'danger')
            return redirect(url_for('simple_inventory'))
        
        # Generate reference number for this bulk transaction
        import random
        reference_number = f'BULK-{datetime.now().strftime("%Y%m%d")}-{random.randint(1000, 9999)}'
        
        processed_items = []
        insufficient_stock_items = []
        
        # Process each item in the bulk transaction
        for i, (item_id, quantity_str) in enumerate(zip(item_ids, quantities)):
            if not item_id or not quantity_str:
                continue
                
            item_id = int(item_id)
            quantity = float(quantity_str)
            item_note = item_notes[i] if i < len(item_notes) else ''
            
            item = SimpleInventoryItem.query.get(item_id)
            if not item:
                flash(f'Invalid item selected', 'danger')
                continue
                
            # Check if sufficient stock
            if item.current_stock < quantity:
                insufficient_stock_items.append({
                    'name': item.name,
                    'requested': quantity,
                    'available': item.current_stock
                })
                continue
            
            # Update stock
            old_stock = item.current_stock
            item.current_stock -= quantity
            item.last_updated = datetime.utcnow()
            
            # Build comprehensive reason
            treatment_reason = f'{treatment_type} Treatment'
            if client_name:
                treatment_reason += f' for {client_name}'
            if reason:
                treatment_reason += f' - {reason}'
            if item_note:
                treatment_reason += f' ({item_note})'
            
            # Create transaction record
            transaction = SimpleStockTransaction(
                item_id=item_id,
                transaction_type='Treatment',
                quantity_changed=-quantity,
                remaining_balance=item.current_stock,
                user_id=current_user.id,
                reason=treatment_reason,
                reference_number=reference_number
            )
            
            db.session.add(transaction)
            processed_items.append({
                'name': item.name,
                'quantity': quantity,
                'remaining': item.current_stock
            })
            
            # Create low stock alert if needed
            if item.is_low_stock:
                existing_alert = SimpleLowStockAlert.query.filter_by(
                    item_id=item_id, 
                    is_acknowledged=False
                ).first()
                
                if not existing_alert:
                    alert = SimpleLowStockAlert(
                        item_id=item_id,
                        current_stock=item.current_stock,
                        reorder_level=item.reorder_level
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

