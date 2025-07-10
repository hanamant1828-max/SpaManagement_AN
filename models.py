from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='staff')  # admin, manager, staff, cashier
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Staff-specific fields
    commission_rate = db.Column(db.Float, default=0.0)
    hourly_rate = db.Column(db.Float, default=0.0)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='assigned_staff', lazy=True)
    expenses = db.relationship('Expense', backref='created_by_user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_role(self, role):
        return self.role == role

    def can_access(self, resource):
        # Define role-based access control
        permissions = {
            'admin': ['all'],
            'manager': ['dashboard', 'bookings', 'clients', 'staff', 'billing', 'inventory', 'expenses', 'reports'],
            'staff': ['dashboard', 'bookings', 'clients'],
            'cashier': ['dashboard', 'bookings', 'billing']
        }
        return 'all' in permissions.get(self.role, []) or resource in permissions.get(self.role, [])

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True)
    phone = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_visit = db.Column(db.DateTime)
    total_visits = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    
    # Client preferences and notes
    preferences = db.Column(db.Text)
    allergies = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Loyalty status
    loyalty_points = db.Column(db.Integer, default=0)
    is_vip = db.Column(db.Boolean, default=False)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='client', lazy=True)
    packages = db.relationship('ClientPackage', backref='client', lazy=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def status(self):
        if not self.is_active:
            return 'Inactive'
        elif self.last_visit and (datetime.utcnow() - self.last_visit).days > 90:
            return 'Inactive Client'
        elif self.total_visits >= 10:
            return 'Loyal Client'
        else:
            return 'Regular Client'

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='service', lazy=True)
    package_services = db.relationship('PackageService', backref='service', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, confirmed, in_progress, completed, cancelled, no_show
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Billing
    amount = db.Column(db.Float)
    discount = db.Column(db.Float, default=0.0)
    tips = db.Column(db.Float, default=0.0)
    is_paid = db.Column(db.Boolean, default=False)

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration_months = db.Column(db.Integer, nullable=False)  # 3, 6, 12 months
    total_price = db.Column(db.Float, nullable=False)
    discount_percentage = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    services = db.relationship('PackageService', backref='package', lazy=True)
    client_packages = db.relationship('ClientPackage', backref='package', lazy=True)

class PackageService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    sessions_included = db.Column(db.Integer, nullable=False)

class ClientPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=False)
    sessions_used = db.Column(db.Integer, default=0)
    total_sessions = db.Column(db.Integer, nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    current_stock = db.Column(db.Integer, default=0)
    min_stock_level = db.Column(db.Integer, default=5)
    unit_price = db.Column(db.Float, default=0.0)
    supplier_name = db.Column(db.String(100))
    supplier_contact = db.Column(db.String(100))
    expiry_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def is_low_stock(self):
        return self.current_stock <= self.min_stock_level

    @property
    def is_expiring_soon(self):
        if not self.expiry_date:
            return False
        days_until_expiry = (self.expiry_date - date.today()).days
        return days_until_expiry <= 30

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # utilities, supplies, maintenance, etc.
    expense_date = db.Column(db.Date, nullable=False, default=date.today)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receipt_number = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(20), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    invoice_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    subtotal = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    tips_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, overdue
    payment_method = db.Column(db.String(20))  # cash, card, online
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    client = db.relationship('Client', backref='invoices')
    appointment = db.relationship('Appointment', backref='invoice', uselist=False)

class StaffSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    # Relationship
    staff = db.relationship('User', backref='schedules')
