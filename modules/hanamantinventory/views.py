"""
Hanaman Inventory Views
Simple, clean routes for inventory management
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from .queries import (
    get_all_products, get_product_by_id, create_product, update_product, delete_product,
    get_all_categories, get_category_by_id, create_category, update_category, delete_category,
    get_low_stock_products, search_products, update_stock, get_inventory_stats, get_stock_movements,
    get_all_suppliers, get_supplier_by_id, create_supplier, update_supplier, delete_supplier,
    get_all_product_masters, get_product_master_by_id, create_product_master, update_product_master, delete_product_master,
    get_all_purchases, get_purchase_by_id, create_purchase, update_purchase, delete_purchase,
    get_all_transactions, get_transaction_by_id, create_transaction, update_transaction, delete_transaction, get_transaction_summary
)
import uuid

# Main inventory page
@app.route('/hanaman-inventory')
@login_required
def hanaman_inventory():
    """Main inventory management page"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get filter parameters
    search_query = request.args.get('search', '')
    filter_type = request.args.get('filter', 'all')

    # Get products based on filters
    if search_query:
        products = search_products(search_query)
    elif filter_type == 'low_stock':
        products = get_low_stock_products()
    else:
        products = get_all_products()

    # Get categories for dropdowns
    categories = get_all_categories()

    # Get statistics
    stats = get_inventory_stats()

    return render_template('hanaman_inventory.html', 
                         products=products, 
                         categories=categories, 
                         stats=stats,
                         search_query=search_query,
                         filter_type=filter_type)

# Product CRUD operations
@app.route('/hanaman-inventory/product/add', methods=['POST'])
@login_required
def hanaman_add_product():
    """Add new product"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        # Generate SKU if not provided
        sku = request.form.get('sku', '').strip()
        if not sku:
            sku = f"HAN-{str(uuid.uuid4())[:8].upper()}"

        product_data = {
            'name': request.form.get('name', '').strip(),
            'sku': sku,
            'description': request.form.get('description', '').strip(),
            'category_id': int(request.form.get('category_id')) if request.form.get('category_id') else None,
            'current_stock': float(request.form.get('current_stock', 0)),
            'min_stock_level': float(request.form.get('min_stock_level', 5)),
            'max_stock_level': float(request.form.get('max_stock_level', 100)),
            'unit': request.form.get('unit', 'pcs').strip(),
            'cost_price': float(request.form.get('cost_price', 0)),
            'selling_price': float(request.form.get('selling_price', 0)),
            'supplier_name': request.form.get('supplier_name', '').strip(),
            'supplier_contact': request.form.get('supplier_contact', '').strip(),
        }

        # Validate required fields
        if not product_data['name']:
            flash('Product name is required', 'danger')
            return redirect(url_for('hanaman_inventory'))

        product = create_product(product_data)
        if product:
            flash(f'Product "{product.name}" added successfully!', 'success')
        else:
            flash('Error adding product. SKU might already exist.', 'danger')

    except ValueError as e:
        flash(f'Invalid input: Please check your data', 'danger')
    except Exception as e:
        flash(f'Error adding product: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory'))

@app.route('/hanaman-inventory/product/edit/<int:product_id>', methods=['POST'])
@login_required
def hanaman_edit_product(product_id):
    """Edit existing product"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        product_data = {
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip(),
            'category_id': int(request.form.get('category_id')) if request.form.get('category_id') else None,
            'min_stock_level': float(request.form.get('min_stock_level', 5)),
            'max_stock_level': float(request.form.get('max_stock_level', 100)),
            'unit': request.form.get('unit', 'pcs').strip(),
            'cost_price': float(request.form.get('cost_price', 0)),
            'selling_price': float(request.form.get('selling_price', 0)),
            'supplier_name': request.form.get('supplier_name', '').strip(),
            'supplier_contact': request.form.get('supplier_contact', '').strip(),
        }

        product = update_product(product_id, product_data)
        if product:
            flash(f'Product "{product.name}" updated successfully!', 'success')
        else:
            flash('Error updating product', 'danger')

    except ValueError:
        flash('Invalid input: Please check your data', 'danger')
    except Exception as e:
        flash(f'Error updating product: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory'))

@app.route('/hanaman-inventory/product/delete/<int:product_id>', methods=['POST'])
@login_required
def hanaman_delete_product(product_id):
    """Delete product"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        product = get_product_by_id(product_id)
        if product and delete_product(product_id):
            flash(f'Product "{product.name}" deleted successfully!', 'success')
        else:
            flash('Error deleting product', 'danger')
    except Exception as e:
        flash(f'Error deleting product: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory'))

# Stock operations
@app.route('/hanaman-inventory/stock/update/<int:product_id>', methods=['POST'])
@login_required
def hanaman_update_stock(product_id):
    """Update product stock"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        new_quantity = float(request.form.get('new_quantity', 0))
        reason = request.form.get('reason', 'Manual stock update').strip()

        product = update_stock(product_id, new_quantity, 'adjust', reason)
        if product:
            flash(f'Stock updated for "{product.name}". New quantity: {new_quantity} {product.unit}', 'success')
        else:
            flash('Error updating stock', 'danger')

    except ValueError:
        flash('Invalid quantity value', 'danger')
    except Exception as e:
        flash(f'Error updating stock: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory'))

# Category operations
@app.route('/hanaman-inventory/category/add', methods=['POST'])
@login_required
def hanaman_add_category():
    """Add new category"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Category name is required', 'danger')
            return redirect(url_for('hanaman_inventory'))

        category = create_category(name, description)
        if category:
            flash(f'Category "{category.name}" added successfully!', 'success')
        else:
            flash('Error adding category. Name might already exist.', 'danger')

    except Exception as e:
        flash(f'Error adding category: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory'))

# Consumption route
@app.route('/hanaman-inventory/consume/<int:product_id>', methods=['POST'])
@login_required
def hanaman_consume_stock(product_id):
    """Consume/Use inventory stock"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        quantity_to_consume = float(request.form.get('new_quantity', 0))
        reason = request.form.get('reason', 'Stock consumption').strip()
        notes = request.form.get('notes', '').strip()

        if quantity_to_consume <= 0:
            flash('Consumption quantity must be greater than zero', 'danger')
            return redirect(url_for('hanaman_inventory'))

        product = get_product_by_id(product_id)
        if not product:
            flash('Product not found', 'danger')
            return redirect(url_for('hanaman_inventory'))

        if product.current_stock < quantity_to_consume:
            flash(f'Insufficient stock. Available: {product.current_stock} {product.unit}', 'danger')
            return redirect(url_for('hanaman_inventory'))

        # Calculate new stock after consumption
        new_stock = max(0, product.current_stock - quantity_to_consume)
        full_reason = f"{reason}" + (f" - {notes}" if notes else "")

        updated_product = update_stock(product_id, new_stock, 'consume', full_reason)
        if updated_product:
            flash(f'Consumed {quantity_to_consume} {product.unit} of "{product.name}". Remaining: {new_stock} {product.unit}', 'success')
        else:
            flash('Error processing consumption', 'danger')

    except ValueError:
        flash('Invalid quantity value', 'danger')
    except Exception as e:
        flash(f'Error consuming stock: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory'))

# API endpoints for AJAX requests
@app.route('/api/hanaman-inventory/product/<int:product_id>')
@login_required
def api_hanaman_get_product(product_id):
    """Get product data as JSON"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    product = get_product_by_id(product_id)
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'description': product.description,
            'category_id': product.category_id,
            'current_stock': product.current_stock,
            'min_stock_level': product.min_stock_level,
            'max_stock_level': product.max_stock_level,
            'unit': product.unit,
            'cost_price': product.cost_price,
            'selling_price': product.selling_price,
            'supplier_name': product.supplier_name,
            'supplier_contact': product.supplier_contact,
            'stock_status': product.stock_status
        })
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/hanaman-inventory/stats')
@login_required
def api_hanaman_inventory_stats():
    """Get inventory statistics as JSON"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    return jsonify(get_inventory_stats())

# Configuration Page
@app.route('/hanaman-inventory/config')
@login_required
def hanaman_inventory_config():
    """Configuration page with categories, suppliers, product masters, purchases and transactions"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    categories = get_all_categories()
    suppliers = get_all_suppliers()
    product_masters_data = get_all_product_masters()
    purchases_data = get_all_purchases()
    transactions_data = get_all_transactions()
    transaction_summary = get_transaction_summary()

    return render_template('hanaman_config.html', 
                         categories=categories,
                         suppliers=suppliers,
                         product_masters_data=product_masters_data,
                         purchases_data=purchases_data,
                         transactions_data=transactions_data,
                         transaction_summary=transaction_summary)

# Category CRUD operations
@app.route('/hanaman-inventory/category/edit/<int:category_id>', methods=['POST'])
@login_required
def hanaman_edit_category(category_id):
    """Edit existing category"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Category name is required', 'danger')
            return redirect(url_for('hanaman_inventory_config'))

        category = update_category(category_id, name, description)
        if category:
            flash(f'Category "{category.name}" updated successfully!', 'success')
        else:
            flash('Error updating category', 'danger')

    except Exception as e:
        flash(f'Error updating category: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory_config'))

@app.route('/hanaman-inventory/category/delete/<int:category_id>', methods=['POST'])
@login_required
def hanaman_delete_category(category_id):
    """Delete category"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        category = get_category_by_id(category_id)
        if category and delete_category(category_id):
            flash(f'Category "{category.name}" deleted successfully!', 'success')
        else:
            flash('Error deleting category', 'danger')
    except Exception as e:
        flash(f'Error deleting category: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory_config'))

# Supplier CRUD operations
@app.route('/hanaman-inventory/supplier/add', methods=['POST'])
@login_required
def hanaman_add_supplier():
    """Add new supplier"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
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
        }

        if not supplier_data['name']:
            flash('Supplier name is required', 'danger')
            return redirect(url_for('hanaman_inventory_config'))

        supplier = create_supplier(supplier_data)
        if supplier:
            flash(f'Supplier "{supplier.name}" added successfully!', 'success')
        else:
            flash('Error adding supplier. Name might already exist.', 'danger')

    except Exception as e:
        flash(f'Error adding supplier: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory_config'))

@app.route('/hanaman-inventory/supplier/edit/<int:supplier_id>', methods=['POST'])
@login_required
def hanaman_edit_supplier(supplier_id):
    """Edit existing supplier"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
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
        }

        supplier = update_supplier(supplier_id, supplier_data)
        if supplier:
            flash(f'Supplier "{supplier.name}" updated successfully!', 'success')
        else:
            flash('Error updating supplier', 'danger')

    except Exception as e:
        flash(f'Error updating supplier: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory_config'))

@app.route('/hanaman-inventory/supplier/delete/<int:supplier_id>', methods=['POST'])
@login_required
def hanaman_delete_supplier(supplier_id):
    """Delete supplier"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        supplier = get_supplier_by_id(supplier_id)
        if supplier and delete_supplier(supplier_id):
            flash(f'Supplier "{supplier.name}" deleted successfully!', 'success')
        else:
            flash('Error deleting supplier', 'danger')
    except Exception as e:
        flash(f'Error deleting supplier: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory_config'))

# Product Master Management Routes
@app.route('/hanaman-inventory/product-master')
@login_required
def hanaman_product_master():
    """Product Master management page"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get all product masters with joined data
    product_masters_data = get_all_product_masters()
    categories = get_all_categories()
    suppliers = get_all_suppliers()

    return render_template('product_master.html', 
                         product_masters_data=product_masters_data,
                         categories=categories,
                         suppliers=suppliers)

@app.route('/hanaman-inventory/product-master/add', methods=['POST'])
@login_required
def hanaman_add_product_master():
    """Add new product master"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        product_data = {
            'product_name': request.form.get('product_name', '').strip(),
            'category_id': int(request.form.get('category_id')),
            'supplier_id': int(request.form.get('supplier_id')),
            'unit': request.form.get('unit', '').strip(),
            'min_stock': int(request.form.get('min_stock', 5))
        }

        # Validate required fields
        if not product_data['product_name']:
            flash('Product name is required', 'danger')
            return redirect(url_for('hanaman_product_master'))

        if not product_data['unit']:
            flash('Unit is required', 'danger')
            return redirect(url_for('hanaman_product_master'))

        product = create_product_master(product_data)
        if product:
            flash(f'Product "{product.product_name}" added successfully!', 'success')
        else:
            flash('Error adding product master', 'danger')

    except ValueError as e:
        flash('Invalid input: Please check your data', 'danger')
    except Exception as e:
        flash(f'Error adding product master: {str(e)}', 'danger')

    return redirect(url_for('hanaman_product_master'))

@app.route('/hanaman-inventory/product-master/edit/<int:product_id>', methods=['POST'])
@login_required
def hanaman_edit_product_master(product_id):
    """Edit existing product master"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        product_data = {
            'product_name': request.form.get('product_name', '').strip(),
            'category_id': int(request.form.get('category_id')),
            'supplier_id': int(request.form.get('supplier_id')),
            'unit': request.form.get('unit', '').strip(),
            'min_stock': int(request.form.get('min_stock', 5))
        }

        product = update_product_master(product_id, product_data)
        if product:
            flash(f'Product "{product.product_name}" updated successfully!', 'success')
        else:
            flash('Error updating product master', 'danger')

    except ValueError:
        flash('Invalid input: Please check your data', 'danger')
    except Exception as e:
        flash(f'Error updating product master: {str(e)}', 'danger')

    return redirect(url_for('hanaman_product_master'))

@app.route('/hanaman-inventory/product-master/delete/<int:product_id>', methods=['POST'])
@login_required
def hanaman_delete_product_master(product_id):
    """Delete product master (soft delete)"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        product = get_product_master_by_id(product_id)
        if product and delete_product_master(product_id):
            flash(f'Product "{product.product_name}" deleted successfully!', 'success')
        else:
            flash('Error deleting product master', 'danger')
    except Exception as e:
        flash(f'Error deleting product master: {str(e)}', 'danger')

    return redirect(url_for('hanaman_product_master'))

@app.route('/api/hanaman-inventory/product-master/<int:product_id>')
@login_required
def api_hanaman_get_product_master(product_id):
    """Get product master data as JSON for editing"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    product = get_product_master_by_id(product_id)
    if product:
        return jsonify({
            'id': product.id,
            'product_name': product.product_name,
            'category_id': product.category_id,
            'supplier_id': product.supplier_id,
            'unit': product.unit,
            'min_stock': product.min_stock,
            'is_active': product.is_active
        })
    return jsonify({'error': 'Product not found'}), 404

# Purchase CRUD Routes
@app.route('/hanaman-inventory/purchase/add', methods=['POST'])
@login_required
def hanaman_add_purchase():
    """Add new purchase"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        from datetime import datetime as dt
        
        purchase_data = {
            'purchase_order_number': request.form.get('purchase_order_number', '').strip(),
            'product_master_id': int(request.form.get('product_master_id')),
            'supplier_id': int(request.form.get('supplier_id')),
            'quantity': float(request.form.get('quantity')),
            'unit_price': float(request.form.get('unit_price')),
            'purchase_date': dt.strptime(request.form.get('purchase_date'), '%Y-%m-%d').date(),
            'received_date': dt.strptime(request.form.get('received_date'), '%Y-%m-%d').date() if request.form.get('received_date') else None,
            'status': request.form.get('status', 'pending'),
            'notes': request.form.get('notes', '').strip(),
            'invoice_number': request.form.get('invoice_number', '').strip()
        }

        # Validate required fields
        if not purchase_data['quantity'] or purchase_data['quantity'] <= 0:
            flash('Quantity must be greater than 0', 'danger')
            return redirect(url_for('hanaman_inventory_config'))

        if not purchase_data['unit_price'] or purchase_data['unit_price'] <= 0:
            flash('Unit price must be greater than 0', 'danger')
            return redirect(url_for('hanaman_inventory_config'))

        purchase = create_purchase(purchase_data)
        if purchase:
            flash(f'Purchase order "{purchase.purchase_order_number}" added successfully!', 'success')
        else:
            flash('Error adding purchase', 'danger')

    except ValueError as e:
        flash('Invalid input: Please check your data', 'danger')
    except Exception as e:
        flash(f'Error adding purchase: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory_config'))

@app.route('/hanaman-inventory/purchase/edit/<int:purchase_id>', methods=['POST'])
@login_required
def hanaman_edit_purchase(purchase_id):
    """Edit existing purchase"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        from datetime import datetime as dt
        
        purchase_data = {
            'product_master_id': int(request.form.get('product_master_id')),
            'supplier_id': int(request.form.get('supplier_id')),
            'quantity': float(request.form.get('quantity')),
            'unit_price': float(request.form.get('unit_price')),
            'purchase_date': dt.strptime(request.form.get('purchase_date'), '%Y-%m-%d').date(),
            'received_date': dt.strptime(request.form.get('received_date'), '%Y-%m-%d').date() if request.form.get('received_date') else None,
            'status': request.form.get('status', 'pending'),
            'notes': request.form.get('notes', '').strip(),
            'invoice_number': request.form.get('invoice_number', '').strip()
        }

        purchase = update_purchase(purchase_id, purchase_data)
        if purchase:
            flash(f'Purchase order "{purchase.purchase_order_number}" updated successfully!', 'success')
        else:
            flash('Error updating purchase', 'danger')

    except ValueError:
        flash('Invalid input: Please check your data', 'danger')
    except Exception as e:
        flash(f'Error updating purchase: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory_config'))

@app.route('/hanaman-inventory/purchase/delete/<int:purchase_id>', methods=['POST'])
@login_required
def hanaman_delete_purchase(purchase_id):
    """Delete purchase (soft delete)"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        purchase = get_purchase_by_id(purchase_id)
        if purchase and delete_purchase(purchase_id):
            flash(f'Purchase order "{purchase.purchase_order_number}" deleted successfully!', 'success')
        else:
            flash('Error deleting purchase', 'danger')
    except Exception as e:
        flash(f'Error deleting purchase: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory_config'))

@app.route('/api/hanaman-inventory/purchase/<int:purchase_id>')
@login_required
def api_hanaman_get_purchase(purchase_id):
    """Get purchase data as JSON for editing"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    purchase = get_purchase_by_id(purchase_id)
    if purchase:
        return jsonify({
            'id': purchase.id,
            'purchase_order_number': purchase.purchase_order_number,
            'product_master_id': purchase.product_master_id,
            'supplier_id': purchase.supplier_id,
            'quantity': purchase.quantity,
            'unit_price': purchase.unit_price,
            'total_amount': purchase.total_amount,
            'purchase_date': purchase.purchase_date.strftime('%Y-%m-%d'),
            'received_date': purchase.received_date.strftime('%Y-%m-%d') if purchase.received_date else '',
            'status': purchase.status,
            'notes': purchase.notes,
            'invoice_number': purchase.invoice_number,
            'is_active': purchase.is_active
        })
    return jsonify({'error': 'Purchase not found'}), 404

# Transaction CRUD Routes
@app.route('/hanaman-inventory/transaction/add', methods=['POST'])
@login_required
def hanaman_add_transaction():
    """Add new transaction"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        from datetime import datetime as dt
        
        transaction_data = {
            'transaction_number': request.form.get('transaction_number', '').strip(),
            'product_master_id': int(request.form.get('product_master_id')),
            'transaction_type': request.form.get('transaction_type'),
            'quantity': float(request.form.get('quantity')),
            'unit_cost': float(request.form.get('unit_cost', 0)),
            'transaction_date': dt.strptime(request.form.get('transaction_date'), '%Y-%m-%d').date(),
            'reason': request.form.get('reason', '').strip(),
            'reference_type': request.form.get('reference_type', '').strip(),
            'reference_id': request.form.get('reference_id', '').strip(),
            'reference_name': request.form.get('reference_name', '').strip(),
            'notes': request.form.get('notes', '').strip()
        }

        # Validate required fields
        if not transaction_data['quantity'] or transaction_data['quantity'] <= 0:
            flash('Quantity must be greater than 0', 'danger')
            return redirect(url_for('hanaman_inventory_config'))

        if not transaction_data['reason']:
            flash('Reason is required', 'danger')
            return redirect(url_for('hanaman_inventory_config'))

        transaction = create_transaction(transaction_data)
        if transaction:
            flash(f'Transaction "{transaction.transaction_number}" added successfully!', 'success')
        else:
            flash('Error adding transaction', 'danger')

    except ValueError as e:
        flash('Invalid input: Please check your data', 'danger')
    except Exception as e:
        flash(f'Error adding transaction: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory_config'))

@app.route('/hanaman-inventory/transaction/edit/<int:transaction_id>', methods=['POST'])
@login_required
def hanaman_edit_transaction(transaction_id):
    """Edit existing transaction"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        from datetime import datetime as dt
        
        transaction_data = {
            'product_master_id': int(request.form.get('product_master_id')),
            'transaction_type': request.form.get('transaction_type'),
            'quantity': float(request.form.get('quantity')),
            'unit_cost': float(request.form.get('unit_cost', 0)),
            'transaction_date': dt.strptime(request.form.get('transaction_date'), '%Y-%m-%d').date(),
            'reason': request.form.get('reason', '').strip(),
            'reference_type': request.form.get('reference_type', '').strip(),
            'reference_id': request.form.get('reference_id', '').strip(),
            'reference_name': request.form.get('reference_name', '').strip(),
            'notes': request.form.get('notes', '').strip()
        }

        transaction = update_transaction(transaction_id, transaction_data)
        if transaction:
            flash(f'Transaction "{transaction.transaction_number}" updated successfully!', 'success')
        else:
            flash('Error updating transaction', 'danger')

    except ValueError:
        flash('Invalid input: Please check your data', 'danger')
    except Exception as e:
        flash(f'Error updating transaction: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory_config'))

@app.route('/hanaman-inventory/transaction/delete/<int:transaction_id>', methods=['POST'])
@login_required
def hanaman_delete_transaction(transaction_id):
    """Delete transaction (soft delete)"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        transaction = get_transaction_by_id(transaction_id)
        if transaction and delete_transaction(transaction_id):
            flash(f'Transaction "{transaction.transaction_number}" deleted successfully!', 'success')
        else:
            flash('Error deleting transaction', 'danger')
    except Exception as e:
        flash(f'Error deleting transaction: {str(e)}', 'danger')

    return redirect(url_for('hanaman_inventory_config'))

@app.route('/api/hanaman-inventory/transaction/<int:transaction_id>')
@login_required
def api_hanaman_get_transaction(transaction_id):
    """Get transaction data as JSON for editing"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    transaction = get_transaction_by_id(transaction_id)
    if transaction:
        return jsonify({
            'id': transaction.id,
            'transaction_number': transaction.transaction_number,
            'product_master_id': transaction.product_master_id,
            'transaction_type': transaction.transaction_type,
            'quantity': transaction.quantity,
            'unit_cost': transaction.unit_cost,
            'total_cost': transaction.total_cost,
            'transaction_date': transaction.transaction_date.strftime('%Y-%m-%d'),
            'reason': transaction.reason,
            'reference_type': transaction.reference_type,
            'reference_id': transaction.reference_id,
            'reference_name': transaction.reference_name,
            'notes': transaction.notes,
            'is_active': transaction.is_active
        })
    return jsonify({'error': 'Transaction not found'}), 404