#!/usr/bin/env python3
"""
End-to-End Testing Script for Student Offer Add, Edit, and Assign Operations
Tests the complete workflow: Create → Edit → Assign to Customer
"""

import requests
import time
from datetime import datetime, timedelta
import json
import sys
import os

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_ADMIN_USERNAME = "admin"
TEST_ADMIN_PASSWORD = "admin123"

class StudentOfferE2ETester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_offer_id = None
        self.test_customer_id = None
        self.assignment_id = None

    def log_test(self, test_name, status, message="", details=None):
        """Log test results"""
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        result = f"{emoji} {test_name}: {message}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        })

    def login_admin(self):
        """Test admin login"""
        print("\n🔐 Testing Admin Login...")

        try:
            login_data = {
                'username': TEST_ADMIN_USERNAME,
                'password': TEST_ADMIN_PASSWORD
            }

            response = self.session.post(f"{BASE_URL}/login", data=login_data)

            if response.status_code == 200 or 'dashboard' in response.url:
                self.log_test("Admin Login", "PASS", "Successfully logged in")
                return True
            else:
                self.log_test("Admin Login", "FAIL", f"Login failed - Status: {response.status_code}")
                return False

        except Exception as e:
            self.log_test("Admin Login", "FAIL", f"Exception: {str(e)}")
            return False

    def test_student_offer_page_access(self):
        """Test access to student offer management page"""
        print("\n📄 Testing Student Offer Page Access...")

        try:
            response = self.session.get(f"{BASE_URL}/packages")

            if response.status_code == 200:
                content = response.text

                # Check for student offer specific elements
                required_elements = [
                    'assign-student-tab',
                    'tblStudentOffers',
                    'addStudentOfferModal',
                    'Student Offers Management'
                ]

                missing_elements = [elem for elem in required_elements if elem not in content]

                if not missing_elements:
                    self.log_test("Student Offer Page Access", "PASS", "All required elements found")
                    return True
                else:
                    self.log_test("Student Offer Page Access", "FAIL", f"Missing elements: {missing_elements}")
                    return False
            else:
                self.log_test("Student Offer Page Access", "FAIL", f"HTTP {response.status_code}")
                return False

        except Exception as e:
            self.log_test("Student Offer Page Access", "FAIL", f"Exception: {str(e)}")
            return False

    def test_add_student_offer(self):
        """Test creating a new student offer"""
        print("\n➕ Testing Add Student Offer...")

        try:
            # Get available services first
            services_response = self.session.get(f"{BASE_URL}/api/services")
            if services_response.status_code != 200:
                self.log_test("Add Student Offer", "FAIL", "Cannot load services")
                return False

            services_data = services_response.json()
            if not services_data.get('services') or len(services_data['services']) == 0:
                self.log_test("Add Student Offer", "FAIL", "No services available")
                return False

            # Use first two services for the offer
            service_ids = [services_data['services'][0]['id'], services_data['services'][1]['id']]

            # Prepare student offer data
            today = datetime.now()
            future_date = today + timedelta(days=180)

            offer_data = {
                'discount_percentage': '25.0',
                'service_ids': service_ids,
                'valid_days': '90',
                'valid_from': today.strftime('%Y-%m-%d'),
                'valid_to': future_date.strftime('%Y-%m-%d'),
                'conditions': 'Valid student ID required. Cannot be combined with other offers. E2E Test Offer.'
            }

            # Create student offer
            response = self.session.post(f"{BASE_URL}/api/student-offers", json=offer_data)

            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success'):
                        self.created_offer_id = result.get('offer_id')
                        self.log_test("Add Student Offer", "PASS", 
                                    f"Student offer created successfully - ID: {self.created_offer_id}")
                        return True
                    else:
                        self.log_test("Add Student Offer", "FAIL", f"API error: {result.get('error')}")
                        return False
                except json.JSONDecodeError:
                    self.log_test("Add Student Offer", "FAIL", "Invalid JSON response")
                    return False
            else:
                self.log_test("Add Student Offer", "FAIL", f"HTTP {response.status_code}")
                return False

        except Exception as e:
            self.log_test("Add Student Offer", "FAIL", f"Exception: {str(e)}")
            return False

    def test_edit_student_offer(self):
        """Test editing the created student offer"""
        print("\n✏️ Testing Edit Student Offer...")

        if not self.created_offer_id:
            self.log_test("Edit Student Offer", "FAIL", "No offer ID available for editing")
            return False

        try:
            # Get current offer data
            get_response = self.session.get(f"{BASE_URL}/api/student-offers/{self.created_offer_id}")

            if get_response.status_code != 200:
                self.log_test("Edit Student Offer", "FAIL", f"Cannot fetch offer data: {get_response.status_code}")
                return False

            current_data = get_response.json()
            if not current_data.get('success'):
                self.log_test("Edit Student Offer", "FAIL", "Failed to get current offer data")
                return False

            # Update the offer
            updated_data = {
                'discount_percentage': '30.0',  # Increased discount
                'service_ids': current_data['offer']['service_ids'],
                'valid_days': '120',  # Extended validity
                'valid_from': current_data['offer']['valid_from'],
                'valid_to': current_data['offer']['valid_to'],
                'conditions': 'Updated: Valid student ID required. Cannot be combined with other offers. E2E Test Offer - EDITED.'
            }

            # Submit update
            response = self.session.put(f"{BASE_URL}/api/student-offers/{self.created_offer_id}", json=updated_data)

            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success'):
                        self.log_test("Edit Student Offer", "PASS", "Student offer updated successfully")

                        # Verify the changes
                        verify_response = self.session.get(f"{BASE_URL}/api/student-offers/{self.created_offer_id}")
                        if verify_response.status_code == 200:
                            verify_data = verify_response.json()
                            updated_offer = verify_data.get('offer', {})

                            if (updated_offer.get('discount_percentage') == 30.0 and 
                                updated_offer.get('valid_days') == 120 and
                                'EDITED' in updated_offer.get('conditions', '')):
                                self.log_test("Edit Verification", "PASS", "Changes verified successfully")
                                return True
                            else:
                                self.log_test("Edit Verification", "FAIL", "Changes not reflected correctly")
                                return False
                        else:
                            self.log_test("Edit Verification", "FAIL", "Cannot verify changes")
                            return False
                    else:
                        self.log_test("Edit Student Offer", "FAIL", f"Update failed: {result.get('error')}")
                        return False
                except json.JSONDecodeError:
                    self.log_test("Edit Student Offer", "FAIL", "Invalid JSON response")
                    return False
            else:
                self.log_test("Edit Student Offer", "FAIL", f"HTTP {response.status_code}")
                return False

        except Exception as e:
            self.log_test("Edit Student Offer", "FAIL", f"Exception: {str(e)}")
            return False

    def get_or_create_test_customer(self):
        """Get existing customer or create one for testing"""
        print("\n👤 Setting up test customer...")

        try:
            # Try to get existing customers
            customers_response = self.session.get(f"{BASE_URL}/packages/api/customers")

            if customers_response.status_code == 200:
                customers_data = customers_response.json()
                if customers_data.get('success') and customers_data.get('customers') and len(customers_data['customers']) > 0:
                    # Use existing customer
                    self.test_customer_id = customers_data['customers'][0]['id']
                    customer_name = customers_data['customers'][0]['name']
                    self.log_test("Test Customer Setup", "PASS", f"Using existing customer: {customer_name}")
                    return True

            # Create new test customer if none exist
            customer_data = {
                'first_name': 'E2E Test',
                'last_name': 'Student',
                'email': 'e2e.test.student@example.com',
                'phone': '9876543210',
                'date_of_birth': '2000-01-01',
                'gender': 'other',
                'address': 'Test Address for E2E Testing',
                'is_active': True
            }

            create_response = self.session.post(f"{BASE_URL}/api/customers", json=customer_data)

            if create_response.status_code == 200:
                create_result = create_response.json()
                if create_result.get('success'):
                    self.test_customer_id = create_result.get('customer_id')
                    self.log_test("Test Customer Setup", "PASS", f"Created test customer - ID: {self.test_customer_id}")
                    return True

            self.log_test("Test Customer Setup", "FAIL", "Cannot create or find test customer")
            return False

        except Exception as e:
            self.log_test("Test Customer Setup", "FAIL", f"Exception: {str(e)}")
            return False

    def test_assign_student_offer(self):
        """Test assigning student offer to customer"""
        print("\n🎯 Testing Assign Student Offer...")

        if not self.created_offer_id:
            self.log_test("Assign Student Offer", "FAIL", "No offer ID available for assignment")
            return False

        if not self.test_customer_id:
            self.log_test("Assign Student Offer", "FAIL", "No customer ID available for assignment")
            return False

        try:
            # Prepare assignment data
            assignment_data = {
                'customer_id': self.test_customer_id,
                'package_id': self.created_offer_id,
                'package_type': 'student_offer',
                'price_paid': 0.0,  # Student offers typically don't have upfront payment
                'notes': 'E2E Test Assignment - Student Offer'
            }

            # Assign the offer
            response = self.session.post(f"{BASE_URL}/packages/api/assign", json=assignment_data)

            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success'):
                        self.assignment_id = result.get('assignment_id') or result.get('customer_package_id')
                        self.log_test("Assign Student Offer", "PASS", 
                                    f"Student offer assigned successfully - Assignment ID: {self.assignment_id}")
                        return True
                    else:
                        self.log_test("Assign Student Offer", "FAIL", f"Assignment failed: {result.get('error')}")
                        return False
                except json.JSONDecodeError:
                    self.log_test("Assign Student Offer", "FAIL", "Invalid JSON response")
                    return False
            else:
                self.log_test("Assign Student Offer", "FAIL", f"HTTP {response.status_code}")
                return False

        except Exception as e:
            self.log_test("Assign Student Offer", "FAIL", f"Exception: {str(e)}")
            return False

    def test_verify_assignment(self):
        """Verify the assignment was created correctly"""
        print("\n🔍 Testing Assignment Verification...")

        if not self.assignment_id:
            self.log_test("Assignment Verification", "FAIL", "No assignment ID to verify")
            return False

        try:
            # Get assignment details
            response = self.session.get(f"{BASE_URL}/packages/api/customer-packages/{self.assignment_id}")

            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success') and result.get('package'):
                        package_data = result['package']

                        # Verify assignment details
                        verifications = {
                            'customer_match': package_data.get('customer_id') == self.test_customer_id,
                            'package_type': 'student' in package_data.get('package_name', '').lower() or 
                                          'student' in str(package_data.get('notes', '')).lower(),
                            'status_active': package_data.get('status') == 'active',
                            'has_items': len(package_data.get('items', [])) > 0
                        }

                        if all(verifications.values()):
                            self.log_test("Assignment Verification", "PASS", 
                                        "Assignment verified - all details correct")
                            return True
                        else:
                            failed_checks = [k for k, v in verifications.items() if not v]
                            self.log_test("Assignment Verification", "FAIL", 
                                        f"Verification failed: {failed_checks}")
                            return False
                    else:
                        self.log_test("Assignment Verification", "FAIL", "Invalid assignment data")
                        return False
                except json.JSONDecodeError:
                    self.log_test("Assignment Verification", "FAIL", "Invalid JSON response")
                    return False
            else:
                self.log_test("Assignment Verification", "FAIL", f"HTTP {response.status_code}")
                return False

        except Exception as e:
            self.log_test("Assignment Verification", "FAIL", f"Exception: {str(e)}")
            return False

    def test_list_student_offers(self):
        """Test listing all student offers"""
        print("\n📋 Testing List Student Offers...")

        try:
            response = self.session.get(f"{BASE_URL}/api/student-offers")

            if response.status_code == 200:
                try:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        # Find our created offer
                        our_offer = None
                        for offer in result:
                            if offer.get('id') == self.created_offer_id:
                                our_offer = offer
                                break

                        if our_offer:
                            self.log_test("List Student Offers", "PASS", 
                                        f"Found our offer in list - {len(result)} total offers")
                            return True
                        else:
                            self.log_test("List Student Offers", "FAIL", "Our offer not found in list")
                            return False
                    else:
                        self.log_test("List Student Offers", "PASS", "List endpoint working (empty list)")
                        return True
                except json.JSONDecodeError:
                    self.log_test("List Student Offers", "FAIL", "Invalid JSON response")
                    return False
            else:
                self.log_test("List Student Offers", "FAIL", f"HTTP {response.status_code}")
                return False

        except Exception as e:
            self.log_test("List Student Offers", "FAIL", f"Exception: {str(e)}")
            return False

    def test_ui_integration(self):
        """Test UI integration elements"""
        print("\n🖥️ Testing UI Integration...")

        try:
            # Test main packages page
            response = self.session.get(f"{BASE_URL}/packages")

            if response.status_code == 200:
                content = response.text

                # Check for JavaScript functions
                js_functions = [
                    'initializeStudentOfferModals',
                    'assignStudentFromTemplate',
                    'submitStudentOfferForm'
                ]

                found_functions = sum(1 for func in js_functions if func in content)

                if found_functions >= 2:  # At least 2 out of 3 functions should be present
                    self.log_test("UI Integration", "PASS", f"Found {found_functions}/3 JS functions")
                    return True
                else:
                    self.log_test("UI Integration", "FAIL", f"Only found {found_functions}/3 JS functions")
                    return False
            else:
                self.log_test("UI Integration", "FAIL", f"HTTP {response.status_code}")
                return False

        except Exception as e:
            self.log_test("UI Integration", "FAIL", f"Exception: {str(e)}")
            return False

    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")

        cleanup_success = True

        # Try to delete assignment (if exists)
        if self.assignment_id:
            try:
                delete_assignment = self.session.delete(f"{BASE_URL}/packages/api/customer-packages/{self.assignment_id}")
                if delete_assignment.status_code in [200, 204, 404]:
                    self.log_test("Cleanup Assignment", "PASS", "Assignment cleaned up")
                else:
                    self.log_test("Cleanup Assignment", "FAIL", f"HTTP {delete_assignment.status_code}")
                    cleanup_success = False
            except:
                self.log_test("Cleanup Assignment", "FAIL", "Exception during cleanup")
                cleanup_success = False

        # Try to delete student offer (if exists)
        if self.created_offer_id:
            try:
                delete_offer = self.session.delete(f"{BASE_URL}/api/student-offers/{self.created_offer_id}")
                if delete_offer.status_code in [200, 204, 404]:
                    self.log_test("Cleanup Student Offer", "PASS", "Student offer cleaned up")
                else:
                    self.log_test("Cleanup Student Offer", "FAIL", f"HTTP {delete_offer.status_code}")
                    cleanup_success = False
            except:
                self.log_test("Cleanup Student Offer", "FAIL", "Exception during cleanup")
                cleanup_success = False

        # Try to delete test customer (if we created one)
        if self.test_customer_id and 'e2e.test.student' in str(self.test_customer_id):
            try:
                delete_customer = self.session.delete(f"{BASE_URL}/api/customers/{self.test_customer_id}")
                if delete_customer.status_code in [200, 204, 404]:
                    self.log_test("Cleanup Test Customer", "PASS", "Test customer cleaned up")
                else:
                    self.log_test("Cleanup Test Customer", "FAIL", f"HTTP {delete_customer.status_code}")
                    cleanup_success = False
            except:
                self.log_test("Cleanup Test Customer", "FAIL", "Exception during cleanup")
                cleanup_success = False

        return cleanup_success

    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Student Offer Add/Edit/Assign E2E Testing Suite")
        print("=" * 80)

        # Test sequence
        tests = [
            ("Admin Login", self.login_admin),
            ("Student Offer Page Access", self.test_student_offer_page_access),
            ("Add Student Offer", self.test_add_student_offer),
            ("Edit Student Offer", self.test_edit_student_offer),
            ("List Student Offers", self.test_list_student_offers),
            ("Setup Test Customer", self.get_or_create_test_customer),
            ("Assign Student Offer", self.test_assign_student_offer),
            ("Verify Assignment", self.test_verify_assignment),
            ("UI Integration", self.test_ui_integration)
        ]

        passed_tests = 0
        total_tests = len(tests)

        for test_name, test_func in tests:
            print(f"\n🔄 Running: {test_name}")
            if test_func():
                passed_tests += 1

        # Cleanup
        print(f"\n🔄 Running: Cleanup")
        self.cleanup_test_data()

        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)

        for result in self.test_results:
            status_icon = "✅" if result['status'] == "PASS" else "❌"
            print(f"{status_icon} {result['test']}: {result['message']}")

        print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
        success_rate = (passed_tests / total_tests) * 100
        print(f"Success Rate: {success_rate:.1f}%")

        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED!")
            print("Student Offer Add/Edit/Assign functionality is working correctly.")
        else:
            print(f"\n⚠️ {total_tests - passed_tests} test(s) failed.")
            print("Please check the failed tests above for issues to address.")

        return passed_tests == total_tests

def main():
    """Main function to run all tests"""
    print("Starting Student Offer Add/Edit/Assign E2E Testing...")

    # Wait a moment for server to be ready
    time.sleep(2)

    tester = StudentOfferE2ETester()
    success = tester.run_all_tests()

    if success:
        print("\n✅ All Student Offer E2E tests completed successfully!")
        print("The Add/Edit/Assign workflow is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the output above for details.")
        print("Issues need to be addressed to ensure full functionality.")

    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)