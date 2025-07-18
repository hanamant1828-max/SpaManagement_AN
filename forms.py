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

class MultiCheckboxField(SelectMultipleField):
    """Custom field for multiple checkboxes"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()
