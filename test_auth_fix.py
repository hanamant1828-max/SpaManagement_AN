
#!/usr/bin/env python3

import requests
import sys

def test_authentication():
    base_url = "http://127.0.0.1:5000"
    
    print("🔧 Testing Authentication Fixes...")
    
    # Test API endpoints that should work without login
    endpoints = [
        '/api/services',
        '/api/staff'
    ]
    
    session = requests.Session()
    
    for endpoint in endpoints:
        try:
            response = session.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                print(f"✅ {endpoint} - Working correctly")
            elif response.status_code == 302:
                print(f"❌ {endpoint} - Still redirecting to login")
            else:
                print(f"⚠️  {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    # Test login functionality
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        if response.status_code == 302:
            print("✅ Login endpoint - Working correctly")
        else:
            print(f"❌ Login endpoint - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Login test failed: {e}")

if __name__ == "__main__":
    test_authentication()
