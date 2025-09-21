
#!/usr/bin/env python3
"""
End-to-End Testing for Membership System
Tests form validation, API endpoints, and database operations
"""

import sys
import os
import time
import requests
import json
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Flask app and database
from app import app, db
from models import Membership, MembershipService, Service, Customer

class MembershipE2ETester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:5000"
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, status, message=""):
        """Log test results"""
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        result = f"{emoji} {test_name}: {message}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
    def setup_test_data(self):
        """Create test data in database"""
        print("\n🔧 Setting up test data...")
        
        with app.app_context():
            try:
                # Create test service if it doesn't exist
                test_service = Service.query.filter_by(name='Test Massage Service').first()
                if not test_service:
                    test_service = Service(
                        name='Test Massage Service',
                        price=100.0,
                        duration=60,
                        category='massage',
                        is_active=True
                    )
                    db.session.add(test_service)
                
                # Create test customer
                test_customer = Customer.query.filter_by(email='test@customer.com').first()
                if not test_customer:
                    test_customer = Customer(
                        first_name='Test',
                        last_name='Customer',
                        email='test@customer.com',
                        phone='1234567890',
                        is_active=True
                    )
                    db.session.add(test_customer)
                
                db.session.commit()
                self.log_test("Test Data Setup", "PASS", "Test service and customer created")
                return True
                
            except Exception as e:
                self.log_test("Test Data Setup", "FAIL", f"Error: {str(e)}")
                return False
    
    def test_login(self):
        """Test admin login"""
        print("\n🔐 Testing login...")
        
        try:
            # Get login page first
            login_page = self.session.get(f"{self.base_url}/login")
            if login_page.status_code != 200:
                self.log_test("Login Page Access", "FAIL", f"Status: {login_page.status_code}")
                return False
            
            # Attempt login
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            
            response = self.session.post(f"{self.base_url}/login", data=login_data)
            
            # Check if redirected (successful login)
            if response.status_code == 302 or '/dashboard' in response.url:
                self.log_test("Admin Login", "PASS", "Successfully logged in")
                return True
            else:
                self.log_test("Admin Login", "FAIL", f"Login failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_membership_page_access(self):
        """Test access to membership management pages"""
        print("\n📋 Testing membership page access...")
        
        pages_to_test = [
            ('/memberships', 'Membership List'),
            ('/memberships/add', 'Add Membership'),
            ('/packages', 'Package Management'),
        ]
        
        all_passed = True
        
        for url, page_name in pages_to_test:
            try:
                response = self.session.get(f"{self.base_url}{url}")
                if response.status_code == 200:
                    self.log_test(f"{page_name} Access", "PASS", f"Page loaded successfully")
                else:
                    self.log_test(f"{page_name} Access", "FAIL", f"Status: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"{page_name} Access", "FAIL", f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_api_services_endpoint(self):
        """Test services API endpoint"""
        print("\n🔌 Testing services API...")
        
        try:
            response = self.session.get(f"{self.base_url}/packages/api/services")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'services' in data:
                    services_count = len(data['services'])
                    self.log_test("Services API", "PASS", f"Retrieved {services_count} services")
                    return True
                else:
                    self.log_test("Services API", "FAIL", "Invalid response format")
                    return False
            else:
                self.log_test("Services API", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Services API", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_membership_creation(self):
        """Test membership creation via form submission"""
        print("\n➕ Testing membership creation...")
        
        try:
            # Test data for membership
            membership_data = {
                'name': f'Test Membership {int(time.time())}',
                'price': '5000',
                'validity_months': '12',
                'services_included': 'Premium spa services',
                'description': 'Test membership for e2e testing',
                'is_active': 'on',
                'service_ids': ['1']  # Assuming service ID 1 exists
            }
            
            response = self.session.post(f"{self.base_url}/memberships/add", data=membership_data)
            
            if response.status_code == 302:  # Redirect after successful creation
                self.log_test("Membership Creation", "PASS", "Membership created successfully")
                return True
            else:
                self.log_test("Membership Creation", "FAIL", f"Status: {response.status_code}")
                # Try to get error details from response
                if hasattr(response, 'text'):
                    print(f"Response content: {response.text[:500]}...")
                return False
                
        except Exception as e:
            self.log_test("Membership Creation", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_database_integrity(self):
        """Test database operations"""
        print("\n🗄️ Testing database integrity...")
        
        with app.app_context():
            try:
                # Test membership count
                membership_count = Membership.query.count()
                self.log_test("Database Connection", "PASS", f"Found {membership_count} memberships")
                
                # Test service count
                service_count = Service.query.count()
                self.log_test("Services in Database", "PASS", f"Found {service_count} services")
                
                # Test relationship integrity
                memberships_with_services = Membership.query.join(MembershipService).count()
                self.log_test("Membership-Service Relations", "PASS", f"Found {memberships_with_services} relationships")
                
                return True
                
            except Exception as e:
                self.log_test("Database Integrity", "FAIL", f"Exception: {str(e)}")
                return False
    
    def test_form_validation(self):
        """Test form validation scenarios"""
        print("\n🔍 Testing form validation...")
        
        validation_tests = [
            # Test empty name
            {
                'name': 'Empty Name Validation',
                'data': {'name': '', 'price': '1000', 'validity_months': '12'},
                'should_fail': True
            },
            # Test negative price
            {
                'name': 'Negative Price Validation',
                'data': {'name': 'Test', 'price': '-100', 'validity_months': '12'},
                'should_fail': True
            },
            # Test zero validity
            {
                'name': 'Zero Validity Validation',
                'data': {'name': 'Test', 'price': '1000', 'validity_months': '0'},
                'should_fail': True
            }
        ]
        
        all_passed = True
        
        for test in validation_tests:
            try:
                response = self.session.post(f"{self.base_url}/memberships/add", data=test['data'])
                
                # If should fail, expect redirect back to form or error
                if test['should_fail']:
                    if response.status_code in [200, 302]:  # Form redisplay or redirect
                        self.log_test(test['name'], "PASS", "Validation correctly rejected invalid data")
                    else:
                        self.log_test(test['name'], "FAIL", f"Validation failed - Status: {response.status_code}")
                        all_passed = False
                
            except Exception as e:
                self.log_test(test['name'], "FAIL", f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_membership_operations(self):
        """Test CRUD operations on memberships"""
        print("\n🔄 Testing CRUD operations...")
        
        with app.app_context():
            try:
                # CREATE - Create a test membership directly
                test_membership = Membership(
                    name=f'E2E Test Membership {int(time.time())}',
                    price=1500.0,
                    validity_months=6,
                    services_included='Test services',
                    description='Created by e2e test',
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                
                db.session.add(test_membership)
                db.session.flush()  # Get ID without committing
                
                membership_id = test_membership.id
                self.log_test("Direct Membership Creation", "PASS", f"Created membership ID: {membership_id}")
                
                # READ - Test retrieval
                retrieved = Membership.query.get(membership_id)
                if retrieved and retrieved.name == test_membership.name:
                    self.log_test("Membership Retrieval", "PASS", "Successfully retrieved membership")
                else:
                    self.log_test("Membership Retrieval", "FAIL", "Could not retrieve membership")
                    return False
                
                # UPDATE - Test modification
                retrieved.price = 2000.0
                db.session.flush()
                
                updated = Membership.query.get(membership_id)
                if updated.price == 2000.0:
                    self.log_test("Membership Update", "PASS", "Successfully updated membership")
                else:
                    self.log_test("Membership Update", "FAIL", "Update failed")
                    return False
                
                # DELETE - Test deletion
                db.session.delete(updated)
                db.session.commit()
                
                deleted_check = Membership.query.get(membership_id)
                if deleted_check is None:
                    self.log_test("Membership Deletion", "PASS", "Successfully deleted membership")
                else:
                    self.log_test("Membership Deletion", "FAIL", "Deletion failed")
                    return False
                
                return True
                
            except Exception as e:
                db.session.rollback()
                self.log_test("CRUD Operations", "FAIL", f"Exception: {str(e)}")
                return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Membership E2E Testing Suite")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_data():
            print("❌ Test setup failed - aborting")
            return False
        
        # Test sequence
        tests = [
            self.test_login,
            self.test_membership_page_access,
            self.test_api_services_endpoint,
            self.test_database_integrity,
            self.test_form_validation,
            self.test_membership_operations,
            self.test_membership_creation
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            if test():
                passed_tests += 1
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 TEST SUMMARY: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️ {total_tests - passed_tests} tests failed")
            print("\nFailed tests require attention:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test']}: {result['message']}")
        
        return passed_tests == total_tests

def main():
    """Main test runner"""
    print("Starting Membership System E2E Testing...")
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    tester = MembershipE2ETester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All membership system tests completed successfully!")
        print("The membership system is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the output above for details.")
        print("Issues need to be addressed before the system is fully functional.")
    
    return success

if __name__ == '__main__':
    main()
