from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, FloatField, IntegerField, DateField, DateTimeField, BooleanField, TimeField, HiddenField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, ValidationError
from wtforms.widgets import TextArea, CheckboxInput, ListWidget
from datetime import datetime, date

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    role = SelectField('Role', choices=[
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('cashier', 'Cashier')
    ], validators=[DataRequired()])
    commission_rate = FloatField('Commission Rate (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    hourly_rate = FloatField('Hourly Rate', validators=[Optional(), NumberRange(min=0)])
    is_active = BooleanField('Active')

class ClientForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=20)])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
    preferences = TextAreaField('Preferences', validators=[Optional()])
    allergies = TextAreaField('Allergies', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])

class ServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    duration = IntegerField('Approx. Time (minutes)', validators=[DataRequired(), NumberRange(min=1)])
    price = FloatField('Price (₹)', validators=[DataRequired(), NumberRange(min=0)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    is_active = BooleanField('Active', default=True)

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        # Dynamically populate categories from database
        from models import Category
        self.category_id.choices = [(0, 'Select Category')] + [
            (c.id, c.display_name) for c in 
            Category.query.filter_by(category_type='service', is_active=True)
            .order_by(Category.sort_order, Category.display_name).all()
        ]

class AppointmentForm(FlaskForm):
    client_id = SelectField('Client', coerce=int, validators=[DataRequired()])
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    staff_id = SelectField('Staff', coerce=int, validators=[DataRequired()])
    appointment_date = DateTimeField('Appointment Date & Time', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    amount = FloatField('Amount', validators=[Optional(), NumberRange(min=0)])
    discount = FloatField('Discount', validators=[Optional(), NumberRange(min=0)])

class InventoryForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    current_stock = IntegerField('Current Stock', validators=[DataRequired(), NumberRange(min=0)])
    min_stock_level = IntegerField('Minimum Stock Level', validators=[DataRequired(), NumberRange(min=0)])
    cost_price = FloatField('Cost Price', validators=[Optional(), NumberRange(min=0)])
    selling_price = FloatField('Selling Price', validators=[Optional(), NumberRange(min=0)])
    supplier = StringField('Supplier Name', validators=[Optional(), Length(max=100)])
    expiry_date = DateField('Expiry Date', validators=[Optional()])

class ExpenseForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired(), Length(max=200)])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    expense_date = DateField('Expense Date', validators=[DataRequired()])
    receipt_path = StringField('Receipt Path', validators=[Optional(), Length(max=200)])
    notes = TextAreaField('Notes', validators=[Optional()])

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=50)])
    display_name = StringField('Display Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    color = StringField('Color', validators=[Optional()], default='#007bff')
    sort_order = IntegerField('Sort Order', validators=[Optional(), NumberRange(min=0)], default=0)
    is_active = BooleanField('Active', default=True)

class PackageForm(FlaskForm):
    name = StringField('Package Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    included_services = SelectMultipleField('Included Services', coerce=int, validators=[DataRequired()])
    total_sessions = IntegerField('No. of Sessions', validators=[DataRequired(), NumberRange(min=1)])
    validity_days = IntegerField('Validity Period (days)', validators=[DataRequired(), NumberRange(min=1)])
    total_price = FloatField('Package Price (₹)', validators=[DataRequired(), NumberRange(min=0)])
    discount_percentage = FloatField('Discount %', validators=[Optional(), NumberRange(min=0, max=100)])
    is_active = BooleanField('Active', default=True)

    def __init__(self, *args, **kwargs):
        super(PackageForm, self).__init__(*args, **kwargs)
        # Dynamically populate services from database
        from models import Service
        self.included_services.choices = [
            (s.id, f"{s.name} (₹{s.price})") for s in 
            Service.query.filter_by(is_active=True).order_by(Service.name).all()
        ]

class EnhancedPackageForm(FlaskForm):
    """Professional package creation form with individual service discounts and complete management"""
    name = StringField('Package Name', validators=[DataRequired(), Length(max=100)], 
                      description='e.g., "Bridal Glow Package", "Monthly Wellness Package"')
    description = TextAreaField('Package Description', validators=[Optional()], 
                               description='Short summary for clients and admin reference')
    validity_days = IntegerField('Validity Period (Days)', validators=[DataRequired(), NumberRange(min=1, max=365)], 
                                default=90, description='Package activation time - how long package remains valid')
    total_price = FloatField('Total Package Price (₹)', validators=[DataRequired(), NumberRange(min=0.01)])
    discount_percentage = FloatField('Overall Package Discount (%)', validators=[Optional(), NumberRange(min=0, max=100)], 
                                   default=0.0, description='Additional discount applied to entire package')
    is_active = BooleanField('Package Status', default=True, description='Active packages can be assigned to clients')

    # Service selection data (handled via JavaScript)
    selected_services = HiddenField('Selected Services JSON')  # JSON: [{"service_id": 1, "sessions": 3, "discount": 10}]

class AssignPackageForm(FlaskForm):
    """Assign package to client form"""
    client_id = SelectField('Select Client', coerce=int, validators=[DataRequired()])
    package_id = HiddenField('Package ID', validators=[DataRequired()])
    custom_price = FloatField('Custom Price (Optional)', validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField('Assignment Notes', validators=[Optional()])

class ClientPackageTrackingForm(FlaskForm):
    """Track package usage for clients"""
    client_package_id = HiddenField('Client Package ID', validators=[DataRequired()])
    service_id = SelectField('Service Used', coerce=int, validators=[DataRequired()])
    sessions_used = IntegerField('Sessions Used', validators=[DataRequired(), NumberRange(min=1)], default=1)
    appointment_id = HiddenField('Appointment ID', validators=[Optional()])

class StaffScheduleForm(FlaskForm):
    staff_id = SelectField('Staff Member', coerce=int, validators=[DataRequired()])
    day_of_week = SelectField('Day of Week', choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday')
    ], coerce=int, validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    is_available = BooleanField('Available', default=True)

# Advanced Forms for Real-World Operations

class ReviewForm(FlaskForm):
    """Customer review and rating form"""
    client_id = HiddenField('Client ID', validators=[DataRequired()])
    appointment_id = HiddenField('Appointment ID')
    staff_id = SelectField('Staff Member', coerce=int, validators=[Optional()])
    service_id = SelectField('Service', coerce=int, validators=[Optional()])
    rating = SelectField('Rating', choices=[
        (5, '⭐⭐⭐⭐⭐ Excellent'),
        (4, '⭐⭐⭐⭐ Good'),
        (3, '⭐⭐⭐ Average'),
        (2, '⭐⭐ Poor'),
        (1, '⭐ Very Poor')
    ], coerce=int, validators=[DataRequired()])
    comment = TextAreaField('Review Comment', validators=[Optional(), Length(max=500)])
    is_public = BooleanField('Make this review public', default=True)

class CommunicationForm(FlaskForm):
    """Client communication tracking form"""
    client_id = SelectField('Client', coerce=int, validators=[DataRequired()])
    type = SelectField('Communication Type', choices=[
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('call', 'Phone Call'),
        ('in_person', 'In Person')
    ], validators=[DataRequired()])
    subject = StringField('Subject', validators=[Optional(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired()])

    def validate_subject(self, field):
        if self.type.data in ['email', 'sms', 'whatsapp'] and not field.data:
            raise ValidationError('Subject is required for this communication type.')

class PromotionForm(FlaskForm):
    """Marketing promotion form"""
    name = StringField('Promotion Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    discount_type = SelectField('Discount Type', choices=[
        ('percentage', 'Percentage Discount'),
        ('fixed_amount', 'Fixed Amount Discount')
    ], validators=[DataRequired()])
    discount_value = FloatField('Discount Value', validators=[DataRequired(), NumberRange(min=0)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    usage_limit = IntegerField('Usage Limit', validators=[Optional(), NumberRange(min=1)])
    applicable_services = SelectField('Applicable Services', validators=[Optional()])
    is_active = BooleanField('Active', default=True)

    def validate_end_date(self, field):
        if field.data and self.start_date.data and field.data <= self.start_date.data:
            raise ValidationError('End date must be after start date.')

class WaitlistForm(FlaskForm):
    """Client waitlist form"""
    client_id = SelectField('Client', coerce=int, validators=[DataRequired()])
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    staff_id = SelectField('Preferred Staff (Optional)', coerce=int, validators=[Optional()])
    preferred_date = DateField('Preferred Date', validators=[DataRequired()])
    preferred_time = TimeField('Preferred Time', validators=[Optional()])
    is_flexible = BooleanField('Flexible with time/date', default=False)
    expires_at = DateTimeField('Expires At', validators=[Optional()])

    def validate_preferred_date(self, field):
        if field.data and field.data < date.today():
            raise ValidationError('Preferred date cannot be in the past.')

class ProductSaleForm(FlaskForm):
    """Retail product sale form"""
    inventory_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    client_id = SelectField('Client (Optional)', coerce=int, validators=[Optional()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    unit_price = FloatField('Unit Price', validators=[DataRequired(), NumberRange(min=0)])
    payment_method = SelectField('Payment Method', choices=[
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('online', 'Online Payment'),
        ('store_credit', 'Store Credit')
    ], validators=[DataRequired()])

class RecurringAppointmentForm(FlaskForm):
    """Recurring appointment setup form"""
    client_id = SelectField('Client', coerce=int, validators=[DataRequired()])
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    staff_id = SelectField('Staff Member', coerce=int, validators=[DataRequired()])
    frequency = SelectField('Frequency', choices=[
        ('weekly', 'Weekly'),
        ('biweekly', 'Every 2 Weeks'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Every 3 Months')
    ], validators=[DataRequired()])
    day_of_week = SelectField('Day of Week', choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday')
    ], coerce=int, validators=[DataRequired()])
    time_slot = TimeField('Time', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date (Optional)', validators=[Optional()])
    is_active = BooleanField('Active', default=True)

    def validate_start_date(self, field):
        if field.data and field.data < date.today():
            raise ValidationError('Start date cannot be in the past.')

    def validate_end_date(self, field):
        if field.data and self.start_date.data and field.data <= self.start_date.data:
            raise ValidationError('End date must be after start date.')

class BusinessSettingsForm(FlaskForm):
    """Business settings configuration form"""
    business_name = StringField('Business Name', validators=[DataRequired(), Length(max=100)])
    business_phone = StringField('Business Phone', validators=[DataRequired(), Length(max=20)])
    business_email = StringField('Business Email', validators=[DataRequired(), Email()])
    business_address = TextAreaField('Business Address', validators=[DataRequired()])
    tax_rate = FloatField('Tax Rate (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    currency_symbol = StringField('Currency Symbol', validators=[DataRequired(), Length(max=5)])
    currency = SelectField('Currency', choices=[
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('CAD', 'Canadian Dollar (C$)'),
        ('AUD', 'Australian Dollar (A$)'),
        ('JPY', 'Japanese Yen (¥)'),
        ('INR', 'Indian Rupee (₹)'),
        ('CHF', 'Swiss Franc (CHF)'),
        ('CNY', 'Chinese Yuan (¥)'),
        ('SEK', 'Swedish Krona (kr)')
    ], validators=[DataRequired()])
    timezone = SelectField('Timezone', choices=[
        ('UTC', 'UTC'),
        ('US/Eastern', 'US Eastern'),
        ('US/Central', 'US Central'),
        ('US/Mountain', 'US Mountain'),
        ('US/Pacific', 'US Pacific'),
        ('Europe/London', 'London'),
        ('Europe/Paris', 'Paris'),
        ('Europe/Berlin', 'Berlin'),
        ('Asia/Tokyo', 'Tokyo'),
        ('Asia/Shanghai', 'Shanghai'),
        ('Asia/Kolkata', 'Mumbai'),
        ('Australia/Sydney', 'Sydney'),
        ('America/Toronto', 'Toronto'),
        ('America/Vancouver', 'Vancouver')
    ], validators=[DataRequired()])
    appointment_buffer = IntegerField('Appointment Buffer (minutes)', validators=[Optional(), NumberRange(min=0, max=60)])
    booking_advance_days = IntegerField('Max Booking Advance (days)', validators=[Optional(), NumberRange(min=1, max=365)])
    cancellation_hours = IntegerField('Cancellation Notice Required (hours)', validators=[Optional(), NumberRange(min=1, max=72)])
    no_show_fee = FloatField('No-Show Fee', validators=[Optional(), NumberRange(min=0)])

class AdvancedClientForm(ClientForm):
    """Enhanced client form with advanced fields"""
    preferred_communication = SelectField('Preferred Communication', choices=[
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('phone', 'Phone Call')
    ], default='email', validators=[DataRequired()])
    marketing_consent = BooleanField('Marketing Consent', default=True)
    referral_source = SelectField('How did you hear about us?', choices=[
        ('', 'Select Source'),
        ('google', 'Google Search'),
        ('social_media', 'Social Media'),
        ('friend_referral', 'Friend Referral'),
        ('advertisement', 'Advertisement'),
        ('walk_in', 'Walk-in'),
        ('repeat_client', 'Repeat Client'),
        ('other', 'Other')
    ], validators=[Optional()])
    emergency_contact = StringField('Emergency Contact', validators=[Optional(), Length(max=100)])
    emergency_phone = StringField('Emergency Phone', validators=[Optional(), Length(max=20)])

class AdvancedUserForm(UserForm):
    """Enhanced staff form with advanced fields"""
    employee_id = StringField('Employee ID', validators=[Optional(), Length(max=20)])
    role_id = SelectField('Role', coerce=int, validators=[Optional()])
    department_id = SelectField('Department', coerce=int, validators=[Optional()])
    department = SelectField('Department', choices=[
        ('', 'Select Department'),
        ('hair', 'Hair Department'),
        ('skincare', 'Skincare Department'),
        ('massage', 'Massage Therapy'),
        ('nails', 'Nail Services'),
        ('reception', 'Reception'),
        ('management', 'Management')
    ], validators=[Optional()])
    hire_date = DateField('Hire Date', validators=[Optional()])
    specialties = TextAreaField('Specialties', validators=[Optional()], 
                               description='List staff specialties and certifications')

class QuickBookingForm(FlaskForm):
    """Quick walk-in booking form"""
    client_name = StringField('Client Name', validators=[DataRequired(), Length(max=100)])
    client_phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    staff_id = SelectField('Staff Member', coerce=int, validators=[DataRequired()])
    appointment_time = DateTimeField('Appointment Time', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    is_walk_in = HiddenField(default='true')

class PaymentForm(FlaskForm):
    """Payment processing form"""
    appointment_id = HiddenField('Appointment ID', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    payment_method = SelectField('Payment Method', choices=[
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('online', 'Online Payment'),
        ('gift_card', 'Gift Card'),
        ('store_credit', 'Store Credit'),
        ('insurance', 'Insurance')
    ], validators=[DataRequired()])
    tips = FloatField('Tips', validators=[Optional(), NumberRange(min=0)])
    discount = FloatField('Discount', validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField('Payment Notes', validators=[Optional()])

# CRUD System Forms for Dynamic Configuration

class RoleForm(FlaskForm):
    """Role management form"""
    name = StringField('Role Name', validators=[DataRequired(), Length(min=3, max=50)])
    display_name = StringField('Display Name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    permissions = SelectMultipleField('Permissions', coerce=int, validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Will be populated dynamically from database
        self.permissions.choices = []

class PermissionForm(FlaskForm):
    """Permission management form"""
    name = StringField('Permission Name', validators=[DataRequired(), Length(min=3, max=50)])
    display_name = StringField('Display Name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    module = StringField('Module', validators=[DataRequired(), Length(min=3, max=50)])
    is_active = BooleanField('Active', default=True)

class CategoryForm(FlaskForm):
    """Category management form"""
    name = StringField('Category Name', validators=[DataRequired(), Length(min=3, max=50)])
    display_name = StringField('Display Name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    category_type = SelectField('Category Type', choices=[
        ('service', 'Service Category'),
        ('product', 'Product Category'),
        ('expense', 'Expense Category'),
        ('inventory', 'Inventory Category')
    ], validators=[DataRequired()])
    color = StringField('Color', validators=[Optional(), Length(min=7, max=7)])
    icon = StringField('Icon', validators=[Optional(), Length(max=50)])
    is_active = BooleanField('Active', default=True)
    sort_order = IntegerField('Sort Order', validators=[Optional(), NumberRange(min=0)])

class DepartmentForm(FlaskForm):
    """Department management form"""
    name = StringField('Department Name', validators=[DataRequired(), Length(min=3, max=50)])
    display_name = StringField('Display Name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    manager_id = SelectField('Manager', coerce=int, validators=[Optional()])
    is_active = BooleanField('Active', default=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Will be populated dynamically from database
        self.manager_id.choices = []

class SystemSettingForm(FlaskForm):
    """System setting management form"""
    key = StringField('Setting Key', validators=[DataRequired(), Length(min=3, max=100)])
    value = TextAreaField('Value', validators=[Optional()])
    data_type = SelectField('Data Type', choices=[
        ('string', 'String'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('json', 'JSON')
    ], validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired(), Length(min=3, max=50)])
    display_name = StringField('Display Name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    is_public = BooleanField('Public Setting', default=False)

class ComprehensiveStaffForm(FlaskForm):
    """Comprehensive Staff Management Form - All 11 Requirements"""

    # Basic Information
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Optional(), Length(min=6)])

    # Staff Profile Details
    profile_photo_url = StringField('Profile Photo URL', validators=[Optional()])
    gender = SelectField('Gender', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    date_of_joining = DateField('Date of Joining', validators=[Optional()])
    staff_code = StringField('Staff Code', validators=[DataRequired(), Length(max=20)])
    notes_bio = TextAreaField('Notes/Bio', validators=[Optional()])
    designation = StringField('Designation', validators=[DataRequired(), Length(max=100)])

    # ID Proofs & Verification
    aadhaar_number = StringField('Aadhaar Number', validators=[Optional(), Length(min=12, max=12)])
    aadhaar_card_url = StringField('Aadhaar Card URL', validators=[Optional()])
    pan_number = StringField('PAN Number', validators=[Optional(), Length(min=10, max=10)])
    pan_card_url = StringField('PAN Card URL', validators=[Optional()])
    verification_status = BooleanField('Verification Status', default=False)

    # Facial Recognition
    face_image_url = StringField('Face Image URL', validators=[Optional()])
    facial_encoding = StringField('Facial Encoding', validators=[Optional()])
    enable_face_checkin = BooleanField('Enable Face Check-in', default=True)

    # Work Schedule
    monday = BooleanField('Monday', default=True)
    tuesday = BooleanField('Tuesday', default=True)
    wednesday = BooleanField('Wednesday', default=True)
    thursday = BooleanField('Thursday', default=True)
    friday = BooleanField('Friday', default=True)
    saturday = BooleanField('Saturday', default=False)
    sunday = BooleanField('Sunday', default=False)

    shift_start_time = TimeField('Shift Start Time', validators=[Optional()])
    shift_end_time = TimeField('Shift End Time', validators=[Optional()])
    break_time = StringField('Break Time', validators=[Optional(), Length(max=50)])
    weekly_off_days = StringField('Weekly Off Days', validators=[Optional(), Length(max=20)])

    # Performance & Commission
    commission_percentage = FloatField('Commission Percentage', validators=[Optional(), NumberRange(min=0, max=100)])
    fixed_commission = FloatField('Fixed Commission', validators=[Optional(), NumberRange(min=0)])
    hourly_rate = FloatField('Hourly Rate', validators=[Optional(), NumberRange(min=0)])

    # Role & Department
    role_id = SelectField('Role', coerce=int, validators=[Optional()])
    department_id = SelectField('Department', coerce=int, validators=[Optional()])

    # Service Assignment
    assigned_services = SelectMultipleField('Assigned Services', coerce=int, validators=[Optional()])

    # Status
    is_active = BooleanField('Active Status', default=True)

    # Submit button
    submit = SubmitField('Save Staff Member')

    def __init__(self, *args, **kwargs):
        super(ComprehensiveStaffForm, self).__init__(*args, **kwargs)
        # Dynamically populate choices from database
        try:
            from models import Role, Department, Service
            self.role_id.choices = [(0, 'Select Role')] + [
                (r.id, r.display_name) for r in 
                Role.query.filter_by(is_active=True).order_by(Role.display_name).all()
            ]
            self.department_id.choices = [(0, 'Select Department')] + [
                (d.id, d.display_name) for d in 
                Department.query.filter_by(is_active=True).order_by(Department.display_name).all()
            ]
            self.assigned_services.choices = [
                (s.id, s.name) for s in 
                Service.query.filter_by(is_active=True).order_by(Service.name).all()
            ]
        except:
            # Fallback if database is not available
            self.role_id.choices = [(0, 'Select Role')]
            self.department_id.choices = [(0, 'Select Department')]
            self.assigned_services.choices = []

class MultiCheckboxField(SelectMultipleField):
    """Custom field for multiple checkboxes"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

# Comprehensive Staff Management Module Forms

class StaffProfileForm(FlaskForm):
    """Form for staff to manage their own profile details"""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    bio = TextAreaField('Biography', validators=[Optional()])
    profile_picture = StringField('Profile Picture URL', validators=[Optional()]) # URL to profile pic

class StaffEmploymentForm(FlaskForm):
    """Form to manage staff employment details"""
    employee_id = StringField('Employee ID', validators=[Optional(), Length(max=20)])
    hire_date = DateField('Hire Date', validators=[Optional()])
    job_title = StringField('Job Title', validators=[DataRequired(), Length(max=100)])
    department_id = SelectField('Department', coerce=int, validators=[Optional()])
    manager_id = SelectField('Manager', coerce=int, validators=[Optional()])
    employment_status = SelectField('Employment Status', choices=[
        ('full-time', 'Full-Time'),
        ('part-time', 'Part-Time'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
        ('terminated', 'Terminated')
    ], validators=[DataRequired()])
    termination_date = DateField('Termination Date', validators=[Optional()])
    salary = FloatField('Salary', validators=[Optional(), NumberRange(min=0)])
    commission_rate = FloatField('Commission Rate (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    hourly_rate = FloatField('Hourly Rate', validators=[Optional(), NumberRange(min=0)])

class StaffAvailabilityForm(FlaskForm):
    """Form to manage staff availability schedule"""
    staff_id = SelectField('Staff Member', coerce=int, validators=[DataRequired()])
    availability_slots = TextAreaField('Availability Slots (JSON format)', validators=[DataRequired()],
                                        description='e.g., [{"day": "Monday", "start_time": "09:00", "end_time": "17:00"}, ...]')
    is_default = BooleanField('Set as Default Schedule', default=False)

class StaffPermissionsForm(FlaskForm):
    """Form to assign roles and permissions to staff"""
    staff_id = HiddenField('Staff ID', validators=[DataRequired()])
    role_id = SelectField('Assigned Role', coerce=int, validators=[DataRequired()])
    permissions = SelectMultipleField('Additional Permissions', coerce=int, validators=[Optional()])

class StaffLeaveRequestForm(FlaskForm):
    """Form for staff to request leave"""
    staff_id = HiddenField('Staff ID', validators=[DataRequired()])
    leave_type = SelectField('Leave Type', choices=[
        ('vacation', 'Vacation'),
        ('sick', 'Sick Leave'),
        ('personal', 'Personal Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('unpaid', 'Unpaid Leave')
    ], validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    reason = TextAreaField('Reason for Leave', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')

    def validate_dates(self, field):
        if self.end_date.data and self.start_date.data and self.end_date.data < self.start_date.data:
            raise ValidationError('End date must be after start date.')

class StaffPerformanceReviewForm(FlaskForm):
    """Form for conducting staff performance reviews"""
    staff_id = SelectField('Staff Member', coerce=int, validators=[DataRequired()])
    reviewer_id = SelectField('Reviewer', coerce=int, validators=[DataRequired()])
    review_date = DateField('Review Date', validators=[DataRequired()])
    rating = SelectField('Rating', choices=[
        (5, '⭐⭐⭐⭐⭐ Outstanding'),
        (4, '⭐⭐⭐⭐ Exceeds Expectations'),
        (3, '⭐⭐⭐ Meets Expectations'),
        (2, '⭐⭐ Needs Improvement'),
        (1, '⭐ Unsatisfactory')
    ], coerce=int, validators=[DataRequired()])
    strengths = TextAreaField('Strengths', validators=[Optional()])
    areas_for_improvement = TextAreaField('Areas for Improvement', validators=[Optional()])
    goals = TextAreaField('Goals for Next Period', validators=[Optional()])
    comments = TextAreaField('Additional Comments', validators=[Optional()])

class StaffTrainingForm(FlaskForm):
    """Form to track staff training and certifications"""
    staff_id = SelectField('Staff Member', coerce=int, validators=[DataRequired()])
    training_name = StringField('Training/Certification Name', validators=[DataRequired(), Length(max=100)])
    provider = StringField('Provider', validators=[Optional(), Length(max=100)])
    completion_date = DateField('Completion Date', validators=[Optional()])
    expiry_date = DateField('Expiry Date', validators=[Optional()])
    certificate_url = StringField('Certificate URL', validators=[Optional()])

class StaffOnboardingForm(FlaskForm):
    """Form to manage the staff onboarding process"""
    staff_id = HiddenField('Staff ID', validators=[DataRequired()])
    onboarding_checklist = TextAreaField('Onboarding Checklist (JSON format)', validators=[Optional()],
                                        description='e.g., [{"task": "Complete HR Forms", "completed": true}, ...]')
    onboarding_status = SelectField('Onboarding Status', choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], default='not_started', validators=[DataRequired()])
    onboarding_complete_date = DateField('Onboarding Completion Date', validators=[Optional()])

class StaffOffboardingForm(FlaskForm):
    """Form to manage the staff offboarding process"""
    staff_id = HiddenField('Staff ID', validators=[DataRequired()])
    offboarding_date = DateField('Offboarding Date', validators=[DataRequired()])
    reason_for_leaving = TextAreaField('Reason for Leaving', validators=[Optional()])
    offboarding_checklist = TextAreaField('Offboarding Checklist (JSON format)', validators=[Optional()],
                                         description='e.g., [{"task": "Return Company Laptop", "completed": true}, ...]')
    offboarding_status = SelectField('Offboarding Status', choices=[
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], default='in_progress', validators=[DataRequired()])

class ComprehensiveStaffForm(FlaskForm):
    """Comprehensive staff management form with all 11 required features"""
    # Basic Information
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = EmailField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])

    # Profile Details
    gender = SelectField('Gender', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], default='other')
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    date_of_joining = DateField('Date of Joining', validators=[Optional()])
    staff_code = StringField('Staff Code', validators=[Optional(), Length(max=20)])
    designation = StringField('Designation', validators=[Optional(), Length(max=100)])
    notes_bio = TextAreaField('Notes/Bio', validators=[Optional()])

    # ID Verification
    aadhaar_number = StringField('Aadhaar Number', validators=[Optional(), Length(max=12)])
    pan_number = StringField('PAN Number', validators=[Optional(), Length(max=10)])
    verification_status = BooleanField('Verified')

    # Facial Recognition
    enable_face_checkin = BooleanField('Enable Face Check-in', default=True)

    # Work Schedule
    shift_start_time = TimeField('Shift Start Time', validators=[Optional()])
    shift_end_time = TimeField('Shift End Time', validators=[Optional()])
    break_time = StringField('Break Time', validators=[Optional()])
    weekly_off_days = StringField('Weekly Off Days', validators=[Optional()])

    # Working Days (checkboxes)
    monday = BooleanField('Monday', default=True)
    tuesday = BooleanField('Tuesday', default=True)
    wednesday = BooleanField('Wednesday', default=True)
    thursday = BooleanField('Thursday', default=True)
    friday = BooleanField('Friday', default=True)
    saturday = BooleanField('Saturday', default=False)
    sunday = BooleanField('Sunday', default=False)

    # Performance & Commission
    commission_percentage = FloatField('Commission Percentage', validators=[Optional()])
    fixed_commission = FloatField('Fixed Commission', validators=[Optional()])
    hourly_rate = FloatField('Hourly Rate', validators=[Optional()])

    # Role & Department
    role_id = SelectField('Role', coerce=int, validators=[Optional()])
    department_id = SelectField('Department', coerce=int, validators=[Optional()])

    # Service Assignment
    assigned_services = SelectMultipleField('Assigned Services', coerce=int, validators=[Optional()])

    # System Settings
    password = PasswordField('Password', validators=[Optional()])
    is_active = BooleanField('Active', default=True)

class StaffExitInterviewForm(FlaskForm):
    """Form to capture feedback during staff exit"""
    staff_id = HiddenField('Staff ID', validators=[DataRequired()])
    interview_date = DateField('Interview Date', validators=[DataRequired()])
    interviewer_name = StringField('Interviewer Name', validators=[DataRequired(), Length(max=100)])
    reason_for_leaving = TextAreaField('Reason for Leaving', validators=[Optional()])
    job_satisfaction = SelectField('Job Satisfaction', choices=[
        ('very_satisfied', 'Very Satisfied'),
        ('satisfied', 'Satisfied'),
        ('neutral', 'Neutral'),
        ('dissatisfied', 'Dissatisfied'),
        ('very_dissatisfied', 'Very Dissatisfied')
    ], validators=[Optional()])
    recommend_company = BooleanField('Would you recommend this company to a friend?', default=False)
    suggestions = TextAreaField('Suggestions for Improvement', validators=[Optional()])
    final_comments = TextAreaField('Final Comments', validators=[Optional()])