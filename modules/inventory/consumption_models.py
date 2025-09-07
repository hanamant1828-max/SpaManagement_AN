
"""
Consumption Tracking Models
Models for tracking product consumption and usage
"""

from app import db
from datetime import datetime

class ConsumptionRecord(db.Model):
    """Track product consumption/usage"""
    __tablename__ = 'consumption_records'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product_master.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    purpose = db.Column(db.String(200))  # Service, treatment, cleaning, etc.
    staff_member = db.Column(db.String(100))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    time = db.Column(db.Time, default=datetime.utcnow().time)
    notes = db.Column(db.Text)
    cost_per_unit = db.Column(db.Float, default=0)
    total_cost = db.Column(db.Float, default=0)
    
    # Audit fields
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    product = db.relationship('ProductMaster', backref='consumption_records')
    recorder = db.relationship('User', foreign_keys=[recorded_by], backref='consumption_records_created')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='consumption_records_updated')
    
    def __str__(self):
        return f"{self.product.product_name} - {self.quantity} {self.unit}"

class ConsumptionTemplate(db.Model):
    """Templates for common consumption patterns"""
    __tablename__ = 'consumption_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    template_name = db.Column(db.String(100), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    description = db.Column(db.Text)
    
    # Template items
    template_items = db.relationship('ConsumptionTemplateItem', backref='template', cascade='all, delete-orphan')
    
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __str__(self):
        return self.template_name

class ConsumptionTemplateItem(db.Model):
    """Individual items in consumption templates"""
    __tablename__ = 'consumption_template_items'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('consumption_templates.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product_master.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.String(200))
    
    # Relationships
    product = db.relationship('ProductMaster')
    
    def __str__(self):
        return f"{self.product.product_name} - {self.quantity} {self.unit}"

class StockAdjustment(db.Model):
    """Stock adjustments and corrections"""
    __tablename__ = 'stock_adjustments'
    
    id = db.Column(db.Integer, primary_key=True)
    adjustment_number = db.Column(db.String(50), unique=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product_master.id'), nullable=False)
    adjustment_type = db.Column(db.String(20), nullable=False)  # increase, decrease, correction
    previous_stock = db.Column(db.Float, nullable=False)
    adjustment_quantity = db.Column(db.Float, nullable=False)
    new_stock = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    reference_type = db.Column(db.String(50))  # damage, expiry, loss, found, correction
    reference_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    adjustment_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    
    # Cost tracking
    unit_cost = db.Column(db.Float, default=0)
    total_cost_impact = db.Column(db.Float, default=0)
    
    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    
    # Relationships
    product = db.relationship('ProductMaster', backref='stock_adjustments')
    creator = db.relationship('User', foreign_keys=[created_by], backref='stock_adjustments_created')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='stock_adjustments_approved')
    
    def __str__(self):
        return f"{self.adjustment_number} - {self.product.product_name}"

class InventoryAlert(db.Model):
    """Inventory alerts and notifications"""
    __tablename__ = 'inventory_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(50), nullable=False)  # low_stock, expiry_warning, overstock
    product_id = db.Column(db.Integer, db.ForeignKey('product_master.id'), nullable=False)
    alert_message = db.Column(db.String(500), nullable=False)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    threshold_value = db.Column(db.Float)
    current_value = db.Column(db.Float)
    
    # Alert management
    is_active = db.Column(db.Boolean, default=True)
    is_acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    acknowledged_at = db.Column(db.DateTime)
    auto_resolve = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Relationships
    product = db.relationship('ProductMaster', backref='alerts')
    acknowledger = db.relationship('User', backref='acknowledged_alerts')
    
    def __str__(self):
        return f"{self.alert_type.replace('_', ' ').title()} - {self.product.product_name}"
