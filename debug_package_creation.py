#!/usr/bin/env python3
"""
Debug package creation process
"""
import requests
import json
import re

def debug_package_creation():
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print("🔍 Debugging Package Creation Process")
    print("=" * 50)
    
    # Login
    login_response = session.get(f"{base_url}/login")
    csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_response.text)
    csrf_token = csrf_match.group(1) if csrf_match else None
    
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrf_token': csrf_token
    }
    
    session.post(f"{base_url}/login", data=login_data)
    
    # Get packages page to extract CSRF token
    packages_response = session.get(f"{base_url}/packages")
    csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', packages_response.text)
    new_csrf_token = csrf_match.group(1) if csrf_match else csrf_token
    
    print(f"CSRF Token: {new_csrf_token[:20]}...")
    
    # Test different form data combinations
    test_cases = [
        {
            'name': 'Basic Package Test',
            'data': {
                'name': 'Test Package 1',
                'description': 'Simple test package',
                'validity_days': '30',
                'total_price': '500.00',
                'discount_percentage': '10',
                'is_active': True,
                'selected_services': '[]',
                'csrf_token': new_csrf_token
            }
        },
        {
            'name': 'Package with Services',
            'data': {
                'name': 'Test Package 2',
                'description': 'Package with services',
                'validity_days': '30',
                'total_price': '500.00',
                'discount_percentage': '10',
                'is_active': True,
                'selected_services': json.dumps([
                    {'service_id': 1, 'sessions': 5, 'discount': 5}
                ]),
                'csrf_token': new_csrf_token
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print("-" * 30)
        
        response = session.post(f"{base_url}/packages/create", data=test_case['data'])
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Check if there are error messages in the response
            if "error" in response.text.lower() or "validation" in response.text.lower():
                # Extract flash messages if any
                flash_matches = re.findall(r'alert-(\w+).*?>(.*?)</div>', response.text, re.DOTALL)
                if flash_matches:
                    print("Flash messages found:")
                    for alert_type, message in flash_matches:
                        print(f"  {alert_type}: {message.strip()}")
                else:
                    print("No specific error messages found")
            else:
                print("Request processed without obvious errors")
        elif response.status_code == 302:
            print("Redirected (likely successful)")
        else:
            print(f"Error: {response.status_code}")
            print(f"Response preview: {response.text[:200]}...")
    
    # Check database for any created packages
    print(f"\n3. Database Check")
    print("-" * 30)
    
    from app import app, db
    from models import Package
    
    with app.app_context():
        packages = Package.query.all()
        print(f"Total packages in database: {len(packages)}")
        
        for package in packages:
            print(f"  - {package.name} (ID: {package.id}, Active: {package.is_active})")

if __name__ == "__main__":
    debug_package_creation()