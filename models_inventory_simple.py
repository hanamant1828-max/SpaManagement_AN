# Simplified Inventory Management Models
# Two main modules: CRUD Operations and Consumption Tracking

from datetime import datetime
from app import db

class InventoryItem(db.Model):
    """Simple inventory items for CRUD operations"""
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Item Information
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(50))
    
    # Stock Information
    current_stock = db.Column(db.Float, default=0.0, nullable=False)
    reorder_level = db.Column(db.Float, default=10.0)
    maximum_stock = db.Column(db.Float, default=100.0)
    
    # Pricing
    unit_price = db.Column(db.Float, default=0.0)
    cost_price = db.Column(db.Float, default=0.0)
    
    # Supplier Information
    supplier_name = db.Column(db.String(100))
    supplier_contact = db.Column(db.String(100))
    
    # Location and Storage
    location = db.Column(db.String(100))
    warehouse_section = db.Column(db.String(50))
    
    # Timestamps
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    transactions = db.relationship('StockTransaction', backref='item', lazy=True)
    
    @property
    def is_low_stock(self):
        """Check if item is below reorder level"""
        return self.current_stock <= self.reorder_level
    
    @property
    def is_out_of_stock(self):
        """Check if item is out of stock"""
        return self.current_stock <= 0
    
    @property
    def stock_value(self):
        """Calculate current stock value"""
        return self.current_stock * self.cost_price

class StockTransaction(db.Model):
    """Consumption tracking - all stock movements and transactions"""
    __tablename__ = 'stock_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Item Reference
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    
    # Transaction Details
    transaction_type = db.Column(db.String(20), nullable=False)  # Sale, Return, Adjustment, Transfer, Purchase
    quantity_changed = db.Column(db.Float, nullable=False)  # Positive for in, negative for out
    remaining_balance = db.Column(db.Float, nullable=False)  # Stock after transaction
    
    # Transaction Information
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    department = db.Column(db.String(50))
    
    # Reference Information
    reference_number = db.Column(db.String(100))  # Invoice ID, Order ID, etc.
    invoice_id = db.Column(db.String(50))
    order_id = db.Column(db.String(50))
    
    # Reason and Notes
    reason = db.Column(db.String(200))
    notes = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', backref='stock_transactions')
    
    @property
    def transaction_display(self):
        """User-friendly transaction display"""
        if self.quantity_changed > 0:
            return f"+{self.quantity_changed} ({self.transaction_type})"
        else:
            return f"{self.quantity_changed} ({self.transaction_type})"

class LowStockAlert(db.Model):
    """Track low stock alerts and notifications"""
    __tablename__ = 'low_stock_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    alert_date = db.Column(db.DateTime, default=datetime.utcnow)
    current_stock = db.Column(db.Float)
    reorder_level = db.Column(db.Float)
    is_acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    acknowledged_at = db.Column(db.DateTime)
    
    # Relationships
    item = db.relationship('InventoryItem', backref='alerts')
    acknowledged_by_user = db.relationship('User', backref='acknowledged_alerts')

class ConsumptionReport(db.Model):
    """Generated consumption reports"""
    __tablename__ = 'consumption_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    report_name = db.Column(db.String(100), nullable=False)
    report_type = db.Column(db.String(50))  # daily, weekly, monthly, custom
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    generated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_items = db.Column(db.Integer)
    total_transactions = db.Column(db.Integer)
    total_value = db.Column(db.Float)
    
    # Relationships
    generated_by_user = db.relationship('User', backref='generated_reports')