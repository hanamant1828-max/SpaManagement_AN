"""
Hanaman Inventory Management Models
Simple, clean inventory system with proper CRUD operations
"""
from app import db
from datetime import datetime

class HanamanCategory(db.Model):
    """Product categories for inventory management"""
    __tablename__ = 'hanaman_category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __str__(self):
        return self.name

class HanamanProduct(db.Model):
    """Main inventory product model"""
    __tablename__ = 'hanaman_product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('hanaman_category.id'))
    
    # Stock information
    current_stock = db.Column(db.Float, default=0.0)
    min_stock_level = db.Column(db.Float, default=5.0)
    max_stock_level = db.Column(db.Float, default=100.0)
    unit = db.Column(db.String(20), default='pcs')
    
    # Pricing information
    cost_price = db.Column(db.Float, default=0.0)
    selling_price = db.Column(db.Float, default=0.0)
    
    # Supplier information
    supplier_name = db.Column(db.String(100))
    supplier_contact = db.Column(db.String(100))
    
    # Status and dates
    is_active = db.Column(db.Boolean, default=True)
    expiry_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = db.relationship('HanamanCategory', backref='products')
    
    @property
    def is_low_stock(self):
        """Check if product is low on stock"""
        return self.current_stock <= self.min_stock_level
    
    @property
    def stock_status(self):
        """Get stock status as string"""
        if self.current_stock <= 0:
            return 'out_of_stock'
        elif self.current_stock <= self.min_stock_level:
            return 'low_stock'
        elif self.current_stock >= self.max_stock_level:
            return 'overstocked'
        else:
            return 'normal'
    
    def __str__(self):
        return f"{self.name} ({self.sku})"

class HanamanStockMovement(db.Model):
    """Track all stock movements for audit trail"""
    __tablename__ = 'hanaman_stock_movement'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('hanaman_product.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # 'in', 'out', 'adjust'
    quantity = db.Column(db.Float, nullable=False)
    previous_stock = db.Column(db.Float, nullable=False)
    new_stock = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(200))
    reference_id = db.Column(db.String(100))  # For linking to orders, services, etc.
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('HanamanProduct', backref='stock_movements')
    user = db.relationship('User', backref='hanaman_stock_movements')
    
    def __str__(self):
        return f"{self.product.name} - {self.movement_type}: {self.quantity}"

class HanamanSupplier(db.Model):
    """Supplier management for inventory"""
    __tablename__ = 'hanaman_supplier'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    pincode = db.Column(db.String(10))
    gst_number = db.Column(db.String(20))
    payment_terms = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __str__(self):
        return self.name

class ProductMaster(db.Model):
    """Product Master for spa inventory management"""
    __tablename__ = 'product_master'
    
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('hanaman_category.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('hanaman_supplier.id'), nullable=False)
    unit = db.Column(db.String(20), nullable=False, default='piece')  # ml, liter, piece, etc.
    min_stock = db.Column(db.Integer, nullable=False, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    category = db.relationship('HanamanCategory', backref='product_masters')
    supplier = db.relationship('HanamanSupplier', backref='product_masters')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_products')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_products')
    
    def __str__(self):
        return self.product_name

class HanamanPurchase(db.Model):
    """Purchase transactions for inventory management"""
    __tablename__ = 'hanaman_purchase'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_number = db.Column(db.String(50), unique=True, nullable=False)
    product_master_id = db.Column(db.Integer, db.ForeignKey('product_master.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('hanaman_supplier.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    received_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, received, cancelled
    notes = db.Column(db.Text)
    invoice_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    product_master = db.relationship('ProductMaster', backref='purchases')
    supplier = db.relationship('HanamanSupplier', backref='purchases')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_purchases')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_purchases')
    
    def __str__(self):
        return f"PO-{self.purchase_order_number} - {self.product_master.product_name}"

