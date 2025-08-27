#!/usr/bin/env python3
"""
Simple package creation test without external dependencies
"""
import requests
import json
import re

def test_package_creation():
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print("🧪 Testing Package Creation Functionality")
    print("=" * 50)
    
    # Step 1: Get login page and extract CSRF token
    print("1. Getting login page...")
    login_response = session.get(f"{base_url}/login")
    print(f"   Status: {login_response.status_code}")
    
    # Extract CSRF token using regex
    csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_response.text)
    csrf_token = csrf_match.group(1) if csrf_match else None
    
    if csrf_token:
        print(f"   ✓ CSRF token extracted: {csrf_token[:20]}...")
    else:
        print("   ⚠️  No CSRF token found")
        return False
    
    # Step 2: Login
    print("2. Attempting login...")
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrf_token': csrf_token
    }
    
    login_result = session.post(f"{base_url}/login", data=login_data)
    print(f"   Status: {login_result.status_code}")
    
    if login_result.status_code == 200 and "Please sign in" in login_result.text:
        print("   ❌ Login failed - still on login page")
        return False
    elif login_result.status_code in [302, 200]:
        print("   ✓ Login successful")
    
    # Step 3: Access packages page
    print("3. Accessing packages page...")
    packages_response = session.get(f"{base_url}/packages")
    print(f"   Status: {packages_response.status_code}")
    
    if packages_response.status_code == 200:
        print("   ✓ Packages page accessible")
        
        # Check for package creation elements
        if "Create New Package" in packages_response.text:
            print("   ✓ Package creation button found")
        if "addPackageModal" in packages_response.text:
            print("   ✓ Package creation modal found")
        if "service-selection" in packages_response.text:
            print("   ✓ Service selection interface found")
    else:
        print(f"   ❌ Cannot access packages page")
        return False
    
    # Step 4: Extract new CSRF token from packages page
    csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', packages_response.text)
    new_csrf_token = csrf_match.group(1) if csrf_match else csrf_token
    
    # Step 5: Test package creation
    print("4. Testing package creation...")
    package_data = {
        'name': 'Test Package - Automated',
        'description': 'Test package created by automation',
        'validity_days': '30',
        'total_price': '500.00',
        'discount_percentage': '10',
        'is_active': 'y',
        'selected_services': json.dumps([
            {'service_id': 1, 'sessions': 5, 'discount': 5},
            {'service_id': 2, 'sessions': 3, 'discount': 10}
        ]),
        'csrf_token': new_csrf_token
    }
    
    create_response = session.post(f"{base_url}/packages/create", data=package_data)
    print(f"   Status: {create_response.status_code}")
    
    if create_response.status_code == 200:
        print("   ✓ Package creation request processed")
        if "error" in create_response.text.lower():
            print("   ⚠️  Possible error in response")
        else:
            print("   ✓ No obvious errors in response")
    elif create_response.status_code == 302:
        print("   ✓ Package creation successful (redirected)")
    else:
        print(f"   ❌ Package creation failed")
        print(f"   Response preview: {create_response.text[:200]}...")
        return False
    
    # Step 6: Verify package was created
    print("5. Verifying package creation...")
    verify_response = session.get(f"{base_url}/packages")
    
    if "Test Package - Automated" in verify_response.text:
        print("   ✓ Package found in the list")
        return True
    else:
        print("   ⚠️  Package not found in list (may still be created)")
        # Check database directly
        from app import app, db
        from models import Package
        
        with app.app_context():
            test_package = Package.query.filter_by(name='Test Package - Automated').first()
            if test_package:
                print("   ✓ Package confirmed in database")
                return True
            else:
                print("   ❌ Package not found in database")
                return False

if __name__ == "__main__":
    success = test_package_creation()
    
    if success:
        print("\n🎉 Package creation test PASSED!")
        print("The package insertion functionality is working correctly.")
    else:
        print("\n❌ Package creation test FAILED!")
        print("There may be an issue with the package insertion process.")