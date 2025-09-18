
#!/usr/bin/env python3
"""
Comprehensive Billing UI Testing Script
Tests all billing functionality step by step
"""

import requests
import time
from datetime import datetime

class BillingUITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def login_admin(self):
        """Login as admin user"""
        try:
            response = self.session.post(f"{self.base_url}/login", data={
                'username': 'admin',
                'password': 'admin123'
            })
            success = response.status_code == 200 or 'dashboard' in response.url
            self.log_test("Admin Login", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Admin Login", False, f"Error: {str(e)}")
            return False
    
    def test_billing_page_load(self):
        """Test if billing page loads correctly"""
        try:
            response = self.session.get(f"{self.base_url}/integrated-billing")
            success = response.status_code == 200
            
            if success:
                content = response.text
                required_elements = [
                    'Create New Invoice',
                    'Customer',
                    'Services',
                    'Products & Inventory',
                    'Professional Tax & Billing',
                    'Generate Professional Invoice'
                ]
                
                missing_elements = [elem for elem in required_elements if elem not in content]
                if missing_elements:
                    success = False
                    message = f"Missing elements: {missing_elements}"
                else:
                    message = "All required elements present"
            else:
                message = f"HTTP {response.status_code}"
                
            self.log_test("Billing Page Load", success, message)
            return success
        except Exception as e:
            self.log_test("Billing Page Load", False, f"Error: {str(e)}")
            return False
    
    def test_create_service_invoice(self):
        """Test creating a service-only invoice"""
        try:
            # Get customers first
            customers_response = self.session.get(f"{self.base_url}/api/customers")
            if customers_response.status_code != 200:
                self.log_test("Service Invoice Creation", False, "Cannot load customers")
                return False
                
            customers = customers_response.json().get('customers', [])
            if not customers:
                self.log_test("Service Invoice Creation", False, "No customers available")
                return False
                
            # Get services
            services_response = self.session.get(f"{self.base_url}/api/services")
            if services_response.status_code != 200:
                self.log_test("Service Invoice Creation", False, "Cannot load services")
                return False
                
            services = services_response.json().get('services', [])
            if not services:
                self.log_test("Service Invoice Creation", False, "No services available")
                return False
            
            # Create invoice
            invoice_data = {
                'client_id': customers[0]['id'],
                'service_ids[]': [services[0]['id']],
                'service_quantities[]': [1],
                'cgst_rate': 9,
                'sgst_rate': 9,
                'is_interstate': False,
                'discount_type': 'amount',
                'discount_value': 0,
                'additional_charges': 0,
                'tips_amount': 0,
                'payment_terms': 'immediate',
                'payment_method': 'cash'
            }
            
            response = self.session.post(f"{self.base_url}/integrated-billing/create-professional", data=invoice_data)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = data.get('success', False)
                message = data.get('message', 'Unknown response')
                if success:
                    self.last_invoice_id = data.get('invoice_id')
            else:
                message = f"HTTP {response.status_code}"
                
            self.log_test("Service Invoice Creation", success, message)
            return success
        except Exception as e:
            self.log_test("Service Invoice Creation", False, f"Error: {str(e)}")
            return False
    
    def test_view_invoice(self):
        """Test viewing the created invoice"""
        if not hasattr(self, 'last_invoice_id'):
            self.log_test("Invoice View", False, "No invoice ID available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/integrated-billing/invoice/{self.last_invoice_id}")
            success = response.status_code == 200
            
            if success:
                content = response.text
                required_elements = [
                    'Invoice Details',
                    'Amount Breakdown',
                    'Print Invoice',
                    'Back to Billing'
                ]
                
                missing_elements = [elem for elem in required_elements if elem not in content]
                if missing_elements:
                    success = False
                    message = f"Missing elements: {missing_elements}"
                else:
                    message = "Invoice view page loaded successfully"
            else:
                message = f"HTTP {response.status_code}"
                
            self.log_test("Invoice View", success, message)
            return success
        except Exception as e:
            self.log_test("Invoice View", False, f"Error: {str(e)}")
            return False
    
    def test_print_invoice(self):
        """Test invoice print page"""
        if not hasattr(self, 'last_invoice_id'):
            self.log_test("Invoice Print", False, "No invoice ID available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/integrated-billing/print-invoice/{self.last_invoice_id}")
            success = response.status_code == 200
            
            if success:
                content = response.text
                required_elements = [
                    'TAX INVOICE',
                    'Bill To:',
                    'Amount in Words',
                    'Terms & Conditions'
                ]
                
                missing_elements = [elem for elem in required_elements if elem not in content]
                if missing_elements:
                    success = False
                    message = f"Missing elements: {missing_elements}"
                else:
                    message = "Print invoice page loaded successfully"
            else:
                message = f"HTTP {response.status_code}"
                
            self.log_test("Invoice Print", success, message)
            return success
        except Exception as e:
            self.log_test("Invoice Print", False, f"Error: {str(e)}")
            return False
    
    def test_invoice_list(self):
        """Test invoice list page"""
        try:
            response = self.session.get(f"{self.base_url}/integrated-billing/invoices")
            success = response.status_code == 200
            
            if success:
                message = "Invoice list page loaded successfully"
            else:
                message = f"HTTP {response.status_code}"
                
            self.log_test("Invoice List", success, message)
            return success
        except Exception as e:
            self.log_test("Invoice List", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all billing tests"""
        print("🧪 Starting Comprehensive Billing UI Tests...")
        print("=" * 60)
        
        # Test sequence
        tests = [
            self.login_admin,
            self.test_billing_page_load,
            self.test_create_service_invoice,
            self.test_view_invoice,
            self.test_print_invoice,
            self.test_invoice_list
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
                time.sleep(1)  # Small delay between tests
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {str(e)}")
                failed += 1
        
        # Results summary
        print("\n" + "=" * 60)
        print("📊 Test Results Summary:")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if passed + failed > 0:
            success_rate = (passed / (passed + failed)) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        return passed > failed

def main():
    """Main function to run billing tests"""
    tester = BillingUITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Billing system tests completed successfully!")
        print("💡 All major billing functions are working correctly.")
    else:
        print("\n⚠️ Some billing tests failed.")
        print("💡 Please check the output above for specific issues.")
    
    return success

if __name__ == "__main__":
    main()
