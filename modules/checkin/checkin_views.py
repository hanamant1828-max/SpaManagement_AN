
"""
Check-in views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from .checkin_queries import (
    get_todays_appointments, get_appointment_by_id, check_in_appointment,
    get_client_by_phone, get_client_appointments_today
)

# Import face recognition API (optional)
try:
    from . import face_recognition_api
except ImportError as e:
    print(f"⚠️ Face recognition not available: {e}")
    face_recognition_api = None

@app.route('/checkin')
@login_required
def checkin():
    """Face recognition check-in page"""
    try:
        appointments = get_todays_appointments()
        return render_template('checkin.html', appointments=appointments)
    except Exception as e:
        print(f"Checkin error: {e}")
        flash('Error loading check-in page', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/checkin/appointment/<int:id>', methods=['POST'])
@login_required
def checkin_appointment(id):
    """Check in an appointment"""
    try:
        appointment = check_in_appointment(id)
        if appointment:
            flash(f'Client {appointment.client.full_name} checked in successfully!', 'success')
        else:
            flash('Appointment not found', 'danger')
        return redirect(url_for('checkin'))
    except Exception as e:
        print(f"Checkin appointment error: {e}")
        flash('Error checking in appointment', 'danger')
        return redirect(url_for('checkin'))

@app.route('/checkin/search', methods=['POST'])
@login_required
def checkin_search():
    """Search for client by phone"""
    try:
        phone = request.form.get('phone')
        if phone:
            client = get_client_by_phone(phone)
            if client:
                appointments = get_client_appointments_today(client.id)
                return render_template('checkin.html', 
                                     appointments=appointments, 
                                     search_client=client)
            else:
                flash('Client not found with this phone number', 'warning')
        return redirect(url_for('checkin'))
    except Exception as e:
        print(f"Checkin search error: {e}")
        flash('Error searching for client', 'danger')
        return redirect(url_for('checkin'))

@app.route('/api/customer/<int:customer_id>/appointments', methods=['GET'])
@login_required
def api_get_customer_appointments(customer_id):
    """Get customer appointments for a specific date"""
    try:
        from datetime import datetime, date
        from models import Appointment, Customer, UnakiBooking
        from sqlalchemy import func, or_
        
        # Get date parameter (default to today)
        date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get customer
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
        
        # Get appointments from both Appointment and UnakiBooking tables
        appointments_data = []
        
        # Query legacy Appointment table
        legacy_appointments = Appointment.query.filter(
            Appointment.client_id == customer_id,
            func.date(Appointment.appointment_date) == target_date
        ).all()
        
        for apt in legacy_appointments:
            appointments_data.append({
                'id': apt.id,
                'client_name': customer.full_name,
                'service_name': apt.service.name if apt.service else 'Unknown',
                'staff_name': apt.assigned_staff.full_name if apt.assigned_staff else 'Unassigned',
                'appointment_date': apt.appointment_date.isoformat(),
                'status': apt.status,
                'amount': float(apt.amount) if apt.amount else 0.0
            })
        
        # Query UnakiBooking table (new booking system)
        unaki_bookings = UnakiBooking.query.filter(
            or_(
                UnakiBooking.client_id == customer_id,
                UnakiBooking.client_phone == customer.phone
            ),
            UnakiBooking.appointment_date == target_date
        ).all()
        
        for booking in unaki_bookings:
            appointments_data.append({
                'id': booking.id,
                'client_name': booking.client_name,
                'service_name': booking.service_name,
                'staff_name': booking.staff_name,
                'appointment_date': f"{booking.appointment_date.isoformat()}T{booking.start_time.isoformat()}",
                'status': booking.status,
                'amount': float(booking.service_price) if booking.service_price else 0.0
            })
        
        return jsonify({
            'success': True,
            'appointments': appointments_data,
            'customer': {
                'id': customer.id,
                'name': customer.full_name,
                'phone': customer.phone
            }
        })
        
    except Exception as e:
        print(f"Error getting customer appointments: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
