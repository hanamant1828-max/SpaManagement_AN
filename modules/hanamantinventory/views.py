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
    get_all_item_templates, get_item_template_by_id, create_item_template, update_item_template, delete_item_template
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
    """Configuration page with categories, suppliers, and item templates"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    categories = get_all_categories()
    suppliers = get_all_suppliers()
    item_templates = get_all_item_templates()
    
    return render_template('hanaman_config.html', 
                         categories=categories,
                         suppliers=suppliers,
                         item_templates=item_templates)

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

# Item Template CRUD operations
@app.route('/hanaman-inventory/template/add', methods=['POST'])
@login_required
def hanaman_add_template():
    """Add new item template"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        template_data = {
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip(),
            'category_id': int(request.form.get('category_id')) if request.form.get('category_id') else None,
            'default_unit': request.form.get('default_unit', 'pcs').strip(),
            'default_min_stock': float(request.form.get('default_min_stock', 5)),
            'default_max_stock': float(request.form.get('default_max_stock', 100)),
            'estimated_cost': float(request.form.get('estimated_cost', 0)),
        }
        
        if not template_data['name']:
            flash('Template name is required', 'danger')
            return redirect(url_for('hanaman_inventory_config'))
        
        template = create_item_template(template_data)
        if template:
            flash(f'Item template "{template.name}" added successfully!', 'success')
        else:
            flash('Error adding item template', 'danger')
            
    except ValueError:
        flash('Invalid input: Please check your data', 'danger')
    except Exception as e:
        flash(f'Error adding item template: {str(e)}', 'danger')
    
    return redirect(url_for('hanaman_inventory_config'))

@app.route('/hanaman-inventory/template/edit/<int:template_id>', methods=['POST'])
@login_required
def hanaman_edit_template(template_id):
    """Edit existing item template"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        template_data = {
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip(),
            'category_id': int(request.form.get('category_id')) if request.form.get('category_id') else None,
            'default_unit': request.form.get('default_unit', 'pcs').strip(),
            'default_min_stock': float(request.form.get('default_min_stock', 5)),
            'default_max_stock': float(request.form.get('default_max_stock', 100)),
            'estimated_cost': float(request.form.get('estimated_cost', 0)),
        }
        
        template = update_item_template(template_id, template_data)
        if template:
            flash(f'Item template "{template.name}" updated successfully!', 'success')
        else:
            flash('Error updating item template', 'danger')
            
    except ValueError:
        flash('Invalid input: Please check your data', 'danger')
    except Exception as e:
        flash(f'Error updating item template: {str(e)}', 'danger')
    
    return redirect(url_for('hanaman_inventory_config'))

@app.route('/hanaman-inventory/template/delete/<int:template_id>', methods=['POST'])
@login_required
def hanaman_delete_template(template_id):
    """Delete item template"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        template = get_item_template_by_id(template_id)
        if template and delete_item_template(template_id):
            flash(f'Item template "{template.name}" deleted successfully!', 'success')
        else:
            flash('Error deleting item template', 'danger')
    except Exception as e:
        flash(f'Error deleting item template: {str(e)}', 'danger')
    
    return redirect(url_for('hanaman_inventory_config'))