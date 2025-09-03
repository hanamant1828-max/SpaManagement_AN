"""
Inventory-related database queries with comprehensive management features
"""
from datetime import date, timedelta
from sqlalchemy import func, and_, or_, desc, asc, text
from sqlalchemy.orm import joinedload
from app import db
from models import (
    InventoryProduct, InventoryTransaction, Service, Appointment, 
    InventoryCategory, User, InventoryItem, 
    ConsumptionEntry, UsageDuration, InventorySupplier,
    InventoryAlert, StockMovement
)
# Alias for compatibility
Inventory = InventoryProduct
Category = InventoryCategory

def get_all_inventory():
    """Get all active inventory items"""
    return Inventory.query.filter_by(is_active=True).order_by(Inventory.name).all()

def get_inventory_by_id(inventory_id):
    """Get inventory item by ID"""
    return Inventory.query.get(inventory_id)

def get_low_stock_items():
    """Get items with low stock"""
    return Inventory.query.filter(
        Inventory.current_stock <= Inventory.min_stock_level,
        Inventory.is_active == True
    ).order_by(Inventory.name).all()

def get_expiring_items(days=30):
    """Get items expiring within specified days"""
    today = date.today()
    return Inventory.query.filter(
        Inventory.expiry_date != None,
        Inventory.expiry_date <= today + timedelta(days=days),
        Inventory.expiry_date > today,
        Inventory.is_active == True
    ).order_by(Inventory.expiry_date).all()

def get_inventory_categories():
    """Get all active inventory categories"""
    return Category.query.filter(
        Category.is_active == True
    ).order_by(Category.category_name).all()

def search_inventory(query):
    """Search inventory by name or description"""
    return Inventory.query.filter(
        Inventory.is_active == True,
        or_(
            Inventory.name.ilike(f'%{query}%'),
            Inventory.description.ilike(f'%{query}%')
        )
    ).order_by(Inventory.name).all()

def create_inventory(inventory_data):
    """Create a new inventory item"""
    from app import db
    from models import Inventory
    import uuid

    try:
        # Generate SKU if not provided
        if not inventory_data.get('sku'):
            # Generate a unique SKU
            sku_prefix = inventory_data.get('name', 'ITEM')[:3].upper().replace(' ', '')
            sku_suffix = str(uuid.uuid4())[:8].upper()
            inventory_data['sku'] = f"{sku_prefix}-{sku_suffix}"

        # Set default values for required fields
        inventory_data.setdefault('base_unit', 'pcs')
        inventory_data.setdefault('selling_unit', 'pcs')
        inventory_data.setdefault('conversion_factor', 1.0)
        inventory_data.setdefault('item_type', 'consumable')
        inventory_data.setdefault('is_service_item', True)
        inventory_data.setdefault('is_retail_item', False)
        inventory_data.setdefault('tracking_type', 'piece_wise')

        # Set default stock levels
        current_stock = inventory_data.get('current_stock', 0)
        min_stock = inventory_data.get('min_stock_level', 5)
        inventory_data.setdefault('max_stock_level', max(100, current_stock * 2))
        inventory_data.setdefault('reorder_point', max(10, min_stock))
        inventory_data.setdefault('reorder_quantity', max(50, min_stock * 2))

        inventory = Inventory(**inventory_data)
        db.session.add(inventory)
        db.session.commit()
        return inventory

    except Exception as e:
        db.session.rollback()
        print(f"Error creating inventory: {e}")
        return None

def update_inventory(inventory_id, inventory_data):
    """Update an existing inventory item"""
    inventory = Inventory.query.get(inventory_id)
    if inventory:
        for key, value in inventory_data.items():
            setattr(inventory, key, value)
        db.session.commit()
    return inventory

def delete_inventory(inventory_id):
    """Soft delete an inventory item"""
    inventory = Inventory.query.get(inventory_id)
    if inventory:
        inventory.is_active = False
        db.session.commit()
        return True
    return False

def update_stock(inventory_id, quantity_change, movement_type='adjustment', reference_id=None, reference_type=None, reason=None, created_by=1):
    """Update stock quantity with movement tracking"""
    inventory = Inventory.query.get(inventory_id)
    if inventory:
        old_stock = inventory.current_stock
        inventory.current_stock += quantity_change

        # Create stock movement record
        movement = StockMovement(
            inventory_id=inventory_id,
            movement_type=movement_type,
            quantity=quantity_change,
            unit=inventory.base_unit,
            reference_id=reference_id,
            reference_type=reference_type,
            reason=reason or f'Stock {movement_type}',
            created_by=created_by
        )
        db.session.add(movement)
        db.session.commit()
        return inventory
    return None

# Enhanced inventory query functions

def get_items_by_status(status='all'):
    """Get inventory items by stock status"""
    query = Inventory.query.filter_by(is_active=True)

    if status == 'low_stock':
        query = query.filter(Inventory.current_stock <= Inventory.min_stock_level)
    elif status == 'out_of_stock':
        query = query.filter(Inventory.current_stock <= 0)
    elif status == 'expiring_soon':
        expiry_threshold = date.today() + timedelta(days=30)
        query = query.filter(
            Inventory.has_expiry == True,
            Inventory.expiry_date <= expiry_threshold,
            Inventory.expiry_date > date.today()
        )
    elif status == 'expired':
        query = query.filter(
            Inventory.has_expiry == True,
            Inventory.expiry_date < date.today()
        )
    elif status == 'reorder_needed':
        query = query.filter(Inventory.current_stock <= Inventory.reorder_point)
    elif status == 'overstocked':
        query = query.filter(Inventory.current_stock > Inventory.max_stock_level)
    # For 'all' status, no additional filters are applied

    return query.order_by(Inventory.name).all()

def get_stock_movements(inventory_id=None, movement_type=None, days=30):
    """Get stock movements with filters"""
    query = StockMovement.query

    if inventory_id:
        query = query.filter_by(inventory_id=inventory_id)

    if movement_type:
        query = query.filter_by(movement_type=movement_type)

    if days:
        date_threshold = date.today() - timedelta(days=days)
        query = query.filter(StockMovement.created_at >= date_threshold)

    return query.order_by(desc(StockMovement.created_at)).all()

def get_consumption_by_service(service_id=None, days=30):
    """Get inventory consumption by service"""
    query = db.session.query(
        StockMovement.inventory_id,
        Inventory.name.label('item_name'),
        func.sum(func.abs(StockMovement.quantity)).label('total_consumed'),
        StockMovement.unit
    ).join(Inventory).filter(
        StockMovement.movement_type == 'service_use',
        StockMovement.created_at >= date.today() - timedelta(days=days)
    )

    if service_id:
        query = query.filter(
            StockMovement.reference_type == 'service',
            StockMovement.reference_id == service_id
        )

    return query.group_by(
        StockMovement.inventory_id, 
        Inventory.name, 
        StockMovement.unit
    ).all()

def get_wastage_report(days=30):
    """Get wastage and adjustment report"""
    return StockMovement.query.filter(
        StockMovement.movement_type.in_(['wastage', 'damage', 'expiry', 'theft']),
        StockMovement.created_at >= date.today() - timedelta(days=days)
    ).order_by(desc(StockMovement.created_at)).all()

def get_supplier_performance():
    """Get supplier performance metrics"""
    return db.session.query(
        Supplier.id,
        Supplier.name,
        func.count(PurchaseOrder.id).label('total_orders'),
        func.avg(PurchaseOrder.total_amount).label('avg_order_value'),
        func.sum(PurchaseOrder.total_amount).label('total_spent'),
        Supplier.rating
    ).outerjoin(PurchaseOrder).group_by(Supplier.id, Supplier.name, Supplier.rating).all()

def get_inventory_valuation():
    """Get total inventory valuation"""
    return db.session.query(
        func.sum(Inventory.current_stock * Inventory.cost_price).label('total_cost_value'),
        func.sum(Inventory.current_stock * Inventory.selling_price / Inventory.conversion_factor).label('total_selling_value'),
        func.count(Inventory.id).label('total_items')
    ).filter(Inventory.is_active == True).first()

def convert_units(quantity, from_unit, to_unit, conversion_factor=1.0):
    """Convert between different units of measurement"""
    # Unit conversion mapping (to base unit - grams for weight, ml for volume)
    unit_conversions = {
        # Weight units (base: gram)
        'gram': 1.0, 'g': 1.0,
        'kg': 1000.0, 'kilogram': 1000.0,
        'pound': 453.592, 'lb': 453.592,
        'ounce': 28.3495, 'oz': 28.3495,

        # Volume units (base: ml)
        'ml': 1.0, 'milliliter': 1.0,
        'liter': 1000.0, 'l': 1000.0,
        'gallon': 3785.41, 'gal': 3785.41,
        'quart': 946.353, 'qt': 946.353,
        'pint': 473.176, 'pt': 473.176,
        'cup': 236.588,
        'fluid_ounce': 29.5735, 'fl_oz': 29.5735,

        # Count units
        'piece': 1.0, 'pcs': 1.0, 'pc': 1.0,
        'dozen': 12.0, 'dz': 12.0,
        'gross': 144.0,
        'pair': 2.0
    }

    from_factor = unit_conversions.get(from_unit.lower(), 1.0)
    to_factor = unit_conversions.get(to_unit.lower(), 1.0)

    # Convert to base unit, then to target unit
    base_quantity = quantity * from_factor
    converted_quantity = base_quantity / to_factor

    # Apply custom conversion factor if provided
    return converted_quantity * conversion_factor

def auto_deduct_service_inventory(appointment_id):
    """Automatically deduct inventory when service is completed and billed"""
    from models import Appointment

    appointment = Appointment.query.get(appointment_id)
    if not appointment or appointment.inventory_deducted:
        return False

    if appointment.status == 'completed' and appointment.is_paid:
        return appointment.process_inventory_deduction()

    return False

def create_stock_adjustment(inventory_id, new_quantity, adjustment_type, reason, created_by):
    """Create a stock adjustment record"""
    from models import Inventory, InventoryAdjustment, StockMovement
    inventory = Inventory.query.get(inventory_id)
    if not inventory:
        return None

    old_quantity = inventory.current_stock
    adjustment_quantity = new_quantity - old_quantity

    # Create adjustment record
    adjustment = InventoryAdjustment(
        inventory_id=inventory_id,
        adjustment_type=adjustment_type,
        old_quantity=old_quantity,
        new_quantity=new_quantity,
        adjustment_quantity=adjustment_quantity,
        reason=reason,
        cost_impact=abs(adjustment_quantity) * inventory.cost_price,
        created_by=created_by
    )

    # Update stock
    inventory.current_stock = new_quantity

    # Create stock movement
    movement = StockMovement(
        inventory_id=inventory_id,
        movement_type='adjustment',
        quantity=adjustment_quantity,
        unit=inventory.base_unit,
        reference_type='adjustment',
        reference_id=adjustment.id,
        reason=reason,
        created_by=created_by
    )

    db.session.add(adjustment)
    db.session.add(movement)
    db.session.commit()

    return adjustment

def generate_reorder_suggestions():
    """Generate automatic reorder suggestions based on consumption patterns"""
    suggestions = []

    # Get items that are low stock
    low_stock_items = get_low_stock_items()

    for item in low_stock_items:
        # Calculate suggested reorder quantity based on consumption rate
        recent_movements = StockMovement.query.filter(
            StockMovement.inventory_id == item.id,
            StockMovement.movement_type == 'out',
            StockMovement.created_at >= datetime.utcnow() - timedelta(days=30)
        ).all()

        monthly_consumption = sum(abs(m.quantity) for m in recent_movements)
        suggested_quantity = max(monthly_consumption * 2, item.min_stock_level * 3)

        suggestions.append({
            'item_id': item.id,
            'item_name': item.name,
            'current_stock': item.current_stock,
            'suggested_quantity': suggested_quantity,
            'estimated_cost': suggested_quantity * (item.cost_price or 0),
            'supplier_name': item.supplier_name,
            'priority': 'high' if item.current_stock <= 0 else 'medium'
        })

    return suggestions

def open_inventory_item(inventory_id, quantity, reason, batch_number, user_id):
    """Open/Issue an inventory item for container/lifecycle tracking"""
    try:
        inventory = Inventory.query.get(inventory_id)
        if not inventory or inventory.current_stock < quantity:
            return None

        # Create inventory item record
        item_code = f"ITM{datetime.now().strftime('%Y%m%d%H%M%S')}"
        inventory_item = InventoryItem(
            item_code=item_code,
            inventory_id=inventory_id,
            quantity=quantity,
            remaining_quantity=quantity,
            status='issued',
            issued_at=datetime.utcnow(),
            batch_number=batch_number,
            issued_by=user_id
        )

        # Create stock movement
        movement = StockMovement(
            inventory_id=inventory_id,
            movement_type='out',
            quantity=-quantity,
            unit=inventory.base_unit or 'pcs',
            reason=reason,
            created_by=user_id,
            created_at=datetime.utcnow()
        )

        # Update inventory stock
        inventory.current_stock -= quantity

        # Create consumption entry
        consumption = ConsumptionEntry(
            inventory_id=inventory_id,
            entry_type='open',
            quantity=quantity,
            unit=inventory.base_unit or 'pcs',
            reason=reason,
            staff_id=user_id,
            created_at=datetime.utcnow()
        )

        db.session.add(inventory_item)
        db.session.add(movement)
        db.session.add(consumption)
        db.session.commit()

        return inventory_item

    except Exception as e:
        db.session.rollback()
        print(f"Error opening inventory item: {e}")
        return None

def consume_inventory_item(item_id, reason, user_id):
    """Mark inventory item as fully consumed"""
    try:
        inventory_item = InventoryItem.query.get(item_id)
        if not inventory_item or inventory_item.status != 'issued':
            return None

        # Update item status
        inventory_item.status = 'consumed'
        inventory_item.consumed_at = datetime.utcnow()
        inventory_item.consumed_by = user_id

        # Calculate duration if needed
        duration_hours = None
        if inventory_item.issued_at:
            duration = datetime.utcnow() - inventory_item.issued_at
            duration_hours = duration.total_seconds() / 3600

        # Create consumption entry
        consumption = ConsumptionEntry(
            inventory_id=inventory_item.inventory_id,
            entry_type='consume',
            quantity=inventory_item.remaining_quantity,
            unit=inventory_item.inventory.base_unit or 'pcs',
            reason=reason,
            staff_id=user_id,
            created_at=datetime.utcnow()
        )

        # Create usage duration record
        if duration_hours:
            usage_duration = UsageDuration(
                inventory_item_id=item_id,
                started_at=inventory_item.issued_at,
                ended_at=datetime.utcnow(),
                duration_hours=duration_hours,
                staff_id=user_id
            )
            db.session.add(usage_duration)

        db.session.add(consumption)
        db.session.commit()

        class Result:
            def __init__(self, duration_hours):
                self.duration_hours = duration_hours

        return Result(duration_hours)

    except Exception as e:
        db.session.rollback()
        print(f"Error consuming inventory item: {e}")
        return None

def deduct_inventory_quantity(inventory_id, quantity, unit, reason, reference_id, reference_type, user_id):
    """Deduct specific quantity for piece-wise tracking"""
    try:
        inventory = Inventory.query.get(inventory_id)
        if not inventory or inventory.current_stock < quantity:
            return None

        # Create stock movement
        movement = StockMovement(
            inventory_id=inventory_id,
            movement_type='out',
            quantity=-quantity,
            unit=unit,
            reason=reason,
            reference_id=reference_id,
            reference_type=reference_type,
            created_by=user_id,
            created_at=datetime.utcnow()
        )

        # Update inventory stock
        inventory.current_stock -= quantity

        # Create consumption entry
        consumption = ConsumptionEntry(
            inventory_id=inventory_id,
            entry_type='deduct',
            quantity=quantity,
            unit=unit,
            reason=reason,
            staff_id=user_id,
            created_at=datetime.utcnow()
        )

        db.session.add(movement)
        db.session.add(consumption)
        db.session.commit()

        return {
            'remaining_stock': inventory.current_stock,
            'deducted_quantity': quantity
        }

    except Exception as e:
        db.session.rollback()
        print(f"Error deducting inventory quantity: {e}")
        return None

def create_manual_adjustment(inventory_id, new_quantity, adjustment_type, reason, user_id):
    """Create manual stock adjustment"""
    try:
        inventory = Inventory.query.get(inventory_id)
        if not inventory:
            return None

        old_quantity = inventory.current_stock
        adjustment = new_quantity - old_quantity

        # Create stock movement
        movement = StockMovement(
            inventory_id=inventory_id,
            movement_type='adjustment',
            quantity=adjustment,
            unit=inventory.base_unit or 'pcs',
            reason=f"{adjustment_type}: {reason}",
            created_by=user_id,
            created_at=datetime.utcnow()
        )

        # Update inventory stock
        inventory.current_stock = new_quantity

        # Create consumption entry
        consumption = ConsumptionEntry(
            inventory_id=inventory_id,
            entry_type='adjust',
            quantity=abs(adjustment),
            unit=inventory.base_unit or 'pcs',
            reason=reason,
            staff_id=user_id,
            created_at=datetime.utcnow()
        )

        db.session.add(movement)
        db.session.add(consumption)
        db.session.commit()

        return {
            'old_quantity': old_quantity,
            'new_quantity': new_quantity,
            'adjustment': adjustment
        }

    except Exception as e:
        db.session.rollback()
        print(f"Error creating manual adjustment: {e}")
        return None

def get_consumption_entries(inventory_id=None, entry_type=None, staff_id=None, days=30):
    """Get consumption entries with filtering using StockMovement table"""
    from models import StockMovement, Inventory, User
    from datetime import datetime, timedelta

    query = StockMovement.query.join(Inventory)

    if inventory_id:
        query = query.filter(StockMovement.inventory_id == inventory_id)

    if entry_type:
        # Map entry types to movement types
        movement_type_map = {
            'open': 'service_use',
            'consume': 'service_use', 
            'deduct': 'service_use',
            'adjust': 'adjustment'
        }
        movement_type = movement_type_map.get(entry_type, entry_type)
        query = query.filter(StockMovement.movement_type == movement_type)

    if staff_id:
        query = query.filter(StockMovement.created_by == staff_id)

    # Filter by date range
    start_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(StockMovement.created_at >= start_date)

    return query.order_by(StockMovement.created_at.desc()).limit(50).all()

def get_usage_duration_report(inventory_id=None, days=30):
    """Get usage duration report"""
    from models import UsageDuration, Inventory
    from datetime import datetime, timedelta
    from sqlalchemy import func

    query = db.session.query(
        Inventory.name,
        func.count(UsageDuration.id).label('total_items'),
        func.avg(UsageDuration.duration_hours).label('avg_duration_hours'),
        func.min(UsageDuration.duration_hours).label('min_duration_hours'),
        func.max(UsageDuration.duration_hours).label('max_duration_hours')
    ).join(UsageDuration, Inventory.id == UsageDuration.inventory_id)

    if inventory_id:
        query = query.filter(Inventory.id == inventory_id)

    # Filter by date range
    start_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(UsageDuration.opened_at >= start_date)
    query = query.filter(UsageDuration.finished_at.isnot(None))

    results = query.group_by(Inventory.name).all()

    return [{
        'item_name': result.name,
        'total_items_consumed': result.total_items,
        'average_duration_hours': round(float(result.avg_duration_hours or 0), 2),
        'minimum_duration_hours': round(float(result.min_duration_hours or 0), 2),
        'maximum_duration_hours': round(float(result.max_duration_hours or 0), 2)
    } for result in results]

def get_staff_usage_report(staff_id=None, days=30):
    """Get staff usage report"""
    from models import ConsumptionEntry, User, Inventory
    from datetime import datetime, timedelta
    from sqlalchemy import func

    query = db.session.query(
        User.first_name,
        User.last_name,
        Inventory.name,
        ConsumptionEntry.entry_type,
        func.sum(ConsumptionEntry.quantity).label('total_quantity'),
        func.sum(ConsumptionEntry.cost_impact).label('total_cost'),
        func.count(ConsumptionEntry.id).label('total_entries')
    ).join(ConsumptionEntry, User.id == ConsumptionEntry.created_by) \
     .join(Inventory, ConsumptionEntry.inventory_id == Inventory.id)

    if staff_id:
        query = query.filter(User.id == staff_id)

    # Filter by date range
    start_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(ConsumptionEntry.created_at >= start_date)

    results = query.group_by(
        User.first_name, User.last_name, 
        Inventory.name, ConsumptionEntry.entry_type
    ).all()

    return [{
        'staff_name': f"{result.first_name} {result.last_name}",
        'item_name': result.name,
        'entry_type': result.entry_type,
        'total_quantity': float(result.total_quantity),
        'total_cost_impact': float(result.total_cost or 0),
        'total_entries': result.total_entries
    } for result in results]