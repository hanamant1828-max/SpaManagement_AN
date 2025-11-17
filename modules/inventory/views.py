from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import app, db
from .models import InventoryProduct, InventoryCategory, InventoryLocation, InventoryBatch, InventoryAdjustment, InventoryConsumption, InventoryTransfer
from .queries import *
from datetime import datetime, date
from sqlalchemy import or_, desc
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
            'category_name': p.category.name if p.category else 'No Category',
            'sku': p.sku,
            'unit_of_measure': p.unit_of_measure,
            'barcode': p.barcode,
            'total_stock': float(p.total_stock),  # Dynamic property from batches
            'batch_count': p.batch_count,  # Number of batches for this product
            'is_active': p.is_active,
            'is_service_item': p.is_service_item,
            'is_retail_item': p.is_retail_item,
            'stock_status': p.stock_status  # Add stock status for better UI display
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

@app.route('/api/inventory/batches/for-product/<int:product_id>')
@login_required
def api_get_batches_for_product(product_id):
    """Get batches for a specific product ordered by FIFO (expiry date)"""
    try:
        from datetime import date
        from sqlalchemy.orm import joinedload

        # Get active batches for the product with stock, ordered by expiry (FIFO)
        batches = InventoryBatch.query.options(
            joinedload(InventoryBatch.product),
            joinedload(InventoryBatch.location)
        ).filter(
            InventoryBatch.product_id == product_id,
            InventoryBatch.status == 'active',
            InventoryBatch.qty_available > 0
        ).order_by(
            InventoryBatch.expiry_date.asc().nullslast(),
            InventoryBatch.batch_name
        ).all()

        batch_data = []
        for batch in batches:
            # Check if batch is expired
            is_expired = batch.expiry_date and batch.expiry_date < date.today()

            # Skip expired batches
            if is_expired:
                continue

            batch_info = {
                'id': batch.id,
                'batch_name': batch.batch_name,
                'product_id': batch.product_id,
                'location_id': batch.location_id,
                'location_name': batch.location.name if batch.location else 'Unassigned',
                'qty_available': float(batch.qty_available or 0),
                'unit_cost': float(batch.unit_cost or 0),
                'selling_price': float(batch.selling_price or 0) if batch.selling_price else float(batch.unit_cost or 0),
                'expiry_date': batch.expiry_date.isoformat() if batch.expiry_date else None,
                'days_to_expiry': batch.days_to_expiry,
                'is_expired': False,
                'status': batch.status
            }
            batch_data.append(batch_info)

        return jsonify({
            'success': True,
            'batches': batch_data
        })
    except Exception as e:
        print(f"Error in api_get_batches_for_product: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'batches': []
        }), 500

@app.route('/api/inventory/adjustments', methods=['POST'])
@login_required
def api_create_adjustment():
    """Create inventory adjustment and assign product/location to batch if needed"""
    try:
        from decimal import Decimal
        data = request.get_json()

        # Handle both single item and items array structures
        if 'items' in data and data['items']:
            # New structure with items array
            item = data['items'][0]  # Get first item
            batch_id = item.get('batch_id')
            quantity = Decimal(str(item.get('quantity_in', 0)))
            unit_cost = Decimal(str(item.get('unit_cost', 0)))
            product_id = item.get('product_id')
            location_id = item.get('location_id')
            adjustment_type = item.get('adjustment_type', 'add')
        else:
            # Direct structure
            batch_id = data.get('batch_id')
            quantity = Decimal(str(data.get('quantity', 0)))
            unit_cost = Decimal(str(data.get('unit_cost', 0)))
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
            if quantity > batch.qty_available:
                return jsonify({'error': f'Cannot remove {quantity}. Only {batch.qty_available} available in stock.'}), 400

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
            created_by=current_user.id
        )

        # Update batch quantity based on adjustment type with Decimal arithmetic
        if adjustment_type == 'add':
            batch.qty_available = batch.qty_available + quantity
            if unit_cost > 0:
                batch.unit_cost = unit_cost
        else:  # remove
            batch.qty_available = batch.qty_available - quantity
            # Ensure qty_available doesn't go negative
            if batch.qty_available < 0:
                batch.qty_available = Decimal('0')

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
        # Show all active batches, but prioritize those with available stock
        batches = InventoryBatch.query.options(
            joinedload(InventoryBatch.product),
            joinedload(InventoryBatch.location)
        ).filter(
            InventoryBatch.status == 'active'
        ).order_by(
            InventoryBatch.qty_available.desc().nullslast(),
            InventoryBatch.expiry_date.asc().nullslast(),
            InventoryBatch.batch_name
        ).all()

        batch_data = []
        print(f"📊 Total batches found for consumption: {len(batches)}")

        for batch in batches:
            qty_available = float(batch.qty_available or 0)
            unit = batch.product.unit_of_measure if batch.product else 'pcs'
            product_name = batch.product.name if batch.product else 'Unassigned'
            location_name = batch.location.name if batch.location else 'Unassigned'

            print(f"📦 Processing batch: {batch.batch_name}, Status: {batch.status}, Qty: {qty_available}")

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

@app.route('/api/inventory/batches/for-adjustment', methods=['GET'])
@login_required
def api_get_batches_for_adjustment():
    """Get batches available for inventory adjustments"""
    try:
        from .models import InventoryBatch
        from datetime import date
        from sqlalchemy.orm import joinedload

        # Get all active batches (include all for adjustments, even with 0 stock)
        batches = InventoryBatch.query.options(
            joinedload(InventoryBatch.product),
            joinedload(InventoryBatch.location)
        ).filter(
            InventoryBatch.status == 'active'
        ).order_by(InventoryBatch.expiry_date.asc().nullslast(), InventoryBatch.batch_name).all()

        print(f"🔧 Total batches found for adjustment: {len(batches)}")

        batch_data = []
        for batch in batches:
            product_name = batch.product.name if batch.product else 'Unassigned'
            location_name = batch.location.name if batch.location else 'Unassigned'
            unit = batch.product.unit_of_measure if batch.product else 'pcs'

            # Create display text for dropdown
            expiry_text = f", Exp: {batch.expiry_date.strftime('%d/%m/%Y')}" if batch.expiry_date else ""
            dropdown_display = f"{batch.batch_name} ({product_name}{expiry_text}) - Available: {batch.qty_available} {unit}"

            batch_info = {
                'id': batch.id,
                'batch_name': batch.batch_name,
                'product_id': batch.product_id,
                'product_name': product_name,
                'location_id': batch.location_id,
                'location_name': location_name,
                'qty_available': float(batch.qty_available or 0),
                'unit_cost': float(batch.unit_cost or 0),
                'unit': unit,
                'expiry_date': batch.expiry_date.isoformat() if batch.expiry_date else None,
                'days_to_expiry': batch.days_to_expiry,
                'is_expired': batch.is_expired,
                'status': batch.status,
                'dropdown_display': dropdown_display
            }
            batch_data.append(batch_info)

        return jsonify({
            'success': True,
            'batches': batch_data
        })
    except Exception as e:
        print(f"Error in api_get_batches_for_adjustment: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============ BATCH-CENTRIC CONSUMPTION ENDPOINTS ============

@app.route('/api/inventory/consumption', methods=['GET'])
@login_required
def api_get_consumption_records():
    """Get consumption records with pagination support"""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))
        from_date = request.args.get('from_date', '')
        to_date = request.args.get('to_date', '')
        search = request.args.get('search', '')

        # Build query
        query = InventoryConsumption.query

        # Apply date filters
        if from_date:
            from datetime import datetime
            start_date = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(InventoryConsumption.created_at >= start_date)

        if to_date:
            from datetime import datetime
            end_date = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(InventoryConsumption.created_at <= end_date)

        # Apply search filter
        if search:
            query = query.join(InventoryBatch).filter(
                or_(
                    InventoryBatch.batch_name.ilike(f'%{search}%'),
                    InventoryConsumption.reference.ilike(f'%{search}%'),
                    InventoryConsumption.notes.ilike(f'%{search}%'),
                    InventoryConsumption.issued_to.ilike(f'%{search}%')
                )
            )

        # Order by created_at desc
        query = query.order_by(desc(InventoryConsumption.created_at))

        # Get total count
        total = query.count()
        total_pages = (total + per_page - 1) // per_page

        # Apply pagination
        consumption_records = query.offset((page - 1) * per_page).limit(per_page).all()

        # Format response data
        consumption_data = []
        for c in consumption_records:
            unit_of_measure = c.batch.product.unit_of_measure if c.batch and c.batch.product else 'pcs'
            consumption_data.append({
                'id': c.id,
                'batch_id': c.batch_id,
                'batch_name': c.batch.batch_name if c.batch else 'Unknown',
                'product_name': c.batch.product.name if c.batch and c.batch.product else 'Unknown',
                'quantity': float(c.quantity),
                'unit_of_measure': unit_of_measure,
                'issued_to': c.issued_to,
                'reference': c.reference or '',
                'purpose': getattr(c, 'purpose', 'other'),
                'notes': c.notes or '',
                'created_at': c.created_at.isoformat() if c.created_at else None,
                'created_by_name': c.user.full_name if c.user else 'Unknown'
            })

        return jsonify({
            'success': True,
            'data': consumption_data,
            'total': total,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        print(f"Error in api_get_consumption_records: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': [],
            'total': 0,
            'total_pages': 1
        }), 500

@app.route('/api/inventory/consumption', methods=['POST'])
@login_required
def api_create_consumption():
    """Create consumption record - BATCH-CENTRIC"""
    try:
        from decimal import Decimal
        data = request.get_json()

        # Validate required fields
        required_fields = ['batch_id', 'quantity', 'issued_to']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        batch_id = data['batch_id']
        quantity = Decimal(str(data['quantity']))
        issued_to = data['issued_to']
        reference = data.get('reference', '')
        notes = data.get('notes', '')

        # Get the batch and validate
        batch = InventoryBatch.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404

        if batch.is_expired:
            return jsonify({'error': 'Cannot consume from expired batch'}), 400

        if quantity > batch.qty_available:
            return jsonify({'error': f'Insufficient stock. Available: {batch.qty_available}, Required: {quantity}'}), 400

        # Get purpose from data if provided
        purpose = data.get('purpose', 'other')  # Default to 'other' if not provided

        # Create consumption record
        consumption = InventoryConsumption(
            batch_id=batch_id,
            quantity=quantity,
            issued_to=issued_to,
            reference=reference,
            purpose=purpose,
            notes=notes,
            created_by=current_user.id
        )

        # Update batch quantity with Decimal arithmetic
        batch.qty_available = batch.qty_available - quantity

        db.session.add(consumption)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Consumption record created successfully',
            'consumption_id': consumption.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/consumption/<int:consumption_id>', methods=['GET'])
@login_required
def api_get_consumption(consumption_id):
    """Get specific consumption record"""
    try:
        consumption = InventoryConsumption.query.get(consumption_id)
        if not consumption:
            return jsonify({'error': 'Consumption record not found'}), 404

        unit_of_measure = consumption.batch.product.unit_of_measure if consumption.batch and consumption.batch.product else 'pcs'

        return jsonify({
            'success': True,
            'consumption_date': consumption.created_at.strftime('%Y-%m-%d') if consumption.created_at else '',
            'reference_doc_no': consumption.reference or '',
            'batch_name': consumption.batch.batch_name if consumption.batch else 'Unknown',
            'product_name': consumption.batch.product.name if consumption.batch and consumption.batch.product else 'Unknown',
            'quantity_used': float(consumption.quantity),
            'unit_of_measure': unit_of_measure,
            'issued_to': consumption.issued_to or '',
            'purpose': getattr(consumption, 'purpose', 'Other'),
            'notes': consumption.notes or ''
        })
    except Exception as e:
        print(f"Error in api_get_consumption: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/consumption/<int:consumption_id>', methods=['PUT'])
@login_required
def api_update_consumption(consumption_id):
    """Update consumption record"""
    try:
        from decimal import Decimal
        data = request.get_json()

        consumption = InventoryConsumption.query.get(consumption_id)
        if not consumption:
            return jsonify({'error': 'Consumption record not found'}), 404

        # Store old values for quantity adjustment
        old_quantity = consumption.quantity
        old_batch_id = consumption.batch_id

        # Update consumption fields
        if 'date' in data:
            from datetime import datetime
            consumption.created_at = datetime.strptime(data['date'], '%Y-%m-%d')

        if 'reference' in data:
            consumption.reference = data['reference']

        if 'quantity' in data:
            new_quantity = Decimal(str(data['quantity']))
            consumption.quantity = new_quantity

        if 'issued_to' in data:
            consumption.issued_to = data['issued_to']

        if 'purpose' in data:
            consumption.purpose = data['purpose']

        if 'notes' in data:
            consumption.notes = data['notes']

        # Handle batch change or quantity change
        if 'batch_id' in data and data['batch_id']:
            new_batch_id = int(data['batch_id'])
            new_batch = InventoryBatch.query.get(new_batch_id)
            if not new_batch:
                return jsonify({'error': 'New batch not found'}), 404

            # If batch changed, restore stock to old batch and consume from new batch
            if new_batch_id != old_batch_id:
                # Restore quantity to old batch
                old_batch = InventoryBatch.query.get(old_batch_id)
                if old_batch:
                    old_batch.qty_available = old_batch.qty_available + old_quantity

                # Check if new batch has enough stock
                if consumption.quantity > new_batch.qty_available:
                    return jsonify({'error': f'Insufficient stock in new batch. Available: {new_batch.qty_available}, Required: {consumption.quantity}'}), 400

                # Consume from new batch
                new_batch.qty_available = new_batch.qty_available - consumption.quantity
                consumption.batch_id = new_batch_id

            else:
                # Same batch, just adjust quantity difference
                quantity_difference = consumption.quantity - old_quantity
                if quantity_difference > 0:
                    # Need more stock
                    if quantity_difference > consumption.batch.qty_available:
                        return jsonify({'error': f'Insufficient stock for increase. Available: {consumption.batch.qty_available}, Additional needed: {quantity_difference}'}), 400
                    consumption.batch.qty_available = consumption.batch.qty_available - quantity_difference
                else:
                    # Return excess stock
                    consumption.batch.qty_available = consumption.batch.qty_available + abs(quantity_difference)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Consumption record updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error in api_update_consumption: {e}")
        return jsonify({'error': str(e)}), 500

# ============ BATCH-CENTRIC ADJUSTMENT ENDPOINTS ============

@app.route('/api/inventory/adjustments', methods=['GET'])
@login_required
def api_get_adjustments():
    """Get adjustment records with pagination support"""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))
        from_date = request.args.get('from_date', '')
        to_date = request.args.get('to_date', '')
        search = request.args.get('search', '')

        # Build query
        query = InventoryAdjustment.query

        # Apply date filters
        if from_date:
            from datetime import datetime
            start_date = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(InventoryAdjustment.created_at >= start_date)

        if to_date:
            from datetime import datetime
            end_date = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(InventoryAdjustment.created_at <= end_date)

        # Apply search filter
        if search:
            query = query.join(InventoryBatch).filter(
                or_(
                    InventoryBatch.batch_name.ilike(f'%{search}%'),
                    InventoryAdjustment.remarks.ilike(f'%{search}%')
                )
            )

        # Order by created_at desc
        query = query.order_by(desc(InventoryAdjustment.created_at))

        # Get total count
        total = query.count()
        total_pages = (total + per_page - 1) // per_page

        # Apply pagination
        adjustments = query.offset((page - 1) * per_page).limit(per_page).all()

        # Format response data
        adjustments_data = []
        for a in adjustments:
            adjustments_data.append({
                'id': a.id,
                'batch_id': a.batch_id,
                'batch_name': a.batch.batch_name if a.batch else 'Unknown',
                'product_name': a.batch.product.name if a.batch and a.batch.product else 'Unknown',
                'adjustment_type': a.adjustment_type,
                'quantity': float(a.quantity),
                'unit': a.batch.product.unit_of_measure if a.batch and a.batch.product else 'pcs',
                'remarks': a.remarks or '',
                'created_at': a.created_at.isoformat() if a.created_at else None,
                'created_by_name': a.user.full_name if a.user else 'Unknown',
                'reference_id': f'ADJ-{a.id}',
                'adjustment_date': a.created_at.strftime('%Y-%m-%d') if a.created_at else None
            })

        return jsonify({
            'success': True,
            'records': adjustments_data,
            'total': total,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        print(f"Error in api_get_adjustments: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'records': [],
            'total': 0,
            'total_pages': 1
        }), 500

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

@app.route('/api/inventory/batches/<int:batch_id>', methods=['GET'])
@login_required
def api_get_batch(batch_id):
    """Get a single batch by ID for editing"""
    try:
        batch = InventoryBatch.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404

        return jsonify({
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
                'status': batch.status
            }
        })
    except Exception as e:
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

@app.route('/api/inventory/batches/<int:batch_id>', methods=['DELETE'])
@login_required
def api_delete_batch(batch_id):
    """Delete a batch"""
    try:
        batch = InventoryBatch.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404

        # Check if batch has stock
        if batch.qty_available and batch.qty_available > 0:
            return jsonify({'error': 'Cannot delete batch with available stock. Please consume or adjust stock to zero first.'}), 400

        # Delete the batch
        db.session.delete(batch)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Batch deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============ TRANSFER ENDPOINTS ============

@app.route('/api/inventory/transfers', methods=['GET'])
@login_required
def api_get_transfers():
    """Get all transfers with pagination"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 25))
        from_date = request.args.get('from_date', '')
        to_date = request.args.get('to_date', '')
        status = request.args.get('status', '')
        search = request.args.get('search', '')

        query = InventoryTransfer.query

        if from_date:
            from datetime import datetime
            start_date = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(InventoryTransfer.transfer_date >= start_date)

        if to_date:
            from datetime import datetime
            end_date = datetime.strptime(to_date, '%Y-%m-%d')
            query = query.filter(InventoryTransfer.transfer_date <= end_date)

        if status:
            query = query.filter(InventoryTransfer.status == status)

        if search:
            query = query.filter(
                or_(
                    InventoryTransfer.transfer_id.ilike(f'%{search}%'),
                    InventoryTransfer.notes.ilike(f'%{search}%')
                )
            )

        query = query.order_by(desc(InventoryTransfer.transfer_date))

        total = query.count()
        total_pages = (total + page_size - 1) // page_size

        transfers = query.offset((page - 1) * page_size).limit(page_size).all()

        transfers_data = []
        for t in transfers:
            transfers_data.append({
                'id': t.id,
                'transfer_id': t.transfer_id,
                'transfer_date': t.transfer_date.strftime('%Y-%m-%d') if t.transfer_date else '',
                'from_location_id': t.from_location_id,
                'from_location_name': t.from_location.name if t.from_location else 'Unknown',
                'to_location_id': t.to_location_id,
                'to_location_name': t.to_location.name if t.to_location else 'Unknown',
                'status': t.status,
                'notes': t.notes or '',
                'item_count': len(t.items) if t.items else 0,
                'created_at': t.created_at.isoformat() if t.created_at else None
            })

        return jsonify({
            'success': True,
            'transfers': transfers_data,
            'total': total,
            'total_pages': total_pages,
            'current_page': page
        })
    except Exception as e:
        print(f"Error in api_get_transfers: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'transfers': []
        }), 500

@app.route('/api/inventory/transfers', methods=['POST'])
@login_required
def api_create_transfer():
    """Create a new transfer"""
    try:
        from decimal import Decimal
        data = request.get_json()

        # Validate required fields
        if not data.get('from_location_id') or not data.get('to_location_id'):
            return jsonify({'error': 'Both from and to locations are required'}), 400

        if data['from_location_id'] == data['to_location_id']:
            return jsonify({'error': 'From and To locations must be different'}), 400

        if not data.get('items') or len(data['items']) == 0:
            return jsonify({'error': 'At least one item is required'}), 400

        # Generate transfer ID if not provided
        transfer_id = data.get('transfer_id')
        if not transfer_id:
            from datetime import datetime
            now = datetime.now()
            transfer_id = f"TRF-{now.strftime('%Y%m%d-%H%M')}"

        # Create transfer
        transfer = InventoryTransfer(
            transfer_id=transfer_id,
            transfer_date=datetime.strptime(data['transfer_date'], '%Y-%m-%d').date() if data.get('transfer_date') else date.today(),
            from_location_id=data['from_location_id'],
            to_location_id=data['to_location_id'],
            status='pending',
            notes=data.get('notes', ''),
            created_by=current_user.id
        )

        db.session.add(transfer)
        db.session.flush()

        # Add transfer items
        for item_data in data['items']:
            batch = InventoryBatch.query.get(item_data['batch_id'])
            if not batch:
                db.session.rollback()
                return jsonify({'error': f'Batch {item_data["batch_id"]} not found'}), 404

            quantity = Decimal(str(item_data['quantity']))
            
            if quantity > batch.qty_available:
                db.session.rollback()
                return jsonify({'error': f'Insufficient stock for batch {batch.batch_name}'}), 400

            # Create transfer item
            from .models import InventoryTransferItem
            transfer_item = InventoryTransferItem(
                transfer_id=transfer.id,
                batch_id=batch.id,
                product_id=batch.product_id,
                quantity=quantity
            )
            db.session.add(transfer_item)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Transfer created successfully',
            'transfer_id': transfer.id
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error creating transfer: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/transfers/<int:transfer_id>', methods=['GET'])
@login_required
def api_get_transfer(transfer_id):
    """Get transfer details"""
    try:
        transfer = InventoryTransfer.query.get(transfer_id)
        if not transfer:
            return jsonify({'error': 'Transfer not found'}), 404

        items_data = []
        for item in transfer.items:
            items_data.append({
                'batch_id': item.batch_id,
                'batch_name': item.batch.batch_name if item.batch else 'Unknown',
                'product_id': item.product_id,
                'product_name': item.product.name if item.product else 'Unknown',
                'quantity': float(item.quantity),
                'unit': item.product.unit_of_measure if item.product else 'pcs'
            })

        return jsonify({
            'success': True,
            'transfer': {
                'id': transfer.id,
                'transfer_id': transfer.transfer_id,
                'transfer_date': transfer.transfer_date.strftime('%Y-%m-%d') if transfer.transfer_date else '',
                'from_location_id': transfer.from_location_id,
                'from_location_name': transfer.from_location.name if transfer.from_location else 'Unknown',
                'to_location_id': transfer.to_location_id,
                'to_location_name': transfer.to_location.name if transfer.to_location else 'Unknown',
                'status': transfer.status,
                'notes': transfer.notes or '',
                'items': items_data
            }
        })
    except Exception as e:
        print(f"Error getting transfer: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/transfers/<int:transfer_id>/complete', methods=['POST'])
@login_required
def api_complete_transfer(transfer_id):
    """Complete a transfer - move stock between locations"""
    try:
        from decimal import Decimal
        transfer = InventoryTransfer.query.get(transfer_id)
        if not transfer:
            return jsonify({'error': 'Transfer not found'}), 404

        if transfer.status != 'pending':
            return jsonify({'error': 'Only pending transfers can be completed'}), 400

        # Process each item
        for item in transfer.items:
            # Reduce quantity from source batch
            source_batch = item.batch
            if source_batch.qty_available < item.quantity:
                db.session.rollback()
                return jsonify({'error': f'Insufficient stock in batch {source_batch.batch_name}'}), 400

            source_batch.qty_available -= item.quantity

            # Find existing batch at destination with same product and batch details
            dest_batch = InventoryBatch.query.filter_by(
                product_id=source_batch.product_id,
                location_id=transfer.to_location_id,
                mfg_date=source_batch.mfg_date,
                expiry_date=source_batch.expiry_date
            ).first()

            if dest_batch:
                # Update existing batch at destination
                dest_batch.qty_available += item.quantity
            else:
                # Generate unique batch name for destination
                base_name = source_batch.batch_name
                new_batch_name = base_name
                counter = 1
                
                # Check if batch name already exists, if so append a suffix
                while InventoryBatch.query.filter_by(batch_name=new_batch_name).first():
                    new_batch_name = f"{base_name}-T{counter}"
                    counter += 1
                
                # Create new batch at destination with unique name
                dest_batch = InventoryBatch(
                    batch_name=new_batch_name,
                    product_id=source_batch.product_id,
                    location_id=transfer.to_location_id,
                    mfg_date=source_batch.mfg_date,
                    expiry_date=source_batch.expiry_date,
                    qty_available=item.quantity,
                    unit_cost=source_batch.unit_cost,
                    selling_price=source_batch.selling_price,
                    status='active'
                )
                db.session.add(dest_batch)

        # Update transfer status
        transfer.status = 'completed'
        transfer.completed_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Transfer completed successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error completing transfer: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/transfers/<int:transfer_id>/cancel', methods=['POST'])
@login_required
def api_cancel_transfer(transfer_id):
    """Cancel a transfer"""
    try:
        transfer = InventoryTransfer.query.get(transfer_id)
        if not transfer:
            return jsonify({'error': 'Transfer not found'}), 404

        if transfer.status != 'pending':
            return jsonify({'error': 'Only pending transfers can be cancelled'}), 400

        transfer.status = 'cancelled'
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Transfer cancelled successfully'
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


@app.route('/modules/staff/inventory_punch_out', methods=['POST'])
@login_required
def inventory_punch_out():
    """Endpoint for inventory staff punch out (placeholder)"""
    try:
        # Implement punch out logic here
        flash('Punch out successful', 'success')
        return redirect(url_for('staff_dashboard'))
    except Exception as e:
        flash(f'Punch out failed: {e}', 'danger')
        return redirect(url_for('staff_dashboard'))


# ============ BATCH-CENTRIC PRODUCT BATCHES ENDPOINTS ============
@app.route('/api/inventory/products/batches/<int:product_id>', methods=['GET'])
@login_required
def get_product_batches(product_id):
    """Get all batches for a specific product"""
    try:
        batches = InventoryBatch.query.filter_by(
            product_id=product_id,
            status='active'
        ).order_by(InventoryBatch.expiry_date.asc()).all()

        return jsonify({
            'success': True,
            'batches': [{
                'id': b.id,
                'batch_name': b.batch_name,
                'expiry_date': b.expiry_date.isoformat() if b.expiry_date else None,
                'qty_available': float(b.qty_available or 0),
                'unit_cost': float(b.unit_cost or 0),
                'location_id': b.location_id,
                'location_name': b.location.name if b.location else 'Unknown'
            } for b in batches]
        })
    except Exception as e:
        print(f"Error loading batches: {e}")
        return jsonify({'success': False, 'error': str(e)}), 404


# ============ BATCH-CENTRIC ADJUSTMENTS DATA ENDPOINT ============
@app.route('/inventory/adjustments/data')
@login_required
def inventory_adjustments_data():
    """API endpoint to get inventory adjustments"""
    try:
        from datetime import datetime
        from sqlalchemy import or_

        # Get filter parameters
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        search = request.args.get('search', '').strip()

        # Base query with eager loading
        query = InventoryAdjustment.query.options(
            joinedload(InventoryAdjustment.product),
            joinedload(InventoryAdjustment.batch),
            joinedload(InventoryAdjustment.created_by_user)
        )

        # Apply date filters only if provided
        if from_date:
            try:
                from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
                query = query.filter(InventoryAdjustment.adjustment_date >= from_date_obj)
            except ValueError:
                pass

        if to_date:
            try:
                to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
                query = query.filter(InventoryAdjustment.adjustment_date <= to_date_obj)
            except ValueError:
                pass

        # Apply search filter
        if search:
            query = query.join(InventoryProduct).filter(
                or_(
                    InventoryAdjustment.reference_id.ilike(f'%{search}%'),
                    InventoryAdjustment.remarks.ilike(f'%{search}%'),
                    InventoryProduct.name.ilike(f'%{search}%')
                )
            )

        # Get all adjustments ordered by date descending
        adjustments = query.order_by(InventoryAdjustment.adjustment_date.desc(), InventoryAdjustment.id.desc()).all()

        print(f"📊 Found {len(adjustments)} inventory adjustments")

        # Format data for response
        adjustments_data = []
        for adj in adjustments:
            try:
                adjustment_info = {
                    'id': adj.id,
                    'reference_id': adj.reference_id or f'ADJ-{adj.id}',
                    'adjustment_date': adj.adjustment_date.strftime('%Y-%m-%d') if adj.adjustment_date else 'N/A',
                    'batch_number': adj.batch.batch_name if adj.batch else 'N/A',
                    'product_name': adj.product.name if adj.product else 'Unknown Product',
                    'quantity': float(adj.quantity) if adj.quantity else 0,
                    'adjustment_type': adj.adjustment_type or 'manual',
                    'remarks': adj.remarks or '',
                    'created_by': adj.created_by_user.username if adj.created_by_user else 'System',
                    'created_at': adj.created_at.strftime('%Y-%m-%d %H:%M') if adj.created_at else 'N/A'
                }
                adjustments_data.append(adjustment_info)
            except Exception as item_error:
                print(f"Error formatting adjustment {adj.id}: {item_error}")
                continue

        print(f"✅ Returning {len(adjustments_data)} formatted adjustments")

        return jsonify({
            'success': True,
            'adjustments': adjustments_data,
            'total': len(adjustments_data)
        })

    except Exception as e:
        print(f"❌ Error loading adjustments data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'adjustments': [],
            'total': 0
        }), 500

@app.route('/api/inventory/status', methods=['GET'])
@login_required
def api_inventory_status():
    """Get comprehensive inventory status"""
    try:
        from datetime import timedelta
        
        # Get all products and batches
        products = InventoryProduct.query.all()
        batches = InventoryBatch.query.all()
        categories = InventoryCategory.query.all()
        
        # Calculate overview statistics
        total_products = len(products)
        total_batches = len([b for b in batches if b.status == 'active' and (b.qty_available or 0) > 0])
        total_inventory_value = sum(
            float(b.qty_available or 0) * float(b.unit_cost or 0) 
            for b in batches if b.status == 'active'
        )
        
        # Stock status summary
        stock_summary = {
            'in_stock': len([p for p in products if p.total_stock > 10]),
            'low_stock': len([p for p in products if 0 < p.total_stock <= 10]),
            'out_of_stock': len([p for p in products if p.total_stock == 0])
        }
        
        # Alerts
        today = date.today()
        expiring_soon_date = today + timedelta(days=30)
        
        expired_batches = [b for b in batches if b.expiry_date and b.expiry_date < today and (b.qty_available or 0) > 0]
        expiring_soon_batches = [
            b for b in batches 
            if b.expiry_date and today <= b.expiry_date <= expiring_soon_date and (b.qty_available or 0) > 0
        ]
        
        alerts = {
            'out_of_stock_count': stock_summary['out_of_stock'],
            'low_stock_count': stock_summary['low_stock'],
            'expired_batches_count': len(expired_batches),
            'expiring_soon_count': len(expiring_soon_batches)
        }
        
        # Category breakdown
        category_breakdown = []
        for cat in categories:
            product_count = len([p for p in products if p.category_id == cat.id])
            if product_count > 0:
                category_breakdown.append({
                    'category': cat.name,
                    'product_count': product_count
                })
        
        # Recent activity (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_consumption = InventoryConsumption.query.filter(
            InventoryConsumption.created_at >= seven_days_ago
        ).count()
        recent_adjustments = InventoryAdjustment.query.filter(
            InventoryAdjustment.created_at >= seven_days_ago
        ).count()
        
        recent_activity = {
            'consumption_records': recent_consumption,
            'adjustments': recent_adjustments
        }
        
        # Low stock items
        low_stock_items = []
        for p in products:
            if 0 < p.total_stock <= 10:
                low_stock_items.append({
                    'name': p.name,
                    'sku': p.sku,
                    'current_stock': p.total_stock,
                    'status': 'low_stock'
                })
        
        # Expired batches data
        expired_batches_data = []
        for b in expired_batches[:10]:  # Limit to 10
            expired_batches_data.append({
                'batch_name': b.batch_name,
                'product_name': b.product.name if b.product else 'Unknown',
                'expiry_date': b.expiry_date.strftime('%Y-%m-%d'),
                'qty_available': float(b.qty_available or 0)
            })
        
        # Expiring soon data
        expiring_soon_data = []
        for b in expiring_soon_batches[:10]:  # Limit to 10
            days_until_expiry = (b.expiry_date - today).days
            expiring_soon_data.append({
                'batch_name': b.batch_name,
                'product_name': b.product.name if b.product else 'Unknown',
                'expiry_date': b.expiry_date.strftime('%Y-%m-%d'),
                'days_until_expiry': days_until_expiry
            })
        
        # Product-wise data
        product_wise_data = []
        for p in products:
            if p.total_stock > 0:
                total_value = sum(
                    float(b.qty_available or 0) * float(b.unit_cost or 0)
                    for b in p.batches if b.status == 'active'
                )
                product_wise_data.append({
                    'name': p.name,
                    'sku': p.sku,
                    'category': p.category.name if p.category else 'Uncategorized',
                    'total_quantity': p.total_stock,
                    'unit_of_measure': p.unit_of_measure,
                    'batch_count': p.batch_count,
                    'total_value': total_value,
                    'status': p.stock_status
                })
        
        # Batch-wise data
        batch_wise_data = []
        for b in batches:
            if b.status == 'active' and (b.qty_available or 0) > 0:
                total_value = float(b.qty_available or 0) * float(b.unit_cost or 0)
                batch_wise_data.append({
                    'batch_name': b.batch_name,
                    'product_name': b.product.name if b.product else 'Unknown',
                    'location_name': b.location.name if b.location else 'Unknown',
                    'qty_available': float(b.qty_available or 0),
                    'unit_of_measure': b.product.unit_of_measure if b.product else 'pcs',
                    'unit_cost': float(b.unit_cost or 0),
                    'total_value': total_value,
                    'mfg_date': b.mfg_date.strftime('%Y-%m-%d') if b.mfg_date else None,
                    'expiry_date': b.expiry_date.strftime('%Y-%m-%d') if b.expiry_date else None
                })
        
        return jsonify({
            'success': True,
            'overview': {
                'total_products': total_products,
                'total_batches': total_batches,
                'total_inventory_value': round(total_inventory_value, 2),
                'stock_summary': stock_summary
            },
            'alerts': alerts,
            'category_breakdown': category_breakdown,
            'recent_activity': recent_activity,
            'low_stock_items': low_stock_items,
            'expired_batches': expired_batches_data,
            'expiring_soon': expiring_soon_data,
            'product_wise_data': product_wise_data,
            'batch_wise_data': batch_wise_data
        })
    
    except Exception as e:
        print(f"Error getting inventory status: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500