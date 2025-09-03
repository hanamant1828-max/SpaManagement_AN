"""
Professional Inventory Management System Views
Advanced inventory management with comprehensive business logic, analytics, and reporting
"""

from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_, desc
from app import app, db
from models import (InventoryCategory, InventorySupplier, User, Role, Permission, InventoryProduct)
import json
import io
import csv
from collections import defaultdict

@app.route('/inventory_pro')
@login_required
def inventory_pro():
    """Professional inventory management interface with advanced features"""
    if not current_user.can_access('inventory'):
        flash('Access denied to inventory management', 'danger')
        return redirect(url_for('dashboard'))

    try:
        # Get inventory products
        products = InventoryProduct.query.filter_by(is_active=True).all()
        
        # Get categories and suppliers for master data
        categories = InventoryCategory.query.filter_by(is_active=True).all()
        suppliers = InventorySupplier.query.filter_by(is_active=True).all()
        
        # Calculate basic metrics
        total_items = len(products)
        total_stock_value = sum(p.current_stock * p.unit_cost for p in products if p.current_stock and p.unit_cost)
        low_stock_count = sum(1 for p in products if p.current_stock <= p.reorder_level)
        out_of_stock_count = sum(1 for p in products if p.current_stock <= 0)
        todays_transactions = 0  # Will be updated when transaction model is available
        
        return render_template('professional_inventory.html',
                             products=products,
                             categories=categories,
                             suppliers=suppliers,
                             total_items=total_items,
                             total_stock_value=total_stock_value,
                             low_stock_count=low_stock_count,
                             out_of_stock_count=out_of_stock_count,
                             todays_transactions=todays_transactions,
                             items=products,  # For compatibility
                             transactions=[],  # Empty for now
                             alerts=[])  # Empty for now
                             
    except Exception as e:
        app.logger.error(f"Error in professional inventory: {str(e)}")
        flash('An error occurred while loading inventory data. Please try again.', 'danger')
        return redirect(url_for('dashboard'))
        

    except Exception as e:
        app.logger.error(f"Error in professional inventory: {str(e)}")
        flash('An error occurred while loading inventory data. Please try again.', 'danger')
        return redirect(url_for('dashboard'))

def calculate_inventory_metrics(items):
    """Calculate comprehensive inventory metrics"""
    if not items:
        return {
            'total_items': 0,
            'total_stock_value': 0,
            'total_retail_value': 0,
            'low_stock_count': 0,
            'out_of_stock_count': 0,
            'near_expiry_count': 0,
            'expired_count': 0,
            'todays_transactions': 0,
            'average_turnover': 0,
            'total_categories': 0,
            'total_suppliers': 0
        }

    # Basic counts
    total_items = len(items)
    low_stock_count = sum(1 for item in items if item.is_low_stock)
    out_of_stock_count = sum(1 for item in items if item.is_out_of_stock)
    near_expiry_count = sum(1 for item in items if item.is_near_expiry)
    expired_count = sum(1 for item in items if item.is_expired)

    # Value calculations
    total_stock_value = sum(item.stock_value for item in items)
    total_retail_value = sum(item.retail_value for item in items if item.selling_price)

    # Diversity metrics
    categories = set(item.category for item in items if item.category)
    suppliers = set(item.supplier for item in items if item.supplier)

    # Today's activity (simplified since SimpleStockTransaction doesn't exist)
    today = date.today()
    todays_transactions = 0  # Will be updated when transaction model is available

    # Average turnover (simplified since turnover_rate doesn't exist)
    average_turnover = 0

    return {
        'total_items': total_items,
        'total_stock_value': total_stock_value,
        'total_retail_value': total_retail_value,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'near_expiry_count': near_expiry_count,
        'expired_count': expired_count,
        'todays_transactions': todays_transactions,
        'average_turnover': round(average_turnover, 2),
        'total_categories': len(categories),
        'total_suppliers': len(suppliers)
    }

def prepare_analytics_data(items, transactions):
    """Prepare analytics data for charts and reports"""
    # Stock status distribution
    status_distribution = {
        'normal': 0,
        'low_stock': 0,
        'out_of_stock': 0,
        'overstocked': 0
    }

    # ABC classification distribution
    abc_distribution = {'A': 0, 'B': 0, 'C': 0}

    # Category value distribution
    category_values = defaultdict(float)

    for item in items:
        # Stock status (simplified)
        if item.current_stock <= 0:
            status_distribution['out_of_stock'] += 1
        elif item.current_stock <= item.reorder_level:
            status_distribution['low_stock'] += 1
        else:
            status_distribution['normal'] += 1

        # ABC classification (default to 'C' since abc_classification doesn't exist)
        abc_distribution['C'] += 1

        # Category values
        if hasattr(item, 'category') and item.category:
            stock_value = (item.current_stock * item.unit_cost) if item.current_stock and item.unit_cost else 0
            category_values[item.category] += stock_value

    # Transaction trends (last 30 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    daily_transactions = defaultdict(int)
    transaction_types = defaultdict(int)

    for transaction in transactions:
        if start_date <= transaction.date_time.date() <= end_date:
            day_key = transaction.date_time.strftime('%Y-%m-%d')
            daily_transactions[day_key] += 1
            transaction_types[transaction.transaction_type] += 1

    return {
        'stock_status': status_distribution,
        'abc_classification': abc_distribution,
        'category_values': dict(category_values),
        'daily_transactions': dict(daily_transactions),
        'transaction_types': dict(transaction_types)
    }

@app.route('/api/inventory/pro_metrics')
@login_required
def api_inventory_pro_metrics():
    """API endpoint for professional inventory metrics"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        items = InventoryProduct.query.filter_by(is_active=True).all()
        metrics = calculate_inventory_metrics(items)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/pro_alerts')
@login_required
def api_inventory_pro_alerts():
    """API endpoint for professional inventory alerts"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # For now return empty alerts since SimpleLowStockAlert model doesn't exist
        alerts_data = []
        return jsonify({'alerts': alerts_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/inventory/add_professional_item', methods=['POST'])
@login_required
def add_professional_inventory_item():
    """Add new inventory item with professional features"""
    if not current_user.can_access('inventory'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    try:
        # Get form data with comprehensive fields
        data = request.get_json() if request.is_json else request.form

        # Generate SKU if not provided
        sku = data.get('sku') or f"AUTO-{int(datetime.now().timestamp())}"

        # Check if SKU or barcode already exists
        existing_item = InventoryProduct.query.filter(
            or_(
                InventoryProduct.sku == sku,
                and_(
                    InventoryProduct.barcode == data.get('barcode'),
                    InventoryProduct.barcode.isnot(None)
                )
            )
        ).first()

        if existing_item:
            return jsonify({
                'success': False, 
                'error': 'SKU or barcode already exists'
            }), 400

        # Parse dates
        expiry_date = None
        if data.get('expiry_date'):
            try:
                expiry_date = datetime.strptime(data.get('expiry_date'), '%Y-%m-%d').date()
            except ValueError:
                pass

        manufacturing_date = None
        if data.get('manufacturing_date'):
            try:
                manufacturing_date = datetime.strptime(data.get('manufacturing_date'), '%Y-%m-%d').date()
            except ValueError:
                pass

        # Create comprehensive item
        new_item = InventoryProduct(
            # Basic info
            sku=sku,
            barcode=data.get('barcode'),
            name=data.get('name', '').strip(),
            description=data.get('description', '').strip(),
            category=data.get('category', '').strip(),
            subcategory=data.get('subcategory', '').strip(),
            brand=data.get('brand', '').strip(),

            # Stock levels
            current_stock=float(data.get('initial_stock', 0)),
            minimum_stock=float(data.get('minimum_stock', 5)),
            maximum_stock=float(data.get('maximum_stock', 100)) if data.get('maximum_stock') else None,
            reorder_point=float(data.get('reorder_point', 10)),
            reorder_quantity=float(data.get('reorder_quantity', 50)),

            # Location
            location=data.get('location', '').strip(),
            bin_location=data.get('bin_location', '').strip(),
            warehouse_zone=data.get('warehouse_zone', '').strip(),

            # Pricing
            unit_cost=float(data.get('unit_cost', 0)),
            selling_price=float(data.get('selling_price', 0)) if data.get('selling_price') else None,
            markup_percentage=float(data.get('markup_percentage', 0)) if data.get('markup_percentage') else None,

            # Supplier
            supplier=data.get('supplier', '').strip(),
            supplier_code=data.get('supplier_code', '').strip(),
            supplier_contact=data.get('supplier_contact', '').strip(),
            lead_time_days=int(data.get('lead_time_days', 7)) if data.get('lead_time_days') else 7,

            # Product details
            unit_of_measure=data.get('unit_of_measure', 'pcs').strip(),
            weight=float(data.get('weight', 0)) if data.get('weight') else None,
            dimensions=data.get('dimensions', '').strip(),
            color=data.get('color', '').strip(),
            size=data.get('size', '').strip(),

            # Dates and tracking
            expiry_date=expiry_date,
            manufacturing_date=manufacturing_date,
            batch_number=data.get('batch_number', '').strip(),
            lot_number=data.get('lot_number', '').strip(),

            # Flags
            is_serialized=bool(data.get('is_serialized')),
            is_perishable=bool(data.get('is_perishable')),
            is_hazardous=bool(data.get('is_hazardous')),
            requires_approval=bool(data.get('requires_approval'))
        )

        db.session.add(new_item)
        db.session.flush()  # Get the item ID

        # Initial stock transaction logging (will be enhanced when transaction model is available)
        initial_stock = float(data.get('initial_stock', 0))
        if initial_stock > 0:
            app.logger.info(f"Initial stock entry: {new_item.name} - {initial_stock} units")

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Item "{new_item.name}" added successfully',
            'item_id': new_item.id
        })

    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding inventory item: {str(e)}")
        return jsonify({'success': False, 'error': 'Database error occurred'}), 500

@app.route('/inventory/reports/abc_analysis')
@login_required
def generate_abc_analysis_report():
    """Generate ABC Analysis Report"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        items = InventoryProduct.query.filter_by(is_active=True).all()

        # Group by ABC classification
        abc_data = {'A': [], 'B': [], 'C': []}
        totals = {'A': 0, 'B': 0, 'C': 0}

        for item in items:
            classification = item.abc_classification
            abc_data[classification].append({
                'name': item.name,
                'sku': item.sku,
                'category': item.category,
                'stock_value': item.stock_value,
                'current_stock': item.current_stock,
                'turnover_rate': item.turnover_rate
            })
            totals[classification] += item.stock_value

        report_data = {
            'generated_at': datetime.now().isoformat(),
            'total_items': len(items),
            'classifications': abc_data,
            'totals': totals,
            'percentages': {
                'A': round(totals['A'] / sum(totals.values()) * 100, 2) if sum(totals.values()) > 0 else 0,
                'B': round(totals['B'] / sum(totals.values()) * 100, 2) if sum(totals.values()) > 0 else 0,
                'C': round(totals['C'] / sum(totals.values()) * 100, 2) if sum(totals.values()) > 0 else 0
            }
        }

        return jsonify({'success': True, 'data': report_data})

    except Exception as e:
        app.logger.error(f"Error generating ABC analysis: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/inventory/export/csv')
@login_required
def export_inventory_csv():
    """Export inventory data to CSV"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('inventory_pro'))

    try:
        items = InventoryProduct.query.filter_by(is_active=True).all()

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write headers
        headers = [
            'SKU', 'Barcode', 'Name', 'Description', 'Category', 'Brand',
            'Current Stock', 'Minimum Stock', 'Maximum Stock', 'Reorder Point',
            'Unit Cost', 'Selling Price', 'Stock Value', 'Retail Value',
            'Supplier', 'Location', 'Status', 'ABC Classification',
            'Expiry Date', 'Days Until Expiry', 'Last Updated'
        ]
        writer.writerow(headers)

        # Write data
        for item in items:
            status = item.get_stock_status()
            writer.writerow([
                item.sku,
                item.barcode or '',
                item.name,
                item.description or '',
                item.category or '',
                item.brand or '',
                item.current_stock,
                item.minimum_stock,
                item.maximum_stock or '',
                item.reorder_point,
                item.unit_cost,
                item.selling_price or '',
                item.stock_value,
                item.retail_value,
                item.supplier or '',
                item.location or '',
                status['status'],
                item.abc_classification,
                item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else '',
                item.days_until_expiry or '',
                item.last_updated.strftime('%Y-%m-%d %H:%M:%S')
            ])

        # Create file response
        output.seek(0)

        # Create a BytesIO object for the file
        mem = io.BytesIO()
        mem.write(output.getvalue().encode('utf-8'))
        mem.seek(0)

        filename = f'inventory_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        app.logger.error(f"Error exporting inventory: {str(e)}")
        flash('Error exporting inventory data', 'danger')
        return redirect(url_for('inventory_pro'))

# Additional API endpoints for real-time updates
@app.route('/api/inventory/quick_stock_update', methods=['POST'])
@login_required
def api_quick_stock_update():
    """API for quick stock updates"""
    if not current_user.can_access('inventory'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    try:
        data = request.get_json()
        item_id = data.get('item_id')
        adjustment = float(data.get('adjustment', 0))
        reason = data.get('reason', 'Quick stock adjustment')

        item = InventoryProduct.query.get_or_404(item_id)

        # Calculate new stock
        previous_stock = item.current_stock
        new_stock = previous_stock + adjustment

        if new_stock < 0:
            return jsonify({
                'success': False, 
                'error': f'Insufficient stock. Current: {previous_stock}'
            }), 400

        # Update stock
        item.current_stock = new_stock

        # Transaction tracking will be added when SimpleStockTransaction model is available
        # For now, just log the change
        app.logger.info(f"Stock adjustment: {item.name} changed by {adjustment} (from {previous_stock} to {new_stock})")

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Stock updated for {item.name}',
            'new_stock': new_stock,
            'change': adjustment
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500