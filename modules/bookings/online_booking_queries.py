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
    validate_against_shift
)


def get_online_bookings(status_filter=None, date_from=None, date_to=None):
    """Get all online bookings with optional filters"""
    try:
        query = UnakiBooking.query.filter_by(booking_source='online')

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
    return UnakiBooking.query.filter_by(
        id=booking_id,
        booking_source='online'
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
                'category': 'Staff Schedule',
                'message': staff_conflict_result.get('reason', 'Staff scheduling conflict')
            })
        else:
            # Overlapping appointments
            conflicts = staff_conflict_result.get('conflicts', [])
            for conflict in conflicts:
                validation_errors.append({
                    'category': 'Staff Conflicts',
                    'message': f"Staff {staff.full_name} already has an appointment from {conflict['start_time']} to {conflict['end_time']} with {conflict['client_name']}"
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
    """
    Accept multiple bookings with individual staff assignments and comprehensive validation
    Validates ALL bookings before accepting ANY (atomic operation)
    booking_staff_map: dict mapping booking_id to staff_id
    """
    results = {'success': [], 'failed': []}
    
    # Step 1: Fetch all bookings and validate they exist
    bookings_to_process = []
    for booking_id, staff_id in booking_staff_map.items():
        booking = get_online_booking_by_id(int(booking_id))
        if not booking:
            results['failed'].append({'id': booking_id, 'error': 'Booking not found'})
            continue
        
        # Require staff assignment
        final_staff_id = int(staff_id) if staff_id else booking.staff_id
        if not final_staff_id:
            results['failed'].append({'id': booking_id, 'error': 'Staff assignment is required'})
            continue
        
        # Validate staff exists
        staff = User.query.get(final_staff_id)
        if not staff:
            results['failed'].append({'id': booking_id, 'error': f'Staff member with ID {final_staff_id} not found'})
            continue
        
        bookings_to_process.append({
            'booking': booking,
            'booking_id': int(booking_id),
            'staff_id': final_staff_id,
            'staff': staff
        })
    
    # Step 2: Collect ALL validation errors for each booking (comprehensive checking)
    booking_errors = {}  # Map booking_id to list of errors
    
    for item in bookings_to_process:
        booking = item['booking']
        staff_id = item['staff_id']
        staff = item['staff']
        booking_id = item['booking_id']
        
        # Initialize error list for this booking
        if booking_id not in booking_errors:
            booking_errors[booking_id] = []
        
        start_time_str = booking.start_time.strftime('%H:%M')
        end_time_str = booking.end_time.strftime('%H:%M')
        appointment_date = booking.appointment_date
        
        # VALIDATION 1: Check staff conflicts (collect ALL conflicts, not just first)
        staff_conflict_result = check_staff_conflicts(
            staff_id, 
            appointment_date, 
            start_time_str, 
            end_time_str,
            exclude_id=booking_id
        )
        
        if staff_conflict_result.get('has_conflicts'):
            if staff_conflict_result.get('shift_violation'):
                # Shift violations (not scheduled, outside hours, during break)
                booking_errors[booking_id].append({
                    'category': 'Staff Schedule',
                    'message': staff_conflict_result.get('reason', 'Staff scheduling conflict')
                })
            else:
                # Overlapping appointments (show ALL conflicts, not just first)
                conflicts = staff_conflict_result.get('conflicts', [])
                for conflict in conflicts:
                    booking_errors[booking_id].append({
                        'category': 'Staff Conflicts',
                        'message': f"{staff.full_name} already has an appointment from {conflict['start_time']} to {conflict['end_time']} with {conflict['client_name']}"
                    })
    
    # Step 3: Check for INTERNAL conflicts (between bookings in this group)
    # For each pair of bookings, check if same staff has time overlap
    internal_conflicts_found = set()  # Track which bookings have internal conflicts
    
    for i, item1 in enumerate(bookings_to_process):
        for item2 in bookings_to_process[i+1:]:
            # Check if same staff and same date
            if item1['staff_id'] == item2['staff_id'] and \
               item1['booking'].appointment_date == item2['booking'].appointment_date:
                
                # Check time overlap
                start1 = datetime.combine(item1['booking'].appointment_date, item1['booking'].start_time)
                end1 = datetime.combine(item1['booking'].appointment_date, item1['booking'].end_time)
                start2 = datetime.combine(item2['booking'].appointment_date, item2['booking'].start_time)
                end2 = datetime.combine(item2['booking'].appointment_date, item2['booking'].end_time)
                
                if start1 < end2 and start2 < end1:
                    # Only add error once per pair
                    pair_key = f"{min(item1['booking_id'], item2['booking_id'])}-{max(item1['booking_id'], item2['booking_id'])}"
                    if pair_key not in internal_conflicts_found:
                        internal_conflicts_found.add(pair_key)
                        
                        # Add internal conflict error to BOTH bookings
                        conflict_msg = f"Overlaps with booking #{item2['booking_id']} for {item1['staff'].full_name} ({item1['booking'].start_time.strftime('%I:%M %p')} - {item1['booking'].end_time.strftime('%I:%M %p')})"
                        booking_errors[item1['booking_id']].append({
                            'category': 'Internal Conflicts',
                            'message': conflict_msg
                        })
                        
                        conflict_msg2 = f"Overlaps with booking #{item1['booking_id']} for {item2['staff'].full_name} ({item2['booking'].start_time.strftime('%I:%M %p')} - {item2['booking'].end_time.strftime('%I:%M %p')})"
                        booking_errors[item2['booking_id']].append({
                            'category': 'Internal Conflicts',
                            'message': conflict_msg2
                        })
    
    # Step 4: Format errors and build failed results
    for booking_id, errors in booking_errors.items():
        if errors:  # Only add to failed if there are errors
            error_message = f"Booking #{booking_id}:\n" + _format_validation_errors(errors)
            results['failed'].append({'id': booking_id, 'error': error_message})
    
    # Step 5: If there are any validation errors, don't accept ANY bookings
    if results['failed']:
        print(f"⚠️ Grouped booking validation failed: {len(results['failed'])} booking(s) have errors")
        return results
    
    # Step 6: All validations passed - accept all bookings
    for item in bookings_to_process:
        # Skip if somehow marked as failed
        if item['booking_id'] in [f['id'] for f in results['failed']]:
            continue
        
        booking = item['booking']
        staff = item['staff']
        staff_id = item['staff_id']
        booking_id = item['booking_id']
        
        try:
            booking.status = 'confirmed'
            booking.confirmed_at = datetime.now()
            booking.staff_id = staff_id
            booking.staff_name = f"{staff.first_name} {staff.last_name}"
            
            validation_note = f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Booking accepted (grouped) with validations passed"
            booking.notes = (booking.notes or '') + validation_note
            
            results['success'].append(booking_id)
        except Exception as e:
            db.session.rollback()
            results['failed'].append({'id': booking_id, 'error': str(e)})
    
    # Commit all changes if at least one succeeded
    if results['success']:
        try:
            db.session.commit()
            print(f"✅ Successfully accepted {len(results['success'])} grouped bookings")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error committing grouped bookings: {e}")
            # Move all success to failed
            for booking_id in results['success']:
                results['failed'].append({'id': booking_id, 'error': 'Database commit failed'})
            results['success'] = []
    
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

    total = UnakiBooking.query.filter_by(booking_source='online').count()
    pending = UnakiBooking.query.filter_by(booking_source='online', status='scheduled').count()
    accepted = UnakiBooking.query.filter_by(booking_source='online', status='confirmed').count()
    rejected = UnakiBooking.query.filter_by(booking_source='online', status='cancelled').count()

    return {
        'total': total,
        'pending': pending,
        'accepted': accepted,
        'rejected': rejected
    }