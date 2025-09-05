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
from models import Service, Customer, User

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
    
    # Debug: Print service data
    print(f"Services loaded for booking: {len(services)} services found")
    for service in services:
        print(f"Service: {service.name}, Price: {service.price}, Active: {service.is_active}")
    
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

@app.route('/calendar-booking')
@login_required
def calendar_booking():
    """Calendar timetable view for booking appointments"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get selected date from query params
    selected_date_str = request.args.get('date')
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    # Get staff members
    staff_members = get_staff_members()
    
    # Generate time slots for the day (9 AM to 6 PM, 30-minute intervals)
    time_slots = []
    start_time = datetime.combine(selected_date, datetime.min.time().replace(hour=9))
    end_time = datetime.combine(selected_date, datetime.min.time().replace(hour=18))
    
    current_time = start_time
    while current_time < end_time:
        time_slots.append({
            'start_time': current_time,
            'duration': 30
        })
        current_time += timedelta(minutes=30)
    
    # Get staff availability for each time slot
    staff_availability = {}
    existing_appointments = get_appointments_by_date(selected_date)
    
    for staff in staff_members:
        for time_slot in time_slots:
            slot_key = (staff.id, time_slot['start_time'])
            
            # Check if this time slot is booked
            booked_appointment = None
            for appointment in existing_appointments:
                if (appointment.staff_id == staff.id and 
                    appointment.appointment_date.time() == time_slot['start_time'].time()):
                    booked_appointment = appointment
                    break
            
            if booked_appointment:
                staff_availability[slot_key] = {
                    'status': 'booked',
                    'client_name': booked_appointment.client.full_name if booked_appointment.client else 'Unknown',
                    'service_name': booked_appointment.service.name if booked_appointment.service else 'Service'
                }
            else:
                staff_availability[slot_key] = {
                    'status': 'available'
                }
    
    # Get clients and services
    clients = get_active_clients()
    services = get_active_services()
    
    # Get today's stats
    today_appointments = get_appointments_by_date(date.today()) if selected_date == date.today() else []
    today_revenue = sum(apt.amount for apt in today_appointments if apt.amount and apt.payment_status == 'paid')
    
    return render_template('calendar_booking.html',
                         selected_date=selected_date,
                         staff_members=staff_members,
                         time_slots=time_slots,
                         staff_availability=staff_availability,
                         clients=clients,
                         services=services,
                         today_appointments=today_appointments,
                         today_revenue=today_revenue)

@app.route('/appointments/book', methods=['POST'])
@login_required
def book_appointment_api():
    """API endpoint to book an appointment from the calendar view"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['client_id', 'staff_id', 'service_id', 'appointment_date', 'appointment_time']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Parse date and time
        appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
        appointment_datetime = datetime.combine(appointment_date, appointment_time)
        
        # Get service details for pricing
        service = Service.query.get(data['service_id'])
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        # Create appointment data
        appointment_data = {
            'client_id': data['client_id'],
            'service_id': data['service_id'],
            'staff_id': data['staff_id'],
            'appointment_date': appointment_datetime,
            'notes': data.get('notes', ''),
            'status': 'scheduled',
            'amount': service.price,
            'payment_status': 'pending'
        }
        
        # Create the appointment
        appointment = create_appointment(appointment_data)
        
        return jsonify({
            'success': True,
            'appointment_id': appointment.id,
            'message': 'Appointment booked successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/booking-services')
@login_required
def api_booking_services():
    """API endpoint to get all active services"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        services = get_active_services()
        return jsonify([{
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'duration': service.duration,
            'price': float(service.price),
            'category': service.category,
            'is_active': service.is_active
        } for service in services])
    except Exception as e:
        print(f"Error in api_services: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/quick-book', methods=['POST'])
@login_required
def api_quick_book():
    """Quick booking API - minimal data required"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        # Get the next available slot for this staff/service combination
        from datetime import datetime, timedelta
        
        # Default to tomorrow at 9 AM if no time specified
        if 'appointment_date' not in data:
            tomorrow = datetime.now() + timedelta(days=1)
            appointment_datetime = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        else:
            appointment_datetime = datetime.strptime(data['appointment_date'], '%Y-%m-%d %H:%M')
        
        # Get service details
        service = Service.query.get(data['service_id'])
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        # Create appointment with minimal data
        appointment_data = {
            'client_id': data['client_id'],
            'service_id': data['service_id'],
            'staff_id': data.get('staff_id', 1),  # Default to first staff if not specified
            'appointment_date': appointment_datetime,
            'notes': data.get('notes', 'Quick booking'),
            'status': 'scheduled',
            'amount': service.price
        }
        
        appointment = create_appointment(appointment_data)
        
        return jsonify({
            'success': True,
            'appointment_id': appointment.id,
            'message': 'Quick booking successful!',
            'appointment_time': appointment_datetime.strftime('%Y-%m-%d %H:%M')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/appointments/schedule')
@login_required 
def appointments_schedule():
    """Timetable view for appointment scheduling - exactly as requested"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get selected date from query params
    selected_date_str = request.args.get('date')
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    # Get staff members
    staff_members = get_staff_members()
    
    # Generate time slots for the day (9 AM to 6 PM, 30-minute intervals)
    time_slots = []
    start_time = datetime.combine(selected_date, datetime.min.time().replace(hour=9))
    end_time = datetime.combine(selected_date, datetime.min.time().replace(hour=18))
    
    current_time = start_time
    while current_time < end_time:
        time_slots.append({
            'start_time': current_time,
            'end_time': current_time + timedelta(minutes=30),
            'duration': 30
        })
        current_time += timedelta(minutes=30)
    
    # Get existing appointments for the selected date
    existing_appointments = get_appointments_by_date(selected_date)
    
    # Create staff availability grid
    staff_availability = {}
    for staff in staff_members:
        for time_slot in time_slots:
            slot_key = (staff.id, time_slot['start_time'])
            
            # Check if this time slot is booked
            booked_appointment = None
            for appointment in existing_appointments:
                if (appointment.staff_id == staff.id and 
                    appointment.appointment_date <= time_slot['start_time'] and
                    (appointment.end_time is None or appointment.end_time > time_slot['start_time']) and
                    appointment.status != 'cancelled'):
                    booked_appointment = appointment
                    break
            
            if booked_appointment:
                staff_availability[slot_key] = {
                    'status': 'booked',
                    'appointment': booked_appointment,
                    'client_name': booked_appointment.client.full_name if booked_appointment.client else 'Unknown',
                    'service_name': booked_appointment.service.name if booked_appointment.service else 'Service',
                    'time_range': f"{booked_appointment.appointment_date.strftime('%H:%M')} - {booked_appointment.end_time.strftime('%H:%M') if booked_appointment.end_time else 'N/A'}"
                }
            else:
                staff_availability[slot_key] = {
                    'status': 'available'
                }
    
    # Get clients and services for booking form
    clients = get_active_clients()
    services = get_active_services()
    
    return render_template('appointments_schedule.html',
                         selected_date=selected_date,
                         staff_members=staff_members,
                         time_slots=time_slots,
                         staff_availability=staff_availability,
                         clients=clients,
                         services=services)

@app.route('/appointments/book', methods=['GET', 'POST'])
@login_required
def appointments_book():
    """Book appointment form with pre-filled staff and time"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get pre-filled data from query params
    staff_id = request.args.get('staff_id', type=int)
    appointment_date = request.args.get('date')
    appointment_time = request.args.get('time')
    
    if request.method == 'POST':
        try:
            # Get form data
            client_id = request.form.get('client_id', type=int)
            service_id = request.form.get('service_id', type=int)
            staff_id = request.form.get('staff_id', type=int)
            appointment_date = request.form.get('appointment_date')
            appointment_time = request.form.get('appointment_time')
            notes = request.form.get('notes', '')
            
            # Validate required fields
            if not all([client_id, service_id, staff_id, appointment_date, appointment_time]):
                flash('All fields are required', 'danger')
                return redirect(request.url)
            
            # Parse date and time
            appointment_date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            appointment_time_obj = datetime.strptime(appointment_time, '%H:%M').time()
            appointment_datetime = datetime.combine(appointment_date_obj, appointment_time_obj)
            
            # Get service details for end time calculation
            service = Service.query.get(service_id)
            if not service:
                flash('Service not found', 'danger')
                return redirect(request.url)
            
            end_time = appointment_datetime + timedelta(minutes=service.duration)
            
            # Create appointment data
            appointment_data = {
                'client_id': client_id,
                'service_id': service_id,
                'staff_id': staff_id,
                'appointment_date': appointment_datetime,
                'end_time': end_time,
                'notes': notes,
                'status': 'scheduled',
                'amount': service.price
            }
            
            # Create the appointment
            appointment = create_appointment(appointment_data)
            
            if appointment:
                flash('Appointment booked successfully!', 'success')
                return redirect(url_for('appointments_schedule', date=appointment_date))
            else:
                flash('Error booking appointment', 'danger')
                
        except Exception as e:
            flash(f'Error booking appointment: {str(e)}', 'danger')
    
    # Get data for form
    clients = get_active_clients()
    services = get_active_services()
    staff_members = get_staff_members()
    
    return render_template('appointments_book.html',
                         clients=clients,
                         services=services,
                         staff_members=staff_members,
                         staff_id=staff_id,
                         appointment_date=appointment_date,
                         appointment_time=appointment_time)

@app.route('/appointments/cancel/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    appointment = get_appointment_by_id(appointment_id)
    if not appointment:
        flash('Appointment not found', 'danger')
        return redirect(url_for('appointments_schedule'))
    
    # Update status to cancelled
    update_appointment(appointment_id, {'status': 'cancelled'})
    flash('Appointment cancelled successfully!', 'success')
    
    # Get the date to redirect back to schedule
    appointment_date = appointment.appointment_date.strftime('%Y-%m-%d')
    return redirect(url_for('appointments_schedule', date=appointment_date))

@app.route('/appointments/edit/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def edit_appointment(appointment_id):
    """Edit an existing appointment"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    appointment = get_appointment_by_id(appointment_id)
    if not appointment:
        flash('Appointment not found', 'danger')
        return redirect(url_for('appointments_schedule'))
    
    if request.method == 'POST':
        try:
            # Get form data
            client_id = request.form.get('client_id', type=int)
            service_id = request.form.get('service_id', type=int)
            staff_id = request.form.get('staff_id', type=int)
            appointment_date = request.form.get('appointment_date')
            appointment_time = request.form.get('appointment_time')
            notes = request.form.get('notes', '')
            
            # Parse date and time
            appointment_date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            appointment_time_obj = datetime.strptime(appointment_time, '%H:%M').time()
            appointment_datetime = datetime.combine(appointment_date_obj, appointment_time_obj)
            
            # Get service details for end time calculation
            service = Service.query.get(service_id)
            if service:
                end_time = appointment_datetime + timedelta(minutes=service.duration)
            else:
                end_time = appointment.end_time
            
            # Update appointment data
            appointment_data = {
                'client_id': client_id,
                'service_id': service_id,
                'staff_id': staff_id,
                'appointment_date': appointment_datetime,
                'end_time': end_time,
                'notes': notes,
                'amount': service.price if service else appointment.amount
            }
            
            # Update the appointment
            update_appointment(appointment_id, appointment_data)
            flash('Appointment updated successfully!', 'success')
            return redirect(url_for('appointments_schedule', date=appointment_date))
            
        except Exception as e:
            flash(f'Error updating appointment: {str(e)}', 'danger')
    
    # Get data for form
    clients = get_active_clients()
    services = get_active_services()
    staff_members = get_staff_members()
    
    return render_template('appointments_edit.html',
                         appointment=appointment,
                         clients=clients,
                         services=services,
                         staff_members=staff_members)