"""
Online Booking Management Views
Routes for managing bookings received from the website
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta

from app import app, db
from models import UnakiBooking, User
from .online_booking_queries import (
    get_online_bookings, get_online_booking_by_id,
    update_booking_status, accept_booking, reject_booking,
    bulk_accept_bookings, bulk_reject_bookings, get_online_booking_stats,
    get_grouped_online_bookings, accept_grouped_bookings
)


@app.route('/online-bookings/accept/<int:group_id>')
@login_required
def accept_booking_page(group_id):
    """Dedicated page for accepting a booking group"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get grouped bookings
    grouped_bookings = get_grouped_online_bookings()
    
    # Find the specific group
    target_group = None
    if group_id > 0 and group_id <= len(grouped_bookings):
        target_group = [grouped_bookings[group_id - 1]]
    
    if not target_group:
        flash('Booking not found', 'danger')
        return redirect(url_for('online_bookings'))
    
    # Get staff members for assignment
    staff_members = User.query.filter_by(is_active=True).order_by(User.first_name).all()
    
    # Convert booking objects to dictionaries for JSON serialization
    serializable_groups = []
    for group in target_group:
        serializable_bookings = []
        for booking in group['bookings']:
            serializable_bookings.append({
                'id': booking.id,
                'service_name': booking.service_name,
                'service_duration': booking.service_duration,
                'service_price': float(booking.service_price or 0),
                'start_time': booking.start_time.strftime('%H:%M'),
                'end_time': booking.end_time.strftime('%H:%M'),
                'appointment_date': booking.appointment_date.strftime('%Y-%m-%d'),
                'staff_name': booking.staff_name,
                'client_name': booking.client_name
            })
        
        serializable_group = group.copy()
        serializable_group['serializable_bookings'] = serializable_bookings
        serializable_groups.append(serializable_group)
    
    return render_template('accept_booking.html',
                         grouped_bookings=target_group,
                         serializable_groups=serializable_groups,
                         staff_members=staff_members)


@app.route('/online-bookings')
@login_required
def online_bookings():
    """Main page for managing online bookings"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get filters from query params
    status_filter = request.args.get('status', 'scheduled')  # Default to 'scheduled' (pending review)

    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    # Parse dates
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        except ValueError:
            date_from = None

    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            date_to = None

    # Get grouped bookings with filters
    grouped_bookings = get_grouped_online_bookings(
        status_filter=status_filter if status_filter != 'all' else None,
        date_from=date_from,
        date_to=date_to
    )

    # Convert grouped bookings to JSON-serializable format for JavaScript
    grouped_bookings_json = []
    for group in grouped_bookings:
        bookings_list = []
        for booking in group['bookings']:
            bookings_list.append({
                'id': booking.id,
                'service_name': booking.service_name,
                'service_duration': booking.service_duration,
                'service_price': float(booking.service_price or 0),
                'start_time': booking.start_time.isoformat() if booking.start_time else None,
                'staff_name': booking.staff_name
            })

        grouped_bookings_json.append({
            'customer_name': group['customer_name'],
            'customer_phone': group['customer_phone'],
            'bookings': bookings_list
        })

    # Get statistics
    stats = get_online_booking_stats()

    # Get staff members for assignment
    staff_members = User.query.filter_by(is_active=True).order_by(User.first_name).all()

    return render_template('online_bookings.html',
                         grouped_bookings=grouped_bookings,
                         grouped_bookings_json=grouped_bookings_json,
                         stats=stats,
                         staff_members=staff_members,
                         status_filter=status_filter,
                         date_from=date_from,
                         date_to=date_to)


@app.route('/online-bookings/<int:booking_id>/accept', methods=['POST'])
@login_required
def accept_online_booking(booking_id):
    """Accept an online booking"""
    if not current_user.can_access('bookings'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    staff_id = request.form.get('staff_id', type=int)
    notes = request.form.get('notes', '')

    booking, error = accept_booking(booking_id, staff_id, notes)

    if booking:
        flash(f'✅ Booking #{booking_id} ({booking.client_name} - {booking.service_name}) accepted successfully', 'success')
        if request.is_json:
            return jsonify({'success': True, 'booking_id': booking_id})
        return redirect(url_for('online_bookings'))
    else:
        # Get booking details for better error context
        failed_booking = get_online_booking_by_id(booking_id)
        if failed_booking:
            error_header = f"Cannot accept Booking #{booking_id} ({failed_booking.client_name} - {failed_booking.service_name}):"
        else:
            error_header = f"Cannot accept Booking #{booking_id}:"

        flash(f'❌ {error_header}\n{error}', 'danger')
        if request.is_json:
            return jsonify({'success': False, 'error': error}), 400
        return redirect(url_for('online_bookings'))


@app.route('/online-bookings/<int:booking_id>/reject', methods=['POST'])
@login_required
def reject_online_booking(booking_id):
    """Reject an online booking"""
    if not current_user.can_access('bookings'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    reason = request.form.get('reason', 'No reason provided')

    booking, error = reject_booking(booking_id, reason)

    if booking:
        flash(f'Booking #{booking_id} rejected', 'warning')
        if request.is_json:
            return jsonify({'success': True, 'booking_id': booking_id})
        return redirect(url_for('online_bookings'))
    else:
        flash(f'Error rejecting booking: {error}', 'danger')
        if request.is_json:
            return jsonify({'success': False, 'error': error}), 400
        return redirect(url_for('online_bookings'))


@app.route('/online-bookings/bulk-action', methods=['POST'])
@login_required
def bulk_action_online_bookings():
    """Perform bulk actions on online bookings"""
    if not current_user.can_access('bookings'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    action = request.form.get('action')
    booking_ids = request.form.getlist('booking_ids[]', type=int)

    if not booking_ids:
        flash('No bookings selected', 'warning')
        return redirect(url_for('online_bookings'))

    if action == 'accept':
        staff_id = request.form.get('bulk_staff_id', type=int)
        results = bulk_accept_bookings(booking_ids, staff_id)
        flash(f'Accepted {len(results["success"])} bookings', 'success')
    elif action == 'reject':
        reason = request.form.get('bulk_reason', 'Bulk rejection')
        results = bulk_reject_bookings(booking_ids, reason)
        flash(f'Rejected {len(results["success"])} bookings', 'warning')
    else:
        flash('Invalid action', 'danger')

    return redirect(url_for('online_bookings'))


@app.route('/online-bookings/<int:booking_id>/details')
@login_required
def online_booking_details(booking_id):
    """View detailed information about an online booking"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    booking = get_online_booking_by_id(booking_id)
    if not booking:
        flash('Booking not found', 'danger')
        return redirect(url_for('online_bookings'))

    # Get staff members for assignment dropdown
    staff_members = User.query.filter_by(is_active=True).order_by(User.first_name).all()

    return render_template('online_booking_detail.html',
                         booking=booking,
                         staff_members=staff_members)


@app.route('/api/validate-booking-time-change', methods=['POST'])
@login_required
def validate_booking_time_change():
    """Validate a booking time change without committing to database
    
    Returns conflict information and suggestions for alternative times
    """
    if not current_user.can_access('bookings'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    try:
        from modules.bookings.booking_services import validate_booking_for_acceptance, check_staff_conflicts
        
        data = request.get_json()
        booking_id = data.get('booking_id')
        staff_id = data.get('staff_id')
        appointment_date = data.get('appointment_date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if not all([booking_id, staff_id, appointment_date, start_time, end_time]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        booking = get_online_booking_by_id(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        # Parse date and times
        appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        
        # Create a temporary booking object with new times for validation
        original_date = booking.appointment_date
        original_start = booking.start_time
        original_end = booking.end_time
        
        # Temporarily update booking times for validation
        booking.appointment_date = appointment_date
        booking.start_time = datetime.strptime(start_time, '%H:%M').time()
        booking.end_time = datetime.strptime(end_time, '%H:%M').time()
        
        # Validate the new time
        validation_errors = validate_booking_for_acceptance(booking, int(staff_id))
        
        # Restore original times
        booking.appointment_date = original_date
        booking.start_time = original_start
        booking.end_time = original_end
        
        # Get conflict details and suggestions
        staff_conflict_result = check_staff_conflicts(
            int(staff_id),
            appointment_date,
            start_time,
            end_time,
            exclude_id=booking_id
        )
        
        if validation_errors:
            # Has conflicts
            return jsonify({
                'success': True,
                'valid': False,
                'has_conflicts': True,
                'errors': validation_errors,
                'suggestions': staff_conflict_result.get('suggestions', []),
                'message': 'The selected time has conflicts. Please choose a different time or see suggestions.'
            })
        else:
            # No conflicts - time is valid
            return jsonify({
                'success': True,
                'valid': True,
                'has_conflicts': False,
                'message': 'Selected time is available! You can now confirm the booking.'
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/online-bookings/<int:booking_id>/update-time', methods=['POST'])
@login_required
def update_booking_time(booking_id):
    """Update booking time and accept with new time"""
    if not current_user.can_access('bookings'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    try:
        data = request.get_json()
        appointment_date = data.get('appointment_date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        staff_id = data.get('staff_id')

        if not all([appointment_date, start_time, end_time, staff_id]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        booking = get_online_booking_by_id(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        # Parse date and times
        appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        start_time_obj = datetime.strptime(start_time, '%H:%M').time()
        end_time_obj = datetime.strptime(end_time, '%H:%M').time()

        # Update booking times and flush to database (but don't commit yet)
        # flush() makes changes visible within the transaction without committing
        booking.appointment_date = appointment_date
        booking.start_time = start_time_obj
        booking.end_time = end_time_obj
        db.session.flush()  # Make changes visible to accept_booking without committing
        
        # Now try to accept with the new time
        accepted_booking, error = accept_booking(booking_id, int(staff_id))
        
        if accepted_booking:
            # Only commit if accept succeeds
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'Booking accepted with new time: {appointment_date.strftime("%b %d, %Y")} at {start_time}',
                'booking': {
                    'id': booking_id,
                    'appointment_date': appointment_date.strftime('%Y-%m-%d'),
                    'start_time': start_time,
                    'end_time': end_time
                }
            })
        else:
            # Roll back time changes if accept fails
            db.session.rollback()
            return jsonify({'success': False, 'error': error}), 400

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/online-bookings/<int:booking_id>/callback', methods=['POST'])
@login_required
def log_booking_callback(booking_id):
    """Log that customer was called back"""
    if not current_user.can_access('bookings'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    booking = get_online_booking_by_id(booking_id)
    
    if not booking:
        return jsonify({'success': False, 'error': 'Booking not found'}), 404

    try:
        data = request.get_json() or {}
        callback_note = data.get('notes', 'Customer called back')

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        callback_log = f"\n[{timestamp}] CALLBACK: {callback_note} (by {current_user.full_name})"

        booking.notes = (booking.notes or '') + callback_log
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# API endpoints for AJAX operations
@app.route('/api/online-bookings/stats')
@login_required
def api_online_booking_stats():
    """Get online booking statistics"""
    stats = get_online_booking_stats()
    return jsonify(stats)


@app.route('/online-bookings/accept-group', methods=['POST'])
@login_required
def accept_grouped_booking():
    """Accept a group of bookings with individual staff assignments"""
    if not current_user.can_access('bookings'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    try:
        # Get booking IDs and their staff assignments from the form
        booking_ids = request.form.getlist('booking_ids[]')

        # Build mapping of booking_id to staff_id
        booking_staff_map = {}
        for booking_id in booking_ids:
            staff_id = request.form.get(f'staff_{booking_id}')
            booking_staff_map[booking_id] = staff_id if staff_id else None

        if not booking_staff_map:
            flash('No bookings selected', 'warning')
            return redirect(url_for('online_bookings'))

        # Accept all bookings with their individual staff assignments
        results = accept_grouped_bookings(booking_staff_map)

        success_count = len(results['success'])
        failed_count = len(results['failed'])

        if success_count > 0:
            flash(f'✅ Successfully accepted {success_count} booking(s)', 'success')

        if failed_count > 0:
            # Log detailed validation errors to console
            print("\n" + "="*80)
            print(f"❌ VALIDATION ERRORS: {failed_count} booking(s) failed to accept")
            print("="*80)
            
            # Store conflict data for modal display
            conflict_bookings = []
            conflict_messages = []
            
            for failed_booking in results['failed']:
                booking_id = failed_booking['booking_id']
                error_msg = failed_booking['error']
                
                # Log to console with full details
                print(f"\n📋 Booking #{booking_id}:")
                print(f"   Error: {error_msg}")
                print("-" * 80)
                
                # Get the booking details for context
                booking = get_online_booking_by_id(booking_id)
                if booking:
                    error_header = f"Booking #{booking_id} ({booking.client_name} - {booking.service_name}):"
                    conflict_messages.append(error_msg)
                    
                    # Store all conflict booking data
                    conflict_bookings.append({
                        'id': booking_id,
                        'client_name': booking.client_name,
                        'service_name': booking.service_name,
                        'current_date': booking.appointment_date.strftime('%Y-%m-%d'),
                        'current_start_time': booking.start_time.strftime('%H:%M'),
                        'current_end_time': booking.end_time.strftime('%H:%M'),
                        'service_duration': booking.service_duration,
                        'staff_id': request.form.get(f'staff_{booking_id}'),
                        'error': error_msg
                    })
                else:
                    error_header = f"Booking #{booking_id}:"
                    conflict_messages.append(error_msg)

                # Flash the error with clear formatting
                flash(f"{error_header}\n{error_msg}", 'danger')
            
            print("="*80 + "\n")
            
            # Always return JSON for AJAX requests (the form uses fetch)
            return jsonify({
                'success': False,
                'has_conflicts': True,
                'conflict_bookings': conflict_bookings,
                'conflict_messages': conflict_messages,
                'results': results
            }), 200  # Return 200 to prevent error handling

        # Success - return appropriate response
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'results': results})

        return redirect(url_for('online_bookings'))

    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f'Error accepting bookings: {str(e)}', 'danger')
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        return redirect(url_for('online_bookings'))