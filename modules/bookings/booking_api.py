"""
Booking API Endpoints

This module contains all API endpoints for the booking system.
All routes start with /api and return JSON responses.
Includes endpoints for:
- Time slot management
- Appointment operations (create, update, check conflicts)
- Client operations (quick add, get appointments)
- Unaki system integration
- Check-in operations
"""

from flask import request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta, time
import pytz
from sqlalchemy import func

from app import app, db
from models import (
    Appointment, Customer, Service, User, ShiftManagement,
    ShiftLogs, UnakiBooking
)
from .bookings_queries import get_time_slots, get_active_services, create_appointment
from .booking_services import (
    validate_against_shift, check_staff_conflicts, check_client_conflicts
)


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


@app.route('/api/appointment/<int:appointment_id>/customer-id')
@login_required
def api_get_appointment_customer_id(appointment_id):
    """API endpoint to get customer ID from appointment ID - works with both Appointment and UnakiBooking tables"""
    try:
        # First try to find in UnakiBooking table (primary system)
        try:
            unaki_appointment = UnakiBooking.query.get(appointment_id)
            if unaki_appointment:
                return jsonify({
                    'success': True,
                    'appointment_id': appointment_id,
                    'customer_id': unaki_appointment.client_id,
                    'customer_name': unaki_appointment.client_name,
                    'customer_phone': unaki_appointment.client_phone
                })
        except ImportError:
            pass

        # Fallback to regular Appointment table
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({
                'success': False,
                'error': 'Appointment not found'
            }), 404

        return jsonify({
            'success': True,
            'appointment_id': appointment_id,
            'customer_id': appointment.client_id,
            'customer_name': appointment.client.full_name if appointment.client else None,
            'customer_phone': appointment.client.phone if appointment.client else None
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/unaki/book-appointment', methods=['POST'])
@login_required
def api_unaki_book_appointment():
    """API endpoint to book a single appointment in Unaki system"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied', 'success': False}), 403

    try:
        data = request.get_json()
        print(f"📝 Booking request data: {data}")

        # Validate required fields with flexible field names
        client_id = data.get('client_id') or data.get('clientId')
        client_name = data.get('client_name') or data.get('clientName')
        staff_id = data.get('staff_id') or data.get('staffId')
        service_name = data.get('service_name') or data.get('serviceName') or data.get('serviceType')
        appointment_date_str = data.get('appointment_date') or data.get('date')
        start_time_str = data.get('start_time') or data.get('startTime')
        end_time_str = data.get('end_time') or data.get('endTime')

        # Check for missing required fields
        missing_fields = []
        if not client_name:
            missing_fields.append('client_name')
        if not staff_id:
            missing_fields.append('staff_id')
        if not service_name:
            missing_fields.append('service_name')
        if not appointment_date_str:
            missing_fields.append('appointment_date')
        if not start_time_str:
            missing_fields.append('start_time')
        if not end_time_str:
            missing_fields.append('end_time')

        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}',
                'success': False,
                'received_data': data
            }), 400

        # Parse date and times
        try:
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError as ve:
            return jsonify({
                'error': f'Invalid date/time format: {str(ve)}',
                'success': False
            }), 400

        # Create datetime objects for overlap checking
        start_datetime = datetime.combine(appointment_date, start_time)
        end_datetime = datetime.combine(appointment_date, end_time)

        # Validate staff exists
        staff = User.query.get(staff_id)
        if not staff:
            return jsonify({
                'error': f'Staff member with ID {staff_id} not found',
                'success': False
            }), 400

        # Check for overlapping appointments in UnakiBooking table
        existing_bookings = UnakiBooking.query.filter_by(
            staff_id=staff_id,
            appointment_date=appointment_date
        ).filter(UnakiBooking.status.in_(['scheduled', 'confirmed'])).all()

        print(f"🔍 Checking conflicts for staff {staff_id} on {appointment_date}")
        print(f"📅 New appointment: {start_time_str} - {end_time_str}")
        print(f"📋 Existing bookings: {len(existing_bookings)}")

        for booking in existing_bookings:
            existing_start = datetime.combine(appointment_date, booking.start_time)
            existing_end = datetime.combine(appointment_date, booking.end_time)

            print(f"   Existing: {booking.start_time} - {booking.end_time} ({booking.client_name})")

            # Check for overlap: appointments overlap if start < other_end AND end > other_start
            if start_datetime < existing_end and end_datetime > existing_start:
                conflict_msg = f'Time conflict! Staff member already has an appointment with {booking.client_name} from {booking.start_time.strftime("%I:%M %p")} to {booking.end_time.strftime("%I:%M %p")}'
                print(f"❌ Conflict detected: {conflict_msg}")
                return jsonify({
                    'error': conflict_msg,
                    'success': False
                }), 400

        # Check for client conflicts - prevent same client from having multiple appointments at the same time
        client_bookings = UnakiBooking.query.filter_by(
            client_name=client_name,
            appointment_date=appointment_date
        ).filter(UnakiBooking.status.in_(['scheduled', 'confirmed'])).all()

        print(f"🔍 Checking client conflicts for {client_name} on {appointment_date}")
        print(f"📋 Existing client bookings: {len(client_bookings)}")

        for booking in client_bookings:
            existing_start = datetime.combine(appointment_date, booking.start_time)
            existing_end = datetime.combine(appointment_date, booking.end_time)

            print(f"   Client's existing: {booking.start_time} - {booking.end_time} (Staff: {booking.staff_name})")

            # Check for overlap
            if start_datetime < existing_end and end_datetime > existing_start:
                conflict_msg = f'Client conflict! {client_name} already has an appointment from {booking.start_time.strftime("%I:%M %p")} to {booking.end_time.strftime("%I:%M %p")} with {booking.staff_name}'
                print(f"❌ Client conflict detected: {conflict_msg}")
                return jsonify({
                    'error': conflict_msg,
                    'success': False
                }), 400

        # Get staff name if not provided
        staff_name = data.get('staff_name') or data.get('staffName') or staff.full_name

        # Calculate service duration if not provided
        service_duration = data.get('service_duration') or data.get('serviceDuration')
        if not service_duration:
            duration_minutes = int((end_datetime - start_datetime).total_seconds() / 60)
            service_duration = duration_minutes
        else:
            service_duration = int(service_duration)

        # Handle customer creation if needed
        customer = None
        client_phone = data.get('client_phone', '').strip() or data.get('clientPhone', '').strip()
        client_email = data.get('client_email', '').strip() or data.get('clientEmail', '').strip()

        # Try to find existing customer
        if client_id:
            try:
                customer = Customer.query.get(int(client_id))
            except (ValueError, TypeError):
                pass

        if not customer and client_phone:
            customer = Customer.query.filter_by(phone=client_phone).first()

        if not customer and client_email:
            customer = Customer.query.filter_by(email=client_email).first()

        # Create customer if needed and contact info provided
        if not customer and (client_phone or client_email):
            try:
                name_parts = str(client_name).strip().split(' ', 1)
                first_name = name_parts[0] if name_parts else 'Unknown'
                last_name = name_parts[1] if len(name_parts) > 1 else ''

                customer = Customer(
                    first_name=first_name,
                    last_name=last_name,
                    phone=client_phone if client_phone else None,
                    email=client_email if client_email else None,
                    is_active=True
                )
                db.session.add(customer)
                db.session.flush()
                print(f"✅ Created new customer: {customer.full_name} (ID: {customer.id})")
            except Exception as ce:
                print(f"⚠️ Warning: Could not create customer record: {ce}")

        appointment = UnakiBooking(
            client_id=customer.id if customer else None,
            client_name=client_name,
            client_phone=client_phone or None,
            client_email=client_email or None,
            staff_id=int(staff_id),
            staff_name=staff_name,
            service_name=service_name,
            service_duration=service_duration,
            service_price=float(data.get('service_price', 0)) or float(data.get('servicePrice', 0)),
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_time,
            status='scheduled',
            notes=data.get('notes', ''),
            booking_source=data.get('booking_source', 'online'),
            booking_method='multi_service',
            amount_charged=float(data.get('amount_charged', data.get('service_price', 0))),
            payment_status='pending'
        )

        db.session.add(appointment)
        db.session.commit()

        print(f"✅ Appointment booked successfully: ID {appointment.id}")

        return jsonify({
            'success': True,
            'message': f'Appointment booked successfully for {client_name}',
            'appointment_id': appointment.id,
            'service': service_name,
            'time': f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
        })

    except Exception as e:
        print(f"❌ Error booking Unaki appointment: {e}")
        import traceback
        traceback.print_exc()
        if 'db' in locals():
            db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/unaki/check-staff-conflicts', methods=['POST'])
@login_required
def api_check_staff_conflicts():
    """API endpoint to check for staff appointment conflicts including shift, break, and OOO validation"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied', 'success': False}), 403

    try:
        data = request.get_json()

        staff_id = data.get('staff_id')
        appointment_date_str = data.get('appointment_date')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')

        if not all([staff_id, appointment_date_str, start_time_str, end_time_str]):
            return jsonify({
                'success': True,
                'has_conflict': False,
                'message': 'Missing required fields'
            })

        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()

        start_datetime = datetime.combine(appointment_date, start_time)
        end_datetime = datetime.combine(appointment_date, end_time)

        if end_datetime <= start_datetime:
            return jsonify({
                'success': True,
                'has_conflict': True,
                'shift_violation': True,
                'message': 'End time must be after start time'
            })

        staff = User.query.get(staff_id)
        if not staff:
            return jsonify({
                'success': False,
                'has_conflict': True,
                'message': 'Staff member not found'
            }), 404

        # 1. CHECK SHIFT SCHEDULE
        shift_management = ShiftManagement.query.filter(
            ShiftManagement.staff_id == staff_id,
            ShiftManagement.from_date <= appointment_date,
            ShiftManagement.to_date >= appointment_date
        ).first()

        # Block booking if no shift management found
        if not shift_management:
            return jsonify({
                'success': True,
                'has_conflict': True,
                'shift_violation': True,
                'message': f"{staff.first_name} {staff.last_name} has no schedule configured for {appointment_date.strftime('%B %d, %Y')}. Please contact admin to set up staff schedules."
            })

        # Get shift log for the specific date
        shift_log = ShiftLogs.query.filter(
            ShiftLogs.shift_management_id == shift_management.id,
            ShiftLogs.individual_date == appointment_date
        ).first()

        # Block booking if no shift log found for this specific date
        if not shift_log:
            return jsonify({
                'success': True,
                'has_conflict': True,
                'shift_violation': True,
                'message': f"{staff.first_name} {staff.last_name} has no shift scheduled for {appointment_date.strftime('%B %d, %Y')}. Please contact admin to configure daily schedules."
            })

        # Now we have a valid shift_log, proceed with validations
        if shift_log:
                # Check if staff is working (not absent/holiday)
                if shift_log.status not in ['scheduled', 'completed']:
                    return jsonify({
                        'success': True,
                        'has_conflict': True,
                        'shift_violation': True,
                        'message': f"{staff.first_name} {staff.last_name} is {shift_log.status} on {appointment_date.strftime('%B %d, %Y')}"
                    })

                # Check shift hours
                shift_start = shift_log.shift_start_time
                shift_end = shift_log.shift_end_time

                if start_time < shift_start or end_time > shift_end:
                    return jsonify({
                        'success': True,
                        'has_conflict': True,
                        'shift_violation': True,
                        'message': f"{staff.first_name} {staff.last_name} works {shift_start.strftime('%I:%M %p')} - {shift_end.strftime('%I:%M %p')}. Appointment time is outside shift hours."
                    })

                # Check break time
                if shift_log.break_start_time and shift_log.break_end_time:
                    break_start_dt = datetime.combine(appointment_date, shift_log.break_start_time)
                    break_end_dt = datetime.combine(appointment_date, shift_log.break_end_time)

                    # Check if appointment overlaps with break
                    if not (end_datetime <= break_start_dt or start_datetime >= break_end_dt):
                        return jsonify({
                            'success': True,
                            'has_conflict': True,
                            'shift_violation': True,
                            'message': f"{staff.first_name} {staff.last_name} has break from {shift_log.break_start_time.strftime('%I:%M %p')} to {shift_log.break_end_time.strftime('%I:%M %p')}"
                        })

                # Check out of office periods
                if shift_log.out_of_office_start and shift_log.out_of_office_end:
                    ooo_start_dt = datetime.combine(appointment_date, shift_log.out_of_office_start)
                    ooo_end_dt = datetime.combine(appointment_date, shift_log.out_of_office_end)

                    # Check if appointment overlaps with OOO
                    if not (end_datetime <= ooo_start_dt or start_datetime >= ooo_end_dt):
                        reason = shift_log.out_of_office_reason or "Out of office"
                        return jsonify({
                            'success': True,
                            'has_conflict': True,
                            'shift_violation': True,
                            'message': f"{staff.first_name} {staff.last_name} is out of office from {shift_log.out_of_office_start.strftime('%I:%M %p')} to {shift_log.out_of_office_end.strftime('%I:%M %p')} ({reason})"
                        })

        # 2. CHECK APPOINTMENT CONFLICTS
        conflicting_bookings = UnakiBooking.query.filter(
            UnakiBooking.staff_id == staff_id,
            UnakiBooking.appointment_date == appointment_date,
            UnakiBooking.status.in_(['scheduled', 'confirmed', 'in_progress'])
        ).all()

        for booking in conflicting_bookings:
            existing_start = datetime.combine(appointment_date, booking.start_time)
            existing_end = datetime.combine(appointment_date, booking.end_time)

            if start_datetime < existing_end and end_datetime > existing_start:
                return jsonify({
                    'success': True,
                    'has_conflict': True,
                    'shift_violation': False,
                    'message': f"{staff.first_name} {staff.last_name} has appointment from {booking.start_time.strftime('%I:%M %p')} to {booking.end_time.strftime('%I:%M %p')} with {booking.client_name}"
                })

        # All checks passed
        return jsonify({
            'success': True,
            'has_conflict': False,
            'shift_violation': False,
            'message': 'No conflicts found'
        })

    except Exception as e:
        print(f"❌ Error checking staff conflicts: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'has_conflict': False,
            'error': str(e)
        }), 500


@app.route('/api/unaki/quick-add-client', methods=['POST'])
@login_required
def api_quick_add_client():
    """Quick add new client from booking page"""
    if not current_user.can_access('bookings'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    try:
        data = request.get_json()

        # Validate required fields
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone = data.get('phone', '').strip()
        gender = data.get('gender', '').strip()

        if not all([first_name, last_name, phone, gender]):
            return jsonify({
                'success': False,
                'error': 'First name, last name, phone, and gender are required'
            }), 400

        # Check if client with same phone already exists
        existing = Customer.query.filter_by(phone=phone).first()
        if existing:
            return jsonify({
                'success': False,
                'error': f'Client with phone {phone} already exists'
            }), 400

        # Create new client
        new_client = Customer(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=data.get('email', '').strip() or None,
            gender=gender,
            is_active=True
        )

        db.session.add(new_client)
        db.session.commit()

        return jsonify({
            'success': True,
            'client_id': new_client.id,
            'client_name': f"{first_name} {last_name}",
            'message': 'Client added successfully'
        })

    except Exception as e:
        print(f"❌ Error in quick-add-client: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/unaki/check-client-conflicts', methods=['POST'])
@login_required
def api_check_client_conflicts():
    """API endpoint to check for client appointment conflicts in real-time"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied', 'success': False}), 403

    try:
        data = request.get_json()

        # Get parameters
        client_id = data.get('client_id')
        client_name = data.get('client_name', '')
        client_phone = data.get('client_phone', '')
        appointment_date_str = data.get('appointment_date')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')

        # Validate required fields
        if not all([appointment_date_str, start_time_str, end_time_str]):
            return jsonify({
                'success': True,
                'has_conflict': False,
                'message': 'Missing required fields'
            })

        # Parse date and times
        try:
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
            return jsonify({
                'success': True,
                'has_conflict': False,
                'message': 'Invalid date/time format'
            })

        # Get client name and phone if not provided but client_id is
        if client_id and not (client_name and client_phone):
            client = Customer.query.get(client_id)
            if client:
                client_name = f"{client.first_name} {client.last_name}".strip()
                client_phone = client.phone

        # Use the business logic function from booking_services
        result = check_client_conflicts(
            client_id=client_id,
            client_name=client_name,
            client_phone=client_phone,
            appointment_date=appointment_date,
            start_time_str=start_time_str,
            end_time_str=end_time_str
        )
        return jsonify(result)

    except Exception as e:
        print(f"❌ Error checking client conflicts: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'has_conflict': False,
            'error': str(e)
        }), 500


@app.route('/api/unaki/get-booking/<int:booking_id>')
@login_required
def api_get_unaki_booking(booking_id):
    """API endpoint to get a specific Unaki booking by ID"""
    try:
        booking = UnakiBooking.query.get(booking_id)
        if not booking:
            return jsonify({
                'success': False,
                'error': 'Booking not found'
            }), 404

        return jsonify({
            'success': True,
            'booking': booking.to_dict()
        })

    except Exception as e:
        print(f"Error fetching Unaki booking {booking_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/unaki/customer-appointments/<int:customer_id>')
@login_required
def api_get_customer_appointments_unaki(customer_id):
    """API endpoint to get all appointments for a specific customer"""
    try:
        # Try to get customer
        customer = Customer.query.get(customer_id)

        if customer:
            # Get appointments by client_id
            appointments = UnakiBooking.query.filter_by(client_id=customer_id).all()

            # Also try to match by name and phone if client_id doesn't return results
            if not appointments:
                full_name = f"{customer.first_name} {customer.last_name}".strip()
                appointments = UnakiBooking.query.filter(
                    db.or_(
                        UnakiBooking.client_name.ilike(f'%{full_name}%'),
                        UnakiBooking.client_phone == customer.phone
                    )
                ).all()
        else:
            # If customer not found, try to get appointments for this booking's customer
            booking = UnakiBooking.query.get(customer_id)
            if booking:
                appointments = UnakiBooking.query.filter(
                    db.or_(
                        UnakiBooking.client_id == booking.client_id,
                        UnakiBooking.client_name == booking.client_name,
                        UnakiBooking.client_phone == booking.client_phone
                    )
                ).all()
            else:
                appointments = []

        return jsonify({
            'success': True,
            'bookings': [apt.to_dict() for apt in appointments]
        })

    except Exception as e:
        print(f"Error fetching customer appointments: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/unaki/check-conflicts', methods=['POST'])
@login_required
def api_unaki_check_conflicts():
    """API endpoint for real-time conflict checking in Unaki system"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['staff_id', 'start_time', 'end_time', 'date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        staff_id = int(data['staff_id'])
        start_time = data['start_time']
        end_time = data['end_time']
        check_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        exclude_id = data.get('exclude_id')  # For edit operations

        # Use the business logic function from booking_services
        result = check_staff_conflicts(staff_id, check_date, start_time, end_time, exclude_id)
        return jsonify(result)

    except Exception as e:
        print(f"Error in Unaki conflict checking: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/check-conflicts', methods=['POST'])
@login_required
def api_check_conflicts():
    """API endpoint for real-time conflict checking"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['staff_id', 'start_time', 'end_time', 'date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        staff_id = int(data['staff_id'])
        start_time = data['start_time']
        end_time = data['end_time']
        check_date = datetime.strptime(data['date'], '%Y-%m-%d').date()

        # Use the business logic function from booking_services
        result = check_staff_conflicts(staff_id, check_date, start_time, end_time)
        return jsonify(result)

    except Exception as e:
        print(f"Error in conflict checking: {e}")
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

        appointment, error = create_appointment(appointment_data)

        if not appointment:
            return jsonify({
                'success': False,
                'error': error or 'Failed to create appointment'
            }), 400

        return jsonify({
            'success': True,
            'appointment_id': appointment.id,
            'message': 'Quick booking successful!',
            'appointment_time': appointment_datetime.strftime('%Y-%m-%d %H:%M')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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


@app.route('/api/unaki/save-draft', methods=['POST'])
@login_required
def api_unaki_save_draft():
    """Save Unaki booking as draft - keeps status as scheduled and payment as pending"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied', 'success': False}), 403

    try:
        data = request.get_json()
        print(f"📝 Saving draft booking with data: {data}")

        # Extract and validate fields
        client_name = data.get('clientName')
        staff_id = data.get('staffId')
        service_type = data.get('serviceType')
        start_time_str = data.get('startTime')
        end_time_str = data.get('endTime')
        appointment_date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        notes = data.get('notes', '')

        if not all([client_name, staff_id, service_type, start_time_str, end_time_str]):
            return jsonify({
                'error': 'Missing required fields: client name, staff, service, start time, and end time are required for draft.',
                'success': False
            }), 400

        # Parse date and times
        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()

        # Create UnakiBooking object with draft status
        booking = UnakiBooking(
            client_name=client_name,
            staff_id=int(staff_id),
            service_name=service_type,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_time,
            notes=notes,
            status='scheduled',  # Keep as scheduled for draft
            payment_status='pending'  # Keep payment as pending
        )

        db.session.add(booking)
        db.session.commit()

        print(f"✅ Draft booking saved successfully: ID {booking.id}")

        return jsonify({
            'success': True,
            'message': 'Booking saved as draft successfully.',
            'booking_id': booking.id
        })

    except Exception as e:
        print(f"❌ Error saving draft Unaki booking: {e}")
        import traceback
        traceback.print_exc()
        if 'db' in locals():
            db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/unaki/customer-appointments/<int:client_id>', methods=['GET'])
@login_required
def api_unaki_customer_appointments(client_id):
    """API endpoint to get all Unaki appointments for a customer"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied', 'success': False}), 403

    try:
        customer = Customer.query.get(client_id)
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found', 'bookings': []}), 404

        # Get all Unaki bookings for this customer
        bookings = UnakiBooking.query.filter_by(client_id=customer.id).all()

        # If no bookings found by client_id, try matching by phone if customer.phone exists
        if not bookings and customer.phone:
            bookings = UnakiBooking.query.filter(
                UnakiBooking.client_phone == customer.phone,
                UnakiBooking.client_id.is_(None)  # Only consider if client_id is not set
            ).all()

        appointments_data = []
        for appointment in bookings:
            apt_dict = appointment.to_dict()

            # Ensure service_price is set
            if not apt_dict.get('service_price'):
                apt_dict['service_price'] = 0.0

            # Try to match service by name or service_id
            matching_service = None
            if appointment.service_id:
                matching_service = Service.query.get(appointment.service_id)
            elif appointment.service_name:
                # Try exact match first
                matching_service = Service.query.filter(
                    Service.name == appointment.service_name,
                    Service.is_active == True
                ).first()

                # If no exact match, try partial match (service name might include price/duration)
                if not matching_service:
                    service_base_name = appointment.service_name.split('(')[0].strip()
                    matching_service = Service.query.filter(
                        Service.name.ilike(f'{service_base_name}%'),
                        Service.is_active == True
                    ).first()

            # Add service details to appointment data
            if matching_service:
                apt_dict['service_id'] = matching_service.id
                apt_dict['service_name'] = matching_service.name
                apt_dict['service_price'] = float(matching_service.price)
                apt_dict['service_duration'] = matching_service.duration
            else:
                # If still no match, log it for debugging
                app.logger.warning(f"No matching service found for appointment {appointment.id} with service_name: {appointment.service_name}")

            # Get staff name from staff_id (UnakiBooking doesn't have staff relationship)
            if appointment.staff_id:
                staff_member = User.query.get(appointment.staff_id)
                if staff_member:
                    apt_dict['staff_name'] = staff_member.full_name
                else:
                    apt_dict['staff_name'] = 'Unknown'
            else:
                apt_dict['staff_name'] = 'Unknown'

            appointments_data.append(apt_dict)

        return jsonify({
            'success': True,
            'bookings': appointments_data
        })

    except Exception as e:
        print(f"❌ Error fetching customer appointments: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False, 'bookings': []}), 500


@app.route('/api/unaki/checkin/<int:booking_id>', methods=['POST'])
@login_required
def api_unaki_checkin_appointment(booking_id):
    """Check in a specific Unaki appointment"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied', 'success': False}), 403

    try:
        booking = UnakiBooking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        # Check in the appointment
        booking.checked_in = True
        booking.checked_in_at = datetime.now(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Client {booking.client_name} checked in successfully!',
            'booking_id': booking.id,
            'client_id': booking.client_id,
            'checked_in_at': booking.checked_in_at.isoformat() if booking.checked_in_at else None
        })

    except Exception as e:
        print(f"❌ Error checking in appointment: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/unaki/checkin/manual', methods=['POST'])
@login_required
def api_unaki_manual_checkin():
    """Manual check-in for a client - checks in all their appointments for today"""
    if not current_user.can_access('bookings'):
        print("❌ Check-in access denied")
        return jsonify({'error': 'Access denied', 'success': False}), 403

    try:
        data = request.get_json()
        print(f"🔵 Manual check-in request data: {data}")

        client_id = data.get('client_id')

        if not client_id:
            print("❌ No client_id provided")
            return jsonify({'error': 'Client ID is required', 'success': False}), 400

        print(f"🔍 Looking for customer with ID: {client_id}")

        # Get customer details
        customer = Customer.query.get(client_id)
        if not customer:
            print(f"❌ Customer not found with ID: {client_id}")
            return jsonify({'error': 'Customer not found', 'success': False}), 404

        print(f"✅ Found customer: {customer.full_name}")

        # Get all appointments for this customer today
        today = datetime.now(pytz.timezone('Asia/Kolkata')).date()
        print(f"📅 Searching for appointments on: {today}")

        # Build comprehensive search query using OR conditions
        customer_name = f"{customer.first_name} {customer.last_name}".strip()
        customer_phone = customer.phone
        
        print(f"🔍 Searching for appointments with:")
        print(f"   - client_id: {client_id}")
        print(f"   - client_name: {customer_name}")
        print(f"   - client_phone: {customer_phone}")

        # Search by client_id OR name OR phone (cast to same type for comparison)
        from sqlalchemy import or_
        
        search_conditions = [
            UnakiBooking.client_id == client_id
        ]
        
        # Add name search (try both exact and partial match)
        if customer_name:
            search_conditions.append(UnakiBooking.client_name == customer_name)
            search_conditions.append(UnakiBooking.client_name.ilike(f"%{customer_name}%"))
            
            # Also try first name only (in case last name is missing in booking)
            if customer.first_name:
                search_conditions.append(UnakiBooking.client_name.ilike(f"{customer.first_name}%"))
        
        # Add phone search
        if customer_phone:
            search_conditions.append(UnakiBooking.client_phone == customer_phone)
        
        bookings = UnakiBooking.query.filter(
            or_(*search_conditions),
            func.date(UnakiBooking.appointment_date) == today,
            UnakiBooking.status.in_(['scheduled', 'confirmed'])
        ).all()

        print(f"🔍 Found {len(bookings)} appointments using comprehensive search")
        
        # Log what was found
        for booking in bookings:
            print(f"   📋 Booking {booking.id}: {booking.client_name} (client_id={booking.client_id}, phone={booking.client_phone})")

        if not bookings:
            error_msg = f'No scheduled appointments found for {customer.full_name} today'
            print(f"❌ {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 404

        # Check in all appointments and update client_id if missing
        checked_in_count = 0
        already_checked_in_count = 0
        
        for booking in bookings:
            print(f"📋 Booking {booking.id}: checked_in={booking.checked_in}, client_id={booking.client_id}")
            
            # Update client_id if it's missing or NULL
            if not booking.client_id:
                booking.client_id = client_id
                print(f"✅ Updated client_id to {client_id} for booking {booking.id}")
            
            if not booking.checked_in:
                booking.checked_in = True
                booking.checked_in_at = datetime.now(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None)
                checked_in_count += 1
                print(f"✅ Checked in booking {booking.id}")
            else:
                already_checked_in_count += 1
                print(f"ℹ️ Booking {booking.id} was already checked in")

        db.session.commit()
        print(f"💾 Database committed. Total checked in: {checked_in_count}, Already checked in: {already_checked_in_count}")

        # Build appropriate message
        if checked_in_count > 0 and already_checked_in_count > 0:
            message = f'Checked in {checked_in_count} appointment(s) for {customer.full_name}. {already_checked_in_count} appointment(s) were already checked in.'
        elif checked_in_count > 0:
            message = f'Checked in {checked_in_count} appointment(s) for {customer.full_name}'
        elif already_checked_in_count > 0:
            message = f'All {already_checked_in_count} appointment(s) for {customer.full_name} were already checked in'
        else:
            message = f'No appointments to check in for {customer.full_name}'

        return jsonify({
            'success': True,
            'message': message,
            'client_id': client_id,
            'client_name': customer.full_name,
            'checked_in_count': checked_in_count,
            'already_checked_in_count': already_checked_in_count,
            'total_appointments': len(bookings),
            'booking_ids': [b.id for b in bookings]
        })

    except Exception as e:
        print(f"❌ Error in manual check-in: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/unaki/checkin/undo/<int:booking_id>', methods=['POST'])
@login_required
def api_unaki_undo_checkin(booking_id):
    """Undo check-in for a specific Unaki appointment"""
    if not current_user.can_access('bookings'):
        return jsonify({'error': 'Access denied', 'success': False}), 403

    try:
        booking = UnakiBooking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        # Undo check-in
        booking.checked_in = False
        booking.checked_in_at = None

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Check-in removed for {booking.client_name}',
            'booking_id': booking.id
        })

    except Exception as e:
        print(f"❌ Error undoing check-in: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500