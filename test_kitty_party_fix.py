
#!/usr/bin/env python3
"""
Comprehensive test for Kitty Party functionality after boolean fix
"""

import json
import requests
import time
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_ADMIN_USERNAME = "admin"
TEST_ADMIN_PASSWORD = "admin123"

def login_admin():
    """Login as admin user"""
    print("🔐 Logging in as admin...")
    login_data = {
        'username': TEST_ADMIN_USERNAME,
        'password': TEST_ADMIN_PASSWORD
    }
    
    session = requests.Session()
    response = session.post(f"{BASE_URL}/login", data=login_data)
    
    if response.status_code == 200 and "dashboard" in response.url:
        print("✅ Admin login successful")
        return session
    else:
        print(f"❌ Admin login failed. Status: {response.status_code}")
        print(f"Response URL: {response.url}")
        return None

def test_kitty_party_creation(session):
    """Test creating a kitty party with the fixed boolean handling"""
    print("\n🎉 Testing Kitty Party Creation...")
    
    # Prepare test data
    today = datetime.now()
    future_date = today + timedelta(days=90)
    
    kitty_data = {
        "name": "Test Spa Party",
        "price": "25000.00",
        "after_value": "30000.00",
        "min_guests": "8",
        "valid_from": today.strftime('%Y-%m-%d'),
        "valid_to": future_date.strftime('%Y-%m-%d'),
        "conditions": "Valid with advance booking only",
        "is_active": "on",  # This was causing the error
        "service_ids": [1, 2, 3]  # Assuming these service IDs exist
    }
    
    # Test creating kitty party
    response = session.post(
        f"{BASE_URL}/api/kitty-parties",
        json=kitty_data
    )
    
    print(f"Create Kitty Party Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Kitty party creation successful!")
            print(f"   Party ID: {result.get('party_id')}")
            return result.get('party_id')
        else:
            print(f"❌ Kitty party creation failed: {result.get('error')}")
            return None
    else:
        print(f"❌ Kitty party creation request failed")
        try:
            error_data = response.json()
            print(f"   Error: {error_data}")
        except:
            print(f"   Raw response: {response.text}")
        return None

def test_kitty_party_list(session):
    """Test fetching kitty party list"""
    print("\n📋 Testing Kitty Party List...")
    
    response = session.get(f"{BASE_URL}/api/kitty-parties")
    
    if response.status_code == 200:
        parties = response.json()
        print(f"✅ Successfully fetched {len(parties)} kitty parties")
        
        for party in parties:
            print(f"   - {party['name']}: ₹{party['price']} (Min guests: {party['min_guests']})")
            print(f"     Services: {len(party.get('selected_services', []))} services selected")
            print(f"     Active: {party['is_active']}")
        
        return parties
    else:
        print(f"❌ Failed to fetch kitty parties. Status: {response.status_code}")
        return []

def test_kitty_party_update(session, party_id):
    """Test updating a kitty party"""
    if not party_id:
        print("\n⚠️  Skipping update test - no party ID available")
        return False
    
    print(f"\n✏️  Testing Kitty Party Update (ID: {party_id})...")
    
    update_data = {
        "name": "Updated Test Spa Party",
        "price": "28000.00",
        "after_value": "35000.00",
        "min_guests": "10",
        "conditions": "Updated conditions - Valid with 48-hour advance booking",
        "is_active": "on",  # Test boolean conversion again
        "service_ids": [1, 2]  # Reduce services
    }
    
    response = session.put(
        f"{BASE_URL}/api/kitty-parties/{party_id}",
        json=update_data
    )
    
    print(f"Update Kitty Party Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Kitty party update successful!")
            return True
        else:
            print(f"❌ Kitty party update failed: {result.get('error')}")
            return False
    else:
        print(f"❌ Kitty party update request failed")
        try:
            error_data = response.json()
            print(f"   Error: {error_data}")
        except:
            print(f"   Raw response: {response.text}")
        return False

def test_packages_page_load(session):
    """Test loading the packages page"""
    print("\n📄 Testing Packages Page Load...")
    
    response = session.get(f"{BASE_URL}/packages")
    
    if response.status_code == 200:
        print("✅ Packages page loaded successfully")
        
        # Check if kitty party tab content is present
        if "Kitty Parties" in response.text and "Add Kitty Party" in response.text:
            print("✅ Kitty Party tab content found")
            return True
        else:
            print("⚠️  Kitty Party tab content not found in page")
            return False
    else:
        print(f"❌ Failed to load packages page. Status: {response.status_code}")
        return False

def test_form_submission_formats(session):
    """Test different form submission formats"""
    print("\n🧪 Testing Different Form Submission Formats...")
    
    # Test 1: Form data (like from HTML form)
    form_data = {
        "name": "Form Data Test Party",
        "price": "15000",
        "after_value": "18000",
        "min_guests": "6",
        "conditions": "Test form data submission",
        "is_active": "on",  # HTML checkbox value
        "service_ids": "1"
    }
    
    response = session.post(
        f"{BASE_URL}/api/kitty-parties",
        data=form_data  # Send as form data, not JSON
    )
    
    print(f"Form Data Test Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Form data submission successful!")
        else:
            print(f"❌ Form data submission failed: {result.get('error')}")
    
    # Test 2: JSON with string boolean
    json_data = {
        "name": "JSON Test Party",
        "price": "20000",
        "after_value": "25000", 
        "min_guests": "8",
        "conditions": "Test JSON submission",
        "is_active": "true",  # String boolean
        "service_ids": [1, 2]
    }
    
    response = session.post(
        f"{BASE_URL}/api/kitty-parties",
        json=json_data
    )
    
    print(f"JSON Data Test Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ JSON data submission successful!")
        else:
            print(f"❌ JSON data submission failed: {result.get('error')}")

def run_comprehensive_test():
    """Run all kitty party tests"""
    print("🚀 Starting Comprehensive Kitty Party Test Suite")
    print("=" * 60)
    
    # Login
    session = login_admin()
    if not session:
        print("❌ Cannot proceed without admin session")
        return
    
    # Wait a moment for the session to be fully established
    time.sleep(1)
    
    # Test 1: Load packages page
    test_packages_page_load(session)
    
    # Test 2: Test different form submission formats
    test_form_submission_formats(session)
    
    # Test 3: Create kitty party
    party_id = test_kitty_party_creation(session)
    
    # Test 4: List kitty parties
    parties = test_kitty_party_list(session)
    
    # Test 5: Update kitty party (if creation was successful)
    if party_id:
        test_kitty_party_update(session, party_id)
    
    print("\n" + "=" * 60)
    print("🏁 Kitty Party Test Suite Complete!")
    
    if party_id and len(parties) > 0:
        print("✅ All core functionality appears to be working")
    else:
        print("⚠️  Some issues detected - check the logs above")

if __name__ == "__main__":
    run_comprehensive_test()
