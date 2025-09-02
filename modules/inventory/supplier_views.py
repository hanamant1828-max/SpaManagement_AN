
"""
Supplier Management Views
CRUD operations for inventory suppliers
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import InventorySupplier

def get_all_suppliers():
    """Get all suppliers ordered by name"""
    return InventorySupplier.query.order_by(InventorySupplier.supplier_name).all()

def get_supplier_by_id(supplier_id):
    """Get supplier by ID"""
    return InventorySupplier.query.get(supplier_id)

def create_supplier(data):
    """Create new supplier"""
    supplier = InventorySupplier(
        supplier_name=data['supplier_name'],
        supplier_code=data.get('supplier_code'),
        contact_person=data.get('contact_person'),
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address'),
        city=data.get('city'),
        state=data.get('state'),
        postal_code=data.get('postal_code'),
        country=data.get('country'),
        tax_id=data.get('tax_id'),
        payment_terms=data.get('payment_terms', 'Net 30'),
        rating=data.get('rating', 5.0),
        is_active=data.get('is_active', True),
        created_by=current_user.username if current_user else 'system'
    )
    
    db.session.add(supplier)
    db.session.commit()
    return supplier

def update_supplier(supplier_id, data):
    """Update supplier"""
    supplier = get_supplier_by_id(supplier_id)
    if not supplier:
        raise ValueError("Supplier not found")
    
    for key, value in data.items():
        if hasattr(supplier, key):
            setattr(supplier, key, value)
    
    supplier.updated_by = current_user.username if current_user else 'system'
    db.session.commit()
    return supplier

@app.route('/suppliers')
@login_required
def suppliers():
    """Supplier Management with CRUD operations"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    suppliers = get_all_suppliers()
    
    return render_template('suppliers.html', suppliers=suppliers)

@app.route('/suppliers/create', methods=['POST'])
@login_required
def create_supplier_route():
    """Create new supplier"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('suppliers'))
    
    try:
        # Get form data
        supplier_name = request.form.get('supplier_name', '').strip()
        supplier_code = request.form.get('supplier_code', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        postal_code = request.form.get('postal_code', '').strip()
        country = request.form.get('country', '').strip()
        tax_id = request.form.get('tax_id', '').strip()
        payment_terms = request.form.get('payment_terms', 'Net 30')
        rating = float(request.form.get('rating', 5.0))
        is_active = 'is_active' in request.form
        
        # Basic validation
        if not supplier_name:
            flash('Supplier name is required', 'danger')
            return redirect(url_for('suppliers'))
        
        # Create supplier
        supplier = create_supplier({
            'supplier_name': supplier_name,
            'supplier_code': supplier_code if supplier_code else None,
            'contact_person': contact_person,
            'phone': phone,
            'email': email,
            'address': address,
            'city': city,
            'state': state,
            'postal_code': postal_code,
            'country': country,
            'tax_id': tax_id,
            'payment_terms': payment_terms,
            'rating': rating,
            'is_active': is_active
        })
        flash(f'Supplier "{supplier.supplier_name}" created successfully', 'success')
        
    except Exception as e:
        flash(f'Error creating supplier: {str(e)}', 'danger')
    
    return redirect(url_for('suppliers'))

@app.route('/suppliers/<int:supplier_id>/edit', methods=['POST'])
@login_required
def edit_supplier(supplier_id):
    """Edit supplier"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('suppliers'))
    
    supplier = get_supplier_by_id(supplier_id)
    if not supplier:
        flash('Supplier not found', 'danger')
        return redirect(url_for('suppliers'))
    
    try:
        # Get form data
        supplier_name = request.form.get('supplier_name', '').strip()
        supplier_code = request.form.get('supplier_code', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        postal_code = request.form.get('postal_code', '').strip()
        country = request.form.get('country', '').strip()
        tax_id = request.form.get('tax_id', '').strip()
        payment_terms = request.form.get('payment_terms', 'Net 30')
        rating = float(request.form.get('rating', 5.0))
        is_active = 'is_active' in request.form
        
        # Basic validation
        if not supplier_name:
            flash('Supplier name is required', 'danger')
            return redirect(url_for('suppliers'))
        
        # Update supplier
        update_supplier(supplier_id, {
            'supplier_name': supplier_name,
            'supplier_code': supplier_code if supplier_code else None,
            'contact_person': contact_person,
            'phone': phone,
            'email': email,
            'address': address,
            'city': city,
            'state': state,
            'postal_code': postal_code,
            'country': country,
            'tax_id': tax_id,
            'payment_terms': payment_terms,
            'rating': rating,
            'is_active': is_active
        })
        flash(f'Supplier "{supplier.supplier_name}" updated successfully', 'success')
        
    except Exception as e:
        flash(f'Error updating supplier: {str(e)}', 'danger')
    
    return redirect(url_for('suppliers'))

@app.route('/suppliers/<int:supplier_id>/delete', methods=['POST'])
@login_required
def delete_supplier(supplier_id):
    """Delete supplier"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('suppliers'))
    
    supplier = get_supplier_by_id(supplier_id)
    if not supplier:
        flash('Supplier not found', 'danger')
        return redirect(url_for('suppliers'))
    
    try:
        # Check if supplier is being used by any inventory products
        from models import InventoryProduct
        products_using_supplier = InventoryProduct.query.filter_by(supplier_id=supplier_id).count()
        
        if products_using_supplier > 0:
            flash(f'Cannot delete supplier "{supplier.supplier_name}" as it is being used by {products_using_supplier} product(s)', 'danger')
            return redirect(url_for('suppliers'))
        
        supplier_name = supplier.supplier_name
        db.session.delete(supplier)
        db.session.commit()
        flash(f'Supplier "{supplier_name}" deleted successfully', 'success')
        
    except Exception as e:
        flash(f'Error deleting supplier: {str(e)}', 'danger')
    
    return redirect(url_for('suppliers'))

@app.route('/suppliers/<int:supplier_id>/toggle', methods=['POST'])
@login_required
def toggle_supplier(supplier_id):
    """Toggle supplier active status"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('suppliers'))
    
    supplier = get_supplier_by_id(supplier_id)
    if not supplier:
        flash('Supplier not found', 'danger')
        return redirect(url_for('suppliers'))
    
    try:
        supplier.is_active = not supplier.is_active
        supplier.updated_by = current_user.username if current_user else 'system'
        db.session.commit()
        
        status = "activated" if supplier.is_active else "deactivated"
        flash(f'Supplier "{supplier.supplier_name}" {status} successfully', 'success')
        
    except Exception as e:
        flash(f'Error updating supplier status: {str(e)}', 'danger')
    
    return redirect(url_for('suppliers'))

@app.route('/suppliers/<int:supplier_id>/view')
@login_required
def view_supplier(supplier_id):
    """View supplier details"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    supplier = get_supplier_by_id(supplier_id)
    if not supplier:
        flash('Supplier not found', 'danger')
        return redirect(url_for('suppliers'))
    
    # Get products associated with this supplier
    from models import InventoryProduct
    products = InventoryProduct.query.filter_by(supplier_id=supplier_id).all()
    
    return render_template('supplier_details.html', 
                         supplier=supplier, 
                         products=products)
