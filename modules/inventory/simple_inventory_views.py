
"""
Simple Inventory Management System Views
Ready for fresh implementation
"""

from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import app, db
from datetime import datetime

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

# CRUD Operations for Products
@app.route('/inventory/product/add', methods=['GET', 'POST'])
@login_required
def add_inventory_product():
    """Add new inventory product"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            from models import InventoryProduct, InventoryCategory, InventorySupplier
            
            # Create new product
            product = InventoryProduct(
                product_code=request.form.get('product_code'),
                name=request.form.get('name'),
                description=request.form.get('description'),
                category_id=request.form.get('category_id') if request.form.get('category_id') else None,
                supplier_id=request.form.get('supplier_id') if request.form.get('supplier_id') else None,
                unit=request.form.get('unit', 'pcs'),
                unit_cost=float(request.form.get('unit_cost', 0)),
                selling_price=float(request.form.get('selling_price', 0)),
                reorder_level=int(request.form.get('reorder_level', 0)),
                max_stock_level=int(request.form.get('max_stock_level', 0)) if request.form.get('max_stock_level') else None,
                current_stock=float(request.form.get('current_stock', 0)),
                barcode=request.form.get('barcode'),
                is_batch_tracked=bool(request.form.get('is_batch_tracked')),
                is_expiry_tracked=bool(request.form.get('is_expiry_tracked')),
                created_by=current_user.username
            )
            
            db.session.add(product)
            db.session.commit()
            
            flash('Product added successfully!', 'success')
            return redirect(url_for('professional_inventory'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding product: {str(e)}', 'danger')
            print(f"Error adding product: {e}")
    
    # GET request - show form
    from models import InventoryCategory, InventorySupplier
    categories = InventoryCategory.query.filter_by(is_active=True).all()
    suppliers = InventorySupplier.query.filter_by(is_active=True).all()
    
    return render_template('add_inventory_product.html', 
                         categories=categories, 
                         suppliers=suppliers)

@app.route('/inventory/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_inventory_product(product_id):
    """Edit inventory product"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    from models import InventoryProduct, InventoryCategory, InventorySupplier
    product = InventoryProduct.query.get_or_404(product_id)
    
    if request.method == 'POST':
        try:
            # Update product fields
            product.product_code = request.form.get('product_code')
            product.name = request.form.get('name')
            product.description = request.form.get('description')
            product.category_id = request.form.get('category_id') if request.form.get('category_id') else None
            product.supplier_id = request.form.get('supplier_id') if request.form.get('supplier_id') else None
            product.unit = request.form.get('unit', 'pcs')
            product.unit_cost = float(request.form.get('unit_cost', 0))
            product.selling_price = float(request.form.get('selling_price', 0))
            product.reorder_level = int(request.form.get('reorder_level', 0))
            product.max_stock_level = int(request.form.get('max_stock_level', 0)) if request.form.get('max_stock_level') else None
            product.current_stock = float(request.form.get('current_stock', 0))
            product.barcode = request.form.get('barcode')
            product.is_batch_tracked = bool(request.form.get('is_batch_tracked'))
            product.is_expiry_tracked = bool(request.form.get('is_expiry_tracked'))
            product.updated_by = current_user.username
            
            db.session.commit()
            
            flash('Product updated successfully!', 'success')
            return redirect(url_for('professional_inventory'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'danger')
            print(f"Error updating product: {e}")
    
    # GET request - show form with existing data
    categories = InventoryCategory.query.filter_by(is_active=True).all()
    suppliers = InventorySupplier.query.filter_by(is_active=True).all()
    
    return render_template('edit_inventory_product.html', 
                         product=product,
                         categories=categories, 
                         suppliers=suppliers)

@app.route('/inventory/product/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_inventory_product(product_id):
    """Delete (deactivate) inventory product"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        from models import InventoryProduct
        product = InventoryProduct.query.get_or_404(product_id)
        
        # Soft delete - set as inactive
        product.is_active = False
        product.updated_by = current_user.username
        
        db.session.commit()
        
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'danger')
        print(f"Error deleting product: {e}")
    
    return redirect(url_for('professional_inventory'))

# CRUD Operations for Categories
@app.route('/inventory/category/add', methods=['POST'])
@login_required
def add_inventory_category():
    """Add new inventory category"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        from models import InventoryCategory
        
        category = InventoryCategory(
            category_name=request.form.get('category_name'),
            description=request.form.get('description'),
            created_by=current_user.username
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('Category added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding category: {str(e)}', 'danger')
        print(f"Error adding category: {e}")
    
    return redirect(url_for('professional_inventory'))

@app.route('/inventory/supplier/add', methods=['POST'])
@login_required
def add_inventory_supplier():
    """Add new inventory supplier"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        from models import InventorySupplier
        
        supplier = InventorySupplier(
            supplier_name=request.form.get('supplier_name'),
            supplier_code=request.form.get('supplier_code'),
            contact_person=request.form.get('contact_person'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            created_by=current_user.username
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        flash('Supplier added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding supplier: {str(e)}', 'danger')
        print(f"Error adding supplier: {e}")
    
    return redirect(url_for('professional_inventory'))
