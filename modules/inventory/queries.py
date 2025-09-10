"""
Inventory Management Database Queries - BATCH-CENTRIC APPROACH
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_, desc
from app import db
from .models import (
    InventoryProduct, InventoryCategory, InventoryAlert, InventoryConsumption, InventoryBatch,
    InventoryAuditLog, InventoryAdjustment, InventoryTransfer, InventoryLocation
)

# ============ PRODUCT MANAGEMENT (NO STOCK TRACKING) ============

def get_all_products(include_inactive=False):
    """Get all products with optional inactive filter"""
    query = InventoryProduct.query
    if not include_inactive:
        query = query.filter(InventoryProduct.is_active == True)
    return query.order_by(InventoryProduct.name).all()

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

def create_product(product_data):
    """Create new product - NO STOCK FIELDS"""
    try:
        valid_fields = ['sku', 'name', 'description', 'category_id', 'unit_of_measure', 'barcode', 'is_active', 'is_service_item', 'is_retail_item']
        filtered_data = {k: v for k, v in product_data.items() if k in valid_fields}

        product = InventoryProduct(**filtered_data)
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

        valid_fields = ['sku', 'name', 'description', 'category_id', 'unit_of_measure', 'barcode', 'is_active', 'is_service_item', 'is_retail_item']
        for key, value in product_data.items():
            if key in valid_fields and hasattr(product, key) and value is not None:
                setattr(product, key, value)

        product.updated_at = datetime.utcnow()
        db.session.commit()
        return product
    except Exception as e:
        db.session.rollback()
        raise e

def delete_product(product_id):
    """Delete a product - marks as inactive instead of hard delete"""
    try:
        product = InventoryProduct.query.get(product_id)
        if not product:
            return None
            
        # Soft delete - mark as inactive instead of hard delete
        product.is_active = False
        product.updated_at = datetime.utcnow()
        db.session.commit()
        return product
    except Exception as e:
        db.session.rollback()
        raise e

def update_category(category_id, category_data):
    """Update existing category"""
    try:
        category = InventoryCategory.query.get(category_id)
        if not category:
            return None

        valid_fields = ['name', 'description', 'color_code', 'is_active']
        for key, value in category_data.items():
            if key in valid_fields and hasattr(category, key) and value is not None:
                setattr(category, key, value)

        db.session.commit()
        return category
    except Exception as e:
        db.session.rollback()
        raise e

def update_location(location_id, location_data):
    """Update existing location"""
    try:
        location = InventoryLocation.query.get(location_id)
        if not location:
            return None

        valid_fields = ['name', 'type', 'address', 'contact_person', 'phone', 'status']
        for key, value in location_data.items():
            if key in valid_fields and hasattr(location, key) and value is not None:
                setattr(location, key, value)

        location.updated_at = datetime.utcnow()
        db.session.commit()
        return location
    except Exception as e:
        db.session.rollback()
        raise e

# ============ BATCH-CENTRIC STOCK LOGIC ============

def get_low_stock_products():
    """Get products that are low on stock (based on batch totals)"""
    products = InventoryProduct.query.filter(InventoryProduct.is_active == True).all()
    return [p for p in products if p.total_stock <= 10]

def get_out_of_stock_products():
    """Get products that are out of stock (based on batch totals)"""
    products = InventoryProduct.query.filter(InventoryProduct.is_active == True).all()
    return [p for p in products if p.total_stock <= 0]

def get_products_needing_reorder():
    """Get products that need to be reordered (based on batch totals)"""
    products = InventoryProduct.query.filter(InventoryProduct.is_active == True).all()
    return [p for p in products if p.total_stock <= 20]

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

# ============ LOCATION MANAGEMENT ============

def get_all_locations(include_inactive=False):
    """Get all inventory locations"""
    query = InventoryLocation.query
    if not include_inactive:
        query = query.filter(InventoryLocation.status == 'active')
    return query.order_by(InventoryLocation.name).all()

def get_location_by_id(location_id):
    """Get location by ID"""
    return InventoryLocation.query.get(location_id)

def create_location(location_data):
    """Create new location"""
    try:
        location = InventoryLocation(**location_data)
        db.session.add(location)
        db.session.commit()
        return location
    except Exception as e:
        db.session.rollback()
        raise e

def initialize_default_locations():
    """Initialize default locations if none exist"""
    try:
        if InventoryLocation.query.count() > 0:
            return True

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

def initialize_default_categories():
    """Initialize default categories if none exist"""
    try:
        if InventoryCategory.query.count() > 0:
            return True

        default_categories = [
            {
                'name': 'Skincare Products',
                'description': 'Facial and body skincare treatments',
                'color_code': '#e74c3c',
                'is_active': True
            },
            {
                'name': 'Massage Oils',
                'description': 'Essential oils and massage therapy products',
                'color_code': '#3498db',
                'is_active': True
            },
            {
                'name': 'Spa Equipment',
                'description': 'Tools and equipment for spa treatments',
                'color_code': '#9b59b6',
                'is_active': True
            },
            {
                'name': 'Towels & Linens',
                'description': 'Towels, robes, and spa linens',
                'color_code': '#2ecc71',
                'is_active': True
            }
        ]

        for category_data in default_categories:
            category = InventoryCategory(**category_data)
            db.session.add(category)

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False

# ============ BATCH MANAGEMENT ============

def get_all_batches():
    """Get all batches"""
    return InventoryBatch.query.order_by(InventoryBatch.batch_name).all()

def get_batch_by_id(batch_id):
    """Get batch by ID"""
    return InventoryBatch.query.get(batch_id)

def get_available_batches_for_transactions():
    """Get batches available for adjustments and consumption"""
    from datetime import date
    return InventoryBatch.query.filter(
        InventoryBatch.status == 'active',
        or_(
            InventoryBatch.expiry_date == None,
            InventoryBatch.expiry_date >= date.today()
        )
    ).order_by(InventoryBatch.expiry_date.asc().nullslast(), InventoryBatch.batch_name).all()

def get_available_batches_for_consumption():
    """Get batches available for consumption - alias for transactions"""
    return get_available_batches_for_transactions()

def get_expiring_batches(days=30):
    """Get batches expiring within specified days"""
    from datetime import date, timedelta
    expiry_threshold = date.today() + timedelta(days=days)
    return InventoryBatch.query.filter(
        and_(
            InventoryBatch.expiry_date <= expiry_threshold,
            InventoryBatch.expiry_date > date.today(),
            InventoryBatch.qty_available > 0
        )
    ).all()

def get_expired_batches():
    """Get all expired batches"""
    from datetime import date
    return InventoryBatch.query.filter(
        InventoryBatch.expiry_date <= date.today()
    ).all()

# ============ AUDIT LOG MANAGEMENT ============

def create_audit_log(batch_id, product_id, user_id, action_type, quantity_delta, stock_before, stock_after, reference_type=None, reference_id=None, notes=None):
    """Create audit log entry for batch stock changes"""
    try:
        audit_log = InventoryAuditLog(
            batch_id=batch_id,
            product_id=product_id,
            user_id=user_id,
            action_type=action_type,
            quantity_delta=quantity_delta,
            stock_before=stock_before,
            stock_after=stock_after,
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes
        )
        db.session.add(audit_log)
        db.session.commit()
        return audit_log
    except Exception as e:
        db.session.rollback()
        raise e

def get_recent_audit_logs(limit=50):
    """Get recent audit logs for dashboard"""
    return InventoryAuditLog.query.order_by(desc(InventoryAuditLog.timestamp)).limit(limit).all()

# ============ BATCH-CENTRIC CONSUMPTION MANAGEMENT ============

def get_consumption_records(limit=50):
    """Get consumption records - BATCH-CENTRIC"""
    return InventoryConsumption.query.order_by(desc(InventoryConsumption.created_at)).limit(limit).all()

def create_consumption_record(batch_id, quantity, issued_to, reference=None, notes=None, user_id=None):
    """Create consumption record and update batch stock"""
    try:
        batch = InventoryBatch.query.get(batch_id)
        if not batch:
            raise ValueError("Batch not found")

        if batch.is_expired:
            raise ValueError("Cannot consume from expired batch")

        if float(quantity) > float(batch.qty_available):
            raise ValueError(f"Insufficient stock. Available: {batch.qty_available}, Required: {quantity}")

        # Create consumption record
        consumption = InventoryConsumption(
            batch_id=batch_id,
            quantity=quantity,
            issued_to=issued_to,
            reference=reference,
            notes=notes,
            created_by=user_id
        )

        # Update batch quantity
        old_qty = float(batch.qty_available)
        batch.qty_available -= float(quantity)

        # Create audit log
        create_audit_log(
            batch_id=batch_id,
            product_id=batch.product_id,
            user_id=user_id,
            action_type='consumption',
            quantity_delta=-float(quantity),
            stock_before=old_qty,
            stock_after=float(batch.qty_available),
            reference_type='consumption',
            reference_id=consumption.id,
            notes=f"Consumed by: {issued_to}"
        )

        db.session.add(consumption)
        db.session.commit()
        return consumption
    except Exception as e:
        db.session.rollback()
        raise e

# ============ BATCH-CENTRIC ADJUSTMENT MANAGEMENT ============

def create_adjustment_record(batch_id, adjustment_type, quantity, remarks, user_id=None, product_id=None, location_id=None):
    """Create adjustment record and update batch stock"""
    try:
        batch = InventoryBatch.query.get(batch_id)
        if not batch:
            raise ValueError("Batch not found")

        # Assign product and location if not already assigned
        if product_id and not batch.product_id:
            batch.product_id = product_id
        if location_id and not batch.location_id:
            batch.location_id = location_id

        # Create adjustment record
        adjustment = InventoryAdjustment(
            batch_id=batch_id,
            adjustment_type=adjustment_type,
            quantity=quantity,
            remarks=remarks,
            created_by=user_id
        )

        # Update batch quantity
        old_qty = float(batch.qty_available)
        if adjustment_type == 'add':
            batch.qty_available += float(quantity)
            quantity_delta = float(quantity)
        else:  # remove
            if float(quantity) > old_qty:
                raise ValueError(f"Cannot remove {quantity}. Only {old_qty} available.")
            batch.qty_available -= float(quantity)
            quantity_delta = -float(quantity)

        # Create audit log
        create_audit_log(
            batch_id=batch_id,
            product_id=batch.product_id,
            user_id=user_id,
            action_type=f'adjustment_{adjustment_type}',
            quantity_delta=quantity_delta,
            stock_before=old_qty,
            stock_after=float(batch.qty_available),
            reference_type='adjustment',
            reference_id=adjustment.id,
            notes=remarks
        )

        db.session.add(adjustment)
        db.session.commit()
        return adjustment
    except Exception as e:
        db.session.rollback()
        raise e

# ============ ALERT MANAGEMENT ============

def get_active_alerts():
    """Get all active (unresolved) alerts"""
    return InventoryAlert.query.filter_by(is_resolved=False).order_by(desc(InventoryAlert.created_at)).all()

def check_stock_alerts(product):
    """Check and create stock alerts for a product based on batch totals"""
    try:
        # Clear existing unresolved alerts for this product
        InventoryAlert.query.filter_by(
            product_id=product.id,
            is_resolved=False
        ).delete()

        alerts_to_create = []
        total_stock = product.total_stock

        if total_stock <= 0:
            alerts_to_create.append({
                'alert_type': 'out_of_stock',
                'message': f'{product.name} is out of stock',
                'severity': 'critical'
            })
        elif total_stock <= 10:
            alerts_to_create.append({
                'alert_type': 'low_stock',
                'message': f'{product.name} is running low (Current: {total_stock})',
                'severity': 'high'
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

# ============ DASHBOARD STATISTICS ============

def get_inventory_dashboard_stats():
    """Get comprehensive inventory statistics for dashboard - BATCH-CENTRIC"""
    try:
        total_products = InventoryProduct.query.filter_by(is_active=True).count()
        low_stock_count = len(get_low_stock_products())
        out_of_stock_count = len(get_out_of_stock_products())

        # Total inventory value from batches
        total_value = 0
        batches = InventoryBatch.query.filter(InventoryBatch.status == 'active').all()
        for batch in batches:
            if batch.qty_available and batch.unit_cost:
                total_value += float(batch.qty_available) * float(batch.unit_cost)

        # Recent audit logs instead of movements
        recent_movements = get_recent_audit_logs(limit=10)

        # Active alerts
        active_alerts = len(get_active_alerts())

        return {
            'total_products': total_products,
            'total_batches': len(batches),
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'total_value': float(total_value),
            'recent_movements': recent_movements,
            'active_alerts': active_alerts
        }
    except Exception as e:
        return {
            'total_products': 0,
            'total_batches': 0,
            'low_stock_count': 0,
            'out_of_stock_count': 0,
            'total_value': 0,
            'recent_movements': [],
            'active_alerts': 0
        }