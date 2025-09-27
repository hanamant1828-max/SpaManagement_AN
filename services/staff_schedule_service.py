"""
Professional Staff Schedule Integration Service
Connects Shift Scheduler, Staff Availability, and Booking Systems
"""

import re
from datetime import datetime, date, timedelta, time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class SlotStatus(Enum):
    """Enumeration of possible time slot statuses"""
    AVAILABLE = "available"
    BOOKED = "booked"
    BREAK = "break"
    OFF_SHIFT = "off_shift"
    UNAVAILABLE = "unavailable"

@dataclass
class TimeSlot:
    """Professional time slot representation"""
    time: str  # HH:MM format
    datetime_obj: datetime
    status: SlotStatus
    display_time: str  # 12-hour format
    iso_time: str  # ISO format for JSON
    reason: Optional[str] = None  # Why unavailable
    appointment_id: Optional[int] = None  # If booked
    
    @property
    def available(self) -> bool:
        """Backward compatibility"""
        return self.status == SlotStatus.AVAILABLE

@dataclass
class WorkingInterval:
    """Represents a continuous working period"""
    start_time: datetime
    end_time: datetime
    
    def contains(self, slot_start: datetime, slot_end: datetime) -> bool:
        """Check if a time slot is completely within this interval"""
        return slot_start >= self.start_time and slot_end <= self.end_time
    
    def overlaps_with(self, other_start: datetime, other_end: datetime) -> bool:
        """Check if this interval overlaps with another time range"""
        return not (self.end_time <= other_start or self.start_time >= other_end)

@dataclass
class StaffScheduleInfo:
    """Complete schedule information for a staff member"""
    staff_id: int
    staff_name: str
    schedule_date: date
    is_working: bool
    shift_start: Optional[time] = None
    shift_end: Optional[time] = None
    break_start: Optional[time] = None
    break_end: Optional[time] = None
    break_minutes: int = 0
    schedule_name: str = ""
    working_intervals: List[WorkingInterval] = None
    
    def __post_init__(self):
        if self.working_intervals is None:
            self.working_intervals = []

class StaffScheduleService:
    """Professional service for managing staff schedules and availability"""
    
    def __init__(self, slot_duration=15):
        # Support flexible slot durations: 5, 10, 15, 30, 45, 60 minutes
        self.valid_durations = [5, 10, 15, 30, 45, 60]
        if slot_duration not in self.valid_durations:
            slot_duration = 15  # Default to 15-minute slots for more flexibility
        self.slot_duration = slot_duration
    
    def parse_break_time(self, break_time_string: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse break time string from shift scheduler.
        Supports formats:
        - "60 minutes (13:00 - 14:00)"
        - "30 minutes (12:30 - 13:00)"
        - "90 minutes"
        """
        if not break_time_string:
            return None, None
        
        try:
            # Look for time range pattern: (HH:MM - HH:MM)
            pattern = r'\((\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})\)'
            match = re.search(pattern, break_time_string)
            
            if match:
                return match.group(1), match.group(2)
            
            # If no time range found, extract minutes and create default break
            minutes_pattern = r'(\d+)\s*minutes?'
            minutes_match = re.search(minutes_pattern, break_time_string)
            if minutes_match:
                minutes = int(minutes_match.group(1))
                # Default lunch break at 13:00
                start_time = time(13, 0)
                end_time = (datetime.combine(date.today(), start_time) + timedelta(minutes=minutes)).time()
                return start_time.strftime('%H:%M'), end_time.strftime('%H:%M')
            
            return None, None
            
        except Exception as e:
            print(f"Error parsing break time '{break_time_string}': {e}")
            return None, None
    
    def get_staff_schedule_for_date(self, staff_id: int, target_date: date) -> Optional[StaffScheduleInfo]:
        """
        Get comprehensive schedule information for a staff member on a specific date.
        Integrates with StaffScheduleRange model from shift scheduler.
        """
        from models import StaffScheduleRange, User
        
        if not staff_id:
            return None
        
        # Get staff information
        staff_member = User.query.get(staff_id)
        if not staff_member:
            return None
        
        # Find active schedule that covers the target date
        schedule = StaffScheduleRange.query.filter(
            StaffScheduleRange.staff_id == staff_id,
            StaffScheduleRange.start_date <= target_date,
            StaffScheduleRange.end_date >= target_date,
            StaffScheduleRange.is_active == True
        ).order_by(StaffScheduleRange.priority.desc()).first()
        
        if not schedule:
            # Staff has no schedule for this date
            return StaffScheduleInfo(
                staff_id=staff_id,
                staff_name=f"{staff_member.first_name} {staff_member.last_name}",
                schedule_date=target_date,
                is_working=False,
                schedule_name="No Schedule"
            )
        
        # Check if staff is working on this day of the week
        weekday = target_date.weekday()  # Monday = 0, Sunday = 6
        working_days = [
            schedule.monday, schedule.tuesday, schedule.wednesday, 
            schedule.thursday, schedule.friday, schedule.saturday, schedule.sunday
        ]
        
        if not working_days[weekday]:
            return StaffScheduleInfo(
                staff_id=staff_id,
                staff_name=f"{staff_member.first_name} {staff_member.last_name}",
                schedule_date=target_date,
                is_working=False,
                schedule_name=schedule.schedule_name
            )
        
        # Parse break times
        break_start_str, break_end_str = self.parse_break_time(schedule.break_time)
        break_start = None
        break_end = None
        break_minutes = 0
        
        if break_start_str and break_end_str:
            try:
                break_start = datetime.strptime(break_start_str, '%H:%M').time()
                break_end = datetime.strptime(break_end_str, '%H:%M').time()
                break_minutes = int((datetime.combine(target_date, break_end) - 
                                   datetime.combine(target_date, break_start)).total_seconds() / 60)
            except ValueError as e:
                print(f"Error parsing break times: {e}")
        
        # Create schedule info object
        schedule_info = StaffScheduleInfo(
            staff_id=staff_id,
            staff_name=f"{staff_member.first_name} {staff_member.last_name}",
            schedule_date=target_date,
            is_working=True,
            shift_start=schedule.shift_start_time,
            shift_end=schedule.shift_end_time,
            break_start=break_start,
            break_end=break_end,
            break_minutes=break_minutes,
            schedule_name=schedule.schedule_name
        )
        
        # Calculate working intervals (shift time minus break time)
        if schedule_info.shift_start and schedule_info.shift_end:
            shift_start_dt = datetime.combine(target_date, schedule_info.shift_start)
            shift_end_dt = datetime.combine(target_date, schedule_info.shift_end)
            
            if schedule_info.break_start and schedule_info.break_end:
                break_start_dt = datetime.combine(target_date, schedule_info.break_start)
                break_end_dt = datetime.combine(target_date, schedule_info.break_end)
                
                # Split shift into two intervals: before break and after break
                if break_start_dt > shift_start_dt:
                    schedule_info.working_intervals.append(
                        WorkingInterval(shift_start_dt, break_start_dt)
                    )
                
                if break_end_dt < shift_end_dt:
                    schedule_info.working_intervals.append(
                        WorkingInterval(break_end_dt, shift_end_dt)
                    )
            else:
                # No break - entire shift is working time
                schedule_info.working_intervals.append(
                    WorkingInterval(shift_start_dt, shift_end_dt)
                )
        
        return schedule_info
    
    def generate_time_slots(self, target_date: date, staff_id: Optional[int] = None, 
                          service_id: Optional[int] = None) -> List[TimeSlot]:
        """
        Generate professional time slots with comprehensive status information.
        Integrates shift scheduler data with booking system.
        """
        from modules.bookings.bookings_queries import get_appointments_by_date
        
        # Get service duration
        service_duration = 60  # Default 60 minutes
        if service_id:
            from models import Service
            service = Service.query.get(service_id)
            if service:
                service_duration = service.duration
        
        # Get existing appointments
        appointments = get_appointments_by_date(target_date)
        
        slots = []
        
        # Get staff schedule if specified
        staff_schedule = None
        if staff_id:
            staff_schedule = self.get_staff_schedule_for_date(staff_id, target_date)
            
            if not staff_schedule or not staff_schedule.is_working:
                # Staff not working - generate minimal slots showing unavailable
                business_start = datetime.combine(target_date, time(9, 0))
                business_end = datetime.combine(target_date, time(18, 0))
                
                current_time = business_start
                while current_time < business_end:
                    slots.append(TimeSlot(
                        time=current_time.strftime('%H:%M'),
                        datetime_obj=current_time,
                        status=SlotStatus.OFF_SHIFT,
                        display_time=current_time.strftime('%I:%M %p'),
                        iso_time=current_time.isoformat(),
                        reason="Staff not scheduled"
                    ))
                    current_time += timedelta(minutes=self.slot_duration)
                
                return slots
        
        # Determine time boundaries
        if staff_schedule and staff_schedule.working_intervals:
            # Use staff's working hours
            earliest_start = min(interval.start_time for interval in staff_schedule.working_intervals)
            latest_end = max(interval.end_time for interval in staff_schedule.working_intervals)
        else:
            # Use business hours
            earliest_start = datetime.combine(target_date, time(9, 0))
            latest_end = datetime.combine(target_date, time(18, 0))
        
        # Generate slots within the time range using flexible slot duration
        current_time = earliest_start
        while current_time < latest_end:
            slot_end = current_time + timedelta(minutes=self.slot_duration)
            
            # Determine slot status
            status = self._determine_slot_status(
                current_time, slot_end, staff_schedule, appointments, staff_id
            )
            
            # Create time slot
            slot = TimeSlot(
                time=current_time.strftime('%H:%M'),
                datetime_obj=current_time,
                status=status,
                display_time=current_time.strftime('%I:%M %p'),
                iso_time=current_time.isoformat(),
                reason=self._get_status_reason(status, current_time, staff_schedule)
            )
            
            # Add appointment ID if booked
            if status == SlotStatus.BOOKED:
                for appointment in appointments:
                    if staff_id and appointment.staff_id != staff_id:
                        continue
                    
                    apt_start = appointment.appointment_date
                    apt_end = apt_start + timedelta(minutes=appointment.service.duration if appointment.service else 60)
                    
                    if not (current_time >= apt_end or slot_end <= apt_start):
                        slot.appointment_id = appointment.id
                        break
            
            slots.append(slot)
            current_time += timedelta(minutes=self.slot_duration)
        
        return slots
    
    def _determine_slot_status(self, slot_start: datetime, slot_end: datetime, 
                             staff_schedule: Optional[StaffScheduleInfo], 
                             appointments: List[Any], staff_id: Optional[int]) -> SlotStatus:
        """Determine the status of a specific time slot"""
        
        # If no staff specified, only check appointments
        if not staff_id or not staff_schedule:
            for appointment in appointments:
                apt_start = appointment.appointment_date
                apt_end = apt_start + timedelta(minutes=appointment.service.duration if appointment.service else 60)
                if not (slot_start >= apt_end or slot_end <= apt_start):
                    return SlotStatus.BOOKED
            return SlotStatus.AVAILABLE
        
        # Staff not working
        if not staff_schedule.is_working:
            return SlotStatus.OFF_SHIFT
        
        # Check if slot is within any working interval
        in_working_interval = False
        for interval in staff_schedule.working_intervals:
            if interval.contains(slot_start, slot_end):
                in_working_interval = True
                break
        
        if not in_working_interval:
            # Check if it's during break time
            if (staff_schedule.break_start and staff_schedule.break_end):
                break_start_dt = datetime.combine(staff_schedule.schedule_date, staff_schedule.break_start)
                break_end_dt = datetime.combine(staff_schedule.schedule_date, staff_schedule.break_end)
                
                if not (slot_end <= break_start_dt or slot_start >= break_end_dt):
                    return SlotStatus.BREAK
            
            return SlotStatus.OFF_SHIFT
        
        # Check for existing appointments
        for appointment in appointments:
            if staff_id and appointment.staff_id != staff_id:
                continue
            
            apt_start = appointment.appointment_date
            apt_end = apt_start + timedelta(minutes=appointment.service.duration if appointment.service else 60)
            
            if not (slot_start >= apt_end or slot_end <= apt_start):
                return SlotStatus.BOOKED
        
        return SlotStatus.AVAILABLE
    
    def _get_status_reason(self, status: SlotStatus, slot_time: datetime, 
                          staff_schedule: Optional[StaffScheduleInfo]) -> Optional[str]:
        """Get human-readable reason for slot status"""
        if status == SlotStatus.AVAILABLE:
            return None
        elif status == SlotStatus.OFF_SHIFT:
            return "Outside working hours"
        elif status == SlotStatus.BREAK:
            if staff_schedule and staff_schedule.break_start and staff_schedule.break_end:
                return f"Break time ({staff_schedule.break_start.strftime('%H:%M')} - {staff_schedule.break_end.strftime('%H:%M')})"
            return "Break time"
        elif status == SlotStatus.BOOKED:
            return "Already booked"
        else:
            return "Unavailable"
    
    def get_staff_availability_summary(self, staff_id: int, start_date: date, 
                                     end_date: date) -> Dict[str, Any]:
        """Get comprehensive availability summary for a date range"""
        summary = {
            'staff_id': staff_id,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'daily_schedules': [],
            'total_working_days': 0,
            'total_working_hours': 0,
            'total_break_minutes': 0
        }
        
        current_date = start_date
        while current_date <= end_date:
            schedule_info = self.get_staff_schedule_for_date(staff_id, current_date)
            
            daily_summary = {
                'date': current_date.isoformat(),
                'is_working': schedule_info.is_working if schedule_info else False,
                'schedule_name': schedule_info.schedule_name if schedule_info else "No Schedule",
                'working_hours': 0,
                'break_minutes': 0
            }
            
            if schedule_info and schedule_info.is_working:
                summary['total_working_days'] += 1
                
                if schedule_info.shift_start and schedule_info.shift_end:
                    shift_duration = (datetime.combine(current_date, schedule_info.shift_end) - 
                                    datetime.combine(current_date, schedule_info.shift_start))
                    working_hours = shift_duration.total_seconds() / 3600
                    
                    daily_summary['working_hours'] = working_hours
                    daily_summary['break_minutes'] = schedule_info.break_minutes
                    daily_summary['shift_start'] = schedule_info.shift_start.strftime('%H:%M')
                    daily_summary['shift_end'] = schedule_info.shift_end.strftime('%H:%M')
                    
                    summary['total_working_hours'] += working_hours
                    summary['total_break_minutes'] += schedule_info.break_minutes
            
            summary['daily_schedules'].append(daily_summary)
            current_date += timedelta(days=1)
        
        return summary
    
    def validate_booking_request(self, staff_id: int, appointment_datetime: datetime, 
                               service_duration: int) -> Dict[str, Any]:
        """
        Validate if a booking request is valid based on staff schedule.
        Returns validation result with detailed information.
        """
        appointment_date = appointment_datetime.date()
        appointment_end = appointment_datetime + timedelta(minutes=service_duration)
        
        # Get staff schedule
        schedule_info = self.get_staff_schedule_for_date(staff_id, appointment_date)
        
        result = {
            'valid': False,
            'reason': '',
            'staff_id': staff_id,
            'requested_time': appointment_datetime.isoformat(),
            'service_duration': service_duration,
            'schedule_info': None
        }
        
        if not schedule_info:
            result['reason'] = "Staff member not found"
            return result
        
        if not schedule_info.is_working:
            result['reason'] = "Staff member is not scheduled to work on this date"
            return result
        
        # Check if appointment is within working intervals
        appointment_in_working_time = False
        for interval in schedule_info.working_intervals:
            if interval.contains(appointment_datetime, appointment_end):
                appointment_in_working_time = True
                break
        
        if not appointment_in_working_time:
            # Check if it overlaps with break time specifically
            if (schedule_info.break_start and schedule_info.break_end):
                break_start_dt = datetime.combine(appointment_date, schedule_info.break_start)
                break_end_dt = datetime.combine(appointment_date, schedule_info.break_end)
                
                if not (appointment_end <= break_start_dt or appointment_datetime >= break_end_dt):
                    result['reason'] = f"Appointment conflicts with break time ({schedule_info.break_start.strftime('%H:%M')} - {schedule_info.break_end.strftime('%H:%M')})"
                else:
                    result['reason'] = "Appointment is outside working hours"
            else:
                result['reason'] = "Appointment is outside working hours"
            return result
        
        # Check for existing appointments
        from modules.bookings.bookings_queries import get_appointments_by_date
        appointments = get_appointments_by_date(appointment_date)
        
        for appointment in appointments:
            if appointment.staff_id != staff_id:
                continue
            
            existing_start = appointment.appointment_date
            existing_end = existing_start + timedelta(minutes=appointment.service.duration if appointment.service else 60)
            
            if not (appointment_datetime >= existing_end or appointment_end <= existing_start):
                result['reason'] = f"Time slot conflicts with existing appointment at {existing_start.strftime('%H:%M')}"
                return result
        
        # All validations passed
        result['valid'] = True
        result['reason'] = "Appointment slot is available"
        result['schedule_info'] = {
            'schedule_name': schedule_info.schedule_name,
            'shift_start': schedule_info.shift_start.strftime('%H:%M') if schedule_info.shift_start else None,
            'shift_end': schedule_info.shift_end.strftime('%H:%M') if schedule_info.shift_end else None,
            'break_start': schedule_info.break_start.strftime('%H:%M') if schedule_info.break_start else None,
            'break_end': schedule_info.break_end.strftime('%H:%M') if schedule_info.break_end else None
        }
        
        return result

# Global service instance
staff_schedule_service = StaffScheduleService()