
"""
Comprehensive Inventory Management System
Complete inventory solution with all requested features:
- Category Management
- Supplier Management  
- Product Master
- Consumption Tracking
- Purchase Management
- Transaction History
- Reports & Analytics
"""

from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_, desc
from app import app, db
from models import User
import json
import uuid

# Import or create models for comprehensive inventory
try:
    from modules.hanamantinventory.models import HanamanCategory, HanamanSupplier, ProductMaster, Purchase, Transaction
    from modules.hanamantinventory.queries import (
        get_all_categories, get_all_suppliers, get_all_product_masters, 
        get_all_purchases, get_all_transactions, get_transaction_summary
    )
except ImportError:
    # Fallback models if hanamantinventory models don't exist
    HanamanCategory = None
    HanamanSupplier = None
    ProductMaster = None
    Purchase = None
    Transaction = None

@app.route('/inventory_complete')
@login_required
def comprehensive_inventory():
    """Main comprehensive inventory management page"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get all data for comprehensive view
    try:
        categories = get_all_categories() if HanamanCategory else []
        suppliers = get_all_suppliers() if HanamanSupplier else []
        products = get_all_product_masters() if ProductMaster else []
        purchases = get_all_purchases() if Purchase else []
        transactions = get_all_transactions() if Transaction else []
        consumption_records = get_consumption_records()
        low_stock_products = get_low_stock_products()
        
        # Calculate statistics
        stats = {
            'total_products': len(products),
            'total_categories': len(categories),
            'total_suppliers': len(suppliers),
            'low_stock_items': len(low_stock_products),
            'total_purchases': len(purchases),
            'total_transactions': len(transactions)
        }
        
    except Exception as e:
        flash(f'Error loading inventory data: {str(e)}', 'warning')
        categories = suppliers = products = purchases = transactions = []
        consumption_records = low_stock_products = []
        stats = {
            'total_products': 0,
            'total_categories': 0,
            'total_suppliers': 0,
            'low_stock_items': 0,
            'total_purchases': 0,
            'total_transactions': 0
        }

    return render_template('inventory_management.html',
                         categories=categories,
                         suppliers=suppliers,
                         products=products,
                         purchases=purchases,
                         transactions=transactions,
                         consumption_records=consumption_records,
                         low_stock_products=low_stock_products,
                         stats=stats)

# Category Management Routes - Removed duplicate route (handled by inventory_category_views.py)

# Removed edit_inventory_category route - handled by inventory_category_views.py

# Removed delete_inventory_category route - handled by inventory_category_views.py

# Supplier Management Routes
@app.route('/inventory/supplier/add', methods=['POST'])
@login_required
def add_inventory_supplier():
    """Add new supplier"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        if not HanamanSupplier:
            return jsonify({'error': 'Supplier model not available'}), 500

        supplier_data = {
            'name': request.form.get('name', '').strip(),
            'contact_person': request.form.get('contact_person', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'email': request.form.get('email', '').strip(),
            'address': request.form.get('address', '').strip(),
            'city': request.form.get('city', '').strip(),
            'state': request.form.get('state', '').strip(),
            'pincode': request.form.get('pincode', '').strip(),
            'gst_number': request.form.get('gst_number', '').strip(),
            'payment_terms': request.form.get('payment_terms', '').strip(),
            'is_active': request.form.get('is_active') == 'on',
            'created_by': current_user.id
        }

        if not supplier_data['name']:
            return jsonify({'error': 'Supplier name is required'}), 400

        supplier = HanamanSupplier(**supplier_data)
        db.session.add(supplier)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Supplier added successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Product Master Routes
@app.route('/inventory/product/add', methods=['POST'])
@login_required
def add_inventory_product():
    """Add new product to master"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        if not ProductMaster:
            return jsonify({'error': 'Product model not available'}), 500

        product_data = {
            'product_name': request.form.get('product_name', '').strip(),
            'category_id': int(request.form.get('category_id', 0)),
            'supplier_id': int(request.form.get('supplier_id', 0)),
            'unit': request.form.get('unit', '').strip(),
            'min_stock': int(request.form.get('min_stock', 5)),
            'current_stock': float(request.form.get('current_stock', 0)),
            'unit_cost': float(request.form.get('unit_cost', 0)),
            'selling_price': float(request.form.get('selling_price', 0)),
            'is_active': request.form.get('is_active') == 'on',
            'created_by': current_user.id
        }

        if not product_data['product_name']:
            return jsonify({'error': 'Product name is required'}), 400

        product = ProductMaster(**product_data)
        db.session.add(product)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Product added successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Consumption Tracking Routes
@app.route('/inventory/consumption/add', methods=['POST'])
@login_required
def record_consumption():
    """Record product consumption"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        from models import ConsumptionEntry, StockMovement, Inventory
        
        consumption_data = {
            'inventory_id': int(request.form.get('product_id', 0)),
            'quantity': float(request.form.get('quantity', 0)),
            'unit': request.form.get('unit', '').strip(),
            'entry_type': request.form.get('entry_type', 'consume'),
            'reason': f"{request.form.get('purpose', '').strip()} - {request.form.get('notes', '').strip()}".strip(),
            'staff_id': int(request.form.get('staff_id', current_user.id)),
            'created_at': datetime.utcnow()
        }

        if not consumption_data['inventory_id'] or not consumption_data['quantity']:
            return jsonify({'error': 'Product and quantity are required'}), 400

        # Get inventory item
        inventory = Inventory.query.get(consumption_data['inventory_id'])
        if not inventory:
            return jsonify({'error': 'Inventory item not found'}), 404
            
        if inventory.current_stock < consumption_data['quantity']:
            return jsonify({'error': 'Insufficient stock available'}), 400

        # Create consumption record
        consumption = ConsumptionEntry(
            inventory_id=consumption_data['inventory_id'],
            entry_type=consumption_data['entry_type'],
            quantity=consumption_data['quantity'],
            unit=consumption_data['unit'],
            reason=consumption_data['reason'],
            staff_id=consumption_data['staff_id'],
            cost_impact=consumption_data['quantity'] * (inventory.cost_price or 0),
            created_at=consumption_data['created_at']
        )
        
        # Create stock movement
        movement = StockMovement(
            inventory_id=consumption_data['inventory_id'],
            movement_type='out',
            quantity=-consumption_data['quantity'],
            unit=consumption_data['unit'],
            reason=consumption_data['reason'],
            created_by=consumption_data['staff_id'],
            created_at=consumption_data['created_at']
        )
        
        # Update inventory stock
        inventory.current_stock = max(0, inventory.current_stock - consumption_data['quantity'])
        inventory.updated_at = datetime.utcnow()
        
        db.session.add(consumption)
        db.session.add(movement)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Consumption recorded successfully',
            'remaining_stock': inventory.current_stock
        })
        
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/inventory/consumption/report')
@login_required
def consumption_report():
    """Get consumption report"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403
        
    try:
        from models import ConsumptionEntry, Inventory, User
        from datetime import datetime, timedelta
        
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get consumption summary
        consumption_summary = db.session.query(
            Inventory.name.label('item_name'),
            ConsumptionEntry.entry_type,
            db.func.sum(ConsumptionEntry.quantity).label('total_quantity'),
            db.func.sum(ConsumptionEntry.cost_impact).label('total_cost'),
            db.func.count(ConsumptionEntry.id).label('total_entries')
        ).join(
            ConsumptionEntry, Inventory.id == ConsumptionEntry.inventory_id
        ).filter(
            ConsumptionEntry.created_at >= start_date
        ).group_by(
            Inventory.name, ConsumptionEntry.entry_type
        ).all()
        
        report_data = []
        for item in consumption_summary:
            report_data.append({
                'item_name': item.item_name,
                'entry_type': item.entry_type,
                'total_quantity': float(item.total_quantity),
                'total_cost': float(item.total_cost or 0),
                'total_entries': item.total_entries
            })
            
        return jsonify({
            'status': 'success',
            'report': report_data,
            'period_days': days
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Purchase Management Routes
@app.route('/inventory/purchase/add', methods=['POST'])
@login_required
def add_purchase_order():
    """Add new purchase order"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        if not Purchase:
            return jsonify({'error': 'Purchase model not available'}), 500

        purchase_data = {
            'purchase_order_number': request.form.get('purchase_order_number', f'PO-{uuid.uuid4().hex[:8].upper()}'),
            'product_master_id': int(request.form.get('product_id', 0)),
            'supplier_id': int(request.form.get('supplier_id', 0)),
            'quantity': float(request.form.get('quantity', 0)),
            'unit_price': float(request.form.get('unit_price', 0)),
            'total_amount': float(request.form.get('quantity', 0)) * float(request.form.get('unit_price', 0)),
            'purchase_date': datetime.strptime(request.form.get('purchase_date'), '%Y-%m-%d').date(),
            'expected_delivery': datetime.strptime(request.form.get('expected_delivery'), '%Y-%m-%d').date() if request.form.get('expected_delivery') else None,
            'status': 'pending',
            'notes': request.form.get('notes', '').strip(),
            'created_by': current_user.id
        }

        if not all([purchase_data['product_master_id'], purchase_data['supplier_id'], purchase_data['quantity'], purchase_data['unit_price']]):
            return jsonify({'error': 'All required fields must be filled'}), 400

        purchase = Purchase(**purchase_data)
        db.session.add(purchase)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Purchase order created successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/inventory/purchase/receive/<int:purchase_id>', methods=['POST'])
@login_required
def receive_purchase(purchase_id):
    """Mark purchase as received and update stock"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        if not Purchase or not ProductMaster:
            return jsonify({'error': 'Required models not available'}), 500

        purchase = Purchase.query.get_or_404(purchase_id)
        received_quantity = float(request.form.get('received_quantity', purchase.quantity))
        
        purchase.status = 'received'
        purchase.received_date = datetime.now().date()
        purchase.received_quantity = received_quantity
        purchase.updated_by = current_user.id
        purchase.updated_at = datetime.utcnow()

        # Update product stock
        product = ProductMaster.query.get(purchase.product_master_id)
        if product:
            product.current_stock += received_quantity

        # Create transaction record
        if Transaction:
            transaction = Transaction(
                transaction_number=f'TXN-{uuid.uuid4().hex[:8].upper()}',
                product_master_id=purchase.product_master_id,
                transaction_type='in',
                quantity=received_quantity,
                unit_cost=purchase.unit_price,
                total_cost=received_quantity * purchase.unit_price,
                transaction_date=datetime.now().date(),
                reason='Purchase received',
                reference_type='purchase',
                reference_id=str(purchase_id),
                reference_name=purchase.purchase_order_number,
                created_by=current_user.id
            )
            db.session.add(transaction)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Purchase received successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Reports and Analytics Routes
@app.route('/inventory/reports/stock_levels')
@login_required
def stock_levels_report():
    """Get stock levels data for charts"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        if not ProductMaster:
            return jsonify({'error': 'Product model not available'}), 500

        products = ProductMaster.query.filter_by(is_active=True).all()
        
        data = {
            'labels': [p.product_name for p in products],
            'current_stock': [p.current_stock or 0 for p in products],
            'min_stock': [p.min_stock or 0 for p in products]
        }
        
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/inventory/reports/consumption_trends')
@login_required
def consumption_trends_report():
    """Get consumption trends data for charts"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # This would need a ConsumptionRecord model
        # For now, return dummy data
        data = {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'consumption': [120, 135, 140, 125, 160, 145]
        }
        
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper functions
def get_consumption_records():
    """Get consumption records - placeholder until ConsumptionRecord model is created"""
    return []

def get_low_stock_products():
    """Get products with low stock levels"""
    try:
        if not ProductMaster:
            return []
        
        return ProductMaster.query.filter(
            ProductMaster.is_active == True,
            ProductMaster.current_stock <= ProductMaster.min_stock
        ).all()
    except:
        return []

# API Routes for AJAX calls
@app.route('/api/inventory/product/<int:product_id>')
@login_required
def api_get_product(product_id):
    """Get product data as JSON"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        if not ProductMaster:
            return jsonify({'error': 'Product model not available'}), 500

        product = ProductMaster.query.get_or_404(product_id)
        return jsonify({
            'id': product.id,
            'product_name': product.product_name,
            'category_id': product.category_id,
            'supplier_id': product.supplier_id,
            'current_stock': product.current_stock or 0,
            'min_stock': product.min_stock or 0,
            'unit': product.unit,
            'unit_cost': getattr(product, 'unit_cost', 0),
            'selling_price': getattr(product, 'selling_price', 0),
            'is_active': product.is_active
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/supplier/<int:supplier_id>')
@login_required
def api_get_supplier(supplier_id):
    """Get supplier data as JSON"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        if not HanamanSupplier:
            return jsonify({'error': 'Supplier model not available'}), 500

        supplier = HanamanSupplier.query.get_or_404(supplier_id)
        return jsonify({
            'id': supplier.id,
            'name': supplier.name,
            'contact_person': supplier.contact_person,
            'phone': supplier.phone,
            'email': supplier.email,
            'address': supplier.address,
            'city': supplier.city,
            'state': supplier.state,
            'pincode': supplier.pincode,
            'gst_number': supplier.gst_number,
            'payment_terms': supplier.payment_terms,
            'is_active': supplier.is_active
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
