"""
Hanaman Inventory Database Queries
Clean CRUD operations for inventory management
"""
from app import db
from .models import HanamanProduct, HanamanCategory, HanamanStockMovement, HanamanSupplier, HanamanItemTemplate
from datetime import datetime
from flask_login import current_user

# Category CRUD Operations
def get_all_categories():
    """Get all active categories"""
    return HanamanCategory.query.filter_by(is_active=True).order_by(HanamanCategory.name).all()

def get_category_by_id(category_id):
    """Get category by ID"""
    return HanamanCategory.query.get(category_id)

def create_category(name, description=""):
    """Create a new category"""
    try:
        category = HanamanCategory(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        return category
    except Exception as e:
        db.session.rollback()
        print(f"Error creating category: {e}")
        return None

def update_category(category_id, name, description=""):
    """Update existing category"""
    try:
        category = HanamanCategory.query.get(category_id)
        if category:
            category.name = name
            category.description = description
            category.updated_at = datetime.utcnow()
            db.session.commit()
            return category
        return None
    except Exception as e:
        db.session.rollback()
        print(f"Error updating category: {e}")
        return None

def delete_category(category_id):
    """Soft delete category"""
    try:
        category = HanamanCategory.query.get(category_id)
        if category:
            category.is_active = False
            category.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting category: {e}")
        return False

# Product CRUD Operations
def get_all_products():
    """Get all active products"""
    return HanamanProduct.query.filter_by(is_active=True).order_by(HanamanProduct.name).all()

def get_product_by_id(product_id):
    """Get product by ID"""
    return HanamanProduct.query.get(product_id)

def get_product_by_sku(sku):
    """Get product by SKU"""
    return HanamanProduct.query.filter_by(sku=sku, is_active=True).first()

def search_products(query):
    """Search products by name or SKU"""
    search_term = f"%{query}%"
    return HanamanProduct.query.filter(
        HanamanProduct.is_active == True,
        (HanamanProduct.name.ilike(search_term) | HanamanProduct.sku.ilike(search_term))
    ).order_by(HanamanProduct.name).all()

def get_low_stock_products():
    """Get products with low stock"""
    return HanamanProduct.query.filter(
        HanamanProduct.is_active == True,
        HanamanProduct.current_stock <= HanamanProduct.min_stock_level
    ).order_by(HanamanProduct.current_stock).all()

def create_product(product_data):
    """Create a new product"""
    try:
        product = HanamanProduct(**product_data)
        db.session.add(product)
        db.session.commit()
        return product
    except Exception as e:
        db.session.rollback()
        print(f"Error creating product: {e}")
        return None

def update_product(product_id, product_data):
    """Update existing product"""
    try:
        product = HanamanProduct.query.get(product_id)
        if product:
            for key, value in product_data.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            product.updated_at = datetime.utcnow()
            db.session.commit()
            return product
        return None
    except Exception as e:
        db.session.rollback()
        print(f"Error updating product: {e}")
        return None

def delete_product(product_id):
    """Soft delete product"""
    try:
        product = HanamanProduct.query.get(product_id)
        if product:
            product.is_active = False
            product.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting product: {e}")
        return False

# Stock Management
def update_stock(product_id, new_quantity, movement_type, reason="Manual adjustment"):
    """Update product stock and create movement record"""
    try:
        product = HanamanProduct.query.get(product_id)
        if not product:
            return None
            
        previous_stock = product.current_stock
        quantity_change = new_quantity - previous_stock
        
        # Update product stock
        product.current_stock = new_quantity
        product.updated_at = datetime.utcnow()
        
        # Create stock movement record
        movement = HanamanStockMovement(
            product_id=product_id,
            movement_type=movement_type,
            quantity=quantity_change,
            previous_stock=previous_stock,
            new_stock=new_quantity,
            reason=reason,
            created_by=current_user.id if current_user.is_authenticated else None
        )
        
        db.session.add(movement)
        db.session.commit()
        return product
    except Exception as e:
        db.session.rollback()
        print(f"Error updating stock: {e}")
        return None

def adjust_stock(product_id, quantity_change, reason="Stock adjustment"):
    """Adjust stock by a specific amount"""
    try:
        product = HanamanProduct.query.get(product_id)
        if not product:
            return None
            
        new_quantity = max(0, product.current_stock + quantity_change)
        movement_type = 'in' if quantity_change > 0 else 'out'
        
        return update_stock(product_id, new_quantity, movement_type, reason)
    except Exception as e:
        print(f"Error adjusting stock: {e}")
        return None

def get_stock_movements(product_id=None, limit=50):
    """Get stock movement history"""
    query = HanamanStockMovement.query
    if product_id:
        query = query.filter_by(product_id=product_id)
    return query.order_by(HanamanStockMovement.created_at.desc()).limit(limit).all()

# Dashboard Statistics
def get_inventory_stats():
    """Get basic inventory statistics"""
    total_products = HanamanProduct.query.filter_by(is_active=True).count()
    low_stock_count = HanamanProduct.query.filter(
        HanamanProduct.is_active == True,
        HanamanProduct.current_stock <= HanamanProduct.min_stock_level
    ).count()
    out_of_stock_count = HanamanProduct.query.filter(
        HanamanProduct.is_active == True,
        HanamanProduct.current_stock <= 0
    ).count()
    
    total_value = db.session.query(
        db.func.sum(HanamanProduct.current_stock * HanamanProduct.cost_price)
    ).filter(HanamanProduct.is_active == True).scalar() or 0
    
    return {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'total_inventory_value': round(total_value, 2)
    }

# Supplier CRUD Operations
def get_all_suppliers():
    """Get all active suppliers"""
    return HanamanSupplier.query.filter_by(is_active=True).order_by(HanamanSupplier.name).all()

def get_supplier_by_id(supplier_id):
    """Get supplier by ID"""
    return HanamanSupplier.query.get(supplier_id)

def create_supplier(supplier_data):
    """Create a new supplier"""
    try:
        supplier = HanamanSupplier(**supplier_data)
        db.session.add(supplier)
        db.session.commit()
        return supplier
    except Exception as e:
        db.session.rollback()
        print(f"Error creating supplier: {e}")
        return None

def update_supplier(supplier_id, supplier_data):
    """Update existing supplier"""
    try:
        supplier = HanamanSupplier.query.get(supplier_id)
        if supplier:
            for key, value in supplier_data.items():
                if hasattr(supplier, key):
                    setattr(supplier, key, value)
            supplier.updated_at = datetime.utcnow()
            db.session.commit()
            return supplier
        return None
    except Exception as e:
        db.session.rollback()
        print(f"Error updating supplier: {e}")
        return None

def delete_supplier(supplier_id):
    """Soft delete supplier"""
    try:
        supplier = HanamanSupplier.query.get(supplier_id)
        if supplier:
            supplier.is_active = False
            supplier.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting supplier: {e}")
        return False

# Item Template CRUD Operations
def get_all_item_templates():
    """Get all active item templates"""
    return HanamanItemTemplate.query.filter_by(is_active=True).order_by(HanamanItemTemplate.name).all()

def get_item_template_by_id(template_id):
    """Get item template by ID"""
    return HanamanItemTemplate.query.get(template_id)

def create_item_template(template_data):
    """Create a new item template"""
    try:
        template = HanamanItemTemplate(**template_data)
        db.session.add(template)
        db.session.commit()
        return template
    except Exception as e:
        db.session.rollback()
        print(f"Error creating item template: {e}")
        return None

def update_item_template(template_id, template_data):
    """Update existing item template"""
    try:
        template = HanamanItemTemplate.query.get(template_id)
        if template:
            for key, value in template_data.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            template.updated_at = datetime.utcnow()
            db.session.commit()
            return template
        return None
    except Exception as e:
        db.session.rollback()
        print(f"Error updating item template: {e}")
        return None

def delete_item_template(template_id):
    """Soft delete item template"""
    try:
        template = HanamanItemTemplate.query.get(template_id)
        if template:
            template.is_active = False
            template.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting item template: {e}")
        return False

def create_product_from_template(template_id, product_data):
    """Create a product using an item template"""
    try:
        template = HanamanItemTemplate.query.get(template_id)
        if not template:
            return None
        
        # Merge template data with provided data
        merged_data = {
            'name': product_data.get('name', template.name),
            'description': product_data.get('description', template.description),
            'category_id': product_data.get('category_id', template.category_id),
            'unit': product_data.get('unit', template.default_unit),
            'min_stock_level': product_data.get('min_stock_level', template.default_min_stock),
            'max_stock_level': product_data.get('max_stock_level', template.default_max_stock),
            'cost_price': product_data.get('cost_price', template.estimated_cost),
            'current_stock': product_data.get('current_stock', 0),
            'sku': product_data.get('sku', ''),
            'selling_price': product_data.get('selling_price', 0),
            'supplier_name': product_data.get('supplier_name', ''),
            'supplier_contact': product_data.get('supplier_contact', ''),
        }
        
        return create_product(merged_data)
    except Exception as e:
        print(f"Error creating product from template: {e}")
        return None