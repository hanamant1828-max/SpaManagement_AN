"""
Online Booking Management Queries
Handles database operations for managing online bookings
"""
from datetime import datetime, date
from sqlalchemy import func, and_, or_
from app import db
from models import UnakiBooking, Customer, Service, User


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
    """Accept an online booking and optionally assign staff"""
    booking = get_online_booking_by_id(booking_id)
    if not booking:
        return None, "Booking not found"

    # Change status from 'scheduled' (pending) to 'confirmed' (accepted)
    booking.status = 'confirmed'
    booking.confirmed_at = datetime.now()
    
    if staff_id:
        staff = User.query.get(staff_id)
        if staff:
            booking.staff_id = staff_id
            booking.staff_name = f"{staff.first_name} {staff.last_name}"

    if notes:
        booking.notes = (booking.notes or '') + f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Booking accepted: {notes}"

    db.session.commit()
    return booking, None


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
    Accept multiple bookings with individual staff assignments
    booking_staff_map: dict mapping booking_id to staff_id
    """
    results = {'success': [], 'failed': []}
    
    for booking_id, staff_id in booking_staff_map.items():
        booking, error = accept_booking(int(booking_id), int(staff_id) if staff_id else None)
        if booking:
            results['success'].append(booking_id)
        else:
            results['failed'].append({'id': booking_id, 'error': error})
    
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