from datetime import datetime, date
import calendar

def format_currency(amount):
    """Format amount as currency"""
    if amount is None:
        return "$0.00"
    return f"${amount:.2f}"

def format_datetime(dt):
    """Format datetime for display"""
    if not dt:
        return ""
    return dt.strftime("%m/%d/%Y %I:%M %p")

def format_date(d):
    """Format date for display"""
    if not d:
        return ""
    return d.strftime("%m/%d/%Y")

def format_time(t):
    """Format time for display"""
    if not t:
        return ""
    return t.strftime("%I:%M %p")

def get_status_class(status):
    """Get Bootstrap class for status"""
    status_classes = {
        'scheduled': 'info',
        'confirmed': 'primary',
        'in_progress': 'warning',
        'completed': 'success',
        'cancelled': 'danger',
        'no_show': 'secondary',
        'pending': 'warning',
        'paid': 'success',
        'overdue': 'danger'
    }
    return status_classes.get(status, 'secondary')

def get_month_name(month_num):
    """Get month name from number"""
    return calendar.month_name[month_num]

def calculate_age(birth_date):
    """Calculate age from birth date"""
    if not birth_date:
        return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def get_day_name(day_num):
    """Get day name from number (0=Monday)"""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[day_num] if 0 <= day_num <= 6 else ''

def truncate_text(text, length=50):
    """Truncate text to specified length"""
    if not text:
        return ""
    return text[:length] + "..." if len(text) > length else text

def get_priority_class(priority):
    """Get Bootstrap class for priority levels"""
    priority_classes = {
        'low': 'success',
        'medium': 'warning',
        'high': 'danger',
        'urgent': 'danger'
    }
    return priority_classes.get(priority, 'secondary')

def is_business_hours(dt):
    """Check if datetime is within business hours (9 AM - 8 PM)"""
    if not dt:
        return False
    return 9 <= dt.hour <= 20

def get_next_business_day(current_date):
    """Get next business day (Monday-Saturday)"""
    next_day = current_date
    while next_day.weekday() == 6:  # Sunday
        next_day += timedelta(days=1)
    return next_day

def calculate_service_end_time(start_time, duration_minutes):
    """Calculate service end time"""
    return start_time + timedelta(minutes=duration_minutes)

def validate_appointment_time(appointment_date, duration, staff_id):
    """Validate if appointment time slot is available"""
    from models import Appointment
    end_time = appointment_date + timedelta(minutes=duration)
    
    # Check for overlapping appointments
    overlapping = Appointment.query.filter(
        Appointment.staff_id == staff_id,
        Appointment.status.in_(['scheduled', 'confirmed', 'in_progress']),
        or_(
            and_(Appointment.appointment_date <= appointment_date, Appointment.end_time > appointment_date),
            and_(Appointment.appointment_date < end_time, Appointment.end_time >= end_time),
            and_(Appointment.appointment_date >= appointment_date, Appointment.end_time <= end_time)
        )
    ).first()
    
    return overlapping is None

def generate_invoice_number():
    """Generate unique invoice number"""
    today = date.today()
    prefix = today.strftime("INV%Y%m%d")
    
    from models import Invoice
    last_invoice = Invoice.query.filter(
        Invoice.invoice_number.like(f"{prefix}%")
    ).order_by(Invoice.invoice_number.desc()).first()
    
    if last_invoice:
        last_num = int(last_invoice.invoice_number[-3:])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"{prefix}{new_num:03d}"
