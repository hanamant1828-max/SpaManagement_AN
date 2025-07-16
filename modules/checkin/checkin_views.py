"""
Check-in views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app
from .checkin_queries import (
    get_todays_appointments, get_appointment_by_id, check_in_appointment,
    get_client_by_phone, get_client_appointments_today
)

@app.route('/checkin')
@login_required
def checkin():
    if not current_user.can_access('face_checkin_view'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    appointments = get_todays_appointments()
    
    return render_template('checkin.html', appointments=appointments)

@app.route('/checkin/appointment/<int:id>', methods=['POST'])
@login_required
def checkin_appointment(id):
    if not current_user.can_access('face_checkin_view'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    appointment = check_in_appointment(id)
    if appointment:
        flash(f'Client {appointment.client.full_name} checked in successfully!', 'success')
    else:
        flash('Appointment not found', 'danger')
    
    return redirect(url_for('checkin'))

@app.route('/checkin/search', methods=['POST'])
@login_required
def checkin_search():
    if not current_user.can_access('face_checkin_view'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
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