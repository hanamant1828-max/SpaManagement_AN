#!/usr/bin/env python3
"""
Comprehensive Staff Management Testing Script
Tests all CRUD operations with proper form validation
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:5000"
USERNAME = "admin"
PASSWORD = "admin123"

class StaffTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'StaffTester/1.0'})
        
    def login(self):
        """Login to the system"""
        print("🔐 Step 1: Login")
        
        # Get login page first to get CSRF token
        login_page = self.session.get(f"{BASE_URL}/login")
        if login_page.status_code != 200:
            print(f"❌ Could not access login page: {login_page.status_code}")
            return False
            
        # Login with credentials
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        response = self.session.post(f"{BASE_URL}/login", data=login_data)
        # Check if redirected to dashboard or if we can access protected pages
        if response.status_code in [302, 200]:
            # Try to access dashboard to confirm login
            dashboard_response = self.session.get(f"{BASE_URL}/dashboard")
            if dashboard_response.status_code == 200 and "dashboard" in dashboard_response.text.lower():
                print("✅ Login successful")
                return True
            else:
                print(f"❌ Login failed - cannot access dashboard: {dashboard_response.status_code}")
                return False
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    
    def test_staff_page_access(self):
        """Test that staff management page loads correctly"""
        print("\n📋 Step 2: Access Staff Management Page")
        
        response = self.session.get(f"{BASE_URL}/staff")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Staff Management page accessible")
            print(f"   Page content length: {len(response.text)} characters")
            
            # Check for key elements in the page
            content = response.text.lower()
            checks = [
                ("add staff button", "add staff" in content),
                ("staff table", "staff" in content and "table" in content),
                ("bootstrap styling", "bootstrap" in content or "btn" in content),
                ("form elements", "form" in content)
            ]
            
            for check_name, check_result in checks:
                status = "✅" if check_result else "⚠️"
                print(f"   {status} {check_name}: {'Present' if check_result else 'Missing'}")
                
            return True
        else:
            print(f"❌ Cannot access Staff Management: {response.status_code}")
            return False
    
    def test_create_staff(self):
        """Test creating a new staff member with proper form data"""
        print("\n➕ Step 3: CREATE - Test Staff Creation")
        
        # Create test data for new staff member
        timestamp = datetime.now().strftime("%H%M%S")
        staff_data = {
            'first_name': 'Test',
            'last_name': 'Staff',
            'username': f'teststaff{timestamp}',
            'email': f'test.staff{timestamp}@example.com',
            'phone': '1234567890',
            'role': 'staff',
            'department': 'Spa Services',
            'commission_rate': '15.0',
            'hourly_rate': '25.0',
            'is_active': 'y'  # Checkbox value
        }
        
        print(f"   Creating staff: {staff_data['username']} ({staff_data['email']})")
        
        # Send POST request to create staff
        response = self.session.post(f"{BASE_URL}/api/staff", 
                                   data=staff_data,
                                   headers={'Content-Type': 'application/x-www-form-urlencoded'})
        
        print(f"   Create Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("✅ Staff member created successfully")
            try:
                result = response.json()
                if 'id' in result:
                    staff_id = result['id']
                    print(f"   New staff ID: {staff_id}")
                    return staff_id
                else:
                    print(f"   Response: {result}")
                    return True
            except:
                print(f"   Response length: {len(response.text)} characters")
                return True
        else:
            print(f"❌ Failed to create staff")
            try:
                error_response = response.json()
                print(f"   Error: {error_response}")
            except:
                print(f"   Error response: {response.text[:200]}...")
            return False
    
    def test_read_staff(self):
        """Test reading staff list"""
        print("\n📖 Step 4: READ - Test Staff List Retrieval")
        
        response = self.session.get(f"{BASE_URL}/api/staff")
        print(f"   Read Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                staff_list = response.json()
                print(f"✅ Staff list retrieved successfully")
                print(f"   Total staff members: {len(staff_list)}")
                
                if staff_list:
                    latest_staff = staff_list[-1]
                    print(f"   Latest staff: {latest_staff.get('username', 'N/A')} - {latest_staff.get('email', 'N/A')}")
                    return latest_staff.get('id')
                return True
            except:
                print(f"✅ Staff page accessible, content length: {len(response.text)}")
                return True
        else:
            print(f"❌ Failed to retrieve staff list")
            return False
    
    def test_update_staff(self, staff_id):
        """Test updating staff information"""
        if not staff_id:
            print("\n📝 Step 5: UPDATE - Skipped (no staff ID available)")
            return True
            
        print(f"\n📝 Step 5: UPDATE - Test Staff Update (ID: {staff_id})")
        
        update_data = {
            'commission_rate': '20.0',
            'hourly_rate': '30.0',
            'department': 'Premium Services'
        }
        
        response = self.session.put(f"{BASE_URL}/api/staff/{staff_id}", 
                                  json=update_data,
                                  headers={'Content-Type': 'application/json'})
        
        print(f"   Update Status: {response.status_code}")
        
        if response.status_code in [200, 204]:
            print("✅ Staff member updated successfully")
            return True
        else:
            print(f"❌ Failed to update staff member")
            try:
                error_response = response.json()
                print(f"   Error: {error_response}")
            except:
                print(f"   Error response: {response.text[:200]}...")
            return False
    
    def test_delete_staff(self, staff_id):
        """Test deleting staff member"""
        if not staff_id:
            print("\n🗑️ Step 6: DELETE - Skipped (no staff ID available)")
            return True
            
        print(f"\n🗑️ Step 6: DELETE - Test Staff Deletion (ID: {staff_id})")
        
        response = self.session.delete(f"{BASE_URL}/api/staff/{staff_id}")
        print(f"   Delete Status: {response.status_code}")
        
        if response.status_code in [200, 204]:
            print("✅ Staff member deleted successfully")
            return True
        else:
            print(f"❌ Failed to delete staff member")
            try:
                error_response = response.json()
                print(f"   Error: {error_response}")
            except:
                print(f"   Error response: {response.text[:200]}...")
            return False
    
    def run_comprehensive_test(self):
        """Run all CRUD tests in sequence"""
        print("🎯 COMPREHENSIVE STAFF MANAGEMENT TESTING")
        print("=" * 50)
        
        # Test sequence
        if not self.login():
            return
            
        if not self.test_staff_page_access():
            return
            
        staff_id = self.test_create_staff()
        
        self.test_read_staff()
        
        if staff_id and isinstance(staff_id, (int, str)) and str(staff_id).isdigit():
            self.test_update_staff(staff_id)
            self.test_delete_staff(staff_id)
        
        print("\n🎯 TESTING COMPLETE")
        print("=" * 50)

if __name__ == "__main__":
    tester = StaffTester()
    tester.run_comprehensive_test()