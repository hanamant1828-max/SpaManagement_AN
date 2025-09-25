
"""
Unaki Booking API endpoints for multiple service bookings
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, time, timedelta
from app import db
from models import Customer, Service, User, UnakiStaff, UnakiAppointment, UnakiBreak
import json

# Create Blueprint
unaki_api = Blueprint('unaki_api', __name__, url_prefix='/api/unaki')

@unaki_api.route('/services', methods=['GET'])
@login_required
def get_services():
    """Get all active services"""
    try:
        services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
        services_data = []
        
        for service in services:
            services_data.append({
                'id': service.id,
                'name': service.name,
                'duration': service.duration,
                'price': float(service.price),
                'description': service.description,
                'category': service.category
            })
        
        return jsonify(services_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@unaki_api.route('/staff', methods=['GET'])
@login_required  
def get_staff():
    """Get all active staff members"""
    try:
        # Try Unaki staff first, fallback to regular staff
        unaki_staff = UnakiStaff.query.filter_by(active=True).order_by(UnakiStaff.name).all()
        
        if unaki_staff:
            staff_data = []
            for staff in unaki_staff:
                staff_data.append({
                    'id': staff.id,
                    'name': staff.name,
                    'specialty': staff.specialty,
                    'active': staff.active
                })
        else:
            # Fallback to regular User staff
            regular_staff = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()
            staff_data = []
            for staff in regular_staff:
                staff_data.append({
                    'id': staff.id,
                    'name': f"{staff.first_name} {staff.last_name}",
                    'specialty': staff.designation or staff.role,
                    'active': staff.is_active
                })
        
        return jsonify(staff_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@unaki_api.route('/clients/search', methods=['GET'])
@login_required
def search_client():
    """Search client by phone number"""
    try:
        phone = request.args.get('phone', '').strip()
        
        if not phone:
            return jsonify({'error': 'Phone number is required'}), 400
        
        # Search for client by phone number
        client = Customer.query.filter_by(phone=phone, is_active=True).first()
        
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        client_data = {
            'id': client.id,
            'first_name': client.first_name,
            'last_name': client.last_name,
            'phone': client.phone,
            'email': client.email,
            'gender': client.gender,
            'date_of_birth': client.date_of_birth.isoformat() if client.date_of_birth else None,
            'total_visits': client.total_visits,
            'total_spent': float(client.total_spent) if client.total_spent else 0.0
        }
        
        return jsonify(client_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@unaki_api.route('/clients', methods=['POST'])
@login_required
def add_client():
    """Add new client"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('first_name') or not data.get('last_name') or not data.get('phone'):
            return jsonify({'error': 'First name, last name, and phone are required'}), 400
        
        # Check if phone already exists
        existing_client = Customer.query.filter_by(phone=data['phone']).first()
        if existing_client:
            return jsonify({'error': 'A client with this phone number already exists'}), 400
        
        # Create new client
        client = Customer(
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            email=data.get('email'),
            gender=data.get('gender'),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            is_active=True,
            total_visits=0,
            total_spent=0.0
        )
        
        db.session.add(client)
        db.session.commit()
        
        client_data = {
            'id': client.id,
            'first_name': client.first_name,
            'last_name': client.last_name,
            'phone': client.phone,
            'email': client.email,
            'gender': client.gender,
            'date_of_birth': client.date_of_birth.isoformat() if client.date_of_birth else None,
            'total_visits': client.total_visits,
            'total_spent': float(client.total_spent)
        }
        
        return jsonify(client_data), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@unaki_api.route('/bookings/multiple', methods=['POST'])
@login_required
def create_multiple_bookings():
    """Create multiple appointments for a client"""
    try:
        data = request.get_json()
        
        client_id = data.get('client_id')
        bookings = data.get('bookings', [])
        
        if not client_id or not bookings:
            return jsonify({'error': 'Client ID and bookings are required'}), 400
        
        # Verify client exists
        client = Customer.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        created_appointments = []
        
        for booking_data in bookings:
            # Validate booking data
            required_fields = ['service_id', 'staff_id', 'appointment_date', 'start_time']
            for field in required_fields:
                if not booking_data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Get service details
            service = Service.query.get(booking_data['service_id'])
            if not service:
                return jsonify({'error': f'Service not found: {booking_data["service_id"]}'}), 404
            
            # Parse appointment datetime
            appointment_date = datetime.strptime(booking_data['appointment_date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(booking_data['start_time'], '%H:%M').time()
            
            start_datetime = datetime.combine(appointment_date, start_time)
            end_datetime = start_datetime + timedelta(minutes=booking_data.get('duration', service.duration))
            
            # Check for conflicts (optional - you may want to allow overlaps)
            existing_appointment = UnakiAppointment.query.filter(
                UnakiAppointment.staff_id == booking_data['staff_id'],
                UnakiAppointment.appointment_date == appointment_date,
                UnakiAppointment.start_time < end_datetime.time(),
                UnakiAppointment.end_time > start_time
            ).first()
            
            if existing_appointment:
                return jsonify({
                    'error': f'Time conflict detected for staff member at {booking_data["start_time"]} on {booking_data["appointment_date"]}'
                }), 400
            
            # Create appointment
            appointment = UnakiAppointment(
                staff_id=booking_data['staff_id'],
                client_name=f"{client.first_name} {client.last_name}",
                service=service.name,
                start_time=start_datetime,
                end_time=end_datetime,
                phone=client.phone,
                notes=booking_data.get('notes', ''),
                appointment_date=appointment_date
            )
            
            db.session.add(appointment)
            created_appointments.append(appointment)
        
        # Update client stats
        client.total_visits += len(created_appointments)
        total_amount = sum(booking.get('price', 0) for booking in bookings)
        client.total_spent = (client.total_spent or 0) + total_amount
        client.last_visit = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Appointments created successfully',
            'booked_count': len(created_appointments),
            'total_amount': total_amount
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@unaki_api.route('/schedule', methods=['GET'])
@login_required
def get_schedule():
    """Get schedule for a specific date"""
    try:
        selected_date_str = request.args.get('date')
        if not selected_date_str:
            selected_date = date.today()
        else:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        
        # Get appointments for the date
        appointments = UnakiAppointment.query.filter_by(appointment_date=selected_date).all()
        appointments_data = [apt.to_dict() for apt in appointments]
        
        # Get breaks for the date
        breaks = UnakiBreak.query.filter_by(break_date=selected_date).all()
        breaks_data = [brk.to_dict() for brk in breaks]
        
        return jsonify({
            'date': selected_date.isoformat(),
            'appointments': appointments_data,
            'breaks': breaks_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Register the blueprint
def register_unaki_api(app):
    """Register the Unaki API blueprint with the app"""
    app.register_blueprint(unaki_api)
