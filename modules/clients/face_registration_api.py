
"""
Face registration API for customers
"""
from flask import request, jsonify, Blueprint
from flask_login import login_required, current_user
from app import app, db
from models import Customer
import base64
import io
import json
import threading

# Lazy imports for PIL and numpy to avoid import errors
try:
    from PIL import Image
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ PIL/Pillow not available - face registration will be disabled")

face_registration_bp = Blueprint('face_registration', __name__, url_prefix='/api/face-registration')

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
                    
                    print("🔄 Initializing InsightFace model for registration...")
                    _face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
                    _face_app.prepare(ctx_id=0, det_size=(640, 640))
                    print("✅ InsightFace model initialized successfully")
                except Exception as e:
                    print(f"❌ Failed to initialize InsightFace: {e}")
                    raise
    
    return _face_app

@face_registration_bp.route('/register', methods=['POST'])
@login_required
def register_face():
    """
    Register customer face for recognition
    """
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        face_image = data.get('face_image')

        if not customer_id or not face_image:
            return jsonify({
                'success': False,
                'error': 'Customer ID and face image are required'
            }), 400

        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({
                'success': False,
                'error': 'Customer not found'
            }), 404

        # Decode image
        if ',' in face_image:
            face_image = face_image.split(',')[1]
        
        image_data = base64.b64decode(face_image)
        image = Image.open(io.BytesIO(image_data))
        image_array = np.array(image)
        
        # Convert RGB to BGR
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = image_array[:, :, ::-1]

        # Get or initialize face analysis model
        try:
            face_app = get_face_app()
            
            faces = face_app.get(image_array)
            
            if len(faces) == 0:
                return jsonify({
                    'success': False,
                    'error': 'No face detected in image. Please ensure face is clearly visible.'
                }), 400
            
            if len(faces) > 1:
                return jsonify({
                    'success': False,
                    'error': 'Multiple faces detected. Please ensure only one face is visible.'
                }), 400
            
            # Get face embedding
            face_embedding = faces[0].embedding.tolist()
            
            # Check for duplicate faces
            existing_customers = Customer.query.filter(
                Customer.face_encoding.isnot(None),
                Customer.id != customer_id
            ).all()
            
            duplicate_threshold = 0.6
            duplicates = []
            
            for existing in existing_customers:
                try:
                    existing_embedding = np.array(json.loads(existing.face_encoding))
                    similarity = np.dot(face_embedding, existing_embedding) / (
                        np.linalg.norm(face_embedding) * np.linalg.norm(existing_embedding)
                    )
                    
                    if similarity > duplicate_threshold:
                        duplicates.append({
                            'id': existing.id,
                            'name': existing.full_name,
                            'similarity': f"{similarity*100:.1f}%"
                        })
                except:
                    continue
            
            # Save face encoding
            customer.face_encoding = json.dumps(face_embedding)
            customer.face_image_url = f"data:image/jpeg;base64,{face_image.split(',')[1] if ',' in face_image else face_image}"
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Face registered successfully',
                'duplicate_warning': len(duplicates) > 0,
                'duplicates': duplicates
            }), 200
            
        except Exception as e:
            print(f"Face encoding error: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to process face image'
            }), 500

    except Exception as e:
        app.logger.error(f"Face registration error: {e}")
        return jsonify({
            'success': False,
            'error': 'Face registration failed'
        }), 500


@face_registration_bp.route('/delete/<int:customer_id>', methods=['POST'])
@login_required
def delete_face(customer_id):
    """
    Delete customer face data
    """
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({
                'success': False,
                'error': 'Customer not found'
            }), 404

        customer.face_encoding = None
        customer.face_image_url = None
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Face data deleted for {customer.full_name}'
        }), 200

    except Exception as e:
        app.logger.error(f"Face deletion error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete face data'
        }), 500
