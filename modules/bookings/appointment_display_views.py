
"""
Appointment Display Views - Comprehensive display logic for booked appointments
"""
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_, desc
from collections import defaultdict

from app import app
from models import Appointment, Customer, Service, User, UnakiBooking
from .bookings_queries import get_appointments_by_date_range, get_appointment_by_id

@app.route('/appointments/display')
@login_required
def appointment_display():
    """Comprehensive appointment display with multiple views"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get filter parameters
    start_date_str = request.args.get('startDate')
    end_date_str = request.args.get('endDate')
    status_filter = request.args.get('status')
    staff_filter = request.args.get('staff', type=int)
    service_filter = request.args.get('service', type=int)
    
    # Set default date range (last 30 days to next 30 days)
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    else:
        start_date = date.today() - timedelta(days=30)
        
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        end_date = date.today() + timedelta(days=30)
    
    # Build base query for traditional appointments
    traditional_query = Appointment.query
    
    # Build base query for Unaki appointments
    unaki_query = UnakiBooking.query
    
    # Apply date filters
    traditional_query = traditional_query.filter(
        func.date(Appointment.appointment_date) >= start_date,
        func.date(Appointment.appointment_date) <= end_date
    )
    
    unaki_query = unaki_query.filter(
        UnakiBooking.appointment_date >= start_date,
        UnakiBooking.appointment_date <= end_date
    )
    
    # Apply status filter
    if status_filter:
        traditional_query = traditional_query.filter(Appointment.status == status_filter)
        unaki_query = unaki_query.filter(UnakiBooking.status == status_filter)
    
    # Apply staff filter
    if staff_filter:
        traditional_query = traditional_query.filter(Appointment.staff_id == staff_filter)
        unaki_query = unaki_query.filter(UnakiBooking.staff_id == staff_filter)
    
    # Apply service filter
    if service_filter:
        traditional_query = traditional_query.filter(Appointment.service_id == service_filter)
        # For Unaki, we need to join with service or filter by service name
        service = Service.query.get(service_filter)
        if service:
            unaki_query = unaki_query.filter(UnakiBooking.service_name == service.name)
    
    # Execute queries
    traditional_appointments = traditional_query.order_by(desc(Appointment.appointment_date)).all()
    unaki_appointments = unaki_query.order_by(desc(UnakiBooking.appointment_date)).all()
    
    # Combine and normalize appointments
    appointments = []
    
    # Add traditional appointments
    for apt in traditional_appointments:
        appointments.append({
            'id': apt.id,
            'type': 'traditional',
            'appointment_date': apt.appointment_date,
            'end_time': apt.end_time,
            'client': apt.client,
            'client_name': apt.client.full_name if apt.client else 'Unknown',
            'client_phone': apt.client.phone if apt.client else None,
            'client_email': apt.client.email if apt.client else None,
            'service': apt.service,
            'service_name': apt.service.name if apt.service else 'Unknown Service',
            'service_duration': apt.service.duration if apt.service else None,
            'assigned_staff': apt.assigned_staff,
            'staff_name': apt.assigned_staff.full_name if apt.assigned_staff else 'Unknown Staff',
            'status': apt.status,
            'amount': apt.amount,
            'amount_charged': apt.amount,
            'discount': apt.discount,
            'payment_status': apt.payment_status,
            'is_paid': apt.is_paid,
            'notes': apt.notes,
            'created_at': apt.created_at,
            'updated_at': apt.updated_at
        })
    
    # Add Unaki appointments
    for apt in unaki_appointments:
        # Combine date and time for appointment_date
        appointment_datetime = datetime.combine(apt.appointment_date, apt.start_time)
        end_datetime = datetime.combine(apt.appointment_date, apt.end_time)
        
        # Get staff object
        staff = User.query.get(apt.staff_id) if apt.staff_id else None
        
        appointments.append({
            'id': apt.id,
            'type': 'unaki',
            'appointment_date': appointment_datetime,
            'end_time': end_datetime,
            'client': None,  # Unaki doesn't use client objects
            'client_name': apt.client_name,
            'client_phone': apt.client_phone,
            'client_email': apt.client_email,
            'service': None,  # Unaki doesn't use service objects
            'service_name': apt.service_name,
            'service_duration': apt.service_duration,
            'assigned_staff': staff,
            'staff_name': apt.staff_name,
            'status': apt.status,
            'amount': apt.service_price,
            'amount_charged': apt.amount_charged,
            'discount': 0,  # Unaki doesn't have discount field
            'payment_status': apt.payment_status,
            'is_paid': apt.payment_status == 'paid',
            'notes': apt.notes,
            'created_at': apt.created_at,
            'updated_at': apt.updated_at
        })
    
    # Sort combined appointments by date
    appointments.sort(key=lambda x: x['appointment_date'], reverse=True)
    
    # Group appointments by date for timeline view
    appointments_by_date = defaultdict(list)
    for apt in appointments:
        apt_date = apt['appointment_date'].date()
        appointments_by_date[apt_date].append(apt)
    
    # Sort dates
    appointments_by_date = dict(sorted(appointments_by_date.items(), reverse=True))
    
    # Calculate statistics
    stats = calculate_appointment_stats(appointments)
    
    # Get dropdown data
    staff_members = User.query.filter(
        User.role.in_(['staff', 'manager', 'admin']),
        User.is_active == True
    ).order_by(User.first_name).all()
    
    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
    
    return render_template('appointment_display.html',
                         appointments=appointments,
                         appointments_by_date=appointments_by_date,
                         stats=stats,
                         staff_members=staff_members,
                         services=services,
                         start_date=start_date.strftime('%Y-%m-%d'),
                         end_date=end_date.strftime('%Y-%m-%d'),
                         status_filter=status_filter,
                         staff_filter=staff_filter,
                         service_filter=service_filter)

def calculate_appointment_stats(appointments):
    """Calculate comprehensive appointment statistics"""
    total_appointments = len(appointments)
    
    stats = {
        'total_appointments': total_appointments,
        'scheduled': 0,
        'confirmed': 0,
        'in_progress': 0,
        'completed': 0,
        'cancelled': 0,
        'no_show': 0,
        'total_revenue': 0,
        'pending_payment': 0,
        'paid_amount': 0
    }
    
    for apt in appointments:
        status = apt['status']
        if status in stats:
            stats[status] += 1
        
        # Revenue calculations
        amount = apt['amount_charged'] or apt['amount'] or 0
        if apt['is_paid']:
            stats['paid_amount'] += amount
        else:
            stats['pending_payment'] += amount
        
        if status == 'completed':
            stats['total_revenue'] += amount
    
    return stats

@app.route('/api/appointment/<int:appointment_id>')
@login_required
def api_appointment_details(appointment_id):
    """Get detailed appointment information"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if it's a traditional appointment first
    appointment = Appointment.query.get(appointment_id)
    
    if appointment:
        return jsonify({
            'id': appointment.id,
            'type': 'traditional',
            'client': {
                'id': appointment.client.id if appointment.client else None,
                'name': appointment.client.full_name if appointment.client else 'Unknown',
                'phone': appointment.client.phone if appointment.client else 'N/A',
                'email': appointment.client.email if appointment.client else 'N/A'
            },
            'service': {
                'id': appointment.service.id if appointment.service else None,
                'name': appointment.service.name if appointment.service else 'Unknown',
                'duration': appointment.service.duration if appointment.service else 0,
                'price': float(appointment.service.price) if appointment.service else 0
            },
            'staff': {
                'id': appointment.assigned_staff.id if appointment.assigned_staff else None,
                'name': appointment.assigned_staff.full_name if appointment.assigned_staff else 'Unknown'
            },
            'appointment_date': appointment.appointment_date.strftime('%Y-%m-%d %H:%M'),
            'end_time': appointment.end_time.strftime('%Y-%m-%d %H:%M') if appointment.end_time else None,
            'status': appointment.status,
            'amount': float(appointment.amount) if appointment.amount else 0,
            'discount': float(appointment.discount) if appointment.discount else 0,
            'payment_status': appointment.payment_status,
            'is_paid': appointment.is_paid,
            'notes': appointment.notes or ''
        })
    
    # Check if it's a Unaki appointment
    unaki_appointment = UnakiBooking.query.get(appointment_id)
    
    if unaki_appointment:
        staff = User.query.get(unaki_appointment.staff_id) if unaki_appointment.staff_id else None
        
        return jsonify({
            'id': unaki_appointment.id,
            'type': 'unaki',
            'client': {
                'id': None,
                'name': unaki_appointment.client_name,
                'phone': unaki_appointment.client_phone or 'N/A',
                'email': unaki_appointment.client_email or 'N/A'
            },
            'service': {
                'id': None,
                'name': unaki_appointment.service_name,
                'duration': unaki_appointment.service_duration,
                'price': float(unaki_appointment.service_price) if unaki_appointment.service_price else 0
            },
            'staff': {
                'id': staff.id if staff else None,
                'name': staff.full_name if staff else unaki_appointment.staff_name
            },
            'appointment_date': f"{unaki_appointment.appointment_date} {unaki_appointment.start_time}",
            'end_time': f"{unaki_appointment.appointment_date} {unaki_appointment.end_time}",
            'status': unaki_appointment.status,
            'amount': float(unaki_appointment.amount_charged) if unaki_appointment.amount_charged else 0,
            'discount': 0,
            'payment_status': unaki_appointment.payment_status,
            'is_paid': unaki_appointment.payment_status == 'paid',
            'notes': unaki_appointment.notes or ''
        })
    
    return jsonify({'error': 'Appointment not found'}), 404

@app.route('/appointments/update-status/<int:appointment_id>', methods=['POST'])
@login_required
def update_appointment_status(appointment_id):
    """Update appointment status"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied'}), 403
    
    new_status = request.form.get('status')
    if new_status not in ['scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show']:
        return jsonify({'error': 'Invalid status'}), 400
    
    # Try traditional appointment first
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        appointment.status = new_status
        appointment.updated_at = datetime.utcnow()
        
        if new_status == 'completed':
            appointment.completed_at = datetime.utcnow()
        
        from app import db
        db.session.commit()
        return jsonify({'success': True, 'message': 'Status updated successfully'})
    
    # Try Unaki appointment
    unaki_appointment = UnakiBooking.query.get(appointment_id)
    if unaki_appointment:
        unaki_appointment.status = new_status
        unaki_appointment.updated_at = datetime.utcnow()
        
        if new_status == 'completed':
            unaki_appointment.completed_at = datetime.utcnow()
        
        from app import db
        db.session.commit()
        return jsonify({'success': True, 'message': 'Status updated successfully'})
    
    return jsonify({'error': 'Appointment not found'}), 404
