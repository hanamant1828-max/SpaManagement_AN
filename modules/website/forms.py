from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField
from wtforms.validators import DataRequired, Email, Optional, Length

class OnlineBookingForm(FlaskForm):
    """Form for online appointment booking"""
    client_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    client_phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    client_email = StringField('Email', validators=[Optional(), Email()])
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    appointment_date = DateField('Preferred Date', validators=[DataRequired()])
    appointment_time = TimeField('Preferred Time', validators=[DataRequired()])
    notes = TextAreaField('Special Requests', validators=[Optional(), Length(max=500)])

class ContactForm(FlaskForm):
    """Form for contact inquiries"""
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=3, max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])
