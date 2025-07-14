"""
Inventory-related database queries
"""
from datetime import date, timedelta
from sqlalchemy import or_, func
from app import db
from models import Inventory, Category

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

def update_stock(inventory_id, quantity_change):
    """Update stock quantity"""
    inventory = Inventory.query.get(inventory_id)
    if inventory:
        inventory.current_stock += quantity_change
        db.session.commit()
        return inventory
    return None