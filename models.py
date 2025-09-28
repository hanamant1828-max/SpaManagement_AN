from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import json

# Inventory models are imported separately to avoid circular imports


# CRUD System Models for Dynamic Configuration
class Role(db.Model):
    """Dynamic roles management"""
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    users = db.relationship('User', backref='dynamic_role', lazy=True, foreign_keys='User.role_id')
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

    # Relationships
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
    email = db.Column(db.String(120), unique=False, nullable=True, index=True)
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
        """Set password with proper hashing"""
        if password:
            self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash with fallback options"""
        if not password:
            return False

        # Primary method: check against password_hash
        if self.password_hash:
            try:
                return check_password_hash(self.password_hash, password)
            except Exception as e:
                print(f"Password hash check error: {e}")

        return False

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @full_name.setter
    def full_name(self, value):
        """Allow setting full name by splitting into first and last name"""
        if value and ' ' in value:
            names = value.split(' ', 1)
            self.first_name = names[0]
            self.last_name = names[1] if len(names) > 1 else ''
        elif value:
            self.first_name = value
            self.last_name = ''

    def has_role(self, role):
        # Support both dynamic and legacy role systems
        if self.role_id and hasattr(self, 'dynamic_role') and self.dynamic_role:
            return self.dynamic_role.name == role
        return self.role == role

    def can_access(self, resource):
        """Check if user can access a specific resource based on role permissions"""
        if not self.is_active:
            return False

        # Allow billing access for all active users (spa staff need to create bills)
        if resource == 'billing':
            return True

        # Super admin has access to everything
        if self.has_role('admin') or self.has_role('super_admin') or self.role == 'admin':
            return True

        # Resource to permission mapping
        resource_permissions = {
            'dashboard': ['dashboard_view'],
            'inventory': ['inventory_view', 'inventory_create', 'inventory_edit'],
            'staff': ['staff_view', 'staff_create', 'staff_edit'],
            'clients': ['clients_view', 'clients_create', 'clients_edit'],
            'services': ['services_view', 'services_create', 'services_edit'],
            'packages': ['packages_view', 'packages_create', 'packages_edit'],
            'reports': ['reports_view'],
            'appointments': ['appointments_view', 'appointments_create', 'appointments_edit'],
            'expenses': ['expenses_view', 'expenses_create', 'expenses_edit'],
            'settings': ['settings_view', 'settings_edit']
        }

        # Get required permissions for resource
        required_permissions = resource_permissions.get(resource, [])
        if not required_permissions:
            # If resource not defined, check basic role access
            return self.role in ['manager', 'staff'] or (hasattr(self, 'dynamic_role') and self.dynamic_role and self.dynamic_role.is_active)

        # Check dynamic role system first
        if self.role_id:
            try:
                user_role = Role.query.get(self.role_id)
                if user_role and user_role.is_active:
                    user_permissions = []
                    for role_permission in user_role.permissions:
                        if role_permission.permission.is_active:
                            user_permissions.append(role_permission.permission.name)

                    # Check if user has any of the required permissions
                    return any(perm in user_permissions for perm in required_permissions)
            except:
                pass  # Fall back to legacy system

        # Fallback to legacy role system
        role_access_map = {
            'admin': True,  # Admin can access everything
            'manager': resource in ['dashboard', 'inventory', 'staff', 'clients',
                                   'services', 'packages', 'reports', 'appointments', 'expenses'],
            'staff': resource in ['dashboard', 'clients', 'appointments', 'services'],
            'receptionist': resource in ['dashboard', 'clients', 'appointments']
        }

        return role_access_map.get(self.role, False)

    def __repr__(self):
        return f'<User {self.username}>'

class ShiftManagement(db.Model):
    """One entry per staff member for shift management"""
    __tablename__ = 'shift_management'

    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)  # One per staff
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    staff = db.relationship('User', backref='shift_management')
    shift_logs = db.relationship('ShiftLogs', backref='shift_management', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ShiftManagement {self.staff_id}: {self.from_date} to {self.to_date}>'

class ShiftLogs(db.Model):
    """Individual shift log entries for each date"""
    __tablename__ = 'shift_logs'

    id = db.Column(db.Integer, primary_key=True)
    shift_management_id = db.Column(db.Integer, db.ForeignKey('shift_management.id', ondelete='CASCADE'), nullable=False)
    individual_date = db.Column(db.Date, nullable=False)
    shift_start_time = db.Column(db.Time, nullable=False)
    shift_end_time = db.Column(db.Time, nullable=False)
    break_start_time = db.Column(db.Time, nullable=True)
    break_end_time = db.Column(db.Time, nullable=True)
    status = db.Column(db.Enum('scheduled', 'absent', 'holiday', 'completed', name='shift_status'), default='scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_break_time_display(self):
        """Get formatted break time display"""
        if self.break_start_time and self.break_end_time:
            start_12h = self.break_start_time.strftime('%I:%M %p')
            end_12h = self.break_end_time.strftime('%I:%M %p')
            # Calculate break duration in minutes
            start_minutes = self.break_start_time.hour * 60 + self.break_start_time.minute
            end_minutes = self.break_end_time.hour * 60 + self.break_end_time.minute
            duration = end_minutes - start_minutes
            return f"{duration} minutes ({start_12h} - {end_12h})"
        else:
            return "No break"

    def __repr__(self):
        return f'<ShiftLogs {self.individual_date} - Management {self.shift_management_id}>'

class Customer(db.Model):
    __tablename__ = 'client'  # Keep table name for backward compatibility

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
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
    # Note: Customer package assignments will be handled separately with new package system

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @full_name.setter
    def full_name(self, value):
        """Allow setting full name by splitting into first and last name"""
        if value and ' ' in value:
            names = value.split(' ', 1)
            self.first_name = names[0]
            self.last_name = names[1] if len(names) > 1 else ''
        elif value:
            self.first_name = value
            self.last_name = ''

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
    # Note: Service-package relationships are handled differently in new package system

    def deduct_inventory_for_service(self):
        """Deduct inventory items when this service is performed"""
        movements = []
        try:
            # Check if inventory_items relationship exists
            if hasattr(self, 'inventory_items') and self.inventory_items:
                for service_item in self.inventory_items:
                    # Create a basic audit log entry instead
                    from modules.inventory.models import InventoryAuditLog
                    audit_entry = InventoryAuditLog(
                        batch_id=service_item.batch_id if hasattr(service_item, 'batch_id') else None,
                        product_id=service_item.inventory_id,
                        user_id=None,  # Will be set by calling code with proper user context
                        action_type='service_use',
                        quantity_delta=-service_item.quantity_per_service,  # Negative for outflow
                        stock_before=0,  # Will be updated in actual implementation
                        stock_after=0,   # Will be updated in actual implementation
                        reference_type='service',
                        reference_id=self.id,
                        notes=f'Used in service: {self.name}'
                    )
                    movements.append(audit_entry)
        except Exception as e:
            print(f"Error processing inventory deduction: {e}")

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
            if hasattr(self, 'service') and self.service:
                movements = self.service.deduct_inventory_for_service()
                if movements:
                    from app import db
                    for movement in movements:
                        db.session.add(movement)
                    self.inventory_deducted = True
                    db.session.commit()
                    return True
        return False

# NEW PACKAGE MANAGEMENT SYSTEM - SEPARATE TABLES FOR EACH TYPE

class PrepaidPackage(db.Model):
    """Prepaid credit packages - Pay X, Get Y"""
    __tablename__ = "prepaid_packages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    actual_price = db.Column(db.Float, nullable=False)   # Price customer pays
    after_value = db.Column(db.Float, nullable=False)    # Value they get
    benefit_percent = db.Column(db.Float, nullable=False)
    validity_months = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def money_saved(self):
        return self.after_value - self.actual_price

class ServicePackage(db.Model):
    """Service packages - Pay for X services, get Y total"""
    __tablename__ = "service_packages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)  # Nullable for template creation
    pay_for = db.Column(db.Integer, nullable=False)
    total_services = db.Column(db.Integer, nullable=False)
    benefit_percent = db.Column(db.Float, nullable=False)
    validity_months = db.Column(db.Integer, nullable=True)
    choose_on_assign = db.Column(db.Boolean, default=True)  # Flag for service selection during assignment
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    service = db.relationship('Service', backref='service_packages')

    @property
    def free_services(self):
        return self.total_services - self.pay_for

class Membership(db.Model):
    """Membership packages"""
    __tablename__ = "memberships"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    validity_months = db.Column(db.Integer, nullable=False)  # Usually 12
    services_included = db.Column(db.Text, nullable=True)  # Keep for backward compatibility
    description = db.Column(db.Text, nullable=True)  # Description field for membership details
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    membership_services = db.relationship('MembershipService', backref='membership', lazy=True, cascade='all, delete-orphan')

class StudentOffer(db.Model):
    """Student discount offers"""
    __tablename__ = "student_offers"

    id = db.Column(db.Integer, primary_key=True)
    discount_percentage = db.Column(db.Float, nullable=False)  # 1-100
    valid_from = db.Column(db.Date, nullable=False)
    valid_to = db.Column(db.Date, nullable=False)
    valid_days = db.Column(db.String(50), default="Mon-Fri")  # e.g. "Mon-Fri"
    conditions = db.Column(db.Text, default="Valid with Student ID")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student_offer_services = db.relationship('StudentOfferService', backref='student_offer', lazy=True, cascade='all, delete-orphan')

class StudentOfferService(db.Model):
    """Many-to-many relationship for student offers and services"""
    __tablename__ = 'student_offer_services'

    id = db.Column(db.Integer, primary_key=True)
    offer_id = db.Column(db.Integer, db.ForeignKey('student_offers.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    service = db.relationship('Service', backref='student_offer_services')

    __table_args__ = (db.UniqueConstraint('offer_id', 'service_id'),)

class YearlyMembership(db.Model):
    """Yearly membership packages"""
    __tablename__ = "yearly_memberships"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    discount_percent = db.Column(db.Float, nullable=False)
    validity_months = db.Column(db.Integer, default=12)
    extra_benefits = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class KittyParty(db.Model):
    """Kitty party packages"""
    __tablename__ = "kitty_parties"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    after_value = db.Column(db.Float, nullable=True)
    min_guests = db.Column(db.Integer, nullable=False)
    valid_from = db.Column(db.Date, nullable=True)
    valid_to = db.Column(db.Date, nullable=True)
    conditions = db.Column(db.Text, nullable=True)
    services_included = db.Column(db.Text, nullable=True)  # Keep for backward compatibility
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    kittyparty_services = db.relationship('KittyPartyService', backref='kittyparty', lazy=True, cascade='all, delete-orphan')

# Package-Service Relationship Models
class MembershipService(db.Model):
    """Many-to-many relationship for memberships and services"""
    __tablename__ = 'membership_services'

    id = db.Column(db.Integer, primary_key=True)
    membership_id = db.Column(db.Integer, db.ForeignKey('memberships.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    service = db.relationship('Service', backref='membership_services')

    __table_args__ = (db.UniqueConstraint('membership_id', 'service_id'),)

class KittyPartyService(db.Model):
    """Many-to-many relationship for kitty parties and services"""
    __tablename__ = 'kittyparty_services'

    id = db.Column(db.Integer, primary_key=True)
    kittyparty_id = db.Column(db.Integer, db.ForeignKey('kitty_parties.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    service = db.relationship('Service', backref='kittyparty_services')

    __table_args__ = (db.UniqueConstraint('kittyparty_id', 'service_id'),)

# Inventory Management Models are located in modules/inventory/models.py

# ========================================
# NEW PACKAGE ASSIGNMENT SYSTEM
# ========================================

class ServicePackageAssignment(db.Model):
    """Customer package assignments for new package system"""
    __tablename__ = 'service_package_assignment'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

    # Package reference
    package_type = db.Column(db.String(20), nullable=False)  # prepaid, service_package, membership, etc.
    package_reference_id = db.Column(db.Integer, nullable=False)  # ID in respective package table

    # Service assignment (for service packages)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)

    # Assignment details
    assigned_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_on = db.Column(db.DateTime, nullable=True)
    price_paid = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='active')  # active, completed, expired, cancelled
    notes = db.Column(db.Text)

    # Service package specific fields
    total_sessions = db.Column(db.Integer, default=0)
    used_sessions = db.Column(db.Integer, default=0)
    remaining_sessions = db.Column(db.Integer, default=0)

    # Prepaid package specific fields
    credit_amount = db.Column(db.Float, default=0)
    used_credit = db.Column(db.Float, default=0)
    remaining_credit = db.Column(db.Float, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = db.relationship('Customer', backref='service_package_assignments')
    service = db.relationship('Service', backref='package_assignments')
    usage_logs = db.relationship('PackageAssignmentUsage', backref='assignment', lazy=True, cascade='all, delete-orphan')

    def get_package_template(self):
        """Get the package template based on type and reference ID"""
        if self.package_type == 'prepaid':
            return PrepaidPackage.query.get(self.package_reference_id)
        elif self.package_type == 'service_package':
            return ServicePackage.query.get(self.package_reference_id)
        elif self.package_type == 'membership':
            return Membership.query.get(self.package_reference_id)
        elif self.package_type == 'student_offer':
            return StudentOffer.query.get(self.package_reference_id)
        elif self.package_type == 'yearly_membership':
            return YearlyMembership.query.get(self.package_reference_id)
        elif self.package_type == 'kitty_party':
            return KittyParty.query.get(self.package_reference_id)
        return None

    def is_expired(self):
        """Check if assignment is expired"""
        if self.expires_on and self.expires_on < datetime.utcnow():
            return True
        return False

    def auto_update_status(self):
        """Auto-update status based on usage and expiry"""
        if self.is_expired():
            self.status = 'expired'
        elif self.package_type == 'service_package' and self.remaining_sessions <= 0:
            self.status = 'completed'
        elif self.package_type == 'prepaid' and self.remaining_credit <= 0:
            self.status = 'completed'
        return self.status

    def __repr__(self):
        return f'<ServicePackageAssignment {self.id}: Customer {self.customer_id} - {self.package_type} {self.package_reference_id}>'


class PackageAssignmentUsage(db.Model):
    """Usage log for package assignments"""
    __tablename__ = 'package_assignment_usage'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('service_package_assignment.id'), nullable=False)
    usage_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Usage details
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)
    sessions_used = db.Column(db.Integer, default=0)
    credit_used = db.Column(db.Float, default=0)

    # Staff and appointment references
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=True)

    change_type = db.Column(db.String(20), default='use')  # use, refund, adjust
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    service = db.relationship('Service', backref='assignment_usage_logs')
    staff = db.relationship('User', backref='assignment_staff_usage_logs')
    appointment = db.relationship('Appointment', backref='assignment_appointment_usage_logs')

    def __repr__(self):
        return f'<PackageAssignmentUsage {self.id}: Assignment {self.assignment_id} - {self.change_type}>'

# ========================================
# CUSTOMER PACKAGE MANAGEMENT MODELS
# ========================================

class PackageTemplate(db.Model):
    """Template for package definitions"""
    __tablename__ = 'package_template'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    pkg_type = db.Column(db.Enum('session', 'value', name='package_type'), default='session')
    price = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    template_items = db.relationship('PackageTemplateItem', backref='package_template', lazy=True, cascade='all, delete-orphan')
    customer_packages = db.relationship('CustomerPackage', backref='package_template', lazy=True)

    def __repr__(self):
        return f'<PackageTemplate {self.name}>'


class PackageTemplateItem(db.Model):
    """Components per service for package templates"""
    __tablename__ = 'package_template_item'

    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package_template.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)  # For value-type packages, omit items
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    service = db.relationship('Service', backref='package_template_items')

    def __repr__(self):
        return f'<PackageTemplateItem Package:{self.package_id} Service:{self.service_id} Qty:{self.qty}>'


class CustomerPackage(db.Model):
    """Customer package assignments"""
    __tablename__ = 'customer_package'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)  # FK to client table
    package_id = db.Column(db.Integer, db.ForeignKey('package_template.id'), nullable=False)
    assigned_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_on = db.Column(db.DateTime, nullable=True)
    price_paid = db.Column(db.Numeric(10, 2), nullable=False)
    discount = db.Column(db.Numeric(10, 2), default=0)
    status = db.Column(db.Enum('active', 'completed', 'expired', 'paused', name='package_status'), default='active')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = db.relationship('Customer', backref='customer_packages')  # Customer model uses 'client' table
    package_items = db.relationship('CustomerPackageItem', backref='customer_package', lazy=True, cascade='all, delete-orphan')
    usage_logs = db.relationship('PackageUsage', backref='customer_package', lazy=True)

    # Indexes
    __table_args__ = (
        db.Index('ix_customer_package_customer_status', 'customer_id', 'status'),
    )

    def get_total_services(self):
        """Get total services count"""
        return sum(item.total_qty for item in self.package_items)

    def get_used_services(self):
        """Get used services count"""
        return sum(item.used_qty for item in self.package_items)

    def get_remaining_services(self):
        """Get remaining services count"""
        return sum(item.get_remaining_qty() for item in self.package_items)

    def get_usage_percentage(self):
        """Get usage percentage"""
        total = self.get_total_services()
        if total == 0:
            return 0
        used = self.get_used_services()
        return round((used / total) * 100, 2)

    def is_expired(self):
        """Check if package is expired"""
        if self.expires_on and self.expires_on < datetime.utcnow():
            return True
        return False

    def auto_update_status(self):
        """Auto-update status based on usage and expiry"""
        if self.is_expired():
            self.status = 'expired'
        elif self.get_remaining_services() == 0:
            self.status = 'completed'
        return self.status

    def __repr__(self):
        return f'<CustomerPackage {self.id}: Customer {self.customer_id} - Package {self.package_id}>'


class CustomerPackageItem(db.Model):
    """Per-service balances for customer packages"""
    __tablename__ = 'customer_package_item'

    id = db.Column(db.Integer, primary_key=True)
    customer_package_id = db.Column(db.Integer, db.ForeignKey('customer_package.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    total_qty = db.Column(db.Integer, nullable=False)
    used_qty = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    service = db.relationship('Service', backref='customer_package_items')
    usage_logs = db.relationship('PackageUsage', backref='customer_package_item', lazy=True)

    # Indexes
    __table_args__ = (
        db.Index('ix_customer_package_item_package', 'customer_package_id'),
        db.Index('ix_customer_package_item_service', 'service_id'),
    )

    def get_remaining_qty(self):
        """Get remaining quantity (computed)"""
        return max(self.total_qty - self.used_qty, 0)

    def can_use(self, qty):
        """Check if can use specified quantity"""
        return self.get_remaining_qty() >= qty

    def use_services(self, qty):
        """Use services and update used_qty"""
        if self.can_use(qty):
            self.used_qty += qty
            self.updated_at = datetime.utcnow()
            return True
        return False

    def refund_services(self, qty):
        """Refund services and update used_qty"""
        if self.used_qty >= qty:
            self.used_qty -= qty
            self.updated_at = datetime.utcnow()
            return True
        return False

    def adjust_services(self, qty):
        """Adjust total quantity"""
        new_total = self.total_qty + qty
        if new_total >= self.used_qty:  # Never allow negative remaining
            self.total_qty = new_total
            self.updated_at = datetime.utcnow()
            return True
        return False

    def __repr__(self):
        return f'<CustomerPackageItem {self.id}: Package {self.customer_package_id} - Service {self.service_id} ({self.used_qty}/{self.total_qty})>'


class PackageUsage(db.Model):
    """Audit log for package usage"""
    __tablename__ = 'package_usage'

    id = db.Column(db.Integer, primary_key=True)
    customer_package_id = db.Column(db.Integer, db.ForeignKey('customer_package.id'), nullable=False)
    customer_package_item_id = db.Column(db.Integer, db.ForeignKey('customer_package_item.id'), nullable=True)
    usage_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)
    qty = db.Column(db.Integer, default=0)
    change_type = db.Column(db.Enum('use', 'refund', 'adjust', name='usage_type'), default='use')
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    service = db.relationship('Service', backref='package_usage_logs')
    staff = db.relationship('User', backref='staff_package_usage_logs')
    appointment = db.relationship('Appointment', backref='appointment_package_usage_logs')

    # Indexes
    __table_args__ = (
        db.Index('ix_package_usage_customer_package', 'customer_package_id'),
        db.Index('ix_package_usage_service', 'service_id'),
        db.Index('ix_package_usage_date', 'usage_date'),
    )

    def __repr__(self):
        return f'<PackageUsage {self.id}: {self.change_type} {self.qty} - Package {self.customer_package_id}>'


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.Column(db.String(50), nullable=False)  # Fallback for compatibility
    expense_date = db.Column(db.Date, nullable=False, default=date.today)
    expense_time = db.Column(db.Time)  # Time when expense was made
    payment_method = db.Column(db.String(20), default='cash')  # cash, card, upi, petty_cash, reimbursement
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receipt_number = db.Column(db.String(50))
    receipt_path = db.Column(db.String(255))  # Path to receipt file
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)





# Unaki Booking System Models
class UnakiBooking(db.Model):
    """Main Unaki booking table for appointment scheduling"""
    __tablename__ = 'unaki_booking'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    # Client Information
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=True)  # FK to customer table
    client_name = db.Column(db.String(100), nullable=False)
    client_phone = db.Column(db.String(20))
    client_email = db.Column(db.String(120))

    # Staff Assignment
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    staff_name = db.Column(db.String(100), nullable=False)  # Denormalized for quick access

    # Service Details
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)  # FK to service table
    service_name = db.Column(db.String(100), nullable=False)
    service_duration = db.Column(db.Integer, nullable=False)  # in minutes
    service_price = db.Column(db.Float, default=0.0)

    # Appointment Timing
    appointment_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    # Status and Notes
    status = db.Column(db.String(20), default='scheduled')  # scheduled, confirmed, in_progress, completed, cancelled, no_show
    notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)  # Staff-only notes

    # Booking Source and Method
    booking_source = db.Column(db.String(50), default='unaki_system')  # unaki_system, phone, walk_in, online
    booking_method = db.Column(db.String(50), default='drag_select')  # drag_select, quick_book, manual

    # Payment Information
    amount_charged = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, partial, cancelled
    payment_method = db.Column(db.String(20))  # cash, card, upi, online

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # Relationships
    assigned_staff = db.relationship('User', backref='unaki_bookings', foreign_keys=[staff_id])
    client = db.relationship('Customer', backref='unaki_bookings', foreign_keys=[client_id])
    service = db.relationship('Service', backref='unaki_bookings', foreign_keys=[service_id])

    def to_dict(self):
        """Convert booking to dictionary for API responses"""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'client_name': self.client_name,
            'client_phone': self.client_phone,
            'client_email': self.client_email,
            'staff_id': self.staff_id,
            'staff_name': self.staff_name,
            'service_id': self.service_id,
            'service_name': self.service_name,
            'service_duration': self.service_duration,
            'service_price': float(self.service_price) if self.service_price else 0.0,
            'appointment_date': self.appointment_date.strftime('%Y-%m-%d'),
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'status': self.status,
            'notes': self.notes,
            'booking_source': self.booking_source,
            'amount_charged': float(self.amount_charged) if self.amount_charged else 0.0,
            'payment_status': self.payment_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_duration_display(self):
        """Get human-readable duration"""
        if self.service_duration >= 60:
            hours = self.service_duration // 60
            minutes = self.service_duration % 60
            if minutes > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{hours}h"
        else:
            return f"{self.service_duration}m"

    def get_time_range_display(self):
        """Get formatted time range display"""
        start_12h = self.start_time.strftime('%I:%M %p')
        end_12h = self.end_time.strftime('%I:%M %p')
        return f"{start_12h} - {end_12h}"

    def can_be_cancelled(self):
        """Check if booking can be cancelled"""
        return self.status in ['scheduled', 'confirmed']

    def can_be_rescheduled(self):
        """Check if booking can be rescheduled"""
        return self.status in ['scheduled', 'confirmed']

    def __repr__(self):
        return f'<UnakiBooking {self.id}: {self.client_name} - {self.service_name} on {self.appointment_date}>'

class UnakiStaff(db.Model):
    __tablename__ = 'unaki_staff'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    appointments = db.relationship('UnakiAppointment', backref='staff_member', lazy=True)
    breaks = db.relationship('UnakiBreak', backref='staff_member', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'specialty': self.specialty,
            'active': self.active
        }


class UnakiAppointment(db.Model):
    __tablename__ = 'unaki_appointments'

    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('unaki_staff.id'), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    phone = db.Column(db.String(20))
    notes = db.Column(db.Text)
    appointment_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'staffId': self.staff_id,
            'clientName': self.client_name,
            'service': self.service,
            'startTime': self.start_time.strftime('%H:%M'),
            'endTime': self.end_time.strftime('%H:%M'),
            'phone': self.phone,
            'notes': self.notes,
            'appointmentDate': self.appointment_date.strftime('%Y-%m-%d')
        }

class UnakiBreak(db.Model):
    __tablename__ = 'unaki_breaks'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('unaki_staff.id'), nullable=False)
    break_type = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    break_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'staffId': self.staff_id,
            'breakType': self.break_type,
            'startTime': self.start_time.strftime('%H:%M'),
            'endTime': self.end_time.strftime('%H:%M'),
            'breakDate': self.break_date.strftime('%Y-%m-%d'),
            'notes': self.notes
        }




class StaffSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    # Relationship
    staff = db.relationship('User', backref='schedules')

# ========================================
# COMPREHENSIVE PACKAGE BILLING INTEGRATION
# ========================================

class PackageBenefitTracker(db.Model):
    """Tracks all package benefits and usage with billing integration"""
    __tablename__ = 'package_benefit_tracker'

    id = db.Column(db.Integer, primary_key=True)

    # Customer and package references
    customer_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    package_assignment_id = db.Column(db.Integer, db.ForeignKey('service_package_assignment.id'), nullable=False)

    # Service benefit details
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)  # NULL for prepaid packages
    benefit_type = db.Column(db.String(20), nullable=False)  # 'free', 'discount', 'prepaid', 'unlimited'

    # Usage tracking for limited benefits
    total_allocated = db.Column(db.Integer, default=0)  # Total sessions/uses allocated
    used_count = db.Column(db.Integer, default=0)  # Used sessions/uses
    remaining_count = db.Column(db.Integer, default=0)  # Remaining sessions/uses (NULL for unlimited)

    # Monetary tracking for prepaid benefits
    balance_total = db.Column(db.Float, default=0.0)  # Total prepaid balance
    balance_used = db.Column(db.Float, default=0.0)  # Used prepaid balance
    balance_remaining = db.Column(db.Float, default=0.0)  # Remaining prepaid balance

    # Discount tracking
    discount_percentage = db.Column(db.Float, default=0.0)  # Discount percentage for discount packages

    # Status and validity
    is_active = db.Column(db.Boolean, default=True)
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_to = db.Column(db.DateTime, nullable=False)

    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = db.relationship('Customer', backref='package_benefits')
    service = db.relationship('Service', backref='package_benefits')
    package_assignment = db.relationship('ServicePackageAssignment', backref='benefit_trackers')

    # Indexes for performance
    __table_args__ = (
        db.Index('ix_package_benefit_customer_service_active', 'customer_id', 'service_id', 'is_active'),
        db.Index('ix_package_benefit_validity', 'valid_from', 'valid_to'),
    )

class PackageUsageHistory(db.Model):
    """Comprehensive usage history with billing integration and idempotency"""
    __tablename__ = 'package_usage_history'

    id = db.Column(db.Integer, primary_key=True)

    # References
    customer_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    package_benefit_id = db.Column(db.Integer, db.ForeignKey('package_benefit_tracker.id'), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('enhanced_invoice.id'), nullable=True)
    invoice_item_id = db.Column(db.Integer, db.ForeignKey('invoice_item.id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)

    # Idempotency and concurrency control
    idempotency_key = db.Column(db.String(100), unique=True, nullable=False)  # invoice_id + line_id

    # Usage details
    benefit_type = db.Column(db.String(20), nullable=False)  # 'free', 'discount', 'prepaid', 'unlimited'
    qty_deducted = db.Column(db.Integer, default=0)  # Sessions used
    amount_deducted = db.Column(db.Float, default=0.0)  # Monetary amount deducted (for prepaid)
    discount_applied = db.Column(db.Float, default=0.0)  # Discount amount applied

    # Balance tracking after this transaction
    balance_after_qty = db.Column(db.Integer, default=0)  # Remaining sessions after this use
    balance_after_amount = db.Column(db.Float, default=0.0)  # Remaining balance after this use

    # Transaction details
    transaction_type = db.Column(db.String(20), default='use')  # 'use', 'refund', 'void', 'adjustment'
    reversal_reference_id = db.Column(db.Integer, db.ForeignKey('package_usage_history.id'), nullable=True)  # For reversals

    # Priority and rule tracking
    applied_rule = db.Column(db.String(50))  # Which priority rule was used (auto/manual)
    staff_override = db.Column(db.Boolean, default=False)  # Was this a manual staff override?
    applied_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Audit fields
    charge_date = db.Column(db.DateTime, nullable=False)  # Date of service/charge
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    customer = db.relationship('Customer', backref='package_usage_history')
    package_benefit = db.relationship('PackageBenefitTracker', backref='usage_history')
    service = db.relationship('Service', backref='package_usage_history')
    applied_by_user = db.relationship('User', backref='package_usage_applications')
    reversal_reference = db.relationship('PackageUsageHistory', remote_side=[id], backref='reversed_by')

    # Indexes for performance and integrity
    __table_args__ = (
        db.Index('ix_package_usage_customer_date', 'customer_id', 'charge_date'),
        db.Index('ix_package_usage_invoice', 'invoice_id', 'invoice_item_id'),
    )

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

# Note: MembershipService and KittyPartyService classes are defined earlier in the file

class ServiceInventoryItem(db.Model):
    """Link services with inventory items they consume"""
    __tablename__ = 'service_inventory_items'

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    inventory_id = db.Column(db.Integer, nullable=False)  # Reference to inventory product
    quantity_per_service = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(20), default='pcs')
    is_required = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    service = db.relationship('Service', backref='inventory_items')

# Import Hanaman Inventory Models after all other models are defined
# Hanamantinventory models import removed to fix startup issues