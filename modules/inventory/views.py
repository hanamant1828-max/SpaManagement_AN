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

@app.route('/api/inventory/products', methods=['GET'])
@login_required
def api_get_products():
    """Get all products"""
    try:
        products = get_all_products()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'category_id': p.category_id,
            'category_name': p.category.name if p.category else '',
            'location_id': p.location_id,
            'location_name': p.location.name if p.location else '',
            'sku': p.sku,
            'unit': p.unit,
            'cost_price': float(p.cost_price) if p.cost_price else 0,
            'selling_price': float(p.selling_price) if p.selling_price else 0,
            'current_stock': float(p.current_stock) if p.current_stock else 0,
            'min_stock_level': float(p.min_stock_level) if p.min_stock_level else 0,
            'max_stock_level': float(p.max_stock_level) if p.max_stock_level else 0,
            'is_active': p.is_active
        } for p in products])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/products', methods=['POST'])
@login_required
def api_create_product():
    """Create a new product"""
    try:
        data = request.get_json()

        product = InventoryProduct(
            name=data.get('name'),
            description=data.get('description', ''),
            category_id=data.get('category_id'),
            location_id=data.get('location_id'),
            sku=data.get('sku', ''),
            unit=data.get('unit', 'pcs'),
            cost_price=data.get('cost_price', 0),
            selling_price=data.get('selling_price', 0),
            current_stock=0,  # Always start with 0 stock
            min_stock_level=data.get('min_stock_level', 0),
            max_stock_level=data.get('max_stock_level', 0),
            is_active=True
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

        category = InventoryCategory(
            name=data.get('name'),
            description=data.get('description', ''),
            is_active=True
        )

        db.session.add(category)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Category created successfully',
            'category_id': category.id
        })
    except Exception as e:
        db.session.rollback()
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
            description=data.get('description', ''),
            address=data.get('address', ''),
            is_active=True
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
            qty_available=0  # Start with 0, stock added via adjustments
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
            quantity=data.get('quantity'),
            unit_cost=data.get('unit_cost', batch.unit_cost),
            notes=data.get('notes', ''),
            created_by=current_user.id
        )

        # Update batch quantity
        batch.qty_available += data.get('quantity', 0)

        db.session.add(adjustment)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Inventory adjustment created successfully'
        })
    except Exception as e:
        db.session.rollback()
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

        return jsonify({
            'batches': [{
                'id': b.id,
                'batch_name': b.batch_name,
                'product_id': b.product_id,
                'location_id': b.location_id,
                'product_name': b.product.name if b.product else None,
                'location_name': b.location.name if b.location else None,
                'expiry_date': b.expiry_date.isoformat() if b.expiry_date else None,
                'qty_available': float(b.qty_available or 0),
                'days_to_expiry': b.days_to_expiry,
                'unit_of_measure': b.product.unit_of_measure if b.product else 'pcs'
            } for b in batches]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/consumption', methods=['POST'])
@login_required
def api_create_consumption():
    """Create consumption record"""
    try:
        data = request.get_json()

        batch = InventoryBatch.query.get(data.get('batch_id'))
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404

        quantity = data.get('quantity', 0)
        if quantity > batch.qty_available:
            return jsonify({'error': 'Insufficient stock available'}), 400

        consumption = InventoryConsumption(
            batch_id=data.get('batch_id'),
            quantity=quantity,
            notes=data.get('notes', ''),
            created_by=current_user.id
        )

        # Update batch quantity
        batch.qty_available -= quantity

        db.session.add(consumption)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Consumption recorded successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500