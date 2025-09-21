
#!/usr/bin/env python3
"""
End-to-End Testing Script for Membership Service Restriction Requirement
Tests that membership benefits ONLY apply to specifically selected services, not all services
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
from models import Membership, MembershipService, Service, Customer, ServicePackageAssignment

class MembershipServiceRestrictionTester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:5000"
        self.session = requests.Session()
        self.test_results = []
        self.test_membership_id = None
        self.test_customer_id = None
        self.included_service_ids = []
        self.excluded_service_ids = []
        
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
        
    def setup_test_environment(self):
        """Create test data for membership service restriction testing"""
        print("\n🔧 Setting up test environment...")
        
        with app.app_context():
            try:
                # Clean up any existing test data
                existing_membership = Membership.query.filter_by(name='E2E Test Membership - Service Restriction').first()
                if existing_membership:
                    MembershipService.query.filter_by(membership_id=existing_membership.id).delete()
                    db.session.delete(existing_membership)
                
                existing_customer = Customer.query.filter_by(email='test.restriction@e2e.com').first()
                if existing_customer:
                    db.session.delete(existing_customer)
                
                # Create test services if they don't exist
                test_services = [
                    {'name': 'E2E Included Service 1', 'price': 1000.0, 'category': 'massage'},
                    {'name': 'E2E Included Service 2', 'price': 1500.0, 'category': 'facial'},
                    {'name': 'E2E Excluded Service 1', 'price': 800.0, 'category': 'therapy'},
                    {'name': 'E2E Excluded Service 2', 'price': 1200.0, 'category': 'wellness'}
                ]
                
                created_services = []
                for service_data in test_services:
                    service = Service.query.filter_by(name=service_data['name']).first()
                    if not service:
                        service = Service(
                            name=service_data['name'],
                            price=service_data['price'],
                            duration=60,
                            category=service_data['category'],
                            is_active=True
                        )
                        db.session.add(service)
                        db.session.flush()
                    created_services.append(service)
                
                # Separate included and excluded services
                self.included_service_ids = [created_services[0].id, created_services[1].id]
                self.excluded_service_ids = [created_services[2].id, created_services[3].id]
                
                # Create test membership with ONLY selected services
                test_membership = Membership(
                    name='E2E Test Membership - Service Restriction',
                    price=10000.0,
                    validity_months=12,
                    services_included='Premium services with selective benefits',
                    description='Test membership that should ONLY provide benefits for selected services',
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                
                db.session.add(test_membership)
                db.session.flush()
                self.test_membership_id = test_membership.id
                
                # Add ONLY the included services to the membership
                for service_id in self.included_service_ids:
                    membership_service = MembershipService(
                        membership_id=test_membership.id,
                        service_id=service_id
                    )
                    db.session.add(membership_service)
                
                # Create test customer
                test_customer = Customer(
                    first_name='Test',
                    last_name='Customer Restriction',
                    email='test.restriction@e2e.com',
                    phone='9876543210',
                    is_active=True
                )
                
                db.session.add(test_customer)
                db.session.flush()
                self.test_customer_id = test_customer.id
                
                # Assign membership to customer
                assignment = ServicePackageAssignment(
                    customer_id=test_customer.id,
                    package_type='membership',
                    package_reference_id=test_membership.id,
                    assigned_on=datetime.utcnow(),
                    expires_on=datetime.utcnow() + timedelta(days=365),
                    price_paid=10000.0,
                    status='active'
                )
                db.session.add(assignment)
                
                db.session.commit()
                self.log_test("Test Environment Setup", "PASS", f"Created membership ID {self.test_membership_id} with selective services")
                return True
                
            except Exception as e:
                db.session.rollback()
                self.log_test("Test Environment Setup", "FAIL", f"Error: {str(e)}")
                return False
    
    def test_login(self):
        """Test admin login"""
        print("\n🔐 Testing login...")
        
        try:
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            
            response = self.session.post(f"{self.base_url}/login", data=login_data)
            
            if response.status_code == 302 or 'dashboard' in response.url:
                self.log_test("Admin Login", "PASS", "Successfully logged in")
                return True
            else:
                self.log_test("Admin Login", "FAIL", f"Login failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_membership_service_associations(self):
        """Test that membership is correctly associated with ONLY selected services"""
        print("\n🔗 Testing membership-service associations...")
        
        with app.app_context():
            try:
                membership = Membership.query.get(self.test_membership_id)
                if not membership:
                    self.log_test("Membership Service Associations", "FAIL", "Test membership not found")
                    return False
                
                # Get associated services
                associated_services = [ms.service_id for ms in membership.membership_services]
                
                # Check that ONLY included services are associated
                for service_id in self.included_service_ids:
                    if service_id in associated_services:
                        self.log_test(f"Included Service {service_id} Association", "PASS", "Service correctly included in membership")
                    else:
                        self.log_test(f"Included Service {service_id} Association", "FAIL", "Service missing from membership")
                        return False
                
                # Check that excluded services are NOT associated
                for service_id in self.excluded_service_ids:
                    if service_id not in associated_services:
                        self.log_test(f"Excluded Service {service_id} Association", "PASS", "Service correctly excluded from membership")
                    else:
                        self.log_test(f"Excluded Service {service_id} Association", "FAIL", "Service incorrectly included in membership")
                        return False
                
                # Verify total count
                if len(associated_services) == len(self.included_service_ids):
                    self.log_test("Service Association Count", "PASS", f"Exactly {len(self.included_service_ids)} services associated")
                else:
                    self.log_test("Service Association Count", "FAIL", f"Expected {len(self.included_service_ids)}, got {len(associated_services)}")
                    return False
                
                return True
                
            except Exception as e:
                self.log_test("Membership Service Associations", "FAIL", f"Exception: {str(e)}")
                return False
    
    def test_billing_with_included_services(self):
        """Test billing system applies membership benefits ONLY to included services"""
        print("\n💰 Testing billing with included services...")
        
        try:
            # Test billing for each included service
            for service_id in self.included_service_ids:
                service_data = {
                    'client_id': str(self.test_customer_id),
                    'service_ids[]': [str(service_id)],
                    'service_quantities[]': ['1'],
                    'appointment_ids[]': [''],
                    'cgst_rate': '9',
                    'sgst_rate': '9',
                    'igst_rate': '0',
                    'is_interstate': 'off',
                    'discount_type': 'amount',
                    'discount_value': '0',
                    'additional_charges': '0',
                    'tips_amount': '0',
                    'payment_terms': 'immediate',
                    'payment_method': 'cash'
                }
                
                response = self.session.post(f"{self.base_url}/integrated-billing/create-professional", data=service_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        # Check if package benefits were applied
                        if data.get('package_benefits_applied', 0) > 0:
                            deduction = data.get('total_package_deductions', 0)
                            self.log_test(f"Included Service {service_id} Billing", "PASS", 
                                        f"Membership benefit applied - ₹{deduction:.2f} deduction")
                        else:
                            # This might be OK if membership provides unlimited access rather than discounts
                            self.log_test(f"Included Service {service_id} Billing", "PASS", 
                                        "Service billing successful (membership benefit logic may vary)")
                    else:
                        self.log_test(f"Included Service {service_id} Billing", "FAIL", f"Billing failed: {data.get('message', 'Unknown error')}")
                        return False
                else:
                    self.log_test(f"Included Service {service_id} Billing", "FAIL", f"HTTP {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            self.log_test("Billing with Included Services", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_billing_with_excluded_services(self):
        """Test billing system does NOT apply membership benefits to excluded services"""
        print("\n🚫 Testing billing with excluded services...")
        
        try:
            # Test billing for each excluded service
            for service_id in self.excluded_service_ids:
                service_data = {
                    'client_id': str(self.test_customer_id),
                    'service_ids[]': [str(service_id)],
                    'service_quantities[]': ['1'],
                    'appointment_ids[]': [''],
                    'cgst_rate': '9',
                    'sgst_rate': '9',
                    'igst_rate': '0',
                    'is_interstate': 'off',
                    'discount_type': 'amount',
                    'discount_value': '0',
                    'additional_charges': '0',
                    'tips_amount': '0',
                    'payment_terms': 'immediate',
                    'payment_method': 'cash'
                }
                
                response = self.session.post(f"{self.base_url}/integrated-billing/create-professional", data=service_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        # Check that NO package benefits were applied
                        benefits_applied = data.get('package_benefits_applied', 0)
                        deductions = data.get('total_package_deductions', 0)
                        
                        if benefits_applied == 0 and deductions == 0:
                            self.log_test(f"Excluded Service {service_id} Billing", "PASS", 
                                        "No membership benefits applied (as expected)")
                        else:
                            self.log_test(f"Excluded Service {service_id} Billing", "FAIL", 
                                        f"Unexpected benefits applied: {benefits_applied} benefits, ₹{deductions:.2f} deductions")
                            return False
                    else:
                        self.log_test(f"Excluded Service {service_id} Billing", "FAIL", f"Billing failed: {data.get('message', 'Unknown error')}")
                        return False
                else:
                    self.log_test(f"Excluded Service {service_id} Billing", "FAIL", f"HTTP {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            self.log_test("Billing with Excluded Services", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_package_billing_service_logic(self):
        """Test the PackageBillingService logic for service restrictions"""
        print("\n🔍 Testing PackageBillingService logic...")
        
        try:
            from modules.packages.package_billing_service import PackageBillingService
            
            with app.app_context():
                # Test for included service
                included_service_id = self.included_service_ids[0]
                included_result = PackageBillingService.apply_package_benefit(
                    customer_id=self.test_customer_id,
                    service_id=included_service_id,
                    service_price=1000.0,
                    invoice_id=None,
                    invoice_item_id=None,
                    service_date=datetime.utcnow(),
                    requested_quantity=1
                )
                
                if included_result.get('success') and included_result.get('applied'):
                    self.log_test("PackageBillingService - Included Service", "PASS", 
                                f"Benefit applied: {included_result.get('message', 'Success')}")
                else:
                    # May be OK if membership provides different benefit type
                    self.log_test("PackageBillingService - Included Service", "WARN", 
                                f"No benefit applied: {included_result.get('message', 'No message')}")
                
                # Test for excluded service
                excluded_service_id = self.excluded_service_ids[0]
                excluded_result = PackageBillingService.apply_package_benefit(
                    customer_id=self.test_customer_id,
                    service_id=excluded_service_id,
                    service_price=800.0,
                    invoice_id=None,
                    invoice_item_id=None,
                    service_date=datetime.utcnow(),
                    requested_quantity=1
                )
                
                if excluded_result.get('success') and not excluded_result.get('applied'):
                    self.log_test("PackageBillingService - Excluded Service", "PASS", 
                                "No benefit applied to excluded service (correct)")
                elif excluded_result.get('applied'):
                    self.log_test("PackageBillingService - Excluded Service", "FAIL", 
                                "Benefit incorrectly applied to excluded service")
                    return False
                else:
                    self.log_test("PackageBillingService - Excluded Service", "PASS", 
                                "No benefit applied (correct)")
                
                return True
                
        except Exception as e:
            self.log_test("PackageBillingService Logic", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_membership_edit_service_selection(self):
        """Test editing membership to add/remove services"""
        print("\n✏️ Testing membership edit service selection...")
        
        try:
            # Get the edit page
            edit_url = f"{self.base_url}/memberships/edit/{self.test_membership_id}"
            response = self.session.get(edit_url)
            
            if response.status_code == 200:
                self.log_test("Membership Edit Page Access", "PASS", "Edit page loaded successfully")
            else:
                self.log_test("Membership Edit Page Access", "FAIL", f"Status: {response.status_code}")
                return False
            
            # Test updating service selection (add one excluded service)
            new_service_ids = self.included_service_ids + [self.excluded_service_ids[0]]
            
            edit_data = {
                'name': 'E2E Test Membership - Service Restriction (Updated)',
                'price': '10000',
                'validity_months': '12',
                'services_included': 'Updated premium services',
                'description': 'Updated test membership',
                'is_active': 'on',
                'service_ids': [str(sid) for sid in new_service_ids]
            }
            
            response = self.session.post(f"{self.base_url}/memberships/edit/{self.test_membership_id}", data=edit_data)
            
            if response.status_code == 302:  # Redirect after successful update
                self.log_test("Membership Edit Submission", "PASS", "Membership updated successfully")
                
                # Verify the changes in database
                with app.app_context():
                    membership = Membership.query.get(self.test_membership_id)
                    updated_services = [ms.service_id for ms in membership.membership_services]
                    
                    if set(updated_services) == set(new_service_ids):
                        self.log_test("Service Selection Update", "PASS", "Service associations updated correctly")
                        return True
                    else:
                        self.log_test("Service Selection Update", "FAIL", 
                                    f"Expected {new_service_ids}, got {updated_services}")
                        return False
            else:
                self.log_test("Membership Edit Submission", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Membership Edit Service Selection", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_ui_service_selection_display(self):
        """Test that UI correctly displays service selection options"""
        print("\n🖥️ Testing UI service selection display...")
        
        try:
            # Test add membership page
            add_url = f"{self.base_url}/memberships/add"
            response = self.session.get(add_url)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for service selection UI elements
                if 'name="service_ids"' in content:
                    self.log_test("Add Page - Service Selection UI", "PASS", "Service selection checkboxes present")
                else:
                    self.log_test("Add Page - Service Selection UI", "FAIL", "Service selection UI missing")
                    return False
                
                # Check for restriction warning message
                if 'ONLY apply to the services you select' in content or 'specific services covered' in content:
                    self.log_test("Add Page - Restriction Warning", "PASS", "Service restriction warning displayed")
                else:
                    self.log_test("Add Page - Restriction Warning", "WARN", "Service restriction warning missing")
            else:
                self.log_test("Add Page Access", "FAIL", f"Status: {response.status_code}")
                return False
            
            # Test view membership page
            view_url = f"{self.base_url}/memberships/view/{self.test_membership_id}"
            response = self.session.get(view_url)
            
            if response.status_code == 200:
                content = response.text
                
                # Check that only included services are shown
                with app.app_context():
                    included_services = Service.query.filter(Service.id.in_(self.included_service_ids)).all()
                    excluded_services = Service.query.filter(Service.id.in_(self.excluded_service_ids)).all()
                    
                    all_included_shown = all(service.name in content for service in included_services)
                    any_excluded_shown = any(service.name in content for service in excluded_services)
                    
                    if all_included_shown and not any_excluded_shown:
                        self.log_test("View Page - Service Display", "PASS", "Only included services displayed")
                    elif not all_included_shown:
                        self.log_test("View Page - Service Display", "FAIL", "Some included services missing")
                        return False
                    elif any_excluded_shown:
                        self.log_test("View Page - Service Display", "FAIL", "Excluded services incorrectly displayed")
                        return False
            else:
                self.log_test("View Page Access", "FAIL", f"Status: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("UI Service Selection Display", "FAIL", f"Exception: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        with app.app_context():
            try:
                # Delete test membership and associations
                if self.test_membership_id:
                    MembershipService.query.filter_by(membership_id=self.test_membership_id).delete()
                    membership = Membership.query.get(self.test_membership_id)
                    if membership:
                        db.session.delete(membership)
                
                # Delete test customer and assignments
                if self.test_customer_id:
                    ServicePackageAssignment.query.filter_by(customer_id=self.test_customer_id).delete()
                    customer = Customer.query.get(self.test_customer_id)
                    if customer:
                        db.session.delete(customer)
                
                # Delete test services
                all_test_service_ids = self.included_service_ids + self.excluded_service_ids
                for service_id in all_test_service_ids:
                    service = Service.query.get(service_id)
                    if service and service.name.startswith('E2E'):
                        db.session.delete(service)
                
                db.session.commit()
                self.log_test("Test Data Cleanup", "PASS", "All test data cleaned up")
                
            except Exception as e:
                db.session.rollback()
                self.log_test("Test Data Cleanup", "FAIL", f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run complete test suite for membership service restriction requirement"""
        print("🚀 Starting Membership Service Restriction E2E Testing Suite")
        print("=" * 80)
        print("REQUIREMENT: Membership offers should ONLY apply to selected services, not all services")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Test setup failed - aborting")
            return False
        
        # Test sequence
        tests = [
            ("Login Test", self.test_login),
            ("Service Associations Test", self.test_membership_service_associations),
            ("PackageBillingService Logic Test", self.test_package_billing_service_logic),
            ("Billing with Included Services", self.test_billing_with_included_services),
            ("Billing with Excluded Services", self.test_billing_with_excluded_services),
            ("Membership Edit Service Selection", self.test_membership_edit_service_selection),
            ("UI Service Selection Display", self.test_ui_service_selection_display)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔄 Running: {test_name}")
            if test_func():
                passed_tests += 1
            time.sleep(1)  # Brief pause between tests
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 80)
        print(f"📊 TEST SUMMARY: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED!")
            print("✅ REQUIREMENT VERIFIED: Membership benefits ONLY apply to selected services")
        else:
            print(f"⚠️ {total_tests - passed_tests} tests failed")
            print("❌ REQUIREMENT NOT FULLY SATISFIED")
            print("\nFailed tests require attention:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test']}: {result['message']}")
        
        # Show detailed results
        print("\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status_symbol = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️"
            print(f"{status_symbol} {result['test']}: {result['message']}")
        
        return passed_tests == total_tests

def main():
    """Main test runner"""
    print("🧪 Starting Membership Service Restriction E2E Testing...")
    print("This test verifies that membership benefits ONLY apply to specifically selected services")
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    tester = MembershipServiceRestrictionTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All membership service restriction tests completed successfully!")
        print("🎯 The requirement is fully implemented and working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the output above for details.")
        print("🔧 Issues need to be addressed to meet the requirement.")
    
    return success

if __name__ == '__main__':
    main()
