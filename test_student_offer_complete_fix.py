
#!/usr/bin/env python3
"""
Comprehensive Student Offer Testing - 5-year developer level
Tests all CRUD operations and edge cases
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://0.0.0.0:5000"

def test_student_offer_system():
    """Complete test suite for student offers"""
    
    print("🚀 Starting Student Offer System Test...")
    session = requests.Session()
    
    # Step 1: Login
    print("\n1️⃣ Testing Login...")
    login_data = {'username': 'admin', 'password': 'admin123'}
    login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    
    if login_response.status_code == 200:
        print("✅ Login successful")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    # Step 2: Test Services API
    print("\n2️⃣ Testing Services API...")
    services_response = session.get(f"{BASE_URL}/packages/api/services")
    
    if services_response.status_code == 200:
        services_data = services_response.json()
        if services_data.get('success') and services_data.get('services'):
            print(f"✅ Services API working - Found {len(services_data['services'])} services")
            service_ids = [services_data['services'][0]['id']] if services_data['services'] else []
        else:
            print("❌ Services API returned no data")
            return False
    else:
        print(f"❌ Services API failed: {services_response.status_code}")
        return False
    
    if not service_ids:
        print("❌ No services available for testing")
        return False
    
    # Step 3: Test Student Offer Add Page
    print("\n3️⃣ Testing Student Offer Add Page...")
    add_page_response = session.get(f"{BASE_URL}/student-offers/add")
    
    if add_page_response.status_code == 200:
        print("✅ Student offer add page loads successfully")
    else:
        print(f"❌ Student offer add page failed: {add_page_response.status_code}")
        print(f"Response: {add_page_response.text[:500]}")
        return False
    
    # Step 4: Test Create Student Offer
    print("\n4️⃣ Testing Create Student Offer...")
    today = datetime.now()
    future_date = today + timedelta(days=180)
    
    # Test with packages blueprint endpoint
    offer_data = {
        'service_ids': service_ids,
        'discount_percentage': 25.0,
        'valid_days': 'Mon-Fri',
        'valid_from': today.strftime('%Y-%m-%d'),
        'valid_to': future_date.strftime('%Y-%m-%d'),
        'conditions': 'Valid with Student ID',
        'is_active': True
    }
    
    create_response = session.post(
        f"{BASE_URL}/packages/api/student-offers",
        json=offer_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if create_response.status_code == 200:
        result = create_response.json()
        if result.get('success'):
            offer_id = result.get('offer_id')
            print(f"✅ Student offer created successfully - ID: {offer_id}")
        else:
            print(f"❌ Create failed: {result.get('error', 'Unknown error')}")
            return False
    else:
        print(f"❌ Create request failed: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return False
    
    # Step 5: Test Get Student Offers
    print("\n5️⃣ Testing Get Student Offers...")
    get_response = session.get(f"{BASE_URL}/packages/api/student-offers")
    
    if get_response.status_code == 200:
        offers_data = get_response.json()
        if offers_data.get('success') and offers_data.get('offers'):
            print(f"✅ Get offers successful - Found {len(offers_data['offers'])} offers")
        else:
            print("❌ Get offers returned no data")
            return False
    else:
        print(f"❌ Get offers failed: {get_response.status_code}")
        return False
    
    # Step 6: Test Update Student Offer
    print("\n6️⃣ Testing Update Student Offer...")
    update_data = {
        'service_ids': service_ids,
        'discount_percentage': 30.0,
        'valid_days': 'Mon-Sat',
        'valid_from': today.strftime('%Y-%m-%d'),
        'valid_to': future_date.strftime('%Y-%m-%d'),
        'conditions': 'Updated: Valid with Student ID',
        'is_active': True
    }
    
    update_response = session.put(
        f"{BASE_URL}/packages/api/student-offers/{offer_id}",
        json=update_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if update_response.status_code == 200:
        result = update_response.json()
        if result.get('success'):
            print("✅ Student offer updated successfully")
        else:
            print(f"❌ Update failed: {result.get('error', 'Unknown error')}")
            return False
    else:
        print(f"❌ Update request failed: {update_response.status_code}")
        return False
    
    # Step 7: Test Delete Student Offer
    print("\n7️⃣ Testing Delete Student Offer...")
    delete_response = session.delete(f"{BASE_URL}/packages/api/student-offers/{offer_id}")
    
    if delete_response.status_code == 200:
        result = delete_response.json()
        if result.get('success'):
            print("✅ Student offer deleted successfully")
        else:
            print(f"❌ Delete failed: {result.get('error', 'Unknown error')}")
            return False
    else:
        print(f"❌ Delete request failed: {delete_response.status_code}")
        return False
    
    # Step 8: Test Packages Main Page
    print("\n8️⃣ Testing Packages Main Page...")
    packages_response = session.get(f"{BASE_URL}/packages")
    
    if packages_response.status_code == 200:
        print("✅ Packages main page loads successfully")
    else:
        print(f"❌ Packages main page failed: {packages_response.status_code}")
        return False
    
    print("\n🎉 All Student Offer Tests PASSED!")
    return True

def test_edge_cases():
    """Test edge cases and error handling"""
    
    print("\n🔍 Testing Edge Cases...")
    session = requests.Session()
    
    # Login first
    login_data = {'username': 'admin', 'password': 'admin123'}
    session.post(f"{BASE_URL}/login", data=login_data)
    
    # Test invalid data
    print("\n1️⃣ Testing Invalid Data Handling...")
    
    # Test with missing required fields
    invalid_data = {
        'discount_percentage': 25.0,
        # Missing service_ids
        'valid_days': 'Mon-Fri'
    }
    
    response = session.post(
        f"{BASE_URL}/packages/api/student-offers",
        json=invalid_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200 or not response.json().get('success'):
        print("✅ Invalid data properly rejected")
    else:
        print("❌ Invalid data was accepted")
        return False
    
    # Test with invalid discount percentage
    invalid_discount = {
        'service_ids': [1],
        'discount_percentage': 150.0,  # Invalid - over 100%
        'valid_days': 'Mon-Fri',
        'valid_from': '2025-01-01',
        'valid_to': '2025-06-01'
    }
    
    response = session.post(
        f"{BASE_URL}/packages/api/student-offers",
        json=invalid_discount,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200 or not response.json().get('success'):
        print("✅ Invalid discount properly rejected")
    else:
        print("❌ Invalid discount was accepted")
        return False
    
    print("✅ All edge case tests passed!")
    return True

if __name__ == "__main__":
    print("🧪 Student Offer Complete Fix Test Suite")
    print("=" * 50)
    
    # Run main functionality tests
    main_tests_passed = test_student_offer_system()
    
    # Run edge case tests
    edge_tests_passed = test_edge_cases()
    
    print("\n" + "=" * 50)
    if main_tests_passed and edge_tests_passed:
        print("🎉 ALL TESTS PASSED - Student Offer system is working correctly!")
    else:
        print("❌ SOME TESTS FAILED - Check the output above for details")
    
    print("=" * 50)

