"""
Inventory views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app
from forms import InventoryForm
from .inventory_queries import (
    get_all_inventory, get_inventory_by_id, get_low_stock_items, 
    get_expiring_items, get_inventory_categories, search_inventory, 
    create_inventory, update_inventory, delete_inventory, update_stock
)

@app.route('/inventory')
@login_required
def inventory():
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    search_query = request.args.get('search', '')
    filter_type = request.args.get('filter', 'all')
    
    if search_query:
        inventory_list = search_inventory(search_query)
    elif filter_type == 'low_stock':
        inventory_list = get_low_stock_items()
    elif filter_type == 'expiring':
        inventory_list = get_expiring_items()
    else:
        inventory_list = get_all_inventory()
    
    categories = get_inventory_categories()
    form = InventoryForm()
    form.category_id.choices = [(c.id, c.display_name) for c in categories]
    
    return render_template('inventory.html', 
                         inventory=inventory_list,
                         form=form,
                         categories=categories,
                         search_query=search_query,
                         filter_type=filter_type)

@app.route('/inventory/create', methods=['POST'])
@app.route('/inventory/add', methods=['POST'])
@app.route('/add_inventory', methods=['POST'])
@login_required
def create_inventory_route():
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = InventoryForm()
    categories = get_inventory_categories()
    form.category_id.choices = [(c.id, c.display_name) for c in categories]
    
    if form.validate_on_submit():
        inventory_data = {
            'name': form.name.data,
            'description': form.description.data or '',
            'category_id': form.category_id.data,
            'current_stock': form.current_stock.data,
            'min_stock_level': form.min_stock_level.data,
            'cost_price': form.cost_price.data,
            'selling_price': form.selling_price.data,
            'expiry_date': form.expiry_date.data,
            'supplier': form.supplier.data or '',
            'is_active': True
        }
        
        create_inventory(inventory_data)
        flash('Inventory item created successfully!', 'success')
    else:
        flash('Error creating inventory item. Please check your input.', 'danger')
    
    return redirect(url_for('inventory'))

@app.route('/inventory/update/<int:id>', methods=['POST'])
@login_required
def update_inventory_route(id):
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    inventory_item = get_inventory_by_id(id)
    if not inventory_item:
        flash('Inventory item not found', 'danger')
        return redirect(url_for('inventory'))
    
    form = InventoryForm()
    categories = get_inventory_categories()
    form.category_id.choices = [(c.id, c.display_name) for c in categories]
    
    if form.validate_on_submit():
        inventory_data = {
            'name': form.name.data,
            'description': form.description.data or '',
            'category_id': form.category_id.data,
            'current_stock': form.current_stock.data,
            'min_stock_level': form.min_stock_level.data,
            'cost_price': form.cost_price.data,
            'selling_price': form.selling_price.data,
            'expiry_date': form.expiry_date.data,
            'supplier': form.supplier.data or ''
        }
        
        update_inventory(id, inventory_data)
        flash('Inventory item updated successfully!', 'success')
    else:
        flash('Error updating inventory item. Please check your input.', 'danger')
    
    return redirect(url_for('inventory'))

@app.route('/inventory/delete/<int:id>', methods=['POST'])
@login_required
def delete_inventory_route(id):
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    if delete_inventory(id):
        flash('Inventory item deleted successfully!', 'success')
    else:
        flash('Error deleting inventory item', 'danger')
    
    return redirect(url_for('inventory'))

@app.route('/inventory/stock-update/<int:id>', methods=['POST'])
@login_required
def update_stock_route(id):
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    quantity_change = request.form.get('quantity_change', type=int)
    if quantity_change is not None:
        inventory_item = update_stock(id, quantity_change)
        if inventory_item:
            flash(f'Stock updated. New quantity: {inventory_item.current_stock}', 'success')
        else:
            flash('Error updating stock', 'danger')
    else:
        flash('Invalid quantity change', 'danger')
    
    return redirect(url_for('inventory'))