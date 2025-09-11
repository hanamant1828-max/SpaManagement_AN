
"""
Comprehensive Face Capture System Test
Tests all aspects of face capture and save functionality
"""

import requests
import json
import base64
from io import BytesIO
from PIL import Image, ImageDraw
import sys

# Test configuration
BASE_URL = "http://0.0.0.0:5000"
TEST_CLIENT_ID = 1

def create_test_image():
    """Create a test image to simulate camera capture"""
    # Create a simple test image
    img = Image.new('RGB', (400, 300), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple face-like shape
    draw.ellipse([100, 75, 300, 225], fill='peach', outline='black', width=2)
    draw.ellipse([150, 120, 170, 140], fill='black')  # Left eye
    draw.ellipse([230, 120, 250, 140], fill='black')  # Right eye
    draw.ellipse([190, 160, 210, 180], fill='pink')   # Nose
    draw.arc([160, 180, 240, 210], start=0, end=180, fill='red', width=3)  # Mouth
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    img_data = buffer.getvalue()
    img_base64 = base64.b64encode(img_data).decode('utf-8')
    return f"data:image/jpeg;base64,{img_base64}"

def test_api_endpoints():
    """Test all face-related API endpoints"""
    print("🧪 Testing Face Capture API Endpoints...")
    
    # Test 1: Get customers
    print("\n1️⃣ Testing GET /api/customers")
    try:
        response = requests.get(f"{BASE_URL}/api/customers")
        if response.status_code == 200:
            customers = response.json()
            if customers.get('success'):
                print(f"✅ Successfully retrieved {len(customers.get('customers', []))} customers")
            else:
                print(f"❌ API returned error: {customers.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

    # Test 2: Save face data
    print("\n2️⃣ Testing POST /api/save_face")
    test_image = create_test_image()
    
    test_cases = [
        # Valid case
        {
            'name': 'Valid face data',
            'data': {'client_id': TEST_CLIENT_ID, 'face_image': test_image},
            'expected_success': True
        },
        # Missing client_id
        {
            'name': 'Missing client_id',
            'data': {'face_image': test_image},
            'expected_success': False
        },
        # Missing face_image
        {
            'name': 'Missing face_image',
            'data': {'client_id': TEST_CLIENT_ID},
            'expected_success': False
        },
        # Invalid client_id
        {
            'name': 'Invalid client_id',
            'data': {'client_id': 'invalid', 'face_image': test_image},
            'expected_success': False
        },
        # Invalid image format
        {
            'name': 'Invalid image format',
            'data': {'client_id': TEST_CLIENT_ID, 'face_image': 'invalid_image_data'},
            'expected_success': False
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   🧪 Test 2.{i}: {test_case['name']}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/save_face",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            result = response.json()
            success = result.get('success', False)
            
            if success == test_case['expected_success']:
                status = "✅ PASSED"
                if success:
                    print(f"      {status} - {result.get('message')}")
                else:
                    print(f"      {status} - Expected error: {result.get('error')}")
            else:
                print(f"      ❌ FAILED - Expected success={test_case['expected_success']}, got success={success}")
                print(f"         Response: {result}")
                
        except Exception as e:
            print(f"      ❌ FAILED - Request error: {str(e)}")

    # Test 3: Get customers with faces
    print("\n3️⃣ Testing GET /api/customers_with_faces")
    try:
        response = requests.get(f"{BASE_URL}/api/customers_with_faces")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                face_customers = result.get('customers', [])
                print(f"✅ Found {len(face_customers)} customers with face data")
                for customer in face_customers[:3]:  # Show first 3
                    print(f"   - {customer.get('full_name')} (ID: {customer.get('id')})")
            else:
                print(f"❌ API returned error: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

def test_javascript_functions():
    """Test JavaScript function integrity"""
    print("\n🔍 Testing JavaScript Function Integrity...")
    
    js_file_path = "static/js/main.js"
    
    try:
        with open(js_file_path, 'r') as f:
            js_content = f.read()
        
        required_functions = [
            'startCamera',
            'capturePhoto', 
            'saveFaceImage',
            'retakePhoto',
            'stopCamera',
            'resetFaceCaptureUI',
            'saveFaceFromUI'
        ]
        
        missing_functions = []
        for func in required_functions:
            if f"function {func}" not in js_content and f"const {func}" not in js_content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"❌ Missing JavaScript functions: {', '.join(missing_functions)}")
        else:
            print("✅ All required JavaScript functions are present")
            
        # Check for common issues
        issues = []
        
        if 'getElementById' in js_content and 'null' not in js_content:
            issues.append("Missing null checks for DOM elements")
            
        if 'getUserMedia' in js_content and 'catch' not in js_content:
            issues.append("Missing error handling for camera access")
            
        if issues:
            print(f"⚠️  Potential issues found: {', '.join(issues)}")
        else:
            print("✅ No obvious JavaScript issues detected")
            
    except FileNotFoundError:
        print(f"❌ JavaScript file not found: {js_file_path}")
    except Exception as e:
        print(f"❌ Error reading JavaScript file: {str(e)}")

def test_template_integrity():
    """Test HTML template integrity"""
    print("\n📄 Testing HTML Template Integrity...")
    
    template_path = "templates/customers.html"
    
    try:
        with open(template_path, 'r') as f:
            html_content = f.read()
        
        required_elements = [
            'id="video"',
            'id="canvas"',
            'id="startCameraBtn"',
            'id="captureBtn"',
            'id="retakeBtn"',
            'id="saveFaceBtn"',
            'id="stopBtn"',
            'id="customerSelect"'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in html_content:
                missing_elements.append(element.split('"')[1])
        
        if missing_elements:
            print(f"❌ Missing HTML elements: {', '.join(missing_elements)}")
        else:
            print("✅ All required HTML elements are present")
            
        # Check for onclick handlers
        onclick_functions = ['capturePhoto()', 'retakePhoto()', 'saveFaceFromUI()', 'stopCamera()']
        missing_handlers = []
        
        for handler in onclick_functions:
            if handler not in html_content:
                missing_handlers.append(handler)
                
        if missing_handlers:
            print(f"⚠️  Missing onclick handlers: {', '.join(missing_handlers)}")
        else:
            print("✅ All onclick handlers are present")
            
    except FileNotFoundError:
        print(f"❌ Template file not found: {template_path}")
    except Exception as e:
        print(f"❌ Error reading template file: {str(e)}")

def test_route_integrity():
    """Test route availability"""
    print("\n🛣️  Testing Route Availability...")
    
    routes_to_test = [
        ('/customers', 'GET'),
        ('/api/customers', 'GET'), 
        ('/api/save_face', 'POST'),
        ('/api/customers_with_faces', 'GET')
    ]
    
    for route, method in routes_to_test:
        print(f"\n📍 Testing {method} {route}")
        try:
            if method == 'GET':
                response = requests.get(f"{BASE_URL}{route}", timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{route}", json={}, timeout=5)
            
            if response.status_code < 500:
                print(f"   ✅ Route accessible (Status: {response.status_code})")
            else:
                print(f"   ❌ Server error (Status: {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection failed - Server may not be running")
        except requests.exceptions.Timeout:
            print(f"   ❌ Request timeout")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive Face Capture System Test")
    print("=" * 60)
    
    # Test order matters - check files first, then server
    test_javascript_functions()
    test_template_integrity()
    test_route_integrity()
    test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("🏁 Face Capture System Test Complete")
    print("\n📋 Summary:")
    print("   - Check all ❌ items above and fix them")
    print("   - Ensure server is running for API tests")
    print("   - Test with real camera in browser")
    print("   - Verify face data is saved in database")

if __name__ == "__main__":
    main()
