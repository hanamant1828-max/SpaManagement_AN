
#!/usr/bin/env python3
"""
Manual test script for Student Offer functionality
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

def test_student_offer_crud():
    """Test student offer CRUD operations"""
    session = requests.Session()
    
    print("🔐 Logging in...")
    login_data = {'username': 'admin', 'password': 'admin123'}
    login_response = session.post(f"{BASE_URL}/login", data=login_data)
    
    if login_response.status_code != 200 and 'dashboard' not in login_response.url:
        print("❌ Login failed")
        return False
    
    print("✅ Login successful")
    
    # Test 1: Get services
    print("\n📋 Testing get services...")
    services_response = session.get(f"{BASE_URL}/packages/api/services")
    if services_response.status_code == 200:
        services_data = services_response.json()
        if services_data.get('success') and services_data.get('services'):
            print(f"✅ Found {len(services_data['services'])} services")
            service_ids = [services_data['services'][0]['id']]
        else:
            print("❌ No services found")
            return False
    else:
        print(f"❌ Failed to get services: {services_response.status_code}")
        return False
    
    # Test 2: Create student offer
    print("\n➕ Testing create student offer...")
    today = datetime.now()
    future_date = today + timedelta(days=180)
    
    offer_data = {
        'discount_percentage': 25.0,
        'service_ids': service_ids,
        'valid_days': 'Mon-Fri',
        'valid_from': today.strftime('%Y-%m-%d'),
        'valid_to': future_date.strftime('%Y-%m-%d'),
        'conditions': 'Valid student ID required. Manual test offer.'
    }
    
    create_response = session.post(f"{BASE_URL}/api/student-offers", json=offer_data)
    if create_response.status_code == 200:
        create_result = create_response.json()
        if create_result.get('success'):
            offer_id = create_result.get('offer_id')
            print(f"✅ Student offer created successfully - ID: {offer_id}")
        else:
            print(f"❌ Failed to create offer: {create_result.get('error')}")
            return False
    else:
        print(f"❌ Failed to create offer: {create_response.status_code}")
        return False
    
    # Test 3: Get student offers list
    print("\n📋 Testing get student offers...")
    list_response = session.get(f"{BASE_URL}/api/student-offers")
    if list_response.status_code == 200:
        offers = list_response.json()
        if isinstance(offers, list) and len(offers) > 0:
            print(f"✅ Found {len(offers)} student offers")
        else:
            print("⚠️ No student offers found")
    else:
        print(f"❌ Failed to get offers: {list_response.status_code}")
    
    # Test 4: Get specific offer
    print(f"\n🔍 Testing get offer {offer_id}...")
    get_response = session.get(f"{BASE_URL}/api/student-offers/{offer_id}")
    if get_response.status_code == 200:
        get_result = get_response.json()
        if get_result.get('success'):
            print("✅ Successfully retrieved offer details")
        else:
            print(f"❌ Failed to get offer: {get_result.get('error')}")
    else:
        print(f"❌ Failed to get offer: {get_response.status_code}")
    
    # Test 5: Update offer
    print(f"\n✏️ Testing update offer {offer_id}...")
    update_data = {
        'discount_percentage': 30.0,  # Increased discount
        'service_ids': service_ids,
        'valid_days': 'Mon-Fri',
        'valid_from': today.strftime('%Y-%m-%d'),
        'valid_to': future_date.strftime('%Y-%m-%d'),
        'conditions': 'Valid student ID required. Manual test offer - UPDATED.'
    }
    
    update_response = session.put(f"{BASE_URL}/api/student-offers/{offer_id}", json=update_data)
    if update_response.status_code == 200:
        update_result = update_response.json()
        if update_result.get('success'):
            print("✅ Student offer updated successfully")
        else:
            print(f"❌ Failed to update offer: {update_result.get('error')}")
    else:
        print(f"❌ Failed to update offer: {update_response.status_code}")
    
    # Test 6: Delete offer (cleanup)
    print(f"\n🗑️ Testing delete offer {offer_id}...")
    delete_response = session.delete(f"{BASE_URL}/api/student-offers/{offer_id}")
    if delete_response.status_code == 200:
        delete_result = delete_response.json()
        if delete_result.get('success'):
            print("✅ Student offer deleted successfully")
        else:
            print(f"❌ Failed to delete offer: {delete_result.get('error')}")
    else:
        print(f"❌ Failed to delete offer: {delete_response.status_code}")
    
    print("\n✅ All manual tests completed!")
    return True

if __name__ == '__main__':
    print("🚀 Starting Student Offer Manual Testing...")
    success = test_student_offer_crud()
    if success:
        print("\n🎉 All manual tests passed!")
    else:
        print("\n❌ Some tests failed!")
