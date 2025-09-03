"""
Inventory Master Management Views
CRUD operations for categories and suppliers
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import InventoryCategory, InventorySupplier

@app.route('/inventory/master')
@login_required
def inventory_master():
    """Main inventory master management page"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    categories = InventoryCategory.query.order_by(InventoryCategory.category_name).all()
    suppliers = InventorySupplier.query.order_by(InventorySupplier.supplier_name).all()

    # Calculate statistics
    active_categories = sum(1 for cat in categories if cat.is_active)
    active_suppliers = sum(1 for sup in suppliers if sup.is_active)

    return render_template('inventory_master.html',
                         categories=categories,
                         suppliers=suppliers,
                         active_categories=active_categories,
                         active_suppliers=active_suppliers)

# Category CRUD Operations
@app.route('/inventory/category/add', methods=['POST'])
@login_required
def add_inventory_category():
    """Add new inventory category"""
    if not current_user.can_access('inventory'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    try:
        category_name = request.form.get('category_name', '').strip()
        description = request.form.get('description', '').strip()
        is_active = 'is_active' in request.form

        if not category_name:
            return jsonify({'success': False, 'error': 'Category name is required'})

        # Check if category already exists
        existing = InventoryCategory.query.filter_by(category_name=category_name).first()
        if existing:
            return jsonify({'success': False, 'error': f'Category "{category_name}" already exists'})

        # Create new category
        category = InventoryCategory(
            category_name=category_name,
            description=description if description else None,
            is_active=is_active,
            created_by=current_user.username if hasattr(current_user, 'username') else str(current_user.id)
        )

        db.session.add(category)
        db.session.commit()

        return jsonify({'success': True, 'message': f'Category "{category_name}" created successfully!'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Error creating category: {str(e)}'})

@app.route('/inventory/category/update/<int:category_id>', methods=['POST'])
@login_required
def update_inventory_category(category_id):
    """Update inventory category"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        category = InventoryCategory.query.get_or_404(category_id)

        category_name = request.form.get('category_name', '').strip()
        description = request.form.get('description', '').strip()
        is_active = 'is_active' in request.form

        if not category_name:
            flash('Category name is required', 'danger')
            return redirect(url_for('inventory_master_crud'))

        # Check if name conflicts with another category
        existing = InventoryCategory.query.filter(
            InventoryCategory.category_name == category_name,
            InventoryCategory.category_id != category_id
        ).first()

        if existing:
            flash(f'Category name "{category_name}" is already in use', 'warning')
            return redirect(url_for('inventory_master_crud'))

        # Update category
        category.category_name = category_name
        category.description = description if description else None
        category.is_active = is_active
        category.updated_by = current_user.username if hasattr(current_user, 'username') else str(current_user.id)

        db.session.commit()

        flash(f'Category "{category_name}" updated successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating category: {str(e)}', 'danger')

    return redirect(url_for('inventory_master_crud'))

@app.route('/inventory/category/delete/<int:category_id>', methods=['POST'])
@login_required
def delete_inventory_category(category_id):
    """Delete inventory category"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        category = InventoryCategory.query.get_or_404(category_id)

        # Check if category is being used by any products
        from models import InventoryProduct
        products_using_category = InventoryProduct.query.filter_by(category_id=category_id, is_active=True).count()

        if products_using_category > 0:
            flash(f'Cannot delete category "{category.category_name}" - it is being used by {products_using_category} products', 'warning')
            return redirect(url_for('inventory_master_crud'))

        category_name = category.category_name
        db.session.delete(category)
        db.session.commit()

        flash(f'Category "{category_name}" deleted successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting category: {str(e)}', 'danger')

    return redirect(url_for('inventory_master_crud'))

# Supplier CRUD Operations
@app.route('/supplier/add', methods=['POST'])
@login_required
def add_supplier():
    """Add new supplier"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        supplier_name = request.form.get('supplier_name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        website = request.form.get('website', '').strip()
        address = request.form.get('address', '').strip()
        rating = int(request.form.get('rating', 3))
        is_active = 'is_active' in request.form

        if not supplier_name:
            flash('Supplier name is required', 'danger')
            return redirect(url_for('inventory_master_crud'))

        # Check if supplier already exists
        existing = InventorySupplier.query.filter_by(supplier_name=supplier_name).first()
        if existing:
            flash(f'Supplier "{supplier_name}" already exists', 'warning')
            return redirect(url_for('inventory_master_crud'))

        # Create new supplier
        supplier = InventorySupplier(
            supplier_name=supplier_name,
            contact_person=contact_person if contact_person else None,
            phone=phone if phone else None,
            email=email if email else None,
            website=website if website else None,
            address=address if address else None,
            rating=rating,
            is_active=is_active,
            created_by=current_user.username if hasattr(current_user, 'username') else str(current_user.id)
        )

        db.session.add(supplier)
        db.session.commit()

        flash(f'Supplier "{supplier_name}" created successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error creating supplier: {str(e)}', 'danger')

    return redirect(url_for('inventory_master_crud'))

@app.route('/supplier/update/<int:supplier_id>', methods=['POST'])
@login_required
def update_supplier(supplier_id):
    """Update supplier"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        supplier = InventorySupplier.query.get_or_404(supplier_id)

        supplier_name = request.form.get('supplier_name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        website = request.form.get('website', '').strip()
        address = request.form.get('address', '').strip()
        rating = int(request.form.get('rating', 3))
        is_active = 'is_active' in request.form

        if not supplier_name:
            flash('Supplier name is required', 'danger')
            return redirect(url_for('inventory_master_crud'))

        # Check if name conflicts with another supplier
        existing = InventorySupplier.query.filter(
            InventorySupplier.supplier_name == supplier_name,
            InventorySupplier.supplier_id != supplier_id
        ).first()

        if existing:
            flash(f'Supplier name "{supplier_name}" is already in use', 'warning')
            return redirect(url_for('inventory_master_crud'))

        # Update supplier
        supplier.supplier_name = supplier_name
        supplier.contact_person = contact_person if contact_person else None
        supplier.phone = phone if phone else None
        supplier.email = email if email else None
        supplier.website = website if website else None
        supplier.address = address if address else None
        supplier.rating = rating
        supplier.is_active = is_active
        supplier.updated_by = current_user.username if hasattr(current_user, 'username') else str(current_user.id)

        db.session.commit()

        flash(f'Supplier "{supplier_name}" updated successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating supplier: {str(e)}', 'danger')

    return redirect(url_for('inventory_master_crud'))

@app.route('/supplier/delete/<int:supplier_id>', methods=['POST'])
@login_required
def delete_supplier(supplier_id):
    """Delete supplier"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        supplier = InventorySupplier.query.get_or_404(supplier_id)

        # Check if supplier is being used by any products
        from models import InventoryProduct
        products_using_supplier = InventoryProduct.query.filter_by(supplier_id=supplier_id, is_active=True).count()

        if products_using_supplier > 0:
            flash(f'Cannot delete supplier "{supplier.supplier_name}" - it is being used by {products_using_supplier} products', 'warning')
            return redirect(url_for('inventory_master_crud'))

        supplier_name = supplier.supplier_name
        db.session.delete(supplier)
        db.session.commit()

        flash(f'Supplier "{supplier_name}" deleted successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting supplier: {str(e)}', 'danger')

    return redirect(url_for('inventory_master_crud'))

# API Endpoints for AJAX operations
@app.route('/api/supplier/<int:supplier_id>')
@login_required
def api_get_supplier(supplier_id):
    """Get supplier data for editing"""
    if not current_user.can_access('inventory'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    try:
        supplier = InventorySupplier.query.get_or_404(supplier_id)

        return jsonify({
            'success': True,
            'supplier': {
                'supplier_id': supplier.supplier_id,
                'supplier_name': supplier.supplier_name,
                'contact_person': supplier.contact_person,
                'phone': supplier.phone,
                'email': supplier.email,
                'website': supplier.website,
                'address': supplier.address,
                'rating': supplier.rating,
                'is_active': supplier.is_active
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/inventory/master/export')
@login_required
def export_master_data():
    """Export master data as Excel"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        import pandas as pd
        import io
        from datetime import datetime

        # Get data
        categories = InventoryCategory.query.all()
        suppliers = InventorySupplier.query.all()

        # Create Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:

            # Categories sheet
            categories_data = []
            for cat in categories:
                categories_data.append({
                    'ID': cat.category_id,
                    'Name': cat.category_name,
                    'Description': cat.description or '',
                    'Status': 'Active' if cat.is_active else 'Inactive',
                    'Created': cat.created_at.strftime('%Y-%m-%d %H:%M') if cat.created_at else '',
                    'Created By': cat.created_by or ''
                })

            categories_df = pd.DataFrame(categories_data)
            categories_df.to_excel(writer, sheet_name='Categories', index=False)

            # Suppliers sheet
            suppliers_data = []
            for sup in suppliers:
                suppliers_data.append({
                    'ID': sup.supplier_id,
                    'Name': sup.supplier_name,
                    'Contact Person': sup.contact_person or '',
                    'Phone': sup.phone or '',
                    'Email': sup.email or '',
                    'Website': sup.website or '',
                    'Address': sup.address or '',
                    'Rating': sup.rating or 0,
                    'Status': 'Active' if sup.is_active else 'Inactive',
                    'Created': sup.created_at.strftime('%Y-%m-%d %H:%M') if sup.created_at else '',
                    'Created By': sup.created_by or ''
                })

            suppliers_df = pd.DataFrame(suppliers_data)
            suppliers_df.to_excel(writer, sheet_name='Suppliers', index=False)

        output.seek(0)

        from flask import send_file
        return send_file(
            output,
            as_attachment=True,
            download_name=f'inventory_master_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'danger')
        return redirect(url_for('inventory_master'))