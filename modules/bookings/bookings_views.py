"""
Bookings views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta, time
from app import app
from forms import AppointmentForm, QuickBookingForm
from .bookings_queries import (
    get_appointments_by_date, get_active_clients, get_active_services, 
    get_staff_members, create_appointment, update_appointment, 
    delete_appointment, get_appointment_by_id, get_time_slots,
    get_appointment_stats, get_staff_schedule, get_appointments_by_date_range
)
# Import models
from models import Appointment, Customer, Service, User, ShiftManagement, ShiftLogs
# Late imports to avoid circular dependency
from sqlalchemy import func
import re # Import re for regular expressions

# Helper function to get staff schedule for a specific date
def get_staff_schedule_for_date(staff_id, target_date):
    """Get the detailed schedule for a staff member on a specific date"""
    try:
        # Get shift management for this staff member and date
        shift_management = ShiftManagement.query.filter(
            ShiftManagement.staff_id == staff_id,
            ShiftManagement.from_date <= target_date,
            ShiftManagement.to_date >= target_date
        ).first()

        if not shift_management:
            return None

        # Get specific shift log for this date
        shift_log = ShiftLogs.query.filter(
            ShiftLogs.shift_management_id == shift_management.id,
            ShiftLogs.individual_date == target_date
        ).first()

        if not shift_log:
            return None

        return {
            'schedule_id': shift_management.id,
            'daily_schedule_id': shift_log.id,
            'schedule_name': f'Shift {target_date}',
            'shift_start_time': shift_log.shift_start_time,
            'shift_end_time': shift_log.shift_end_time,
            'break_start_time': shift_log.break_start_time,
            'break_end_time': shift_log.break_end_time,
            'break_duration_minutes': 0,
            'break_time': shift_log.get_break_time_display() if shift_log.break_start_time and shift_log.break_end_time else 'No break',
            'is_working_day': shift_log.status in ['scheduled', 'completed'],
            'notes': ''
        }

    except Exception as e:
        print(f"Error getting staff schedule for date: {e}")
        return None


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

    customers = get_active_clients() # Renamed from clients to customers for consistency
    services = get_active_services()
    staff_members = get_staff_members() # Renamed from staff to staff_members

    # Debug: Print service data
    print(f"Services loaded for booking: {len(services)} services found")
    for service in services:
        print(f"Service: {service.name}, Price: {service.price}, Active: {service.is_active}")

    # Get time slots for the selected date
    time_slots = get_time_slots(filter_date, staff_filter)

    # Get appointment statistics
    stats = get_appointment_stats(filter_date)

    form = AppointmentForm()

    # Get customer_id from URL parameter and validate it
    customer_id_param = request.args.get('customer_id')
    preselected_customer_id = None

    if customer_id_param:
        try:
            preselected_customer_id = int(customer_id_param)
            # Validate that the customer exists
            customer_exists = any(c.id == preselected_customer_id for c in customers)
            if not customer_exists:
                preselected_customer_id = None
        except (ValueError, TypeError):
            preselected_customer_id = None

    # Populate choices
    form.customer_id.choices = [(0, 'Select Customer')] + [(c.id, c.full_name) for c in customers]
    form.service_id.choices = [(0, 'Select Service')] + [(s.id, s.name) for s in services]
    form.staff_id.choices = [(0, 'Select Staff (Optional)')] + [(u.id, f"{u.first_name} {u.last_name}") for u in staff_members]

    # Set the preselected customer if valid
    if preselected_customer_id:
        form.customer_id.data = preselected_customer_id

    return render_template('bookings.html', 
                         appointments=appointments,
                         form=form,
                         filter_date=filter_date,
                         view_type=view_type,
                         staff_filter=staff_filter,
                         time_slots=time_slots,
                         stats=stats,
                         customers=customers, # Pass customers to template
                         services=services,
                         staff_members=staff_members, # Pass staff_members to template
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
    customers = get_active_clients() # Renamed from clients to customers
    services = get_active_services()
    staff_members = get_staff_members() # Renamed from staff to staff_members

    form.customer_id.choices = [(0, 'Select Customer')] + [(c.id, c.full_name) for c in customers]
    form.service_id.choices = [(0, 'Select Service')] + [(s.id, s.name) for s in services]
    form.staff_id.choices = [(0, 'Select Staff (Optional)')] + [(u.id, f"{u.first_name} {u.last_name}") for u in staff_members]

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
    customers = get_active_clients() # Renamed from clients to customers
    services = get_active_services()
    staff_members = get_staff_members() # Renamed from staff to staff_members

    form.customer_id.choices = [(0, 'Select Customer')] + [(c.id, c.full_name) for c in customers]
    form.service_id.choices = [(0, 'Select Service')] + [(s.id, s.name) for s in services]
    form.staff_id.choices = [(0, 'Select Staff (Optional)')] + [(u.id, f"{u.first_name} {u.last_name}") for u in staff_members]

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
    customers = get_active_clients() # Renamed from clients to customers
    services = get_active_services()
    staff_members = get_staff_members() # Renamed from staff to staff_members

    form.customer_id.choices = [(0, 'Select Customer')] + [(c.id, c.full_name) for c in customers]
    form.service_id.choices = [(0, 'Select Service')] + [(s.id, s.name) for s in services]
    form.staff_id.choices = [(0, 'Select Staff (Optional)')] + [(u.id, f"{u.first_name} {u.last_name}") for u in staff_members]

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
    """Calendar timetable view for booking appointments with enhanced shift scheduler integration"""
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

    # Get day of week for schedule checking
    day_of_week = selected_date.weekday()  # Monday = 0, Sunday = 6
    day_mapping = {
        0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday',
        4: 'friday', 5: 'saturday', 6: 'sunday'
    }
    selected_day_field = day_mapping[day_of_week]

    # Get staff schedules for the selected date with enhanced logic
    staff_schedules = {}
    for staff in staff_members:
        # Find active schedules that cover the selected date and include the day of week
        schedule_info = get_staff_schedule_for_date(staff.id, selected_date)

        if schedule_info and schedule_info.get('is_working_day'):
            staff_schedules[staff.id] = {
                'shift_start': schedule_info['shift_start_time'],
                'shift_end': schedule_info['shift_end_time'],
                'schedule_name': schedule_info['schedule_name'],
                'break_time': schedule_info['break_time'],
                'break_start': schedule_info.get('break_start_time'),
                'break_end': schedule_info.get('break_end_time'),
                'is_absent': False,
                'has_shift': True,
                'schedule_id': schedule_info.get('schedule_id'),
                'daily_schedule_id': schedule_info.get('daily_schedule_id'),
                'notes': schedule_info.get('notes', '')
            }
        else:
            # No schedule found or not a working day
            staff_schedules[staff.id] = {
                'shift_start': None,
                'shift_end': None,
                'schedule_name': schedule_info.get('schedule_name', 'Not Scheduled'),
                'break_time': None,
                'break_start': None,
                'break_end': None,
                'is_absent': True, # Treat as absent if no valid schedule
                'has_shift': False,
                'schedule_id': None,
                'daily_schedule_id': None,
                'notes': schedule_info.get('notes', 'No shift scheduled or day off')
            }

    # Generate flexible time slots from 8 AM to 8 PM with configurable intervals
    def generate_flexible_time_slots(start_hour=8, end_hour=20, slot_duration=15):
        """Generate time slots with flexible durations (5, 10, 15, 30, 45, 60 minutes)"""
        time_slots = []
        start_time = datetime.combine(selected_date, datetime.min.time().replace(hour=start_hour))
        end_time = datetime.combine(selected_date, datetime.min.time().replace(hour=end_hour))
        
        current_time = start_time
        while current_time < end_time:
            time_slots.append({
                'start_time': current_time,
                'end_time': current_time + timedelta(minutes=slot_duration),
                'duration': slot_duration
            })
            current_time += timedelta(minutes=slot_duration)
        
        return time_slots
    
    # Get slot duration from request parameter or default to 15 minutes
    slot_duration = int(request.args.get('slot_duration', 15))
    valid_durations = [5, 10, 15, 30, 45, 60]
    if slot_duration not in valid_durations:
        slot_duration = 15
    
    time_slots = generate_flexible_time_slots(slot_duration=slot_duration)

    # Get existing appointments for the selected date
    existing_appointments = get_appointments_by_date(selected_date)

    # Create staff availability grid with enhanced shift integration
    staff_availability = {}
    for staff in staff_members:
        schedule_info = staff_schedules.get(staff.id)

        for time_slot in time_slots:
            slot_key = (staff.id, time_slot['start_time'])
            slot_time = time_slot['start_time'].time()

            # Check if staff is absent or has no shift
            if not schedule_info or not schedule_info.get('has_shift'):
                staff_availability[slot_key] = {
                    'status': 'not_available',
                    'reason': schedule_info.get('notes', 'No shift scheduled'),
                    'display_text': 'Not Available',
                    'css_class': 'bg-secondary text-white',
                    'schedule_info': schedule_info.get('schedule_name', 'No Shift') if schedule_info else 'No Shift'
                }
                continue

            # Get shift times
            shift_start = schedule_info['shift_start']
            shift_end = schedule_info['shift_end']
            break_start = schedule_info.get('break_start')
            break_end = schedule_info.get('break_end')

            # Get break time string from schedule_info
            break_time_str = schedule_info.get('break_time')

            # Check if time slot is outside working hours
            if shift_start and shift_end:
                if slot_time < shift_start or slot_time >= shift_end:
                    # Convert to 12-hour format for display
                    shift_start_12h = shift_start.strftime('%I:%M %p')
                    shift_end_12h = shift_end.strftime('%I:%M %p')
                    staff_availability[slot_key] = {
                        'status': 'off_duty',
                        'reason': f'Off duty (Shift: {shift_start_12h} - {shift_end_12h})',
                        'display_text': 'Off Duty',
                        'shift_times': f'{shift_start_12h} - {shift_end_12h}',
                        'css_class': 'bg-light text-muted',
                        'schedule_info': schedule_info.get('schedule_name', '')
                    }
                    continue

            # Check if time slot is during break time (CRITICAL: MUST BE BEFORE booking checks)
            if break_start and break_end:
                if break_start <= slot_time < break_end:
                    break_start_12h = break_start.strftime('%I:%M %p')
                    break_end_12h = break_end.strftime('%I:%M %p')
                    staff_availability[slot_key] = {
                        'status': 'break',
                        'reason': f'Break time ({break_start_12h} - {break_end_12h})',
                        'display_text': 'Break Time',
                        'break_times': f'{break_start_12h} - {break_end_12h}',
                        'css_class': 'bg-warning text-dark',
                        'schedule_info': schedule_info.get('break_time', '')
                    }
                    continue

            # Check if this time slot conflicts with existing appointments
            is_blocked_by_appointment = False
            blocking_appointment = None

            for appointment in existing_appointments:
                if appointment.staff_id == staff.id and appointment.status != 'cancelled':
                    apt_start = appointment.appointment_date
                    service_duration = appointment.service.duration if appointment.service else 60
                    apt_end = apt_start + timedelta(minutes=service_duration)

                    # Check if current slot overlaps with this appointment
                    slot_start = time_slot['start_time']
                    slot_end = slot_start + timedelta(minutes=slot_duration) # Use flexible slot duration for checking overlap

                    if not (slot_end <= apt_start or slot_start >= apt_end):
                        is_blocked_by_appointment = True
                        blocking_appointment = appointment
                        break

            if is_blocked_by_appointment and blocking_appointment:
                # Show appointment details only on the first slot of the appointment
                apt_start_time = blocking_appointment.appointment_date.time()
                if slot_time == apt_start_time:
                    service_duration = blocking_appointment.service.duration if blocking_appointment.service else 60
                    end_time = blocking_appointment.appointment_date + timedelta(minutes=service_duration)
                    staff_availability[slot_key] = {
                        'status': 'booked',
                        'appointment': blocking_appointment,
                        'client_name': blocking_appointment.client.full_name if blocking_appointment.client else 'Unknown',
                        'service_name': blocking_appointment.service.name if blocking_appointment.service else 'Service',
                        'service_duration': service_duration,
                        'end_time': end_time.strftime('%I:%M %p'),
                        'display_text': f'{blocking_appointment.service.name if blocking_appointment.service else "Service"} ({service_duration}min)',
                        'css_class': 'bg-danger text-white appointment-block',
                        'schedule_info': f'{blocking_appointment.client.full_name if blocking_appointment.client else "Unknown"} - {blocking_appointment.service.name if blocking_appointment.service else "Service"}',
                        'appointment_duration': service_duration,
                        'can_book': False
                    }
                else:
                    # Continuation of the same appointment
                    staff_availability[slot_key] = {
                        'status': 'booked_continuation',
                        'display_text': '↑ Cont.',
                        'css_class': 'bg-danger text-white appointment-continuation',
                        'schedule_info': 'Appointment in progress',
                        'can_book': False
                    }
            else:
                # Available slot within shift hours and outside break time
                shift_start_12h = shift_start.strftime('%I:%M %p') if shift_start else 'N/A'
                shift_end_12h = shift_end.strftime('%I:%M %p') if shift_end else 'N/A'

                # Check if there's enough time for shortest service (15 minutes) before shift end
                remaining_shift_time = (datetime.combine(selected_date, shift_end) - time_slot['start_time']).total_seconds() / 60 if shift_end else 480

                staff_availability[slot_key] = {
                    'status': 'available',
                    'schedule_info': schedule_info['schedule_name'] if schedule_info else None,
                    'display_text': 'Available',
                    'shift_times': f'{shift_start_12h} - {shift_end_12h}',
                    'css_class': 'btn btn-success available-slot',
                    'remaining_time': int(remaining_shift_time),
                    'can_book': remaining_shift_time >= 15
                }

    # Get clients and services for booking form
    clients = get_active_clients()
    services = get_active_services()

    # Get today's stats for selected date
    today_appointments = get_appointments_by_date(selected_date)
    today_revenue = sum(apt.amount for apt in today_appointments if apt.amount and getattr(apt, 'payment_status', 'pending') == 'paid')

    return render_template('calendar_booking.html',
                         selected_date=selected_date,
                         staff_members=staff_members,
                         time_slots=time_slots,
                         staff_availability=staff_availability,
                         staff_schedules=staff_schedules,
                         clients=clients,
                         services=services,
                         today_appointments=today_appointments,
                         today_revenue=today_revenue)

@app.route('/appointments/book', methods=['POST'])
@login_required
def book_appointment_api():
    """API endpoint to book an appointment from the calendar view with staff availability validation"""
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

        # Validate staff availability against shift scheduler
        from models import ShiftManagement, ShiftLogs, User

        staff = User.query.get(data['staff_id'])
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404

        # Check if staff has a schedule for this date using new shift management system
        shift_management = ShiftManagement.query.filter(
            ShiftManagement.staff_id == data['staff_id'],
            ShiftManagement.from_date <= appointment_date,
            ShiftManagement.to_date >= appointment_date
        ).first()

        if not shift_management:
            return jsonify({'error': f'{staff.first_name} {staff.last_name} is not scheduled to work on {appointment_date.strftime("%A, %B %d, %Y")}. Please check staff schedule.'}), 400

        # Get specific shift log for this date
        shift_log = ShiftLogs.query.filter(
            ShiftLogs.shift_management_id == shift_management.id,
            ShiftLogs.individual_date == appointment_date
        ).first()

        if not shift_log or shift_log.status not in ['scheduled', 'completed']:
            return jsonify({'error': f'{staff.first_name} {staff.last_name} is not available on {appointment_date.strftime("%A, %B %d, %Y")}. Status: {shift_log.status if shift_log else "No schedule"}'}), 400

        # Check if appointment time is within shift hours
        shift_start = shift_log.shift_start_time
        shift_end = shift_log.shift_end_time

        if shift_start and shift_end:
            if appointment_time < shift_start or appointment_time >= shift_end:
                shift_start_12h = shift_start.strftime('%I:%M %p')
                shift_end_12h = shift_end.strftime('%I:%M %p')
                return jsonify({'error': f'{staff.first_name} {staff.last_name} is off duty at {appointment_time.strftime("%I:%M %p")}. Shift hours: {shift_start_12h} - {shift_end_12h}'}), 400

        # Check if appointment time conflicts with break time
        break_start = shift_log.break_start_time
        break_end = shift_log.break_end_time

        if break_start and break_end:
            if break_start <= appointment_time < break_end:
                break_start_12h = break_start.strftime('%I:%M %p')
                break_end_12h = break_end.strftime('%I:%M %p')
                return jsonify({'error': f'{staff.first_name} {staff.last_name} is on break at {appointment_time.strftime("%I:%M %p")}. Break time: {break_start_12h} - {break_end_12h}'}), 400

        # Check for existing appointments at the same time
        existing_appointment = get_appointments_by_date(appointment_date)
        for apt in existing_appointment:
            if (apt.staff_id == data['staff_id'] and 
                apt.appointment_date.time() == appointment_time and
                apt.status != 'cancelled'):
                return jsonify({'error': f'{staff.first_name} {staff.last_name} already has an appointment at {appointment_time.strftime("%I:%M %p")}'}), 400

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
            'end_time': appointment_datetime + timedelta(minutes=service.duration),
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
            'message': f'Appointment booked successfully for {appointment_datetime.strftime("%I:%M %p")} on {appointment_date.strftime("%B %d, %Y")}'
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
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

@app.route('/staff-availability')
@login_required
def staff_availability():
    """Enhanced staff availability with proper shift scheduler integration"""
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get selected date from query parameter or default to today
    selected_date_str = request.args.get('date')
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

    # Get all active staff members
    staff_members = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()

    # Get all active clients and services for quick booking
    clients = Customer.query.filter_by(is_active=True).order_by(Customer.first_name, Customer.last_name).all()
    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()

    # Generate flexible time slots for the day (8 AM to 10 PM with configurable intervals)
    slot_duration = int(request.args.get('slot_duration', 15))
    valid_durations = [5, 10, 15, 30, 45, 60]
    if slot_duration not in valid_durations:
        slot_duration = 15
    
    time_slots = []
    start_time = datetime.combine(selected_date, time(8, 0))
    end_time = datetime.combine(selected_date, time(22, 0))
    current_time = start_time

    while current_time < end_time:
        time_slots.append({
            'start_time': current_time,
            'display_time': current_time.strftime('%I:%M %p')
        })
        current_time += timedelta(minutes=slot_duration)

    # Get existing appointments for the selected date
    existing_appointments = Appointment.query.filter(
        func.date(Appointment.appointment_date) == selected_date,
        Appointment.status != 'cancelled'
    ).all()

    # Get enhanced staff schedules for the selected date using new shift schema
    staff_schedules = {}
    for staff in staff_members:
        schedule_info = get_staff_schedule_for_date(staff.id, selected_date)

        if schedule_info and schedule_info.get('is_working_day'):
            staff_schedules[staff.id] = {
                'has_shift': True,
                'is_absent': False,
                'shift_start': schedule_info['shift_start_time'],
                'shift_end': schedule_info['shift_end_time'],
                'break_start': schedule_info.get('break_start_time'),
                'break_end': schedule_info.get('break_end_time'),
                'schedule_name': schedule_info['schedule_name'],
                'break_time': schedule_info['break_time'],
                'description': schedule_info.get('notes', ''),
                'priority': 0
            }
        else:
            # No schedule found or not a working day
            staff_schedules[staff.id] = {
                'has_shift': False,
                'is_absent': True,
                'shift_start': None,
                'shift_end': None,
                'break_start': None,
                'break_end': None,
                'schedule_name': schedule_info.get('schedule_name', 'Not Scheduled') if schedule_info else 'Not Scheduled',
                'break_time': None,
                'description': schedule_info.get('notes', 'No shift scheduled or day off') if schedule_info else 'No shift scheduled or day off',
                'priority': 0
            }

    # Build enhanced staff availability grid
    staff_availability = {}

    for staff in staff_members:
        schedule = staff_schedules.get(staff.id, {})

        for time_slot in time_slots:
            slot_key = (staff.id, time_slot['start_time'])
            slot_time = time_slot['start_time'].time()

            # Check if staff is not scheduled or absent
            if not schedule.get('has_shift', False) or schedule.get('is_absent', False):
                if schedule.get('is_absent', False):
                    staff_availability[slot_key] = {
                        'status': 'absent',
                        'reason': f'Absent - {schedule.get("schedule_name", "Not Available")}',
                        'display_text': 'Absent',
                        'css_class': 'bg-dark text-white',
                        'schedule_info': schedule.get('description', '')
                    }
                else:
                    staff_availability[slot_key] = {
                        'status': 'not_available',
                        'reason': f'Not scheduled - {schedule.get("schedule_name", "No Shift")}',
                        'display_text': 'Not Available',
                        'css_class': 'bg-secondary text-white',
                        'schedule_info': schedule.get('description', '')
                    }
                continue

            # Check if time slot is outside shift hours
            shift_start = schedule.get('shift_start')
            shift_end = schedule.get('shift_end')

            if shift_start and shift_end:
                if slot_time < shift_start or slot_time >= shift_end:
                    shift_times = f"{shift_start.strftime('%I:%M %p')} - {shift_end.strftime('%I:%M %p')}"
                    staff_availability[slot_key] = {
                        'status': 'off_duty',
                        'reason': f'Off duty - Shift: {shift_times}',
                        'display_text': 'Off Duty',
                        'shift_times': shift_times,
                        'css_class': 'bg-light text-muted border',
                        'schedule_info': schedule.get('schedule_name', '')
                    }
                    continue

            # Check if this time slot is during break time (FIXED LOGIC)
            break_start = schedule.get('break_start')
            break_end = schedule.get('break_end')

            if break_start and break_end:
                if break_start <= slot_time < break_end:
                    break_start_12h = break_start.strftime('%I:%M %p')
                    break_end_12h = break_end.strftime('%I:%M %p')
                    staff_availability[slot_key] = {
                        'status': 'break',
                        'reason': f'Break time ({break_start_12h} - {break_end_12h})',
                        'display_text': 'Break Time',
                        'break_times': f'{break_start_12h} - {break_end_12h}',
                        'css_class': 'bg-warning text-dark',
                        'schedule_info': schedule.get('break_time', '')
                    }
                    continue

            # Check if this time slot conflicts with existing appointments
            is_blocked_by_appointment = False
            blocking_appointment = None

            for appointment in existing_appointments:
                if appointment.staff_id == staff.id and appointment.status != 'cancelled':
                    apt_start = appointment.appointment_date
                    service_duration = appointment.service.duration if appointment.service else 60
                    apt_end = apt_start + timedelta(minutes=service_duration)

                    # Check if current slot overlaps with this appointment
                    slot_start = time_slot['start_time']
                    slot_end = slot_start + timedelta(minutes=slot_duration) # Use flexible slot duration for checking overlap

                    if not (slot_end <= apt_start or slot_start >= apt_end):
                        is_blocked_by_appointment = True
                        blocking_appointment = appointment
                        break

            if is_blocked_by_appointment and blocking_appointment:
                # Show appointment details only on the first slot of the appointment
                apt_start_time = blocking_appointment.appointment_date.time()
                if slot_time == apt_start_time:
                    service_duration = blocking_appointment.service.duration if blocking_appointment.service else 60
                    end_time = blocking_appointment.appointment_date + timedelta(minutes=service_duration)
                    staff_availability[slot_key] = {
                        'status': 'booked',
                        'appointment': blocking_appointment,
                        'client_name': blocking_appointment.client.full_name if blocking_appointment.client else 'Unknown',
                        'service_name': blocking_appointment.service.name if blocking_appointment.service else 'Service',
                        'service_duration': service_duration,
                        'end_time': end_time.strftime('%I:%M %p'),
                        'display_text': f'{blocking_appointment.service.name if blocking_appointment.service else "Service"} ({service_duration}min)',
                        'css_class': 'bg-danger text-white appointment-block',
                        'schedule_info': f'{blocking_appointment.client.full_name if blocking_appointment.client else "Unknown"} - {blocking_appointment.service.name if blocking_appointment.service else "Service"}',
                        'appointment_duration': service_duration,
                        'can_book': False
                    }
                else:
                    # Continuation of the same appointment
                    staff_availability[slot_key] = {
                        'status': 'booked_continuation',
                        'display_text': '↑ Cont.',
                        'css_class': 'bg-danger text-white appointment-continuation',
                        'schedule_info': 'Appointment in progress',
                        'can_book': False
                    }
            else:
                # Available slot within shift hours and outside break time
                shift_start_12h = shift_start.strftime('%I:%M %p') if shift_start else 'N/A'
                shift_end_12h = shift_end.strftime('%I:%M %p') if shift_end else 'N/A'

                # Check if there's enough time for shortest service (15 minutes) before shift end
                remaining_shift_time = (datetime.combine(selected_date, shift_end) - time_slot['start_time']).total_seconds() / 60 if shift_end else 480

                staff_availability[slot_key] = {
                    'status': 'available',
                    'schedule_info': schedule_info['schedule_name'] if schedule_info else None,
                    'display_text': 'Available',
                    'shift_times': f'{shift_start_12h} - {shift_end_12h}',
                    'css_class': 'btn btn-success available-slot',
                    'remaining_time': int(remaining_shift_time),
                    'can_book': remaining_shift_time >= 15
                }

    # Calculate enhanced statistics
    today_appointments = [apt for apt in existing_appointments if apt.status in ['scheduled', 'confirmed', 'completed']]
    today_revenue = sum(apt.amount or 0 for apt in today_appointments if apt.amount)

    # Additional statistics for better insights
    total_staff_on_duty = len([s for s in staff_schedules.values() if s.get('has_shift', False)])
    total_available_slots = len([a for a in staff_availability.values() if a.get('status') == 'available'])
    total_booked_slots = len([a for a in staff_availability.values() if a.get('status') == 'booked'])

    return render_template('staff_availability.html',
                         staff_members=staff_members,
                         clients=clients,
                         services=services,
                         time_slots=time_slots,
                         staff_availability=staff_availability,
                         staff_schedules=staff_schedules,
                         selected_date=selected_date,
                         today_appointments=today_appointments,
                         today_revenue=today_revenue,
                         total_staff_on_duty=total_staff_on_duty,
                         total_available_slots=total_available_slots,
                         total_booked_slots=total_booked_slots)

@app.route('/api/appointment/<int:appointment_id>')
@login_required
def api_appointment_details(appointment_id):
    """API endpoint to get appointment details"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Get appointment with eager loading of relationships
        from sqlalchemy.orm import joinedload
        appointment = Appointment.query.options(
            joinedload(Appointment.client),
            joinedload(Appointment.service),
            joinedload(Appointment.assigned_staff)
        ).filter(Appointment.id == appointment_id).first()

        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        # Get client data
        client_data = {}
        if appointment.client:
            client_data = {
                'id': appointment.client.id,
                'name': appointment.client.full_name,
                'phone': appointment.client.phone or 'N/A',
                'email': appointment.client.email or 'N/A'
            }
        else:
            # Fallback to get client by ID if relationship not loaded
            client = Customer.query.get(appointment.client_id) if appointment.client_id else None
            if client:
                client_data = {
                    'id': client.id,
                    'name': client.full_name,
                    'phone': client.phone or 'N/A',
                    'email': client.email or 'N/A'
                }
            else:
                client_data = {'id': None, 'name': 'Unknown Client', 'phone': 'N/A', 'email': 'N/A'}

        # Get service data
        service_data = {}
        if appointment.service:
            service_data = {
                'id': appointment.service.id,
                'name': appointment.service.name,
                'duration': appointment.service.duration,
                'price': float(appointment.service.price)
            }
        else:
            # Fallback to get service by ID if relationship not loaded
            service = Service.query.get(appointment.service_id) if appointment.service_id else None
            if service:
                service_data = {
                    'id': service.id,
                    'name': service.name,
                    'duration': service.duration,
                    'price': float(service.price)
                }
            else:
                service_data = {'id': None, 'name': 'Unknown Service', 'duration': 0, 'price': 0.0}

        # Get staff data
        staff_data = {}
        if hasattr(appointment, 'assigned_staff') and appointment.assigned_staff:
            staff_data = {
                'id': appointment.assigned_staff.id,
                'name': appointment.assigned_staff.full_name
            }
        else:
            # Fallback to get staff by ID if relationship not loaded
            staff = User.query.get(appointment.staff_id) if appointment.staff_id else None
            if staff:
                staff_data = {
                    'id': staff.id,
                    'name': staff.full_name
                }
            else:
                staff_data = {'id': None, 'name': 'Unknown Staff'}

        return jsonify({
            'id': appointment.id,
            'client': client_data,
            'service': service_data,
            'staff': staff_data,
            'appointment_date': appointment.appointment_date.strftime('%Y-%m-%d %H:%M'),
            'status': appointment.status,
            'notes': appointment.notes or '',
            'amount': float(appointment.amount) if appointment.amount else 0
        })

    except Exception as e:
        print(f"Error fetching appointment details: {e}")
        return jsonify({'error': f'Error fetching appointment details: {str(e)}'}), 500

@app.route('/api/appointments')
@login_required
def api_all_appointments():
    """API endpoint to get all appointments with filters"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        from sqlalchemy import func

        # Get filter parameters
        date_filter = request.args.get('date')
        staff_id = request.args.get('staff_id', type=int)
        client_id = request.args.get('client_id', type=int)
        status = request.args.get('status')

        # Base query
        appointments_query = Appointment.query

        # Apply filters
        if date_filter:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments_query = appointments_query.filter(
                func.date(Appointment.appointment_date) == filter_date
            )

        if staff_id:
            appointments_query = appointments_query.filter(Appointment.staff_id == staff_id)

        if client_id:
            appointments_query = appointments_query.filter(Appointment.client_id == client_id)

        if status:
            appointments_query = appointments_query.filter(Appointment.status == status)

        appointments = appointments_query.order_by(Appointment.appointment_date).all()

        # Format response
        appointments_data = []
        for appointment in appointments:
            appointments_data.append({
                'id': appointment.id,
                'client': {
                    'id': appointment.client.id,
                    'name': appointment.client.full_name,
                    'phone': appointment.client.phone,
                    'email': appointment.client.email
                } if appointment.client else None,
                'service': {
                    'id': appointment.service.id,
                    'name': appointment.service.name,
                    'duration': appointment.service.duration,
                    'price': float(appointment.service.price)
                } if appointment.service else None,
                'staff': {
                    'id': appointment.assigned_staff.id,
                    'name': appointment.assigned_staff.full_name
                } if hasattr(appointment, 'assigned_staff') and appointment.assigned_staff else None,
                'appointment_date': appointment.appointment_date.strftime('%Y-%m-%d %H:%M'),
                'end_time': appointment.end_time.strftime('%Y-%m-%d %H:%M') if appointment.end_time else None,
                'status': appointment.status,
                'notes': appointment.notes,
                'amount': float(appointment.amount) if appointment.amount else 0,
                'payment_status': getattr(appointment, 'payment_status', 'pending'),
                'created_at': appointment.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        return jsonify({
            'appointments': appointments_data,
            'total': len(appointments_data),
            'filters': {
                'date': date_filter,
                'staff_id': staff_id,
                'client_id': client_id,
                'status': status
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

    # Generate flexible time slots for the day (9 AM to 6 PM with configurable intervals)
    slot_duration = int(request.args.get('slot_duration', 15))
    valid_durations = [5, 10, 15, 30, 45, 60]
    if slot_duration not in valid_durations:
        slot_duration = 15
    
    time_slots = []
    start_time = datetime.combine(selected_date, datetime.min.time().replace(hour=9))
    end_time = datetime.combine(selected_date, datetime.min.time().replace(hour=18))

    current_time = start_time
    while current_time < end_time:
        time_slots.append({
            'start_time': current_time,
            'end_time': current_time + timedelta(minutes=slot_duration),
            'duration': slot_duration
        })
        current_time += timedelta(minutes=slot_duration)

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
                    appointment.appointment_date.time() == time_slot['start_time'].time() and
                    appointment.status != 'cancelled'):
                    booked_appointment = appointment
                    break

            if booked_appointment:
                staff_availability[slot_key] = {
                    'status': 'booked',
                    'appointment': booked_appointment,
                    'client_name': booked_appointment.client.full_name if booked_appointment.client else 'Unknown',
                    'service_name': booked_appointment.service.name if booked_appointment.service else 'Service',
                    'time_range': f"{booked_appointment.appointment_date.strftime('%H:%M')} - {(booked_appointment.appointment_date + timedelta(minutes=booked_appointment.service.duration if booked_appointment.service else 60)).strftime('%H:%M')}"
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
                         services=services,
                         timedelta=timedelta)

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
            # Get form data from both form and JSON
            if request.is_json:
                data = request.get_json()
                client_id = data.get('client_id', type=int)
                service_id = data.get('service_id', type=int)
                staff_id = data.get('staff_id', type=int)
                appointment_date = data.get('appointment_date')
                appointment_time = data.get('appointment_time')
                notes = data.get('notes', '')
            else:
                client_id = request.form.get('client_id', type=int)
                service_id = request.form.get('service_id', type=int)
                staff_id = request.form.get('staff_id', type=int)
                appointment_date = request.form.get('appointment_date')
                appointment_time = request.form.get('appointment_time')
                notes = request.form.get('notes', '')

            print(f"Booking data: client_id={client_id}, service_id={service_id}, staff_id={staff_id}, date={appointment_date}, time={appointment_time}")

            # Defensive validation with specific error messages
            validation_errors = []

            if not client_id:
                validation_errors.append('Please select a client for the appointment.')
            if not service_id:
                validation_errors.append('Please select a service for the appointment.')
            if not staff_id:
                validation_errors.append('Please select a staff member for the appointment.')
            if not appointment_date:
                validation_errors.append('Please select an appointment date.')
            if not appointment_time:
                validation_errors.append('Please select an appointment time.')

            if validation_errors:
                error_msg = ' '.join(validation_errors)
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'danger')
                return redirect(request.url)

            # Parse date and time
            if isinstance(appointment_date, str):
                appointment_date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            else:
                appointment_date_obj = appointment_date

            if isinstance(appointment_time, str):
                appointment_time_obj = datetime.strptime(appointment_time, '%H:%M').time()
            else:
                appointment_time_obj = appointment_time

            appointment_datetime = datetime.combine(appointment_date_obj, appointment_time_obj)

            # Get service details for end time calculation
            service = Service.query.get(service_id)
            if not service:
                error_msg = 'Service not found'
                if request.is_json:
                    return jsonify({'error': error_msg}), 404
                flash(error_msg, 'danger')
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
                'amount': service.price,
                'payment_status': 'pending',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }

            print(f"Creating appointment with data: {appointment_data}")

            # Create the appointment
            appointment = create_appointment(appointment_data)

            if appointment:
                success_msg = 'Appointment booked successfully!'
                if request.is_json:
                    return jsonify({
                        'success': True, 
                        'message': success_msg,
                        'appointment_id': appointment.id
                    })
                flash(success_msg, 'success')
                return redirect(url_for('staff_availability', date=appointment_date_obj.strftime('%Y-%m-%d')))
            else:
                error_msg = 'Error booking appointment'
                if request.is_json:
                    return jsonify({'error': error_msg}), 500
                flash(error_msg, 'danger')

        except Exception as e:
            error_msg = f'Error booking appointment: {str(e)}'
            print(f"Booking error: {e}")
            import traceback
            traceback.print_exc()
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            flash(error_msg, 'danger')

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

@app.route('/appointments/cancel/<int:appointment_id>', methods=['POST', 'DELETE'])
@login_required
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    if not current_user.can_access('bookings'):
        if request.is_json:
            return jsonify({'error': 'Access denied'}), 403
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    appointment = get_appointment_by_id(appointment_id)
    if not appointment:
        if request.is_json:
            return jsonify({'error': 'Appointment not found'}), 404
        flash('Appointment not found', 'danger')
        return redirect(url_for('staff_availability'))

    try:
        # Get cancellation reason if provided
        cancellation_reason = ''
        if request.is_json:
            data = request.get_json()
            cancellation_reason = data.get('reason', '')
        else:
            cancellation_reason = request.form.get('reason', '')

        # Update status to cancelled
        appointment_data = {
            'status': 'cancelled',
            'notes': f"{appointment.notes}\n[Cancelled: {cancellation_reason}]" if cancellation_reason else appointment.notes,
            'updated_at': datetime.utcnow()
        }

        updated_appointment = update_appointment(appointment_id, appointment_data)

        if updated_appointment:
            success_msg = 'Appointment cancelled successfully!'
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': success_msg,
                    'appointment_id': appointment_id,
                    'status': 'cancelled'
                })
            flash(success_msg, 'success')
        else:
            error_msg = 'Error cancelling appointment'
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            flash(error_msg, 'danger')

    except Exception as e:
        error_msg = f'Error cancelling appointment: {str(e)}'
        print(f"Cancel error: {e}")
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'danger')

    # Get the date to redirect back to schedule
    appointment_date = appointment.appointment_date.strftime('%Y-%m-%d')

    if request.is_json:
        return jsonify({'redirect_url': url_for('staff_availability', date=appointment_date)})

    return redirect(url_for('staff_availability', date=appointment_date))

@app.route('/appointments/delete/<int:appointment_id>', methods=['POST', 'DELETE'])
@login_required
def delete_appointment_permanent(appointment_id):
    """Permanently delete an appointment"""
    if not current_user.can_access('bookings'):
        if request.is_json:
            return jsonify({'error': 'Access denied'}), 403
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    appointment = get_appointment_by_id(appointment_id)
    if not appointment:
        if request.is_json:
            return jsonify({'error': 'Appointment not found'}), 404
        flash('Appointment not found', 'danger')
        return redirect(url_for('staff_availability'))

    try:
        appointment_date = appointment.appointment_date.strftime('%Y-%m-%d')

        # Permanently delete the appointment
        if delete_appointment(appointment_id):
            success_msg = 'Appointment deleted permanently!'
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': success_msg,
                    'appointment_id': appointment_id
                })
            flash(success_msg, 'success')
        else:
            error_msg = 'Error deleting appointment'
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            flash(error_msg, 'danger')

    except Exception as e:
        error_msg = f'Error deleting appointment: {str(e)}'
        print(f"Delete error: {e}")
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'danger')

    if request.is_json:
        return jsonify({'redirect_url': url_for('staff_availability', date=appointment_date)})

    return redirect(url_for('staff_availability', date=appointment_date))

@app.route('/appointments/edit/<int:appointment_id>', methods=['GET', 'POST', 'PUT'])
@login_required
def edit_appointment(appointment_id):
    """Edit an existing appointment"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    appointment = get_appointment_by_id(appointment_id)
    if not appointment:
        if request.is_json:
            return jsonify({'error': 'Appointment not found'}), 404
        flash('Appointment not found', 'danger')
        return redirect(url_for('staff_availability'))

    if request.method in ['POST', 'PUT']:
        try:
            # Get form data from both form and JSON
            if request.is_json:
                data = request.get_json()
                client_id = data.get('client_id', type=int)
                service_id = data.get('service_id', type=int)
                staff_id = data.get('staff_id', type=int)
                appointment_date = data.get('appointment_date')
                appointment_time = data.get('appointment_time')
                notes = data.get('notes', '')
                status = data.get('status', appointment.status)
            else:
                client_id = request.form.get('client_id', type=int)
                service_id = request.form.get('service_id', type=int)
                staff_id = request.form.get('staff_id', type=int)
                appointment_date = request.form.get('appointment_date')
                appointment_time = request.form.get('appointment_time')
                notes = request.form.get('notes', '')
                status = request.form.get('status', appointment.status)

            print(f"Updating appointment {appointment_id}: client_id={client_id}, service_id={service_id}, staff_id={staff_id}")

            # Validate required fields
            if not all([client_id, service_id, staff_id]):
                error_msg = 'Client, Service, and Staff are required'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'danger')
                return redirect(request.url)

            # Parse date and time if provided
            if appointment_date and appointment_time:
                appointment_date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()
                appointment_time_obj = datetime.strptime(appointment_time, '%H:%M').time()
                appointment_datetime = datetime.combine(appointment_date_obj, appointment_time_obj)
            else:
                appointment_datetime = appointment.appointment_date

            # Get service details for end time calculation
            service = Service.query.get(service_id)
            if service:
                end_time = appointment_datetime + timedelta(minutes=service.duration)
                amount = service.price
            else:
                end_time = appointment.end_time
                amount = appointment.amount

            # Update appointment data
            appointment_data = {
                'client_id': client_id,
                'service_id': service_id,
                'staff_id': staff_id,
                'appointment_date': appointment_datetime,
                'end_time': end_time,
                'notes': notes,
                'status': status,
                'amount': amount,
                'updated_at': datetime.utcnow()
            }

            # Update the appointment
            updated_appointment = update_appointment(appointment_id, appointment_data)

            if updated_appointment:
                success_msg = 'Appointment updated successfully!'
                if request.is_json:
                    return jsonify({
                        'success': True,
                        'message': success_msg,
                        'appointment': {
                            'id': updated_appointment.id,
                            'status': updated_appointment.status,
                            'appointment_date': updated_appointment.appointment_date.strftime('%Y-%m-%d %H:%M')
                        }
                    })
                flash(success_msg, 'success')
                return redirect(url_for('staff_availability', date=appointment_datetime.date().strftime('%Y-%m-%d')))
            else:
                error_msg = 'Error updating appointment'
                if request.is_json:
                    return jsonify({'error': error_msg}), 500
                flash(error_msg, 'danger')

        except Exception as e:
            error_msg = f'Error updating appointment: {str(e)}'
            print(f"Update error: {e}")
            import traceback
            traceback.print_exc()
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            flash(error_msg, 'danger')

    # Get data for form
    clients = get_active_clients()
    services = get_active_services()
    staff_members = get_staff_members()

    return render_template('appointments_edit.html',
                         appointment=appointment,
                         clients=clients,
                         services=services,
                         staff_members=staff_members)


# Unaki Booking System API endpoints
@app.route('/api/unaki/schedule/<date_str>')
@login_required
def unaki_schedule_api(date_str):
    """API endpoint to get schedule data for Unaki booking system"""
    try:
        # Parse the date
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get staff members
        staff_members = get_staff_members()
        staff_data = []
        
        for staff in staff_members:
            schedule = get_staff_schedule_for_date(staff.id, target_date)
            staff_info = {
                'id': staff.id,
                'name': staff.full_name or staff.username,
                'specialty': getattr(staff, 'specialization', staff.role if hasattr(staff, 'role') else 'General'),
                'shift_start': schedule['shift_start_time'].strftime('%H:%M') if schedule and schedule['shift_start_time'] else '09:00',
                'shift_end': schedule['shift_end_time'].strftime('%H:%M') if schedule and schedule['shift_end_time'] else '17:00',
                'is_working': schedule['is_working_day'] if schedule else True
            }
            staff_data.append(staff_info)
        
        # Get appointments for the date
        appointments_data = []
        appointments = get_appointments_by_date(target_date)
        
        for appointment in appointments:
            appointment_info = {
                'id': appointment.id,
                'staffId': appointment.staff_id,
                'clientName': appointment.client.full_name if appointment.client else 'Unknown',
                'clientPhone': appointment.client.phone if appointment.client else '',
                'service': appointment.service.name if appointment.service else 'Service',
                'startTime': appointment.appointment_date.strftime('%H:%M'),
                'endTime': appointment.end_time.strftime('%H:%M') if appointment.end_time else None,
                'status': appointment.status,
                'notes': appointment.notes or ''
            }
            appointments_data.append(appointment_info)
        
        # Get breaks data (simplified for now)
        breaks_data = []
        for staff in staff_members:
            schedule = get_staff_schedule_for_date(staff.id, target_date)
            if schedule and schedule.get('break_start_time') and schedule.get('break_end_time'):
                break_info = {
                    'id': f"break_{staff.id}",
                    'staff_id': staff.id,
                    'start_time': schedule['break_start_time'].strftime('%H:%M'),
                    'end_time': schedule['break_end_time'].strftime('%H:%M'),
                    'type': 'break'
                }
                breaks_data.append(break_info)
        
        return jsonify({
            'success': True,
            'date': date_str,
            'staff': staff_data,
            'appointments': appointments_data,
            'breaks': breaks_data
        })
        
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid date format'}), 400
    except Exception as e:
        print(f"Error in unaki_schedule_api: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500


# Removed duplicate unaki_load_sample_data - using implementation from app.py


# Moved to routes.py - avoiding duplicate endpoint
def unaki_create_appointment_impl():
    """API endpoint to create appointments for Unaki booking system"""
    try:
        from app import db
        data = request.get_json()
        
        # Extract appointment data
        staff_id = data.get('staffId')
        client_name = data.get('clientName')
        client_phone = data.get('clientPhone', '')
        service_type = data.get('serviceType')
        start_time = data.get('startTime')
        end_time = data.get('endTime')
        notes = data.get('notes', '')
        appointment_date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Validate required fields
        if not all([staff_id, client_name, service_type, start_time, end_time]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: staff, client name, service, start time, and end time are required'
            }), 400
        
        # Parse date and times
        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
        start_datetime = datetime.combine(appointment_date, datetime.strptime(start_time, '%H:%M').time())
        end_datetime = datetime.combine(appointment_date, datetime.strptime(end_time, '%H:%M').time())
        
        # Find or create customer
        from models import Customer, Service, User, Appointment
        customer = Customer.query.filter_by(full_name=client_name).first()
        if not customer:
            customer = Customer(
                full_name=client_name,
                phone=client_phone,
                email=f"{client_name.lower().replace(' ', '.')}@customer.spa"  # Temporary email
            )
            db.session.add(customer)
            db.session.flush()  # Get the ID
        
        # Find service by name or create a generic one
        service = Service.query.filter_by(name=service_type).first()
        if not service:
            service = Service(
                name=service_type,
                duration=60,  # Default 60 minutes
                price=100.0,  # Default price
                is_active=True
            )
            db.session.add(service)
            db.session.flush()
        
        # Verify staff exists
        staff = User.query.get(staff_id)
        if not staff:
            return jsonify({
                'success': False,
                'error': 'Staff member not found'
            }), 400
        
        # Create the appointment
        appointment = Appointment(
            client_id=customer.id,
            service_id=service.id,
            staff_id=staff_id,
            appointment_date=start_datetime,
            end_time=end_datetime,
            status='confirmed',
            notes=notes,
            amount=service.price
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Appointment created successfully',
            'appointment': {
                'id': appointment.id,
                'staff_id': staff_id,
                'client_name': client_name,
                'client_phone': client_phone,
                'service_type': service_type,
                'start_time': start_time,
                'end_time': end_time,
                'date': appointment_date_str,
                'status': 'confirmed',
                'notes': notes,
                'created_at': appointment.created_at.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in unaki_create_appointment: {e}")
        return jsonify({'success': False, 'error': f'Failed to create appointment: {str(e)}'}), 500


@app.route('/api/schedule', methods=['GET'])
@login_required  
def get_schedule():
    """General schedule API endpoint with static data"""
    try:
        # Static hardcoded data structure for the frontend
        schedule_data = {
            "staff": [
                {
                    "id": 1,
                    "name": "Sarah Johnson",
                    "specialty": "Facial Specialist",
                    "shift_start": "09:00",
                    "shift_end": "17:00",
                    "is_working": True
                },
                {
                    "id": 2,
                    "name": "Michael Chen",
                    "specialty": "Massage Therapist", 
                    "shift_start": "10:00",
                    "shift_end": "18:00",
                    "is_working": True
                },
                {
                    "id": 3,
                    "name": "Emily Rodriguez",
                    "specialty": "Hair Stylist",
                    "shift_start": "08:00",
                    "shift_end": "16:00",
                    "is_working": True
                }
            ],
            "appointments": [
                {
                    "id": "apt_001",
                    "staff_id": 1,
                    "client_name": "Jessica Williams",
                    "service": "Deep Cleansing Facial",
                    "start_time": "10:00",
                    "end_time": "11:30",
                    "status": "confirmed",
                    "notes": "First time client"
                },
                {
                    "id": "apt_002", 
                    "staff_id": 2,
                    "client_name": "David Brown",
                    "service": "Relaxation Massage",
                    "start_time": "14:00",
                    "end_time": "15:00",
                    "status": "confirmed",
                    "notes": "Regular client"
                }
            ],
            "breaks": [
                {
                    "id": "break_1",
                    "staff_id": 1,
                    "start_time": "12:00",
                    "end_time": "13:00",
                    "type": "lunch"
                },
                {
                    "id": "break_2",
                    "staff_id": 2, 
                    "start_time": "12:30",
                    "end_time": "13:30",
                    "type": "lunch"
                }
            ]
        }
        
        return jsonify(schedule_data)
        
    except Exception as e:
        print(f"Error in get_schedule: {e}")
        return jsonify({'error': 'Server error'}), 500