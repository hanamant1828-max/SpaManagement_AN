"""
Inventory views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from app import app, db
from forms import InventoryForm
import pandas as pd
import io
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from .inventory_queries import (
    get_all_inventory, get_inventory_by_id, get_low_stock_items, 
    get_expiring_items, get_inventory_categories, search_inventory, 
    create_inventory, update_inventory, delete_inventory, update_stock,
    get_items_by_status, get_stock_movements, get_consumption_by_service,
    get_wastage_report, get_supplier_performance, get_inventory_valuation,
    convert_units, auto_deduct_service_inventory, create_stock_adjustment,
    generate_reorder_suggestions
)
from models import Inventory, InventoryMaster, InventoryTransaction, Category

@app.route('/inventory')
@login_required
def inventory():
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    search_query = request.args.get('search', '')
    filter_type = request.args.get('filter', 'all')

    if search_query:
        inventory_list = search_inventory(search_query)
    elif filter_type == 'low_stock':
        inventory_list = get_low_stock_items()
    elif filter_type == 'expiring':
        inventory_list = get_expiring_items()
    else:
        inventory_list = get_all_inventory()

    categories = get_inventory_categories()
    form = InventoryForm()
    form.category_id.choices = [(c.id, c.display_name) for c in categories]
    
    # Get master items for the Inventory Master tab
    try:
        master_items = InventoryMaster.query.filter_by(is_active=True).all()
    except:
        # Fallback: if InventoryMaster table doesn't exist, use regular inventory
        master_items = inventory_list

    return render_template('inventory.html', 
                         items=inventory_list,  # Changed from inventory to items
                         form=form,
                         categories=categories,
                         search_query=search_query,
                         filter_type=filter_type,
                         master_items=master_items)

# NEW: Inventory Master Routes (Structured Approach)
@app.route('/inventory/master')
@login_required
def inventory_master():
    """View inventory master catalog - products only, no stock levels"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    master_items = InventoryMaster.query.filter_by(is_active=True).all()
    categories = Category.query.all()
    
    # Calculate stats
    low_stock_count = sum(1 for item in master_items if item.is_low_stock)
    active_items = len(master_items)
    
    return render_template('inventory_master.html',
                         master_items=master_items,
                         categories=categories,
                         low_stock_count=low_stock_count,
                         active_items=active_items)

@app.route('/inventory/master/add', methods=['POST'])
@login_required
def inventory_master_add():
    """Add new product to master catalog"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # Create master item
        master_item = InventoryMaster(
            name=request.form.get('name'),
            sku=request.form.get('sku'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            base_unit=request.form.get('base_unit'),
            min_stock_level=float(request.form.get('min_stock_level', 5)),
            max_stock_level=float(request.form.get('max_stock_level', 100)),
            reorder_point=float(request.form.get('reorder_point', 10))
        )
        
        db.session.add(master_item)
        db.session.commit()
        
        flash(f'Product "{master_item.name}" added to catalog successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding product: {str(e)}', 'error')
    
    return redirect(url_for('inventory_master'))

@app.route('/inventory/transactions')
@login_required
def inventory_transactions():
    """View all inventory transactions"""
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    transactions = InventoryTransaction.query.order_by(InventoryTransaction.created_at.desc()).limit(100).all()
    
    return render_template('inventory_transactions.html', transactions=transactions)

@app.route('/inventory/bulk-import', methods=['GET', 'POST'])
@login_required
def bulk_import_inventory():
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'GET':
        return render_template('inventory_import.html')
    
    # Handle file upload
    if 'inventory_file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('bulk_import_inventory'))
    
    file = request.files['inventory_file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('bulk_import_inventory'))
    
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        flash('Please upload an Excel file (.xlsx or .xls)', 'error')
        return redirect(url_for('bulk_import_inventory'))
    
    try:
        # Read the Excel file
        df = pd.read_excel(file)
        
        # Validate required columns
        required_columns = ['name', 'sku', 'category', 'current_stock', 'cost_price']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            flash(f'Missing required columns: {", ".join(missing_columns)}', 'error')
            return redirect(url_for('bulk_import_inventory'))
        
        success_count = 0
        error_count = 0
        errors = []
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Check if SKU already exists
                existing_item = Inventory.query.filter_by(sku=str(row['sku'])).first()
                if existing_item:
                    errors.append(f"Row {index + 2}: SKU '{row['sku']}' already exists")
                    error_count += 1
                    continue
                
                # Get or create category
                category = Category.query.filter_by(name=str(row['category']), category_type='inventory').first()
                if not category:
                    category = Category(
                        name=str(row['category']),
                        display_name=str(row['category']).title(),
                        category_type='inventory',
                        is_active=True
                    )
                    db.session.add(category)
                    db.session.flush()  # Get the ID
                
                # Create inventory item
                inventory_data = {
                    'name': str(row['name']).strip(),
                    'sku': str(row['sku']).strip(),
                    'category_id': category.id,
                    'category': str(row['category']),
                    'current_stock': float(row['current_stock']) if pd.notna(row['current_stock']) else 0.0,
                    'cost_price': float(row['cost_price']) if pd.notna(row['cost_price']) else 0.0,
                    'description': str(row.get('description', '')) if pd.notna(row.get('description')) else '',
                    'selling_price': float(row.get('selling_price', 0)) if pd.notna(row.get('selling_price')) else 0.0,
                    'min_stock_level': float(row.get('min_stock_level', 5)) if pd.notna(row.get('min_stock_level')) else 5.0,
                    'max_stock_level': float(row.get('max_stock_level', 100)) if pd.notna(row.get('max_stock_level')) else 100.0,
                    'reorder_point': float(row.get('reorder_point', 10)) if pd.notna(row.get('reorder_point')) else 10.0,
                    'reorder_quantity': float(row.get('reorder_quantity', 50)) if pd.notna(row.get('reorder_quantity')) else 50.0,
                    'base_unit': str(row.get('base_unit', 'pcs')).strip() if pd.notna(row.get('base_unit')) else 'pcs',
                    'selling_unit': str(row.get('selling_unit', 'pcs')).strip() if pd.notna(row.get('selling_unit')) else 'pcs',
                    'conversion_factor': float(row.get('conversion_factor', 1.0)) if pd.notna(row.get('conversion_factor')) else 1.0,
                    'item_type': str(row.get('item_type', 'consumable')).strip() if pd.notna(row.get('item_type')) else 'consumable',
                    'supplier_name': str(row.get('supplier_name', '')).strip() if pd.notna(row.get('supplier_name')) else '',
                    'supplier_contact': str(row.get('supplier_contact', '')).strip() if pd.notna(row.get('supplier_contact')) else '',
                    'storage_location': str(row.get('storage_location', '')).strip() if pd.notna(row.get('storage_location')) else '',
                    'storage_temperature': str(row.get('storage_temperature', 'room_temp')).strip() if pd.notna(row.get('storage_temperature')) else 'room_temp',
                    'has_expiry': bool(row.get('has_expiry', False)) if pd.notna(row.get('has_expiry')) else False,
                    'shelf_life_days': int(row.get('shelf_life_days', 0)) if pd.notna(row.get('shelf_life_days')) else None,
                    'enable_low_stock_alert': bool(row.get('enable_low_stock_alert', True)) if pd.notna(row.get('enable_low_stock_alert')) else True,
                    'enable_expiry_alert': bool(row.get('enable_expiry_alert', True)) if pd.notna(row.get('enable_expiry_alert')) else True,
                    'is_active': True,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
                
                # Handle optional date fields
                if pd.notna(row.get('expiry_date')):
                    try:
                        if isinstance(row['expiry_date'], str):
                            inventory_data['expiry_date'] = datetime.strptime(row['expiry_date'], '%Y-%m-%d').date()
                        else:
                            inventory_data['expiry_date'] = row['expiry_date'].date()
                    except:
                        pass
                
                # Calculate markup if selling price is provided
                if inventory_data['cost_price'] > 0 and inventory_data['selling_price'] > 0:
                    inventory_data['markup_percentage'] = ((inventory_data['selling_price'] - inventory_data['cost_price']) / inventory_data['cost_price']) * 100
                
                # Create the inventory item
                new_item = Inventory(**inventory_data)
                db.session.add(new_item)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
                error_count += 1
                continue
        
        # Commit changes
        db.session.commit()
        
        # Show results
        if success_count > 0:
            flash(f'Successfully imported {success_count} inventory items', 'success')
        
        if error_count > 0:
            flash(f'{error_count} items failed to import. Check errors below.', 'warning')
            for error in errors[:10]:  # Show only first 10 errors
                flash(error, 'error')
        
        return redirect(url_for('inventory'))
        
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('bulk_import_inventory'))

@app.route('/inventory/download-template')
@login_required
def download_inventory_template():
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Create sample Excel template
    sample_data = {
        'name': ['Face Cream Premium', 'Hair Shampoo Organic', 'Massage Oil Lavender'],
        'sku': ['FC001', 'HS002', 'MO003'],
        'description': ['Premium anti-aging face cream', 'Organic herbal hair shampoo', 'Relaxing lavender massage oil'],
        'category': ['skincare', 'haircare', 'massage'],
        'current_stock': [25, 15, 30],
        'min_stock_level': [5, 10, 8],
        'max_stock_level': [100, 80, 60],
        'reorder_point': [10, 15, 12],
        'reorder_quantity': [50, 40, 30],
        'base_unit': ['pcs', 'bottles', 'bottles'],
        'selling_unit': ['pcs', 'bottles', 'bottles'],
        'conversion_factor': [1.0, 1.0, 1.0],
        'cost_price': [150.0, 250.0, 180.0],
        'selling_price': [200.0, 350.0, 250.0],
        'item_type': ['consumable', 'consumable', 'consumable'],
        'supplier_name': ['Beauty Supplies Co', 'Organic Products Ltd', 'Essential Oils Inc'],
        'supplier_contact': ['+91-9876543210', '+91-9876543211', '+91-9876543212'],
        'storage_location': ['Shelf A1', 'Shelf B2', 'Cabinet C1'],
        'storage_temperature': ['room_temp', 'room_temp', 'cool'],
        'has_expiry': [True, True, False],
        'shelf_life_days': [365, 730, None],
        'expiry_date': ['2025-12-31', '2026-06-30', None],
        'enable_low_stock_alert': [True, True, True],
        'enable_expiry_alert': [True, True, False]
    }
    
    df = pd.DataFrame(sample_data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write the data
        df.to_excel(writer, sheet_name='Inventory Template', index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Inventory Template']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Add instructions sheet
        instructions_data = {
            'Field': ['name', 'sku', 'description', 'category', 'current_stock', 'min_stock_level', 'max_stock_level', 
                     'reorder_point', 'reorder_quantity', 'base_unit', 'selling_unit', 'conversion_factor',
                     'cost_price', 'selling_price', 'item_type', 'supplier_name', 'supplier_contact',
                     'storage_location', 'storage_temperature', 'has_expiry', 'shelf_life_days', 'expiry_date',
                     'enable_low_stock_alert', 'enable_expiry_alert'],
            'Required': ['Yes', 'Yes', 'No', 'Yes', 'Yes', 'No', 'No', 'No', 'No', 'No', 'No', 'No',
                        'Yes', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No'],
            'Description': [
                'Product name (e.g., Face Cream Premium)',
                'Unique product code (e.g., FC001)',
                'Product description',
                'Category name (e.g., skincare, haircare)',
                'Current stock quantity (e.g., 25)',
                'Minimum stock level for alerts (default: 5)',
                'Maximum stock level (default: 100)',
                'Stock level to trigger reorder (default: 10)',
                'Quantity to reorder (default: 50)',
                'Base unit (pcs, bottles, ml, kg, etc.)',
                'Selling unit (same as base_unit usually)',
                'Conversion factor between units (default: 1.0)',
                'Cost price per unit (e.g., 150.0)',
                'Selling price per unit (e.g., 200.0)',
                'Type: consumable, sellable, or both',
                'Supplier company name',
                'Supplier contact information',
                'Storage location (e.g., Shelf A1)',
                'Storage temperature: room_temp, cool, refrigerated, frozen',
                'True/False - does item expire?',
                'Number of days the item stays fresh',
                'Expiry date in YYYY-MM-DD format',
                'True/False - enable low stock alerts',
                'True/False - enable expiry alerts'
            ]
        }
        
        instructions_df = pd.DataFrame(instructions_data)
        instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
        
        # Auto-adjust instruction sheet columns
        instructions_ws = writer.sheets['Instructions']
        for column in instructions_ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 80)
            instructions_ws.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f'inventory_import_template_{datetime.now().strftime("%Y%m%d")}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/inventory/create', methods=['POST'])
@app.route('/inventory/add', methods=['POST'])
@app.route('/add_inventory', methods=['POST'])
@login_required
def create_inventory_route():
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    form = InventoryForm()
    categories = get_inventory_categories()
    form.category_id.choices = [(c.id, c.display_name) for c in categories]

    if form.validate_on_submit():
        try:
            inventory_data = {
                'name': form.name.data.strip() if form.name.data else '',
                'description': form.description.data.strip() if form.description.data else '',
                'category_id': form.category_id.data if form.category_id.data else None,
                'category': 'general',  # Fallback category
                'current_stock': float(form.current_stock.data or 0),
                'min_stock_level': float(form.min_stock_level.data or 5),
                'cost_price': float(form.cost_price.data or 0),
                'selling_price': float(form.selling_price.data or 0),
                'expiry_date': form.expiry_date.data,
                'supplier_name': form.supplier.data.strip() if form.supplier.data else '',
                'is_active': True
            }

            # Validate required fields
            if not inventory_data['name']:
                flash('Item name is required', 'danger')
                return redirect(url_for('inventory'))

            if inventory_data['current_stock'] < 0:
                flash('Current stock cannot be negative', 'danger')
                return redirect(url_for('inventory'))

            inventory = create_inventory(inventory_data)
            if inventory:
                flash(f'Inventory item "{inventory.name}" created successfully!', 'success')
            else:
                flash('Error creating inventory item. Please try again.', 'danger')

        except ValueError as e:
            flash(f'Invalid input: {str(e)}', 'danger')
        except Exception as e:
            flash(f'Error creating inventory item: {str(e)}', 'danger')
            print(f"Inventory creation error: {e}")
    else:
        # Show specific validation errors
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")

        if error_messages:
            flash(f'Validation errors: {"; ".join(error_messages)}', 'danger')
        else:
            flash('Error creating inventory item. Please check your input.', 'danger')

    return redirect(url_for('inventory'))

@app.route('/inventory/update/<int:id>', methods=['POST'])
@login_required
def update_inventory_route(id):
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    inventory_item = get_inventory_by_id(id)
    if not inventory_item:
        flash('Inventory item not found', 'danger')
        return redirect(url_for('inventory'))

    form = InventoryForm()
    categories = get_inventory_categories()
    form.category_id.choices = [(c.id, c.display_name) for c in categories]

    if form.validate_on_submit():
        inventory_data = {
            'name': form.name.data,
            'description': form.description.data or '',
            'category_id': form.category_id.data,
            'current_stock': form.current_stock.data,
            'min_stock_level': form.min_stock_level.data,
            'cost_price': form.cost_price.data,
            'selling_price': form.selling_price.data,
            'expiry_date': form.expiry_date.data,
            'supplier': form.supplier.data or ''
        }

        update_inventory(id, inventory_data)
        flash('Inventory item updated successfully!', 'success')
    else:
        flash('Error updating inventory item. Please check your input.', 'danger')

    return redirect(url_for('inventory'))

@app.route('/inventory/delete/<int:id>', methods=['POST'])
@login_required
def delete_inventory_route(id):
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    if delete_inventory(id):
        flash('Inventory item deleted successfully!', 'success')
    else:
        flash('Error deleting inventory item', 'danger')

    return redirect(url_for('inventory'))

@app.route('/inventory/stock-update/<int:id>', methods=['POST'])
@login_required
def update_stock_route(id):
    if not current_user.can_access('inventory'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    quantity_change = request.form.get('quantity_change', type=float)
    movement_type = request.form.get('movement_type', 'adjustment')
    reason = request.form.get('reason', 'Manual stock update')

    if quantity_change is not None:
        inventory_item = update_stock(
            id, quantity_change, movement_type, 
            reason=reason, created_by=current_user.id
        )
        if inventory_item:
            flash(f'Stock updated. New quantity: {inventory_item.current_stock:.2f} {inventory_item.base_unit}', 'success')
        else:
            flash('Error updating stock', 'danger')
    else:
        flash('Invalid quantity change', 'danger')

    return redirect(url_for('inventory'))

# API Endpoints for Comprehensive Inventory Management

@app.route('/api/inventory/status/<status>')
@login_required
def api_inventory_by_status(status):
    """API: Get inventory items by status for consumption tracking dropdowns"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        print(f"Loading inventory items with status: {status}")
        
        if status == 'all':
            items = get_all_inventory()
        else:
            items = get_items_by_status(status)
            
        print(f"Found {len(items)} inventory items")
        
        items_data = []

        for item in items:
            try:
                # Get basic attributes safely
                item_data = {
                    'id': item.id,
                    'name': item.name or 'Unnamed Item',
                    'current_stock': float(item.current_stock or 0),
                    'base_unit': getattr(item, 'base_unit', 'pcs') or 'pcs',
                    'selling_unit': getattr(item, 'selling_unit', 'pcs') or 'pcs',
                    'category': getattr(item, 'category', 'general') or 'general',
                    'item_type': getattr(item, 'item_type', 'consumable') or 'consumable',
                    'is_service_item': getattr(item, 'is_service_item', True),
                    'tracking_type': getattr(item, 'tracking_type', 'piece_wise') or 'piece_wise',
                    'cost_price': float(getattr(item, 'cost_price', 0) or 0),
                    'selling_price': float(getattr(item, 'selling_price', 0) or 0),
                    'min_stock_level': float(getattr(item, 'min_stock_level', 0) or 0),
                    'requires_open_close': getattr(item, 'requires_open_close', False),
                    'supports_batches': getattr(item, 'supports_batches', False)
                }
                
                items_data.append(item_data)
                print(f"Added item: {item_data['name']} (Stock: {item_data['current_stock']})")
                
            except Exception as e:
                print(f"Error processing item {item.id}: {e}")
                continue

        print(f"Successfully processed {len(items_data)} items")
        
        return jsonify({
            'status': 'success',
            'items': items_data,
            'total': len(items_data),
            'message': f'Loaded {len(items_data)} inventory items'
        })
        
    except Exception as e:
        print(f"Error in inventory status API: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e),
            'items': [],
            'total': 0
        }), 500

@app.route('/api/inventory/valuation')
@login_required
def api_inventory_valuation():
    """API: Get total inventory valuation"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    valuation = get_inventory_valuation()

    return jsonify({
        'status': 'success',
        'total_cost_value': float(valuation.total_cost_value or 0),
        'total_selling_value': float(valuation.total_selling_value or 0),
        'potential_profit': float((valuation.total_selling_value or 0) - (valuation.total_cost_value or 0)),
        'total_items': valuation.total_items
    })

@app.route('/api/inventory/reorder-suggestions')
@login_required
def api_reorder_suggestions():
    """API: Get automatic reorder suggestions"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    suggestions = generate_reorder_suggestions()

    return jsonify({
        'status': 'success',
        'suggestions': suggestions,
        'total_estimated_cost': sum(s['estimated_cost'] for s in suggestions)
    })

@app.route('/api/inventory/alerts')
@login_required
def api_inventory_alerts():
    """API: Get real-time inventory alerts"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    alerts = []

    # Low stock alerts
    low_stock_items = get_items_by_status('low_stock')
    for item in low_stock_items:
        alerts.append({
            'type': 'low_stock',
            'severity': 'warning',
            'item_id': item.id,
            'item_name': item.name,
            'current_stock': item.current_stock,
            'min_stock': item.min_stock_level,
            'message': f'{item.name} is running low ({item.current_stock} {item.base_unit} remaining)'
        })

    return jsonify({
        'status': 'success',
        'alerts': alerts,
        'alert_counts': {
            'low_stock': len(low_stock_items)
        }
    })

@app.route('/api/appointment/<int:appointment_id>/auto-deduct', methods=['POST'])
@login_required
def api_auto_deduct_inventory(appointment_id):
    """API: Auto-deduct inventory for completed appointment"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    success = auto_deduct_service_inventory(appointment_id)

    if success:
        return jsonify({
            'status': 'success',
            'message': 'Inventory deducted successfully',
            'appointment_id': appointment_id
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to deduct inventory or already processed',
            'appointment_id': appointment_id
        })

# NEW: Advanced Consumption Tracking API Endpoints

@app.route('/api/inventory/<int:inventory_id>/open', methods=['POST'])
@login_required
def api_open_inventory_item(inventory_id):
    """API: Open/Issue an inventory item (Container/Lifecycle tracking)"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    from modules.inventory.inventory_queries import open_inventory_item

    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        quantity = float(data.get('quantity', 1.0))
        reason = data.get('reason', 'Opened for use')
        batch_number = data.get('batch_number', '')

        if quantity <= 0:
            return jsonify({'status': 'error', 'message': 'Quantity must be greater than 0'}), 400

        result = open_inventory_item(inventory_id, quantity, reason, batch_number, current_user.id)

        if result:
            return jsonify({
                'status': 'success',
                'message': 'Item opened successfully',
                'item_code': result.item_code,
                'quantity': result.quantity
            })
        else:
            return jsonify({'status': 'error', 'message': 'Failed to open item. Check if sufficient stock is available.'}), 400

    except ValueError as e:
        return jsonify({'status': 'error', 'message': 'Invalid quantity value'}), 400
    except Exception as e:
        print(f"Error in open inventory API: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route('/api/inventory-item/<int:item_id>/consume', methods=['POST'])
@login_required
def api_consume_inventory_item(item_id):
    """API: Mark inventory item as fully consumed"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    from modules.inventory.inventory_queries import consume_inventory_item

    data = request.get_json()
    reason = data.get('reason', 'Fully consumed')

    result = consume_inventory_item(item_id, reason, current_user.id)

    if result:
        return jsonify({
            'status': 'success',
            'message': 'Item marked as consumed',
            'duration_hours': result.duration_hours if result else None
        })
    else:
        return jsonify({'status': 'error', 'message': 'Failed to consume item'}), 400

@app.route('/api/inventory/<int:inventory_id>/deduct', methods=['POST'])
@login_required
def api_deduct_inventory(inventory_id):
    """API: Deduct specific quantity (Piece-wise tracking)"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    from modules.inventory.inventory_queries import deduct_inventory_quantity

    data = request.get_json()
    quantity = float(data.get('quantity'))
    unit = data.get('unit', 'pcs')
    reason = data.get('reason', 'Service consumption')
    reference_id = data.get('reference_id')
    reference_type = data.get('reference_type', 'manual')

    result = deduct_inventory_quantity(
        inventory_id, quantity, unit, reason, 
        reference_id, reference_type, current_user.id
    )

    if result:
        return jsonify({
            'status': 'success',
            'message': 'Quantity deducted successfully',
            'remaining_stock': result['remaining_stock'],
            'deducted_quantity': quantity
        })
    else:
        return jsonify({'status': 'error', 'message': 'Failed to deduct quantity'}), 400

@app.route('/api/inventory/<int:inventory_id>/adjust', methods=['POST'])
@login_required
def api_adjust_inventory(inventory_id):
    """API: Manual stock adjustment"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    from modules.inventory.inventory_queries import create_manual_adjustment

    data = request.get_json()
    new_quantity = float(data.get('new_quantity'))
    adjustment_type = data.get('adjustment_type', 'manual_adjustment')
    reason = data.get('reason', 'Manual adjustment')

    result = create_manual_adjustment(
        inventory_id, new_quantity, adjustment_type, reason, current_user.id
    )

    if result:
        return jsonify({
            'status': 'success',
            'message': 'Stock adjusted successfully',
            'old_quantity': result['old_quantity'],
            'new_quantity': result['new_quantity'],
            'adjustment': result['adjustment']
        })
    else:
        return jsonify({'status': 'error', 'message': 'Failed to adjust stock'}), 400

@app.route('/api/inventory/consumption-entries')
@login_required
def api_consumption_entries():
    """API: Get consumption entries with filtering"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        from models import StockMovement, Inventory, User
        from datetime import datetime, timedelta

        # Get query parameters
        inventory_id = request.args.get('inventory_id', type=int)
        entry_type = request.args.get('entry_type')
        staff_id = request.args.get('staff_id', type=int)
        days = request.args.get('days', 30, type=int)

        # Build query for stock movements (consumption tracking)
        query = db.session.query(StockMovement).join(Inventory, StockMovement.inventory_id == Inventory.id)

        if inventory_id:
            query = query.filter(StockMovement.inventory_id == inventory_id)

        if entry_type:
            query = query.filter(StockMovement.movement_type == entry_type)

        if staff_id:
            query = query.filter(StockMovement.created_by == staff_id)

        # Filter by date range
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(StockMovement.created_at >= start_date)

        movements = query.order_by(StockMovement.created_at.desc()).limit(50).all()

        entries_data = []
        for movement in movements:
            try:
                entry_data = {
                    'id': movement.id,
                    'inventory_name': movement.inventory.name if movement.inventory else 'Unknown',
                    'entry_type': movement.movement_type,
                    'quantity': abs(float(movement.quantity)),
                    'unit': movement.unit or 'units',
                    'reason': movement.reason or 'No reason provided',
                    'staff_name': f"{movement.created_by_user.first_name} {movement.created_by_user.last_name}" if movement.created_by_user else 'System',
                    'created_at': movement.created_at.isoformat() if movement.created_at else '',
                    'cost_impact': 0.0  # Calculate if needed
                }
                entries_data.append(entry_data)
            except Exception as e:
                print(f"Error processing movement {movement.id}: {e}")
                continue

        return jsonify({
            'status': 'success',
            'entries': entries_data,
            'total_entries': len(entries_data)
        })

    except Exception as e:
        print(f"Error in consumption entries API: {e}")
        return jsonify({
            'status': 'success',
            'entries': [],
            'total_entries': 0
        })

@app.route('/api/inventory/usage-duration')
@login_required
def api_usage_duration():
    """API: Get usage duration reports"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    from modules.inventory.inventory_queries import get_usage_duration_report

    inventory_id = request.args.get('inventory_id', type=int)
    days = request.args.get('days', 30, type=int)

    report = get_usage_duration_report(inventory_id, days)

    return jsonify({
        'status': 'success',
        'report': report
    })

@app.route('/api/inventory/staff-usage')
@login_required
def api_staff_usage():
    """API: Get staff usage reports"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    from modules.inventory.inventory_queries import get_staff_usage_report

    staff_id = request.args.get('staff_id', type=int)
    days = request.args.get('days', 30, type=int)

    report = get_staff_usage_report(staff_id, days)

    return jsonify({
        'status': 'success',
        'report': report
    })

@app.route('/api/inventory/open-items')
@login_required
def api_open_items():
    """API: Get currently open inventory items"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        from models import InventoryItem

        open_items = InventoryItem.query.filter_by(status='issued').all()

        items_data = []
        for item in open_items:
            items_data.append({
                'id': item.id,
                'item_code': item.item_code,
                'inventory_name': item.inventory.name,
                'remaining_quantity': float(item.remaining_quantity),
                'unit': item.inventory.base_unit or 'units',
                'issued_at': item.issued_at.isoformat() if item.issued_at else None
            })

        return jsonify({
            'status': 'success',
            'items': items_data
        })

    except Exception as e:
        print(f"Error in open items API: {e}")
        return jsonify({
            'status': 'success',
            'items': []
        })

@app.route('/api/inventory/activity-summary')
@login_required
def api_activity_summary():
    """API: Get consumption activity summary for dashboard cards"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        from models import ConsumptionEntry, InventoryItem
        from datetime import datetime, timedelta
        from app import db

        # Today's activity
        today = datetime.utcnow().date()
        today_count = ConsumptionEntry.query.filter(
            db.func.date(ConsumptionEntry.created_at) == today
        ).count()

        # Currently open items
        open_count = InventoryItem.query.filter_by(status='issued').count()

        # Weekly usage
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_count = ConsumptionEntry.query.filter(
            ConsumptionEntry.created_at >= week_ago,
            ConsumptionEntry.entry_type == 'consume'
        ).count()

        return jsonify({
            'status': 'success',
            'today_count': today_count,
            'open_items_count': open_count,
            'weekly_count': weekly_count
        })

    except Exception as e:
        print(f"Error in activity summary API: {e}")
        return jsonify({
            'status': 'success',
            'today_count': 0,
            'open_items_count': 0,
            'weekly_count': 0
        })

@app.route('/api/inventory/consumption-analytics')
@login_required
def api_consumption_analytics():
    """API: Get detailed consumption analytics"""
    if not current_user.can_access('inventory'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        from models import ConsumptionEntry, Inventory, UsageDuration
        from datetime import datetime, timedelta
        from app import db

        # This month's data
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Total opened and consumed this month
        total_opened = ConsumptionEntry.query.filter(
            ConsumptionEntry.created_at >= month_start,
            ConsumptionEntry.entry_type == 'open'
        ).count()

        total_consumed = ConsumptionEntry.query.filter(
            ConsumptionEntry.created_at >= month_start,
            ConsumptionEntry.entry_type == 'consume'
        ).count()

        # Average duration (if usage duration tracking exists)
        avg_duration = 0
        try:
            duration_result = db.session.query(db.func.avg(UsageDuration.duration_hours)).filter(
                UsageDuration.started_at >= month_start,
                UsageDuration.duration_hours.isnot(None)
            ).scalar()
            avg_duration = float(duration_result or 0)
        except:
            avg_duration = 0

        # Top consumed items this month
        top_items_query = db.session.query(
            Inventory.name.label('item_name'),
            db.func.count(ConsumptionEntry.id).label('usage_count'),
            db.func.sum(ConsumptionEntry.quantity).label('total_quantity'),
            Inventory.base_unit.label('unit'),
            db.func.sum(ConsumptionEntry.cost_impact).label('cost_impact')
        ).join(
            ConsumptionEntry, Inventory.id == ConsumptionEntry.inventory_id
        ).filter(
            ConsumptionEntry.created_at >= month_start
        ).group_by(
            Inventory.id, Inventory.name, Inventory.base_unit
        ).order_by(
            db.func.count(ConsumptionEntry.id).desc()
        ).limit(10).all()

        top_items = []
        for item in top_items_query:
            top_items.append({
                'item_name': item.item_name,
                'usage_count': item.usage_count,
                'total_quantity': float(item.total_quantity or 0),
                'unit': item.unit or 'units',
                'cost_impact': float(item.cost_impact or 0)
            })

        return jsonify({
            'status': 'success',
            'total_opened': total_opened,
            'total_consumed': total_consumed,
            'avg_duration': avg_duration,
            'top_items': top_items
        })

    except Exception as e:
        print(f"Error in consumption analytics API: {e}")
        return jsonify({
            'status': 'success',
            'total_opened': 0,
            'total_consumed': 0,
            'avg_duration': 0,
            'top_items': []
        })