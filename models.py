
from datetime import datetime, date, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import json

# Hanaman Inventory Models will be imported at the end to avoid circular imports


# CRUD System Models for Dynamic Configuration
class Role(db.Model):
    """Dynamic roles management"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    users = db.relationship('User', backref='user_role', lazy=True, foreign_keys='User.role_id')
    permissions = db.relationship('RolePermission', backref='role', lazy=True, cascade='all, delete-orphan')

class Permission(db.Model):
    """Dynamic permissions management"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    module = db.Column(db.String(50), nullable=False)  # dashboard, staff, clients, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    role_permissions = db.relationship('RolePermission', backref='permission', lazy=True, cascade='all, delete-orphan')

class RolePermission(db.Model):
    """Many-to-many relationship for roles and permissions"""
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('role_id', 'permission_id'),)

class Category(db.Model):
    """Dynamic categories for services, products, etc."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category_type = db.Column(db.String(50), nullable=False)  # service, product, expense, etc.
    color = db.Column(db.String(7), default='#007bff')  # Hex color for UI
    icon = db.Column(db.String(50), default='fas fa-tag')  # Font Awesome icon
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships (remove the problematic inventory relationship for now)
    services = db.relationship('Service', backref='service_category', lazy=True, foreign_keys='Service.category_id')
    expenses = db.relationship('Expense', backref='expense_category', lazy=True, foreign_keys='Expense.category_id')

class Department(db.Model):
    """Dynamic departments for staff"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    staff = db.relationship('User', backref='staff_department', lazy=True, foreign_keys='User.department_id')
    managed_by = db.relationship('User', backref='managed_departments', lazy=True, foreign_keys='Department.manager_id')

class SystemSetting(db.Model):
    """Dynamic system settings"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    data_type = db.Column(db.String(20), default='string')  # string, integer, float, boolean, json
    category = db.Column(db.String(50), nullable=False)  # business, appearance, notifications, etc.
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)  # Can be accessed by non-admin users
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    # Dynamic role system
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='staff')  # Fallback for compatibility

    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Staff-specific fields
    commission_rate = db.Column(db.Float, default=0.0)
    hourly_rate = db.Column(db.Float, default=0.0)
    employee_id = db.Column(db.String(20), unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    department = db.Column(db.String(50))  # Fallback for compatibility
    hire_date = db.Column(db.Date)

    # 1. Enhanced Staff Profile Details
    profile_photo_url = db.Column(db.String(255))
    gender = db.Column(db.String(10), default='other')
    date_of_birth = db.Column(db.Date)
    date_of_joining = db.Column(db.Date, default=date.today)
    staff_code = db.Column(db.String(20), unique=True)
    notes_bio = db.Column(db.Text)
    designation = db.Column(db.String(100))

    # 2. ID Proofs & Verification
    aadhaar_number = db.Column(db.String(12))
    aadhaar_card_url = db.Column(db.String(255))
    pan_number = db.Column(db.String(10))
    pan_card_url = db.Column(db.String(255))
    verification_status = db.Column(db.Boolean, default=False)

    # 3. Facial Recognition Login
    face_image_url = db.Column(db.String(255))
    facial_encoding = db.Column(db.Text)
    enable_face_checkin = db.Column(db.Boolean, default=True)

    # 4. Work Schedule
    working_days = db.Column(db.String(7), default='1111100')
    shift_start_time = db.Column(db.Time)
    shift_end_time = db.Column(db.Time)
    break_time = db.Column(db.String(50))
    weekly_off_days = db.Column(db.String(20))

    # 5. Performance & Commission
    commission_percentage = db.Column(db.Float, default=0.0)
    fixed_commission = db.Column(db.Float, default=0.0)
    total_revenue_generated = db.Column(db.Float, default=0.0)

    # 6. Activity & Status
    last_login = db.Column(db.DateTime)
    last_service_performed = db.Column(db.DateTime)

    # Performance tracking
    total_sales = db.Column(db.Float, default=0.0)
    total_clients_served = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default=0.0)

    # Availability and preferences
    work_schedule = db.Column(db.Text)  # JSON for weekly schedule
    specialties = db.Column(db.Text)  # JSON for service specialties

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
        # Support both dynamic and legacy role systems
        if self.user_role:
            return self.user_role.name == role
        return self.role == role

    def can_access(self, resource):
        # Admin users have full access - shortcut for efficiency
        if self.role == 'admin' or (self.user_role and self.user_role.name == 'admin'):
            return True

        # Dynamic permissions from role-permission system
        if self.user_role:
            user_permissions = [rp.permission.name for rp in self.user_role.permissions if rp.permission.is_active]
            # Check for 'all' permission or specific resource permissions
            if 'all' in user_permissions:
                return True
            # Check for specific resource permissions (e.g., 'clients_view', 'clients_create')
            resource_permissions = [p for p in user_permissions if p.startswith(resource + '_')]
            return len(resource_permissions) > 0 or resource in user_permissions

        # Fallback to legacy permissions
        permissions = {
            'admin': ['all'],
            'manager': ['dashboard', 'bookings', 'clients', 'staff', 'billing', 'inventory', 'expenses', 'reports'],
            'staff': ['dashboard', 'bookings', 'clients'],
            'cashier': ['dashboard', 'bookings', 'billing']
        }
        user_role_permissions = permissions.get(self.role, [])
        return 'all' in user_role_permissions or resource in user_role_permissions

    def get_role_name(self):
        """Get the role name from dynamic system or fallback"""
        if self.user_role:
            return self.user_role.name
        return self.role

class Customer(db.Model):
    __tablename__ = 'client'  # Keep table name for backward compatibility

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

    # Customer preferences and notes
    preferences = db.Column(db.Text)
    allergies = db.Column(db.Text)
    notes = db.Column(db.Text)
    face_encoding = db.Column(db.Text)  # Store face encoding as JSON string
    face_image_url = db.Column(db.String(255))  # Store face image path

    # Loyalty status
    loyalty_points = db.Column(db.Integer, default=0)
    is_vip = db.Column(db.Boolean, default=False)

    # Communication preferences
    preferred_communication = db.Column(db.String(20), default='email')  # email, sms, whatsapp
    marketing_consent = db.Column(db.Boolean, default=True)
    reminder_preferences = db.Column(db.Text)  # JSON for reminder settings

    # Advanced customer tracking
    referral_source = db.Column(db.String(100))
    lifetime_value = db.Column(db.Float, default=0.0)
    last_no_show = db.Column(db.DateTime)
    no_show_count = db.Column(db.Integer, default=0)

    # Relationships
    appointments = db.relationship('Appointment', backref='client', lazy=True)
    packages = db.relationship('CustomerPackage', backref='customer', lazy=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def status(self):
        if not self.is_active:
            return 'Inactive'
        elif self.last_visit and (datetime.utcnow() - self.last_visit).days > 90:
            return 'Inactive Customer'
        elif self.total_visits >= 10:
            return 'Loyal Customer'
        else:
            return 'Regular Customer'

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.Column(db.String(50), nullable=False)  # Fallback for compatibility
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    appointments = db.relationship('Appointment', backref='service', lazy=True)
    package_services = db.relationship('PackageService', backref='service', lazy=True)
    inventory_items = db.relationship('ServiceInventoryItem', backref='service', lazy=True)

    def deduct_inventory_for_service(self):
        """Deduct inventory items when this service is performed"""
        movements = []
        for service_item in self.inventory_items:
            if service_item.inventory_item.can_fulfill_quantity(service_item.quantity_per_service):
                # Create stock movement record
                movement = StockMovement(
                    inventory_id=service_item.inventory_id,
                    movement_type='service_use',
                    quantity=-service_item.quantity_per_service,  # Negative for outflow
                    unit=service_item.unit,
                    reference_type='service',
                    reference_id=self.id,
                    created_by=1  # System user, should be current user in real implementation
                )
                movements.append(movement)

                # Update inventory stock
                service_item.inventory_item.current_stock -= service_item.quantity_per_service

        return movements

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)  # Keep FK reference to table name
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
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, partial
    is_paid = db.Column(db.Boolean, default=False)
    inventory_deducted = db.Column(db.Boolean, default=False)  # Track if inventory was deducted

    # Relationships - use existing backref from User model
    # staff relationship is already created by User.appointments backref='assigned_staff'

    def process_inventory_deduction(self):
        """Process inventory deduction when appointment is completed and billed"""
        if not self.inventory_deducted and self.status == 'completed' and self.is_paid:
            movements = self.service.deduct_inventory_for_service()
            if movements:
                from app import db
                for movement in movements:
                    db.session.add(movement)
                self.inventory_deducted = True
                db.session.commit()
                return True
        return False

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    package_type = db.Column(db.String(50), default='regular')  # regular, prepaid, membership, student_offer, kitty_party
    duration_months = db.Column(db.Integer, nullable=False)  # 3, 6, 12 months
    validity_days = db.Column(db.Integer, nullable=False, default=90)  # Validity in days
    total_sessions = db.Column(db.Integer, nullable=False, default=1)  # Total sessions in package
    total_price = db.Column(db.Float, nullable=False)
    credit_amount = db.Column(db.Float, default=0.0)  # For prepaid packages - amount credited
    discount_percentage = db.Column(db.Float, default=0.0)
    student_discount = db.Column(db.Float, default=0.0)  # Additional student discount
    min_guests = db.Column(db.Integer, default=1)  # For kitty party packages
    membership_benefits = db.Column(db.Text)  # JSON string for membership benefits
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # New fields for unlimited sessions and date ranges
    has_unlimited_sessions = db.Column(db.Boolean, default=False)  # True for unlimited packages
    start_date = db.Column(db.Date)  # Optional start date for package validity
    end_date = db.Column(db.Date)  # Optional end date for package validity

    # Relationships
    services = db.relationship('PackageService', backref='package', lazy=True)
    customer_packages = db.relationship('CustomerPackage', backref='package', lazy=True)

    @property
    def services_included(self):
        """Get formatted list of services included"""
        return [ps.service.name for ps in self.services if ps.service]

class PackageService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    sessions_included = db.Column(db.Integer, nullable=False)
    service_discount = db.Column(db.Float, default=0.0)  # Individual service discount percentage
    original_price = db.Column(db.Float, nullable=False)  # Original service price
    discounted_price = db.Column(db.Float, nullable=False)  # Final discounted price

    # New field for unlimited sessions per service
    is_unlimited = db.Column(db.Boolean, default=False)  # True for unlimited sessions

class CustomerPackage(db.Model):
    __tablename__ = 'client_package'  # Keep table name for backward compatibility

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)  # Keep FK reference to table name
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=False)
    sessions_used = db.Column(db.Integer, default=0)
    total_sessions = db.Column(db.Integer, nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    auto_renewed = db.Column(db.Boolean, default=False)
    renewal_count = db.Column(db.Integer, default=0)

    # Service-wise session tracking
    sessions_remaining = db.relationship('CustomerPackageSession', backref='customer_package', lazy=True)

class CustomerPackageSession(db.Model):
    """Track remaining sessions for each service in a customer's package"""
    __tablename__ = 'client_package_session'  # Keep table name for backward compatibility

    id = db.Column(db.Integer, primary_key=True)
    client_package_id = db.Column(db.Integer, db.ForeignKey('client_package.id'), nullable=False)  # Keep FK reference to table name
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    sessions_total = db.Column(db.Integer, nullable=False)
    sessions_used = db.Column(db.Integer, default=0)
    is_unlimited = db.Column(db.Boolean, default=False)  # True for unlimited sessions

    @property
    def sessions_remaining(self):
        if self.is_unlimited:
            return float('inf')  # Unlimited sessions
        return max(0, self.sessions_total - self.sessions_used)

    # Relationships
    service = db.relationship('Service', backref='customer_sessions')

# 📦 Professional Inventory Management System
# Built from scratch following the comprehensive plan

class InventoryCategory(db.Model):
    """Enhanced category master with full audit trail"""
    __tablename__ = 'inventory_category'
    
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(50))
    updated_by = db.Column(db.String(50))

class InventorySupplier(db.Model):
    """Enhanced supplier master with complete business details"""
    __tablename__ = 'inventory_supplier'
    
    supplier_id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(150), nullable=False, index=True)
    supplier_code = db.Column(db.String(50), unique=True, index=True)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(50))
    tax_id = db.Column(db.String(50))
    payment_terms = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True, index=True)
    rating = db.Column(db.Float, default=5.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(50))
    updated_by = db.Column(db.String(50))

class InventoryLocation(db.Model):
    """Multi-location inventory management"""
    __tablename__ = 'inventory_location'
    
    location_id = db.Column(db.Integer, primary_key=True)
    location_code = db.Column(db.String(20), unique=True, nullable=False)
    location_name = db.Column(db.String(100), nullable=False)
    location_type = db.Column(db.String(20), default='SECTION')  # WAREHOUSE, ROOM, SHELF, SECTION
    parent_location_id = db.Column(db.Integer, db.ForeignKey('inventory_location.location_id'))
    capacity = db.Column(db.Integer)
    temperature_controlled = db.Column(db.Boolean, default=False)
    security_level = db.Column(db.String(10), default='LOW')  # LOW, MEDIUM, HIGH
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Self-referencing relationship for parent-child locations
    children = db.relationship('InventoryLocation', backref=db.backref('parent', remote_side=[location_id]))

class InventoryProduct(db.Model):
    """Enhanced inventory master with professional features"""
    __tablename__ = 'inventory_product'
    
    product_id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('inventory_category.category_id'), index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('inventory_supplier.supplier_id'), index=True)
    unit = db.Column(db.String(20), default='pcs')
    unit_cost = db.Column(db.Float, default=0.0)
    selling_price = db.Column(db.Float, default=0.0)
    reorder_level = db.Column(db.Integer, default=0)
    max_stock_level = db.Column(db.Integer)
    storage_location = db.Column(db.String(100))
    shelf_life_days = db.Column(db.Integer)
    is_batch_tracked = db.Column(db.Boolean, default=False)
    is_expiry_tracked = db.Column(db.Boolean, default=False)
    barcode = db.Column(db.String(100), index=True)
    image_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(50))
    updated_by = db.Column(db.String(50))
    
    # Legacy compatibility fields
    current_stock = db.Column(db.Float, default=0.0)  # For existing code compatibility
    min_stock_level = db.Column(db.Float, default=0.0)  # Alias for reorder_level
    cost_price = db.Column(db.Float, default=0.0)  # Alias for unit_cost
    
    # Relationships
    category = db.relationship('InventoryCategory', backref='products')
    supplier = db.relationship('InventorySupplier', backref='products')
    
    @property
    def id(self):
        """Legacy compatibility - return product_id as id"""
        return self.product_id
    
    def can_fulfill_quantity(self, quantity):
        """Calculate if we have enough stock to fulfill a quantity"""
        # Calculate current stock from approved transactions
        approved_in = sum(t.quantity for t in self.transactions 
                         if t.status == 'APPROVED' and t.transaction_type == 'IN')
        approved_out = sum(t.quantity for t in self.transactions 
                          if t.status == 'APPROVED' and t.transaction_type == 'OUT')
        calculated_stock = approved_in - approved_out
        
        # Update current_stock field for compatibility
        self.current_stock = calculated_stock
        
        return calculated_stock >= quantity

class InventoryTransaction(db.Model):
    """Advanced inventory transactions with approval workflow"""
    __tablename__ = 'inventory_transaction'
    
    transaction_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_product.product_id'), index=True)
    transaction_type = db.Column(db.String(10), nullable=False, index=True)  # IN, OUT, ADJUST, TRANSFER, DAMAGED, EXPIRED, RETURNED
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float, default=0.0)
    total_value = db.Column(db.Float, default=0.0)
    batch_number = db.Column(db.String(50), index=True)
    lot_number = db.Column(db.String(50))
    expiry_date = db.Column(db.Date)
    reference_document = db.Column(db.String(100))
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    notes = db.Column(db.Text)
    location_from = db.Column(db.String(100))
    location_to = db.Column(db.String(100))
    created_by = db.Column(db.String(50), index=True)
    approved_by = db.Column(db.String(50))
    approved_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='PENDING', index=True)  # PENDING, APPROVED, REJECTED, CANCELLED
    
    # Relationship
    product = db.relationship('InventoryProduct', backref='transactions')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-calculate total value
        if self.unit_cost and self.quantity:
            self.total_value = self.quantity * self.unit_cost

class InventoryAlert(db.Model):
    """Advanced stock alerts system"""
    __tablename__ = 'inventory_alert'
    
    alert_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_product.product_id'), index=True)
    alert_type = db.Column(db.String(20), nullable=False, index=True)  # LOW_STOCK, OUT_OF_STOCK, EXPIRY_SOON, EXPIRED, OVERSTOCK, DAMAGED
    alert_message = db.Column(db.Text)
    threshold_value = db.Column(db.Integer)
    current_value = db.Column(db.Integer)
    alert_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_resolved = db.Column(db.Boolean, default=False, index=True)
    resolved_by = db.Column(db.String(50))
    resolved_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)
    
    # Relationship
    product = db.relationship('InventoryProduct', backref='alerts')

class InventoryStockCount(db.Model):
    """Physical stock count management"""
    __tablename__ = 'inventory_stock_count'
    
    count_id = db.Column(db.Integer, primary_key=True)
    count_reference = db.Column(db.String(50), unique=True, nullable=False)
    count_date = db.Column(db.Date, index=True)
    location = db.Column(db.String(100), index=True)
    count_type = db.Column(db.String(20), default='FULL')  # FULL, CYCLE, SPOT, LOCATION
    status = db.Column(db.String(20), default='PLANNED', index=True)  # PLANNED, IN_PROGRESS, COMPLETED, CANCELLED
    started_by = db.Column(db.String(50))
    started_at = db.Column(db.DateTime)
    completed_by = db.Column(db.String(50))
    completed_at = db.Column(db.DateTime)
    total_products = db.Column(db.Integer, default=0)
    counted_products = db.Column(db.Integer, default=0)
    products_with_variance = db.Column(db.Integer, default=0)
    total_variance_value = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InventoryReorderRule(db.Model):
    """Automated reordering system"""
    __tablename__ = 'inventory_reorder_rule'
    
    rule_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_product.product_id'), unique=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('inventory_supplier.supplier_id'))
    reorder_point = db.Column(db.Integer, nullable=False)
    reorder_quantity = db.Column(db.Integer, nullable=False)
    max_stock_level = db.Column(db.Integer)
    lead_time_days = db.Column(db.Integer, default=7)
    is_active = db.Column(db.Boolean, default=True)
    auto_reorder_enabled = db.Column(db.Boolean, default=False)
    last_reorder_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('InventoryProduct', backref='reorder_rule', uselist=False)
    supplier = db.relationship('InventorySupplier', backref='reorder_rules')

# Legacy compatibility models for existing code
class StockMovement(db.Model):
    """Track all stock movements - legacy compatibility"""
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory_product.product_id'))
    movement_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='pcs')
    reference_type = db.Column(db.String(50))
    reference_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    inventory = db.relationship('InventoryProduct', backref='movements')

class InventoryItem(db.Model):
    """Simple inventory items - legacy compatibility"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    current_stock = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(20), default='pcs')
    cost_price = db.Column(db.Float, default=0.0)
    selling_price = db.Column(db.Float, default=0.0)
    reorder_level = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def can_fulfill_quantity(self, quantity):
        return self.current_stock >= quantity

class ServiceInventoryItem(db.Model):
    """Link services to inventory items"""
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory_product.product_id'))
    quantity_per_service = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='pcs')
    
    inventory_item = db.relationship('InventoryProduct', backref='service_items')

class ConsumptionEntry(db.Model):
    """Track inventory consumption"""
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory_product.product_id'))
    quantity_used = db.Column(db.Float, nullable=False)
    used_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    inventory_item = db.relationship('InventoryProduct', backref='consumption_entries')

class UsageDuration(db.Model):
    """Track usage duration"""
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory_product.product_id'))
    usage_days = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    inventory_item = db.relationship('InventoryProduct', backref='usage_durations')

class InventoryAdjustment(db.Model):
    """Inventory adjustments"""
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory_product.product_id'))
    adjustment_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    inventory_item = db.relationship('InventoryProduct', backref='adjustments')

# Legacy aliases for existing code
Inventory = InventoryProduct
InventoryMaster = InventoryProduct
CategoryMaster = InventoryCategory
SupplierMaster = InventorySupplier
InventoryTransaction = InventoryTransaction

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.Column(db.String(50), nullable=False)  # Fallback for compatibility
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
    customer = db.relationship('Customer', backref='invoices')
    appointment = db.relationship('Appointment', backref='invoice', uselist=False)

# Enhanced Billing Models for Integrated Billing System
class EnhancedInvoice(db.Model):
    """Enhanced invoice model supporting services, packages, subscriptions, and inventory"""
    __tablename__ = 'enhanced_invoice'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(20), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    invoice_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    
    # Billing Components
    services_subtotal = db.Column(db.Float, default=0.0)
    packages_deduction = db.Column(db.Float, default=0.0)
    subscription_deduction = db.Column(db.Float, default=0.0)
    inventory_subtotal = db.Column(db.Float, default=0.0)
    
    # Calculations
    gross_subtotal = db.Column(db.Float, default=0.0)  # Before deductions
    total_deductions = db.Column(db.Float, default=0.0)  # Package + Subscription
    net_subtotal = db.Column(db.Float, default=0.0)  # After deductions
    
    # Final amounts
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    tips_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Payment tracking
    payment_status = db.Column(db.String(20), default='pending')  # pending, partial, paid, overdue
    payment_methods = db.Column(db.Text)  # JSON for multiple payment methods
    amount_paid = db.Column(db.Float, default=0.0)
    balance_due = db.Column(db.Float, default=0.0)
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer', backref='enhanced_invoices')
    invoice_items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')
    invoice_payments = db.relationship('InvoicePayment', backref='invoice', lazy=True, cascade='all, delete-orphan')

class InvoiceItem(db.Model):
    """Individual items on an invoice (services, inventory items, etc.)"""
    __tablename__ = 'invoice_item'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('enhanced_invoice.id'), nullable=False)
    
    # Item details
    item_type = db.Column(db.String(20), nullable=False)  # service, package_service, inventory, subscription
    item_id = db.Column(db.Integer)  # ID of service/inventory item
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))  # For service items
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))  # For package-related items
    
    # Descriptions
    item_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Pricing
    quantity = db.Column(db.Float, default=1.0)
    unit_price = db.Column(db.Float, default=0.0)
    original_amount = db.Column(db.Float, default=0.0)  # Before any deductions
    deduction_amount = db.Column(db.Float, default=0.0)  # Package/subscription deduction
    final_amount = db.Column(db.Float, default=0.0)  # Amount actually charged
    
    # Status indicators
    is_package_deduction = db.Column(db.Boolean, default=False)
    is_subscription_deduction = db.Column(db.Boolean, default=False)
    is_extra_charge = db.Column(db.Boolean, default=False)  # Beyond package/subscription
    
    # Relationships
    appointment = db.relationship('Appointment', backref='invoice_items')
    package = db.relationship('Package', backref='invoice_items')

class InvoicePayment(db.Model):
    """Multiple payment records for a single invoice supporting mixed payment methods"""
    __tablename__ = 'invoice_payment'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('enhanced_invoice.id'), nullable=False)
    
    payment_method = db.Column(db.String(20), nullable=False)  # cash, card, upi, wallet
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Payment method specific details
    card_last4 = db.Column(db.String(4))  # Last 4 digits of card
    transaction_id = db.Column(db.String(100))  # UPI/online transaction ID
    reference_number = db.Column(db.String(100))
    
    notes = db.Column(db.Text)
    processed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    processor = db.relationship('User', backref='processed_payments')

class StaffSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    # Relationship
    staff = db.relationship('User', backref='schedules')

# Advanced Models for Real-World Operations

class Review(db.Model):
    """Customer reviews and ratings"""
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    staff = db.relationship('User', backref='reviews')
    service = db.relationship('Service', backref='reviews')
    appointment = db.relationship('Appointment', backref='review', uselist=False)

class Communication(db.Model):
    """Track all communications with clients"""
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # email, sms, whatsapp, call, in_person
    subject = db.Column(db.String(200))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, sent, delivered, failed
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationships
    creator = db.relationship('User', backref='communications')

class Commission(db.Model):
    """Track staff commissions and payroll"""
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    service_amount = db.Column(db.Float, nullable=False)
    commission_rate = db.Column(db.Float, nullable=False)
    commission_amount = db.Column(db.Float, nullable=False)
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    staff = db.relationship('User', backref='commissions')
    appointment = db.relationship('Appointment', backref='commission', uselist=False)

# ProductSale model removed - fresh implementation coming

class Promotion(db.Model):
    """Marketing promotions and discounts"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    discount_type = db.Column(db.String(20), nullable=False)  # percentage, fixed_amount
    discount_value = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    usage_limit = db.Column(db.Integer)
    times_used = db.Column(db.Integer, default=0)
    applicable_services = db.Column(db.Text)  # JSON for service IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Waitlist(db.Model):
    """Client waitlist for fully booked times"""
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    preferred_date = db.Column(db.Date, nullable=False)
    preferred_time = db.Column(db.Time)
    is_flexible = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='waiting')  # waiting, contacted, booked, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    # Relationships
    customer = db.relationship('Customer', backref='waitlist_entries')
    service = db.relationship('Service', backref='waitlist_entries')
    staff = db.relationship('User', backref='waitlist_requests')

class RecurringAppointment(db.Model):
    """Recurring appointment templates"""
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # weekly, biweekly, monthly
    day_of_week = db.Column(db.Integer)  # 0=Monday, 6=Sunday
    time_slot = db.Column(db.Time, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    customer = db.relationship('Customer', backref='recurring_appointments')
    service = db.relationship('Service', backref='recurring_bookings')
    staff = db.relationship('User', backref='recurring_schedule')

class Location(db.Model):
    """Support for multiple locations/branches"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean, default=True)
    operating_hours = db.Column(db.Text)  # JSON for weekly hours
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    manager = db.relationship('User', backref='managed_locations')

class BusinessSettings(db.Model):
    """Global business settings and preferences"""
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(50), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    data_type = db.Column(db.String(20), default='string')  # string, integer, float, boolean, json
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationships
    updater = db.relationship('User', backref='setting_updates')



class Attendance(db.Model):
    """Staff attendance tracking"""
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=False)
    check_out_time = db.Column(db.DateTime)
    check_in_method = db.Column(db.String(20), default='manual')  # manual, facial, biometric
    total_hours = db.Column(db.Float)
    date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    staff = db.relationship('User', backref='attendance_records')

class Leave(db.Model):
    """Staff leave management"""
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)  # sick, casual, emergency
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationships
    staff = db.relationship('User', backref='leave_requests', foreign_keys=[staff_id])
    approver = db.relationship('User', foreign_keys=[approved_by])

class StaffService(db.Model):
    """Staff-Service assignment with skill levels"""
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    skill_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, expert
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    staff = db.relationship('User', backref='staff_services')
    service = db.relationship('Service', backref='service_staff')

class StaffPerformance(db.Model):
    """Monthly performance tracking"""
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    services_completed = db.Column(db.Integer, default=0)
    revenue_generated = db.Column(db.Float, default=0.0)
    client_ratings_avg = db.Column(db.Float, default=0.0)
    attendance_percentage = db.Column(db.Float, default=0.0)
    commission_earned = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    staff = db.relationship('User', backref='performance_records')

# Import Hanaman Inventory Models after all other models are defined
from modules.hanamantinventory.models import HanamanProduct, HanamanCategory, HanamanStockMovement, HanamanSupplier, ProductMaster
