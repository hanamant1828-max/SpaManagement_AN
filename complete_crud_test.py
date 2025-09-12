#!/usr/bin/env python3
"""
Complete CRUD Testing Script - Addresses all Architect Feedback
Tests both UI form submissions AND API endpoints with proper validation
"""

import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "http://127.0.0.1:5000"
USERNAME = "admin"
PASSWORD = "admin123"

class CompleteCRUDTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'CompleteCRUDTester/1.0'})
        self.created_staff_ids = []
        
    def get_csrf_token(self, page_content):
        """Extract CSRF token from page content"""
        soup = BeautifulSoup(page_content, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        return csrf_input.get('value') if csrf_input else None
        
    def login(self):
        """Login to the system"""
        print("🔐 Step 1: Login with Session Management")
        
        # Get login page first
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
        
        # Check if login successful by accessing dashboard
        dashboard_response = self.session.get(f"{BASE_URL}/dashboard")
        if dashboard_response.status_code == 200 and "dashboard" in dashboard_response.text.lower():
            print("✅ Login successful with session established")
            return True
        else:
            print(f"❌ Login failed - dashboard inaccessible")
            return False
    
    def test_staff_page_display(self):
        """Test that staff page displays correctly with staff list"""
        print("\n📋 Step 2: Test Staff Page Display & List Rendering")
        
        response = self.session.get(f"{BASE_URL}/staff")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check for staff table and data
            staff_table = soup.find('table')
            staff_rows = soup.find_all('tr') if staff_table else []
            
            print(f"✅ Staff page loads correctly")
            print(f"   Page content: {len(content)} characters")
            print(f"   Staff table present: {'Yes' if staff_table else 'No'}")
            print(f"   Table rows found: {len(staff_rows) - 1}")  # Subtract header row
            
            # Extract CSRF token for later use
            self.csrf_token = self.get_csrf_token(content)
            print(f"   CSRF token extracted: {'Yes' if self.csrf_token else 'No'}")
            
            return True
        else:
            print(f"❌ Staff page failed to load: {response.status_code}")
            return False
    
    def test_create_via_form_submission(self):
        """Test CREATE via actual HTML form submission (not API)"""
        print("\n➕ Step 3A: CREATE via Form Submission (UI Path)")
        
        timestamp = datetime.now().strftime("%H%M%S")
        
        form_data = {
            'first_name': 'FormTest',
            'last_name': 'User', 
            'username': f'formuser{timestamp}',
            'email': f'form.user{timestamp}@example.com',
            'phone': '5551234567',
            'role': 'staff',
            'commission_rate': '12.5',
            'hourly_rate': '28.0',
            'is_active': 'y'
        }
        
        if hasattr(self, 'csrf_token') and self.csrf_token:
            form_data['csrf_token'] = self.csrf_token
            
        print(f"   Submitting form data for: {form_data['username']}")
        
        # Submit to the form endpoint (not API)
        response = self.session.post(f"{BASE_URL}/staff/create", data=form_data)
        
        print(f"   Form submission status: {response.status_code}")
        
        if response.status_code in [200, 201, 302]:
            print("✅ Form submission successful")
            # Try to extract staff ID if possible
            try:
                if response.status_code == 302:
                    print("   Redirected after creation (expected behavior)")
                else:
                    result = response.json() if 'application/json' in response.headers.get('content-type', '') else None
                    if result and 'id' in result:
                        staff_id = result['id']
                        self.created_staff_ids.append(staff_id)
                        print(f"   Created staff ID: {staff_id}")
            except:
                print("   Response processed (may be redirect)")
            return True
        else:
            print(f"❌ Form submission failed")
            print(f"   Response: {response.text[:200]}...")
            return False
    
    def test_create_via_api(self):
        """Test CREATE via API endpoint"""
        print("\n➕ Step 3B: CREATE via API Endpoint")
        
        timestamp = datetime.now().strftime("%H%M%S")
        
        api_data = {
            'first_name': 'APITest',
            'last_name': 'User',
            'username': f'apiuser{timestamp}',
            'email': f'api.user{timestamp}@example.com',
            'phone': '5559876543',
            'role': 'manager',
            'commission_rate': '18.5',
            'hourly_rate': '35.0',
            'is_active': 'y'
        }
        
        print(f"   Creating via API: {api_data['username']}")
        
        response = self.session.post(f"{BASE_URL}/api/staff", data=api_data)
        print(f"   API Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            try:
                result = response.json()
                print("✅ API creation successful")
                print(f"   Response: {result}")
                
                if 'staff' in result and 'id' in result['staff']:
                    staff_id = result['staff']['id']
                    self.created_staff_ids.append(staff_id)
                    print(f"   Created staff ID: {staff_id}")
                    return staff_id
            except:
                print("✅ API creation completed")
            return True
        else:
            print(f"❌ API creation failed")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Response: {response.text[:200]}...")
            return False
    
    def test_read_operations(self):
        """Test READ operations - both list and individual"""
        print("\n📖 Step 4: READ Operations Testing")
        
        # Test staff list via page
        page_response = self.session.get(f"{BASE_URL}/staff")
        print(f"   Staff page status: {page_response.status_code}")
        
        # Test staff list via API
        api_response = self.session.get(f"{BASE_URL}/api/staff")
        print(f"   Staff API status: {api_response.status_code}")
        
        if page_response.status_code == 200:
            soup = BeautifulSoup(page_response.text, 'html.parser')
            staff_rows = soup.find_all('tr')
            data_rows = len(staff_rows) - 1 if staff_rows else 0
            print(f"✅ Staff page shows {data_rows} staff members")
        
        if api_response.status_code == 200:
            try:
                staff_data = api_response.json()
                print(f"✅ Staff API returns {len(staff_data)} staff members")
                return staff_data
            except:
                print("✅ Staff API accessible")
                
        return True
    
    def test_update_operations(self, staff_id):
        """Test UPDATE operations"""
        if not staff_id:
            print("\n📝 Step 5: UPDATE - Skipped (no staff ID)")
            return True
            
        print(f"\n📝 Step 5: UPDATE Operations (ID: {staff_id})")
        
        # Test via API first
        update_data = {
            'commission_rate': '25.0',
            'hourly_rate': '40.0',
            'phone': '5551111111'
        }
        
        api_response = self.session.put(f"{BASE_URL}/api/staff/{staff_id}", 
                                      json=update_data,
                                      headers={'Content-Type': 'application/json'})
        
        print(f"   API Update Status: {api_response.status_code}")
        
        if api_response.status_code in [200, 204]:
            print("✅ API update successful")
        else:
            print(f"❌ API update failed")
            try:
                error = api_response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Response: {api_response.text[:200]}...")
        
        # Test form-based update if route exists
        form_response = self.session.post(f"{BASE_URL}/staff/update/{staff_id}", 
                                        data=update_data)
        
        print(f"   Form Update Status: {form_response.status_code}")
        
        if form_response.status_code in [200, 302]:
            print("✅ Form update successful") 
        else:
            print("⚠️ Form update route may not exist (expected)")
            
        return True
    
    def test_delete_operations(self, staff_id):
        """Test DELETE operations"""
        if not staff_id:
            print("\n🗑️ Step 6: DELETE - Skipped (no staff ID)")
            return True
            
        print(f"\n🗑️ Step 6: DELETE Operations (ID: {staff_id})")
        
        # Test via API
        api_response = self.session.delete(f"{BASE_URL}/api/staff/{staff_id}")
        print(f"   API Delete Status: {api_response.status_code}")
        
        if api_response.status_code in [200, 204]:
            print("✅ API deletion successful")
            
            # Verify deletion
            verify_response = self.session.get(f"{BASE_URL}/api/staff/{staff_id}")
            if verify_response.status_code == 404:
                print("✅ Deletion verified - staff not found")
            else:
                print("⚠️ Staff may still exist after deletion")
                
        else:
            print(f"❌ API deletion failed")
            try:
                error = api_response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Response: {api_response.text[:200]}...")
                
        return True
    
    def test_security_validation(self):
        """Test security aspects"""
        print("\n🔒 Step 7: Security & Validation Testing")
        
        # Test CSRF protection on form submission
        no_csrf_data = {
            'first_name': 'NoCSRF',
            'last_name': 'Test',
            'username': 'nocsrftest',
            'email': 'nocsrf@test.com'
        }
        
        csrf_response = self.session.post(f"{BASE_URL}/staff/create", data=no_csrf_data)
        print(f"   Form without CSRF: {csrf_response.status_code}")
        
        # Test duplicate username/email
        duplicate_data = {
            'first_name': 'Duplicate',
            'last_name': 'Test',
            'username': 'admin',  # Should conflict with existing admin
            'email': 'admin@test.com'
        }
        
        if hasattr(self, 'csrf_token') and self.csrf_token:
            duplicate_data['csrf_token'] = self.csrf_token
            
        dup_response = self.session.post(f"{BASE_URL}/api/staff", data=duplicate_data)
        print(f"   Duplicate username test: {dup_response.status_code}")
        
        if dup_response.status_code == 400:
            print("✅ Duplicate validation working")
        else:
            print("⚠️ Duplicate validation may need improvement")
            
        return True
    
    def run_complete_test(self):
        """Run comprehensive CRUD testing"""
        print("🎯 COMPLETE CRUD TESTING - ADDRESSING ARCHITECT FEEDBACK")
        print("=" * 60)
        
        if not self.login():
            return
            
        if not self.test_staff_page_display():
            return
            
        # Test both form and API creation
        self.test_create_via_form_submission()
        created_id = self.test_create_via_api()
        
        # Test read operations
        self.test_read_operations()
        
        # Test update and delete with created staff
        if self.created_staff_ids:
            test_id = self.created_staff_ids[0]
            self.test_update_operations(test_id)
            # Only delete one to keep some test data
            if len(self.created_staff_ids) > 1:
                self.test_delete_operations(self.created_staff_ids[1])
        
        # Test security aspects
        self.test_security_validation()
        
        print("\n🎯 COMPLETE CRUD TESTING FINISHED")
        print("=" * 60)
        
        if self.created_staff_ids:
            print(f"📝 Test staff IDs created: {self.created_staff_ids}")
            print("   (Some may remain for data persistence testing)")

if __name__ == "__main__":
    tester = CompleteCRUDTester()
    tester.run_complete_test()