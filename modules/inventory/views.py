"""
Comprehensive Inventory Management Views
Stock tracking, supplier management, and order processing
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_required, current_user
from datetime import datetime, date
import csv
import io
from app import app, db
from .models import (
    InventoryProduct, InventoryCategory, Supplier, StockMovement,
    PurchaseOrder, PurchaseOrderItem, InventoryAlert
)
from .queries import (
    get_all_products, get_product_by_id, create_product, update_product, delete_product,
    get_all_categories, get_category_by_id, create_category, update_category, delete_category,
    get_all_suppliers, get_supplier_by_id, create_supplier, update_supplier,
    get_low_stock_products, get_out_of_stock_products, get_products_needing_reorder,
    search_products, update_stock, add_stock, remove_stock, get_stock_movements,
    create_purchase_order, get_purchase_orders, get_purchase_order_by_id,
    get_inventory_dashboard_stats, get_active_alerts, check_stock_alerts
)

# ============ MAIN INVENTORY DASHBOARD ============

@app.route('/inventory')
@login_required
def inventory_dashboard():
    """Main inventory dashboard with comprehensive overview"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get dashboard statistics
    stats = get_inventory_dashboard_stats()
    
    # Get critical alerts
    critical_alerts = [alert for alert in get_active_alerts() if alert.severity == 'critical']
    
    # Recent activities
    recent_movements = get_stock_movements(limit=5)
    
    # Get data for all tabs
    categories = get_all_categories()
    purchase_orders = get_purchase_orders()
    
    return render_template('inventory/dashboard.html',
                         stats=stats,
                         critical_alerts=critical_alerts,
                         recent_movements=recent_movements,
                         categories=categories,
                         purchase_orders=purchase_orders)

# ============ PRODUCT MANAGEMENT ============

@app.route('/inventory/products')
@login_required
def inventory_products():
    """Product catalog management"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get filter parameters
    category_filter = request.args.get('category')
    status_filter = request.args.get('status', 'all')
    search_term = request.args.get('search', '')
    
    # Apply filters
    if search_term:
        products = search_products(search_term)
    elif status_filter == 'low_stock':
        products = get_low_stock_products()
    elif status_filter == 'out_of_stock':
        products = get_out_of_stock_products()
    elif status_filter == 'reorder':
        products = get_products_needing_reorder()
    else:
        products = get_all_products()
    
    # Apply category filter
    if category_filter and category_filter != 'all':
        products = [p for p in products if str(p.category_id) == category_filter]
    
    categories = get_all_categories()
    suppliers = get_all_suppliers()
    
    return render_template('inventory/products.html',
                         products=products,
                         categories=categories,
                         suppliers=suppliers,
                         current_filters={
                             'category': category_filter,
                             'status': status_filter,
                             'search': search_term
                         })

@app.route('/inventory/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """Add new product"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            product_data = {
                'sku': request.form.get('sku').strip(),
                'name': request.form.get('name').strip(),
                'description': request.form.get('description', '').strip(),
                'category_id': int(request.form.get('category_id')) if request.form.get('category_id') else None,
                'supplier_id': int(request.form.get('supplier_id')) if request.form.get('supplier_id') else None,
                'current_stock': float(request.form.get('current_stock', 0)),
                'min_stock_level': float(request.form.get('min_stock_level', 10)),
                'max_stock_level': float(request.form.get('max_stock_level', 100)),
                'reorder_point': float(request.form.get('reorder_point', 20)),
                'cost_price': float(request.form.get('cost_price', 0)),
                'selling_price': float(request.form.get('selling_price', 0)),
                'unit_of_measure': request.form.get('unit_of_measure', 'pcs').strip(),
                'barcode': request.form.get('barcode', '').strip(),
                'location': request.form.get('location', '').strip(),
                'is_service_item': 'is_service_item' in request.form,
                'is_retail_item': 'is_retail_item' in request.form
            }
            
            # Validation
            if not product_data['name']:
                flash('Product name is required', 'danger')
                return redirect(request.url)
            
            if not product_data['sku']:
                flash('SKU is required', 'danger')
                return redirect(request.url)
            
            product = create_product(product_data)
            
            # Create initial stock movement if stock > 0
            if product.current_stock > 0:
                update_stock(product.id, product.current_stock, 'in', 
                           'Initial stock', 'manual', None, current_user.id)
            
            flash(f'Product "{product.name}" added successfully!', 'success')
            return redirect(url_for('inventory_products'))
            
        except ValueError:
            flash('Invalid input values. Please check your data.', 'danger')
        except Exception as e:
            flash(f'Error adding product: {str(e)}', 'danger')
    
    categories = get_all_categories()
    suppliers = get_all_suppliers()
    return render_template('inventory/product_form.html',
                         categories=categories,
                         suppliers=suppliers,
                         action='add')

@app.route('/inventory/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Edit existing product"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('inventory_products'))
    
    if request.method == 'POST':
        try:
            old_stock = product.current_stock
            
            product_data = {
                'name': request.form.get('name').strip(),
                'description': request.form.get('description', '').strip(),
                'category_id': int(request.form.get('category_id')) if request.form.get('category_id') else None,
                'supplier_id': int(request.form.get('supplier_id')) if request.form.get('supplier_id') else None,
                'min_stock_level': float(request.form.get('min_stock_level', 10)),
                'max_stock_level': float(request.form.get('max_stock_level', 100)),
                'reorder_point': float(request.form.get('reorder_point', 20)),
                'cost_price': float(request.form.get('cost_price', 0)),
                'selling_price': float(request.form.get('selling_price', 0)),
                'unit_of_measure': request.form.get('unit_of_measure', 'pcs').strip(),
                'barcode': request.form.get('barcode', '').strip(),
                'location': request.form.get('location', '').strip(),
                'is_service_item': 'is_service_item' in request.form,
                'is_retail_item': 'is_retail_item' in request.form
            }
            
            updated_product = update_product(product_id, product_data)
            if updated_product:
                flash(f'Product "{updated_product.name}" updated successfully!', 'success')
                return redirect(url_for('inventory_products'))
            else:
                flash('Error updating product', 'danger')
                
        except ValueError:
            flash('Invalid input values. Please check your data.', 'danger')
        except Exception as e:
            flash(f'Error updating product: {str(e)}', 'danger')
    
    categories = get_all_categories()
    suppliers = get_all_suppliers()
    return render_template('inventory/product_form.html',
                         product=product,
                         categories=categories,
                         suppliers=suppliers,
                         action='edit')

@app.route('/inventory/products/<int:product_id>/view')
@login_required
def view_product(product_id):
    """View product details with stock history"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('inventory_products'))
    
    # Get stock movement history
    movements = get_stock_movements(product_id, limit=20)
    
    return render_template('inventory/product_details.html',
                         product=product,
                         movements=movements)

# ============ CATEGORY MANAGEMENT ============

@app.route('/inventory/categories')
@login_required
def inventory_categories():
    """Category management with table view"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    categories = get_all_categories()
    return render_template('inventory/categories.html', categories=categories)

@app.route('/inventory/categories/add', methods=['GET', 'POST'])
@login_required
def add_inventory_category():
    """Add new category"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            category_data = {
                'name': request.form.get('name', '').strip(),
                'description': request.form.get('description', '').strip(),
                'color_code': request.form.get('color_code', '#007bff').strip()
            }
            
            if not category_data['name']:
                flash('Category name is required', 'danger')
                return redirect(request.url)
            
            category = create_category(category_data)
            flash(f'Category "{category.name}" added successfully!', 'success')
            return redirect(url_for('inventory_categories'))
            
        except Exception as e:
            flash(f'Error adding category: {str(e)}', 'danger')
    
    return render_template('inventory/category_form.html', action='add')

@app.route('/inventory/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_inventory_category(category_id):
    """Edit existing category"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    category = get_category_by_id(category_id)
    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('inventory_categories'))
    
    if request.method == 'POST':
        try:
            category_data = {
                'name': request.form.get('name', '').strip(),
                'description': request.form.get('description', '').strip(),
                'color_code': request.form.get('color_code', '#007bff').strip()
            }
            
            if not category_data['name']:
                flash('Category name is required', 'danger')
                return redirect(request.url)
            
            updated_category = update_category(category_id, category_data)
            if updated_category:
                flash(f'Category "{updated_category.name}" updated successfully!', 'success')
                return redirect(url_for('inventory_categories'))
            else:
                flash('Error updating category', 'danger')
                
        except Exception as e:
            flash(f'Error updating category: {str(e)}', 'danger')
    
    return render_template('inventory/category_form.html', 
                         category=category, 
                         action='edit')

@app.route('/inventory/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category_route(category_id):
    """Delete category"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    category = get_category_by_id(category_id)
    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('inventory_categories'))
    
    try:
        # Check if category has products
        if category.products:
            flash(f'Cannot delete category "{category.name}" because it has {len(category.products)} associated products', 'danger')
            return redirect(url_for('inventory_categories'))
        
        if delete_category(category_id):
            flash(f'Category "{category.name}" deleted successfully!', 'success')
        else:
            flash('Error deleting category', 'danger')
            
    except Exception as e:
        flash(f'Error deleting category: {str(e)}', 'danger')
    
    return redirect(url_for('inventory_categories'))

# ============ STOCK MANAGEMENT ============

@app.route('/inventory/products/<int:product_id>/stock', methods=['POST'])
@login_required
def adjust_stock(product_id):
    """Adjust product stock levels"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('inventory_products'))
    
    try:
        adjustment_type = request.form.get('adjustment_type')  # set, add, remove
        quantity = float(request.form.get('quantity', 0))
        reason = request.form.get('reason', 'Stock adjustment').strip()
        
        if adjustment_type == 'set':
            updated_product = update_stock(product_id, quantity, 'adjustment', 
                                         reason, 'manual', None, current_user.id)
            action_msg = f'Stock set to {quantity}'
        elif adjustment_type == 'add':
            updated_product = add_stock(product_id, quantity, reason, 
                                      'manual', None, 0, current_user.id)
            action_msg = f'{quantity} units added'
        elif adjustment_type == 'remove':
            updated_product = remove_stock(product_id, quantity, reason, 
                                         'manual', None, current_user.id)
            action_msg = f'{quantity} units removed'
        else:
            flash('Invalid adjustment type', 'danger')
            return redirect(request.referrer or url_for('inventory_products'))
        
        if updated_product:
            flash(f'{product.name}: {action_msg}. New stock: {updated_product.current_stock}', 'success')
        else:
            flash('Error adjusting stock', 'danger')
            
    except ValueError:
        flash('Invalid quantity value', 'danger')
    except Exception as e:
        flash(f'Error adjusting stock: {str(e)}', 'danger')
    
    return redirect(request.referrer or url_for('inventory_products'))

@app.route('/inventory/stock-movements')
@login_required
def stock_movements():
    """View all stock movements with filtering"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    product_id = request.args.get('product_id', type=int)
    limit = request.args.get('limit', 50, type=int)
    
    movements = get_stock_movements(product_id, limit)
    products = get_all_products()  # For filter dropdown
    
    return render_template('inventory/stock_movements.html',
                         movements=movements,
                         products=products,
                         current_product_id=product_id)

# ============ SUPPLIER MANAGEMENT ============

@app.route('/inventory/suppliers')
@login_required
def suppliers():
    """Supplier management"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    suppliers = get_all_suppliers()
    return render_template('inventory/suppliers.html', suppliers=suppliers)

@app.route('/inventory/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    """Add new supplier"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            supplier_data = {
                'name': request.form.get('name').strip(),
                'contact_person': request.form.get('contact_person', '').strip(),
                'email': request.form.get('email', '').strip(),
                'phone': request.form.get('phone', '').strip(),
                'address': request.form.get('address', '').strip(),
                'city': request.form.get('city', '').strip(),
                'state': request.form.get('state', '').strip(),
                'postal_code': request.form.get('postal_code', '').strip(),
                'country': request.form.get('country', 'United States').strip(),
                'tax_id': request.form.get('tax_id', '').strip(),
                'payment_terms': request.form.get('payment_terms', 'Net 30').strip(),
                'credit_limit': float(request.form.get('credit_limit', 0)),
                'rating': int(request.form.get('rating', 5))
            }
            
            if not supplier_data['name']:
                flash('Supplier name is required', 'danger')
                return redirect(request.url)
            
            supplier = create_supplier(supplier_data)
            flash(f'Supplier "{supplier.name}" added successfully!', 'success')
            return redirect(url_for('suppliers'))
            
        except ValueError:
            flash('Invalid input values. Please check your data.', 'danger')
        except Exception as e:
            flash(f'Error adding supplier: {str(e)}', 'danger')
    
    return render_template('inventory/supplier_form.html', action='add')

@app.route('/inventory/suppliers/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    """Edit existing supplier"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    supplier = get_supplier_by_id(supplier_id)
    if not supplier:
        flash('Supplier not found', 'danger')
        return redirect(url_for('suppliers'))
    
    if request.method == 'POST':
        try:
            supplier_data = {
                'name': request.form.get('name').strip(),
                'contact_person': request.form.get('contact_person', '').strip(),
                'email': request.form.get('email', '').strip(),
                'phone': request.form.get('phone', '').strip(),
                'address': request.form.get('address', '').strip(),
                'city': request.form.get('city', '').strip(),
                'state': request.form.get('state', '').strip(),
                'postal_code': request.form.get('postal_code', '').strip(),
                'country': request.form.get('country', 'United States').strip(),
                'tax_id': request.form.get('tax_id', '').strip(),
                'payment_terms': request.form.get('payment_terms', 'Net 30').strip(),
                'credit_limit': float(request.form.get('credit_limit', 0)),
                'rating': int(request.form.get('rating', 5))
            }
            
            updated_supplier = update_supplier(supplier_id, supplier_data)
            if updated_supplier:
                flash(f'Supplier "{updated_supplier.name}" updated successfully!', 'success')
                return redirect(url_for('suppliers'))
            else:
                flash('Error updating supplier', 'danger')
                
        except ValueError:
            flash('Invalid input values. Please check your data.', 'danger')
        except Exception as e:
            flash(f'Error updating supplier: {str(e)}', 'danger')
    
    return render_template('inventory/supplier_form.html',
                         supplier=supplier,
                         action='edit')

# ============ PURCHASE ORDER MANAGEMENT ============

@app.route('/inventory/orders')
@login_required
def purchase_orders():
    """Purchase order management"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    status_filter = request.args.get('status', 'all')
    
    if status_filter != 'all':
        orders = get_purchase_orders(status_filter)
    else:
        orders = get_purchase_orders()
    
    return render_template('inventory/purchase_orders.html',
                         orders=orders,
                         current_status=status_filter)

@app.route('/inventory/orders/create', methods=['GET', 'POST'])
@login_required
def create_order():
    """Create new purchase order"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            # Get order data
            po_data = {
                'supplier_id': int(request.form.get('supplier_id')),
                'expected_delivery': datetime.strptime(request.form.get('expected_delivery'), '%Y-%m-%d').date() if request.form.get('expected_delivery') else None,
                'delivery_address': request.form.get('delivery_address', '').strip(),
                'notes': request.form.get('notes', '').strip(),
                'terms_and_conditions': request.form.get('terms_and_conditions', '').strip(),
                'created_by': current_user.id
            }
            
            # Get items data
            items_data = []
            product_ids = request.form.getlist('product_id[]')
            quantities = request.form.getlist('quantity[]')
            unit_costs = request.form.getlist('unit_cost[]')
            
            for i, product_id in enumerate(product_ids):
                if product_id and quantities[i] and unit_costs[i]:
                    quantity = float(quantities[i])
                    unit_cost = float(unit_costs[i])
                    items_data.append({
                        'product_id': int(product_id),
                        'quantity_ordered': quantity,
                        'unit_cost': unit_cost,
                        'total_cost': quantity * unit_cost
                    })
            
            if not items_data:
                flash('At least one item is required', 'danger')
                return redirect(request.url)
            
            po = create_purchase_order(po_data, items_data)
            flash(f'Purchase Order {po.po_number} created successfully!', 'success')
            return redirect(url_for('purchase_orders'))
            
        except ValueError:
            flash('Invalid input values. Please check your data.', 'danger')
        except Exception as e:
            flash(f'Error creating purchase order: {str(e)}', 'danger')
    
    suppliers = get_all_suppliers()
    products = get_all_products()
    
    return render_template('inventory/order_form.html',
                         suppliers=suppliers,
                         products=products,
                         action='create')

# ============ ALERTS AND REPORTING ============

@app.route('/inventory/alerts')
@login_required
def inventory_alerts():
    """View inventory alerts"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    alerts = get_active_alerts()
    return render_template('inventory/alerts.html', alerts=alerts)

@app.route('/inventory/reports')
@login_required
def inventory_reports():
    """Inventory reporting dashboard"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    stats = get_inventory_dashboard_stats()
    
    return render_template('inventory/reports.html', stats=stats)

@app.route('/inventory/export/products')
@login_required
def export_products():
    """Export products to CSV"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    products = get_all_products()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'SKU', 'Name', 'Category', 'Supplier', 'Current Stock', 'Min Level',
        'Max Level', 'Reorder Point', 'Cost Price', 'Selling Price', 'Unit',
        'Location', 'Status', 'Stock Value'
    ])
    
    # Write data
    for product in products:
        writer.writerow([
            product.sku,
            product.name,
            product.category.name if product.category else '',
            product.supplier.name if product.supplier else '',
            product.current_stock,
            product.min_stock_level,
            product.max_stock_level,
            product.reorder_point,
            product.cost_price,
            product.selling_price,
            product.unit_of_measure,
            product.location,
            product.stock_status,
            product.stock_value
        ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-disposition": f"attachment; filename=inventory_products_{date.today().strftime('%Y%m%d')}.csv"}
    )

# ============ API ENDPOINTS ============

@app.route('/api/inventory/product/<int:product_id>')
@login_required
def api_get_product(product_id):
    """Get product data as JSON"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403
    
    product = get_product_by_id(product_id)
    if product:
        return jsonify({
            'id': product.id,
            'sku': product.sku,
            'name': product.name,
            'current_stock': float(product.current_stock),
            'min_stock_level': float(product.min_stock_level),
            'cost_price': float(product.cost_price),
            'selling_price': float(product.selling_price),
            'unit_of_measure': product.unit_of_measure,
            'stock_status': product.stock_status
        })
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/inventory/dashboard-stats')
@login_required
def api_dashboard_stats():
    """Get dashboard statistics as JSON"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403
    
    stats = get_inventory_dashboard_stats()
    return jsonify(stats)