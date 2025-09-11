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
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

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
        from .models import InventoryProduct
        from sqlalchemy.orm import joinedload
        
        # Load products with their related data
        products = InventoryProduct.query.options(
            joinedload(InventoryProduct.category),
            joinedload(InventoryProduct.batches)
        ).filter(InventoryProduct.is_active == True).all()
        
        product_list = []
        for p in products:
            # Calculate dynamic properties safely
            try:
                total_stock = sum(float(batch.qty_available or 0) for batch in p.batches if batch.status == 'active')
                batch_count = len([b for b in p.batches if b.status == 'active'])
                
                # Determine status based on stock
                if total_stock <= 0:
                    status = 'out_of_stock'
                elif total_stock <= 10:
                    status = 'low_stock'  
                else:
                    status = 'in_stock'
                    
                product_data = {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description or '',
                    'category_id': p.category_id,
                    'category_name': p.category.name if p.category else '',
                    'category': p.category.name if p.category else '',
                    'sku': p.sku,
                    'unit_of_measure': p.unit_of_measure or 'pcs',
                    'unit': p.unit_of_measure or 'pcs',
                    'barcode': p.barcode or '',
                    'total_stock': total_stock,
                    'stock': total_stock,  # Alias for compatibility
                    'batch_count': batch_count,
                    'status': status,
                    'is_active': p.is_active,
                    'is_service_item': p.is_service_item or False,
                    'is_retail_item': p.is_retail_item or False,
                    'created_at': p.created_at.isoformat() if p.created_at else None,
                    'updated_at': p.updated_at.isoformat() if p.updated_at else None
                }
                product_list.append(product_data)
            except Exception as inner_e:
                print(f"Error processing product {p.id}: {inner_e}")
                continue
                
        return jsonify(product_list)
    except Exception as e:
        print(f"ERROR in api_get_products_master: {str(e)}")
        import traceback
        traceback.print_exc()
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
        from .models import InventoryProduct
        
        data = request.get_json()
        
        # Validation
        if not data.get('name'):
            return jsonify({'error': 'Product name is required'}), 400
        if not data.get('sku'):
            return jsonify({'error': 'SKU is required'}), 400
            
        # Check for duplicate SKU
        existing = InventoryProduct.query.filter_by(sku=data.get('sku')).first()
        if existing:
            return jsonify({'error': 'SKU already exists'}), 400
        
        # Handle both camelCase (frontend) and underscore (backend) field names
        product = InventoryProduct(
            name=data.get('name'),
            description=data.get('description', ''),
            category_id=data.get('category_id') or data.get('categoryId'),
            sku=data.get('sku', ''),
            unit_of_measure=data.get('unit_of_measure') or data.get('unit', 'pcs'),
            barcode=data.get('barcode', ''),
            is_active=True,
            is_service_item=data.get('is_service_item', False) or data.get('trackBatches', False),
            is_retail_item=data.get('is_retail_item', True) or data.get('trackSerials', True)
        )
        
        db.session.add(product)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'product_id': product.id
        })
    except Exception as e:
        db.session.rollback()
        print(f"ERROR creating product: {str(e)}")
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
        from .models import InventoryProduct
        
        product = InventoryProduct.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if product has active batches
        active_batches = [b for b in product.batches if b.status == 'active']
        if active_batches:
            return jsonify({'error': 'Cannot delete product with active batches. Please remove or deactivate all batches first.'}), 400
        
        # Soft delete - mark as inactive
        product.is_active = False
        product.updated_at = datetime.utcnow()
        db.session.commit()
            
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"ERROR deleting product: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/categories', methods=['GET'])
@login_required
def api_get_categories():
    """Get all categories"""
    try:
        from .models import InventoryCategory
        
        categories = InventoryCategory.query.filter(InventoryCategory.is_active == True).order_by(InventoryCategory.name).all()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'description': c.description or '',
            'color_code': getattr(c, 'color_code', '#007bff'),
            'is_active': c.is_active
        } for c in categories])
    except Exception as e:
        print(f"ERROR in api_get_categories: {str(e)}")
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
        from .models import InventoryLocation
        
        locations = InventoryLocation.query.filter(InventoryLocation.status == 'active').order_by(InventoryLocation.name).all()
        return jsonify({
            'locations': [{
                'id': l.id,
                'name': l.name,
                'type': l.type or 'warehouse',
                'address': l.address or '',
                'contact_person': getattr(l, 'contact_person', '') or '',
                'phone': getattr(l, 'phone', '') or '',
                'status': l.status,
                'total_products': len([b for b in getattr(l, 'batches', []) if b.status == 'active']),
                'total_stock_value': 0  # Calculate if needed
            } for l in locations]
        })
    except Exception as e:
        print(f"ERROR in api_get_locations: {str(e)}")
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
    """Get all batches with proper relationships"""
    try:
        from .models import InventoryBatch
        from sqlalchemy.orm import joinedload
        
        print("DEBUG: Loading batches from database...")
        
        # Load batches with their related product and location data
        batches = InventoryBatch.query.options(
            joinedload(InventoryBatch.product),
            joinedload(InventoryBatch.location)
        ).filter(InventoryBatch.status != 'deleted').all()
        
        print(f"DEBUG: Found {len(batches)} batches in database")
        
        batch_list = []
        for b in batches:
            batch_data = {
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
            }
            batch_list.append(batch_data)
            print(f"DEBUG: Batch {b.id}: {b.batch_name}, Product: {b.product_id}, Location: {b.location_id}")
        
        print(f"DEBUG: Returning {len(batch_list)} batches to frontend")
        
        return jsonify({
            'batches': batch_list
        })
    except Exception as e:
        print(f"ERROR in api_get_batches: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/batches', methods=['POST'])
@login_required
def api_create_batch():
    """Create a new batch with proper data handling"""
    try:
        from .models import InventoryBatch
        from datetime import datetime

        data = request.get_json()
        print(f"DEBUG: Received batch data: {data}")  # Debug logging

        # Validate required fields
        required_fields = ['batch_name', 'mfg_date', 'expiry_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Validate batch name is not empty
        batch_name = data['batch_name'].strip()
        if not batch_name:
            return jsonify({'error': 'Batch name cannot be empty'}), 400

        # Check if batch name is globally unique
        existing_batch = InventoryBatch.query.filter_by(batch_name=batch_name).first()
        if existing_batch:
            return jsonify({'error': 'Batch name must be unique'}), 400

        # Parse and validate dates
        try:
            mfg_date = datetime.strptime(data['mfg_date'], '%Y-%m-%d').date()
            expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        except ValueError as e:
            return jsonify({'error': f'Invalid date format: {str(e)}'}), 400

        # Validate date logic
        if expiry_date <= mfg_date:
            return jsonify({'error': 'Expiry date must be later than manufacturing date'}), 400

        # Parse created_date if provided
        created_date = None
        if data.get('created_date'):
            try:
                created_date = datetime.strptime(data['created_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid created date format'}), 400

        # Parse product_id and location_id
        product_id = None
        if data.get('product_id') and str(data.get('product_id')).strip():
            try:
                product_id = int(data['product_id'])
                # Verify product exists
                from .models import InventoryProduct
                if not InventoryProduct.query.get(product_id):
                    return jsonify({'error': 'Selected product does not exist'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid product ID'}), 400

        location_id = None
        if data.get('location_id') and str(data.get('location_id')).strip():
            location_id = str(data['location_id']).strip()
            # Verify location exists
            from .models import InventoryLocation
            if not InventoryLocation.query.get(location_id):
                return jsonify({'error': 'Selected location does not exist'}), 400

        # Parse pricing
        try:
            unit_cost = float(data.get('unit_cost', 0))
            selling_price = None
            if data.get('selling_price') and str(data.get('selling_price')).strip():
                selling_price = float(data['selling_price'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid pricing values'}), 400

        # Create the batch
        batch = InventoryBatch(
            batch_name=batch_name,
            product_id=product_id,
            location_id=location_id,
            mfg_date=mfg_date,
            expiry_date=expiry_date,
            created_date=created_date or datetime.utcnow().date(),
            unit_cost=unit_cost,
            selling_price=selling_price,
            qty_available=0,  # Start with 0, stock added via adjustments
            status='active'
        )

        print(f"DEBUG: Creating batch: {batch.batch_name}, Product: {batch.product_id}, Location: {batch.location_id}")  # Debug logging

        db.session.add(batch)
        db.session.commit()

        print(f"DEBUG: Batch created successfully with ID: {batch.id}")  # Debug logging

        return jsonify({
            'success': True,
            'message': 'Batch created successfully',
            'batch_id': batch.id
        })

    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Error creating batch: {str(e)}")  # Debug logging
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/adjustments', methods=['POST'])
@login_required
def api_create_adjustment():
    """Create inventory adjustment from the frontend modal"""
    try:
        from datetime import datetime
        data = request.get_json()
        print(f"DEBUG: Received adjustment data: {data}")

        # Handle both single item and items array structures
        if 'items' in data and data['items']:
            # New structure with items array
            item = data['items'][0]  # Get first item
            batch_id = item.get('batch_id')
            quantity = float(item.get('quantity_in', 0))
            unit_cost = float(item.get('unit_cost', 0))
            product_id = item.get('product_id')
            location_id = item.get('location_id')
        else:
            # Direct structure
            batch_id = data.get('batch_id')
            quantity = float(data.get('quantity', 0))
            unit_cost = float(data.get('unit_cost', 0))
            product_id = data.get('product_id')
            location_id = data.get('location_id')

        # Validate required fields
        if not batch_id:
            return jsonify({'error': 'Batch is required'}), 400
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be positive'}), 400

        batch = InventoryBatch.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404

        # Assign product and location to batch if provided and not already assigned
        if product_id and not batch.product_id:
            batch.product_id = int(product_id)
        
        if location_id and not batch.location_id:
            batch.location_id = str(location_id)

        # Generate reference ID if not provided
        reference_no = data.get('reference_no')
        if not reference_no:
            today = datetime.now()
            reference_no = f"ADJ-{today.strftime('%Y%m%d-%H%M%S')}"

        # Create adjustment record
        adjustment = InventoryAdjustment(
            batch_id=batch_id,
            adjustment_type='add',
            quantity=quantity,
            remarks=data.get('notes', '') or 'Stock adjustment via inventory management',
            created_by=current_user.id
        )

        # Update batch quantity and cost
        batch.qty_available = float(batch.qty_available or 0) + quantity
        if unit_cost > 0:
            batch.unit_cost = unit_cost

        db.session.add(adjustment)
        db.session.commit()

        print(f"DEBUG: Adjustment created - ID: {adjustment.id}, Batch: {batch_id}, Qty: {quantity}")

        return jsonify({
            'success': True,
            'message': 'Inventory adjustment created successfully',
            'adjustment_id': adjustment.id,
            'reference_no': reference_no
        })
    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Error creating adjustment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/batches/for-consumption', methods=['GET'])
@login_required
def api_get_batches_for_consumption():
    """Get batches available for consumption with FEFO ordering"""
    try:
        from .queries import get_available_batches_for_consumption
        batches = get_available_batches_for_consumption()
        batch_data = [{
            'id': b.id,
            'batch_name': b.batch_name,
            'product_name': b.product.name if b.product else 'Unassigned',
            'location_name': b.location.name if b.location else 'Unassigned',
            'qty_available': float(b.qty_available or 0),
            'unit': b.product.unit_of_measure if b.product else 'pcs',
            'expiry_date': b.expiry_date.isoformat() if b.expiry_date else None,
            'dropdown_display': b.dropdown_display
        } for b in batches]
        
        return jsonify({
            'success': True,
            'batches': batch_data
        })
    except Exception as e:
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
    """Get adjustment records with proper structure for frontend"""
    try:
        from sqlalchemy.orm import joinedload
        from sqlalchemy import desc
        
        adjustments = InventoryAdjustment.query.options(
            joinedload(InventoryAdjustment.batch).joinedload(InventoryBatch.product),
            joinedload(InventoryAdjustment.batch).joinedload(InventoryBatch.location),
            joinedload(InventoryAdjustment.user)
        ).order_by(desc(InventoryAdjustment.created_at)).limit(100).all()

        records = []
        for a in adjustments:
            # Generate reference ID (this should ideally be stored in DB)
            reference_id = f"ADJ-{a.created_at.strftime('%Y%m%d-%H%M%S')}-{a.id}" if a.created_at else f"ADJ-{a.id}"
            
            record = {
                'id': a.id,
                'reference_id': reference_id,
                'batch_id': a.batch_id,
                'batch_name': a.batch.batch_name if a.batch else 'Unknown Batch',
                'product_name': a.batch.product.name if a.batch and a.batch.product else 'Unknown Product',
                'location_name': a.batch.location.name if a.batch and a.batch.location else 'Unknown Location',
                'adjustment_date': a.created_at.strftime('%Y-%m-%d') if a.created_at else '',
                'adjustment_type': a.adjustment_type,
                'quantity': float(a.quantity),
                'unit_cost': float(a.batch.unit_cost or 0) if a.batch else 0,
                'remarks': a.remarks or '',
                'notes': a.remarks or '',  # Alias for compatibility
                'created_at': a.created_at.isoformat() if a.created_at else None,
                'created_by': a.user.full_name if a.user else 'System'
            }
            records.append(record)

        return jsonify({
            'success': True,
            'records': records
        })
    except Exception as e:
        print(f"ERROR in api_get_adjustments: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/products/<int:product_id>', methods=['PUT'])
@login_required
def api_update_product(product_id):
    """Update an existing product"""
    try:
        from .models import InventoryProduct
        
        data = request.get_json()
        product = InventoryProduct.query.get(product_id)
        
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
        if data.get('is_service_item') is not None or data.get('trackBatches') is not None:
            product.is_service_item = data.get('is_service_item', False) or data.get('trackBatches', False)
        if data.get('is_retail_item') is not None or data.get('trackSerials') is not None:
            product.is_retail_item = data.get('is_retail_item', True) or data.get('trackSerials', True)
        
        product.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Product updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"ERROR updating product: {str(e)}")
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

        if data.get('product_id'):
            batch.product_id = int(data['product_id'])
        
        if data.get('location_id'):
            batch.location_id = data['location_id']

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

@app.route('/api/inventory/batches/<int:batch_id>', methods=['GET'])
@login_required
def api_get_batch(batch_id):
    """Get a single batch by ID"""
    try:
        from sqlalchemy.orm import joinedload
        
        batch = InventoryBatch.query.options(
            joinedload(InventoryBatch.product),
            joinedload(InventoryBatch.location)
        ).get(batch_id)
        
        if not batch or batch.status == 'deleted':
            return jsonify({'error': 'Batch not found'}), 404

        return jsonify({
            'success': True,
            'batch': {
                'id': batch.id,
                'batch_name': batch.batch_name,
                'product_id': batch.product_id,
                'location_id': batch.location_id,
                'product_name': batch.product.name if batch.product else 'Not Assigned',
                'location_name': batch.location.name if batch.location else 'Not Assigned',
                'created_date': batch.created_date.isoformat() if batch.created_date else None,
                'mfg_date': batch.mfg_date.isoformat() if batch.mfg_date else None,
                'expiry_date': batch.expiry_date.isoformat() if batch.expiry_date else None,
                'qty_available': float(batch.qty_available or 0),
                'unit_cost': float(batch.unit_cost or 0),
                'selling_price': float(batch.selling_price or 0) if batch.selling_price else None,
                'status': batch.status,
                'is_expired': batch.is_expired,
                'days_to_expiry': batch.days_to_expiry
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/batches/<int:batch_id>', methods=['DELETE'])
@login_required
def api_delete_batch(batch_id):
    """Delete a batch (soft delete - mark as inactive)"""
    try:
        from datetime import datetime
        batch = InventoryBatch.query.get(batch_id)
        
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404

        # Check if batch has stock - prevent deletion if it does
        if batch.qty_available and float(batch.qty_available) > 0:
            return jsonify({'error': 'Cannot delete batch with remaining stock. Current stock: ' + str(batch.qty_available)}), 400

        # Soft delete - mark as inactive
        batch.status = 'deleted'
        batch.updated_at = datetime.utcnow()
        
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Batch deleted successfully'
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

@app.route('/api/inventory/adjustments/<int:adjustment_id>', methods=['GET'])
@login_required
def api_get_adjustment(adjustment_id):
    """Get single adjustment for viewing"""
    try:
        from sqlalchemy.orm import joinedload
        
        adjustment = InventoryAdjustment.query.options(
            joinedload(InventoryAdjustment.batch).joinedload(InventoryBatch.product),
            joinedload(InventoryAdjustment.batch).joinedload(InventoryBatch.location),
            joinedload(InventoryAdjustment.user)
        ).get(adjustment_id)
        
        if not adjustment:
            return jsonify({'error': 'Adjustment not found'}), 404

        reference_id = f"ADJ-{adjustment.created_at.strftime('%Y%m%d-%H%M%S')}-{adjustment.id}" if adjustment.created_at else f"ADJ-{adjustment.id}"
        
        return jsonify({
            'success': True,
            'id': adjustment.id,
            'reference_id': reference_id,
            'batch_name': adjustment.batch.batch_name if adjustment.batch else 'Unknown Batch',
            'product_name': adjustment.batch.product.name if adjustment.batch and adjustment.batch.product else 'Unknown Product',
            'location_name': adjustment.batch.location.name if adjustment.batch and adjustment.batch.location else 'Unknown Location',
            'adjustment_date': adjustment.created_at.strftime('%Y-%m-%d') if adjustment.created_at else '',
            'quantity': float(adjustment.quantity),
            'remarks': adjustment.remarks or '',
            'created_by': adjustment.user.full_name if adjustment.user else 'System',
            'created_at': adjustment.created_at.isoformat() if adjustment.created_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/adjustments/<int:adjustment_id>', methods=['DELETE'])
@login_required
def api_delete_adjustment(adjustment_id):
    """Delete adjustment and reverse stock change"""
    try:
        adjustment = InventoryAdjustment.query.get(adjustment_id)
        if not adjustment:
            return jsonify({'error': 'Adjustment not found'}), 404

        batch = adjustment.batch
        if batch:
            # Reverse the adjustment
            if adjustment.adjustment_type == 'add':
                batch.qty_available = float(batch.qty_available or 0) - float(adjustment.quantity)
            else:
                batch.qty_available = float(batch.qty_available or 0) + float(adjustment.quantity)
            
            # Ensure stock doesn't go negative
            if batch.qty_available < 0:
                batch.qty_available = 0

        db.session.delete(adjustment)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Adjustment deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/batches/for-adjustment', methods=['GET'])
@login_required
def api_get_batches_for_adjustment():
    """Get batches available for adjustments"""
    try:
        from sqlalchemy.orm import joinedload
        
        batches = InventoryBatch.query.options(
            joinedload(InventoryBatch.product),
            joinedload(InventoryBatch.location)
        ).filter(InventoryBatch.status == 'active').order_by(InventoryBatch.batch_name).all()

        batch_list = []
        for b in batches:
            batch_data = {
                'id': b.id,
                'batch_name': b.batch_name,
                'product_id': b.product_id,
                'product_name': b.product.name if b.product else 'Not Assigned',
                'location_id': b.location_id,
                'location_name': b.location.name if b.location else 'Not Assigned',
                'qty_available': float(b.qty_available or 0),
                'unit': b.product.unit_of_measure if b.product else 'pcs',
                'expiry_date': b.expiry_date.isoformat() if b.expiry_date else None,
                'unit_cost': float(b.unit_cost or 0)
            }
            batch_list.append(batch_data)

        return jsonify({
            'success': True,
            'batches': batch_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/test', methods=['GET'])
@login_required
def api_test_inventory():
    """Test endpoint to verify all inventory APIs are working"""
    try:
        # Test products
        products = get_all_products()
        
        # Test locations
        locations = get_all_locations()
        
        # Test batches
        batches = InventoryBatch.query.filter(InventoryBatch.status != 'deleted').all()
        
        # Test categories
        categories = get_all_categories()
        
        return jsonify({
            'success': True,
            'data': {
                'products_count': len(products),
                'locations_count': len(locations),
                'batches_count': len(batches),
                'categories_count': len(categories),
                'sample_product': products[0].name if products else 'No products',
                'sample_location': locations[0].name if locations else 'No locations',
                'sample_batch': batches[0].batch_name if batches else 'No batches'
            },
            'message': 'All inventory APIs are working correctly'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error testing inventory APIs'
        }), 500