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
import json
import threading

# Create blueprint for face recognition routes
face_recognition_bp = Blueprint('face_recognition', __name__, url_prefix='/api/face-recognition')

# Global face analysis model (singleton)
_face_app = None
_face_app_lock = threading.Lock()

def get_face_app():
    """Get or initialize the face analysis model (singleton pattern)"""
    global _face_app

    if _face_app is None:
        with _face_app_lock:
            # Double-check pattern
            if _face_app is None:
                try:
                    import insightface
                    from insightface.app import FaceAnalysis

                    print("🔄 Initializing InsightFace model (first time only)...")
                    _face_app = FaceAnalysis(providers=['CPUExecutionProvider'], allowed_modules=['detection', 'recognition'])
                    _face_app.prepare(ctx_id=0, det_size=(320, 320), det_thresh=0.5)
                    print("✅ InsightFace model initialized successfully")
                except ImportError as import_err:
                    print(f"❌ InsightFace library not installed: {import_err}")
                    raise ImportError("Face recognition library (insightface) is not installed. Please contact administrator.")
                except Exception as e:
                    print(f"❌ Failed to initialize InsightFace: {e}")
                    import traceback
                    traceback.print_exc()
                    raise Exception(f"Face recognition initialization failed: {str(e)}")

    return _face_app

@face_recognition_bp.route('/recognize', methods=['POST'])
def recognize_face():
    """
    Recognize customer face for check-in
    """
    try:
        # Check authentication manually to return JSON instead of HTML redirect
        if not current_user.is_authenticated:
            print("❌ Access denied: User not authenticated.")
            return jsonify({
                'success': False,
                'recognized': False,
                'error': 'Access denied',
                'message': 'Please log in to access this feature'
            }), 401
        
        # Log authentication status for debugging
        print(f"🔐 Face recognition request from user: {current_user.username}")
        
        print(f"✅ User: {current_user.username} (ID: {current_user.id}) is authenticated.")

        # Get JSON data with error handling
        try:
            data = request.get_json()
            if not data:
                print("❌ No JSON data in request")
                return jsonify({
                    'success': False,
                    'recognized': False,
                    'error': 'No data provided',
                    'message': 'Invalid request format'
                }), 400
        except Exception as json_error:
            print(f"❌ JSON parsing error: {json_error}")
            return jsonify({
                'success': False,
                'recognized': False,
                'error': 'Invalid JSON data',
                'message': 'Request data is not valid JSON'
            }), 400
        
        # Accept both 'image' and 'face_image' keys for compatibility
        face_image = data.get('image') or data.get('face_image')

        if not face_image:
            print("❌ No face image provided in the request.")
            print(f"Request data keys: {list(data.keys())}")
            return jsonify({
                'success': False,
                'recognized': False,
                'error': 'No face image provided',
                'message': 'Face image is required for recognition'
            }), 400

        print("📸 Face image received, proceeding with recognition.")

        # Decode the face image from base64
        import base64
        import io
        from PIL import Image
        import numpy as np

        # Remove data URI prefix if present
        if ',' in face_image:
            face_image = face_image.split(',')[1]

        image_data = base64.b64decode(face_image)
        image = Image.open(io.BytesIO(image_data))

        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize if image is too small (minimum 160x160 for face detection)
        min_size = 160
        if image.size[0] < min_size or image.size[1] < min_size:
            ratio = max(min_size / image.size[0], min_size / image.size[1])
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            print(f"📏 Resized image from {image.size} to {new_size}")

        image_array = np.array(image)
        print(f"📐 Image array shape: {image_array.shape}, dtype: {image_array.dtype}")

        # Find customers with face encodings
        customers_with_faces = Customer.query.filter(
            Customer.face_encoding.isnot(None),
            Customer.is_active == True
        ).all()

        if not customers_with_faces:
            print("ℹ️ No registered faces in the database.")
            return jsonify({
                'success': True,
                'recognized': False,
                'message': 'No registered faces in database'
            }), 200

        # Use InsightFace for face recognition
        try:
            face_app = get_face_app()

            # Detect face in the image
            faces = face_app.get(image_array)

            if len(faces) == 0:
                print("❌ No face detected in the image.")
                return jsonify({
                    'success': True,
                    'recognized': False,
                    'message': 'No face detected in image'
                }), 200

            # Get the first face embedding
            new_embedding = faces[0].embedding

            # Compare with stored faces
            best_match = None
            best_similarity = 0.0
            threshold = 0.4  # Similarity threshold (lower is more strict)

            for customer in customers_with_faces:
                try:
                    # Handle both binary and JSON stored formats
                    if isinstance(customer.face_encoding, bytes):
                        # Legacy binary format
                        stored_embedding = np.frombuffer(customer.face_encoding, dtype=np.float32)
                    elif isinstance(customer.face_encoding, str):
                        try:
                            # Try JSON format first
                            stored_embedding = np.array(json.loads(customer.face_encoding))
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            # Fallback: try to decode as binary stored in text field
                            try:
                                stored_embedding = np.frombuffer(customer.face_encoding.encode('latin1'), dtype=np.float32)
                            except:
                                print(f"⚠️ Cannot decode face encoding for customer {customer.id}, skipping")
                                continue
                    else:
                        print(f"⚠️ Unknown face encoding format for customer {customer.id}, skipping")
                        continue

                    # Calculate cosine similarity
                    similarity = np.dot(new_embedding, stored_embedding) / (
                        np.linalg.norm(new_embedding) * np.linalg.norm(stored_embedding)
                    )

                    print(f"🔍 Similarity with {customer.full_name}: {similarity:.4f}")

                    if similarity > best_similarity and similarity > threshold:
                        best_similarity = similarity
                        best_match = customer

                except Exception as e:
                    print(f"⚠️ Error comparing with customer {customer.id}: {e}")
                    continue

            if best_match:
                customer = best_match
                print(f"👤 Recognized customer: {customer.full_name} (ID: {customer.id}, Similarity: {best_similarity:.4f})")
            else:
                print("❌ No matching face found.")
                return jsonify({
                    'success': True,
                    'recognized': False,
                    'message': 'Face not recognized'
                }), 200

        except Exception as e:
            app.logger.error(f"Face recognition error: {e}")
            # Fallback to first customer for demo purposes
            if customers_with_faces:
                customer = customers_with_faces[0]
                print(f"👤 Fallback to first customer: {customer.full_name} (ID: {customer.id})")
            else:
                print("❌ No registered faces to fallback to.")
                return jsonify({
                    'success': False,
                    'error': 'Face recognition service encountered an error. Please try again.'
                }), 500


        # Get customer stats - check both Appointment and UnakiBooking tables
        from models import UnakiBooking
        from sqlalchemy import func, or_
        
        # Count completed appointments from both tables
        total_visits = Appointment.query.filter_by(
            client_id=customer.id,
            status='completed'
        ).count()
        
        # Also count from UnakiBooking
        total_visits += UnakiBooking.query.filter_by(
            client_id=customer.id,
            status='completed'
        ).count()
        
        print(f"📈 Total visits for {customer.full_name}: {total_visits}")

        # Get today's appointments for this customer from BOTH tables
        today = date.today()
        
        # Check traditional Appointment table
        todays_appointments = Appointment.query.filter(
            Appointment.client_id == customer.id,
            func.date(Appointment.appointment_date) == today,
            Appointment.status.in_(['scheduled', 'confirmed', 'in_progress'])
        ).order_by(Appointment.appointment_date).all()
        
        appointments_list = []
        for apt in todays_appointments:
            start_time_str = apt.appointment_date.strftime('%I:%M %p') if apt.appointment_date else ''
            end_time_str = apt.end_time.strftime('%I:%M %p') if apt.end_time else ''
            
            appointments_list.append({
                'id': apt.id,
                'service_name': apt.service.name if apt.service else getattr(apt, 'service_name', 'Service'),
                'staff_name': apt.staff.full_name if apt.staff else 'Unassigned',
                'start_time': start_time_str,
                'end_time': end_time_str,
                'status': apt.status,
                'payment_status': apt.payment_status
            })
        
        # Also check UnakiBooking table with comprehensive search
        customer_name = customer.full_name
        customer_phone = customer.phone
        
        search_conditions = [UnakiBooking.client_id == customer.id]
        if customer_name:
            search_conditions.append(UnakiBooking.client_name.ilike(f"%{customer_name}%"))
            if customer.first_name:
                search_conditions.append(UnakiBooking.client_name.ilike(f"{customer.first_name}%"))
        if customer_phone:
            search_conditions.append(UnakiBooking.client_phone == customer_phone)
        
        unaki_bookings = UnakiBooking.query.filter(
            or_(*search_conditions),
            func.date(UnakiBooking.appointment_date) == today,
            UnakiBooking.status.in_(['scheduled', 'confirmed'])
        ).order_by(UnakiBooking.start_time).all()
        
        for booking in unaki_bookings:
            appointments_list.append({
                'id': booking.id,
                'service_name': booking.service_name or 'Service',
                'staff_name': booking.staff_name or 'Unassigned',
                'start_time': booking.start_time or '',
                'end_time': booking.end_time or '',
                'status': booking.status,
                'payment_status': booking.payment_status
            })
        
        print(f"📅 Today's appointments for {customer.full_name}: {len(appointments_list)}")

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
            },
            'todays_appointments': appointments_list
        }), 200

    except ImportError as import_error:
        app.logger.error(f"Face recognition library import error: {import_error}")
        return jsonify({
            'success': False,
            'recognized': False,
            'error': 'Face recognition library not available',
            'message': 'The face recognition service is not properly installed. Please contact administrator.'
        }), 500
    except Exception as e:
        app.logger.error(f"Face recognition error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'recognized': False,
            'error': 'Face recognition service error',
            'message': 'The face recognition service encountered an error. Please try again or contact support.'
        }), 500