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

@app.route('/modules/checkin') # This is a placeholder, will be fixed soon
@login_required
def checkin():
    """Placeholder for checkin view"""
    return render_template('checkin.html')

@app.route('/modules/checkin/new', methods=['POST']) # This is a placeholder, will be fixed soon
@login_required
def checkin_new():
    """Placeholder for new checkin"""
    flash('Checkin functionality not yet implemented', 'warning')
    return redirect(url_for('checkin'))

@app.route('/modules/checkout') # This is a placeholder, will be fixed soon
@login_required
def checkout():
    """Placeholder for checkout view"""
    return render_template('checkout.html')

@app.route('/modules/checkout/new', methods=['POST']) # This is a placeholder, will be fixed soon
@login_required
def checkout_new():
    """Placeholder for new checkout"""
    flash('Checkout functionality not yet implemented', 'warning')
    return redirect(url_for('checkout'))

@app.route('/modules/staff') # This is a placeholder, will be fixed soon
@login_required
def staff_dashboard():
    """Placeholder for staff dashboard"""
    return render_template('staff_dashboard.html')

@app.route('/modules/staff/punch_in', methods=['POST']) # This is the correct endpoint for punch in
@login_required
def punch_in():
    """Endpoint for staff to punch in"""
    try:
        # Implement punch in logic here
        flash('Punch in successful', 'success')
        return redirect(url_for('staff_dashboard'))
    except Exception as e:
        flash(f'Punch in failed: {e}', 'danger')
        return redirect(url_for('staff_dashboard'))

@app.route('/modules/staff/punch_out', methods=['POST']) # This is a placeholder, will be fixed soon
@login_required
def punch_out():
    """Endpoint for staff to punch out"""
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