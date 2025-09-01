"""
Inventory Category Management Views
CRUD operations for inventory categories
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import Category

def get_all_inventory_categories():
    """Get all inventory categories ordered by sort_order"""
    return Category.query.filter_by(category_type='inventory').order_by(
        Category.sort_order, Category.display_name
    ).all()

def get_inventory_category_by_id(category_id):
    """Get inventory category by ID"""
    return Category.query.filter_by(id=category_id, category_type='inventory').first()

def create_inventory_category(data):
    """Create new inventory category"""
    category = Category(
        name=data['name'],
        display_name=data['display_name'],
        description=data.get('description'),
        category_type='inventory',
        color=data.get('color', '#007bff'),
        icon=data.get('icon', 'fas fa-boxes'),
        is_active=data.get('is_active', True),
        sort_order=data.get('sort_order', 0)
    )
    
    db.session.add(category)
    db.session.commit()
    return category

def update_inventory_category(category_id, data):
    """Update inventory category"""
    category = get_inventory_category_by_id(category_id)
    if not category:
        raise ValueError("Category not found")
    
    for key, value in data.items():
        if hasattr(category, key):
            setattr(category, key, value)
    
    db.session.commit()
    return category

@app.route('/inventory-categories')
@login_required
def inventory_categories():
    """Inventory Category Management with CRUD operations"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    categories = get_all_inventory_categories()
    
    return render_template('inventory_categories.html', 
                         categories=categories)

@app.route('/inventory-categories/create', methods=['POST'])
@login_required
def create_inventory_category_route():
    """Create new inventory category"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('inventory_categories'))
    
    try:
        # Get form data directly from request
        name = request.form.get('name', '').strip()
        display_name = request.form.get('display_name', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', '#28a745')
        icon = request.form.get('icon', 'fas fa-boxes')
        sort_order = int(request.form.get('sort_order', 0))
        is_active = 'is_active' in request.form
        
        # Basic validation
        if not name or not display_name:
            flash('Category name and display name are required', 'danger')
            return redirect(url_for('inventory_categories'))
        
        # Create category
        category = create_inventory_category({
            'name': name.lower().replace(' ', '_'),
            'display_name': display_name,
            'description': description,
            'color': color,
            'icon': icon,
            'is_active': is_active,
            'sort_order': sort_order
        })
        flash(f'Inventory category "{category.display_name}" created successfully', 'success')
        
    except Exception as e:
        flash(f'Error creating category: {str(e)}', 'danger')
    
    return redirect(url_for('inventory_categories'))

@app.route('/inventory-categories/<int:category_id>/edit', methods=['POST'])
@login_required
def edit_inventory_category(category_id):
    """Edit inventory category"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('inventory_categories'))
    
    category = get_inventory_category_by_id(category_id)
    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('inventory_categories'))
    
    try:
        # Get form data directly from request
        name = request.form.get('name', '').strip()
        display_name = request.form.get('display_name', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', '#28a745')
        icon = request.form.get('icon', 'fas fa-boxes')
        sort_order = int(request.form.get('sort_order', 0))
        is_active = 'is_active' in request.form
        
        # Basic validation
        if not name or not display_name:
            flash('Category name and display name are required', 'danger')
            return redirect(url_for('inventory_categories'))
        
        # Update category
        update_inventory_category(category_id, {
            'name': name.lower().replace(' ', '_'),
            'display_name': display_name,
            'description': description,
            'color': color,
            'icon': icon,
            'is_active': is_active,
            'sort_order': sort_order
        })
        flash(f'Inventory category "{category.display_name}" updated successfully', 'success')
        
    except Exception as e:
        flash(f'Error updating category: {str(e)}', 'danger')
    
    return redirect(url_for('inventory_categories'))

@app.route('/inventory-categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_inventory_category(category_id):
    """Delete inventory category"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('inventory_categories'))
    
    category = get_inventory_category_by_id(category_id)
    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('inventory_categories'))
    
    try:
        # Check if category is being used by any inventory items
        from models import SimpleInventoryItem
        items_using_category = SimpleInventoryItem.query.filter_by(category=category.name).count()
        
        if items_using_category > 0:
            flash(f'Cannot delete category "{category.display_name}" as it is being used by {items_using_category} inventory item(s)', 'danger')
            return redirect(url_for('inventory_categories'))
        
        category_name = category.display_name
        db.session.delete(category)
        db.session.commit()
        flash(f'Inventory category "{category_name}" deleted successfully', 'success')
        
    except Exception as e:
        flash(f'Error deleting category: {str(e)}', 'danger')
    
    return redirect(url_for('inventory_categories'))

@app.route('/inventory-categories/<int:category_id>/toggle', methods=['POST'])
@login_required
def toggle_inventory_category(category_id):
    """Toggle inventory category active status"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('inventory_categories'))
    
    category = get_inventory_category_by_id(category_id)
    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('inventory_categories'))
    
    try:
        category.is_active = not category.is_active
        db.session.commit()
        
        status = "activated" if category.is_active else "deactivated"
        flash(f'Inventory category "{category.display_name}" {status} successfully', 'success')
        
    except Exception as e:
        flash(f'Error updating category status: {str(e)}', 'danger')
    
    return redirect(url_for('inventory_categories'))