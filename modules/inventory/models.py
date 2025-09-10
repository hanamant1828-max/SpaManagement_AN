"""
Inventory Management Models
"""
from datetime import datetime
from app import db
from sqlalchemy import func

class InventoryLocation(db.Model):
    """Inventory storage locations (branches, warehouses, rooms)"""
    __tablename__ = 'inventory_locations'
    
    id = db.Column(db.String(50), primary_key=True)  # Use string ID for compatibility
    name = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String(20), nullable=False)  # branch, warehouse, room
    address = db.Column(db.Text)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='active')  # active, inactive
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def total_products(self):
        """Get total number of products with stock in this location"""
        # Use the location field instead of location_stock for now
        products_in_location = InventoryProduct.query.filter_by(location=self.name).all()
        return len([p for p in products_in_location if (p.current_stock or 0) > 0])
    
    @property
    def total_stock_value(self):
        """Calculate total stock value for this location"""
        # Use the location field instead of location_stock for now
        products_in_location = InventoryProduct.query.filter_by(location=self.name).all()
        total_value = 0
        for product in products_in_location:
            stock = float(product.current_stock or 0)
            cost = float(product.cost_price or 0)
            total_value += stock * cost
        return total_value


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



class InventoryProduct(db.Model):
    """Main product catalog with comprehensive tracking"""
    __tablename__ = 'inventory_products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Categorization
    category_id = db.Column(db.Integer, db.ForeignKey('inventory_categories.id'))
    
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
    
    # Location-based stock tracking (JSON field) - Temporarily removed for database compatibility
    # location_stock = db.Column(db.JSON, default=dict)  # {"location_id": quantity}
    
    # Status tracking
    is_active = db.Column(db.Boolean, default=True)
    is_service_item = db.Column(db.Boolean, default=False)  # Used in services
    is_retail_item = db.Column(db.Boolean, default=False)   # Sold to customers
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = db.relationship('InventoryCategory', back_populates='products')
    stock_movements = db.relationship('StockMovement', back_populates='product', lazy=True)
    
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
        # Ensure values are not None and convert to float to handle decimal/float type mixing
        current = float(self.current_stock if self.current_stock is not None else 0)
        reserved = float(self.reserved_stock if self.reserved_stock is not None else 0)
        self.available_stock = current - reserved

class StockMovement(db.Model):
    """Track all stock movements for audit trail"""
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('inventory_batches.id'))  # Optional batch tracking
    
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
    batch = db.relationship('InventoryBatch', backref='stock_movements')
    user = db.relationship('User', backref='stock_movements')



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

class InventoryBatch(db.Model):
    """Batch tracking for inventory products with expiry management"""
    __tablename__ = 'inventory_batches'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    location_id = db.Column(db.String(50), db.ForeignKey('inventory_locations.id'), nullable=False)
    
    # Batch identification
    batch_name = db.Column(db.String(100), nullable=False)  # User-friendly batch identifier
    
    # Batch details
    created_date = db.Column(db.Date, default=datetime.utcnow().date())  # Creation date
    mfg_date = db.Column(db.Date, nullable=False)  # Manufacturing date
    expiry_date = db.Column(db.Date, nullable=False)  # Expiry date
    qty_available = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2), default=0)
    selling_price = db.Column(db.Numeric(10, 2))  # Optional selling price override
    
    # Status tracking
    status = db.Column(db.String(20), default='active')  # active, expired, blocked
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = db.relationship('InventoryProduct', backref='batches')
    location = db.relationship('InventoryLocation', backref='batches')
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('product_id', 'batch_name', name='uq_product_batch_name'),
    )
    
    @property
    def is_expired(self):
        """Check if batch is expired"""
        if not self.expiry_date:
            return False
        return self.expiry_date < datetime.utcnow().date()
    
    @property
    def days_to_expiry(self):
        """Get days until expiry"""
        if not self.expiry_date:
            return None
        delta = self.expiry_date - datetime.utcnow().date()
        return delta.days
    
    @property
    def batch_value(self):
        """Calculate total batch value"""
        return float(self.qty_available or 0) * float(self.unit_cost or 0)

class InventoryConsumption(db.Model):
    """Track item usage and issuance for inventory consumption"""
    __tablename__ = 'inventory_consumption'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('inventory_batches.id'))  # Optional batch tracking
    
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
    batch = db.relationship('InventoryBatch', backref='consumption_records')
    user = db.relationship('User', backref='consumption_records')
    
    @property
    def unit_of_measure(self):
        """Get unit of measure from the product"""
        return self.product.unit_of_measure if self.product else 'pcs'