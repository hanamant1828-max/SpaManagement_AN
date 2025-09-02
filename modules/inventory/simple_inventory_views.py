
"""
Simple Inventory Management System Views
Ready for fresh implementation
"""

from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import app, db

@app.route('/simple_inventory')
@login_required
def simple_inventory():
    """Fresh inventory management system - ready for your new plan"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Ready for fresh implementation
    message = """
    🎯 Fresh Inventory System Ready!
    
    All previous inventory data has been cleared.
    You can now implement your new inventory plan:
    
    ✅ Clean database slate
    ✅ Ready for new models
    ✅ Fresh implementation approach
    
    Please share your new inventory plan and I'll implement it!
    """
    
    return render_template('simple_inventory.html', 
                         items=[], 
                         message=message,
                         fresh_start=True)

@app.route('/professional_inventory')
@login_required
def professional_inventory():
    """Professional inventory management system"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        from models import InventoryProduct, InventoryCategory, InventorySupplier
        
        # Get all inventory data
        products = InventoryProduct.query.filter_by(is_active=True).all()
        categories = InventoryCategory.query.filter_by(is_active=True).all()
        suppliers = InventorySupplier.query.filter_by(is_active=True).all()
        
        # Calculate stats
        total_products = len(products)
        total_stock_value = sum(p.current_stock * p.unit_cost for p in products if p.current_stock and p.unit_cost)
        low_stock_count = sum(1 for p in products if p.current_stock <= p.reorder_level)
        
        return render_template('professional_inventory.html', 
                             products=products,
                             categories=categories,
                             suppliers=suppliers,
                             total_products=total_products,
                             total_stock_value=total_stock_value,
                             low_stock_count=low_stock_count)
    except Exception as e:
        print(f"Error loading professional inventory: {e}")
        return render_template('professional_inventory.html', 
                             products=[],
                             categories=[],
                             suppliers=[],
                             total_products=0,
                             total_stock_value=0,
                             low_stock_count=0)
