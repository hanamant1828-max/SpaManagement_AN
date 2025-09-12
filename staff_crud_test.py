#!/usr/bin/env python3
"""
Step-by-Step Staff Management CRUD Testing with Immediate Fixes
"""

import requests
import json
import time
from datetime import datetime

def manual_staff_testing():
    """Manual testing of Staff Management CRUD operations"""
    session = requests.Session()
    base_url = "http://127.0.0.1:5000"
    
    print("🎯 MANUAL STAFF MANAGEMENT TESTING")
    print("=" * 50)
    
    # Step 1: Login
    print("\n🔐 Step 1: Login")
    login_resp = session.post(f"{base_url}/login", data={'username': 'admin', 'password': 'admin123'})
    if login_resp.status_code != 200 or "/login" in login_resp.url:
        print("❌ Login failed")
        return False
    print("✅ Login successful")
    
    # Step 2: Access staff management
    print("\n📋 Step 2: Access Staff Management")
    staff_page_resp = session.get(f"{base_url}/staff")
    print(f"   Status: {staff_page_resp.status_code}")
    if staff_page_resp.status_code == 200:
        print("✅ Staff Management page accessible")
    else:
        print("❌ Cannot access Staff Management")
        return False
    
    # Step 3: Test CREATE - Add new staff
    print("\n➕ Step 3: CREATE - Add new staff member")
    timestamp = int(time.time())
    staff_data = {
        "first_name": f"Test{timestamp}",
        "last_name": "Therapist",
        "email": f"test{timestamp}@example.com",
        "phone": f"555-{timestamp % 10000:04d}",
        "role": "Massage Therapist",
        "department": "Therapy",
        "hire_date": datetime.now().strftime('%Y-%m-%d'),
        "hourly_rate": 30.00,
        "is_active": True
    }
    
    create_resp = session.post(f"{base_url}/api/staff", json=staff_data)
    print(f"   Create Status: {create_resp.status_code}")
    
    if create_resp.status_code == 200:
        result = create_resp.json()
        staff_id = result.get('staff_id') or result.get('id')
        print(f"✅ Staff created successfully (ID: {staff_id})")
    else:
        print(f"❌ Failed to create staff: {create_resp.text[:200]}")
        return False
    
    # Step 4: Test READ - View staff details
    print(f"\n👁️  Step 4: READ - View staff details (ID: {staff_id})")
    read_resp = session.get(f"{base_url}/api/staff/{staff_id}")
    print(f"   Read Status: {read_resp.status_code}")
    
    if read_resp.status_code == 200:
        staff_details = read_resp.json()
        print(f"✅ Staff details retrieved")
        print(f"   Name: {staff_details.get('first_name')} {staff_details.get('last_name')}")
        print(f"   Role: {staff_details.get('role')}")
    else:
        print(f"❌ Failed to read staff details")
    
    # Step 5: Test UPDATE - Edit staff
    print(f"\n✏️  Step 5: UPDATE - Edit staff (ID: {staff_id})")
    update_data = {
        "role": "Senior Massage Therapist",
        "hourly_rate": 40.00
    }
    
    update_resp = session.put(f"{base_url}/api/staff/{staff_id}", json=update_data)
    print(f"   Update Status: {update_resp.status_code}")
    
    if update_resp.status_code == 200:
        print("✅ Staff updated successfully")
    else:
        print(f"❌ Failed to update staff: {update_resp.text[:200]}")
    
    # Step 6: Test DELETE - Remove staff
    print(f"\n🗑️  Step 6: DELETE - Remove staff (ID: {staff_id})")
    delete_resp = session.delete(f"{base_url}/api/staff/{staff_id}")
    print(f"   Delete Status: {delete_resp.status_code}")
    
    if delete_resp.status_code == 200:
        print("✅ Staff deleted successfully")
    else:
        print(f"❌ Failed to delete staff: {delete_resp.text[:200]}")
    
    print("\n✅ STAFF CRUD TESTING COMPLETED")
    return True

if __name__ == "__main__":
    manual_staff_testing()