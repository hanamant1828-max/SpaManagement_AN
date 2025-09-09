"""
Inventory Management Views
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_required, current_user
from datetime import datetime, date
import csv
import io
from sqlalchemy import desc, or_, func
from app import app, db
from .models import (
    InventoryProduct, InventoryCategory, StockMovement, InventoryAlert, InventoryConsumption
)
from .queries import (
    get_all_products, get_product_by_id, create_product, update_product, delete_product,
    get_all_categories, get_category_by_id, create_category, update_category, delete_category,
    get_low_stock_products, get_out_of_stock_products, get_products_needing_reorder,
    search_products, update_stock, add_stock, remove_stock, get_stock_movements,
    get_inventory_dashboard_stats, get_active_alerts, check_stock_alerts,
    get_all_consumption_records, get_consumption_by_id, create_consumption_record,
    update_consumption_record, delete_consumption_record, get_consumption_summary_stats
)

# ============ MAIN INVENTORY DASHBOARD ============

@app.route('/inventory')
@login_required
def inventory_dashboard():
    """Main inventory management dashboard"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('inventory_dashboard.html')

# ============ PRODUCT MANAGEMENT ============

@app.route('/inventory/products')
@login_required
def inventory_products():
    """Product catalog management"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get filter parameters
    category_filter = request.args.get('category')
    status_filter = request.args.get('status', 'all')
    search_term = request.args.get('search', '')

    # Apply filters
    if search_term:
        products = search_products(search_term)
    elif status_filter == 'low_stock':
        products = get_low_stock_products()
    elif status_filter == 'out_of_stock':
        products = get_out_of_stock_products()
    elif status_filter == 'reorder':
        products = get_products_needing_reorder()
    else:
        products = get_all_products()

    # Apply category filter
    if category_filter and category_filter != 'all':
        products = [p for p in products if str(p.category_id) == category_filter]

    categories = get_all_categories()

    return render_template('inventory/products.html',
                         products=products,
                         categories=categories,
                         current_filters={
                             'category': category_filter,
                             'status': status_filter,
                             'search': search_term
                         })

@app.route('/inventory/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """Add new product"""
    if not current_user.can_access('inventory'):
        if request.method == 'GET':
            flash('Access denied', 'danger')
            return redirect(url_for('dashboard'))
        return jsonify({'error': 'Access denied'}), 403

    if request.method == 'GET':
        # Redirect GET requests to the products page
        return redirect(url_for('inventory_products'))

    try:
        # Defensive coding - safely get form data with proper null checking and defaults
        sku = (request.form.get('sku') or '').strip()
        name = (request.form.get('name') or '').strip()
        description = (request.form.get('description') or '').strip()
        category_id = request.form.get('category_id')
        unit_of_measure = (request.form.get('unit_of_measure') or 'pcs').strip()
        barcode = (request.form.get('barcode') or '').strip()
        location = (request.form.get('location') or '').strip()

        # Input validation with user-friendly messages
        if not sku:
            return jsonify({'error': 'Product SKU is required. Please enter a unique product identifier.'}), 400

        if not name:
            return jsonify({'error': 'Product name is required. Please enter a descriptive product name.'}), 400

        if len(name) > 200:
            return jsonify({'error': 'Product name must be less than 200 characters.'}), 400

        if len(sku) > 50:
            return jsonify({'error': 'Product SKU must be less than 50 characters.'}), 400

        # Enhanced helper functions for safe data conversion
        def safe_float(value, default=0.0, field_name="field"):
            """Safely convert value to float with validation"""
            if value is None or value == '' or (isinstance(value, str) and value.strip() == ''):
                return default
            try:
                result = float(value)
                if result < 0 and field_name in ['current_stock', 'min_stock_level', 'max_stock_level', 'cost_price', 'selling_price']:
                    return default
                return result
            except (ValueError, TypeError):
                return default

        def safe_int(value, default=0):
            """Safely convert value to integer with validation"""
            if value is None or value == '' or (isinstance(value, str) and value.strip() == ''):
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        # Validate category_id if provided
        parsed_category_id = None
        if category_id and str(category_id).strip() and str(category_id).strip() != '0':
            try:
                parsed_category_id = int(category_id)
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid category selected. Please choose a valid category.'}), 400

        product_data = {
            'sku': sku,
            'name': name,
            'description': description,
            'category_id': parsed_category_id,
            'current_stock': safe_float(request.form.get('current_stock'), 0.0, 'current_stock'),
            'reserved_stock': 0.0,  # Initialize reserved stock
            'available_stock': 0.0,  # Will be calculated
            'min_stock_level': safe_float(request.form.get('min_stock_level'), 10.0, 'min_stock_level'),
            'max_stock_level': safe_float(request.form.get('max_stock_level'), 100.0, 'max_stock_level'),
            'reorder_point': safe_float(request.form.get('reorder_point'), 20.0, 'reorder_point'),
            'cost_price': safe_float(request.form.get('cost_price'), 0.0, 'cost_price'),
            'selling_price': safe_float(request.form.get('selling_price'), 0.0, 'selling_price'),
            'unit_of_measure': unit_of_measure,
            'barcode': barcode,
            'location': location,
            'is_service_item': bool(request.form.get('is_service_item', False)),
            'is_retail_item': bool(request.form.get('is_retail_item', False))
        }

        # Business logic validation
        if product_data['min_stock_level'] >= product_data['max_stock_level']:
            return jsonify({'error': 'Minimum stock level must be less than maximum stock level.'}), 400

        product = create_product(product_data)

        # Create initial stock movement if stock > 0
        if product.current_stock > 0:
            update_stock(product.id, product.current_stock, 'in', 
                         'Initial stock', 'manual', None, current_user.id)

        return jsonify({'success': True, 'message': f'Product "{product.name}" added successfully!'})

    except ValueError:
        return jsonify({'error': 'Invalid input values. Please check your data.'}), 400
    except Exception as e:
        return jsonify({'error': f'Error adding product: {str(e)}'}), 500

@app.route('/inventory/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Edit existing product"""
    if not current_user.can_access('inventory'):
        if request.method == 'GET':
            flash('Access denied', 'danger')
            return redirect(url_for('dashboard'))
        return jsonify({'error': 'Access denied'}), 403

    product = get_product_by_id(product_id)
    if not product:
        if request.method == 'GET':
            flash('Product not found', 'danger')
            return redirect(url_for('inventory_products'))
        return jsonify({'error': 'Product not found'}), 404

    if request.method == 'POST':
        try:
            # Helper function to safely convert to float with default
            def safe_float(value, default=0.0):
                if value is None or value == '':
                    return default
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default

            # Validation first
            name = request.form.get('name')
            if not name or not name.strip():
                return jsonify({'error': 'Product name is required'}), 400

            product_data = {
                'name': name.strip(),
                'description': request.form.get('description', '').strip(),
                'category_id': int(request.form.get('category_id')) if request.form.get('category_id') and request.form.get('category_id').strip() else None,
                'min_stock_level': safe_float(request.form.get('min_stock_level'), 10.0),
                'max_stock_level': safe_float(request.form.get('max_stock_level'), 100.0),
                'reorder_point': safe_float(request.form.get('reorder_point'), 20.0),
                'cost_price': safe_float(request.form.get('cost_price'), 0.0),
                'selling_price': safe_float(request.form.get('selling_price'), 0.0),
                'unit_of_measure': request.form.get('unit_of_measure', 'pcs').strip(),
                'barcode': request.form.get('barcode', '').strip(),
                'location': request.form.get('location', '').strip(),
                'is_service_item': 'is_service_item' in request.form,
                'is_retail_item': 'is_retail_item' in request.form
            }

            updated_product = update_product(product_id, product_data)
            if updated_product:
                return jsonify({'success': True, 'message': f'Product "{updated_product.name}" updated successfully!'})
            else:
                return jsonify({'error': 'Error updating product'}), 500

        except ValueError:
            return jsonify({'error': 'Invalid input values. Please check your data.'}), 400
        except Exception as e:
            return jsonify({'error': f'Error updating product: {str(e)}'}), 500

    # GET request - render form
    categories = get_all_categories()
    return render_template('inventory/product_form.html',
                         product=product,
                         categories=categories,
                         action='edit')

@app.route('/inventory/products/<int:product_id>/view')
@login_required
def view_product(product_id):
    """View product details with stock history"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('inventory_products'))

    # Get stock movement history
    movements = get_stock_movements(product_id, limit=20)

    return render_template('inventory/product_details.html',
                         product=product,
                         movements=movements)

@app.route('/inventory/products/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product_route(product_id):
    """Delete product"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    product = get_product_by_id(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    try:
        # Check if product has stock movements
        if hasattr(product, 'stock_movements') and product.stock_movements:
            return jsonify({'error': f'Cannot delete product "{product.name}" because it has stock movement history. Please consider deactivating it instead.'}), 400

        # Check if product has current stock
        if product.current_stock and product.current_stock > 0:
            return jsonify({'error': f'Cannot delete product "{product.name}" because it has current stock ({product.current_stock} {product.unit_of_measure}). Please remove all stock first.'}), 400

        # Store product name for success message
        product_name = product.name

        if delete_product(product_id):
            return jsonify({'success': True, 'message': f'Product "{product_name}" deleted successfully'})
        else:
            return jsonify({'error': 'Error deleting product'}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting product: {str(e)}'}), 500

# ============ CATEGORY MANAGEMENT ============

@app.route('/inventory/categories')
@login_required
def inventory_categories():
    """Category management with table view"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    categories = get_all_categories()
    return render_template('inventory/categories.html', categories=categories)

@app.route('/inventory/categories/add', methods=['GET', 'POST'])
@login_required
def add_inventory_category():
    """Add new category"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            category_data = {
                'name': request.form.get('name', '').strip(),
                'description': request.form.get('description', '').strip(),
                'color_code': request.form.get('color_code', '#007bff').strip()
            }

            if not category_data['name']:
                flash('Category name is required', 'danger')
                return redirect(request.url)

            category = create_category(category_data)
            flash(f'Category "{category.name}" added successfully!', 'success')
            return redirect(url_for('inventory_categories'))

        except Exception as e:
            flash(f'Error adding category: {str(e)}', 'danger')

    return render_template('inventory/category_form.html', action='add')

@app.route('/inventory/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_inventory_category(category_id):
    """Edit existing category"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    category = get_category_by_id(category_id)
    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('inventory_categories'))

    if request.method == 'POST':
        try:
            category_data = {
                'name': request.form.get('name', '').strip(),
                'description': request.form.get('description', '').strip(),
                'color_code': request.form.get('color_code', '#007bff').strip()
            }

            if not category_data['name']:
                flash('Category name is required', 'danger')
                return redirect(request.url)

            updated_category = update_category(category_id, category_data)
            if updated_category:
                flash(f'Category "{updated_category.name}" updated successfully!', 'success')
                return redirect(url_for('inventory_categories'))
            else:
                flash('Error updating category', 'danger')

        except Exception as e:
            flash(f'Error updating category: {str(e)}', 'danger')

    return render_template('inventory/category_form.html', 
                         category=category, 
                         action='edit')

@app.route('/inventory/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category_route(category_id):
    """Delete category"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    category = get_category_by_id(category_id)
    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('inventory_categories'))

    try:
        # Check if category has products
        if category.products:
            flash(f'Cannot delete category "{category.name}" because it has {len(category.products)} associated products', 'danger')
            return redirect(url_for('inventory_categories'))

        if delete_category(category_id):
            flash(f'Category "{category.name}" deleted successfully!', 'success')
        else:
            flash('Error deleting category', 'danger')

    except Exception as e:
        flash(f'Error deleting category: {str(e)}', 'danger')

    return redirect(url_for('inventory_categories'))

# ============ STOCK MANAGEMENT ============

@app.route('/inventory/products/<int:product_id>/stock', methods=['POST'])
@login_required
def adjust_stock(product_id):
    """Adjust product stock levels"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('inventory_products'))

    try:
        adjustment_type = request.form.get('adjustment_type')  # set, add, remove
        quantity = float(request.form.get('quantity', 0))
        reason = request.form.get('reason', 'Stock adjustment').strip()

        if adjustment_type == 'set':
            updated_product = update_stock(product_id, quantity, 'adjustment', 
                                         reason, 'manual', None, current_user.id)
            action_msg = f'Stock set to {quantity}'
        elif adjustment_type == 'add':
            updated_product = add_stock(product_id, quantity, reason, 
                                      'manual', None, 0, current_user.id)
            action_msg = f'{quantity} units added'
        elif adjustment_type == 'remove':
            updated_product = remove_stock(product_id, quantity, reason, 
                                         'manual', None, current_user.id)
            action_msg = f'{quantity} units removed'
        else:
            flash('Invalid adjustment type', 'danger')
            return redirect(request.referrer or url_for('inventory_products'))

        if updated_product:
            flash(f'{product.name}: {action_msg}. New stock: {updated_product.current_stock}', 'success')
        else:
            flash('Error adjusting stock', 'danger')

    except ValueError:
        flash('Invalid quantity value', 'danger')
    except Exception as e:
        flash(f'Error adjusting stock: {str(e)}', 'danger')

    return redirect(request.referrer or url_for('inventory_products'))

@app.route('/inventory/stock-movements')
@login_required
def stock_movements():
    """View all stock movements with filtering"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    product_id = request.args.get('product_id', type=int)
    limit = request.args.get('limit', 50, type=int)

    movements = get_stock_movements(product_id, limit)
    products = get_all_products()  # For filter dropdown

    return render_template('inventory/stock_movements.html',
                         movements=movements,
                         products=products,
                         current_product_id=product_id)





# ============ ALERTS AND REPORTING ============

@app.route('/inventory/alerts')
@login_required
def inventory_alerts():
    """View inventory alerts"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    alerts = get_active_alerts()
    return render_template('inventory/alerts.html', alerts=alerts)

@app.route('/inventory/reports')
@login_required
def inventory_reports():
    """Inventory reporting dashboard"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    stats = get_inventory_dashboard_stats()

    return render_template('inventory/reports.html', stats=stats)

@app.route('/inventory/export/products')
@login_required
def export_products():
    """Export products to CSV"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    products = get_all_products()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'SKU', 'Name', 'Category', 'Current Stock', 'Min Level',
        'Max Level', 'Reorder Point', 'Cost Price', 'Selling Price', 'Unit',
        'Location', 'Status', 'Stock Value'
    ])

    # Write data
    for product in products:
        writer.writerow([
            product.sku,
            product.name,
            product.category.name if product.category else '',
            product.current_stock,
            product.min_stock_level,
            product.max_stock_level,
            product.reorder_point,
            product.cost_price,
            product.selling_price,
            product.unit_of_measure,
            product.location,
            product.stock_status,
            product.stock_value
        ])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-disposition": f"attachment; filename=inventory_products_{date.today().strftime('%Y%m%d')}.csv"}
    )

# ============ INVENTORY ADJUSTMENTS API ============

@app.route('/api/inventory/adjustments', methods=['POST'])
@login_required
def api_inventory_adjustments():
    """API endpoint to add inventory items (stock adjustments)"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided. Please submit adjustment details.'}), 400

        # Defensive coding with safe defaults
        adjustment_date = (data.get('adjustment_date') or '').strip()
        reference_no = (data.get('reference_no') or '').strip()
        notes = (data.get('notes') or '').strip()  # Fixed: was referencing 'desc' 
        items = data.get('items') or []

        # Input validation with user-friendly messages
        if not adjustment_date:
            return jsonify({'error': 'Adjustment date is required. Please select a valid date.'}), 400

        if not items or len(items) == 0:
            return jsonify({'error': 'At least one inventory item is required for adjustment. Please add items to proceed.'}), 400

        # Parse the date
        try:
            adjustment_date = datetime.strptime(adjustment_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

        # Process each item with defensive coding
        stock_updates = []
        total_value = 0.0
        processed_items = 0

        for index, item in enumerate(items):
            # Safe extraction with defaults
            product_id = item.get('product_id')
            quantity_in = item.get('quantity_in')
            unit_cost_str = item.get('unit_cost', '0')

            # Skip empty items
            if not product_id:
                continue

            # Validate product_id
            try:
                product_id = int(product_id)
            except (ValueError, TypeError):
                return jsonify({'error': f'Invalid product selected for item #{index + 1}. Please select a valid product.'}), 400

            # Validate quantity with user-friendly messages
            if not quantity_in:
                return jsonify({'error': f'Quantity is required for item #{index + 1}. Please enter the quantity to add.'}), 400

            try:
                quantity_in = float(quantity_in)
                if quantity_in <= 0:
                    return jsonify({'error': f'Quantity must be greater than 0 for item #{index + 1}.'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': f'Invalid quantity value for item #{index + 1}. Please enter a valid number.'}), 400

            # Safe unit cost conversion
            try:
                unit_cost = float(unit_cost_str) if unit_cost_str else 0.0
                if unit_cost < 0:
                    unit_cost = 0.0
            except (ValueError, TypeError):
                unit_cost = 0.0

            product = get_product_by_id(product_id)
            if not product:
                return jsonify({'error': f'Product with ID {product_id} not found'}), 400

            # Build structured reason that can be parsed back to clean fields
            reason_parts = ["Manual stock adjustment"]
            if reference_no and reference_no.strip():
                reason_parts.append(f"Ref: {reference_no.strip()}")

            # Add date and user info
            reason_parts.append(adjustment_date.strftime('%Y-%m-%d'))
            reason_parts.append(current_user.username if current_user else 'System')

            # Add notes if provided
            if notes and notes.strip():
                clean_notes = ' '.join(notes.strip().split())  # Collapse whitespace
                reason_parts.append(f"Notes: {clean_notes}")

            reason = ' — '.join(reason_parts)

            updated_product = add_stock(
                product_id=product_id,
                quantity=quantity_in,
                reason=reason,
                reference_type='manual',
                reference_id=None,
                unit_cost=unit_cost,
                user_id=current_user.id
            )

            if updated_product:
                stock_updates.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_sku': product.sku,
                    'quantity_added': quantity_in,
                    'new_stock_level': float(updated_product.current_stock or 0),
                    'unit_of_measure': product.unit_of_measure
                })
                total_value += float(quantity_in) * float(unit_cost)

        return jsonify({
            'success': True,
            'message': f'Stock adjustment completed successfully. {len(stock_updates)} items updated.',
            'stock_updates': stock_updates,
            'total_value': total_value
        })

    except Exception as e:
        return jsonify({'error': f'Error processing stock adjustment: {str(e)}'}), 500

# ============ INVENTORY ADJUSTMENTS API ============

@app.route('/api/inventory/adjustments')
@login_required
def api_get_adjustments():
    """Get all inventory adjustments"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Get all adjustment records from stock movements
        adjustments = []
        adjustment_movements = db.session.query(StockMovement).filter(
            StockMovement.reference_type == 'manual'
        ).order_by(desc(StockMovement.created_at)).all()

        # Group movements by reference_id and created_at (same adjustment)
        adjustment_groups = {}
        for movement in adjustment_movements:
            # Create a safer key that handles None values
            created_date = movement.created_at.date() if movement.created_at else date.today()
            created_by = movement.created_by if movement.created_by else 0
            reason = movement.reason if movement.reason else 'Manual adjustment'

            key = f"{created_date}_{created_by}_{hash(reason)}"
            if key not in adjustment_groups:
                adjustment_groups[key] = []
            adjustment_groups[key].append(movement)

        for key, movements in adjustment_groups.items():
            if not movements:
                continue

            first_movement = movements[0]
            total_value = sum(float(m.quantity or 0) * float(m.unit_cost or 0) for m in movements)

            # Extract clean reference_id and remarks from reason field
            reference_id = ""
            remarks = ""

            if first_movement.reason:
                reason = first_movement.reason.strip()

                # Extract reference ID if present in new format
                if ' — Ref: ' in reason:
                    try:
                        parts = reason.split(' — ')
                        for part in parts:
                            if part.startswith('Ref: '):
                                reference_id = part[5:].strip()
                            elif part.startswith('Notes: '):
                                remarks = part[7:].strip()
                    except (IndexError, AttributeError):
                        pass

                # Extract reference ID if present in legacy format
                elif ' - Ref: ' in reason:
                    try:
                        ref_part = reason.split(' - Ref: ')[1]
                        reference_id = ref_part.split(' - ')[0].strip()

                        # Extract remaining text as remarks
                        remaining_parts = ref_part.split(' - ')[1:]
                        if remaining_parts:
                            remarks = ' - '.join(remaining_parts).strip()
                    except (IndexError, AttributeError):
                        pass

                # If no structured format, use the whole reason as remarks
                if not reference_id and not remarks:
                    remarks = reason

            adjustments.append({
                'id': first_movement.id,
                'reference_id': reference_id if reference_id else "",
                'adjustment_date': first_movement.created_at.strftime('%Y-%m-%d') if first_movement.created_at else date.today().strftime('%Y-%m-%d'),
                'items_count': len(movements),
                'subtotal': float(total_value),
                'total_value': float(total_value),
                'remarks': remarks if remarks else "",
                'created_by': first_movement.user.username if first_movement.user else "—"
            })

        return jsonify({'records': adjustments})
    except Exception as e:
        return jsonify({'error': f'Error loading adjustments: {str(e)}'}), 500

@app.route('/api/inventory/adjustments/<int:adjustment_id>')
@login_required
def api_get_adjustment(adjustment_id):
    """Get specific adjustment details"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Get the movement record
        movement = StockMovement.query.get(adjustment_id)
        if not movement:
            return jsonify({'error': 'Adjustment not found'}), 404

        # Get all related movements (same reason and date)
        related_movements = StockMovement.query.filter(
            StockMovement.reason == movement.reason,
            StockMovement.created_at == movement.created_at,
            StockMovement.created_by == movement.created_by
        ).all()

        items = []
        total_value = 0
        for mov in related_movements:
            quantity = float(mov.quantity or 0)
            unit_cost = float(mov.unit_cost or 0)
            line_total = quantity * unit_cost
            total_value += line_total

            # Get current stock from product
            current_stock = 0
            if mov.product:
                current_stock = float(mov.product.current_stock or 0)

            items.append({
                'product_id': mov.product_id,
                'product_name': mov.product.name if mov.product else 'Unknown',
                'current_stock': current_stock,
                'quantity_added': quantity,
                'unit_cost': unit_cost,
                'line_total': float(line_total)
            })

        # Extract clean reference_id and remarks from reason field
        reference_id = ""
        remarks = ""

        if movement.reason:
            reason = movement.reason.strip()

            # Extract reference ID if present in new format
            if ' — Ref: ' in reason:
                try:
                    parts = reason.split(' — ')
                    for part in parts:
                        if part.startswith('Ref: '):
                            reference_id = part[5:].strip()
                        elif part.startswith('Notes: '):
                            remarks = part[7:].strip()
                except (IndexError, AttributeError):
                    pass

            # Extract reference ID if present in legacy format
            elif ' - Ref: ' in reason:
                try:
                    ref_part = reason.split(' - Ref: ')[1]
                    reference_id = ref_part.split(' - ')[0].strip()

                    # Extract remaining text as remarks
                    remaining_parts = ref_part.split(' - ')[1:]
                    if remaining_parts:
                        remarks = ' - '.join(remaining_parts).strip()
                except (IndexError, AttributeError):
                    pass

            # If no structured format, use the whole reason as remarks
            if not reference_id and not remarks:
                remarks = reason

        return jsonify({
            'id': adjustment_id,
            'reference_id': reference_id,
            'adjustment_date': movement.created_at.strftime('%Y-%m-%d') if movement.created_at else date.today().strftime('%Y-%m-%d'),
            'created_by': movement.user.username if movement.user else '—',
            'created_date': movement.created_at.strftime('%Y-%m-%d %H:%M:%S') if movement.created_at else 'Unknown',
            'remarks': remarks,
            'items': items,
            'subtotal': float(total_value),
            'tax': 0.0,
            'total_value': float(total_value)
        })
    except Exception as e:
        return jsonify({'error': f'Error loading adjustment: {str(e)}'}), 500

@app.route('/api/inventory/adjustments/<int:adjustment_id>', methods=['DELETE'])
@login_required
def api_delete_adjustment(adjustment_id):
    """Delete adjustment and reverse stock changes"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Get the movement record
        movement = StockMovement.query.get(adjustment_id)
        if not movement:
            return jsonify({'error': 'Adjustment not found'}), 404

        # Get all related movements (same reason and date)
        related_movements = StockMovement.query.filter(
            StockMovement.reason == movement.reason,
            StockMovement.created_at == movement.created_at,
            StockMovement.created_by == movement.created_by
        ).all()

        # Reverse each movement
        for mov in related_movements:
            product = get_product_by_id(mov.product_id)
            if product:
                # Subtract the quantity that was originally added
                new_stock = product.current_stock - mov.quantity
                update_stock(
                    product_id=mov.product_id,
                    new_quantity=new_stock,
                    movement_type='adjustment_reversal',
                    reason=f"Adjustment deleted - Reversed: {mov.reason}",
                    reference_type='adjustment_deleted',
                    reference_id=mov.id,
                    user_id=current_user.id
                )

        # Delete the original movement records
        for mov in related_movements:
            db.session.delete(mov)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Adjustment deleted successfully. Stock levels have been reversed for {len(related_movements)} items.'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting adjustment: {str(e)}'}), 500

# ============ PRODUCT API ENDPOINTS ============

@app.route('/api/inventory/products/<int:product_id>/delete', methods=['DELETE'])
@login_required
def api_delete_product(product_id):
    """Delete product"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Check if product has related records
        product = get_product_by_id(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # Check for related consumption records
        consumption_count = InventoryConsumption.query.filter_by(product_id=product_id).count()
        if consumption_count > 0:
            return jsonify({'error': f'Cannot delete product with {consumption_count} consumption records. Please contact administrator.'}), 400

        # Check for related stock movements
        movement_count = StockMovement.query.filter_by(product_id=product_id).count()
        if movement_count > 0:
            return jsonify({'error': f'Cannot delete product with {movement_count} stock movements. Please contact administrator.'}), 400

        if delete_product(product_id):
            return jsonify({
                'success': True,
                'message': f'Product "{product.name}" deleted successfully'
            })
        else:
            return jsonify({'error': 'Failed to delete product'}), 500

    except Exception as e:
        return jsonify({'error': f'Error deleting product: {str(e)}'}), 500

# ============ CATEGORY API ENDPOINTS ============

@app.route('/api/inventory/categories')
@login_required
def api_get_categories():
    """Get all categories as JSON"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        categories = get_all_categories()
        category_list = []

        for category in categories:
            # Count products in this category
            product_count = len([p for p in category.products if p.is_active])

            category_list.append({
                'id': category.id,
                'name': category.name,
                'description': category.description or '',
                'color_code': category.color_code,
                'is_active': category.is_active,
                'product_count': product_count,
                'created_at': category.created_at.isoformat() if category.created_at else None
            })

        return jsonify({'categories': category_list})
    except Exception as e:
        return jsonify({'error': f'Error loading categories: {str(e)}'}), 500

@app.route('/api/inventory/categories', methods=['POST'])
@login_required
def api_add_category():
    """Add new category"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validation
        if not data.get('name', '').strip():
            return jsonify({'error': 'Category name is required'}), 400

        category_data = {
            'name': data['name'].strip(),
            'description': data.get('description', '').strip(),
            'color_code': data.get('color_code', '#007bff').strip(),
            'is_active': data.get('is_active', True)
        }

        category = create_category(category_data)

        return jsonify({
            'success': True,
            'message': f'Category "{category.name}" added successfully!',
            'category': {
                'id': category.id,
                'name': category.name,
                'color_code': category.color_code
            }
        })

    except Exception as e:
        return jsonify({'error': f'Error adding category: {str(e)}'}), 500

@app.route('/api/inventory/categories/<int:category_id>')
@login_required
def api_get_category(category_id):
    """Get category details"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        category = get_category_by_id(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404

        # Count products in this category
        product_count = InventoryProduct.query.filter_by(category_id=category_id).count()

        return jsonify({
            'id': category.id,
            'name': category.name,
            'description': category.description or '',
            'color_code': category.color_code,
            'is_active': category.is_active,
            'product_count': product_count,
            'created_at': category.created_at.isoformat() if category.created_at else None
        })

    except Exception as e:
        return jsonify({'error': f'Error loading category: {str(e)}'}), 500

@app.route('/api/inventory/categories/<int:category_id>/edit', methods=['POST'])
@login_required
def api_edit_category(category_id):
    """Update category"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        category_data = {
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip(),
            'color_code': request.form.get('color_code', '#007bff').strip(),
            'is_active': request.form.get('is_active') == 'on'
        }

        if not category_data['name']:
            return jsonify({'error': 'Category name is required'}), 400

        updated_category = update_category(category_id, category_data)
        if updated_category:
            return jsonify({
                'success': True,
                'message': f'Category "{updated_category.name}" updated successfully'
            })
        else:
            return jsonify({'error': 'Category not found'}), 404

    except Exception as e:
        return jsonify({'error': f'Error updating category: {str(e)}'}), 500

@app.route('/api/inventory/categories/<int:category_id>/delete', methods=['DELETE'])
@login_required
def api_delete_category(category_id):
    """Delete category (soft delete)"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        category = get_category_by_id(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404

        # Check for products in this category
        product_count = InventoryProduct.query.filter_by(category_id=category_id).count()
        if product_count > 0:
            return jsonify({'error': f'Cannot delete category with {product_count} products. Please reassign products first.'}), 400

        if delete_category(category_id):
            return jsonify({
                'success': True,
                'message': f'Category "{category.name}" deleted successfully'
            })
        else:
            return jsonify({'error': 'Failed to delete category'}), 500

    except Exception as e:
        return jsonify({'error': f'Error deleting category: {str(e)}'}), 500

# ============ CONSUMPTION API ENDPOINTS ============

@app.route('/api/inventory/consumption/<int:consumption_id>/edit', methods=['POST'])
@login_required
def api_edit_consumption(consumption_id):
    """Update consumption record with proper stock delta handling"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Get the original consumption record
        original_consumption = get_consumption_by_id(consumption_id)
        if not original_consumption:
            return jsonify({'error': 'Consumption record not found'}), 404

        # Get form data with defensive coding
        product_id = request.form.get('product_id')
        consumption_date_str = request.form.get('consumption_date', '').strip()
        quantity_used_str = request.form.get('quantity_used', '').strip()
        issued_to = request.form.get('issued_to', '').strip()
        reference_doc_no = request.form.get('reference_doc_no', '').strip()
        notes = request.form.get('notes', '').strip()

        # Validation with user-friendly messages
        if not product_id:
            return jsonify({'error': 'Please select a product'}), 400

        if not consumption_date_str:
            return jsonify({'error': 'Please select a consumption date'}), 400

        if not quantity_used_str:
            return jsonify({'error': 'Please enter the quantity used'}), 400

        if not issued_to:
            return jsonify({'error': 'Please specify who the items were issued to'}), 400

        # Parse and validate data
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid product selected'}), 400

        try:
            from decimal import Decimal
            new_quantity_used = Decimal(str(quantity_used_str))
            if new_quantity_used <= 0:
                return jsonify({'error': 'Quantity must be greater than 0'}), 400
            # Convert back to float for consistency with existing code
            new_quantity_used = float(new_quantity_used)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid quantity value'}), 400

        # Parse date
        try:
            if '/' in consumption_date_str:
                consumption_date = datetime.strptime(consumption_date_str, '%m/%d/%Y').date()
            elif '-' in consumption_date_str and len(consumption_date_str) == 10:
                consumption_date = datetime.strptime(consumption_date_str, '%Y-%m-%d').date()
            else:
                consumption_date = datetime.fromisoformat(consumption_date_str).date()
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD format'}), 400

        # Check if product exists
        product = get_product_by_id(product_id)
        if not product:
            return jsonify({'error': 'Selected product not found'}), 404

        # Calculate delta (difference between new and old quantity) using Decimal
        from decimal import Decimal
        original_quantity = Decimal(str(original_consumption.quantity_used or 0))
        new_quantity_decimal = Decimal(str(new_quantity_used))
        delta = new_quantity_decimal - original_quantity

        # If delta is positive (increase), check if we have enough stock
        if delta > 0:
            current_stock = Decimal(str(product.current_stock or 0))
            if current_stock < delta:
                return jsonify({'error': f'Insufficient stock for increase. Available: {current_stock} {product.unit_of_measure}, Additional required: {delta}'}), 400

        # Update consumption data
        consumption_data = {
            'product_id': product_id,
            'consumption_date': consumption_date,
            'quantity_used': new_quantity_used,
            'issued_to': issued_to,
            'reference_doc_no': reference_doc_no if reference_doc_no else None,
            'notes': notes if notes else None
        }

        # Update the consumption record
        updated_consumption = update_consumption_record(consumption_id, consumption_data, current_user.id)

        if updated_consumption:
            # Handle stock adjustment for the delta
            if delta != 0:
                new_stock = float(product.current_stock) - delta  # Subtract delta (positive delta = more consumed = less stock)
                reason = f"Consumption Edited - {'+' if delta > 0 else ''}{delta} {product.unit_of_measure}"

                update_stock(
                    product_id=product_id,
                    new_quantity=max(0, new_stock),  # Prevent negative stock
                    movement_type='adjustment',
                    reason=reason,
                    reference_type='consumption_edit',
                    reference_id=consumption_id,
                    user_id=current_user.id
                )

            return jsonify({
                'success': True,
                'message': f'Consumption record updated successfully. Stock adjusted by {-delta} {product.unit_of_measure}.'
            })
        else:
            return jsonify({'error': 'Failed to update consumption record'}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error updating consumption: {str(e)}'}), 500

@app.route('/api/inventory/consumption/<int:consumption_id>/delete', methods=['DELETE'])
@login_required
def api_delete_consumption(consumption_id):
    """Delete consumption record and restore stock"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        consumption = get_consumption_by_id(consumption_id)
        if not consumption:
            return jsonify({'error': 'Consumption record not found'}), 404

        # Store details for success message
        product_name = consumption.product.name if consumption.product else 'Unknown Product'
        quantity_restored = float(consumption.quantity_used or 0)
        unit = consumption.unit_of_measure or 'pcs'

        # Restore stock by adding back the consumed quantity
        product = get_product_by_id(consumption.product_id)
        if product:
            restored_stock = float(product.current_stock or 0) + quantity_restored
            update_stock(
                product_id=consumption.product_id,
                new_quantity=restored_stock,
                movement_type='in',
                reason=f"Consumption Deleted - Stock Restored (+{quantity_restored} {unit})",
                reference_type='consumption_deletion',
                reference_id=consumption_id,
                user_id=current_user.id
            )

        # Delete the consumption record
        if delete_consumption_record(consumption_id):
            return jsonify({
                'success': True,
                'message': f'Consumption record deleted successfully. Restored {quantity_restored} {unit} to {product_name}.'
            })
        else:
            return jsonify({'error': 'Failed to delete consumption record'}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting consumption: {str(e)}'}), 500

# ============ ADJUSTMENT API ENDPOINTS ============

@app.route('/api/inventory/adjustments/<int:adjustment_id>/edit', methods=['POST'])
@login_required
def api_edit_adjustment(adjustment_id):
    """Update adjustment record"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Get the original movement record
        original_movement = StockMovement.query.get(adjustment_id)
        if not original_movement:
            return jsonify({'error': 'Adjustment not found'}), 404

        # Extract data with defaults
        adjustment_date_str = data.get('adjustment_date', '')
        reference_id = data.get('reference_id', '').strip()
        remarks = data.get('remarks', '').strip()
        items = data.get('items', [])

        if not adjustment_date_str:
            return jsonify({'error': 'Adjustment date is required'}), 400

        if not items:
            return jsonify({'error': 'At least one item is required'}), 400

        # Parse date
        try:
            adjustment_date = datetime.strptime(adjustment_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

        # Get all related movements (same original reason and created_at)
        related_movements = StockMovement.query.filter(
            StockMovement.reason == original_movement.reason,
            StockMovement.created_at == original_movement.created_at,
            StockMovement.created_by == original_movement.created_by
        ).all()

        # Reverse original stock changes
        for movement in related_movements:
            if movement.product:
                product = movement.product
                # Subtract the original quantity that was added
                new_stock = float(product.current_stock) - float(movement.quantity)
                product.current_stock = max(0, new_stock)

        # Delete original movement records
        for movement in related_movements:
            db.session.delete(movement)

        # Create new movements for updated items
        updated_products = []
        for item in items:
            product_id = item.get('product_id')
            quantity = float(item.get('quantity_added', 0))
            unit_cost = float(item.get('unit_cost', 0))

            if not product_id or quantity <= 0:
                continue

            product = get_product_by_id(product_id)
            if not product:
                return jsonify({'error': f'Product with ID {product_id} not found'}), 400

            # Build structured reason that can be parsed back to clean fields
            reason_parts = ["Manual stock adjustment"]
            if reference_id and reference_id.strip():
                reason_parts.append(f"Ref: {reference_id.strip()}")

            # Add date and user info
            reason_parts.append(adjustment_date.strftime('%Y-%m-%d'))
            reason_parts.append(current_user.username if current_user else 'System')

            # Add remarks if provided
            if remarks and remarks.strip():
                clean_remarks = ' '.join(remarks.strip().split())  # Collapse whitespace
                reason_parts.append(f"Notes: {clean_remarks}")

            reason = ' — '.join(reason_parts)

            # Get current stock before update
            stock_before = float(product.current_stock or 0)

            # Calculate new stock after update
            stock_after = stock_before + quantity

            # Create new stock movement with required fields
            new_movement = StockMovement(
                product_id=product_id,
                movement_type='in',
                quantity=quantity,
                unit_cost=unit_cost,
                stock_before=stock_before,
                stock_after=stock_after,
                reason=reason,
                reference_type='manual',
                reference_id=None,
                created_by=current_user.id,
                created_at=datetime.now()
            )

            # Update product stock
            product.current_stock = stock_after

            db.session.add(new_movement)
            updated_products.append({
                'product_name': product.name,
                'quantity_added': quantity,
                'new_stock': float(product.current_stock)
            })

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Adjustment updated successfully. {len(updated_products)} items updated.',
            'updated_products': updated_products
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error updating adjustment: {str(e)}'}), 500

# ============ API ENDPOINTS ============

@app.route('/api/inventory/product/<int:product_id>')
@login_required
def api_get_product(product_id):
    """Get product data as JSON"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    product = get_product_by_id(product_id)
    if product:
        return jsonify({
            'id': product.id,
            'sku': product.sku or '',
            'name': product.name or '',
            'description': product.description or '',
            'category_id': product.category_id,
            'current_stock': float(product.current_stock or 0),
            'min_stock_level': float(product.min_stock_level or 10),
            'max_stock_level': float(product.max_stock_level or 100),
            'reorder_point': float(product.reorder_point or 20),
            'cost_price': float(product.cost_price or 0),
            'selling_price': float(product.selling_price or 0),
            'unit_of_measure': product.unit_of_measure or 'pcs',
            'barcode': product.barcode or '',
            'location': product.location or '',
            'is_service_item': bool(product.is_service_item),
            'is_retail_item': bool(product.is_retail_item),
            'stock_status': product.stock_status
        })
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/inventory/product/sku/<string:sku>')
@login_required
def api_get_product_by_sku(sku):
    """Get product data by SKU as JSON"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    products = get_all_products()
    product = next((p for p in products if p.sku == sku), None)

    if product:
        return jsonify({
            'id': product.id,
            'sku': product.sku,
            'name': product.name,
            'description': product.description,
            'category_id': product.category_id,
            'current_stock': float(product.current_stock),
            'min_stock_level': float(product.min_stock_level),
            'max_stock_level': float(product.max_stock_level),
            'reorder_point': float(product.reorder_point),
            'cost_price': float(product.cost_price),
            'selling_price': float(product.selling_price),
            'unit_of_measure': product.unit_of_measure,
            'barcode': product.barcode,
            'location': product.location,
            'is_service_item': product.is_service_item,
            'is_retail_item': product.is_retail_item,
            'stock_status': product.stock_status
        })
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/inventory/dashboard-stats')
@login_required
def api_dashboard_stats():
    """Get dashboard statistics as JSON"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    stats = get_inventory_dashboard_stats()
    return jsonify(stats)

# ============ CONSUMPTION MANAGEMENT ============

@app.route('/inventory/consumption')
@login_required
def consumption_records():
    """List consumption records with search and pagination"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', '')
    per_page = 20

    # Get paginated consumption records
    consumption_pagination = get_all_consumption_records(page=page, per_page=per_page, search_term=search_term)

    return jsonify({
        'records': [{
            'id': record.id,
            'product_name': record.product.name,
            'product_sku': record.product.sku,
            'consumption_date': record.consumption_date.strftime('%Y-%m-%d'),
            'quantity_used': float(record.quantity_used),
            'unit_of_measure': record.unit_of_measure,
            'issued_to': record.issued_to,
            'reference_doc_no': record.reference_doc_no or '',
            'notes': record.notes or ''
        } for record in consumption_pagination.items],
        'pagination': {
            'page': page,
            'pages': consumption_pagination.pages,
            'total': consumption_pagination.total,
            'has_prev': consumption_pagination.has_prev,
            'has_next': consumption_pagination.has_next
        }
    })

@app.route('/api/inventory/consumption/add', methods=['POST'])
@login_required
def api_add_consumption():
    """Add new consumption record with proper validation and stock management"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Get form data with defensive coding
        product_id = request.form.get('product_id')
        consumption_date_str = request.form.get('consumption_date', '').strip()
        quantity_used_str = request.form.get('quantity_used', '').strip()
        issued_to = request.form.get('issued_to', '').strip()
        reference_doc_no = request.form.get('reference_doc_no', '').strip()
        notes = request.form.get('notes', '').strip()

        # Validation with user-friendly messages
        if not product_id:
            return jsonify({'error': 'Please select a product'}), 400

        if not consumption_date_str:
            return jsonify({'error': 'Please select a consumption date'}), 400

        if not quantity_used_str:
            return jsonify({'error': 'Please enter the quantity used'}), 400

        if not issued_to:
            return jsonify({'error': 'Please specify who the items were issued to'}), 400

        # Parse and validate data
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid product selected'}), 400

        try:
            from decimal import Decimal
            quantity_used = Decimal(str(quantity_used_str))
            if quantity_used <= 0:
                return jsonify({'error': 'Quantity must be greater than 0'}), 400
            # Convert back to float for JSON serialization compatibility
            quantity_used = float(quantity_used)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid quantity value'}), 400

        # Parse date with multiple format support
        try:
            if '/' in consumption_date_str:
                # Handle MM/DD/YYYY or DD/MM/YYYY formats
                consumption_date = datetime.strptime(consumption_date_str, '%m/%d/%Y').date()
            elif '-' in consumption_date_str and len(consumption_date_str) == 10:
                # Handle YYYY-MM-DD format (ISO)
                consumption_date = datetime.strptime(consumption_date_str, '%Y-%m-%d').date()
            else:
                # Try to parse as ISO date
                consumption_date = datetime.fromisoformat(consumption_date_str).date()
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD format'}), 400

        # Check if product exists and has sufficient stock
        product = get_product_by_id(product_id)
        if not product:
            return jsonify({'error': 'Selected product not found'}), 404

        current_stock = float(product.current_stock or 0)
        if current_stock < quantity_used:
            return jsonify({'error': f'Insufficient stock. Available: {current_stock} {product.unit_of_measure}, Required: {quantity_used}'}), 400

        # Create consumption data
        consumption_data = {
            'product_id': product_id,
            'consumption_date': consumption_date,
            'quantity_used': quantity_used,
            'issued_to': issued_to,
            'reference_doc_no': reference_doc_no if reference_doc_no else None,
            'notes': notes if notes else None
        }

        # Create the consumption record
        consumption = create_consumption_record(consumption_data, current_user.id)

        if consumption:
            return jsonify({
                'success': True,
                'message': f'Consumption record created successfully. Stock reduced by {quantity_used} {product.unit_of_measure}.',
                'id': consumption.id
            })
        else:
            return jsonify({'error': 'Failed to create consumption record'}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error creating consumption record: {str(e)}'}), 500

@app.route('/inventory/consumption/add', methods=['POST'])
@login_required
def add_consumption():
    """Legacy endpoint - redirect to API"""
    return api_add_consumption()

@app.route('/inventory/consumption/<int:consumption_id>/edit', methods=['POST'])
@login_required
def edit_consumption(consumption_id):
    """Edit existing consumption record"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        consumption_data = {
            'product_id': int(request.form.get('product_id')),
            'consumption_date': datetime.strptime(request.form.get('consumption_date'), '%Y-%m-%d').date(),
            'quantity_used': float(request.form.get('quantity_used')),
            'issued_to': request.form.get('issued_to').strip(),
            'reference_doc_no': request.form.get('reference_doc_no', '').strip(),
            'notes': request.form.get('notes', '').strip()
        }

        # Validation
        if not consumption_data['issued_to']:
            return jsonify({'error': 'Issued to field is required'}), 400

        if consumption_data['quantity_used'] <= 0:
            return jsonify({'error': 'Quantity must be greater than 0'}), 400

        consumption = update_consumption_record(consumption_id, consumption_data, current_user.id)
        if consumption:
            return jsonify({
                'success': True,
                'message': 'Consumption record updated successfully'
            })
        else:
            return jsonify({'error': 'Consumption record not found'}), 404

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to update consumption record'}), 500

@app.route('/inventory/consumption/<int:consumption_id>/delete', methods=['POST'])
@login_required
def delete_consumption(consumption_id):
    """Delete consumption record"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        success = delete_consumption_record(consumption_id, current_user.id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Consumption record deleted successfully'
            })
        else:
            return jsonify({'error': 'Consumption record not found'}), 404

    except Exception as e:
        return jsonify({'error': 'Failed to delete consumption record'}), 500

@app.route('/inventory/consumption/export')
@login_required
def export_consumption_csv():
    """Export consumption records to CSV"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    search_term = request.args.get('search', '')

    # Get all consumption records (no pagination for export)
    consumption_records = get_all_consumption_records(per_page=None, search_term=search_term)

    output = io.StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow([
        'Date', 'Item', 'SKU', 'Quantity Used', 'Unit', 
        'Issued To', 'Reference/Doc No.', 'Notes', 'Created By', 'Created At'
    ])

    # Data rows
    for record in consumption_records:
        writer.writerow([
            record.consumption_date.strftime('%Y-%m-%d'),
            record.product.name,
            record.product.sku,
            record.quantity_used,
            record.unit_of_measure,
            record.issued_to,
            record.reference_doc_no or '',
            record.notes or '',
            record.user.username if record.user else '',
            record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-disposition": f"attachment; filename=consumption_records_{date.today().strftime('%Y%m%d')}.csv"}
    )

# ============ CONSUMPTION API ENDPOINTS ============

@app.route('/api/inventory/consumption')
@login_required
def api_get_all_consumption():
    """Get all consumption records as JSON"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Get consumption records
        consumption_records = get_all_consumption_records()

        records = []
        if hasattr(consumption_records, 'items'):
            # If paginated, get items
            items = consumption_records.items
        else:
            # If not paginated, use directly
            items = consumption_records

        for record in items:
            records.append({
                'id': record.id,
                'product_id': record.product_id,
                'product_name': record.product.name if record.product else 'Unknown',
                'product_sku': record.product.sku if record.product else 'N/A',
                'consumption_date': record.consumption_date.strftime('%Y-%m-%d') if record.consumption_date else 'N/A',
                'quantity_used': float(record.quantity_used or 0),
                'unit_of_measure': record.unit_of_measure or 'pcs',
                'issued_to': record.issued_to or '',
                'reference_doc_no': record.reference_doc_no or '',
                'notes': record.notes or '',
                'created_by': record.user.username if record.user else 'System',
                'created_at': record.created_at.isoformat() if record.created_at else None
            })

        return jsonify({'records': records})

    except Exception as e:
        return jsonify({'error': f'Error loading consumption records: {str(e)}'}), 500

@app.route('/api/inventory/consumption/<int:consumption_id>')
@login_required
def api_get_consumption(consumption_id):
    """Get consumption record as JSON"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    consumption = get_consumption_by_id(consumption_id)
    if consumption:
        return jsonify({
            'id': consumption.id,
            'product_id': consumption.product_id,
            'product_name': consumption.product.name if consumption.product else 'Unknown',
            'product_sku': consumption.product.sku if consumption.product else 'N/A',
            'consumption_date': consumption.consumption_date.strftime('%Y-%m-%d') if consumption.consumption_date else 'N/A',
            'quantity_used': float(consumption.quantity_used or 0),
            'unit_of_measure': consumption.unit_of_measure or 'pcs',
            'issued_to': consumption.issued_to or '',
            'reference_doc_no': consumption.reference_doc_no or '',
            'notes': consumption.notes or '',
            'created_by': consumption.user.username if consumption.user else 'System',
            'created_at': consumption.created_at.isoformat() if consumption.created_at else None
        })
    return jsonify({'error': 'Consumption record not found'}), 404

@app.route('/api/inventory/products/for-consumption')
@login_required
def api_products_for_consumption():
    """Get products available for consumption"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    products = get_all_products()
    return jsonify([{
        'id': product.id,
        'name': product.name,
        'sku': product.sku,
        'current_stock': float(product.current_stock),
        'unit_of_measure': product.unit_of_measure
    } for product in products if product.current_stock > 0])

@app.route('/api/inventory/products/master')
@login_required
def api_products_master():
    """Get all products for Product Master table"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    products = get_all_products()
    return jsonify([{
        'id': product.id,
        'sku': product.sku,
        'name': product.name,
        'category': product.category.name if product.category else '',
        'category_color': product.category.color_code if product.category else '#6c757d',
        'unit_of_measure': product.unit_of_measure,
        'current_stock': float(product.current_stock),
        'reorder_level': float(product.reorder_point),
        'status': product.stock_status,
        'location': product.location or '',
        'cost_price': float(product.cost_price or 0)  # Added for inventory adjustments
    } for product in products])

# ============ LOCATION MANAGEMENT API ENDPOINTS ============

@app.route('/api/inventory/locations/<string:location_id>')
@login_required
def api_get_location(location_id):
    """Get specific location data"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        from .models import InventoryLocation
        location = InventoryLocation.query.get(location_id)
        if not location:
            return jsonify({'error': 'Location not found'}), 404

        # Count products in this location
        products_count = len([p for p in InventoryProduct.query.filter_by(location=location.name).all() if (p.current_stock or 0) > 0])

        return jsonify({
            'id': location.id,
            'name': location.name,
            'type': location.type,
            'address': location.address or '',
            'contact_person': location.contact_person or '',
            'phone': location.phone or '',
            'status': location.status,
            'products_count': products_count,
            'total_stock_value': location.total_stock_value,
            'created_at': location.created_at.isoformat() if location.created_at else None
        })

    except Exception as e:
        return jsonify({'error': f'Error loading location: {str(e)}'}), 500

@app.route('/api/inventory/locations')
@login_required
def api_get_locations():
    """Get all inventory locations"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # For now, return default locations from localStorage format
        # This can be enhanced later with a proper database table
        default_locations = [
            {
                'id': 'loc1',
                'name': 'Main Store',
                'type': 'branch',
                'status': 'active',
                'address': 'Main location',
                'contact_person': '',
                'phone': '',
                'created_at': '2024-01-01T00:00:00'
            },
            {
                'id': 'loc2',
                'name': 'Storage Room',
                'type': 'warehouse',
                'status': 'active',
                'address': 'Back storage area',
                'contact_person': '',
                'phone': '',
                'created_at': '2024-01-01T00:00:00'
            },
            {
                'id': 'loc3',
                'name': 'Treatment Room A',
                'type': 'room',
                'status': 'active',
                'address': 'First treatment room',
                'contact_person': '',
                'phone': '',
                'created_at': '2024-01-01T00:00:00'
            }
        ]

        return jsonify({'locations': default_locations})
    except Exception as e:
        return jsonify({'error': f'Error loading locations: {str(e)}'}), 500

@app.route('/api/inventory/locations', methods=['POST'])
@login_required
def api_add_location():
    """Add new inventory location"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        from .models import InventoryLocation
        import uuid

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Generate unique ID if not provided
        location_id = data.get('id') or f"loc-{str(uuid.uuid4())[:8]}"

        # Validation
        if not data.get('name', '').strip():
            return jsonify({'error': 'Location name is required'}), 400

        if not data.get('type', '').strip():
            return jsonify({'error': 'Location type is required'}), 400

        # Check for duplicate name
        existing = InventoryLocation.query.filter_by(name=data['name'].strip()).first()
        if existing:
            return jsonify({'error': 'Location with this name already exists'}), 400

        # Check for duplicate ID
        existing_id = InventoryLocation.query.filter_by(id=location_id).first()
        if existing_id:
            location_id = f"loc-{str(uuid.uuid4())[:8]}"  # Generate new ID if collision

        location = InventoryLocation(
            id=location_id,
            name=data['name'].strip(),
            type=data['type'].strip(),
            address=data.get('address', '').strip() or None,
            contact_person=data.get('contact_person', '').strip() or None,
            phone=data.get('phone', '').strip() or None,
            status=data.get('status', 'active')
        )

        db.session.add(location)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Location "{location.name}" added successfully!',
            'location': {
                'id': location.id,
                'name': location.name,
                'type': location.type
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error adding location: {str(e)}'}), 500

@app.route('/api/inventory/locations/<string:location_id>', methods=['PUT'])
@login_required
def api_update_location(location_id):
    """Update inventory location"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        from .models import InventoryLocation

        location = InventoryLocation.query.get(location_id)
        if not location:
            return jsonify({'error': 'Location not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validation
        if not data.get('name', '').strip():
            return jsonify({'error': 'Location name is required'}), 400

        # Check for duplicate name (excluding current location)
        existing = InventoryLocation.query.filter(
            InventoryLocation.name == data['name'].strip(),
            InventoryLocation.id != location_id
        ).first()
        if existing:
            return jsonify({'error': 'Location with this name already exists'}), 400

        # Update location
        location.name = data['name'].strip()
        location.type = data.get('type', location.type).strip()
        location.address = data.get('address', '').strip()
        location.contact_person = data.get('contact_person', '').strip()
        location.phone = data.get('phone', '').strip()
        location.status = data.get('status', location.status)
        location.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Location "{location.name}" updated successfully!'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error updating location: {str(e)}'}), 500

@app.route('/api/inventory/locations/<string:location_id>', methods=['DELETE'])
@login_required
def api_delete_location(location_id):
    """Delete inventory location"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        from .models import InventoryLocation

        location = InventoryLocation.query.get(location_id)
        if not location:
            return jsonify({'error': 'Location not found'}), 404

        # Check if location has stock
        products = InventoryProduct.query.all()
        has_stock = False
        for product in products:
            if product.location_stock and location_id in product.location_stock:
                if product.location_stock[location_id] > 0:
                    has_stock = True
                    break

        if has_stock:
            return jsonify({
                'error': 'Cannot delete location that still has stock. Please transfer all items first.'
            }), 400

        location_name = location.name
        db.session.delete(location)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Location "{location_name}" deleted successfully!'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting location: {str(e)}'}), 500

# ============ CONSUMPTION API ENDPOINTS ============