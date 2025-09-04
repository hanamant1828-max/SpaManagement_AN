"""
Hanaman Inventory Database Queries
Clean CRUD operations for inventory management
"""
from app import db
from .models import HanamanProduct, HanamanCategory, HanamanStockMovement, HanamanSupplier, ProductMaster, HanamanPurchase
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

# Product Master CRUD Operations
def get_all_product_masters():
    """Get all active product masters with joined data"""
    return db.session.query(ProductMaster, HanamanCategory, HanamanSupplier).join(
        HanamanCategory, ProductMaster.category_id == HanamanCategory.id
    ).join(
        HanamanSupplier, ProductMaster.supplier_id == HanamanSupplier.id
    ).filter(ProductMaster.is_active == True).order_by(ProductMaster.product_name).all()

def get_product_master_by_id(product_id):
    """Get product master by ID"""
    return ProductMaster.query.get(product_id)

def create_product_master(product_data):
    """Create a new product master"""
    try:
        product = ProductMaster(
            product_name=product_data['product_name'],
            category_id=product_data['category_id'],
            supplier_id=product_data['supplier_id'],
            unit=product_data['unit'],
            min_stock=product_data['min_stock'],
            created_by=current_user.id if current_user.is_authenticated else 1
        )
        db.session.add(product)
        db.session.commit()
        return product
    except Exception as e:
        db.session.rollback()
        print(f"Error creating product master: {e}")
        return None

def update_product_master(product_id, product_data):
    """Update existing product master"""
    try:
        product = ProductMaster.query.get(product_id)
        if product:
            product.product_name = product_data['product_name']
            product.category_id = product_data['category_id']
            product.supplier_id = product_data['supplier_id']
            product.unit = product_data['unit']
            product.min_stock = product_data['min_stock']
            product.updated_by = current_user.id if current_user.is_authenticated else 1
            product.updated_at = datetime.utcnow()
            db.session.commit()
            return product
        return None
    except Exception as e:
        db.session.rollback()
        print(f"Error updating product master: {e}")
        return None

def delete_product_master(product_id):
    """Soft delete product master"""
    try:
        product = ProductMaster.query.get(product_id)
        if product:
            product.is_active = False
            product.updated_by = current_user.id if current_user.is_authenticated else 1
            product.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting product master: {e}")
        return False

# Purchase CRUD Operations
def get_all_purchases():
    """Get all active purchases with joined data"""
    from .models import HanamanPurchase, ProductMaster, HanamanSupplier
    return db.session.query(HanamanPurchase, ProductMaster, HanamanSupplier).join(
        ProductMaster, HanamanPurchase.product_master_id == ProductMaster.id
    ).join(
        HanamanSupplier, HanamanPurchase.supplier_id == HanamanSupplier.id
    ).filter(HanamanPurchase.is_active == True).order_by(HanamanPurchase.purchase_date.desc()).all()

def get_purchase_by_id(purchase_id):
    """Get purchase by ID"""
    from .models import HanamanPurchase
    return HanamanPurchase.query.get(purchase_id)

def create_purchase(purchase_data):
    """Create a new purchase"""
    from .models import HanamanPurchase
    try:
        # Generate purchase order number if not provided
        if not purchase_data.get('purchase_order_number'):
            import uuid
            purchase_data['purchase_order_number'] = f"PO-{str(uuid.uuid4())[:8].upper()}"
        
        purchase = HanamanPurchase(
            purchase_order_number=purchase_data['purchase_order_number'],
            product_master_id=purchase_data['product_master_id'],
            supplier_id=purchase_data['supplier_id'],
            quantity=purchase_data['quantity'],
            unit_price=purchase_data['unit_price'],
            total_amount=purchase_data['quantity'] * purchase_data['unit_price'],
            purchase_date=purchase_data['purchase_date'],
            received_date=purchase_data.get('received_date'),
            status=purchase_data.get('status', 'pending'),
            notes=purchase_data.get('notes', ''),
            invoice_number=purchase_data.get('invoice_number', ''),
            created_by=current_user.id if current_user.is_authenticated else 1
        )
        db.session.add(purchase)
        db.session.commit()
        return purchase
    except Exception as e:
        db.session.rollback()
        print(f"Error creating purchase: {e}")
        return None

def update_purchase(purchase_id, purchase_data):
    """Update existing purchase"""
    from .models import HanamanPurchase
    try:
        purchase = HanamanPurchase.query.get(purchase_id)
        if purchase:
            purchase.product_master_id = purchase_data['product_master_id']
            purchase.supplier_id = purchase_data['supplier_id']
            purchase.quantity = purchase_data['quantity']
            purchase.unit_price = purchase_data['unit_price']
            purchase.total_amount = purchase_data['quantity'] * purchase_data['unit_price']
            purchase.purchase_date = purchase_data['purchase_date']
            purchase.received_date = purchase_data.get('received_date')
            purchase.status = purchase_data.get('status', 'pending')
            purchase.notes = purchase_data.get('notes', '')
            purchase.invoice_number = purchase_data.get('invoice_number', '')
            purchase.updated_by = current_user.id if current_user.is_authenticated else 1
            purchase.updated_at = datetime.utcnow()
            db.session.commit()
            return purchase
        return None
    except Exception as e:
        db.session.rollback()
        print(f"Error updating purchase: {e}")
        return None

def delete_purchase(purchase_id):
    """Soft delete purchase"""
    from .models import HanamanPurchase
    try:
        purchase = HanamanPurchase.query.get(purchase_id)
        if purchase:
            purchase.is_active = False
            purchase.updated_by = current_user.id if current_user.is_authenticated else 1
            purchase.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting purchase: {e}")
        return False

# Transaction CRUD Operations
def get_all_transactions():
    """Get all active transactions with joined data"""
    from .models import HanamanTransaction, ProductMaster
    return db.session.query(HanamanTransaction, ProductMaster).join(
        ProductMaster, HanamanTransaction.product_master_id == ProductMaster.id
    ).filter(HanamanTransaction.is_active == True).order_by(HanamanTransaction.transaction_date.desc()).all()

def get_transaction_by_id(transaction_id):
    """Get transaction by ID"""
    from .models import HanamanTransaction
    return HanamanTransaction.query.get(transaction_id)

def create_transaction(transaction_data):
    """Create a new transaction"""
    from .models import HanamanTransaction
    try:
        # Generate transaction number if not provided
        if not transaction_data.get('transaction_number'):
            import uuid
            transaction_data['transaction_number'] = f"TXN-{str(uuid.uuid4())[:8].upper()}"
        
        transaction = HanamanTransaction(
            transaction_number=transaction_data['transaction_number'],
            product_master_id=transaction_data['product_master_id'],
            transaction_type=transaction_data['transaction_type'],
            quantity=transaction_data['quantity'],
            unit_cost=transaction_data.get('unit_cost', 0.0),
            total_cost=transaction_data['quantity'] * transaction_data.get('unit_cost', 0.0),
            transaction_date=transaction_data['transaction_date'],
            reason=transaction_data['reason'],
            reference_type=transaction_data.get('reference_type', ''),
            reference_id=transaction_data.get('reference_id', ''),
            reference_name=transaction_data.get('reference_name', ''),
            notes=transaction_data.get('notes', ''),
            created_by=current_user.id if current_user.is_authenticated else 1
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction
    except Exception as e:
        db.session.rollback()
        print(f"Error creating transaction: {e}")
        return None

def update_transaction(transaction_id, transaction_data):
    """Update existing transaction"""
    from .models import HanamanTransaction
    try:
        transaction = HanamanTransaction.query.get(transaction_id)
        if transaction:
            transaction.product_master_id = transaction_data['product_master_id']
            transaction.transaction_type = transaction_data['transaction_type']
            transaction.quantity = transaction_data['quantity']
            transaction.unit_cost = transaction_data.get('unit_cost', 0.0)
            transaction.total_cost = transaction_data['quantity'] * transaction_data.get('unit_cost', 0.0)
            transaction.transaction_date = transaction_data['transaction_date']
            transaction.reason = transaction_data['reason']
            transaction.reference_type = transaction_data.get('reference_type', '')
            transaction.reference_id = transaction_data.get('reference_id', '')
            transaction.reference_name = transaction_data.get('reference_name', '')
            transaction.notes = transaction_data.get('notes', '')
            transaction.updated_by = current_user.id if current_user.is_authenticated else 1
            transaction.updated_at = datetime.utcnow()
            db.session.commit()
            return transaction
        return None
    except Exception as e:
        db.session.rollback()
        print(f"Error updating transaction: {e}")
        return None

def delete_transaction(transaction_id):
    """Soft delete transaction"""
    from .models import HanamanTransaction
    try:
        transaction = HanamanTransaction.query.get(transaction_id)
        if transaction:
            transaction.is_active = False
            transaction.updated_by = current_user.id if current_user.is_authenticated else 1
            transaction.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting transaction: {e}")
        return False

def get_transactions_by_product(product_id, days=30):
    """Get transactions for a specific product"""
    from .models import HanamanTransaction
    from datetime import date, timedelta
    
    start_date = date.today() - timedelta(days=days)
    return HanamanTransaction.query.filter(
        HanamanTransaction.product_master_id == product_id,
        HanamanTransaction.transaction_date >= start_date,
        HanamanTransaction.is_active == True
    ).order_by(HanamanTransaction.transaction_date.desc()).all()

def get_transactions_by_type(transaction_type, days=30):
    """Get transactions by type"""
    from .models import HanamanTransaction
    from datetime import date, timedelta
    
    start_date = date.today() - timedelta(days=days)
    return HanamanTransaction.query.filter(
        HanamanTransaction.transaction_type == transaction_type,
        HanamanTransaction.transaction_date >= start_date,
        HanamanTransaction.is_active == True
    ).order_by(HanamanTransaction.transaction_date.desc()).all()

def get_transaction_summary(days=30):
    """Get transaction summary statistics"""
    from .models import HanamanTransaction
    from datetime import date, timedelta
    
    start_date = date.today() - timedelta(days=days)
    
    total_transactions = HanamanTransaction.query.filter(
        HanamanTransaction.transaction_date >= start_date,
        HanamanTransaction.is_active == True
    ).count()
    
    total_cost = db.session.query(
        db.func.sum(HanamanTransaction.total_cost)
    ).filter(
        HanamanTransaction.transaction_date >= start_date,
        HanamanTransaction.is_active == True
    ).scalar() or 0
    
    consumption_count = HanamanTransaction.query.filter(
        HanamanTransaction.transaction_type == 'consumption',
        HanamanTransaction.transaction_date >= start_date,
        HanamanTransaction.is_active == True
    ).count()
    
    usage_count = HanamanTransaction.query.filter(
        HanamanTransaction.transaction_type == 'usage',
        HanamanTransaction.transaction_date >= start_date,
        HanamanTransaction.is_active == True
    ).count()
    
    return {
        'total_transactions': total_transactions,
        'total_cost': round(total_cost, 2),
        'consumption_count': consumption_count,
        'usage_count': usage_count
    }

