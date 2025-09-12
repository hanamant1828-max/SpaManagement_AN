from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import app, db
from .models import InventoryProduct, InventoryCategory, InventoryLocation, InventoryBatch, InventoryAdjustment, InventoryConsumption, InventoryTransfer
from .queries import *
from datetime import datetime, date, timedelta
import json

@app.route('/inventory')

def inventory_dashboard():
    """Inventory dashboard main page"""
    if False:
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
            created_by=1  # Default user ID for testing (no login_manager)
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

def api_get_consumption_records():
    """Get consumption records"""
    try:
        # Get filter parameters
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        search = request.args.get('search', '')
        
        # Get all consumption records first
        query = InventoryConsumption.query
        
        # Apply date filters if provided
        if from_date:
            try:
                from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
                query = query.filter(InventoryConsumption.created_at >= from_date_obj)
            except ValueError:
                pass  # Invalid date format, ignore
                
        if to_date:
            try:
                to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
                # Add one day to include records from the entire to_date day
                to_date_obj = to_date_obj + timedelta(days=1)
                query = query.filter(InventoryConsumption.created_at < to_date_obj)
            except ValueError:
                pass  # Invalid date format, ignore
        
        # Apply search filter if provided
        if search:
            query = query.join(InventoryBatch).join(InventoryProduct).filter(
                or_(
                    InventoryConsumption.issued_to.ilike(f'%{search}%'),
                    InventoryConsumption.reference.ilike(f'%{search}%'),
                    InventoryConsumption.notes.ilike(f'%{search}%'),
                    InventoryBatch.batch_name.ilike(f'%{search}%'),
                    InventoryProduct.name.ilike(f'%{search}%')
                )
            )
        
        # Get filtered records ordered by creation date (newest first)
        consumption_records = query.order_by(InventoryConsumption.created_at.desc()).limit(100).all()
        
        records_data = [{
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
        } for c in consumption_records]
        
        return jsonify({
            'success': True,
            'data': records_data,
            'pagination': {
                'page': 1,
                'pages': 1,
                'total': len(records_data)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/consumption', methods=['POST'])

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
            user_id=1  # Default user ID for testing (no login_manager)
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

@app.route('/api/inventory/categories/<int:category_id>', methods=['DELETE'])
def api_delete_category(category_id):
    """Delete (deactivate) a category"""
    try:
        from .models import InventoryCategory, InventoryProduct
        from datetime import datetime
        
        category = InventoryCategory.query.get(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        # Check if category has associated products
        product_count = InventoryProduct.query.filter_by(category_id=category_id, is_active=True).count()
        if product_count > 0:
            return jsonify({'error': f'Cannot delete category with {product_count} associated products. Please remove or reassign products first.'}), 400
        
        # Soft delete - mark as inactive
        category.is_active = False
        category.updated_at = datetime.utcnow()
        db.session.commit()
            
        return jsonify({
            'success': True,
            'message': 'Category deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"ERROR deleting category: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/locations/<location_id>', methods=['PUT'])

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

@app.route('/api/inventory/locations/<location_id>', methods=['DELETE'])
def api_delete_location(location_id):
    """Delete (deactivate) a location"""
    try:
        from .models import InventoryLocation, InventoryBatch
        from datetime import datetime
        
        location = InventoryLocation.query.get(location_id)
        if not location:
            return jsonify({'error': 'Location not found'}), 404
        
        # Check if location has associated batches
        batch_count = InventoryBatch.query.filter_by(location_id=location_id).filter(InventoryBatch.status != 'deleted').count()
        if batch_count > 0:
            return jsonify({'error': f'Cannot delete location with {batch_count} associated batches. Please remove or reassign batches first.'}), 400
        
        # Soft delete - mark as inactive
        location.status = 'inactive'
        location.updated_at = datetime.utcnow()
        db.session.commit()
            
        return jsonify({
            'success': True,
            'message': 'Location deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"ERROR deleting location: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/batches/<int:batch_id>', methods=['PUT'])

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


@app.route('/api/inventory/status', methods=['GET'])

def api_get_inventory_status():
    """Get comprehensive inventory status overview"""
    try:
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        # Product counts by category
        category_stats = db.session.query(
            InventoryCategory.name,
            func.count(InventoryProduct.id).label('product_count')
        ).join(InventoryProduct).filter(
            InventoryProduct.is_active == True
        ).group_by(InventoryCategory.name).all()
        
        # Overall stock levels
        total_products = InventoryProduct.query.filter(InventoryProduct.is_active == True).count()
        total_batches = InventoryBatch.query.filter(InventoryBatch.status == 'active').count()
        
        # Calculate stock status counts
        stock_summary = {
            'in_stock': 0,
            'low_stock': 0, 
            'out_of_stock': 0
        }
        
        # Low stock and expired items
        low_stock_items = []
        expired_batches = []
        expiring_soon = []
        
        # Calculate total inventory value
        total_value = 0
        
        # Process all active products
        products = InventoryProduct.query.filter(InventoryProduct.is_active == True).all()
        
        for product in products:
            active_batches = [b for b in product.batches if b.status == 'active']
            total_stock = sum(float(batch.qty_available or 0) for batch in active_batches)
            
            # Stock status categorization
            if total_stock <= 0:
                stock_summary['out_of_stock'] += 1
                low_stock_items.append({
                    'id': product.id,
                    'name': product.name,
                    'sku': product.sku,
                    'current_stock': total_stock,
                    'status': 'out_of_stock'
                })
            elif total_stock <= 10:  # Low stock threshold
                stock_summary['low_stock'] += 1
                low_stock_items.append({
                    'id': product.id,
                    'name': product.name,
                    'sku': product.sku,
                    'current_stock': total_stock,
                    'status': 'low_stock'
                })
            else:
                stock_summary['in_stock'] += 1
            
            # Calculate value from batches
            for batch in active_batches:
                if batch.qty_available and batch.unit_cost:
                    total_value += float(batch.qty_available) * float(batch.unit_cost)
        
        # Check for expired and expiring batches
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        
        all_batches = InventoryBatch.query.filter(InventoryBatch.status == 'active').all()
        
        for batch in all_batches:
            if batch.expiry_date:
                if batch.expiry_date < today:
                    expired_batches.append({
                        'id': batch.id,
                        'batch_name': batch.batch_name,
                        'product_name': batch.product.name if batch.product else 'Unknown',
                        'expiry_date': batch.expiry_date.isoformat(),
                        'qty_available': float(batch.qty_available or 0)
                    })
                elif batch.expiry_date <= next_week:
                    expiring_soon.append({
                        'id': batch.id,
                        'batch_name': batch.batch_name,
                        'product_name': batch.product.name if batch.product else 'Unknown',
                        'expiry_date': batch.expiry_date.isoformat(),
                        'qty_available': float(batch.qty_available or 0),
                        'days_until_expiry': (batch.expiry_date - today).days
                    })
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_consumption = InventoryConsumption.query.filter(
            InventoryConsumption.created_at >= week_ago
        ).count()
        
        recent_adjustments = InventoryAdjustment.query.filter(
            InventoryAdjustment.created_at >= week_ago
        ).count()
        
        # Get all batches with detailed information
        all_batches_detailed = []
        batches = InventoryBatch.query.filter(InventoryBatch.status == 'active').all()
        
        for batch in batches:
            batch_data = {
                'id': batch.id,
                'batch_name': batch.batch_name,
                'product_name': batch.product.name if batch.product else 'Unknown',
                'product_sku': batch.product.sku if batch.product else '',
                'location_name': batch.location.name if batch.location else 'Unknown',
                'location_id': batch.location_id,
                'qty_available': float(batch.qty_available or 0),
                'unit_of_measure': batch.product.unit_of_measure if batch.product else 'pcs',
                'unit_cost': float(batch.unit_cost or 0),
                'total_value': float(batch.qty_available or 0) * float(batch.unit_cost or 0),
                'mfg_date': batch.mfg_date.isoformat() if batch.mfg_date else None,
                'expiry_date': batch.expiry_date.isoformat() if batch.expiry_date else None,
                'status': batch.status
            }
            all_batches_detailed.append(batch_data)
        
        # Get product-wise totals
        product_wise_totals = []
        for product in products:
            active_batches = [b for b in product.batches if b.status == 'active']
            total_qty = sum(float(batch.qty_available or 0) for batch in active_batches)
            total_value_product = sum(float(batch.qty_available or 0) * float(batch.unit_cost or 0) for batch in active_batches)
            batch_count = len(active_batches)
            
            # Determine status
            if total_qty <= 0:
                status = 'out_of_stock'
            elif total_qty <= 10:
                status = 'low_stock'
            else:
                status = 'in_stock'
            
            product_data = {
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'category': product.category.name if product.category else 'Uncategorized',
                'unit_of_measure': product.unit_of_measure or 'pcs',
                'total_quantity': total_qty,
                'total_value': round(total_value_product, 2),
                'batch_count': batch_count,
                'status': status
            }
            product_wise_totals.append(product_data)

        return jsonify({
            'success': True,
            'overview': {
                'total_products': total_products,
                'total_batches': total_batches,
                'total_inventory_value': round(total_value, 2),
                'stock_summary': stock_summary
            },
            'category_breakdown': [
                {'category': cat[0], 'product_count': cat[1]} 
                for cat in category_stats
            ],
            'alerts': {
                'low_stock_count': len([item for item in low_stock_items if item['status'] == 'low_stock']),
                'out_of_stock_count': len([item for item in low_stock_items if item['status'] == 'out_of_stock']),
                'expired_batches_count': len(expired_batches),
                'expiring_soon_count': len(expiring_soon)
            },
            'low_stock_items': low_stock_items[:10],  # Limit to top 10
            'expired_batches': expired_batches[:10],
            'expiring_soon': expiring_soon[:10],
            'recent_activity': {
                'consumption_records': recent_consumption,
                'adjustments': recent_adjustments
            },
            'batch_wise_data': all_batches_detailed,
            'product_wise_data': product_wise_totals
        })
        
    except Exception as e:
        print(f"Error getting inventory status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# INVENTORY REPORTS SECTION
# =============================================================================

@app.route('/inventory/reports')

def inventory_reports():
    """Inventory reports page with dropdown selection"""
    if False:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # Default to last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        # Get date range from request
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                
                # Validate date range
                if start_date > end_date:
                    flash('Start date cannot be after end date', 'danger')
                    start_date = end_date - timedelta(days=30)
                    
            except ValueError:
                flash('Invalid date format. Using default date range.', 'warning')
                end_date = date.today()
                start_date = end_date - timedelta(days=30)
        
        return render_template('inventory_reports.html', 
                             start_date=start_date, 
                             end_date=end_date)
    except Exception as e:
        print(f"Inventory reports error: {e}")
        flash('Error loading inventory reports', 'danger')
        return redirect(url_for('inventory_dashboard'))


@app.route('/api/inventory/reports/product-wise', methods=['GET'])

def api_get_product_wise_report():
    """Get product-wise report with current quantities"""
    # Authorization check
    if False:
        return jsonify({
            'success': False,
            'error': 'Access denied. You do not have permission to access inventory reports.'
        }), 403
    
    try:
        from sqlalchemy.orm import joinedload
        
        # Use joinedload to prevent N+1 queries
        products = InventoryProduct.query.options(
            joinedload(InventoryProduct.category),
            joinedload(InventoryProduct.batches)
        ).filter(InventoryProduct.is_active == True).all()
        
        report_data = []
        for product in products:
            # Calculate current stock from active batches
            total_qty = sum(float(batch.qty_available or 0) for batch in product.batches if batch.status == 'active')
            total_value = sum(float(batch.qty_available or 0) * float(batch.unit_cost or 0) for batch in product.batches if batch.status == 'active')
            batch_count = len([b for b in product.batches if b.status == 'active'])
            
            # Determine stock status
            if total_qty <= 0:
                status = 'out_of_stock'
            elif total_qty <= 10:
                status = 'low_stock'
            else:
                status = 'in_stock'
            
            report_data.append({
                'product_name': product.name,
                'sku': product.sku,
                'category': product.category.name if product.category else 'Uncategorized',
                'unit_of_measure': product.unit_of_measure or 'pcs',
                'current_quantity': total_qty,
                'total_value': round(total_value, 2),
                'batch_count': batch_count,
                'status': status
            })
        
        return jsonify({
            'success': True,
            'report_type': 'Product-wise Report',
            'data': report_data,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error generating product-wise report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/inventory/reports/batch-wise', methods=['GET'])
  
def api_get_batch_wise_report():
    """Get batch-wise report with current quantities"""
    # Authorization check
    if False:
        return jsonify({
            'success': False,
            'error': 'Access denied. You do not have permission to access inventory reports.'
        }), 403
    
    try:
        from sqlalchemy.orm import joinedload
        
        batches = InventoryBatch.query.options(
            joinedload(InventoryBatch.product),
            joinedload(InventoryBatch.location)
        ).filter(InventoryBatch.status == 'active').all()
        
        report_data = []
        for batch in batches:
            total_value = float(batch.qty_available or 0) * float(batch.unit_cost or 0)
            
            report_data.append({
                'batch_name': batch.batch_name,
                'product_name': batch.product.name if batch.product else 'Unknown',
                'sku': batch.product.sku if batch.product else 'N/A',
                'location': batch.location.name if batch.location else 'Unknown',
                'current_quantity': float(batch.qty_available or 0),
                'unit_of_measure': batch.product.unit_of_measure if batch.product else 'pcs',
                'unit_cost': float(batch.unit_cost or 0),
                'total_value': round(total_value, 2),
                'mfg_date': batch.mfg_date.isoformat() if batch.mfg_date else None,
                'expiry_date': batch.expiry_date.isoformat() if batch.expiry_date else None
            })
        
        return jsonify({
            'success': True,
            'report_type': 'Batch-wise Report',
            'data': report_data,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error generating batch-wise report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/inventory/reports/consumption-today', methods=['GET'])

def api_get_consumption_today_report():
    """Get today's consumption report"""
    # Authorization check
    if False:
        return jsonify({
            'success': False,
            'error': 'Access denied. You do not have permission to access inventory reports.'
        }), 403
    
    try:
        from sqlalchemy.orm import joinedload
        
        today = date.today()
        consumption_records = InventoryConsumption.query.options(
            joinedload(InventoryConsumption.batch).joinedload(InventoryBatch.product),
            joinedload(InventoryConsumption.user)
        ).filter(
            db.func.date(InventoryConsumption.created_at) == today
        ).all()
        
        report_data = []
        for record in consumption_records:
            batch = record.batch
            product = batch.product if batch else None
            
            report_data.append({
                'consumption_date': record.created_at.isoformat() if record.created_at else None,
                'batch_name': batch.batch_name if batch else 'Unknown',
                'product_name': product.name if product else 'Unknown',
                'sku': product.sku if product else 'N/A',
                'quantity_consumed': float(record.quantity or 0),
                'unit_of_measure': product.unit_of_measure if product else 'pcs',
                'purpose': record.issued_to or 'Service',
                'staff_member': record.user.username if record.user else 'Unknown',
                'notes': record.notes or ''
            })
        
        total_consumed_items = len(report_data)
        total_quantity_consumed = sum(float(record['quantity_consumed']) for record in report_data)
        
        return jsonify({
            'success': True,
            'report_type': 'Today\'s Consumption Report',
            'data': report_data,
            'summary': {
                'total_items_consumed': total_consumed_items,
                'total_quantity_consumed': total_quantity_consumed,
                'report_date': today.isoformat()
            },
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error generating consumption report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/inventory/reports/consumption', methods=['GET'])

def api_get_consumption_report():
    """Get consumption report for specified date range"""
    # Authorization check
    if False:
        return jsonify({
            'success': False,
            'error': 'Access denied. You do not have permission to access inventory reports.'
        }), 403
    
    try:
        from sqlalchemy.orm import joinedload
        from datetime import datetime
        
        # Get date parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'error': 'Both start_date and end_date parameters are required'
            }), 400
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD format.'
            }), 400
        
        # Get consumption records within date range
        consumption_records = InventoryConsumption.query.options(
            joinedload(InventoryConsumption.batch).joinedload(InventoryBatch.product),
            joinedload(InventoryConsumption.user)
        ).filter(
            db.func.date(InventoryConsumption.created_at) >= start_date,
            db.func.date(InventoryConsumption.created_at) <= end_date
        ).order_by(InventoryConsumption.created_at.desc()).all()
        
        report_data = []
        for record in consumption_records:
            batch = record.batch
            product = batch.product if batch else None
            
            report_data.append({
                'consumption_date': record.created_at.isoformat() if record.created_at else None,
                'batch_name': batch.batch_name if batch else 'Unknown',
                'product_name': product.name if product else 'Unknown',
                'sku': product.sku if product else 'N/A',
                'quantity_consumed': float(record.quantity or 0),
                'unit_of_measure': product.unit_of_measure if product else 'pcs',
                'purpose': record.issued_to or 'Service',
                'staff_member': record.user.username if record.user else 'Unknown',
                'notes': record.notes or ''
            })
        
        total_consumed_items = len(report_data)
        total_quantity_consumed = sum(float(record['quantity_consumed']) for record in report_data)
        
        return jsonify({
            'success': True,
            'report_type': f'Consumption Report ({start_date} to {end_date})',
            'data': report_data,
            'summary': {
                'total_items_consumed': total_consumed_items,
                'total_quantity_consumed': total_quantity_consumed,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error generating consumption report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/inventory/reports/adjustments', methods=['GET'])

def api_get_adjustments_report():
    """Get adjustments report for specified date range"""
    # Authorization check
    if False:
        return jsonify({
            'success': False,
            'error': 'Access denied. You do not have permission to access inventory reports.'
        }), 403
    
    try:
        from sqlalchemy.orm import joinedload
        from datetime import datetime
        
        # Get date parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'error': 'Both start_date and end_date parameters are required'
            }), 400
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD format.'
            }), 400
        
        # Get adjustment records within date range
        adjustment_records = InventoryAdjustment.query.options(
            joinedload(InventoryAdjustment.batch).joinedload(InventoryBatch.product),
            joinedload(InventoryAdjustment.user)
        ).filter(
            db.func.date(InventoryAdjustment.created_at) >= start_date,
            db.func.date(InventoryAdjustment.created_at) <= end_date
        ).order_by(InventoryAdjustment.created_at.desc()).all()
        
        report_data = []
        total_adjustments = 0
        net_quantity_change = 0
        
        for record in adjustment_records:
            batch = record.batch
            product = batch.product if batch else None
            
            # Calculate quantity change based on adjustment type
            quantity_change = float(record.quantity_change or 0)
            if record.adjustment_type == 'decrease':
                quantity_change = -abs(quantity_change)
            
            net_quantity_change += quantity_change
            total_adjustments += 1
            
            report_data.append({
                'adjustment_date': record.created_at.isoformat() if record.created_at else None,
                'batch_name': batch.batch_name if batch else 'Unknown',
                'product_name': product.name if product else 'Unknown',
                'sku': product.sku if product else 'N/A',
                'adjustment_type': record.adjustment_type or 'unknown',
                'quantity_change': quantity_change,
                'unit_of_measure': product.unit_of_measure if product else 'pcs',
                'staff_member': record.user.username if record.user else 'Unknown',
                'reason': record.reason or ''
            })
        
        return jsonify({
            'success': True,
            'report_type': f'Stock Adjustments Report ({start_date} to {end_date})',
            'data': report_data,
            'summary': {
                'total_adjustments': total_adjustments,
                'net_quantity_change': net_quantity_change,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error generating adjustments report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/inventory/reports/item-batch-wise', methods=['GET'])

def api_get_item_batch_wise_report():
    """Get item-wise batch-wise detailed report"""
    # Authorization check
    if False:
        return jsonify({
            'success': False,
            'error': 'Access denied. You do not have permission to access inventory reports.'
        }), 403
    
    try:
        from sqlalchemy.orm import joinedload
        
        # Get all products with their batches
        products = InventoryProduct.query.options(
            joinedload(InventoryProduct.category),
            joinedload(InventoryProduct.batches).joinedload(InventoryBatch.location)
        ).filter(InventoryProduct.is_active == True).all()
        
        report_data = []
        for product in products:
            # Get all active batches for this product
            active_batches = [b for b in product.batches if b.status == 'active']
            
            # Calculate product totals
            total_qty = sum(float(batch.qty_available or 0) for batch in active_batches)
            total_value = sum(float(batch.qty_available or 0) * float(batch.unit_cost or 0) for batch in active_batches)
            
            # Create product entry with batch details
            product_entry = {
                'product_name': product.name,
                'sku': product.sku,
                'category': product.category.name if product.category else 'Uncategorized',
                'unit_of_measure': product.unit_of_measure or 'pcs',
                'total_quantity': total_qty,
                'total_value': round(total_value, 2),
                'batch_count': len(active_batches),
                'batches': []
            }
            
            # Add batch details
            for batch in active_batches:
                batch_value = float(batch.qty_available or 0) * float(batch.unit_cost or 0)
                product_entry['batches'].append({
                    'batch_name': batch.batch_name,
                    'location': batch.location.name if batch.location else 'Unknown',
                    'quantity': float(batch.qty_available or 0),
                    'unit_cost': float(batch.unit_cost or 0),
                    'total_value': round(batch_value, 2),
                    'mfg_date': batch.mfg_date.isoformat() if batch.mfg_date else None,
                    'expiry_date': batch.expiry_date.isoformat() if batch.expiry_date else None
                })
            
            report_data.append(product_entry)
        
        return jsonify({
            'success': True,
            'report_type': 'Item-wise Batch-wise Report',
            'data': report_data,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error generating item-batch-wise report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500