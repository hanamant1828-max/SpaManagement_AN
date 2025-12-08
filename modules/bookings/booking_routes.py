"""
Booking View Routes

This module contains all view routes for the booking system.
These routes render HTML templates and handle page navigation.
Includes:
- Main bookings page
- Calendar booking views  
- Staff availability pages
- Multi-appointment booking
- Appointment scheduling and management
- Billing integration
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta, time
from sqlalchemy import func
from urllib.parse import quote

from app import app, db
from forms import AppointmentForm, QuickBookingForm
from models import (
    Appointment, Customer, Service, User, ShiftManagement,
    ShiftLogs, UnakiBooking
)
from .bookings_queries import (
    get_appointments_by_date, get_active_clients, get_active_services,
    get_staff_members, create_appointment, update_appointment,
    delete_appointment, get_appointment_by_id, get_time_slots,
    get_appointment_stats
)
from .booking_helpers import get_staff_schedule_for_date, generate_time_slots


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

    customers = get_active_clients()
    services = get_active_services()
    staff_members = get_staff_members()

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
                         customers=customers,
                         services=services,
                         staff_members=staff_members,
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
    customers = get_active_clients()
    services = get_active_services()
    staff_members = get_staff_members()

    form.customer_id.choices = [(0, 'Select Customer')] + [(c.id, c.full_name) for c in customers]
    form.service_id.choices = [(0, 'Select Service')] + [(s.id, s.name) for s in services]
    form.staff_id.choices = [(0, 'Select Staff (Optional)')] + [(u.id, f"{u.first_name} {u.last_name}") for u in staff_members]

    if form.validate_on_submit():
        appointment_data = {
            'client_id': form.customer_id.data,
            'service_id': form.service_id.data,
            'staff_id': form.staff_id.data,
            'appointment_date': form.appointment_date.data,
            'notes': form.notes.data or '',
            'status': 'scheduled',
            'booking_source': 'manual'
        }

        appointment, error = create_appointment(appointment_data)
        if appointment:
            flash('Appointment created successfully!', 'success')
        else:
            error_msg = error or 'Error creating appointment. Please check your input.'
            flash(error_msg, 'danger')
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
    customers = get_active_clients()
    services = get_active_services()
    staff_members = get_staff_members()

    form.customer_id.choices = [(0, 'Select Customer')] + [(c.id, c.full_name) for c in customers]
    form.service_id.choices = [(0, 'Select Service')] + [(s.id, s.name) for s in services]
    form.staff_id.choices = [(0, 'Select Staff (Optional)')] + [(u.id, f"{u.first_name} {u.last_name}") for u in staff_members]

    if form.validate_on_submit():
        appointment_data = {
            'client_id': form.customer_id.data,
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
                'is_absent': True,
                'has_shift': False,
                'schedule_id': None,
                'daily_schedule_id': None,
                'notes': schedule_info.get('notes', 'No shift scheduled or day off')
            }

    # Get slot duration from request parameter or default to 15 minutes
    slot_duration = int(request.args.get('slot_duration', 15))
    valid_durations = [5, 10, 15, 30, 45, 60]
    if slot_duration not in valid_durations:
        slot_duration = 15

    time_slots = generate_time_slots(start_hour=8, end_hour=20, slot_duration=slot_duration, selected_date=selected_date)

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
                    slot_end = slot_start + timedelta(minutes=slot_duration)

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
                        'appointment_id': blocking_appointment.id,
                        'client_name': blocking_appointment.client.full_name if blocking_appointment.client else 'Unknown',
                        'service_name': blocking_appointment.service.name if blocking_appointment.service else 'Service',
                        'service_duration': service_duration,
                        'end_time': end_time.strftime('%I:%M %p'),
                        'display_text': f'{blocking_appointment.service.name if blocking_appointment.service else "Service"} ({service_duration}min)',
                        'css_class': 'bg-danger text-white appointment-block',
                        'schedule_info': f'{blocking_appointment.client.full_name if blocking_appointment.client else "Unknown"} - {blocking_appointment.service.name if blocking_appointment.service else "Service"}',
                        'appointment_duration': service_duration,
                        'booking_source': blocking_appointment.booking_source if hasattr(blocking_appointment, 'booking_source') else None,
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
    today_revenue = sum(apt.amount or 0 for apt in today_appointments if apt.amount and getattr(apt, 'payment_status', 'pending') == 'paid')

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
                    slot_end = slot_start + timedelta(minutes=slot_duration)

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
                        'appointment_id': blocking_appointment.id,
                        'client_name': blocking_appointment.client.full_name if blocking_appointment.client else 'Unknown',
                        'service_name': blocking_appointment.service.name if blocking_appointment.service else 'Service',
                        'service_duration': service_duration,
                        'end_time': end_time.strftime('%I:%M %p'),
                        'display_text': f'{blocking_appointment.service.name if blocking_appointment.service else "Service"} ({service_duration}min)',
                        'css_class': 'bg-danger text-white appointment-block',
                        'schedule_info': f'{blocking_appointment.client.full_name if blocking_appointment.client else "Unknown"} - {blocking_appointment.service.name if blocking_appointment.service else "Service"}',
                        'appointment_duration': service_duration,
                        'booking_source': blocking_appointment.booking_source if hasattr(blocking_appointment, 'booking_source') else None,
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


@app.route('/multi-appointment-booking')
@login_required
def multi_appointment_booking():
    """Dedicated page for booking multiple appointments - supports both new bookings and editing existing ones"""
    if not current_user.can_access('bookings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        from modules.staff.staff_queries import get_staff_members
        from modules.services.services_queries import get_all_services
        from modules.clients.clients_queries import get_all_customers

        staff_members = get_staff_members()
        services = get_all_services()
        clients = get_all_customers()
        today = date.today().strftime('%Y-%m-%d')
        
        # Check if we're editing an existing appointment
        edit_id = request.args.get('edit_id')
        edit_appointments = []  # Array of all unpaid/scheduled appointments for the client
        edit_client_id = None
        
        if edit_id:
            try:
                # Get the appointment to find the client
                clicked_booking = UnakiBooking.query.get(int(edit_id))
                if clicked_booking and clicked_booking.client_id:
                    edit_client_id = clicked_booking.client_id
                    
                    # Fetch ALL unpaid and scheduled appointments for this client
                    all_client_appointments = UnakiBooking.query.filter(
                        UnakiBooking.client_id == edit_client_id,
                        UnakiBooking.status.in_(['scheduled', 'confirmed', 'checked_in']),
                        UnakiBooking.payment_status.in_(['unpaid', 'pending', None])
                    ).order_by(UnakiBooking.appointment_date, UnakiBooking.start_time).all()
                    
                    print(f"📝 Found {len(all_client_appointments)} unpaid/scheduled appointments for client {edit_client_id}")
                    
                    for booking in all_client_appointments:
                        appt_data = {
                            'id': booking.id,
                            'client_id': booking.client_id,
                            'client_name': f"{booking.client.first_name} {booking.client.last_name}" if booking.client else '',
                            'service_id': booking.service_id,
                            'service_name': booking.service.name if booking.service else '',
                            'staff_id': booking.staff_id,
                            'staff_name': f"{booking.staff.first_name} {booking.staff.last_name}" if booking.staff else '',
                            'appointment_date': booking.appointment_date.strftime('%Y-%m-%d') if booking.appointment_date else today,
                            'start_time': booking.start_time.strftime('%H:%M') if booking.start_time else '',
                            'end_time': booking.end_time.strftime('%H:%M') if booking.end_time else '',
                            'notes': booking.notes or '',
                            'status': booking.status or 'scheduled',
                            'booking_source': booking.booking_source or 'walk_in',
                            'is_clicked': booking.id == int(edit_id)  # Mark the one that was clicked
                        }
                        edit_appointments.append(appt_data)
                        print(f"  - Appointment {booking.id}: {booking.service.name if booking.service else 'N/A'} on {booking.appointment_date}")
                    
            except Exception as e:
                print(f"Error loading appointments for editing: {e}")
                import traceback
                traceback.print_exc()
                flash('Could not load appointments for editing', 'warning')

        return render_template('multi_appointment_booking.html',
                             staff_members=staff_members,
                             services=services,
                             clients=clients,
                             today=today,
                             edit_appointments=edit_appointments,
                             edit_client_id=edit_client_id)
    except Exception as e:
        print(f"Error in multi_appointment_booking: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading booking page', 'danger')
        return redirect(url_for('unaki_booking'))


@app.route('/appointments/schedule')
@login_required
def appointments_schedule():
    """Timeline view for appointment scheduling with horizontal calendar layout"""
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

    # Generate flexible time slots for the day (9 AM to 10 PM for timeline view)
    slot_duration = int(request.args.get('slot_duration', 15))
    valid_durations = [5, 10, 15, 30, 45, 60]
    if slot_duration not in valid_durations:
        slot_duration = 15

    time_slots = []
    start_time = datetime.combine(selected_date, datetime.min.time().replace(hour=9))
    end_time = datetime.combine(selected_date, datetime.min.time().replace(hour=22))

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

    # Also get UnakiBooking appointments for the same date
    unaki_bookings = UnakiBooking.query.filter_by(appointment_date=selected_date).all()

    # Calculate appointment positioning for timeline view
    # Timeline starts at 9 AM, each hour is 80px wide
    timeline_start_hour = 9
    px_per_hour = 80

    appointments_with_position = []
    for appointment in existing_appointments:
        if appointment.status == 'cancelled':
            continue

        # Calculate position from left (based on time from 9 AM)
        apt_time = appointment.appointment_date
        hour_decimal = apt_time.hour + apt_time.minute / 60.0
        hours_from_start = hour_decimal - timeline_start_hour
        position_left = hours_from_start * px_per_hour

        # Calculate width based on service duration
        service_duration = appointment.service.duration if appointment.service else 60
        width = (service_duration / 60.0) * px_per_hour

        # Determine service type for color coding
        service_type = 'default'
        if appointment.service:
            service_name_lower = appointment.service.name.lower()
            if 'massage' in service_name_lower:
                service_type = 'massage'
            elif 'facial' in service_name_lower:
                service_type = 'facial'
            elif 'manicure' in service_name_lower:
                service_type = 'manicure'
            elif 'pedicure' in service_name_lower:
                service_type = 'pedicure'
            elif 'hair' in service_name_lower or 'cut' in service_name_lower:
                service_type = 'haircut'
            elif 'wax' in service_name_lower:
                service_type = 'waxing'

        appointments_with_position.append({
            'id': appointment.id,
            'staff_id': appointment.staff_id,
            'client_name': appointment.client.full_name if appointment.client else 'Unknown',
            'service_name': appointment.service.name if appointment.service else 'Service',
            'service_type': service_type,
            'start_time': appointment.appointment_date,
            'duration': service_duration,
            'position_left': position_left,
            'width': max(width, 40)  # Minimum width of 40px for visibility
        })

    # Create staff availability grid for the old format (kept for compatibility)
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
                    'client_name': booked_appointment.client.full_name if booked_appointment.client else 'Unknown',
                    'service_name': booked_appointment.service.name if booked_appointment.service else 'Unknown Service',
                    'service_duration': booked_appointment.service.duration if booked_appointment.service else 60,
                    'reason': f'Booked: {booked_appointment.client.full_name if booked_appointment.client else "Unknown"}'
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
                         appointments=appointments_with_position,
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

            if not client_id or client_id == 0:
                validation_errors.append('Please select a client')
            if not service_id or service_id == 0:
                validation_errors.append('Please select a service')
            if not staff_id or staff_id == 0:
                validation_errors.append('Please select a staff member')
            if not appointment_date:
                validation_errors.append('Please select an appointment date')
            if not appointment_time:
                validation_errors.append('Please select an appointment time')

            if validation_errors:
                error_msg = '. '.join(validation_errors)
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'error': error_msg
                    }), 400
                flash(error_msg, 'danger')
                return redirect(request.referrer or url_for('appointments_schedule'))

            # Parse datetime
            appointment_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", '%Y-%m-%d %H:%M')

            # Get service for duration
            service = Service.query.get(service_id)
            if not service:
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'error': 'Service not found'
                    }), 404
                flash('Service not found', 'danger')
                return redirect(request.referrer or url_for('appointments_schedule'))

            # Create appointment
            appointment_data = {
                'client_id': client_id,
                'service_id': service_id,
                'staff_id': staff_id,
                'appointment_date': appointment_datetime,
                'end_time': appointment_datetime + timedelta(minutes=service.duration),
                'notes': notes,
                'status': 'scheduled',
                'amount': service.price,
                'payment_status': 'pending',
                'booking_source': 'unaki_system'
            }

            appointment, error = create_appointment(appointment_data)

            if appointment:
                success_msg = f'Appointment booked successfully for {appointment_datetime.strftime("%I:%M %p")} on {appointment_date}'
                if request.is_json:
                    return jsonify({
                        'success': True,
                        'message': success_msg,
                        'appointment_id': appointment.id
                    })
                flash(success_msg, 'success')
                return redirect(url_for('appointments_schedule', date=appointment_date))
            else:
                error_msg = error or 'Failed to create appointment'
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'error': error_msg
                    }), 400
                flash(error_msg, 'danger')
                return redirect(request.referrer or url_for('appointments_schedule'))

        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = f'Error creating appointment: {str(e)}'
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 500
            flash(error_msg, 'danger')
            return redirect(request.referrer or url_for('appointments_schedule'))

    # GET request - show form
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


@app.route('/appointment/<int:appointment_id>/go-to-billing')
@login_required
def appointment_go_to_billing(appointment_id):
    """Redirect to billing page with appointment pre-filled"""
    try:
        from models import UnakiBooking, Customer
        from urllib.parse import quote

        print(f"🧾 Accessing go-to-billing route for appointment {appointment_id}")

        # Get the appointment
        appointment = UnakiBooking.query.get(appointment_id)

        if not appointment:
            print(f"❌ Appointment {appointment_id} not found in UnakiBooking table")
            flash('Appointment not found', 'error')
            return redirect(url_for('unaki_booking'))

        print(f"✅ Found appointment {appointment_id}")
        print(f"   Client: {appointment.client_name} (ID: {appointment.client_id})")
        print(f"   Phone: {appointment.client_phone}")
        print(f"   Service: {appointment.service_name}")

        # Try to get customer by client_id first
        customer = None
        if appointment.client_id:
            customer = Customer.query.get(appointment.client_id)
            print(f"   ✅ Found customer by ID: {customer.full_name if customer else 'None'}")

        # If no customer found by ID, try to find by phone
        if not customer and appointment.client_phone:
            customer = Customer.query.filter_by(phone=appointment.client_phone).first()
            print(f"   📞 Found customer by phone: {customer.full_name if customer else 'None'}")

        # If still no customer, try to find by name (case-insensitive)
        if not customer and appointment.client_name:
            customer = Customer.query.filter(
                Customer.first_name.ilike(f'%{appointment.client_name.split()[0]}%')
            ).first()
            print(f"   👤 Found customer by name: {customer.full_name if customer else 'None'}")

        # Build redirect URL with query parameters
        if customer:
            # Redirect with customer pre-selected and appointment
            redirect_url = url_for('integrated_billing', customer_id=customer.id, appointment_id=appointment_id)
            print(f"   ➡️  Redirecting to: {redirect_url}")
            return redirect(redirect_url)
        else:
            # Redirect with appointment details but no customer pre-selected
            client_name_encoded = appointment.client_name or ''
            client_phone_encoded = appointment.client_phone or ''

            flash(f'Customer "{appointment.client_name}" not found. Please select customer from dropdown.', 'warning')

            redirect_url = url_for('integrated_billing', 
                                  appointment_id=appointment_id,
                                  client_name=client_name_encoded,
                                  client_phone=client_phone_encoded)
            print(f"   ⚠️  Customer not found, redirecting to: {redirect_url}")
            return redirect(redirect_url)

    except Exception as e:
        print(f"❌ Error in appointment_go_to_billing: {e}")
        import traceback
        traceback.print_exc()
        flash('Error accessing billing information. Please try again.', 'error')
        return redirect(url_for('unaki_booking'))