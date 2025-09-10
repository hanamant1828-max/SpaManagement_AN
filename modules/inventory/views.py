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
        
        # Use the batch-centric create function
        product = create_product({
            'name': data.get('name'),
            'description': data.get('description', ''),
            'category_id': data.get('category_id'),
            'sku': data.get('sku', ''),
            'unit_of_measure': data.get('unit_of_measure', 'pcs'),
            'barcode': data.get('barcode', ''),
            'is_active': True,
            'is_service_item': data.get('is_service_item', False),
            'is_retail_item': data.get('is_retail_item', True)
        })

        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'product_id': product.id
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

@app.route('/api/inventory/locations', methods=['GET'])
@login_required
def api_get_locations():
    """Get all locations"""
    try:
        locations = get_all_locations()
        return jsonify([{
            'id': l.id,
            'name': l.name,
            'type': l.type,
            'address': l.address,
            'status': l.status
        } for l in locations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/locations', methods=['POST'])
@login_required
def api_create_location():
    """Create a new location"""
    try:
        data = request.get_json()

        location = InventoryLocation(
            name=data.get('name'),
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

        batch = InventoryBatch.query.get(data.get('batch_id'))
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404

        # Assign product and location to batch if not already assigned
        if data.get('product_id') and not batch.product_id:
            batch.product_id = data.get('product_id')
        
        if data.get('location_id') and not batch.location_id:
            batch.location_id = data.get('location_id')

        adjustment = InventoryAdjustment(
            batch_id=data.get('batch_id'),
            adjustment_type='add',
            quantity=float(data.get('quantity', 0)),
            unit_cost=float(data.get('unit_cost', batch.unit_cost or 0)),
            notes=data.get('notes', ''),
            created_by=current_user.id
        )

        # Update batch quantity
        batch.qty_available = float(batch.qty_available or 0) + float(data.get('quantity', 0))

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
        from .queries import get_available_batches_for_consumption
        batches = get_available_batches_for_consumption()
        return jsonify([{
            'id': b.id,
            'batch_name': b.batch_name,
            'product_name': b.product.name if b.product else 'Unassigned',
            'location_name': b.location.name if b.location else 'Unassigned',
            'qty_available': float(b.qty_available or 0),
            'expiry_date': b.expiry_date.isoformat() if b.expiry_date else None,
            'dropdown_display': b.dropdown_display
        } for b in batches])
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
            'created_by_name': c.creator.full_name if c.creator else 'Unknown'
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
            'unit_cost': float(a.unit_cost) if a.unit_cost else None,
            'notes': a.notes,
            'created_at': a.created_at.isoformat() if a.created_at else None,
            'created_by_name': a.creator.full_name if a.creator else 'Unknown'
        } for a in adjustments])
    except Exception as e:
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