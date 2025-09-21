
"""
End-to-End Testing Script for Package Assignment
Based on the testing plan provided by the user
"""

import requests
import json
from datetime import datetime, timedelta

class PackageAssignmentTester:
    def __init__(self, base_url="http://0.0.0.0:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, status, message=""):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{'✅' if status == 'PASS' else '❌'} {test_name}: {message}")
        
    def login(self, username="admin", password="admin123"):
        """Login to the system"""
        try:
            response = self.session.post(f"{self.base_url}/login", data={
                'username': username,
                'password': password
            })
            if response.status_code == 200 or "dashboard" in response.url:
                self.log_test("Login", "PASS", "Successfully logged in")
                return True
            else:
                self.log_test("Login", "FAIL", f"Login failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Login", "FAIL", f"Login error: {str(e)}")
            return False
            
    def test_prerequisites(self):
        """Test 1: Verify prerequisites are met"""
        print("\n🔍 Testing Prerequisites...")
        
        # Check if customers exist
        try:
            response = self.session.get(f"{self.base_url}/packages/api/customers")
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and len(data.get('customers', [])) > 0:
                    self.log_test("Customers Exist", "PASS", f"Found {len(data['customers'])} customers")
                else:
                    self.log_test("Customers Exist", "FAIL", "No customers found")
            else:
                self.log_test("Customers Exist", "FAIL", f"API error: {response.status_code}")
        except Exception as e:
            self.log_test("Customers Exist", "FAIL", f"Error: {str(e)}")
            
        # Check if packages exist
        try:
            endpoints = [
                ('/api/memberships', 'memberships'),
                ('/api/prepaid-packages', 'prepaid packages'),
                ('/api/service-packages', 'service packages')
            ]
            
            total_packages = 0
            for endpoint, package_type in endpoints:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        count = len(data)
                        total_packages += count
                        self.log_test(f"{package_type.title()} Available", "PASS", f"Found {count} {package_type}")
                    
            if total_packages > 0:
                self.log_test("Packages Available", "PASS", f"Total {total_packages} packages available")
            else:
                self.log_test("Packages Available", "FAIL", "No packages found")
                
        except Exception as e:
            self.log_test("Packages Available", "FAIL", f"Error: {str(e)}")
            
    def test_ui_navigation(self):
        """Test 2: UI & Navigation"""
        print("\n🖥️ Testing UI & Navigation...")
        
        try:
            # Test packages page loads
            response = self.session.get(f"{self.base_url}/packages/customer-packages")
            if response.status_code == 200:
                self.log_test("Package Page Loads", "PASS", "Customer packages page accessible")
                
                # Check for key UI elements in response
                content = response.text
                ui_elements = [
                    ('Assign Package Button', 'openAssignModal'),
                    ('Customer Dropdown', 'assignCustomer'),
                    ('Package Selection', 'assignPackage'),
                    ('Save Button', 'saveAssignPackage')
                ]
                
                for element_name, element_id in ui_elements:
                    if element_id in content:
                        self.log_test(f"UI Element: {element_name}", "PASS", f"{element_id} found")
                    else:
                        self.log_test(f"UI Element: {element_name}", "FAIL", f"{element_id} not found")
            else:
                self.log_test("Package Page Loads", "FAIL", f"Page load failed: {response.status_code}")
                
        except Exception as e:
            self.log_test("Package Page Loads", "FAIL", f"Error: {str(e)}")
            
    def test_positive_assignment_flow(self):
        """Test 3A: Positive Assignment Flow"""
        print("\n✅ Testing Positive Assignment Flow...")
        
        try:
            # Get available customers
            customers_response = self.session.get(f"{self.base_url}/packages/api/customers")
            if customers_response.status_code != 200:
                self.log_test("Get Customers for Assignment", "FAIL", "Could not fetch customers")
                return
                
            customers_data = customers_response.json()
            if not customers_data.get('success') or not customers_data.get('customers'):
                self.log_test("Get Customers for Assignment", "FAIL", "No customers available")
                return
                
            customer = customers_data['customers'][0]
            self.log_test("Get Customers for Assignment", "PASS", f"Using customer: {customer['name']}")
            
            # Get available packages (try memberships first)
            packages_response = self.session.get(f"{self.base_url}/api/memberships")
            if packages_response.status_code != 200:
                self.log_test("Get Packages for Assignment", "FAIL", "Could not fetch packages")
                return
                
            packages_data = packages_response.json()
            if not isinstance(packages_data, list) or len(packages_data) == 0:
                self.log_test("Get Packages for Assignment", "FAIL", "No packages available")
                return
                
            package = packages_data[0]
            self.log_test("Get Packages for Assignment", "PASS", f"Using package: {package['name']}")
            
            # Test package assignment
            assignment_data = {
                'customer_id': customer['id'],
                'package_id': package['id'],
                'package_type': 'membership',
                'price_paid': package.get('price', 100),
                'discount': 0,
                'notes': 'E2E Test Assignment'
            }
            
            assign_response = self.session.post(
                f"{self.base_url}/packages/api/assign",
                json=assignment_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if assign_response.status_code == 200:
                assign_data = assign_response.json()
                if assign_data.get('success'):
                    self.log_test("Package Assignment", "PASS", "Package assigned successfully")
                    
                    # Verify assignment exists
                    assignments_response = self.session.get(f"{self.base_url}/packages/api/all-assignments")
                    if assignments_response.status_code == 200:
                        assignments_data = assignments_response.json()
                        if assignments_data.get('success'):
                            assignments = assignments_data.get('assignments', [])
                            test_assignment = next((a for a in assignments if a.get('notes') == 'E2E Test Assignment'), None)
                            if test_assignment:
                                self.log_test("Verify Assignment Created", "PASS", f"Assignment ID: {test_assignment['assignment_id']}")
                            else:
                                self.log_test("Verify Assignment Created", "FAIL", "Assignment not found in list")
                        else:
                            self.log_test("Verify Assignment Created", "FAIL", "Could not fetch assignments")
                    else:
                        self.log_test("Verify Assignment Created", "FAIL", f"Assignments API error: {assignments_response.status_code}")
                else:
                    self.log_test("Package Assignment", "FAIL", f"Assignment failed: {assign_data.get('error', 'Unknown error')}")
            else:
                self.log_test("Package Assignment", "FAIL", f"Assignment API error: {assign_response.status_code}")
                
        except Exception as e:
            self.log_test("Package Assignment", "FAIL", f"Error: {str(e)}")
            
    def test_validation_errors(self):
        """Test 3B: Validation & Error Handling"""
        print("\n❌ Testing Validation & Error Handling...")
        
        # Test missing customer
        try:
            response = self.session.post(
                f"{self.base_url}/packages/api/assign",
                json={'package_id': 1, 'package_type': 'membership', 'price_paid': 100},
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 400:
                self.log_test("Missing Customer Validation", "PASS", "Correctly rejected assignment without customer")
            else:
                self.log_test("Missing Customer Validation", "FAIL", f"Unexpected response: {response.status_code}")
        except Exception as e:
            self.log_test("Missing Customer Validation", "FAIL", f"Error: {str(e)}")
            
        # Test missing package
        try:
            response = self.session.post(
                f"{self.base_url}/packages/api/assign",
                json={'customer_id': 1, 'package_type': 'membership', 'price_paid': 100},
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 400:
                self.log_test("Missing Package Validation", "PASS", "Correctly rejected assignment without package")
            else:
                self.log_test("Missing Package Validation", "FAIL", f"Unexpected response: {response.status_code}")
        except Exception as e:
            self.log_test("Missing Package Validation", "FAIL", f"Error: {str(e)}")
            
    def test_integration_points(self):
        """Test 4: Integration Testing"""
        print("\n🔗 Testing Integration Points...")
        
        # Test that assigned packages appear in customer details
        try:
            customers_response = self.session.get(f"{self.base_url}/packages/api/customers")
            if customers_response.status_code == 200:
                customers_data = customers_response.json()
                if customers_data.get('success') and customers_data.get('customers'):
                    customer = customers_data['customers'][0]
                    
                    # Try to get customer details
                    detail_response = self.session.get(f"{self.base_url}/packages/api/customers/{customer['id']}")
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        if detail_data.get('success'):
                            self.log_test("Customer Details Integration", "PASS", "Customer details API working")
                        else:
                            self.log_test("Customer Details Integration", "FAIL", "Customer details API error")
                    else:
                        self.log_test("Customer Details Integration", "FAIL", f"API error: {detail_response.status_code}")
        except Exception as e:
            self.log_test("Customer Details Integration", "FAIL", f"Error: {str(e)}")
            
    def test_security_permissions(self):
        """Test 6: Security & Permissions"""
        print("\n🔒 Testing Security & Permissions...")
        
        # Test that assignment API requires authentication
        # Create a new session without login
        unauth_session = requests.Session()
        try:
            response = unauth_session.post(
                f"{self.base_url}/packages/api/assign",
                json={'customer_id': 1, 'package_id': 1, 'package_type': 'membership', 'price_paid': 100}
            )
            if response.status_code in [401, 403, 302]:  # 302 is redirect to login
                self.log_test("Authentication Required", "PASS", "Assignment API properly protected")
            else:
                self.log_test("Authentication Required", "FAIL", f"API not protected: {response.status_code}")
        except Exception as e:
            self.log_test("Authentication Required", "FAIL", f"Error: {str(e)}")
            
    def run_all_tests(self):
        """Run the complete test suite"""
        print("🧪 Starting End-to-End Package Assignment Testing")
        print("=" * 60)
        
        # Login first
        if not self.login():
            print("❌ Cannot proceed without login")
            return
            
        # Run all test categories
        self.test_prerequisites()
        self.test_ui_navigation()
        self.test_positive_assignment_flow()
        self.test_validation_errors()
        self.test_integration_points()
        self.test_security_permissions()
        
        # Summary
        print("\n📊 Test Results Summary")
        print("=" * 60)
        
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test']}: {result['message']}")
        
        return self.test_results

if __name__ == "__main__":
    tester = PackageAssignmentTester()
    results = tester.run_all_tests()
