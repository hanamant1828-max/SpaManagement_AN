"""
Face recognition API endpoints
"""
from flask import request, jsonify, Blueprint
from flask_login import login_required, current_user
from app import app, db
from models import Customer, Appointment
from datetime import datetime, date
import base64
import io
from PIL import Image
import numpy as np

# Create blueprint for face recognition routes
face_recognition_bp = Blueprint('face_recognition', __name__, url_prefix='/api/face-recognition')

@face_recognition_bp.route('/recognize', methods=['POST'])
@login_required
def recognize_face():
    """
    Recognize customer from face image
    """
    try:
        # Log authentication status for debugging
        print(f"🔐 Authenticated user for face recognition: {current_user.username if current_user.is_authenticated else 'Anonymous'}")
        if not current_user.is_authenticated:
            print("❌ Access denied: User not authenticated.")
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 401
        print(f"✅ User: {current_user.username} (ID: {current_user.id}) is authenticated.")

        data = request.get_json()
        face_image = data.get('face_image')

        if not face_image:
            print("❌ No face image provided in the request.")
            return jsonify({
                'success': False,
                'error': 'No face image provided'
            }), 400

        print("📸 Face image received, proceeding with mock recognition.")

        # For now, implement a simple mock recognition
        # In production, you would integrate with face_recognition library or cloud API

        # Mock: Find customers with face photos and return the first one
        # In real implementation, compare face embeddings
        customers_with_faces = Customer.query.filter(
            Customer.face_photo.isnot(None),
            Customer.is_active == True
        ).all()

        if not customers_with_faces:
            print("ℹ️ No registered faces in the database.")
            return jsonify({
                'success': True,
                'recognized': False,
                'message': 'No registered faces in database'
            }), 200

        # Mock recognition - return first customer for demo
        # In production, implement actual face matching
        customer = customers_with_faces[0]
        print(f"👤 Mock recognized customer: {customer.full_name} (ID: {customer.id})")

        # Get customer stats
        total_visits = Appointment.query.filter_by(
            client_id=customer.id,
            status='completed'
        ).count()
        print(f"📈 Total visits for {customer.full_name}: {total_visits}")

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
        }), 200

    except Exception as e:
        app.logger.error(f"Face recognition error: {e}")
        return jsonify({
            'success': False,
            'error': 'Face recognition service encountered an error. Please try again.'
        }), 500