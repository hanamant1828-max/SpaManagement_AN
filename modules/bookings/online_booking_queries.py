"""
Online Booking Management Queries
Handles database operations for managing online bookings
"""
from datetime import datetime, date
from sqlalchemy import func, and_, or_
from app import db
from models import UnakiBooking, Customer, Service, User
from modules.bookings.booking_services import (
    check_staff_conflicts, 
    check_client_conflicts,
    validate_against_shift,
    validate_booking_for_acceptance
)


def get_online_bookings(status_filter=None, date_from=None, date_to=None):
    """Get all online bookings with optional filters"""
    try:
        # Include both 'online' and 'website' sources
        query = UnakiBooking.query.filter(
            UnakiBooking.booking_source.in_(['online', 'website'])
        )

        if status_filter:
            query = query.filter_by(status=status_filter)

        if date_from:
            query = query.filter(UnakiBooking.appointment_date >= date_from)

        if date_to:
            query = query.filter(UnakiBooking.appointment_date <= date_to)

        return query.order_by(UnakiBooking.created_at.desc()).all()
    except Exception as e:
        print(f"❌ Error getting online bookings: {e}")
        import traceback
        traceback.print_exc()
        # Return empty list on error to prevent crashes
        return []


def get_grouped_online_bookings(status_filter=None, date_from=None, date_to=None):
    """Get online bookings grouped by customer and appointment date"""
    try:
        bookings = get_online_bookings(status_filter, date_from, date_to)

        # Group bookings by customer identifier (name + phone + date)
        grouped = {}
        for booking in bookings:
            # Create a unique key for customer + date (includes name to prevent incorrect grouping)
            key = f"{booking.client_name}_{booking.client_phone}_{booking.appointment_date}"

            if key not in grouped:
                grouped[key] = {
                    'customer_name': booking.client_name,
                    'customer_phone': booking.client_phone,
                    'customer_email': booking.client_email,
                    'appointment_date': booking.appointment_date,
                    'client': booking.client,
                    'total_amount': 0,
                    'created_at': booking.created_at,
                    'status': booking.status,
                    'bookings': []
                }

            grouped[key]['bookings'].append(booking)
            grouped[key]['total_amount'] += (booking.service_price or 0)

        # Convert to list and sort by created_at
        result = list(grouped.values())
        result.sort(key=lambda x: x['created_at'], reverse=True)

        return result
    except Exception as e:
        print(f"❌ Error getting grouped online bookings: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_online_booking_by_id(booking_id):
    """Get a specific online booking"""
    return UnakiBooking.query.filter(
        UnakiBooking.id == booking_id,
        UnakiBooking.booking_source.in_(['online', 'website'])
    ).first()


def update_booking_status(booking_id, new_status, notes=None):
    """Update booking status (scheduled, confirmed, in_progress, completed, cancelled, no_show)"""
    booking = get_online_booking_by_id(booking_id)
    if not booking:
        return None, "Booking not found"

    booking.status = new_status
    if notes:
        booking.notes = (booking.notes or '') + f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Status changed to {new_status}: {notes}"

    db.session.commit()
    return booking, None


def accept_booking(booking_id, staff_id=None, notes=None):
    """Accept an online booking and optionally assign staff with comprehensive validation"""
    booking = get_online_booking_by_id(booking_id)
    if not booking:
        return None, "Booking not found"

    # Require staff assignment for validation
    if not staff_id:
        # If booking already has a staff assigned, use that
        if booking.staff_id:
            staff_id = booking.staff_id
        else:
            return None, "Staff assignment is required to accept this booking"

    # Validate staff exists
    staff = User.query.get(staff_id)
    if not staff:
        return None, f"Staff member with ID {staff_id} not found"

    # Prepare time strings for validation
    start_time_str = booking.start_time.strftime('%H:%M')
    end_time_str = booking.end_time.strftime('%H:%M')
    appointment_date = booking.appointment_date

    # COLLECT ALL VALIDATION ERRORS (don't stop at first error)
    validation_errors = []

    # VALIDATION 1: Check staff conflicts (shift hours, breaks, overlapping appointments)
    staff_conflict_result = check_staff_conflicts(
        staff_id, 
        appointment_date, 
        start_time_str, 
        end_time_str,
        exclude_id=booking_id  # Exclude this booking if it's already in the system
    )

    if staff_conflict_result.get('has_conflicts'):
        if staff_conflict_result.get('shift_violation'):
            # Shift violations (outside hours, during break, etc.)
            validation_errors.append({
                'category': 'Staff Availability',
                'message': staff_conflict_result.get('reason', 'Staff scheduling conflict')
            })
        else:
            # Overlapping appointments
            conflicts = staff_conflict_result.get('conflicts', [])
            for conflict in conflicts:
                validation_errors.append({
                    'category': 'Staff Schedule Conflict',
                    'message': f"{staff.full_name} already has an appointment from {conflict['start_time']} to {conflict['end_time']} with {conflict['client_name']}"
                })

    # VALIDATION 2: Check client conflicts (no double-booking the same client)
    client_conflict_result = check_client_conflicts(
        booking.client_id,
        booking.client_phone,
        booking.client_name,
        appointment_date,
        start_time_str,
        end_time_str,
        exclude_id=booking_id
    )

    if client_conflict_result.get('has_conflicts'):
        conflicts = client_conflict_result.get('conflicts', [])
        for conflict in conflicts:
            validation_errors.append({
                'category': 'Client Schedule Conflict',
                'message': f"{booking.client_name} already has an appointment from {conflict['start_time']} to {conflict['end_time']} with {conflict['staff_name']} on {conflict['date']}"
            })

    # If there are any validation errors, return them all
    if validation_errors:
        error_message = _format_validation_errors(validation_errors)
        return None, error_message

    # All validations passed - accept the booking
    booking.status = 'confirmed'
    booking.confirmed_at = datetime.now()

    # Update staff assignment
    booking.staff_id = staff_id
    booking.staff_name = f"{staff.first_name} {staff.last_name}"

    # Add notes
    validation_note = f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Booking accepted - all validations passed"
    if notes:
        booking.notes = (booking.notes or '') + f"{validation_note}: {notes}"
    else:
        booking.notes = (booking.notes or '') + validation_note

    db.session.commit()
    return booking, None


def _format_validation_errors(errors):
    """Format validation errors in a clear, organized way"""
    if not errors:
        return ""

    # Group errors by category
    errors_by_category = {}
    for error in errors:
        category = error.get('category', 'General')
        if category not in errors_by_category:
            errors_by_category[category] = []
        errors_by_category[category].append(error['message'])

    # Format the error message
    formatted_parts = []
    for category, messages in errors_by_category.items():
        if len(messages) == 1:
            formatted_parts.append(f"❌ {category}: {messages[0]}")
        else:
            formatted_parts.append(f"❌ {category}:")
            for msg in messages:
                formatted_parts.append(f"  • {msg}")

    return "\n".join(formatted_parts)


def reject_booking(booking_id, reason):
    """Reject an online booking"""
    booking = get_online_booking_by_id(booking_id)
    if not booking:
        return None, "Booking not found"

    booking.status = 'cancelled'
    booking.notes = (booking.notes or '') + f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Booking rejected: {reason}"

    db.session.commit()
    return booking, None


def bulk_accept_bookings(booking_ids, staff_id=None):
    """Accept multiple bookings at once"""
    results = {'success': [], 'failed': []}

    for booking_id in booking_ids:
        booking, error = accept_booking(booking_id, staff_id)
        if booking:
            results['success'].append(booking_id)
        else:
            results['failed'].append({'id': booking_id, 'error': error})

    return results


def accept_grouped_bookings(booking_staff_map):
    """Accept multiple bookings with individual staff assignments and comprehensive validation
    Validates ALL bookings before accepting ANY (atomic operation)
    booking_staff_map: dict mapping booking_id to staff_id
    """
    results = {'success': [], 'failed': []}

    try:
        for booking_id_str, staff_id_str in booking_staff_map.items():
            booking_id = int(booking_id_str)
            staff_id = int(staff_id_str) if staff_id_str else None

            booking = get_online_booking_by_id(booking_id)
            if not booking:
                results['failed'].append({
                    'booking_id': booking_id,
                    'error': f'Booking #{booking_id}: Booking not found'
                })
                continue

            if not staff_id:
                results['failed'].append({
                    'booking_id': booking_id,
                    'error': f'Booking #{booking_id}: No staff member assigned. Please select a staff member for each service.'
                })
                continue

            # Get staff details
            staff = User.query.get(staff_id)
            if not staff:
                results['failed'].append({
                    'booking_id': booking_id,
                    'error': f'Booking #{booking_id}: Selected staff member not found in system'
                })
                continue

            # Validate booking before accepting
            validation_errors = validate_booking_for_acceptance(booking, staff_id)
            if validation_errors:
                error_message = f"Booking #{booking_id}: " + _format_validation_errors(validation_errors)
                
                # Log validation errors to console
                print(f"\n⚠️ VALIDATION FAILED for Booking #{booking_id}")
                print(f"   Client: {booking.client_name}")
                print(f"   Service: {booking.service_name}")
                print(f"   Date: {booking.appointment_date}")
                print(f"   Time: {booking.start_time.strftime('%H:%M')} - {booking.end_time.strftime('%H:%M')}")
                print(f"   Assigned Staff: {staff.first_name} {staff.last_name} (ID: {staff_id})")
                print(f"   Errors:")
                for err in validation_errors:
                    print(f"      • {err['category']}: {err['message']}")
                print("")
                
                results['failed'].append({
                    'booking_id': booking_id,
                    'error': error_message
                })
                continue

            # Accept the booking
            booking.status = 'confirmed'
            booking.staff_id = staff_id
            booking.staff_name = f"{staff.first_name} {staff.last_name}"

            # Add acceptance note
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            booking.notes = (booking.notes or '') + f"\n[{timestamp}] Booking accepted and assigned to {staff.first_name} {staff.last_name}"

            results['success'].append({
                'booking_id': booking_id,
                'staff_name': f"{staff.first_name} {staff.last_name}"
            })

        # Only commit if at least one booking was successful
        if results['success']:
            db.session.commit()
            print(f"✅ Successfully accepted {len(results['success'])} grouped bookings")
        else:
            db.session.rollback()
            print(f"⚠️ No bookings were accepted due to validation errors")

        return results

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error accepting grouped bookings: {e}")
        import traceback
        traceback.print_exc()
        # Add all remaining bookings as failed
        for booking_id in booking_staff_map.keys():
            if not any(r['booking_id'] == int(booking_id) for r in results['success'] + results['failed']):
                results['failed'].append({
                    'booking_id': int(booking_id),
                    'error': f'System error: {str(e)}'
                })
        return results


def bulk_reject_bookings(booking_ids, reason):
    """Reject multiple bookings at once"""
    results = {'success': [], 'failed': []}

    for booking_id in booking_ids:
        booking, error = reject_booking(booking_id, reason)
        if booking:
            results['success'].append(booking_id)
        else:
            results['failed'].append({'id': booking_id, 'error': error})

    return results


def get_online_booking_stats():
    """Get statistics for online bookings"""
    from models import UnakiBooking
    
    # Get all online bookings and group them to count customer groups
    # Include both 'online' and 'website' sources since the website uses 'website' as booking_source
    all_bookings = UnakiBooking.query.filter(
        UnakiBooking.booking_source.in_(['online', 'website'])
    ).all()
    
    # Group by customer + date
    unique_groups = set()
    pending_groups = set()
    accepted_groups = set()
    rejected_groups = set()
    
    for booking in all_bookings:
        group_key = f"{booking.client_name}_{booking.client_phone}_{booking.appointment_date}"
        unique_groups.add(group_key)
        
        if booking.status == 'scheduled':
            pending_groups.add(group_key)
        elif booking.status == 'confirmed':
            accepted_groups.add(group_key)
        elif booking.status == 'cancelled':
            rejected_groups.add(group_key)
    
    return {
        'total': len(unique_groups),
        'pending': len(pending_groups),
        'accepted': len(accepted_groups),
        'rejected': len(rejected_groups)
    }