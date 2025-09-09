"""
Inventory Management Models
"""
from datetime import datetime
from app import db
from sqlalchemy import func

class InventoryCategory(db.Model):
    """Product categories for better organization"""
    __tablename__ = 'inventory_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    color_code = db.Column(db.String(7), default='#007bff')  # For UI theming
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    products = db.relationship('InventoryProduct', back_populates='category', lazy=True)

class Supplier(db.Model):
    """Supplier management with comprehensive details"""
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100), default='United States')
    
    # Business details
    tax_id = db.Column(db.String(50))
    payment_terms = db.Column(db.String(50), default='Net 30')
    credit_limit = db.Column(db.Numeric(12, 2), default=0)
    
    # Performance tracking
    rating = db.Column(db.Integer, default=5)  # 1-5 stars
    total_orders = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Numeric(12, 2), default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = db.relationship('InventoryProduct', back_populates='supplier', lazy=True)
    purchase_orders = db.relationship('PurchaseOrder', back_populates='supplier', lazy=True)

class InventoryProduct(db.Model):
    """Main product catalog with comprehensive tracking"""
    __tablename__ = 'inventory_products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Categorization
    category_id = db.Column(db.Integer, db.ForeignKey('inventory_categories.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    
    # Inventory tracking
    current_stock = db.Column(db.Numeric(10, 2), default=0)
    reserved_stock = db.Column(db.Numeric(10, 2), default=0)  # Stock allocated but not used
    available_stock = db.Column(db.Numeric(10, 2), default=0)  # current - reserved
    
    # Stock levels
    min_stock_level = db.Column(db.Numeric(10, 2), default=10)
    max_stock_level = db.Column(db.Numeric(10, 2), default=100)
    reorder_point = db.Column(db.Numeric(10, 2), default=20)
    
    # Pricing
    cost_price = db.Column(db.Numeric(10, 2), default=0)  # Purchase cost
    selling_price = db.Column(db.Numeric(10, 2), default=0)  # Retail price
    
    # Product details
    unit_of_measure = db.Column(db.String(20), default='pcs')  # pieces, liters, kg, etc.
    barcode = db.Column(db.String(50))
    location = db.Column(db.String(100))  # Storage location in spa
    
    # Status tracking
    is_active = db.Column(db.Boolean, default=True)
    is_service_item = db.Column(db.Boolean, default=False)  # Used in services
    is_retail_item = db.Column(db.Boolean, default=False)   # Sold to customers
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = db.relationship('InventoryCategory', back_populates='products')
    supplier = db.relationship('Supplier', back_populates='products')
    stock_movements = db.relationship('StockMovement', back_populates='product', lazy=True)
    order_items = db.relationship('PurchaseOrderItem', back_populates='product', lazy=True)
    
    @property
    def stock_status(self):
        """Get stock status for alerts"""
        current = self.current_stock if self.current_stock is not None else 0
        min_level = self.min_stock_level if self.min_stock_level is not None else 0
        reorder = self.reorder_point if self.reorder_point is not None else 0
        
        if current <= 0:
            return 'out_of_stock'
        elif current <= min_level:
            return 'low_stock'
        elif current <= reorder:
            return 'reorder_needed'
        else:
            return 'in_stock'
    
    @property
    def stock_value(self):
        """Calculate total stock value"""
        current = self.current_stock if self.current_stock is not None else 0
        cost = self.cost_price if self.cost_price is not None else 0
        return float(current * cost)
    
    def update_available_stock(self):
        """Update available stock calculation"""
        # Ensure values are not None
        current = self.current_stock if self.current_stock is not None else 0
        reserved = self.reserved_stock if self.reserved_stock is not None else 0
        self.available_stock = current - reserved

class StockMovement(db.Model):
    """Track all stock movements for audit trail"""
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    
    # Movement details
    movement_type = db.Column(db.String(20), nullable=False)  # in, out, adjustment, transfer
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2), default=0)
    
    # Stock levels at time of movement
    stock_before = db.Column(db.Numeric(10, 2), nullable=False)
    stock_after = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Reference and reason
    reference_type = db.Column(db.String(50))  # purchase_order, service, sale, adjustment
    reference_id = db.Column(db.Integer)  # ID of the related record
    reason = db.Column(db.String(200))
    notes = db.Column(db.Text)
    
    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('InventoryProduct', back_populates='stock_movements')
    user = db.relationship('User', backref='stock_movements')

class PurchaseOrder(db.Model):
    """Purchase orders to suppliers"""
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    
    # Order details
    order_date = db.Column(db.Date, default=datetime.utcnow)
    expected_delivery = db.Column(db.Date)
    delivery_address = db.Column(db.Text)
    
    # Financial
    subtotal = db.Column(db.Numeric(12, 2), default=0)
    tax_amount = db.Column(db.Numeric(12, 2), default=0)
    shipping_cost = db.Column(db.Numeric(12, 2), default=0)
    total_amount = db.Column(db.Numeric(12, 2), default=0)
    
    # Status tracking
    status = db.Column(db.String(20), default='draft')  # draft, sent, confirmed, received, cancelled
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, overdue
    
    # Notes and terms
    notes = db.Column(db.Text)
    terms_and_conditions = db.Column(db.Text)
    
    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier = db.relationship('Supplier', back_populates='purchase_orders')
    items = db.relationship('PurchaseOrderItem', back_populates='purchase_order', cascade='all, delete-orphan')
    user = db.relationship('User', backref='purchase_orders')
    
    def calculate_totals(self):
        """Calculate order totals"""
        self.subtotal = sum(item.total_cost for item in self.items)
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost

class PurchaseOrderItem(db.Model):
    """Items in a purchase order"""
    __tablename__ = 'purchase_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    
    # Order details
    quantity_ordered = db.Column(db.Numeric(10, 2), nullable=False)
    quantity_received = db.Column(db.Numeric(10, 2), default=0)
    unit_cost = db.Column(db.Numeric(10, 2), nullable=False)
    total_cost = db.Column(db.Numeric(12, 2), nullable=False)
    
    # Receiving tracking
    received_date = db.Column(db.Date)
    is_fully_received = db.Column(db.Boolean, default=False)
    
    # Relationships
    purchase_order = db.relationship('PurchaseOrder', back_populates='items')
    product = db.relationship('InventoryProduct', back_populates='order_items')
    
    @property
    def pending_quantity(self):
        """Calculate pending quantity to receive"""
        return self.quantity_ordered - self.quantity_received

class InventoryAlert(db.Model):
    """System alerts for inventory management"""
    __tablename__ = 'inventory_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    
    alert_type = db.Column(db.String(20), nullable=False)  # low_stock, out_of_stock, overstock, expiry
    message = db.Column(db.String(200), nullable=False)
    severity = db.Column(db.String(10), default='medium')  # low, medium, high, critical
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('InventoryProduct', backref='alerts')
    resolver = db.relationship('User', backref='resolved_alerts')

class InventoryConsumption(db.Model):
    """Track item usage and issuance for inventory consumption"""
    __tablename__ = 'inventory_consumption'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    
    # Consumption details
    consumption_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    quantity_used = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Issuance information
    issued_to = db.Column(db.String(200), nullable=False)  # department/project/person
    reference_doc_no = db.Column(db.String(100))  # Reference or document number
    notes = db.Column(db.Text)
    
    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = db.relationship('InventoryProduct', backref='consumption_records')
    user = db.relationship('User', backref='consumption_records')
    
    @property
    def unit_of_measure(self):
        """Get unit of measure from the product"""
        return self.product.unit_of_measure if self.product else 'pcs'