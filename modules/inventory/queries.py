"""
Inventory Management Database Queries
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_, desc
from app import db
from .models import (
    InventoryProduct, InventoryCategory, Supplier, StockMovement, 
    PurchaseOrder, PurchaseOrderItem, InventoryAlert, InventoryConsumption
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
        product = get_product_by_id(product_id)
        if product:
            for key, value in product_data.items():
                setattr(product, key, value)
            product.update_available_stock()
            db.session.commit()
            return product
    except Exception as e:
        db.session.rollback()
        raise e
    return None

def delete_product(product_id):
    """Soft delete product (mark as inactive)"""
    try:
        product = get_product_by_id(product_id)
        if product:
            product.is_active = False
            db.session.commit()
            return True
    except Exception as e:
        db.session.rollback()
        raise e
    return False

# ============ STOCK MANAGEMENT ============

def update_stock(product_id, new_quantity, movement_type, reason="", reference_type=None, reference_id=None, user_id=None):
    """Update product stock and create movement record"""
    try:
        product = get_product_by_id(product_id)
        if not product:
            return None
            
        old_stock = product.current_stock
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
        new_quantity = product.current_stock + quantity
        return update_stock(product_id, new_quantity, 'in', reason, reference_type, reference_id, user_id)
    return None

def remove_stock(product_id, quantity, reason="", reference_type=None, reference_id=None, user_id=None):
    """Remove stock from product"""
    product = get_product_by_id(product_id)
    if product:
        new_quantity = max(0, product.current_stock - quantity)
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

# ============ SUPPLIER MANAGEMENT ============

def get_all_suppliers(include_inactive=False):
    """Get all suppliers"""
    query = Supplier.query
    if not include_inactive:
        query = query.filter(Supplier.is_active == True)
    return query.order_by(Supplier.name).all()

def get_supplier_by_id(supplier_id):
    """Get supplier by ID"""
    return Supplier.query.get(supplier_id)

def create_supplier(supplier_data):
    """Create new supplier"""
    try:
        supplier = Supplier(**supplier_data)
        db.session.add(supplier)
        db.session.commit()
        return supplier
    except Exception as e:
        db.session.rollback()
        raise e

def update_supplier(supplier_id, supplier_data):
    """Update existing supplier"""
    try:
        supplier = get_supplier_by_id(supplier_id)
        if supplier:
            for key, value in supplier_data.items():
                setattr(supplier, key, value)
            supplier.updated_at = datetime.utcnow()
            db.session.commit()
            return supplier
    except Exception as e:
        db.session.rollback()
        raise e
    return None

# ============ PURCHASE ORDER MANAGEMENT ============

def create_purchase_order(po_data, items_data):
    """Create purchase order with items"""
    try:
        # Generate PO number if not provided
        if 'po_number' not in po_data:
            po_data['po_number'] = generate_po_number()
        
        po = PurchaseOrder(**po_data)
        db.session.add(po)
        db.session.flush()  # Get PO ID
        
        # Add items
        for item_data in items_data:
            item_data['purchase_order_id'] = po.id
            item = PurchaseOrderItem(**item_data)
            db.session.add(item)
        
        db.session.commit()
        po.calculate_totals()
        db.session.commit()
        
        return po
    except Exception as e:
        db.session.rollback()
        raise e

def get_purchase_orders(status=None):
    """Get purchase orders with optional status filter"""
    query = PurchaseOrder.query
    if status:
        query = query.filter_by(status=status)
    return query.order_by(desc(PurchaseOrder.created_at)).all()

def get_purchase_order_by_id(po_id):
    """Get purchase order by ID"""
    return PurchaseOrder.query.get(po_id)

def generate_po_number():
    """Generate unique PO number"""
    today = date.today()
    count = PurchaseOrder.query.filter(
        func.date(PurchaseOrder.created_at) == today
    ).count() + 1
    return f"PO-{today.strftime('%Y%m%d')}-{count:03d}"

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
        
        # Pending orders
        pending_orders = len(get_purchase_orders('sent'))
        
        # Active alerts
        active_alerts = len(get_active_alerts())
        
        return {
            'total_products': total_products,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'total_value': float(total_value),
            'recent_movements': recent_movements,
            'pending_orders': pending_orders,
            'active_alerts': active_alerts
        }
    except Exception as e:
        return {
            'total_products': 0,
            'low_stock_count': 0,
            'out_of_stock_count': 0,
            'total_value': 0,
            'recent_movements': [],
            'pending_orders': 0,
            'active_alerts': 0
        }

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
        # Create consumption record
        consumption = InventoryConsumption(**consumption_data)
        consumption.created_by = user_id
        db.session.add(consumption)
        db.session.flush()  # Get the ID
        
        # Update stock levels
        product = get_product_by_id(consumption.product_id)
        if product:
            # Check if sufficient stock
            if product.current_stock < consumption.quantity_used:
                raise ValueError(f"Insufficient stock. Available: {product.current_stock}, Required: {consumption.quantity_used}")
            
            # Deduct from stock
            new_stock = product.current_stock - consumption.quantity_used
            update_stock(
                product_id=consumption.product_id,
                new_quantity=new_stock,
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
        consumption = get_consumption_by_id(consumption_id)
        if not consumption:
            return None
        
        old_quantity = consumption.quantity_used
        old_product_id = consumption.product_id
        
        # Update consumption record
        for key, value in consumption_data.items():
            setattr(consumption, key, value)
        consumption.updated_at = datetime.utcnow()
        
        # Handle stock adjustments if quantity or product changed
        if old_product_id != consumption.product_id or old_quantity != consumption.quantity_used:
            # Restore old stock
            old_product = get_product_by_id(old_product_id)
            if old_product:
                old_stock_restored = old_product.current_stock + old_quantity
                update_stock(
                    product_id=old_product_id,
                    new_quantity=old_stock_restored,
                    movement_type='in',
                    reason=f"Consumption adjustment - Restored stock",
                    reference_type='consumption_adjustment',
                    reference_id=consumption.id,
                    user_id=user_id
                )
            
            # Apply new consumption
            new_product = get_product_by_id(consumption.product_id)
            if new_product:
                if new_product.current_stock < consumption.quantity_used:
                    raise ValueError(f"Insufficient stock. Available: {new_product.current_stock}, Required: {consumption.quantity_used}")
                
                new_stock = new_product.current_stock - consumption.quantity_used
                update_stock(
                    product_id=consumption.product_id,
                    new_quantity=new_stock,
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
        consumption = get_consumption_by_id(consumption_id)
        if not consumption:
            return False
        
        # Restore stock levels
        product = get_product_by_id(consumption.product_id)
        if product:
            restored_stock = product.current_stock + consumption.quantity_used
            update_stock(
                product_id=consumption.product_id,
                new_quantity=restored_stock,
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