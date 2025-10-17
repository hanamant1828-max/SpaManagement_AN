"""
Booking Helper Functions

This module contains utility and helper functions for the booking system,
including staff schedule retrieval, time conversions, and date formatting.
"""

from datetime import datetime, date, time, timedelta
from models import ShiftManagement, ShiftLogs
import re


def get_staff_schedule_for_date(staff_id, target_date):
    """Get the detailed schedule for a staff member on a specific date
    
    Args:
        staff_id (int): The ID of the staff member
        target_date (date): The target date to check schedule for
        
    Returns:
        dict: Schedule information including shift times, breaks, and working status
        None: If no schedule found for the date
    """
    try:
        # Get shift management for this staff member and date
        shift_management = ShiftManagement.query.filter(
            ShiftManagement.staff_id == staff_id,
            ShiftManagement.from_date <= target_date,
            ShiftManagement.to_date >= target_date
        ).first()

        if not shift_management:
            return None

        # Get specific shift log for this date
        shift_log = ShiftLogs.query.filter(
            ShiftLogs.shift_management_id == shift_management.id,
            ShiftLogs.individual_date == target_date
        ).first()

        if not shift_log:
            return None

        return {
            'schedule_id': shift_management.id,
            'daily_schedule_id': shift_log.id,
            'schedule_name': f'Shift {target_date}',
            'shift_start_time': shift_log.shift_start_time,
            'shift_end_time': shift_log.shift_end_time,
            'break_start_time': shift_log.break_start_time,
            'break_end_time': shift_log.break_end_time,
            'break_duration_minutes': 0,
            'break_time': shift_log.get_break_time_display() if shift_log.break_start_time and shift_log.break_end_time else 'No break',
            'is_working_day': shift_log.status in ['scheduled', 'completed'],
            'notes': ''
        }

    except Exception as e:
        print(f"Error getting staff schedule for date: {e}")
        return None


def parse_break_time(break_time_string):
    """Parse break time string like '60 minutes (13:00 - 14:00)' to get start and end times
    
    Args:
        break_time_string (str): Break time string with format like '60 minutes (13:00 - 14:00)'
        
    Returns:
        tuple: (break_start, break_end) as strings, or (None, None) if parsing fails
    """
    if not break_time_string:
        return None, None

    try:
        # Look for pattern like "(13:00 - 14:00)" in the break_time string
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


def time_to_minutes(time_str):
    """Convert time string (HH:MM) to total minutes from midnight
    
    Args:
        time_str (str): Time in format 'HH:MM'
        
    Returns:
        int: Total minutes from midnight
    """
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes


def minutes_to_time(minutes):
    """Convert total minutes from midnight to time string (HH:MM)
    
    Args:
        minutes (int): Total minutes from midnight
        
    Returns:
        str: Time in format 'HH:MM'
    """
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def format_time_12h(time_obj):
    """Format a time object to 12-hour format with AM/PM
    
    Args:
        time_obj (time): Python time object
        
    Returns:
        str: Time formatted as 'HH:MM AM/PM' or None if input is None
    """
    if not time_obj:
        return None
    return time_obj.strftime('%I:%M %p')


def format_datetime_12h(datetime_obj):
    """Format a datetime object to 12-hour format with AM/PM
    
    Args:
        datetime_obj (datetime): Python datetime object
        
    Returns:
        str: Time formatted as 'HH:MM AM/PM' or None if input is None
    """
    if not datetime_obj:
        return None
    return datetime_obj.strftime('%I:%M %p')


def generate_time_slots(start_hour=8, end_hour=20, slot_duration=15, selected_date=None):
    """Generate time slots with flexible durations
    
    Args:
        start_hour (int): Starting hour (default 8 AM)
        end_hour (int): Ending hour (default 8 PM)
        slot_duration (int): Duration of each slot in minutes (default 15)
        selected_date (date): Date for the slots (default today)
        
    Returns:
        list: List of dictionaries containing time slot information
    """
    if selected_date is None:
        selected_date = date.today()
        
    time_slots = []
    start_time = datetime.combine(selected_date, datetime.min.time().replace(hour=start_hour))
    end_time = datetime.combine(selected_date, datetime.min.time().replace(hour=end_hour))

    current_time = start_time
    while current_time < end_time:
        time_slots.append({
            'start_time': current_time,
            'end_time': current_time + timedelta(minutes=slot_duration),
            'duration': slot_duration
        })
        current_time += timedelta(minutes=slot_duration)

    return time_slots


def check_time_overlap(start1, end1, start2, end2):
    """Check if two time ranges overlap
    
    Args:
        start1: Start of first time range (can be time string 'HH:MM' or datetime)
        end1: End of first time range
        start2: Start of second time range
        end2: End of second time range
        
    Returns:
        bool: True if times overlap, False otherwise
    """
    # Convert string times to minutes if needed
    if isinstance(start1, str):
        start1 = time_to_minutes(start1)
        end1 = time_to_minutes(end1)
        start2 = time_to_minutes(start2)
        end2 = time_to_minutes(end2)
    
    # For datetime objects, just use direct comparison
    return end1 > start2 and start1 < end2


def parse_date_string(date_str):
    """Parse a date string in various formats to a date object
    
    Args:
        date_str (str): Date string in format 'YYYY-MM-DD' or similar
        
    Returns:
        date: Python date object or None if parsing fails
    """
    if not date_str:
        return None
        
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        try:
            return datetime.strptime(date_str, '%d/%m/%Y').date()
        except ValueError:
            return None


def get_day_of_week_name(date_obj):
    """Get the name of the day of week for a given date
    
    Args:
        date_obj (date): Python date object
        
    Returns:
        str: Day name (e.g., 'Monday', 'Tuesday')
    """
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return day_names[date_obj.weekday()]


def calculate_duration_minutes(start_time, end_time):
    """Calculate duration in minutes between two times
    
    Args:
        start_time: Start time (datetime or time object)
        end_time: End time (datetime or time object)
        
    Returns:
        int: Duration in minutes
    """
    if isinstance(start_time, datetime) and isinstance(end_time, datetime):
        return int((end_time - start_time).total_seconds() / 60)
    elif isinstance(start_time, time) and isinstance(end_time, time):
        start_dt = datetime.combine(date.today(), start_time)
        end_dt = datetime.combine(date.today(), end_time)
        return int((end_dt - start_dt).total_seconds() / 60)
    else:
        return 0
