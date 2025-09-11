"""
Check-in related database queries
"""
from datetime import datetime, date
from sqlalchemy import func, and_
from app import db
# Late imports to avoid circular dependency

def get_todays_appointments():
    """Get today's appointments for check-in"""
    from models import Appointment
    today = date.today()
    return Appointment.query.filter(
        func.date(Appointment.appointment_date) == today,
        Appointment.status.in_(['scheduled', 'confirmed'])
    ).order_by(Appointment.appointment_date).all()

def get_appointment_by_id(appointment_id):
    """Get appointment by ID"""
    from models import Appointment
    return Appointment.query.get(appointment_id)

def check_in_appointment(appointment_id):
    """Check in an appointment"""
    from models import Appointment
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        appointment.status = 'checked_in'
        appointment.checked_in_at = datetime.utcnow()
        db.session.commit()
    return appointment

def get_client_by_phone(phone):
    """Get client by phone number"""
    from models import Customer
    return Customer.query.filter_by(phone=phone, is_active=True).first()

def get_client_appointments_today(client_id):
    """Get client's appointments for today"""
    today = date.today()
    return Appointment.query.filter(
        Appointment.client_id == client_id,
        func.date(Appointment.appointment_date) == today
    ).order_by(Appointment.appointment_date).all()