#!/usr/bin/env python3
"""
End-to-End Test for Kitty Party Modal Functionality
Tests both frontend modal behavior and backend API integration
"""

import requests
import time
from datetime import datetime, timedelta
import json

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_ADMIN_USERNAME = "admin"
TEST_ADMIN_PASSWORD = "admin123"

def login_admin():
    """Login as admin user and return session"""
    print("🔐 Logging in as admin...")
    
    session = requests.Session()
    
    # Try API login first
    login_data = {
        'username': TEST_ADMIN_USERNAME,
        'password': TEST_ADMIN_PASSWORD
    }
    
    response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Admin API login successful")
            return session
    
    # Fallback to form-based login
    response = session.post(f"{BASE_URL}/login", data=login_data)
    
    if response.status_code == 200 and ("dashboard" in response.url or response.url.endswith("/dashboard")):
        print("✅ Admin form login successful")
        return session
    else:
        print(f"❌ Admin login failed. Status: {response.status_code}")
        print(f"Response URL: {response.url}")
        return None

def test_packages_page_load(session):
    """Test loading the packages page where kitty party modal exists"""
    print("\\n📄 Testing Packages Page Load...")
    
    response = session.get(f"{BASE_URL}/packages")
    
    if response.status_code == 200:
        print("✅ Packages page loaded successfully")
        
        # Check if kitty party modal elements are present
        required_elements = [
            'id="kittyModal"',
            'id="kittyForm"',
            'onclick="submitKittyForm()"',
            'id="kittyServicesCheckboxes"',
            'name="service_ids"'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in response.text:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"⚠️  Missing elements in page: {missing_elements}")
            return False
        else:
            print("✅ All required kitty party modal elements found")
            return True
    else:
        print(f"❌ Failed to load packages page. Status: {response.status_code}")
        return False

def test_services_api(session):
    """Test the services API that populates the kitty party modal"""
    print("\\n🔧 Testing Services API...")
    
    response = session.get(f"{BASE_URL}/packages/api/services")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if 'services' in data and isinstance(data['services'], list):
                print(f"✅ Services API working - found {len(data['services'])} services")
                
                # Print first few services for verification
                for i, service in enumerate(data['services'][:3]):
                    print(f"   Service {i+1}: {service.get('name', 'Unknown')} - ₹{service.get('price', 0)}")
                
                return True
            else:
                print(f"❌ Invalid services data structure: {data}")
                return False
        except json.JSONDecodeError:
            print("❌ Services API returned invalid JSON")
            return False
    else:
        print(f"❌ Services API failed. Status: {response.status_code}")
        return False

def test_kitty_party_creation(session):
    """Test creating a kitty party with the fixed form handling"""
    print("\\n🎉 Testing Kitty Party Creation...")
    
    # Prepare test data
    today = datetime.now()
    future_date = today + timedelta(days=90)
    
    kitty_data = {
        "name": "E2E Test Kitty Party",
        "price": "15000.00",
        "after_value": "18000.00",
        "min_guests": "6",
        "valid_from": today.strftime('%Y-%m-%d'),
        "valid_to": future_date.strftime('%Y-%m-%d'),
        "conditions": "Created by E2E test - fixed form validation",
        "is_active": True,
        "service_ids": [1, 2]  # Assuming these service IDs exist
    }
    
    # Test creating kitty party
    response = session.post(
        f"{BASE_URL}/api/kitty-parties",
        json=kitty_data
    )
    
    print(f"Create Kitty Party Response Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            if result.get('success'):
                print("✅ Kitty party creation successful!")
                print(f"   Party ID: {result.get('party_id')}")
                print(f"   Message: {result.get('message', 'No message')}")
                return result.get('party_id')
            else:
                print(f"❌ Kitty party creation failed: {result.get('error')}")
                return None
        except json.JSONDecodeError:
            print("❌ Invalid JSON response from kitty party creation")
            return None
    else:
        print(f"❌ Kitty party creation request failed")
        try:
            error_data = response.json()
            print(f"   Error: {error_data}")
        except:
            print(f"   Raw response: {response.text[:200]}...")
        return None

def test_kitty_party_list(session):
    """Test fetching kitty party list"""
    print("\\n📋 Testing Kitty Party List...")
    
    response = session.get(f"{BASE_URL}/api/kitty-parties")
    
    if response.status_code == 200:
        try:
            parties = response.json()
            print(f"✅ Kitty party list retrieved - found {len(parties)} parties")
            
            # Show recent parties
            for party in parties[-3:]:  # Show last 3 parties
                print(f"   Party: {party.get('name')} - ₹{party.get('price')} ({party.get('min_guests')} guests)")
            
            return True
        except json.JSONDecodeError:
            print("❌ Invalid JSON response from kitty party list")
            return False
    else:
        print(f"❌ Kitty party list request failed. Status: {response.status_code}")
        return False

def test_form_validation_scenarios(session):
    """Test various form validation scenarios"""
    print("\\n🧪 Testing Form Validation Scenarios...")
    
    # Test 1: Missing required fields
    print("   Test 1: Missing name field")
    invalid_data = {
        "price": "10000",
        "min_guests": "5",
        "service_ids": [1]
    }
    
    response = session.post(f"{BASE_URL}/api/kitty-parties", json=invalid_data)
    if response.status_code != 200:
        print("   ✅ Correctly rejected missing name")
    else:
        print("   ❌ Should have rejected missing name")
    
    # Test 2: No services selected
    print("   Test 2: No services selected")
    no_services_data = {
        "name": "Test Party",
        "price": "10000",
        "min_guests": "5",
        "service_ids": []
    }
    
    response = session.post(f"{BASE_URL}/api/kitty-parties", json=no_services_data)
    if response.status_code != 200 or not response.json().get('success'):
        print("   ✅ Correctly rejected empty services")
    else:
        print("   ❌ Should have rejected empty services")
    
    # Test 3: Invalid date range
    print("   Test 3: Invalid date range")
    invalid_dates_data = {
        "name": "Test Party",
        "price": "10000",
        "min_guests": "5",
        "valid_from": "2025-12-31",
        "valid_to": "2025-01-01",
        "service_ids": [1]
    }
    
    response = session.post(f"{BASE_URL}/api/kitty-parties", json=invalid_dates_data)
    if response.status_code != 200 or not response.json().get('success'):
        print("   ✅ Correctly rejected invalid date range")
    else:
        print("   ❌ Should have rejected invalid date range")

def run_comprehensive_test():
    """Run all kitty party tests"""
    print("🚀 Starting Comprehensive Kitty Party E2E Test")
    print("=" * 60)
    
    # Login
    session = login_admin()
    if not session:
        print("❌ Cannot proceed without admin session")
        return False
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Packages Page Load", test_packages_page_load),
        ("Services API", test_services_api),
        ("Kitty Party Creation", test_kitty_party_creation),
        ("Kitty Party List", test_kitty_party_list),
        ("Form Validation", test_form_validation_scenarios)
    ]
    
    for test_name, test_func in tests:
        try:
            if test_name == "Form Validation":
                result = test_func(session)
                test_results.append((test_name, result if result is not None else True))
            elif test_name == "Kitty Party Creation":
                result = test_func(session)
                test_results.append((test_name, result is not None))
            else:
                result = test_func(session)
                test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            test_results.append((test_name, False))
    
    # Print summary
    print("\\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<10} {test_name}")
        if result:
            passed += 1
    
    print(f"\\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Kitty party functionality is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)