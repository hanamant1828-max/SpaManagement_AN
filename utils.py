"""
Utility functions for the Spa Management System
"""
from datetime import datetime, date, timedelta
import re

def format_currency(amount):
    """Format amount as currency"""
    if amount is None:
        return "$0.00"
    return f"${amount:.2f}"

def format_date(date_obj):
    """Format date for display"""
    if date_obj is None:
        return "N/A"
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime('%Y-%m-%d')

def format_datetime(datetime_obj):
    """Format datetime for display"""
    if datetime_obj is None:
        return "N/A"
    if isinstance(datetime_obj, str):
        return datetime_obj
    return datetime_obj.strftime('%Y-%m-%d %H:%M')

def format_time(time_obj):
    """Format time for display"""
    if time_obj is None:
        return "N/A"
    if isinstance(time_obj, str):
        return time_obj
    return time_obj.strftime('%H:%M')

def calculate_age(birth_date):
    """Calculate age from birth date"""
    if birth_date is None:
        return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def format_phone(phone):
    """Format phone number"""
    if not phone:
        return ""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone

def get_status_badge_class(status):
    """Get CSS class for status badges"""
    status_classes = {
        'active': 'badge-success',
        'inactive': 'badge-secondary',
        'pending': 'badge-warning',
        'confirmed': 'badge-info',
        'completed': 'badge-success',
        'cancelled': 'badge-danger',
        'paid': 'badge-success',
        'unpaid': 'badge-danger',
        'partial': 'badge-warning'
    }
    return status_classes.get(status.lower() if status else '', 'badge-secondary')

def truncate_text(text, length=50):
    """Truncate text to specified length"""
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length-3] + "..."

def calculate_percentage(part, total):
    """Calculate percentage"""
    if total == 0:
        return 0
    return round((part / total) * 100, 2)

def generate_invoice_number():
    """Generate unique invoice number"""
    return f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def get_next_business_day(start_date=None):
    """Get next business day (Monday-Friday)"""
    if start_date is None:
        start_date = date.today()
    
    next_day = start_date + timedelta(days=1)
    while next_day.weekday() >= 5:  # Saturday = 5, Sunday = 6
        next_day += timedelta(days=1)
    return next_day

def format_duration(minutes):
    """Format duration in minutes to hours and minutes"""
    if minutes is None:
        return "N/A"
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"