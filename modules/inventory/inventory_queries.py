"""
Inventory-related database queries with comprehensive management features
"""
from datetime import date, timedelta
from sqlalchemy import or_, func, and_, desc
from app import db
from models import (
    Inventory, Category, Supplier, StockMovement, ServiceInventoryItem,
    PurchaseOrder, PurchaseOrderItem, InventoryAdjustment, ProductSale
)

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
        Inventory.has_expiry == True,
        Inventory.expiry_date <= today + timedelta(days=days),
        Inventory.expiry_date > today,
        Inventory.is_active == True
    ).order_by(Inventory.expiry_date).all()

def get_inventory_categories():
    """Get all active inventory categories"""
    return Category.query.filter(
        Category.category_type == 'product',
        Category.is_active == True
    ).order_by(Category.display_name).all()

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
    inventory = Inventory(**inventory_data)
    db.session.add(inventory)
    db.session.commit()
    return inventory

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
    """Generate automatic reorder suggestions"""
    items_to_reorder = Inventory.query.filter(
        Inventory.is_active == True,
        Inventory.current_stock <= Inventory.reorder_point,
        Inventory.reorder_quantity > 0
    ).all()
    
    suggestions = []
    for item in items_to_reorder:
        suggestions.append({
            'item_id': item.id,
            'item_name': item.name,
            'current_stock': item.current_stock,
            'reorder_point': item.reorder_point,
            'suggested_quantity': item.reorder_quantity,
            'supplier_id': item.primary_supplier_id,
            'supplier_name': item.supplier.name if item.supplier else item.supplier_name,
            'estimated_cost': item.reorder_quantity * item.cost_price
        })
    
    return suggestions

# NEW: Advanced Consumption Tracking Functions

def open_inventory_item(inventory_id, quantity, reason, batch_number, created_by):
    """Open/Issue an inventory item for container/lifecycle tracking"""
    from models import Inventory, InventoryItem, ConsumptionEntry, UsageDuration
    from datetime import datetime
    import uuid
    
    inventory = Inventory.query.get(inventory_id)
    if not inventory or inventory.tracking_type != 'container_lifecycle':
        return None
    
    if not inventory.can_fulfill_quantity(quantity):
        return None
    
    # Generate unique item code
    item_code = f"{inventory.sku}-{uuid.uuid4().hex[:8].upper()}"
    
    # Create inventory item instance
    inventory_item = InventoryItem(
        inventory_id=inventory_id,
        item_code=item_code,
        batch_number=batch_number,
        quantity=quantity,
        remaining_quantity=quantity,
        status='issued',
        issued_at=datetime.utcnow(),
        issued_by=created_by
    )
    
    # Create consumption entry
    consumption_entry = ConsumptionEntry(
        inventory_id=inventory_id,
        inventory_item_id=inventory_item.id,
        entry_type='open',
        quantity=quantity,
        unit=inventory.base_unit,
        reason=reason,
        batch_number=batch_number,
        cost_impact=quantity * inventory.cost_price,
        created_by=created_by
    )
    
    # Create usage duration tracking
    usage_duration = UsageDuration(
        inventory_id=inventory_id,
        inventory_item_id=inventory_item.id,
        opened_at=datetime.utcnow(),
        opened_by=created_by
    )
    
    # Update inventory stock
    inventory.current_stock -= quantity
    
    # Create stock movement
    movement = StockMovement(
        inventory_id=inventory_id,
        movement_type='service_use',
        quantity=-quantity,
        unit=inventory.base_unit,
        reference_type='open',
        reference_id=inventory_item.id,
        reason=reason,
        created_by=created_by
    )
    
    db.session.add(inventory_item)
    db.session.add(consumption_entry)
    db.session.add(usage_duration)
    db.session.add(movement)
    db.session.commit()
    
    return inventory_item

def consume_inventory_item(item_id, reason, created_by):
    """Mark inventory item as fully consumed"""
    from models import InventoryItem, ConsumptionEntry, UsageDuration
    from datetime import datetime
    
    inventory_item = InventoryItem.query.get(item_id)
    if not inventory_item or inventory_item.status != 'issued':
        return None
    
    # Update item status
    inventory_item.status = 'consumed'
    inventory_item.consumed_at = datetime.utcnow()
    inventory_item.consumed_by = created_by
    inventory_item.remaining_quantity = 0
    
    # Create consumption entry
    consumption_entry = ConsumptionEntry(
        inventory_id=inventory_item.inventory_id,
        inventory_item_id=item_id,
        entry_type='consume',
        quantity=inventory_item.remaining_quantity,
        unit=inventory_item.inventory.base_unit,
        reason=reason,
        batch_number=inventory_item.batch_number,
        created_by=created_by
    )
    
    # Update usage duration
    usage_duration = UsageDuration.query.filter_by(
        inventory_item_id=item_id, 
        finished_at=None
    ).first()
    
    if usage_duration:
        usage_duration.finished_at = datetime.utcnow()
        usage_duration.finished_by = created_by
        duration = usage_duration.finished_at - usage_duration.opened_at
        usage_duration.duration_hours = duration.total_seconds() / 3600
    
    db.session.add(consumption_entry)
    db.session.commit()
    
    return usage_duration

def deduct_inventory_quantity(inventory_id, quantity, unit, reason, reference_id, reference_type, created_by):
    """Deduct specific quantity for piece-wise tracking"""
    from models import Inventory, ConsumptionEntry
    
    inventory = Inventory.query.get(inventory_id)
    if not inventory:
        return None
    
    # Convert to base unit if needed
    if unit != inventory.base_unit:
        try:
            quantity_in_base = convert_units(quantity, unit, inventory.base_unit)
        except:
            quantity_in_base = quantity
    else:
        quantity_in_base = quantity
    
    if not inventory.can_fulfill_quantity(quantity_in_base):
        return None
    
    # Create consumption entry
    consumption_entry = ConsumptionEntry(
        inventory_id=inventory_id,
        entry_type='deduct',
        quantity=quantity,
        unit=unit,
        reason=reason,
        reference_id=reference_id,
        reference_type=reference_type,
        cost_impact=quantity_in_base * inventory.cost_price,
        created_by=created_by
    )
    
    # Update inventory stock
    inventory.current_stock -= quantity_in_base
    
    # Create stock movement
    movement = StockMovement(
        inventory_id=inventory_id,
        movement_type='service_use',
        quantity=-quantity_in_base,
        unit=inventory.base_unit,
        reference_type=reference_type,
        reference_id=reference_id,
        reason=reason,
        created_by=created_by
    )
    
    db.session.add(consumption_entry)
    db.session.add(movement)
    db.session.commit()
    
    return {
        'remaining_stock': inventory.current_stock,
        'deducted_quantity': quantity_in_base
    }

def create_manual_adjustment(inventory_id, new_quantity, adjustment_type, reason, created_by):
    """Create manual stock adjustment"""
    from models import Inventory, ConsumptionEntry
    
    inventory = Inventory.query.get(inventory_id)
    if not inventory:
        return None
    
    old_quantity = inventory.current_stock
    adjustment_quantity = new_quantity - old_quantity
    
    # Create consumption entry
    consumption_entry = ConsumptionEntry(
        inventory_id=inventory_id,
        entry_type='adjust',
        quantity=abs(adjustment_quantity),
        unit=inventory.base_unit,
        reason=reason,
        reference_type='manual_adjustment',
        cost_impact=abs(adjustment_quantity) * inventory.cost_price,
        created_by=created_by
    )
    
    # Update inventory stock
    inventory.current_stock = new_quantity
    
    # Create stock movement
    movement = StockMovement(
        inventory_id=inventory_id,
        movement_type='adjustment',
        quantity=adjustment_quantity,
        unit=inventory.base_unit,
        reference_type='manual_adjustment',
        reason=reason,
        created_by=created_by
    )
    
    db.session.add(consumption_entry)
    db.session.add(movement)
    db.session.commit()
    
    return {
        'old_quantity': old_quantity,
        'new_quantity': new_quantity,
        'adjustment': adjustment_quantity
    }

def get_consumption_entries(inventory_id=None, entry_type=None, staff_id=None, days=30):
    """Get consumption entries with filtering"""
    from models import ConsumptionEntry
    from datetime import datetime, timedelta
    
    query = ConsumptionEntry.query
    
    if inventory_id:
        query = query.filter(ConsumptionEntry.inventory_id == inventory_id)
    
    if entry_type:
        query = query.filter(ConsumptionEntry.entry_type == entry_type)
    
    if staff_id:
        query = query.filter(ConsumptionEntry.created_by == staff_id)
    
    # Filter by date range
    start_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(ConsumptionEntry.created_at >= start_date)
    
    return query.order_by(ConsumptionEntry.created_at.desc()).all()

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