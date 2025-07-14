"""
Bookings views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app import app
from forms import AppointmentForm, QuickBookingForm
from .bookings_queries import (
    get_appointments_by_date, get_active_clients, get_active_services, 
    get_staff_members, create_appointment, update_appointment, 
    delete_appointment, get_appointment_by_id
)

@app.route('/bookings')
@login_required
def bookings():
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get date filter from query params
    filter_date = request.args.get('date')
    if filter_date:
        try:
            filter_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
        except ValueError:
            filter_date = date.today()
    else:
        filter_date = date.today()
    
    appointments = get_appointments_by_date(filter_date)
    clients = get_active_clients()
    services = get_active_services()
    staff = get_staff_members()
    
    form = AppointmentForm()
    form.client_id.choices = [(c.id, c.full_name) for c in clients]
    form.service_id.choices = [(s.id, f"{s.name} - ${s.price}") for s in services]
    form.staff_id.choices = [(s.id, s.full_name) for s in staff]
    
    return render_template('bookings.html', 
                         appointments=appointments,
                         form=form,
                         filter_date=filter_date,
                         clients=clients,
                         services=services,
                         staff=staff,
                         timedelta=timedelta,
                         date=date)

@app.route('/bookings/create', methods=['POST'])
@app.route('/add_appointment', methods=['POST'])
@login_required
def create_booking():
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = AppointmentForm()
    clients = get_active_clients()
    services = get_active_services()
    staff = get_staff_members()
    
    form.client_id.choices = [(c.id, c.full_name) for c in clients]
    form.service_id.choices = [(s.id, f"{s.name} - ${s.price}") for s in services]
    form.staff_id.choices = [(s.id, s.full_name) for s in staff]
    
    if form.validate_on_submit():
        appointment_data = {
            'client_id': form.client_id.data,
            'service_id': form.service_id.data,
            'staff_id': form.staff_id.data,
            'appointment_date': form.appointment_date.data,
            'notes': form.notes.data or '',
            'status': 'scheduled'
        }
        
        create_appointment(appointment_data)
        flash('Appointment created successfully!', 'success')
    else:
        flash('Error creating appointment. Please check your input.', 'danger')
    
    return redirect(url_for('bookings'))

@app.route('/bookings/update/<int:id>', methods=['POST'])
@login_required
def update_booking(id):
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    appointment = get_appointment_by_id(id)
    if not appointment:
        flash('Appointment not found', 'danger')
        return redirect(url_for('bookings'))
    
    form = AppointmentForm()
    clients = get_active_clients()
    services = get_active_services()
    staff = get_staff_members()
    
    form.client_id.choices = [(c.id, c.full_name) for c in clients]
    form.service_id.choices = [(s.id, f"{s.name} - ${s.price}") for s in services]
    form.staff_id.choices = [(s.id, s.full_name) for s in staff]
    
    if form.validate_on_submit():
        appointment_data = {
            'client_id': form.client_id.data,
            'service_id': form.service_id.data,
            'staff_id': form.staff_id.data,
            'appointment_date': form.appointment_date.data,
            'notes': form.notes.data or '',
            'status': form.status.data if hasattr(form, 'status') else 'scheduled'
        }
        
        update_appointment(id, appointment_data)
        flash('Appointment updated successfully!', 'success')
    else:
        flash('Error updating appointment. Please check your input.', 'danger')
    
    return redirect(url_for('bookings'))

@app.route('/bookings/delete/<int:id>', methods=['POST'])
@login_required
def delete_booking(id):
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    if delete_appointment(id):
        flash('Appointment deleted successfully!', 'success')
    else:
        flash('Error deleting appointment', 'danger')
    
    return redirect(url_for('bookings'))

@app.route('/add_appointment', methods=['POST'])
@login_required
def add_appointment():
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = AppointmentForm()
    clients = get_active_clients()
    services = get_active_services()
    staff = get_staff_members()
    
    form.client_id.choices = [(c.id, c.full_name) for c in clients]
    form.service_id.choices = [(s.id, f"{s.name} - ${s.price}") for s in services]
    form.staff_id.choices = [(s.id, s.full_name) for s in staff]
    
    if form.validate_on_submit():
        appointment_data = {
            'client_id': form.client_id.data,
            'service_id': form.service_id.data,
            'staff_id': form.staff_id.data,
            'appointment_date': form.appointment_date.data,
            'notes': form.notes.data,
            'amount': form.amount.data,
            'discount': form.discount.data or 0
        }
        
        appointment = create_appointment(appointment_data)
        if appointment:
            flash('Appointment created successfully', 'success')
        else:
            flash('Failed to create appointment', 'danger')
    
    return redirect(url_for('bookings'))