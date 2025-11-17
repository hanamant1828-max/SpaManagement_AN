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

    # Relationships
    batches = db.relationship('InventoryBatch', back_populates='location', lazy=True)

    @property
    def total_batches(self):
        """Get total number of batches with stock in this location"""
        return len([b for b in self.batches if (b.qty_available or 0) > 0])

    @property
    def total_stock_value(self):
        """Calculate total stock value for this location based on batches"""
        total_value = 0
        for batch in self.batches:
            if batch.qty_available and batch.unit_cost:
                total_value += float(batch.qty_available) * float(batch.unit_cost)
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
    """Main product catalog - NO STOCK TRACKING (stock exists only at batch level)"""
    __tablename__ = 'inventory_products'

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # Categorization
    category_id = db.Column(db.Integer, db.ForeignKey('inventory_categories.id'))

    # Product details only - NO STOCK FIELDS
    unit_of_measure = db.Column(db.String(20), default='pcs')  # pieces, liters, kg, etc.
    barcode = db.Column(db.String(50))

    # Status tracking
    is_active = db.Column(db.Boolean, default=True)
    is_service_item = db.Column(db.Boolean, default=False)  # Used in services
    is_retail_item = db.Column(db.Boolean, default=False)   # Sold to customers

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = db.relationship('InventoryCategory', back_populates='products')
    batches = db.relationship('InventoryBatch', back_populates='product', lazy=True)

    @property
    def total_stock(self):
        """Get total stock across all batches for this product"""
        return sum(float(batch.qty_available or 0) for batch in self.batches if batch.status == 'active')

    @property
    def stock_status(self):
        """Get stock status based on batch quantities"""
        total = self.total_stock
        if total <= 0:
            return 'out_of_stock'
        elif total <= 10:  # Low stock threshold
            return 'low_stock'
        else:
            return 'in_stock'

    @property
    def batch_count(self):
        """Get number of active batches for this product"""
        return len([b for b in self.batches if b.status == 'active'])

# StockMovement model removed - replaced by InventoryAuditLog for batch-centric tracking



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
    """Batch tracking - CENTRAL element for all stock transactions"""
    __tablename__ = 'inventory_batches'

    id = db.Column(db.Integer, primary_key=True)

    # Core batch identification (CRUD only fields)
    batch_name = db.Column(db.String(100), nullable=False, unique=True)  # Globally unique batch identifier
    created_date = db.Column(db.Date, default=datetime.utcnow().date())  # Creation date (editable)
    mfg_date = db.Column(db.Date, nullable=False)  # Manufacturing date
    expiry_date = db.Column(db.Date, nullable=False)  # Expiry date

    # Product and location assignment (assigned during first transaction)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=True)
    location_id = db.Column(db.String(50), db.ForeignKey('inventory_locations.id'), nullable=True)

    # Stock quantity (updated only through transactions)
    qty_available = db.Column(db.Numeric(10, 2), default=0, nullable=False)

    # Pricing information
    unit_cost = db.Column(db.Numeric(10, 2), default=0)
    selling_price = db.Column(db.Numeric(10, 2))

    # Status tracking
    status = db.Column(db.String(20), default='active')  # active, expired, blocked

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = db.relationship('InventoryProduct', back_populates='batches')
    location = db.relationship('InventoryLocation', back_populates='batches')

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
    def is_near_expiry(self):
        """Check if batch is nearing expiry (within 30 days)"""
        days = self.days_to_expiry
        return days is not None and 0 <= days <= 30

    @property
    def dropdown_display(self):
        """Format for batch dropdown: BatchName (ProductName, Exp: DD-MM-YYYY, Location, Stock: XX)"""
        product_name = self.product.name if self.product else 'Unassigned'
        location_name = self.location.name if self.location else 'Unassigned'
        exp_date = self.expiry_date.strftime('%d-%m-%Y') if self.expiry_date else 'No Date'
        stock = float(self.qty_available or 0)
        return f"{self.batch_name} ({product_name}, Exp: {exp_date}, {location_name}, Stock: {stock})"

# Audit Log Model - Track ALL batch-level stock changes
class InventoryAuditLog(db.Model):
    """Comprehensive audit log for all batch stock changes"""
    __tablename__ = 'inventory_audit_log'

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('inventory_batches.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Action tracking
    action_type = db.Column(db.String(20), nullable=False)  # adjustment_add, adjustment_remove, consumption, transfer_out, transfer_in
    quantity_delta = db.Column(db.Numeric(10, 2), nullable=False)  # +/- change in quantity
    stock_before = db.Column(db.Numeric(10, 2), nullable=False)
    stock_after = db.Column(db.Numeric(10, 2), nullable=False)

    # Reference information
    reference_type = db.Column(db.String(50))  # adjustment, consumption, transfer
    reference_id = db.Column(db.Integer)  # ID of the related transaction record
    notes = db.Column(db.Text)

    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    batch = db.relationship('InventoryBatch', backref='audit_logs')
    product = db.relationship('InventoryProduct', backref='audit_logs')
    user = db.relationship('User', backref='audit_logs')

class InventoryConsumption(db.Model):
    """Track consumption/usage of inventory items"""
    __tablename__ = 'inventory_consumption'

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('inventory_batches.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    issued_to = db.Column(db.String(100))
    reference = db.Column(db.String(100))
    purpose = db.Column(db.String(200))  # Missing column added
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    batch = db.relationship('InventoryBatch', backref='consumption_records')
    user = db.relationship('User', backref='consumption_records')

class InventoryAdjustment(db.Model):
    """Track inventory adjustments (adding/removing stock to/from batches)"""
    __tablename__ = 'inventory_adjustments'

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('inventory_batches.id'), nullable=False)

    # Adjustment details
    adjustment_type = db.Column(db.String(20), nullable=False)  # add, remove
    quantity = db.Column(db.Numeric(10, 2), nullable=False)  # Always positive, direction determined by type
    remarks = db.Column(db.Text, nullable=False)  # Mandatory remarks for all adjustments

    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    batch = db.relationship('InventoryBatch', backref='adjustments')
    user = db.relationship('User', backref='adjustments')


class InventoryTransferItem(db.Model):
    """Items in a transfer"""
    __tablename__ = 'inventory_transfer_items'

    id = db.Column(db.Integer, primary_key=True)
    transfer_id = db.Column(db.Integer, db.ForeignKey('inventory_transfers.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('inventory_batches.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationships
    batch = db.relationship('InventoryBatch')
    product = db.relationship('InventoryProduct')

class InventoryTransfer(db.Model):
    """Track inventory transfers between locations - batch to batch"""
    __tablename__ = 'inventory_transfers'

    id = db.Column(db.Integer, primary_key=True)
    source_batch_id = db.Column(db.Integer, db.ForeignKey('inventory_batches.id'), nullable=False)
    dest_batch_id = db.Column(db.Integer, db.ForeignKey('inventory_batches.id'), nullable=True)  # Created during transfer
    dest_location_id = db.Column(db.String(50), db.ForeignKey('inventory_locations.id'), nullable=False)

    # Transfer details
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    notes = db.Column(db.Text)

    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    source_batch = db.relationship('InventoryBatch', foreign_keys=[source_batch_id], backref='transfers_out')
    dest_batch = db.relationship('InventoryBatch', foreign_keys=[dest_batch_id], backref='transfers_in')
    dest_location = db.relationship('InventoryLocation', backref='transfers_received')
    user = db.relationship('User', backref='transfers')