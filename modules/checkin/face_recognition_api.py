
"""
Face recognition API endpoints
"""
from flask import request, jsonify
from flask_login import login_required
from app import app, db
from models import Customer, Appointment
from datetime import datetime, date
import base64
import io
from PIL import Image
import numpy as np

@app.route('/api/recognize_face', methods=['POST'])
@login_required
def recognize_face():
    """
    Recognize customer from face image
    """
    try:
        data = request.get_json()
        face_image = data.get('face_image')
        
        if not face_image:
            return jsonify({
                'success': False,
                'error': 'No face image provided'
            }), 400
        
        # For now, implement a simple mock recognition
        # In production, you would integrate with face_recognition library or cloud API
        
        # Mock: Find customers with face photos and return the first one
        # In real implementation, compare face embeddings
        customers_with_faces = Customer.query.filter(
            Customer.face_photo.isnot(None),
            Customer.is_active == True
        ).all()
        
        if not customers_with_faces:
            return jsonify({
                'success': True,
                'recognized': False,
                'message': 'No registered faces in database'
            })
        
        # Mock recognition - return first customer for demo
        # In production, implement actual face matching
        customer = customers_with_faces[0]
        
        # Get customer stats
        total_visits = Appointment.query.filter_by(
            client_id=customer.id,
            status='completed'
        ).count()
        
        return jsonify({
            'success': True,
            'recognized': True,
            'customer': {
                'id': customer.id,
                'name': customer.full_name,
                'phone': customer.phone,
                'email': customer.email,
                'is_vip': customer.is_vip,
                'total_visits': total_visits
            }
        })
        
    except Exception as e:
        print(f"Face recognition error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
