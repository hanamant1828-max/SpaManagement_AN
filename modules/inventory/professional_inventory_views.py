"""
Professional Inventory Management System Views
Advanced inventory management with comprehensive business logic, analytics, and reporting
"""

from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_, desc
from app import app, db
from models import (InventoryCategory, Supplier, User, Role, Permission)
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
        # Get filter parameters
        category_filter = request.args.get('category', '')
        status_filter = request.args.get('status', '')
        search_query = request.args.get('search', '')
        abc_filter = request.args.get('abc', '')
        location_filter = request.args.get('location', '')

        # Build base query with optimized loading
        query = InventoryProduct.query.filter_by(is_active=True)

        # Apply filters
        if category_filter:
            query = query.filter(InventoryProduct.category == category_filter)

        if location_filter:
            query = query.filter(InventoryProduct.location == location_filter)

        if status_filter:
            if status_filter == 'low_stock':
                query = query.filter(InventoryProduct.current_stock <= InventoryProduct.minimum_stock)
            elif status_filter == 'out_of_stock':
                query = query.filter(InventoryProduct.current_stock <= 0)
            elif status_filter == 'overstocked':
                query = query.filter(InventoryProduct.current_stock > InventoryProduct.maximum_stock)
            elif status_filter == 'normal':
                query = query.filter(
                    and_(
                        InventoryProduct.current_stock > InventoryProduct.minimum_stock,
                        or_(
                            InventoryProduct.maximum_stock.is_(None),
                            InventoryProduct.current_stock <= InventoryProduct.maximum_stock
                        )
                    )
                )
            elif status_filter == 'expired':
                query = query.filter(
                    and_(
                        InventoryProduct.expiry_date.isnot(None),
                        InventoryProduct.expiry_date < date.today()
                    )
                )

        if search_query:
            search_term = f'%{search_query}%'
            query = query.filter(
                or_(
                    InventoryProduct.name.ilike(search_term),
                    InventoryProduct.sku.ilike(search_term),
                    InventoryProduct.barcode.ilike(search_term),
                    InventoryProduct.description.ilike(search_term),
                    InventoryProduct.supplier.ilike(search_term)
                )
            )

        # Get items with pagination support
        page = request.args.get('page', 1, type=int)
        per_page = 50  # Professional systems typically show more items per page

        items = query.order_by(
            # Smart ordering: critical items first, then by name
            InventoryProduct.current_stock.asc(),
            InventoryProduct.name.asc()
        ).all()  # Get all for now, implement pagination later if needed

        # Apply ABC filter (post-query since it's a calculated property)
        if abc_filter:
            items = [item for item in items if item.abc_classification == abc_filter]

        # Get categories and locations for filters
        categories = db.session.query(InventoryProduct.category).distinct().filter(
            InventoryProduct.category.isnot(None),
            InventoryProduct.is_active == True
        ).all()
        categories = sorted([cat[0] for cat in categories if cat[0]])

        locations = db.session.query(InventoryProduct.location).distinct().filter(
            InventoryProduct.location.isnot(None),
            InventoryProduct.is_active == True
        ).all()
        locations = sorted([loc[0] for loc in locations if loc[0]])

        # Calculate comprehensive metrics
        metrics = calculate_inventory_metrics(items)

        # Get recent transactions for activity feed
        recent_transactions = SimpleStockTransaction.query.join(InventoryProduct).filter(
            InventoryProduct.is_active == True
        ).order_by(desc(SimpleStockTransaction.date_time)).limit(50).all()

        # Get active alerts
        active_alerts = SimpleLowStockAlert.query.join(InventoryProduct).filter(
            and_(
                InventoryProduct.is_active == True,
                SimpleLowStockAlert.is_acknowledged == False,
                SimpleLowStockAlert.is_resolved == False
            )
        ).order_by(desc(SimpleLowStockAlert.alert_date)).limit(10).all()

        # Get transaction types for dropdowns
        transaction_types = TransactionType.query.filter_by(is_active=True).order_by(
            TransactionType.sort_order, TransactionType.display_name
        ).all()

        # Prepare analytics data
        analytics_data = prepare_analytics_data(items, recent_transactions)

        return render_template('professional_inventory.html',
                             # Core data
                             items=items,
                             transactions=recent_transactions,
                             alerts=active_alerts,

                             # Filter options
                             categories=categories,
                             locations=locations,
                             transaction_types=transaction_types,

                             # Current filters
                             category_filter=category_filter,
                             status_filter=status_filter,
                             search_query=search_query,
                             abc_filter=abc_filter,
                             location_filter=location_filter,

                             # Metrics and analytics
                             **metrics,
                             analytics_data=analytics_data,

                             # Additional data
                             current_date=date.today(),
                             user=current_user)

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

    # Today's activity
    today = date.today()
    todays_transactions = SimpleStockTransaction.query.filter(
        func.date(SimpleStockTransaction.date_time) == today
    ).count()

    # Average turnover
    total_turnover = sum(item.turnover_rate for item in items)
    average_turnover = total_turnover / total_items if total_items > 0 else 0

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
        # Stock status
        if item.is_out_of_stock:
            status_distribution['out_of_stock'] += 1
        elif item.is_low_stock:
            status_distribution['low_stock'] += 1
        elif item.is_overstocked:
            status_distribution['overstocked'] += 1
        else:
            status_distribution['normal'] += 1

        # ABC classification
        abc_distribution[item.abc_classification] += 1

        # Category values
        if item.category:
            category_values[item.category] += item.stock_value

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

@app.route('/api/inventory/metrics')
@login_required
def api_inventory_metrics():
    """API endpoint for real-time inventory metrics"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        items = InventoryProduct.query.filter_by(is_active=True).all()
        metrics = calculate_inventory_metrics(items)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/alerts')
@login_required
def api_inventory_alerts():
    """API endpoint for real-time inventory alerts"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        alerts = SimpleLowStockAlert.query.join(InventoryProduct).filter(
            and_(
                InventoryProduct.is_active == True,
                SimpleLowStockAlert.is_acknowledged == False,
                SimpleLowStockAlert.is_resolved == False
            )
        ).order_by(desc(SimpleLowStockAlert.priority_score)).limit(10).all()

        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'item_name': alert.item.name,
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'current_stock': alert.current_stock,
                'minimum_stock': alert.minimum_stock,
                'days_active': alert.days_active,
                'priority_score': alert.priority_score
            })

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

        # Create initial stock transaction if stock > 0
        initial_stock = float(data.get('initial_stock', 0))
        if initial_stock > 0:
            transaction = SimpleStockTransaction(
                item_id=new_item.id,
                transaction_type='Purchase',
                quantity_change=initial_stock,
                previous_stock=0,
                new_stock_level=initial_stock,
                user_id=current_user.id,
                reason='Initial stock entry',
                reference_number=f'INIT-{new_item.id}',
                unit_cost=new_item.unit_cost,
                total_cost=initial_stock * new_item.unit_cost
            )
            db.session.add(transaction)

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

        # Create transaction
        transaction = SimpleStockTransaction(
            item_id=item_id,
            transaction_type='Adjustment',
            quantity_change=adjustment,
            previous_stock=previous_stock,
            new_stock_level=new_stock,
            user_id=current_user.id,
            reason=reason,
            reference_number=f'QUICK-{int(datetime.now().timestamp())}'
        )
        db.session.add(transaction)

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