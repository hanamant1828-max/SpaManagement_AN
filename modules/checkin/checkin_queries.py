"""
Check-in related database queries
"""
from datetime import datetime, date
from sqlalchemy import func, and_
from app import db
from models import Appointment, Customer, User

def get_todays_appointments():
    """Get today's appointments for check-in"""
    today = date.today()
    return Appointment.query.filter(
        func.date(Appointment.appointment_date) == today,
        Appointment.status.in_(['scheduled', 'confirmed'])
    ).order_by(Appointment.appointment_date).all()

def get_appointment_by_id(appointment_id):
    """Get appointment by ID"""
    return Appointment.query.get(appointment_id)

def check_in_appointment(appointment_id):
    """Check in an appointment"""
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        appointment.status = 'checked_in'
        appointment.checked_in_at = datetime.utcnow()
        db.session.commit()
    return appointment

def get_client_by_phone(phone):
    """Get client by phone number"""
    return Customer.query.filter_by(phone=phone, is_active=True).first()

def get_client_appointments_today(client_id):
    """Get client's appointments for today"""
    today = date.today()
    return Appointment.query.filter(
        Appointment.client_id == client_id,
        func.date(Appointment.appointment_date) == today
    ).order_by(Appointment.appointment_date).all()