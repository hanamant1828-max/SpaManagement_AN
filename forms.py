"""
Flask-WTF forms for the Spa Management System
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, SelectMultipleField, IntegerField, FloatField, DateField, TimeField, DateTimeField, HiddenField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, ValidationError
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class UserForm(FlaskForm):
    """User registration/edit form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    role = SelectField('Role', choices=[('staff', 'Staff'), ('manager', 'Manager'), ('admin', 'Admin')])
    is_active = BooleanField('Active')
    submit = SubmitField('Save User')

class CustomerForm(FlaskForm):
    """Customer form with enhanced validation and defensive coding"""
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required. Please enter the customer\'s first name.'), 
        Length(max=50, message='First name must be less than 50 characters.')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required. Please enter the customer\'s last name.'), 
        Length(max=50, message='Last name must be less than 50 characters.')
    ])
    phone = StringField('Phone', validators=[
        DataRequired(message='Phone number is required. Please enter a valid phone number.'), 
        Length(min=10, max=20, message='Phone number must be between 10-20 characters.')
    ])
    email = StringField('Email', validators=[
        Optional(), 
        Email(message='Please enter a valid email address format.')
    ])
    address = TextAreaField('Address', validators=[
        Optional(), 
        Length(max=500, message='Address must be less than 500 characters.')
    ])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    gender = SelectField('Gender', choices=[('', 'Select...'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    preferences = TextAreaField('Preferences', validators=[
        Optional(), 
        Length(max=1000, message='Preferences must be less than 1000 characters.')
    ])
    allergies = TextAreaField('Allergies', validators=[
        Optional(), 
        Length(max=1000, message='Allergies must be less than 1000 characters.')
    ])
    notes = TextAreaField('Notes', validators=[
        Optional(), 
        Length(max=1000, message='Notes must be less than 1000 characters.')
    ])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Customer')

    def validate_phone(self, field):
        """Custom phone validation"""
        if field.data:
            import re
            digits = re.sub(r'[^\d]', '', field.data)
            if len(digits) < 10:
                raise ValidationError('Phone number must contain at least 10 digits.')

    def validate_date_of_birth(self, field):
        """Custom date of birth validation"""
        if field.data:
            from datetime import date
            if field.data > date.today():
                raise ValidationError('Date of birth cannot be in the future.')

class ServiceForm(FlaskForm):
    """Service form"""
    name = StringField('Service Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    duration = IntegerField('Duration (minutes)', validators=[DataRequired(), NumberRange(min=1)])
    category = StringField('Category', validators=[Optional(), Length(max=50)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Service')

class AppointmentForm(FlaskForm):
    """Appointment form"""
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    staff_id = SelectField('Staff Member', coerce=int, validators=[Optional()])
    appointment_date = DateTimeField('Appointment Date', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    notes = TextAreaField('Notes', validators=[Optional()])
    amount = FloatField('Amount', validators=[Optional(), NumberRange(min=0)])
    discount = FloatField('Discount', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Save Appointment')

# InventoryForm removed - no inventory functionality

class ExpenseForm(FlaskForm):
    """Expense form"""
    description = StringField('Description', validators=[DataRequired(), Length(max=200)])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    category = StringField('Category', validators=[Optional(), Length(max=50)])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    expense_date = DateField('Expense Date', validators=[DataRequired()])
    receipt_path = StringField('Receipt Path', validators=[Optional(), Length(max=500)])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Expense')

# Additional forms for advanced features
class PackageForm(FlaskForm):
    """Package form"""
    name = StringField('Package Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    validity_days = IntegerField('Validity (days)', validators=[DataRequired(), NumberRange(min=1)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Package')

class StaffScheduleForm(FlaskForm):
    """Staff schedule form"""
    staff_id = SelectField('Staff Member', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    is_available = BooleanField('Available', default=True)
    submit = SubmitField('Save Schedule')

class ReviewForm(FlaskForm):
    """Review form"""
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    service_id = SelectField('Service', coerce=int, validators=[Optional()])
    rating = SelectField('Rating', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], coerce=int, validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[Optional()])
    submit = SubmitField('Save Review')

class CommunicationForm(FlaskForm):
    """Communication form"""
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    type = SelectField('Type', choices=[('email', 'Email'), ('sms', 'SMS'), ('call', 'Call'), ('note', 'Note')])
    subject = StringField('Subject', validators=[Optional(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send/Save')

class PromotionForm(FlaskForm):
    """Promotion form"""
    name = StringField('Promotion Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    discount_type = SelectField('Discount Type', choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')])
    discount_value = FloatField('Discount Value', validators=[DataRequired(), NumberRange(min=0)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Promotion')

class WaitlistForm(FlaskForm):
    """Waitlist form"""
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    preferred_date = DateField('Preferred Date', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Add to Waitlist')

class ProductSaleForm(FlaskForm):
    """Product sale form"""
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    unit_price = FloatField('Unit Price', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Record Sale')

class RecurringAppointmentForm(FlaskForm):
    """Recurring appointment form"""
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    staff_id = SelectField('Staff Member', coerce=int, validators=[Optional()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    frequency = SelectField('Frequency', choices=[
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly')
    ])
    submit = SubmitField('Create Recurring Appointments')

class BusinessSettingsForm(FlaskForm):
    """Business settings form"""
    business_name = StringField('Business Name', validators=[DataRequired(), Length(max=100)])
    address = TextAreaField('Address', validators=[Optional()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email()])
    business_hours = TextAreaField('Business Hours', validators=[Optional()])
    submit = SubmitField('Save Settings')

class AdvancedCustomerForm(FlaskForm):
    """Advanced customer form with additional fields"""
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Address', validators=[Optional()])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    gender = SelectField('Gender', choices=[('', 'Select...'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    emergency_contact = StringField('Emergency Contact', validators=[Optional(), Length(max=100)])
    emergency_phone = StringField('Emergency Phone', validators=[Optional(), Length(max=20)])
    allergies = TextAreaField('Allergies', validators=[Optional()])
    medical_conditions = TextAreaField('Medical Conditions', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Customer')

class AdvancedUserForm(FlaskForm):
    """Advanced user form with additional fields"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    role = SelectField('Role', choices=[('staff', 'Staff'), ('manager', 'Manager'), ('admin', 'Admin')])
    department = StringField('Department', validators=[Optional(), Length(max=50)])
    hire_date = DateField('Hire Date', validators=[Optional()])
    salary = FloatField('Salary', validators=[Optional(), NumberRange(min=0)])
    commission_rate = FloatField('Commission Rate (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save User')

class QuickBookingForm(FlaskForm):
    """Quick booking form for fast appointments"""
    customer_name = StringField('Customer Name', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=20)])
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    appointment_date = DateTimeField('Appointment Date', validators=[DataRequired()])
    submit = SubmitField('Book Appointment')

class PaymentForm(FlaskForm):
    """Payment form"""
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    payment_method = SelectField('Payment Method', choices=[
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('transfer', 'Bank Transfer'),
        ('other', 'Other')
    ])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Process Payment')

class RoleForm(FlaskForm):
    """Role form"""
    name = StringField('Role Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Role')

class PermissionForm(FlaskForm):
    """Permission form"""
    name = StringField('Permission Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Permission')

class CategoryForm(FlaskForm):
    """Category form"""
    name = StringField('Category Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional()])
    color = StringField('Color', validators=[Optional(), Length(max=7)])
    icon = StringField('Icon', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Save Category')

class DepartmentForm(FlaskForm):
    """Department form"""
    name = StringField('Department Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional()])
    manager_id = SelectField('Manager', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Department')

class SystemSettingForm(FlaskForm):
    """System setting form"""
    key = StringField('Setting Key', validators=[DataRequired(), Length(max=100)])
    value = TextAreaField('Value', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Setting')

class ComprehensiveStaffForm(FlaskForm):
    """Comprehensive staff form with all fields"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    
    # Personal Details
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    date_of_joining = DateField('Date of Joining', validators=[Optional()])
    designation = StringField('Designation', validators=[Optional(), Length(max=100)])
    staff_code = StringField('Staff Code', validators=[Optional(), Length(max=20)])
    notes_bio = TextAreaField('Notes/Bio', validators=[Optional()])
    
    # ID Verification
    aadhaar_number = StringField('Aadhaar Number', validators=[Optional(), Length(max=12)])
    pan_number = StringField('PAN Number', validators=[Optional(), Length(max=10)])
    verification_status = BooleanField('Verified', default=False)
    
    # Role and Department
    role_id = SelectField('Role', coerce=int, validators=[Optional()])
    department_id = SelectField('Department', coerce=int, validators=[Optional()])
    assigned_services = SelectMultipleField('Assigned Services', coerce=int, validators=[Optional()])
    
    # Basic Schedule (Legacy Support)
    shift_start_time = TimeField('Shift Start Time', validators=[Optional()])
    shift_end_time = TimeField('Shift End Time', validators=[Optional()])
    break_time = StringField('Break Time', validators=[Optional(), Length(max=50)])
    weekly_off_days = StringField('Weekly Off Days', validators=[Optional(), Length(max=20)])
    
    # Working Days Checkboxes (Legacy Support)
    monday = BooleanField('Monday', default=True)
    tuesday = BooleanField('Tuesday', default=True)
    wednesday = BooleanField('Wednesday', default=True)
    thursday = BooleanField('Thursday', default=True)
    friday = BooleanField('Friday', default=True)
    saturday = BooleanField('Saturday', default=False)
    sunday = BooleanField('Sunday', default=False)
    
    # Performance & Commission
    commission_percentage = FloatField('Commission (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    hourly_rate = FloatField('Hourly Rate', validators=[Optional(), NumberRange(min=0)])
    
    # Facial Recognition
    enable_face_checkin = BooleanField('Enable Face Check-in', default=True)
    
    # Status
    is_active = BooleanField('Active', default=True)
    
    # Password
    password = PasswordField('Password', validators=[Optional()])
    
    submit = SubmitField('Save Staff Member')

class StaffScheduleRangeForm(FlaskForm):
    """Enhanced date range-based schedule form"""
    schedule_name = StringField('Schedule Name', validators=[DataRequired(), Length(max=100)])
    description = StringField('Description', validators=[Optional(), Length(max=255)])
    
    # Date Range
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    
    # Working Days in this Range
    monday = BooleanField('Monday', default=True)
    tuesday = BooleanField('Tuesday', default=True)
    wednesday = BooleanField('Wednesday', default=True)
    thursday = BooleanField('Thursday', default=True)
    friday = BooleanField('Friday', default=True)
    saturday = BooleanField('Saturday', default=False)
    sunday = BooleanField('Sunday', default=False)
    
    # Shift Times for this Range
    shift_start_time = TimeField('Shift Start Time', validators=[Optional()])
    shift_end_time = TimeField('Shift End Time', validators=[Optional()])
    break_time = StringField('Break Time', validators=[Optional(), Length(max=50)])
    
    # Priority (higher number = higher priority)
    priority = IntegerField('Priority', validators=[Optional(), NumberRange(min=1, max=10)], default=1)
    
    submit = SubmitField('Save Schedule Range')