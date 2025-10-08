"""
Bookings-related database queries
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from app import db
from models import Appointment, Customer, Service, User

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

def parse_break_time(break_time_string):
    """Parse break time string like '60 minutes (13:00 - 14:00)' to get start and end times"""
    if not break_time_string:
        return None, None

    try:
        # Look for pattern like "(13:00 - 14:00)" in the break_time string
        import re
        pattern = r'\((\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})\)'
        match = re.search(pattern, break_time_string)

        if match:
            break_start = match.group(1)  # e.g., "13:00"
            break_end = match.group(2)    # e.g., "14:00"
            return break_start, break_end
        else:
            return None, None
    except Exception as e:
        print(f"Error parsing break time '{break_time_string}': {e}")
        return None, None

def get_staff_schedule_for_date(staff_id, filter_date):
    """Get staff schedule for a specific date from StaffScheduleRange"""
    if not staff_id:
        return None

    from models import StaffScheduleRange

    # Get schedule that covers the filter_date
    schedule = StaffScheduleRange.query.filter(
        StaffScheduleRange.staff_id == staff_id,
        StaffScheduleRange.start_date <= filter_date,
        StaffScheduleRange.end_date >= filter_date,
        StaffScheduleRange.is_active == True
    ).order_by(StaffScheduleRange.priority.desc()).first()

    if not schedule:
        return None

    # Check if staff is working on this day of the week
    weekday = filter_date.weekday()  # Monday = 0, Sunday = 6
    working_days = [schedule.monday, schedule.tuesday, schedule.wednesday, 
                   schedule.thursday, schedule.friday, schedule.saturday, schedule.sunday]

    if not working_days[weekday]:
        return None  # Staff is not working on this day

    return schedule

def get_time_slots(filter_date, staff_id=None, service_id=None):
    """Get available time slots for a given date"""
    try:
        from datetime import datetime, timedelta

        # Generate time slots from 9 AM to 6 PM
        time_slots = []
        start_hour = 9
        end_hour = 18

        for hour in range(start_hour, end_hour):
            for minutes in [0, 30]:
                slot_time = datetime.combine(filter_date, datetime.min.time().replace(hour=hour, minute=minutes))

                # Check if this slot is available
                existing_appointments = get_appointments_by_date(filter_date)
                is_available = True

                for appointment in existing_appointments:
                    if (appointment.appointment_date.time() == slot_time.time() and
                        (not staff_id or appointment.staff_id == staff_id)):
                        is_available = False
                        break

                time_slots.append({
                    'time': slot_time.strftime('%H:%M'),
                    'display_time': slot_time.strftime('%I:%M %p'),
                    'datetime': slot_time,  # Add the datetime object
                    'available': is_available
                })

        return time_slots

    except Exception as e:
        print(f"Error getting time slots: {e}")
        return []

def get_active_clients():
    """Get all active clients"""
    return Customer.query.filter_by(is_active=True).order_by(Customer.first_name).all()

def get_active_services():
    """Get all active services for dropdown"""
    try:
        from models import Service
        services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
        print(f"Retrieved {len(services)} active services from database")

        # Debug: Print each service
        for service in services:
            print(f"Service found: ID={service.id}, Name={service.name}, Price={service.price}, Active={service.is_active}")

        # If no services found, check if there are any services at all
        if not services:
            all_services = Service.query.all()
            print(f"No active services found. Total services in database: {len(all_services)}")
            if all_services:
                print("Available services (all):")
                for service in all_services:
                    print(f"  - {service.name} (Active: {service.is_active})")
            else:
                print("No services found in database at all!")

        return services
    except Exception as e:
        print(f"Error retrieving active services: {e}")
        import traceback
        traceback.print_exc()
        return []

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
    """Create a new appointment
    
    Returns:
        tuple: (appointment, error_message) where appointment is the created Appointment object or None,
               and error_message is a string describing the error or None if successful
    """
    try:
        # Calculate end_time if not provided
        if 'end_time' not in appointment_data and 'service_id' in appointment_data:
            service = Service.query.get(appointment_data['service_id'])
            if service and 'appointment_date' in appointment_data:
                appointment_date = appointment_data['appointment_date']
                if isinstance(appointment_date, str):
                    appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d %H:%M')
                appointment_data['end_time'] = appointment_date + timedelta(minutes=service.duration)

        # Check for client conflicts - prevent same client from having multiple appointments at same time
        if 'client_id' in appointment_data and 'appointment_date' in appointment_data and 'end_time' in appointment_data:
            client_id = appointment_data['client_id']
            start_time = appointment_data['appointment_date']
            end_time = appointment_data['end_time']
            
            if isinstance(start_time, str):
                start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M')
            if isinstance(end_time, str):
                end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M')
            
            # Check existing appointments for this client
            existing_appointments = Appointment.query.filter(
                Appointment.client_id == client_id,
                Appointment.status.in_(['scheduled', 'confirmed']),
                func.date(Appointment.appointment_date) == start_time.date()
            ).all()
            
            for existing in existing_appointments:
                existing_start = existing.appointment_date
                existing_end = existing.end_time
                
                # Skip appointments without end_time or calculate it from service duration
                if not existing_end:
                    if existing.service and existing.service.duration:
                        existing_end = existing_start + timedelta(minutes=existing.service.duration)
                    else:
                        # Skip if we can't determine the end time
                        continue
                
                # Check for overlap
                if start_time < existing_end and end_time > existing_start:
                    error_msg = f'Client already has an appointment from {existing_start.strftime("%I:%M %p")} to {existing_end.strftime("%I:%M %p")}'
                    print(f"❌ Client conflict: {error_msg}")
                    return None, error_msg

        appointment = Appointment(**appointment_data)
        db.session.add(appointment)
        db.session.commit()
        return appointment, None
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error creating appointment: {str(e)}"
        print(error_msg)
        return None, error_msg

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