"""
Bookings-related database queries
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from app import db
from models import Appointment, Client, Service, User

def get_appointments_by_date(filter_date):
    """Get appointments for a specific date with full details"""
    return Appointment.query.filter(
        func.date(Appointment.appointment_date) == filter_date
    ).order_by(Appointment.appointment_date).all()

def get_appointments_by_date_range(start_date, end_date):
    """Get appointments within a date range"""
    return Appointment.query.filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date
    ).order_by(Appointment.appointment_date).all()

def get_staff_schedule(staff_id, filter_date):
    """Get staff schedule for a specific date"""
    return Appointment.query.filter(
        Appointment.staff_id == staff_id,
        func.date(Appointment.appointment_date) == filter_date
    ).order_by(Appointment.appointment_date).all()

def get_time_slots(filter_date, staff_id=None, service_id=None):
    """Generate available time slots for booking"""
    # Define business hours (9 AM to 6 PM)
    business_start = 9
    business_end = 18
    slot_duration = 30  # 30-minute slots
    
    slots = []
    current_time = datetime.combine(filter_date, datetime.min.time().replace(hour=business_start))
    end_time = datetime.combine(filter_date, datetime.min.time().replace(hour=business_end))
    
    # Get existing appointments for the date
    existing_appointments = get_appointments_by_date(filter_date)
    
    # Get service duration if specified
    service_duration = 60  # Default 60 minutes
    if service_id:
        service = Service.query.get(service_id)
        if service:
            service_duration = service.duration
    
    while current_time < end_time:
        # Check if slot is available
        is_available = True
        
        # Check against existing appointments
        for appointment in existing_appointments:
            if staff_id and appointment.staff_id != staff_id:
                continue
                
            appointment_start = appointment.appointment_date
            appointment_end = appointment_start + timedelta(minutes=appointment.service.duration if appointment.service else 60)
            
            # Check if slot conflicts with existing appointment
            slot_end = current_time + timedelta(minutes=service_duration)
            if not (current_time >= appointment_end or slot_end <= appointment_start):
                is_available = False
                break
        
        slots.append({
            'time': current_time.strftime('%H:%M'),
            'datetime': current_time,
            'available': is_available,
            'display_time': current_time.strftime('%I:%M %p')
        })
        
        current_time += timedelta(minutes=slot_duration)
    
    return slots

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

def get_appointment_stats(filter_date):
    """Get appointment statistics for a date"""
    appointments = get_appointments_by_date(filter_date)
    
    stats = {
        'total_appointments': len(appointments),
        'confirmed': len([a for a in appointments if a.status == 'confirmed']),
        'pending': len([a for a in appointments if a.status == 'pending']),
        'completed': len([a for a in appointments if a.status == 'completed']),
        'cancelled': len([a for a in appointments if a.status == 'cancelled']),
        'total_revenue': sum([a.amount or 0 for a in appointments if a.status == 'completed']),
        'staff_utilization': {}
    }
    
    # Calculate staff utilization
    staff_members = get_staff_members()
    for staff in staff_members:
        staff_appointments = [a for a in appointments if a.staff_id == staff.id]
        stats['staff_utilization'][staff.id] = {
            'name': staff.full_name,
            'appointments': len(staff_appointments),
            'hours_booked': sum([a.service.duration if a.service else 60 for a in staff_appointments]) / 60
        }
    
    return stats

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