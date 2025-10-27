"""
Booking Business Logic and Services

This module contains business logic for the booking system, including:
- Shift validation against staff schedules
- Appointment creation and conflict detection
- Validation functions for bookings
"""

from datetime import datetime, date, time, timedelta
from flask import request, jsonify
from app import db
from models import (
    Appointment, Customer, Service, User, ShiftManagement, ShiftLogs, UnakiBooking
)


def validate_against_shift(staff_id, date_obj, start_time_str, end_time_str):
    """
    Validate booking against shift rules (hours, breaks, out-of-office).
    
    Args:
        staff_id (int): ID of the staff member
        date_obj (date): Date of the appointment
        start_time_str (str): Start time in 'HH:MM' format
        end_time_str (str): End time in 'HH:MM' format
    
    Returns:
        tuple: (is_valid, error_message) - is_valid is bool, error_message is str or None
    """
    try:
        # Helper to check time overlap
        def time_overlaps(a_start, a_end, b_start, b_end):
            def to_minutes(t):
                h, m = map(int, t.split(':'))
                return h * 60 + m
            a_s, a_e = to_minutes(a_start), to_minutes(a_end)
            b_s, b_e = to_minutes(b_start), to_minutes(b_end)
            return a_e > b_s and a_s < b_e

        # Get shift management for this staff
        shift_mgmt = ShiftManagement.query.filter(
            ShiftManagement.staff_id == staff_id,
            ShiftManagement.from_date <= date_obj,
            ShiftManagement.to_date >= date_obj
        ).first()

        if not shift_mgmt:
            return False, "Staff is not scheduled for this date."

        # Get shift log for this specific date
        shift_log = ShiftLogs.query.filter(
            ShiftLogs.shift_management_id == shift_mgmt.id,
            ShiftLogs.individual_date == date_obj
        ).first()

        if not shift_log:
            return False, "No shift log found for this date."

        # Check if staff is working
        if shift_log.status in ['absent', 'holiday']:
            return False, f"Staff is {shift_log.status} on this date."

        # Check if within shift hours
        if not (shift_log.shift_start_time and shift_log.shift_end_time):
            return False, "No shift hours set for this staff."

        shift_start = shift_log.shift_start_time.strftime('%H:%M')
        shift_end = shift_log.shift_end_time.strftime('%H:%M')

        if not (start_time_str >= shift_start and end_time_str <= shift_end):
            return False, f"Outside of shift hours ({shift_start} - {shift_end})."

        # Check break time
        if shift_log.break_start_time and shift_log.break_end_time:
            break_start = shift_log.break_start_time.strftime('%H:%M')
            break_end = shift_log.break_end_time.strftime('%H:%M')
            if time_overlaps(start_time_str, end_time_str, break_start, break_end):
                return False, f"Overlaps with break time ({break_start} - {break_end})."

        # Check out-of-office time
        if shift_log.out_of_office_start and shift_log.out_of_office_end:
            ooo_start = shift_log.out_of_office_start.strftime('%H:%M')
            ooo_end = shift_log.out_of_office_end.strftime('%H:%M')
            ooo_reason = shift_log.out_of_office_reason or "Out of office"
            if time_overlaps(start_time_str, end_time_str, ooo_start, ooo_end):
                return False, f"Staff is out of office: {ooo_reason} ({ooo_start} - {ooo_end})."

        return True, None

    except Exception as e:
        print(f"Error in shift validation: {e}")
        return True, None  # Don't block bookings if validation fails


def unaki_create_appointment_impl():
    """API endpoint implementation to create appointments for Unaki booking system
    
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        data = request.get_json()

        # Extract appointment data
        staff_id = data.get('staffId')
        client_name = data.get('clientName')
        client_phone = data.get('clientPhone', '')
        service_type = data.get('serviceType')
        start_time = data.get('startTime')
        end_time = data.get('endTime')
        notes = data.get('notes', '')
        appointment_date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))

        # Validate required fields
        if not all([staff_id, client_name, service_type, start_time, end_time]):
            return {
                'success': False,
                'error': 'Missing required fields: staff, client name, service, start time, and end time are required'
            }, 400

        # Parse date and times
        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
        start_datetime = datetime.combine(appointment_date, datetime.strptime(start_time, '%H:%M').time())
        end_datetime = datetime.combine(appointment_date, datetime.strptime(end_time, '%H:%M').time())

        # Find or create customer
        customer = Customer.query.filter_by(full_name=client_name).first()
        if not customer:
            customer = Customer(
                full_name=client_name,
                phone=client_phone,
                email=f"{client_name.lower().replace(' ', '.')}@customer.spa"  # Temporary email
            )
            db.session.add(customer)
            db.session.flush()  # Get the ID

        # Find service by name or create a generic one
        service = Service.query.filter_by(name=service_type).first()
        if not service:
            service = Service(
                name=service_type,
                duration=60,  # Default 60 minutes
                price=100.0,  # Default price
                is_active=True
            )
            db.session.add(service)
            db.session.flush()

        # Verify staff exists
        staff = User.query.get(staff_id)
        if not staff:
            return {
                'success': False,
                'error': 'Staff member not found'
            }, 400

        # Create the appointment
        appointment = Appointment(
            client_id=customer.id,
            service_id=service.id,
            staff_id=staff_id,
            appointment_date=start_datetime,
            end_time=end_datetime,
            status='confirmed',
            notes=notes,
            amount=service.price
        )

        db.session.add(appointment)
        db.session.commit()

        return {
            'success': True,
            'message': 'Appointment created successfully',
            'appointment': {
                'id': appointment.id,
                'staff_id': staff_id,
                'client_name': client_name,
                'client_phone': client_phone,
                'service_type': service_type,
                'start_time': start_time,
                'end_time': end_time,
                'date': appointment_date_str,
                'status': 'confirmed',
                'notes': notes,
                'created_at': appointment.created_at.isoformat()
            }
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f"Error in unaki_create_appointment: {e}")
        return {'success': False, 'error': f'Failed to create appointment: {str(e)}'}, 500


def check_staff_conflicts(staff_id, appointment_date, start_time_str, end_time_str, exclude_id=None):
    """Check for staff scheduling conflicts
    
    Args:
        staff_id (int): ID of the staff member
        appointment_date (date): Date of the appointment
        start_time_str (str): Start time in 'HH:MM' format
        end_time_str (str): End time in 'HH:MM' format
        exclude_id (int, optional): Appointment ID to exclude (for edit operations)
    
    Returns:
        dict: Conflict information with has_conflicts, conflicts list, and suggestions
    """
    try:
        # First check shift validation
        is_valid_shift, shift_error = validate_against_shift(
            staff_id, appointment_date, start_time_str, end_time_str
        )
        
        if not is_valid_shift:
            return {
                'has_conflicts': True,
                'conflicts': [],
                'shift_violation': True,
                'reason': shift_error,
                'suggestions': [],
                'staff_id': staff_id,
                'requested_time': f"{start_time_str} - {end_time_str}"
            }

        # Get existing appointments for this staff on this date
        query = UnakiBooking.query.filter(
            UnakiBooking.staff_id == staff_id,
            UnakiBooking.appointment_date == appointment_date,
            UnakiBooking.status.in_(['scheduled', 'confirmed'])
        )

        # Exclude current appointment if editing
        if exclude_id:
            query = query.filter(UnakiBooking.id != exclude_id)

        existing_bookings = query.all()

        conflicts = []
        suggestions = []

        # Convert times to minutes for easier comparison
        def time_to_minutes(time_str):
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes

        start_minutes = time_to_minutes(start_time_str)
        end_minutes = time_to_minutes(end_time_str)

        # Check for conflicts
        for booking in existing_bookings:
            booking_start = time_to_minutes(booking.start_time.strftime('%H:%M'))
            booking_end = time_to_minutes(booking.end_time.strftime('%H:%M'))

            # Check overlap
            if start_minutes < booking_end and end_minutes > booking_start:
                conflicts.append({
                    'id': booking.id,
                    'client_name': booking.client_name,
                    'service_name': booking.service_name,
                    'start_time': booking.start_time.strftime('%H:%M'),
                    'end_time': booking.end_time.strftime('%H:%M'),
                    'status': booking.status
                })

        # Generate suggestions if conflicts exist
        if conflicts:
            service_duration = end_minutes - start_minutes

            # Find available slots
            for hour in range(9, 18):  # Business hours
                for minute in [0, 15, 30, 45]:  # 15-minute intervals
                    slot_start_minutes = hour * 60 + minute
                    slot_end_minutes = slot_start_minutes + service_duration

                    if slot_end_minutes >= 18 * 60:  # Don't go past business hours
                        continue

                    # Check if this slot conflicts with any existing booking
                    slot_has_conflict = False
                    for booking in existing_bookings:
                        booking_start = time_to_minutes(booking.start_time.strftime('%H:%M'))
                        booking_end = time_to_minutes(booking.end_time.strftime('%H:%M'))

                        if slot_start_minutes < booking_end and slot_end_minutes > booking_start:
                            slot_has_conflict = True
                            break

                    if not slot_has_conflict:
                        start_time_suggestion = f"{hour:02d}:{minute:02d}"
                        end_hour = slot_end_minutes // 60
                        end_minute = slot_end_minutes % 60
                        end_time_suggestion = f"{end_hour:02d}:{end_minute:02d}"

                        suggestions.append({
                            'start_time': start_time_suggestion,
                            'end_time': end_time_suggestion,
                            'display': f"{start_time_suggestion} - {end_time_suggestion}"
                        })

                        if len(suggestions) >= 5:  # Limit to 5 suggestions
                            break
                if len(suggestions) >= 5:
                    break

        return {
            'has_conflicts': len(conflicts) > 0,
            'conflicts': conflicts,
            'suggestions': suggestions,
            'staff_id': staff_id,
            'requested_time': f"{start_time_str} - {end_time_str}"
        }

    except Exception as e:
        print(f"Error checking staff conflicts: {e}")
        return {'error': str(e)}


def check_client_conflicts(client_id, client_name, client_phone, appointment_date, start_time_str, end_time_str, exclude_booking_id=None):
    """Check for client scheduling conflicts
    
    Args:
        client_id (int): ID of the client (can be None if client not linked yet)
        client_name (str): Name of the client
        client_phone (str): Phone number of the client
        appointment_date (date): Date of the appointment
        start_time_str (str): Start time in 'HH:MM' format
        end_time_str (str): End time in 'HH:MM' format
        exclude_booking_id (int, optional): Booking ID to exclude from conflict check
    
    Returns:
        dict: Conflict information with has_conflict, message, and conflict details
    """
    try:
        # Parse times
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()

        # Validate end time is after start time
        start_datetime = datetime.combine(appointment_date, start_time)
        end_datetime = datetime.combine(appointment_date, end_time)

        if end_datetime <= start_datetime:
            return {
                'has_conflict': True,
                'message': 'End time must be after start time'
            }

        # Build query to find conflicting bookings
        # Search by client_id OR phone number (to catch bookings before client was linked)
        query = UnakiBooking.query.filter(
            db.or_(
                UnakiBooking.client_id == client_id if client_id else False,
                UnakiBooking.client_phone == client_phone if client_phone else False
            )
        ).filter(
            ~UnakiBooking.status.in_(['cancelled', 'no_show'])
        )
        
        # Exclude current booking if provided
        if exclude_booking_id:
            query = query.filter(UnakiBooking.id != exclude_booking_id)
        
        # Get all potential conflicting bookings
        conflicting_bookings = query.all()

        # Check for conflicts
        conflicts = []
        for booking in conflicting_bookings:
            # Skip if this is a completed appointment that's already paid
            if booking.status == 'completed' and booking.payment_status == 'paid':
                continue

            is_same_date = booking.appointment_date == appointment_date

            # Only check same-date appointments for time overlap
            if is_same_date:
                # Same-date appointments: check time overlap
                existing_start = datetime.combine(appointment_date, booking.start_time)
                existing_end = datetime.combine(appointment_date, booking.end_time)

                if start_datetime < existing_end and end_datetime > existing_start:
                    conflicts.append({
                        'id': booking.id,
                        'appointment_date': booking.appointment_date.strftime('%Y-%m-%d'),
                        'start_time': booking.start_time.strftime('%I:%M %p'),
                        'end_time': booking.end_time.strftime('%I:%M %p'),
                        'staff_name': booking.staff_name or 'Unknown',
                        'service_name': booking.service_name,
                        'payment_status': booking.payment_status,
                        'status': booking.status
                    })

        if conflicts:
            conflict = conflicts[0]
            message = f"{client_name} already has an appointment from {conflict['start_time']} to {conflict['end_time']} with {conflict['staff_name']} on {conflict['appointment_date']}"

            return {
                'has_conflict': True,
                'message': message,
                'conflicts': conflicts
            }

        return {
            'has_conflict': False,
            'message': 'No conflicts found'
        }

    except Exception as e:
        print(f"Error checking client conflicts: {e}")
        import traceback
        traceback.print_exc()
        return {
            'has_conflict': False,
            'error': str(e)
        }


def validate_booking_for_acceptance(booking, staff_id):
    """
    Comprehensive validation for accepting a booking
    Checks all possible conflicts: staff schedule, staff availability, client conflicts
    
    Args:
        booking: UnakiBooking object to validate
        staff_id (int): Staff member ID to assign
    
    Returns:
        list: List of validation error dicts with 'category' and 'message', empty if valid
    """
    validation_errors = []
    
    try:
        # Get staff details
        staff = User.query.get(staff_id)
        if not staff:
            validation_errors.append({
                'category': 'Staff Assignment',
                'message': 'Selected staff member not found in system'
            })
            return validation_errors
        
        # Prepare time strings
        start_time_str = booking.start_time.strftime('%H:%M')
        end_time_str = booking.end_time.strftime('%H:%M')
        appointment_date = booking.appointment_date
        
        # VALIDATION 1: Check staff scheduling conflicts
        staff_conflict_result = check_staff_conflicts(
            staff_id,
            appointment_date,
            start_time_str,
            end_time_str,
            exclude_id=booking.id
        )
        
        if staff_conflict_result.get('has_conflicts'):
            if staff_conflict_result.get('shift_violation'):
                # Staff schedule issues (outside hours, during break, out of office, etc.)
                validation_errors.append({
                    'category': 'Staff Availability',
                    'message': staff_conflict_result.get('reason', 'Staff is not available at this time')
                })
            else:
                # Overlapping appointments with other clients
                conflicts = staff_conflict_result.get('conflicts', [])
                for conflict in conflicts:
                    validation_errors.append({
                        'category': 'Staff Schedule Conflict',
                        'message': f"{staff.first_name} {staff.last_name} already has an appointment from {conflict['start_time']} to {conflict['end_time']} with {conflict['client_name']}"
                    })
        
        # VALIDATION 2: Check client conflicts (unpaid bookings, same-day time overlaps)
        client_conflict_result = check_client_conflicts(
            client_id=booking.client_id,
            client_name=booking.client_name,
            client_phone=booking.client_phone,
            appointment_date=appointment_date,
            start_time_str=start_time_str,
            end_time_str=end_time_str,
            exclude_booking_id=booking.id
        )
        
        if client_conflict_result.get('has_conflict'):
            conflicts = client_conflict_result.get('conflicts', [])
            
            # Add time overlap conflicts
            for conflict in conflicts:
                validation_errors.append({
                    'category': 'Client Schedule Conflict',
                    'message': f"{booking.client_name} already has an appointment from {conflict['start_time']} to {conflict['end_time']} with {conflict['staff_name']} on {conflict['appointment_date']}"
                })
        
        return validation_errors
        
    except Exception as e:
        print(f"Error in validate_booking_for_acceptance: {e}")
        import traceback
        traceback.print_exc()
        validation_errors.append({
            'category': 'System Error',
            'message': f'Validation error: {str(e)}'
        })
        return validation_errors
