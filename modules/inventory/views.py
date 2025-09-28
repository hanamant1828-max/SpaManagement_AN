from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import app, db
from .models import InventoryProduct, InventoryCategory, InventoryLocation, InventoryBatch, InventoryAdjustment, InventoryConsumption, InventoryTransfer
from .queries import *
from datetime import datetime, date
import json

@app.route('/inventory')
@login_required
def inventory_dashboard():
    """Inventory dashboard main page"""
    try:
        return render_template('inventory_dashboard.html')
    except Exception as e:
        print(f"Inventory dashboard error: {e}")
        flash('Error loading inventory dashboard', 'danger')
        return redirect(url_for('dashboard'))

# API Routes for Inventory Management

@app.route('/api/inventory/products/master', methods=['GET'])
@login_required
def api_get_products_master():
    """Get all products for master view - BATCH-CENTRIC"""
    try:
        products = get_all_products()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'category_id': p.category_id,
            'category_name': p.category.name if p.category else '',
            'sku': p.sku,
            'unit_of_measure': p.unit_of_measure,
            'barcode': p.barcode,
            'total_stock': p.total_stock,  # Dynamic property from batches
            'batch_count': p.batch_count,  # Number of batches for this product
            'is_active': p.is_active,
            'is_service_item': p.is_service_item,
            'is_retail_item': p.is_retail_item
        } for p in products])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/products', methods=['GET'])
@login_required
def api_get_products():
    """Get all products - BATCH-CENTRIC"""
    try:
        products = get_all_products()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'category_id': p.category_id,
            'category_name': p.category.name if p.category else '',
            'sku': p.sku,
            'unit_of_measure': p.unit_of_measure,
            'barcode': p.barcode,
            'total_stock': p.total_stock,  # Dynamic property from batches
            'batch_count': p.batch_count,  # Number of batches for this product
            'is_active': p.is_active,
            'is_service_item': p.is_service_item,
            'is_retail_item': p.is_retail_item
        } for p in products])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/products', methods=['POST'])
@login_required
def api_create_product():
    """Create a new product - BATCH-CENTRIC"""
    try:
        data = request.get_json()
        
        # Handle both camelCase (frontend) and underscore (backend) field names
        product = InventoryProduct(
            name=data.get('name'),
            description=data.get('description', ''),
            category_id=data.get('category_id') or data.get('categoryId'),
            sku=data.get('sku', ''),
            unit_of_measure=data.get('unit_of_measure') or data.get('unit', 'pcs'),
            barcode=data.get('barcode', ''),
            is_active=True,
            is_service_item=False,  # Default to False
            is_retail_item=True     # Default to True for spa products
        )

        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'product_id': product.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/products/<int:product_id>', methods=['GET'])
@login_required
def api_get_product(product_id):
    """Get a single product by ID for viewing/editing"""
    try:
        product = get_product_by_id(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
            
        # Find primary location from active batches (most common location)
        primary_location_id = None
        primary_location_name = None
        if product.batches:
            from collections import Counter
            active_batches = [b for b in product.batches if b.status == 'active' and b.location_id]
            if active_batches:
                location_counts = Counter(b.location_id for b in active_batches)
                most_common_location_id = location_counts.most_common(1)[0][0]
                # Get location name
                primary_location_batch = next((b for b in active_batches if b.location_id == most_common_location_id), None)
                if primary_location_batch and primary_location_batch.location:
                    primary_location_id = primary_location_batch.location_id
                    primary_location_name = primary_location_batch.location.name
        
        return jsonify({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'category_id': product.category_id,
            'category_name': product.category.name if product.category else '',
            'sku': product.sku,
            'unit_of_measure': product.unit_of_measure,
            'barcode': product.barcode,
            'total_stock': product.total_stock,
            'batch_count': product.batch_count,
            'is_active': product.is_active,
            'is_service_item': product.is_service_item,
            'is_retail_item': product.is_retail_item,
            'location_id': primary_location_id,
            'location_name': primary_location_name,
            'created_at': product.created_at.isoformat() if product.created_at else None,
            'updated_at': product.updated_at.isoformat() if product.updated_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/products/<int:product_id>', methods=['DELETE'])
@login_required
def api_delete_product(product_id):
    """Delete (deactivate) a product"""
    try:
        from .queries import delete_product
        product = delete_product(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
            
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/categories', methods=['GET'])
@login_required
def api_get_categories():
    """Get all categories"""
    try:
        categories = get_all_categories()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'is_active': c.is_active
        } for c in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/categories', methods=['POST'])
@login_required
def api_create_category():
    """Create a new category"""
    try:
        data = request.get_json()
        category = create_category({
            'name': data.get('name'),
            'description': data.get('description', ''),
            'color_code': data.get('color_code', '#007bff'),
            'is_active': True
        })

        return jsonify({
            'success': True,
            'message': 'Category created successfully',
            'category_id': category.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/categories/<int:category_id>', methods=['GET'])
@login_required
def api_get_category(category_id):
    """Get a single category by ID"""
    try:
        category = InventoryCategory.query.get(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404

        return jsonify({
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'color_code': category.color_code,
            'is_active': category.is_active,
            'created_at': category.created_at.isoformat() if category.created_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/locations', methods=['GET'])
@login_required
def api_get_locations():
    """Get all locations"""
    try:
        locations = get_all_locations()
        return jsonify({
            'locations': [{
                'id': l.id,
                'name': l.name,
                'type': l.type,
                'address': l.address,
                'contact_person': l.contact_person,
                'phone': l.phone,
                'status': l.status,
                'total_products': l.total_batches,
                'total_stock_value': l.total_stock_value
            } for l in locations]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/locations', methods=['POST'])
@login_required
def api_create_location():
    """Create a new location"""
    try:
        data = request.get_json()
        
        # Generate a unique ID based on name
        import re
        name = data.get('name', '')
        # Create ID from name: lowercase, replace spaces/special chars with hyphens
        location_id = re.sub(r'[^a-zA-Z0-9]', '-', name.lower()).strip('-')
        
        # Ensure uniqueness by adding suffix if needed
        base_id = location_id
        counter = 1
        while InventoryLocation.query.get(location_id):
            location_id = f"{base_id}-{counter}"
            counter += 1

        location = InventoryLocation(
            id=location_id,
            name=data.get('name'),
            type=data.get('type', 'warehouse'),  # Default type
            address=data.get('address', ''),
            status='active'
        )

        db.session.add(location)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Location created successfully',
            'location_id': location.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/batches', methods=['GET'])
@login_required
def api_get_batches():
    """Get all batches"""
    try:
        from .models import InventoryBatch
        batches = InventoryBatch.query.all()
        return jsonify({
            'batches': [{
                'id': b.id,
                'batch_name': b.batch_name,
                'product_id': b.product_id,
                'location_id': b.location_id,
                'product_name': b.product.name if b.product else 'Not Assigned',
                'location_name': b.location.name if b.location else 'Not Assigned',
                'created_date': b.created_date.isoformat() if b.created_date else None,
                'mfg_date': b.mfg_date.isoformat() if b.mfg_date else None,
                'expiry_date': b.expiry_date.isoformat() if b.expiry_date else None,
                'qty_available': float(b.qty_available or 0),
                'unit_cost': float(b.unit_cost or 0),
                'selling_price': float(b.selling_price or 0) if b.selling_price else None,
                'status': b.status,
                'is_expired': b.is_expired,
                'days_to_expiry': b.days_to_expiry
            } for b in batches]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/batches', methods=['POST'])
@login_required
def api_create_batch():
    """Create a new batch (simplified - no product/location selection)"""
    try:
        from .models import InventoryBatch
        from datetime import datetime

        data = request.get_json()

        # Validate required fields (simplified)
        required_fields = ['batch_name', 'mfg_date', 'expiry_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Check if batch name is globally unique
        existing_batch = InventoryBatch.query.filter_by(
            batch_name=data['batch_name']
        ).first()

        if existing_batch:
            return jsonify({'error': 'Batch name must be unique'}), 400

        # Parse dates
        mfg_date = datetime.strptime(data['mfg_date'], '%Y-%m-%d').date()
        expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()

        # Validate dates
        if expiry_date <= mfg_date:
            return jsonify({'error': 'Expiry date must be later than manufacturing date'}), 400

        # Create batch (no product/location required)
        batch = InventoryBatch(
            batch_name=data['batch_name'],
            mfg_date=mfg_date,
            expiry_date=expiry_date,
            unit_cost=float(data.get('unit_cost', 0)),
            selling_price=float(data.get('selling_price', 0)) if data.get('selling_price') else None,
            qty_available=0,  # Start with 0, stock added via adjustments
            status='active'
        )

        # Set created_date if provided
        if data.get('created_date'):
            batch.created_date = datetime.strptime(data['created_date'], '%Y-%m-%d').date()

        db.session.add(batch)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Batch created successfully',
            'batch_id': batch.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/adjustments', methods=['POST'])
@login_required
def api_create_adjustment():
    """Create inventory adjustment and assign product/location to batch if needed"""
    try:
        data = request.get_json()

        # Handle both single item and items array structures
        if 'items' in data and data['items']:
            # New structure with items array
            item = data['items'][0]  # Get first item
            batch_id = item.get('batch_id')
            quantity = float(item.get('quantity_in', 0))
            unit_cost = float(item.get('unit_cost', 0))
            product_id = item.get('product_id')
            location_id = item.get('location_id')
            adjustment_type = item.get('adjustment_type', 'add')
        else:
            # Direct structure
            batch_id = data.get('batch_id')
            quantity = float(data.get('quantity', 0))
            unit_cost = float(data.get('unit_cost', 0))
            product_id = data.get('product_id')
            location_id = data.get('location_id')
            adjustment_type = data.get('adjustment_type', 'add')

        # Validate required fields
        if not batch_id:
            return jsonify({'error': 'Batch is required'}), 400
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be positive'}), 400
        if adjustment_type not in ['add', 'remove']:
            return jsonify({'error': 'Invalid adjustment type'}), 400

        batch = InventoryBatch.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404

        # Additional validation for remove operations
        if adjustment_type == 'remove':
            current_stock = float(batch.qty_available or 0)
            if quantity > current_stock:
                return jsonify({'error': f'Cannot remove {quantity}. Only {current_stock} available in stock.'}), 400

        # Assign product and location to batch if provided and not already assigned
        if product_id and not batch.product_id:
            batch.product_id = int(product_id)

        if location_id and not batch.location_id:
            batch.location_id = str(location_id)

        adjustment = InventoryAdjustment(
            batch_id=batch_id,
            adjustment_type=adjustment_type,
            quantity=quantity,
            remarks=data.get('notes', '') or f'Stock {adjustment_type} via inventory management',
            created_by=None  # No user tracking for now
        )

        # Update batch quantity based on adjustment type
        if adjustment_type == 'add':
            batch.qty_available = float(batch.qty_available or 0) + quantity
            if unit_cost > 0:
                batch.unit_cost = unit_cost
        else:  # remove
            batch.qty_available = float(batch.qty_available or 0) - quantity
            # Ensure qty_available doesn't go negative
            if batch.qty_available < 0:
                batch.qty_available = 0

        db.session.add(adjustment)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Inventory adjustment created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/batches/for-consumption', methods=['GET'])
@login_required
def api_get_batches_for_consumption():
    """Get batches available for consumption with FEFO ordering"""
    try:
        from sqlalchemy.orm import joinedload
        from datetime import date

        # Load batches with their related product and location data
        batches = InventoryBatch.query.options(
            joinedload(InventoryBatch.product),
            joinedload(InventoryBatch.location)
        ).filter(
            InventoryBatch.status == 'active',
            InventoryBatch.qty_available > 0
        ).order_by(InventoryBatch.expiry_date.asc().nullslast(), InventoryBatch.batch_name).all()

        batch_data = []
        for batch in batches:
            qty_available = float(batch.qty_available or 0)
            unit = batch.product.unit_of_measure if batch.product else 'pcs'
            product_name = batch.product.name if batch.product else 'Unassigned'
            location_name = batch.location.name if batch.location else 'Unassigned'

            # Create dropdown display text
            expiry_text = f", Exp: {batch.expiry_date.strftime('%d/%m/%Y')}" if batch.expiry_date else ""
            dropdown_display = f"{batch.batch_name} ({product_name}{expiry_text}) - Available: {qty_available} {unit}"

            # Include selling price in batch API response
            batch_info = {
                'id': batch.id,
                'batch_name': batch.batch_name,
                'product_id': batch.product_id,
                'product_name': batch.product.name if batch.product else 'Unassigned',
                'location': batch.location.name if batch.location else 'Unknown',
                'qty_available': float(batch.qty_available or 0),
                'unit_cost': float(batch.unit_cost or 0),
                'selling_price': float(batch.selling_price or 0) if batch.selling_price else float(batch.unit_cost or 0),
                'unit': batch.product.unit_of_measure if batch.product else 'pcs',
                'expiry_date': batch.expiry_date.isoformat() if batch.expiry_date else None,
                'days_to_expiry': batch.days_to_expiry,
                'is_near_expiry': batch.is_near_expiry,
                'status': batch.status,
                'dropdown_display': dropdown_display
            }
            batch_data.append(batch_info)

        return jsonify({
            'success': True,
            'batches': batch_data
        })
    except Exception as e:
        print(f"Error in api_get_batches_for_consumption: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/batches/available', methods=['GET'])
@login_required
def api_get_available_batches():
    """Get batches available for adjustments and consumption"""
    try:
        from .models import InventoryBatch
        from datetime import date
        
        # Get all active batches (not expired)
        batches = InventoryBatch.query.filter(
            InventoryBatch.status == 'active',
            or_(
                InventoryBatch.expiry_date == None,
                InventoryBatch.expiry_date >= date.today()
            )
        ).order_by(InventoryBatch.expiry_date.asc().nullslast(), InventoryBatch.batch_name).all()
        
        return jsonify([{
            'id': b.id,
            'batch_name': b.batch_name,
            'product_id': b.product_id,
            'location_id': b.location_id,
            'product_name': b.product.name if b.product else 'Not Assigned',
            'location_name': b.location.name if b.location else 'Not Assigned',
            'qty_available': float(b.qty_available or 0),
            'expiry_date': b.expiry_date.isoformat() if b.expiry_date else None,
            'is_expired': b.is_expired,
            'days_to_expiry': b.days_to_expiry
        } for b in batches])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ BATCH-CENTRIC CONSUMPTION ENDPOINTS ============

@app.route('/api/inventory/consumption', methods=['GET'])
@login_required
def api_get_consumption_records():
    """Get consumption records"""
    try:
        consumption_records = get_consumption_records(limit=100)
        return jsonify([{
            'id': c.id,
            'batch_id': c.batch_id,
            'batch_name': c.batch.batch_name if c.batch else 'Unknown',
            'product_name': c.batch.product.name if c.batch and c.batch.product else 'Unknown',
            'quantity': float(c.quantity),
            'issued_to': c.issued_to,
            'reference': c.reference,
            'notes': c.notes,
            'created_at': c.created_at.isoformat() if c.created_at else None,
            'created_by_name': c.user.full_name if c.user else 'Unknown'
        } for c in consumption_records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/consumption', methods=['POST'])
@login_required
def api_create_consumption():
    """Create consumption record - BATCH-CENTRIC"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['batch_id', 'quantity', 'issued_to']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create consumption using batch-centric function
        consumption = create_consumption_record(
            batch_id=data['batch_id'],
            quantity=float(data['quantity']),
            issued_to=data['issued_to'],
            reference=data.get('reference', ''),
            notes=data.get('notes', ''),
            user_id=current_user.id
        )
        
        return jsonify({
            'success': True,
            'message': 'Consumption record created successfully',
            'consumption_id': consumption.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ BATCH-CENTRIC ADJUSTMENT ENDPOINTS ============

@app.route('/api/inventory/adjustments', methods=['GET'])
@login_required  
def api_get_adjustments():
    """Get adjustment records"""
    try:
        adjustments = InventoryAdjustment.query.order_by(desc(InventoryAdjustment.created_at)).limit(100).all()
        return jsonify([{
            'id': a.id,
            'batch_id': a.batch_id,
            'batch_name': a.batch.batch_name if a.batch else 'Unknown',
            'product_name': a.batch.product.name if a.batch and a.batch.product else 'Unknown',
            'adjustment_type': a.adjustment_type,
            'quantity': float(a.quantity),
            'notes': a.remarks,
            'created_at': a.created_at.isoformat() if a.created_at else None,
            'created_by_name': a.user.full_name if a.user else 'Unknown'
        } for a in adjustments])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/products/<int:product_id>', methods=['PUT'])
@login_required
def api_update_product(product_id):
    """Update an existing product"""
    try:
        data = request.get_json()
        
        # Handle both camelCase (frontend) and underscore (backend) field names
        product = update_product(product_id, {
            'name': data.get('name'),
            'description': data.get('description', ''),
            'category_id': data.get('category_id') or data.get('categoryId'),  # Support both formats
            'sku': data.get('sku', ''),
            'unit_of_measure': data.get('unit_of_measure') or data.get('unit', 'pcs'),  # Support both formats
            'barcode': data.get('barcode', ''),
            'is_service_item': data.get('is_service_item', False) or data.get('trackBatches', False),
            'is_retail_item': data.get('is_retail_item', True) or data.get('trackSerials', True)
        })

        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # Check for duplicate SKU (excluding current product)
        if data.get('sku') and data.get('sku') != product.sku:
            existing = InventoryProduct.query.filter(
                InventoryProduct.sku == data.get('sku'),
                InventoryProduct.id != product_id
            ).first()
            if existing:
                return jsonify({'error': 'SKU already exists'}), 400

        # Handle both camelCase (frontend) and underscore (backend) field names
        if data.get('name'):
            product.name = data.get('name')
        if data.get('description') is not None:
            product.description = data.get('description')
        if data.get('category_id') or data.get('categoryId'):
            product.category_id = data.get('category_id') or data.get('categoryId')
        if data.get('sku'):
            product.sku = data.get('sku')
        if data.get('unit_of_measure') or data.get('unit'):
            product.unit_of_measure = data.get('unit_of_measure') or data.get('unit')
        if data.get('barcode') is not None:
            product.barcode = data.get('barcode')
        # is_service_item and is_retail_item are no longer user-editable
        # They maintain their current values

        product.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Product updated successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/categories/<int:category_id>', methods=['PUT'])
@login_required
def api_update_category(category_id):
    """Update an existing category"""
    try:
        data = request.get_json()
        category = InventoryCategory.query.get(category_id)
        
        if not category:
            return jsonify({'error': 'Category not found'}), 404

        category.name = data.get('name', category.name)
        category.description = data.get('description', category.description)
        category.color_code = data.get('color_code', category.color_code)
        category.is_active = data.get('is_active', category.is_active)
        
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Category updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/locations/<location_id>', methods=['PUT'])
@login_required
def api_update_location(location_id):
    """Update an existing location"""
    try:
        data = request.get_json()
        location = InventoryLocation.query.get(location_id)
        
        if not location:
            return jsonify({'error': 'Location not found'}), 404

        location.name = data.get('name', location.name)
        location.type = data.get('type', location.type)
        location.address = data.get('address', location.address)
        location.contact_person = data.get('contact_person', location.contact_person)
        location.phone = data.get('phone', location.phone)
        location.status = data.get('status', location.status)
        
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Location updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/batches/<int:batch_id>', methods=['PUT'])
@login_required
def api_update_batch(batch_id):
    """Update an existing batch"""
    try:
        from datetime import datetime
        data = request.get_json()
        batch = InventoryBatch.query.get(batch_id)
        
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404

        # Update allowed fields
        if data.get('batch_name'):
            # Check for unique batch name (excluding current batch)
            existing = InventoryBatch.query.filter(
                InventoryBatch.batch_name == data['batch_name'],
                InventoryBatch.id != batch_id
            ).first()
            if existing:
                return jsonify({'error': 'Batch name must be unique'}), 400
            batch.batch_name = data['batch_name']

        if data.get('created_date'):
            batch.created_date = datetime.strptime(data['created_date'], '%Y-%m-%d').date()

        if data.get('mfg_date'):
            batch.mfg_date = datetime.strptime(data['mfg_date'], '%Y-%m-%d').date()

        if data.get('expiry_date'):
            batch.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()

        if data.get('unit_cost') is not None:
            batch.unit_cost = float(data['unit_cost'])

        if data.get('selling_price') is not None:
            batch.selling_price = float(data['selling_price']) if data['selling_price'] else None

        # Validate dates
        if batch.expiry_date <= batch.mfg_date:
            return jsonify({'error': 'Expiry date must be later than manufacturing date'}), 400

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Batch updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['GET'])
@login_required
def api_get_products_simple():
    """Simple products API endpoint"""
    try:
        products = get_all_products()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'category_name': p.category.name if p.category else 'No Category'
        } for p in products])
    except Exception as e:
        return jsonify({'error': str(e)}), 500