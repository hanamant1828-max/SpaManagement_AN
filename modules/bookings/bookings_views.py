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
    delete_appointment, get_appointment_by_id, get_time_slots,
    get_appointment_stats, get_staff_schedule, get_appointments_by_date_range
)

@app.route('/bookings')
@login_required
def bookings():
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get filters from query params
    filter_date = request.args.get('date')
    view_type = request.args.get('view', 'calendar')  # calendar, table, timeline
    staff_filter = request.args.get('staff_id', type=int)
    
    if filter_date:
        try:
            filter_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
        except ValueError:
            filter_date = date.today()
    else:
        filter_date = date.today()
    
    # Get data based on view type
    appointments = get_appointments_by_date(filter_date)
    if staff_filter:
        appointments = [a for a in appointments if a.staff_id == staff_filter]
    
    clients = get_active_clients()
    services = get_active_services()
    staff = get_staff_members()
    
    # Get time slots for the selected date
    time_slots = get_time_slots(filter_date, staff_filter)
    
    # Get appointment statistics
    stats = get_appointment_stats(filter_date)
    
    # Create appointment form
    form = AppointmentForm()
    form.client_id.choices = [(c.id, c.full_name) for c in clients]
    form.service_id.choices = [(s.id, f"{s.name} - ${s.price:.2f}") for s in services]
    form.staff_id.choices = [(s.id, s.full_name) for s in staff]
    
    return render_template('bookings.html', 
                         appointments=appointments,
                         form=form,
                         filter_date=filter_date,
                         view_type=view_type,
                         staff_filter=staff_filter,
                         time_slots=time_slots,
                         stats=stats,
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

# API Endpoints for Dynamic Booking Features
@app.route('/api/time-slots')
@login_required
def api_time_slots():
    """API endpoint to get available time slots"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied'}), 403
    
    date_str = request.args.get('date')
    staff_id = request.args.get('staff_id', type=int)
    service_id = request.args.get('service_id', type=int)
    
    if not date_str:
        return jsonify({'error': 'Date is required'}), 400
    
    try:
        filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    time_slots = get_time_slots(filter_date, staff_id, service_id)
    
    return jsonify({
        'slots': time_slots,
        'date': date_str,
        'staff_id': staff_id,
        'service_id': service_id
    })

@app.route('/api/appointment/<int:appointment_id>')
@login_required
def api_appointment_details(appointment_id):
    """API endpoint to get appointment details"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied'}), 403
    
    appointment = get_appointment_by_id(appointment_id)
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    return jsonify({
        'id': appointment.id,
        'client': {
            'id': appointment.client.id,
            'name': appointment.client.full_name,
            'phone': appointment.client.phone,
            'email': appointment.client.email
        },
        'service': {
            'id': appointment.service.id,
            'name': appointment.service.name,
            'duration': appointment.service.duration,
            'price': float(appointment.service.price)
        },
        'staff': {
            'id': appointment.staff.id,
            'name': appointment.staff.full_name
        },
        'appointment_date': appointment.appointment_date.strftime('%Y-%m-%d %H:%M'),
        'status': appointment.status,
        'notes': appointment.notes,
        'amount': float(appointment.amount) if appointment.amount else 0
    })

@app.route('/bookings/update-status/<int:appointment_id>', methods=['POST'])
@login_required
def update_appointment_status(appointment_id):
    """Update appointment status"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    new_status = request.form.get('status')
    if new_status not in ['pending', 'confirmed', 'completed', 'cancelled']:
        flash('Invalid status', 'danger')
        return redirect(url_for('bookings'))
    
    appointment = get_appointment_by_id(appointment_id)
    if not appointment:
        flash('Appointment not found', 'danger')
        return redirect(url_for('bookings'))
    
    update_appointment(appointment_id, {'status': new_status})
    flash(f'Appointment status updated to {new_status}', 'success')
    
    return redirect(url_for('bookings'))