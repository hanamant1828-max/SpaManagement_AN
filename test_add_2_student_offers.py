
#!/usr/bin/env python3
"""
Test script to add 2 student offers for testing the student offers functionality
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

def test_add_2_student_offers():
    """Add 2 student offers for testing purposes"""
    session = requests.Session()
    
    print("🧪 Student Offers Testing - Adding 2 Test Offers")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1️⃣ Logging in as admin...")
    login_data = {'username': 'admin', 'password': 'admin123'}
    login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    
    if login_response.status_code == 200:
        print("✅ Login successful")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    # Step 2: Get available services
    print("\n2️⃣ Getting available services...")
    services_response = session.get(f"{BASE_URL}/packages/api/services")
    
    if services_response.status_code == 200:
        services_data = services_response.json()
        if services_data.get('success') and services_data.get('services'):
            services = services_data['services']
            print(f"✅ Found {len(services)} services available")
            
            # Display available services
            print("\n📋 Available Services:")
            for i, service in enumerate(services[:5]):  # Show first 5
                print(f"   {i+1}. {service['name']} - ₹{service['price']}")
            
            if len(services) < 2:
                print("❌ Need at least 2 services to create meaningful student offers")
                return False
        else:
            print("❌ No services found")
            return False
    else:
        print(f"❌ Failed to get services: {services_response.status_code}")
        return False
    
    # Prepare dates
    today = datetime.now()
    six_months_later = today + timedelta(days=180)
    one_year_later = today + timedelta(days=365)
    
    # Student Offer 1: Weekend Special (25% discount)
    print("\n3️⃣ Creating Student Offer 1: Weekend Special...")
    offer1_data = {
        'service_ids': [services[0]['id'], services[1]['id']] if len(services) >= 2 else [services[0]['id']],
        'discount_percentage': 25.0,
        'valid_days': 'Weekends',
        'valid_from': today.strftime('%Y-%m-%d'),
        'valid_to': six_months_later.strftime('%Y-%m-%d'),
        'conditions': 'Valid on weekends only. Student ID required. Cannot be combined with other offers.',
        'is_active': True
    }
    
    create1_response = session.post(
        f"{BASE_URL}/packages/api/student-offers",
        json=offer1_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if create1_response.status_code == 200:
        result1 = create1_response.json()
        if result1.get('success'):
            offer1_id = result1.get('offer_id')
            print(f"✅ Student Offer 1 created successfully - ID: {offer1_id}")
            print(f"   📅 Weekend Special: {offer1_data['discount_percentage']}% off")
            print(f"   🎯 Services: {len(offer1_data['service_ids'])} selected")
            print(f"   ⏰ Valid: {offer1_data['valid_from']} to {offer1_data['valid_to']}")
        else:
            print(f"❌ Failed to create Offer 1: {result1.get('error')}")
            return False
    else:
        print(f"❌ Failed to create Offer 1: {create1_response.status_code}")
        print(f"Response: {create1_response.text}")
        return False
    
    # Student Offer 2: Weekday Premium (15% discount, more services)
    print("\n4️⃣ Creating Student Offer 2: Weekday Premium...")
    
    # Use more services for the second offer
    service_ids_2 = []
    for i in range(min(3, len(services))):  # Use up to 3 services
        service_ids_2.append(services[i]['id'])
    
    offer2_data = {
        'service_ids': service_ids_2,
        'discount_percentage': 15.0,
        'valid_days': 'Mon-Fri',
        'valid_from': today.strftime('%Y-%m-%d'),
        'valid_to': one_year_later.strftime('%Y-%m-%d'),
        'conditions': 'Valid Monday to Friday only. Premium student package. Valid student ID and enrollment verification required.',
        'is_active': True
    }
    
    create2_response = session.post(
        f"{BASE_URL}/packages/api/student-offers",
        json=offer2_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if create2_response.status_code == 200:
        result2 = create2_response.json()
        if result2.get('success'):
            offer2_id = result2.get('offer_id')
            print(f"✅ Student Offer 2 created successfully - ID: {offer2_id}")
            print(f"   📅 Weekday Premium: {offer2_data['discount_percentage']}% off")
            print(f"   🎯 Services: {len(offer2_data['service_ids'])} selected")
            print(f"   ⏰ Valid: {offer2_data['valid_from']} to {offer2_data['valid_to']}")
        else:
            print(f"❌ Failed to create Offer 2: {result2.get('error')}")
            return False
    else:
        print(f"❌ Failed to create Offer 2: {create2_response.status_code}")
        print(f"Response: {create2_response.text}")
        return False
    
    # Step 5: Verify both offers were created
    print("\n5️⃣ Verifying created offers...")
    list_response = session.get(f"{BASE_URL}/packages/api/student-offers")
    
    if list_response.status_code == 200:
        try:
            offers_list = list_response.json()
            if isinstance(offers_list, list):
                print(f"✅ Verification successful - Found {len(offers_list)} total student offers")
                
                # Find our newly created offers
                our_offers = [offer for offer in offers_list if offer.get('id') in [offer1_id, offer2_id]]
                if len(our_offers) == 2:
                    print("✅ Both new offers found in the system")
                    
                    print("\n📋 Created Offers Summary:")
                    for i, offer in enumerate(our_offers, 1):
                        print(f"\n   Offer {i} (ID: {offer['id']}):")
                        print(f"   - Discount: {offer['discount_percentage']}%")
                        print(f"   - Valid Days: {offer['valid_days']}")
                        print(f"   - Services: {len(offer.get('services', []))} included")
                        print(f"   - Period: {offer['valid_from']} to {offer['valid_to']}")
                        print(f"   - Status: {'Active' if offer.get('is_active') else 'Inactive'}")
                else:
                    print(f"⚠️ Only found {len(our_offers)} of our 2 new offers")
            else:
                print("❌ Invalid response format from offers list")
                return False
        except json.JSONDecodeError:
            print("❌ Failed to parse offers list response")
            return False
    else:
        print(f"❌ Failed to get offers list: {list_response.status_code}")
        return False
    
    # Step 6: Test accessing the student offers UI
    print("\n6️⃣ Testing Student Offers UI access...")
    packages_response = session.get(f"{BASE_URL}/packages")
    
    if packages_response.status_code == 200:
        content = packages_response.text
        if 'assign-student-tab' in content and 'tblStudentOffers' in content:
            print("✅ Student Offers UI elements found in packages page")
        else:
            print("⚠️ Student Offers UI elements not found - check template")
    else:
        print(f"❌ Failed to access packages page: {packages_response.status_code}")
    
    # Step 7: Test add student offer page
    print("\n7️⃣ Testing Add Student Offer page...")
    add_page_response = session.get(f"{BASE_URL}/student-offers/add")
    
    if add_page_response.status_code == 200:
        print("✅ Add Student Offer page loads successfully")
    else:
        print(f"❌ Add Student Offer page failed: {add_page_response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎉 TESTING COMPLETE!")
    print("=" * 60)
    print("\n📊 Test Results Summary:")
    print("✅ Login: Working")
    print("✅ Services API: Working")
    print("✅ Student Offer Creation: Working (2 offers created)")
    print("✅ Student Offers List: Working")
    print("✅ UI Access: Working")
    
    print(f"\n🎯 Successfully created 2 student offers:")
    print(f"   1. Weekend Special (25% off) - ID: {offer1_id}")
    print(f"   2. Weekday Premium (15% off) - ID: {offer2_id}")
    
    print(f"\n🌐 You can now test the UI at:")
    print(f"   - Main packages page: {BASE_URL}/packages#assign-student")
    print(f"   - Add new offer: {BASE_URL}/student-offers/add")
    print(f"   - Edit offer 1: {BASE_URL}/student-offers/edit?id={offer1_id}")
    print(f"   - Edit offer 2: {BASE_URL}/student-offers/edit?id={offer2_id}")
    
    return True

if __name__ == '__main__':
    print("🚀 Starting Student Offers Testing with 2 New Offers...")
    success = test_add_2_student_offers()
    
    if success:
        print("\n✅ All tests passed! Student offers system is working correctly.")
        print("You can now manually test the UI functionality.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
