"""
Bookings-related database queries
"""
from datetime import datetime, date
from sqlalchemy import func
from app import db
from models import Appointment, Client, Service, User

def get_appointments_by_date(filter_date):
    """Get appointments for a specific date"""
    return Appointment.query.filter(
        func.date(Appointment.appointment_date) == filter_date
    ).order_by(Appointment.appointment_date).all()

def get_active_clients():
    """Get all active clients"""
    return Client.query.filter_by(is_active=True).order_by(Client.first_name).all()

def get_active_services():
    """Get all active services"""
    return Service.query.filter_by(is_active=True).order_by(Service.name).all()

def get_staff_members():
    """Get all staff members"""
    return User.query.filter(
        User.role.in_(['staff', 'manager', 'admin']), 
        User.is_active == True
    ).order_by(User.first_name).all()

def create_appointment(appointment_data):
    """Create a new appointment"""
    appointment = Appointment(**appointment_data)
    db.session.add(appointment)
    db.session.commit()
    return appointment

def update_appointment(appointment_id, appointment_data):
    """Update an existing appointment"""
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        for key, value in appointment_data.items():
            setattr(appointment, key, value)
        db.session.commit()
    return appointment

def delete_appointment(appointment_id):
    """Delete an appointment"""
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        db.session.delete(appointment)
        db.session.commit()
        return True
    return False

def get_appointment_by_id(appointment_id):
    """Get appointment by ID"""
    return Appointment.query.get(appointment_id)