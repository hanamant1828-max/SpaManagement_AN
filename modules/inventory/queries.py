"""
Inventory Management Database Queries
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_, desc
from app import db
from .models import (
    InventoryProduct, InventoryCategory, StockMovement, InventoryAlert, InventoryConsumption
)

# ============ PRODUCT MANAGEMENT ============

def get_all_products(include_inactive=False):
    """Get all products with optional inactive filter"""
    query = InventoryProduct.query
    if not include_inactive:
        query = query.filter(InventoryProduct.is_active == True)
    return query.order_by(InventoryProduct.name).all()

def get_products_by_category(category_id):
    """Get products by category"""
    return InventoryProduct.query.filter_by(category_id=category_id, is_active=True).all()

def get_product_by_id(product_id):
    """Get product by ID"""
    return InventoryProduct.query.get(product_id)

def get_product_by_sku(sku):
    """Get product by SKU"""
    return InventoryProduct.query.filter_by(sku=sku).first()

def search_products(search_term):
    """Search products by name, SKU, or description"""
    return InventoryProduct.query.filter(
        or_(
            InventoryProduct.name.ilike(f'%{search_term}%'),
            InventoryProduct.sku.ilike(f'%{search_term}%'),
            InventoryProduct.description.ilike(f'%{search_term}%')
        )
    ).filter(InventoryProduct.is_active == True).all()

def get_low_stock_products():
    """Get products that are low on stock"""
    return InventoryProduct.query.filter(
        InventoryProduct.current_stock <= InventoryProduct.min_stock_level,
        InventoryProduct.is_active == True
    ).all()

def get_out_of_stock_products():
    """Get products that are out of stock"""
    return InventoryProduct.query.filter(
        InventoryProduct.current_stock <= 0,
        InventoryProduct.is_active == True
    ).all()

def get_products_needing_reorder():
    """Get products that need to be reordered"""
    return InventoryProduct.query.filter(
        InventoryProduct.current_stock <= InventoryProduct.reorder_point,
        InventoryProduct.is_active == True
    ).all()

def create_product(product_data):
    """Create new product"""
    try:
        # Ensure numeric fields have proper defaults
        defaults = {
            'current_stock': 0.0,
            'reserved_stock': 0.0,
            'available_stock': 0.0,
            'min_stock_level': 10.0,
            'max_stock_level': 100.0,
            'reorder_point': 20.0,
            'cost_price': 0.0,
            'selling_price': 0.0
        }

        # Apply defaults for missing numeric fields
        for key, default_value in defaults.items():
            if key not in product_data or product_data[key] is None:
                product_data[key] = default_value

        product = InventoryProduct(**product_data)
        product.update_available_stock()
        db.session.add(product)
        db.session.commit()
        return product
    except Exception as e:
        db.session.rollback()
        raise e

def update_product(product_id, product_data):
    """Update existing product"""
    try:
        product = InventoryProduct.query.get(product_id)
        if not product:
            return None

        # Update fields
        for key, value in product_data.items():
            if hasattr(product, key):
                setattr(product, key, value)

        product.updated_at = datetime.utcnow()
        db.session.commit()

        return product

    except Exception as e:
        db.session.rollback()
        raise e

def delete_product(product_id):
    """Delete product"""
    try:
        product = InventoryProduct.query.get(product_id)
        if not product:
            return False

        db.session.delete(product)
        db.session.commit()

        return True

    except Exception as e:
        db.session.rollback()
        raise e

# ============ STOCK MANAGEMENT ============

def update_stock(product_id, new_quantity, movement_type, reason="", reference_type=None, reference_id=None, user_id=None):
    """Update product stock and create movement record"""
    try:
        product = get_product_by_id(product_id)
        if not product:
            return None

        # Convert to float to handle decimal/float type mixing
        old_stock = float(product.current_stock or 0)
        new_quantity = float(new_quantity)
        quantity_change = new_quantity - old_stock

        # Create stock movement record
        movement = StockMovement(
            product_id=product_id,
            movement_type=movement_type,
            quantity=abs(quantity_change),
            stock_before=old_stock,
            stock_after=new_quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            reason=reason,
            created_by=user_id
        )

        # Update product stock
        product.current_stock = new_quantity
        product.update_available_stock()
        product.updated_at = datetime.utcnow()

        db.session.add(movement)
        db.session.commit()

        # Check for alerts
        check_stock_alerts(product)

        return product
    except Exception as e:
        db.session.rollback()
        raise e

def add_stock(product_id, quantity, reason="", reference_type=None, reference_id=None, unit_cost=0, user_id=None):
    """Add stock to product"""
    product = get_product_by_id(product_id)
    if product:
        # Convert to float to handle decimal/float type mixing
        current_stock = float(product.current_stock or 0)
        quantity = float(quantity)
        new_quantity = current_stock + quantity
        
        updated_product = update_stock(product_id, new_quantity, 'in', reason, reference_type, reference_id, user_id)
        
        # Update the movement with unit cost if provided
        if updated_product and unit_cost:
            latest_movement = StockMovement.query.filter_by(
                product_id=product_id,
                created_by=user_id
            ).order_by(desc(StockMovement.created_at)).first()
            if latest_movement:
                latest_movement.unit_cost = float(unit_cost)
                db.session.commit()
        
        return updated_product
    return None

def remove_stock(product_id, quantity, reason="", reference_type=None, reference_id=None, user_id=None):
    """Remove stock from product"""
    product = get_product_by_id(product_id)
    if product:
        # Convert to float to handle decimal/float type mixing
        current_stock = float(product.current_stock or 0)
        quantity = float(quantity)
        new_quantity = max(0, current_stock - quantity)
        return update_stock(product_id, new_quantity, 'out', reason, reference_type, reference_id, user_id)
    return None

def get_stock_movements(product_id=None, limit=50):
    """Get stock movements with optional product filter"""
    query = StockMovement.query
    if product_id:
        query = query.filter_by(product_id=product_id)
    return query.order_by(desc(StockMovement.created_at)).limit(limit).all()

# ============ CATEGORY MANAGEMENT ============

def get_all_categories(include_inactive=False):
    """Get all categories"""
    query = InventoryCategory.query
    if not include_inactive:
        query = query.filter(InventoryCategory.is_active == True)
    return query.order_by(InventoryCategory.name).all()

def get_category_by_id(category_id):
    """Get category by ID"""
    return InventoryCategory.query.get(category_id)

def create_category(category_data):
    """Create new category"""
    try:
        category = InventoryCategory(**category_data)
        db.session.add(category)
        db.session.commit()
        return category
    except Exception as e:
        db.session.rollback()
        raise e

def update_category(category_id, category_data):
    """Update existing category"""
    try:
        category = get_category_by_id(category_id)
        if category:
            for key, value in category_data.items():
                setattr(category, key, value)
            db.session.commit()
            return category
    except Exception as e:
        db.session.rollback()
        raise e
    return None

def delete_category(category_id):
    """Soft delete category (mark as inactive)"""
    try:
        category = get_category_by_id(category_id)
        if category:
            category.is_active = False
            db.session.commit()
            return True
    except Exception as e:
        db.session.rollback()
        raise e
    return False



# ============ ALERT MANAGEMENT ============

def check_stock_alerts(product):
    """Check and create stock alerts for a product"""
    try:
        # Clear existing unresolved alerts for this product
        InventoryAlert.query.filter_by(
            product_id=product.id,
            is_resolved=False
        ).delete()

        alerts_to_create = []

        if product.current_stock <= 0:
            alerts_to_create.append({
                'alert_type': 'out_of_stock',
                'message': f'{product.name} is out of stock',
                'severity': 'critical'
            })
        elif product.current_stock <= product.min_stock_level:
            alerts_to_create.append({
                'alert_type': 'low_stock',
                'message': f'{product.name} is running low (Current: {product.current_stock}, Min: {product.min_stock_level})',
                'severity': 'high'
            })
        elif product.current_stock <= product.reorder_point:
            alerts_to_create.append({
                'alert_type': 'reorder_needed',
                'message': f'{product.name} needs to be reordered',
                'severity': 'medium'
            })

        # Create alerts
        for alert_data in alerts_to_create:
            alert_data['product_id'] = product.id
            alert = InventoryAlert(**alert_data)
            db.session.add(alert)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

def get_active_alerts():
    """Get all active (unresolved) alerts"""
    return InventoryAlert.query.filter_by(is_resolved=False).order_by(desc(InventoryAlert.created_at)).all()

def get_alerts_by_severity(severity):
    """Get alerts by severity level"""
    return InventoryAlert.query.filter_by(severity=severity, is_resolved=False).all()

# ============ DASHBOARD STATISTICS ============

def get_inventory_dashboard_stats():
    """Get comprehensive inventory statistics for dashboard"""
    try:
        total_products = InventoryProduct.query.filter_by(is_active=True).count()
        low_stock_count = len(get_low_stock_products())
        out_of_stock_count = len(get_out_of_stock_products())

        # Total inventory value
        total_value = db.session.query(
            func.sum(InventoryProduct.current_stock * InventoryProduct.cost_price)
        ).filter(InventoryProduct.is_active == True).scalar() or 0

        # Recent movements
        recent_movements = get_stock_movements(limit=10)

        # Active alerts
        active_alerts = len(get_active_alerts())

        return {
            'total_products': total_products,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'total_value': float(total_value),
            'recent_movements': recent_movements,
            'active_alerts': active_alerts
        }
    except Exception as e:
        return {
            'total_products': 0,
            'low_stock_count': 0,
            'out_of_stock_count': 0,
            'total_value': 0,
            'recent_movements': [],
            'active_alerts': 0
        }

# ============ LOCATION MANAGEMENT ============

def get_all_locations(include_inactive=False):
    """Get all inventory locations"""
    from .models import InventoryLocation
    query = InventoryLocation.query
    if not include_inactive:
        query = query.filter(InventoryLocation.status == 'active')
    return query.order_by(InventoryLocation.name).all()

def get_location_by_id(location_id):
    """Get location by ID"""
    from .models import InventoryLocation
    return InventoryLocation.query.get(location_id)

def create_location(location_data):
    """Create new location"""
    try:
        from .models import InventoryLocation
        location = InventoryLocation(**location_data)
        db.session.add(location)
        db.session.commit()
        return location
    except Exception as e:
        db.session.rollback()
        raise e

def update_location(location_id, location_data):
    """Update existing location"""
    try:
        from .models import InventoryLocation
        location = InventoryLocation.query.get(location_id)
        if not location:
            return None

        for key, value in location_data.items():
            if hasattr(location, key):
                setattr(location, key, value)

        location.updated_at = datetime.utcnow()
        db.session.commit()
        return location
    except Exception as e:
        db.session.rollback()
        raise e

def delete_location(location_id):
    """Delete location"""
    try:
        from .models import InventoryLocation
        location = InventoryLocation.query.get(location_id)
        if not location:
            return False

        db.session.delete(location)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e

def initialize_default_locations():
    """Initialize default locations if none exist"""
    try:
        from .models import InventoryLocation
        
        # Check if locations already exist
        if InventoryLocation.query.count() > 0:
            return True
            
        # Create default locations
        default_locations = [
            {
                'id': 'main-spa',
                'name': 'Main Spa',
                'type': 'branch',
                'address': 'Main Building',
                'status': 'active'
            },
            {
                'id': 'storage-room',
                'name': 'Storage Room',
                'type': 'warehouse',
                'address': 'Back Storage Area',
                'status': 'active'
            },
            {
                'id': 'reception',
                'name': 'Reception Area',
                'type': 'room',
                'address': 'Front Desk',
                'status': 'active'
            }
        ]
        
        for location_data in default_locations:
            location = InventoryLocation(**location_data)
            db.session.add(location)
            
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating default locations: {e}")
        return False

def get_all_locations(include_inactive=False):
    """Get all inventory locations"""
    from .models import InventoryLocation
    query = InventoryLocation.query
    if not include_inactive:
        query = query.filter(InventoryLocation.status == 'active')
    return query.order_by(InventoryLocation.name).all()

def get_location_by_id(location_id):
    """Get location by ID"""
    from .models import InventoryLocation
    return InventoryLocation.query.get(location_id)

def create_location(location_data):
    """Create new location"""
    try:
        from .models import InventoryLocation
        location = InventoryLocation(**location_data)
        db.session.add(location)
        db.session.commit()
        return location
    except Exception as e:
        db.session.rollback()
        raise e

def update_location(location_id, location_data):
    """Update existing location"""
    try:
        from .models import InventoryLocation
        location = InventoryLocation.query.get(location_id)
        if not location:
            return None

        for key, value in location_data.items():
            if hasattr(location, key):
                setattr(location, key, value)

        location.updated_at = datetime.utcnow()
        db.session.commit()
        return location
    except Exception as e:
        db.session.rollback()
        raise e

def delete_location(location_id):
    """Delete location"""
    try:
        from .models import InventoryLocation
        location = InventoryLocation.query.get(location_id)
        if not location:
            return False

        db.session.delete(location)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e

def initialize_default_locations():
    """Initialize default locations if none exist"""
    try:
        from .models import InventoryLocation
        if InventoryLocation.query.count() == 0:
            default_locations = [
                {
                    'id': 'main-branch',
                    'name': 'Main Branch',
                    'type': 'branch',
                    'address': 'Main Street, Downtown',
                    'contact_person': 'Manager',
                    'phone': '(555) 123-4567',
                    'status': 'active'
                },
                {
                    'id': 'storage-room',
                    'name': 'Storage Room',
                    'type': 'room',
                    'address': 'Back Office Area',
                    'contact_person': 'Store Keeper',
                    'phone': '',
                    'status': 'active'
                }
            ]
            
            for location_data in default_locations:
                location = InventoryLocation(**location_data)
                db.session.add(location)
            
            db.session.commit()
            return True
    except Exception as e:
        db.session.rollback()
        return False

# ============ CONSUMPTION MANAGEMENT ============

def get_all_consumption_records(page=1, per_page=20, search_term=''):
    """Get consumption records with pagination and search"""
    try:
        query = InventoryConsumption.query

        # Apply search filter
        if search_term:
            query = query.join(InventoryProduct).filter(
                or_(
                    InventoryProduct.name.ilike(f'%{search_term}%'),
                    InventoryProduct.sku.ilike(f'%{search_term}%'),
                    InventoryConsumption.issued_to.ilike(f'%{search_term}%'),
                    InventoryConsumption.reference_doc_no.ilike(f'%{search_term}%')
                )
            )

        # Order by most recent first
        query = query.order_by(desc(InventoryConsumption.consumption_date), desc(InventoryConsumption.created_at))

        # Get paginated results
        if per_page:
            return query.paginate(page=page, per_page=per_page, error_out=False)
        else:
            return query.all()
    except Exception as e:
        return []

def get_consumption_by_id(consumption_id):
    """Get consumption record by ID"""
    return InventoryConsumption.query.get(consumption_id)

def create_consumption_record(consumption_data, user_id=None):
    """Create new consumption record and update stock levels"""
    try:
        from decimal import Decimal
        
        # Ensure quantity_used is Decimal for consistency
        if 'quantity_used' in consumption_data:
            consumption_data['quantity_used'] = Decimal(str(consumption_data['quantity_used']))
        
        # Create consumption record
        consumption = InventoryConsumption(**consumption_data)
        consumption.created_by = user_id
        db.session.add(consumption)
        db.session.flush()  # Get the ID

        # Update stock levels
        product = get_product_by_id(consumption.product_id)
        if product:
            # Convert to Decimal for consistent arithmetic
            current_stock = Decimal(str(product.current_stock or 0))
            quantity_used = Decimal(str(consumption.quantity_used or 0))
            
            # Check if sufficient stock
            if current_stock < quantity_used:
                raise ValueError(f"Insufficient stock. Available: {current_stock}, Required: {quantity_used}")

            # Deduct from stock - now both are Decimal types
            new_stock = current_stock - quantity_used
            update_stock(
                product_id=consumption.product_id,
                new_quantity=float(new_stock),  # Convert to float for update_stock
                movement_type='out',
                reason=f"Consumption - Issued to: {consumption.issued_to}",
                reference_type='consumption',
                reference_id=consumption.id,
                user_id=user_id
            )

        db.session.commit()
        return consumption
    except Exception as e:
        db.session.rollback()
        raise e

def update_consumption_record(consumption_id, consumption_data, user_id=None):
    """Update existing consumption record and adjust stock levels"""
    try:
        from decimal import Decimal
        
        consumption = get_consumption_by_id(consumption_id)
        if not consumption:
            return None

        # Convert to Decimal for consistent arithmetic
        old_quantity = Decimal(str(consumption.quantity_used or 0))
        old_product_id = consumption.product_id

        # Ensure quantity_used is Decimal if being updated
        if 'quantity_used' in consumption_data:
            consumption_data['quantity_used'] = Decimal(str(consumption_data['quantity_used']))

        # Update consumption record
        for key, value in consumption_data.items():
            setattr(consumption, key, value)
        consumption.updated_at = datetime.utcnow()

        # Convert new quantity to Decimal
        new_quantity = Decimal(str(consumption.quantity_used or 0))

        # Handle stock adjustments if quantity or product changed
        if old_product_id != consumption.product_id or old_quantity != new_quantity:
            # Restore old stock
            old_product = get_product_by_id(old_product_id)
            if old_product:
                old_current_stock = Decimal(str(old_product.current_stock or 0))
                old_stock_restored = old_current_stock + old_quantity
                update_stock(
                    product_id=old_product_id,
                    new_quantity=float(old_stock_restored),
                    movement_type='in',
                    reason=f"Consumption adjustment - Restored stock",
                    reference_type='consumption_adjustment',
                    reference_id=consumption.id,
                    user_id=user_id
                )

            # Apply new consumption
            new_product = get_product_by_id(consumption.product_id)
            if new_product:
                new_current_stock = Decimal(str(new_product.current_stock or 0))
                
                if new_current_stock < new_quantity:
                    raise ValueError(f"Insufficient stock. Available: {new_current_stock}, Required: {new_quantity}")

                final_stock = new_current_stock - new_quantity
                update_stock(
                    product_id=consumption.product_id,
                    new_quantity=float(final_stock),
                    movement_type='out',
                    reason=f"Consumption update - Issued to: {consumption.issued_to}",
                    reference_type='consumption',
                    reference_id=consumption.id,
                    user_id=user_id
                )

        db.session.commit()
        return consumption
    except Exception as e:
        db.session.rollback()
        raise e

def delete_consumption_record(consumption_id, user_id=None):
    """Delete consumption record and restore stock levels"""
    try:
        from decimal import Decimal
        
        consumption = get_consumption_by_id(consumption_id)
        if not consumption:
            return False

        # Restore stock levels
        product = get_product_by_id(consumption.product_id)
        if product:
            # Convert to Decimal for consistent arithmetic
            current_stock = Decimal(str(product.current_stock or 0))
            quantity_to_restore = Decimal(str(consumption.quantity_used or 0))
            restored_stock = current_stock + quantity_to_restore
            
            update_stock(
                product_id=consumption.product_id,
                new_quantity=float(restored_stock),
                movement_type='in',
                reason=f"Consumption deleted - Stock restored",
                reference_type='consumption_deleted',
                reference_id=consumption.id,
                user_id=user_id
            )

        db.session.delete(consumption)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e

def get_consumption_by_product(product_id, limit=None):
    """Get consumption records for a specific product"""
    query = InventoryConsumption.query.filter_by(product_id=product_id)
    query = query.order_by(desc(InventoryConsumption.consumption_date))

    if limit:
        return query.limit(limit).all()
    return query.all()

def get_consumption_by_date_range(start_date, end_date):
    """Get consumption records within date range"""
    return InventoryConsumption.query.filter(
        and_(
            InventoryConsumption.consumption_date >= start_date,
            InventoryConsumption.consumption_date <= end_date
        )
    ).order_by(desc(InventoryConsumption.consumption_date)).all()

def get_consumption_summary_stats():
    """Get consumption summary statistics"""
    try:
        total_records = InventoryConsumption.query.count()

        # Get consumption for current month
        today = date.today()
        first_day = today.replace(day=1)
        monthly_records = InventoryConsumption.query.filter(
            InventoryConsumption.consumption_date >= first_day
        ).count()

        # Get most consumed items
        most_consumed = db.session.query(
            InventoryProduct.name,
            func.sum(InventoryConsumption.quantity_used).label('total_consumed')
        ).join(InventoryConsumption).group_by(InventoryProduct.id, InventoryProduct.name).order_by(
            desc('total_consumed')
        ).limit(5).all()

        return {
            'total_records': total_records,
            'monthly_records': monthly_records,
            'most_consumed': most_consumed
        }
    except Exception as e:
        return {
            'total_records': 0,
            'monthly_records': 0,
            'most_consumed': []
        }