
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
    bulk_accept_bookings, bulk_reject_bookings, get_online_booking_stats
)


@app.route('/online-bookings')
@login_required
def online_bookings():
    """Main page for managing online bookings"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get filters from query params
    status_filter = request.args.get('status', 'scheduled')  # Default to 'scheduled' (pending review)
    
    # Validate status filter - only allow valid enum values
    valid_statuses = ['scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show', 'all']
    if status_filter not in valid_statuses:
        flash(f'Invalid status filter: {status_filter}. Using "scheduled" instead.', 'warning')
        status_filter = 'scheduled'
    
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
    
    # Get bookings with filters
    bookings = get_online_bookings(
        status_filter=status_filter if status_filter != 'all' else None,
        date_from=date_from,
        date_to=date_to
    )
    
    # Get statistics
    stats = get_online_booking_stats()
    
    # Get staff members for assignment
    staff_members = User.query.filter_by(is_active=True).order_by(User.first_name).all()
    
    return render_template('online_bookings.html',
                         bookings=bookings,
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
        flash(f'Booking #{booking_id} accepted successfully', 'success')
        if request.is_json:
            return jsonify({'success': True, 'booking_id': booking_id})
        return redirect(url_for('online_bookings'))
    else:
        flash(f'Error accepting booking: {error}', 'danger')
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
