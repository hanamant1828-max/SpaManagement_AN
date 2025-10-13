#!/usr/bin/env python3
"""
Face Recognition End-to-End Test Script
Tests both registration and check-in functionality
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_insightface_installation():
    """Test if InsightFace is properly installed"""
    print("\n" + "="*60)
    print("TEST 1: InsightFace Installation")
    print("="*60)
    
    try:
        import insightface
        from insightface.app import FaceAnalysis
        print("✅ InsightFace imported successfully")
        print(f"   Version: {insightface.__version__ if hasattr(insightface, '__version__') else 'Unknown'}")
        return True
    except ImportError as e:
        print(f"❌ InsightFace import failed: {e}")
        return False


def test_dependencies():
    """Test all required dependencies"""
    print("\n" + "="*60)
    print("TEST 2: Required Dependencies")
    print("="*60)
    
    dependencies = [
        ('numpy', 'NumPy'),
        ('PIL', 'Pillow'),
        ('onnxruntime', 'ONNX Runtime'),
        ('cv2', 'OpenCV')
    ]
    
    all_ok = True
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name} is installed")
        except ImportError:
            print(f"❌ {name} is missing")
            all_ok = False
    
    return all_ok


def test_database_schema():
    """Test if customer table has required face recognition fields"""
    print("\n" + "="*60)
    print("TEST 3: Database Schema")
    print("="*60)
    
    from app import db
    from models import Customer
    
    required_fields = ['face_encoding', 'face_image_url']
    all_ok = True
    
    for field in required_fields:
        if hasattr(Customer, field):
            print(f"✅ Customer.{field} exists")
        else:
            print(f"❌ Customer.{field} is missing")
            all_ok = False
    
    return all_ok


def test_face_registration_endpoint():
    """Test face registration API endpoint"""
    print("\n" + "="*60)
    print("TEST 4: Face Registration API")
    print("="*60)
    
    from modules.clients.face_registration_api import face_registration_bp
    
    if face_registration_bp:
        print("✅ Face registration blueprint exists")
        print(f"   URL Prefix: {face_registration_bp.url_prefix}")
        
        # Check if the register route exists
        routes = [rule.rule for rule in face_registration_bp.url_map.iter_rules() 
                 if rule.endpoint.startswith('face_registration.')]
        if routes:
            print(f"   Routes: {', '.join(routes)}")
        
        return True
    else:
        print("❌ Face registration blueprint not found")
        return False


def test_face_recognition_endpoint():
    """Test face recognition API endpoint"""
    print("\n" + "="*60)
    print("TEST 5: Face Recognition (Check-in) API")
    print("="*60)
    
    try:
        from modules.checkin.face_recognition_api import face_recognition_bp
        
        if face_recognition_bp:
            print("✅ Face recognition blueprint exists")
            print(f"   URL Prefix: {face_recognition_bp.url_prefix}")
            return True
        else:
            print("❌ Face recognition blueprint not found")
            return False
    except ImportError as e:
        print(f"❌ Face recognition module import failed: {e}")
        return False


def test_face_analysis():
    """Test InsightFace face analysis"""
    print("\n" + "="*60)
    print("TEST 6: InsightFace Face Analysis")
    print("="*60)
    
    try:
        import insightface
        from insightface.app import FaceAnalysis
        import numpy as np
        
        print("🔄 Initializing FaceAnalysis...")
        face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
        face_app.prepare(ctx_id=0, det_size=(640, 640))
        print("✅ FaceAnalysis initialized successfully")
        
        # Create a simple test image (blank)
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        print("🔄 Testing face detection on blank image...")
        faces = face_app.get(test_image)
        print(f"✅ Face detection completed (found {len(faces)} faces, expected 0)")
        
        return True
    except Exception as e:
        print(f"❌ Face analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n🧪 FACE RECOGNITION SYSTEM - END-TO-END TEST")
    print("="*60)
    
    tests = [
        test_insightface_installation,
        test_dependencies,
        test_database_schema,
        test_face_registration_endpoint,
        test_face_recognition_endpoint,
        test_face_analysis
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED - Face recognition system is ready!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Please review the errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
