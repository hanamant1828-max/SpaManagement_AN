#!/usr/bin/env python3
"""
Client Management API for Unaki Booking System
Provides simplified client CRUD operations with phone-based validation
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import Client
from sqlalchemy.exc import IntegrityError
import re

# Create blueprint for client API
client_api_bp = Blueprint('client_api', __name__, url_prefix='/api/unaki/clients')

def validate_client_data(data, is_update=False):
    """Validate client data with proper error messages"""
    errors = []
    
    # Validate name
    name = data.get('name', '').strip()
    if not name and not is_update:
        errors.append('Name is required')
    elif name and not Client.validate_name(name):
        errors.append('Name must be at least 2 characters')
    
    # Validate phone
    phone = data.get('phone', '').strip()
    if not phone and not is_update:
        errors.append('Phone number is required')
    elif phone:
        formatted_phone = Client.format_phone(phone)
        if not Client.validate_phone(phone):
            errors.append('Phone number must be 10-15 digits')
        
        # Check for duplicate phone (skip for updates with same phone)
        existing_client = Client.query.filter_by(phone=formatted_phone).first()
        if existing_client:
            client_id = data.get('id') or data.get('client_id')
            if not is_update or (existing_client.id != client_id):
                errors.append(f'Phone number already registered to: {existing_client.name}')
    
    return errors, name, Client.format_phone(phone) if phone else None

@client_api_bp.route('', methods=['POST'])
@login_required
def create_client():
    """Create new client - POST /api/unaki/clients"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided', 'success': False}), 400
        
        # Validate input data
        errors, name, formatted_phone = validate_client_data(data, is_update=False)
        if errors:
            return jsonify({'error': '; '.join(errors), 'success': False}), 400
        
        # Create new client
        client = Client(
            name=name,
            phone=formatted_phone
        )
        
        db.session.add(client)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Client {name} created successfully',
            'client': client.to_dict()
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        if 'UNIQUE constraint failed: client.phone' in str(e):
            return jsonify({'error': 'Phone number already exists', 'success': False}), 409
        return jsonify({'error': 'Database constraint error', 'success': False}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create client: {str(e)}', 'success': False}), 500

@client_api_bp.route('', methods=['GET'])
@login_required
def list_clients():
    """List all clients - GET /api/unaki/clients"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '').strip()
        
        # Build query
        query = Client.query
        
        # Add search filter
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    Client.name.ilike(search_term),
                    Client.phone.like(search_term)
                )
            )
        
        # Order by name
        query = query.order_by(Client.name)
        
        # Apply pagination
        if per_page > 100:  # Limit maximum results
            per_page = 100
            
        clients = query.limit(per_page).offset((page - 1) * per_page).all()
        total = query.count()
        
        return jsonify({
            'success': True,
            'clients': [client.to_dict() for client in clients],
            'total': total,
            'page': page,
            'per_page': per_page,
            'has_more': total > page * per_page
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to list clients: {str(e)}', 'success': False}), 500

@client_api_bp.route('/<int:client_id>', methods=['GET'])
@login_required
def get_client(client_id):
    """Get client by ID - GET /api/unaki/clients/{id}"""
    try:
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found', 'success': False}), 404
        
        # Get appointment history
        appointments = []
        for booking in client.unaki_bookings:
            appointments.append({
                'id': booking.id,
                'date': booking.appointment_date.strftime('%Y-%m-%d'),
                'time': f"{booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}",
                'service': booking.service_name,
                'staff': booking.staff_name,
                'status': booking.status,
                'amount': float(booking.service_price) if booking.service_price else 0.0
            })
        
        # Sort appointments by date (newest first)
        appointments.sort(key=lambda x: x['date'], reverse=True)
        
        client_data = client.to_dict()
        client_data['appointments'] = appointments
        client_data['total_appointments'] = len(appointments)
        
        return jsonify({
            'success': True,
            'client': client_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get client: {str(e)}', 'success': False}), 500

@client_api_bp.route('/<int:client_id>', methods=['PUT'])
@login_required
def update_client(client_id):
    """Update client - PUT /api/unaki/clients/{id}"""
    try:
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found', 'success': False}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided', 'success': False}), 400
        
        # Add client ID for duplicate checking
        data['id'] = client_id
        
        # Validate input data
        errors, name, formatted_phone = validate_client_data(data, is_update=True)
        if errors:
            return jsonify({'error': '; '.join(errors), 'success': False}), 400
        
        # Update fields if provided
        if name:
            client.name = name
        if formatted_phone:
            client.phone = formatted_phone
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Client {client.name} updated successfully',
            'client': client.to_dict()
        })
        
    except IntegrityError as e:
        db.session.rollback()
        if 'UNIQUE constraint failed: client.phone' in str(e):
            return jsonify({'error': 'Phone number already exists', 'success': False}), 409
        return jsonify({'error': 'Database constraint error', 'success': False}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update client: {str(e)}', 'success': False}), 500

@client_api_bp.route('/search', methods=['GET'])
@login_required
def search_clients():
    """Search clients by phone - GET /api/unaki/clients/search?phone={phone}"""
    try:
        phone = request.args.get('phone', '').strip()
        if not phone:
            return jsonify({'error': 'Phone parameter is required', 'success': False}), 400
        
        # Format phone for search
        formatted_phone = Client.format_phone(phone)
        if not formatted_phone:
            return jsonify({'error': 'Invalid phone format', 'success': False}), 400
        
        # Find exact match first
        client = Client.query.filter_by(phone=formatted_phone).first()
        
        result = {
            'success': True,
            'phone_searched': formatted_phone,
            'exact_match': client.to_dict() if client else None,
            'suggestions': []
        }
        
        # If no exact match, find similar phone numbers
        if not client and len(formatted_phone) >= 4:
            # Search for phones containing the last 4+ digits
            search_suffix = formatted_phone[-4:]
            similar_clients = Client.query.filter(
                Client.phone.like(f'%{search_suffix}')
            ).limit(5).all()
            
            result['suggestions'] = [c.to_dict() for c in similar_clients]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to search clients: {str(e)}', 'success': False}), 500

# Export endpoints for registration
def get_client_endpoints():
    """Get all client management routes for manual registration"""
    return [
        ('POST', '/api/unaki/clients', create_client),
        ('GET', '/api/unaki/clients', list_clients),
        ('GET', '/api/unaki/clients/<int:client_id>', get_client),
        ('PUT', '/api/unaki/clients/<int:client_id>', update_client),
        ('GET', '/api/unaki/clients/search', search_clients)
    ]