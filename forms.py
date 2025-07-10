from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, FloatField, IntegerField, DateField, DateTimeField, BooleanField, TimeField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange
from wtforms.widgets import TextArea

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
    duration = IntegerField('Duration (minutes)', validators=[DataRequired(), NumberRange(min=1)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Category', choices=[
        ('hair', 'Hair'),
        ('facial', 'Facial'),
        ('massage', 'Massage'),
        ('nails', 'Nails'),
        ('body', 'Body Treatments'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    is_active = BooleanField('Active', default=True)

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
    category = SelectField('Category', choices=[
        ('consumables', 'Consumables'),
        ('equipment', 'Equipment'),
        ('retail', 'Retail Products'),
        ('cleaning', 'Cleaning Supplies'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    current_stock = IntegerField('Current Stock', validators=[DataRequired(), NumberRange(min=0)])
    min_stock_level = IntegerField('Minimum Stock Level', validators=[DataRequired(), NumberRange(min=0)])
    unit_price = FloatField('Unit Price', validators=[Optional(), NumberRange(min=0)])
    supplier_name = StringField('Supplier Name', validators=[Optional(), Length(max=100)])
    supplier_contact = StringField('Supplier Contact', validators=[Optional(), Length(max=100)])
    expiry_date = DateField('Expiry Date', validators=[Optional()])

class ExpenseForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired(), Length(max=200)])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Category', choices=[
        ('utilities', 'Utilities'),
        ('supplies', 'Supplies'),
        ('maintenance', 'Maintenance'),
        ('marketing', 'Marketing'),
        ('rent', 'Rent'),
        ('salaries', 'Salaries'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    expense_date = DateField('Expense Date', validators=[DataRequired()])
    receipt_number = StringField('Receipt Number', validators=[Optional(), Length(max=50)])
    notes = TextAreaField('Notes', validators=[Optional()])

class PackageForm(FlaskForm):
    name = StringField('Package Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    duration_months = SelectField('Duration', choices=[
        (3, '3 Months'),
        (6, '6 Months'),
        (12, '12 Months')
    ], coerce=int, validators=[DataRequired()])
    total_price = FloatField('Total Price', validators=[DataRequired(), NumberRange(min=0)])
    discount_percentage = FloatField('Discount %', validators=[Optional(), NumberRange(min=0, max=100)])

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
