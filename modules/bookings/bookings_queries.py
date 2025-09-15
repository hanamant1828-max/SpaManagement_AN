"""
Bookings-related database queries
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from app import db
# Late imports to avoid circular dependency

def get_appointments_by_date(filter_date):
    """Get appointments for a specific date with full details"""
    from models import Appointment
    return Appointment.query.filter(
        func.date(Appointment.appointment_date) == filter_date
    ).order_by(Appointment.appointment_date).all()

def get_appointments_by_date_range(start_date, end_date):
    """Get appointments within a date range"""
    from models import Appointment
    return Appointment.query.filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date
    ).order_by(Appointment.appointment_date).all()

def get_staff_schedule(staff_id, filter_date):
    """Get staff schedule for a specific date"""
    from models import Appointment
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
    """Generate available time slots for booking with explicit status classification"""
    # Default business hours (9 AM to 6 PM) - fallback if no staff schedule
    business_start = 9
    business_end = 18
    slot_duration = 30  # 30-minute slots

    slots = []
    
    # Get existing appointments for the date
    existing_appointments = get_appointments_by_date(filter_date)

    # Get service duration if specified
    service_duration = 60  # Default 60 minutes
    if service_id:
        from models import Service
        service = Service.query.get(service_id)
        if service:
            service_duration = service.duration

    # Get staff schedule and break times if staff is specified
    break_start_time = None
    break_end_time = None
    shift_start_time = None
    shift_end_time = None
    staff_schedule = None
    
    if staff_id:
        staff_schedule = get_staff_schedule_for_date(staff_id, filter_date)
        if staff_schedule:
            print(f"Found schedule for staff {staff_id}: {staff_schedule.schedule_name}")
            print(f"Break time: {staff_schedule.break_time}")
            
            # Get break times
            break_start, break_end = parse_break_time(staff_schedule.break_time)
            if break_start and break_end:
                try:
                    break_start_time = datetime.combine(filter_date, datetime.strptime(break_start, '%H:%M').time())
                    break_end_time = datetime.combine(filter_date, datetime.strptime(break_end, '%H:%M').time())
                    print(f"Parsed break: {break_start_time.time()} - {break_end_time.time()}")
                except ValueError as e:
                    print(f"Error parsing break times: {e}")
            else:
                print(f"Could not parse break times from: '{staff_schedule.break_time}'")
            
            # Get shift times - use these as the iteration bounds if available
            if staff_schedule.shift_start_time and staff_schedule.shift_end_time:
                shift_start_time = datetime.combine(filter_date, staff_schedule.shift_start_time)
                shift_end_time = datetime.combine(filter_date, staff_schedule.shift_end_time)
                print(f"Shift hours: {shift_start_time.time()} - {shift_end_time.time()}")
        else:
            print(f"No schedule found for staff {staff_id} on {filter_date}")

    # Determine iteration bounds
    if staff_id and shift_start_time and shift_end_time:
        # Use actual shift hours for this staff member
        current_time = shift_start_time
        end_time = shift_end_time
    else:
        # Use default business hours
        current_time = datetime.combine(filter_date, datetime.min.time().replace(hour=business_start))
        end_time = datetime.combine(filter_date, datetime.min.time().replace(hour=business_end))

    # Generate slots within the determined time range
    while current_time < end_time:
        slot_end = current_time + timedelta(minutes=service_duration)
        
        # Determine slot status
        if staff_id and not staff_schedule:
            # Staff not scheduled to work
            status = 'off_shift'
        elif staff_id and shift_start_time and shift_end_time:
            # Staff has a schedule, check various conditions
            if current_time < shift_start_time or slot_end > shift_end_time:
                # Outside shift hours
                status = 'off_shift'
            elif break_start_time and break_end_time:
                # Check if slot overlaps with break time
                if not (slot_end <= break_start_time or current_time >= break_end_time):
                    status = 'break'
                else:
                    # Check for existing appointments
                    status = 'available'
                    for appointment in existing_appointments:
                        if staff_id and appointment.staff_id != staff_id:
                            continue
                        appointment_start = appointment.appointment_date
                        appointment_end = appointment_start + timedelta(minutes=appointment.service.duration if appointment.service else 60)
                        if not (current_time >= appointment_end or slot_end <= appointment_start):
                            status = 'booked'
                            break
            else:
                # No break time, just check appointments
                status = 'available'
                for appointment in existing_appointments:
                    if staff_id and appointment.staff_id != staff_id:
                        continue
                    appointment_start = appointment.appointment_date
                    appointment_end = appointment_start + timedelta(minutes=appointment.service.duration if appointment.service else 60)
                    if not (current_time >= appointment_end or slot_end <= appointment_start):
                        status = 'booked'
                        break
        else:
            # No staff specified, check appointments only
            status = 'available'
            for appointment in existing_appointments:
                appointment_start = appointment.appointment_date
                appointment_end = appointment_start + timedelta(minutes=appointment.service.duration if appointment.service else 60)
                if not (current_time >= appointment_end or slot_end <= appointment_start):
                    status = 'booked'
                    break

        # Create slot object
        slot = {
            'time': current_time.strftime('%H:%M'),
            'status': status,
            'available': status == 'available',
            'display_time': current_time.strftime('%I:%M %p'),
            'iso_time': current_time.isoformat()  # JSON-serializable time
        }
        
        slots.append(slot)
        current_time += timedelta(minutes=slot_duration)

    return slots

def get_active_clients():
    """Get all active clients"""
    from models import Customer
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
    from models import User
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
    from models import Service, Appointment
    try:
        # Calculate end_time if not provided
        if 'end_time' not in appointment_data and 'service_id' in appointment_data:
            service = Service.query.get(appointment_data['service_id'])
            if service and 'appointment_date' in appointment_data:
                appointment_date = appointment_data['appointment_date']
                if isinstance(appointment_date, str):
                    appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d %H:%M')
                appointment_data['end_time'] = appointment_date + timedelta(minutes=service.duration)
        
        appointment = Appointment(**appointment_data)
        db.session.add(appointment)
        db.session.commit()
        return appointment
    except Exception as e:
        db.session.rollback()
        print(f"Error creating appointment: {e}")
        return None

def update_appointment(appointment_id, appointment_data):
    """Update an existing appointment"""
    from models import Appointment
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        for key, value in appointment_data.items():
            setattr(appointment, key, value)
        db.session.commit()
    return appointment

def delete_appointment(appointment_id):
    """Delete an appointment"""
    from models import Appointment
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        db.session.delete(appointment)
        db.session.commit()
        return True
    return False

def get_appointment_by_id(appointment_id):
    """Get appointment by ID"""
    from models import Appointment
    return Appointment.query.get(appointment_id)