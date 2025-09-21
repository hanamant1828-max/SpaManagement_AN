
#!/usr/bin/env python3
"""
Comprehensive Billing System Test Cases
Tests both functionality and UI scenarios
"""

from app import app, db
from models import Customer, Service, EnhancedInvoice, InvoiceItem
from modules.inventory.models import InventoryProduct, InventoryBatch, InventoryLocation
from datetime import datetime, date
import json

class BillingTestRunner:
    def __init__(self):
        self.test_results = []
        self.customer_id = None
        self.service_id = None
        self.product_id = None
        self.batch_id = None
    
    def log_test(self, test_name, success, message="", details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'details': details
        })
    
    def setup_test_data(self):
        """Set up test data for billing tests"""
        print("🔧 Setting up test data...")
        
        try:
            # Create test customer
            customer = Customer(
                first_name="Test",
                last_name="Customer",
                email="test@example.com",
                phone="1234567890",
                is_active=True
            )
            db.session.add(customer)
            db.session.flush()
            self.customer_id = customer.id
            
            # Create test service
            service = Service(
                name="Test Service",
                description="Test service description",
                duration=60,
                price=100.0,
                category="test",
                is_active=True
            )
            db.session.add(service)
            db.session.flush()
            self.service_id = service.id
            
            # Create test inventory data
            location = InventoryLocation(
                id="test-loc",
                name="Test Location",
                type="warehouse",
                status="active"
            )
            db.session.add(location)
            
            product = InventoryProduct(
                sku="TEST-001",
                name="Test Product",
                description="Test product for billing",
                unit_of_measure="pcs",
                is_active=True
            )
            db.session.add(product)
            db.session.flush()
            self.product_id = product.id
            
            batch = InventoryBatch(
                batch_name="TEST-BATCH-001",
                product_id=product.id,
                location_id=location.id,
                mfg_date=date.today(),
                expiry_date=date(2025, 12, 31),
                qty_available=100.0,
                unit_cost=10.0,
                selling_price=15.0,
                status="active"
            )
            db.session.add(batch)
            db.session.flush()
            self.batch_id = batch.id
            
            db.session.commit()
            print("✅ Test data setup completed")
            return True
            
        except Exception as e:
            print(f"❌ Test data setup failed: {str(e)}")
            db.session.rollback()
            return False
    
    def test_case_1_service_only_invoice(self):
        """Test Case 1: Create invoice with service only"""
        try:
            with app.test_client() as client:
                # Login as admin
                client.post('/login', data={'username': 'admin', 'password': 'admin123'})
                
                # Create service-only invoice
                response = client.post('/integrated-billing/create-professional', data={
                    'client_id': self.customer_id,
                    'service_ids[]': [self.service_id],
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
                })
                
                success = response.status_code == 200
                if success:
                    data = response.get_json()
                    success = data and data.get('success', False)
                    message = data.get('message', '') if data else 'No response data'
                else:
                    message = f"HTTP {response.status_code}"
                
                self.log_test("Service Only Invoice", success, message)
                return success
                
        except Exception as e:
            self.log_test("Service Only Invoice", False, f"Exception: {str(e)}")
            return False
    
    def test_case_2_product_only_invoice(self):
        """Test Case 2: Create invoice with product only"""
        try:
            with app.test_client() as client:
                # Login as admin
                client.post('/login', data={'username': 'admin', 'password': 'admin123'})
                
                # Create product-only invoice
                response = client.post('/integrated-billing/create-professional', data={
                    'client_id': self.customer_id,
                    'product_ids[]': [self.product_id],
                    'batch_ids[]': [self.batch_id],
                    'product_quantities[]': [2],
                    'product_prices[]': [15.0],
                    'cgst_rate': 9,
                    'sgst_rate': 9,
                    'is_interstate': False,
                    'discount_type': 'amount',
                    'discount_value': 0,
                    'additional_charges': 0,
                    'tips_amount': 0,
                    'payment_terms': 'immediate',
                    'payment_method': 'cash'
                })
                
                success = response.status_code == 200
                if success:
                    data = response.get_json()
                    success = data and data.get('success', False)
                    message = data.get('message', '') if data else 'No response data'
                else:
                    message = f"HTTP {response.status_code}"
                
                self.log_test("Product Only Invoice", success, message)
                return success
                
        except Exception as e:
            self.log_test("Product Only Invoice", False, f"Exception: {str(e)}")
            return False
    
    def test_case_3_mixed_service_product_invoice(self):
        """Test Case 3: Create invoice with both service and product"""
        try:
            with app.test_client() as client:
                # Login as admin
                client.post('/login', data={'username': 'admin', 'password': 'admin123'})
                
                # Create mixed invoice
                response = client.post('/integrated-billing/create-professional', data={
                    'client_id': self.customer_id,
                    'service_ids[]': [self.service_id],
                    'service_quantities[]': [1],
                    'product_ids[]': [self.product_id],
                    'batch_ids[]': [self.batch_id],
                    'product_quantities[]': [3],
                    'product_prices[]': [15.0],
                    'cgst_rate': 9,
                    'sgst_rate': 9,
                    'is_interstate': False,
                    'discount_type': 'percentage',
                    'discount_value': 10,
                    'additional_charges': 5,
                    'tips_amount': 10,
                    'payment_terms': 'net_15',
                    'payment_method': 'card'
                })
                
                success = response.status_code == 200
                if success:
                    data = response.get_json()
                    success = data and data.get('success', False)
                    message = data.get('message', '') if data else 'No response data'
                else:
                    message = f"HTTP {response.status_code}"
                
                self.log_test("Mixed Service+Product Invoice", success, message)
                return success
                
        except Exception as e:
            self.log_test("Mixed Service+Product Invoice", False, f"Exception: {str(e)}")
            return False
    
    def test_case_4_interstate_invoice(self):
        """Test Case 4: Create interstate invoice with IGST"""
        try:
            with app.test_client() as client:
                # Login as admin
                client.post('/login', data={'username': 'admin', 'password': 'admin123'})
                
                # Create interstate invoice
                response = client.post('/integrated-billing/create-professional', data={
                    'client_id': self.customer_id,
                    'service_ids[]': [self.service_id],
                    'service_quantities[]': [1],
                    'cgst_rate': 0,
                    'sgst_rate': 0,
                    'igst_rate': 18,
                    'is_interstate': True,
                    'discount_type': 'amount',
                    'discount_value': 0,
                    'additional_charges': 0,
                    'tips_amount': 0,
                    'payment_terms': 'immediate',
                    'payment_method': 'upi'
                })
                
                success = response.status_code == 200
                if success:
                    data = response.get_json()
                    success = data and data.get('success', False)
                    message = data.get('message', '') if data else 'No response data'
                else:
                    message = f"HTTP {response.status_code}"
                
                self.log_test("Interstate Invoice (IGST)", success, message)
                return success
                
        except Exception as e:
            self.log_test("Interstate Invoice (IGST)", False, f"Exception: {str(e)}")
            return False
    
    def test_case_5_high_discount_invoice(self):
        """Test Case 5: Create invoice with high discount"""
        try:
            with app.test_client() as client:
                # Login as admin
                client.post('/login', data={'username': 'admin', 'password': 'admin123'})
                
                # Create high discount invoice
                response = client.post('/integrated-billing/create-professional', data={
                    'client_id': self.customer_id,
                    'service_ids[]': [self.service_id],
                    'service_quantities[]': [2],
                    'cgst_rate': 9,
                    'sgst_rate': 9,
                    'is_interstate': False,
                    'discount_type': 'percentage',
                    'discount_value': 25,
                    'additional_charges': 0,
                    'tips_amount': 15,
                    'payment_terms': 'advance',
                    'payment_method': 'bank_transfer'
                })
                
                success = response.status_code == 200
                if success:
                    data = response.get_json()
                    success = data and data.get('success', False)
                    message = data.get('message', '') if data else 'No response data'
                else:
                    message = f"HTTP {response.status_code}"
                
                self.log_test("High Discount Invoice", success, message)
                return success
                
        except Exception as e:
            self.log_test("High Discount Invoice", False, f"Exception: {str(e)}")
            return False
    
    def test_case_6_multiple_quantities_invoice(self):
        """Test Case 6: Create invoice with multiple quantities"""
        try:
            with app.test_client() as client:
                # Login as admin
                client.post('/login', data={'username': 'admin', 'password': 'admin123'})
                
                # Create multiple quantities invoice
                response = client.post('/integrated-billing/create-professional', data={
                    'client_id': self.customer_id,
                    'service_ids[]': [self.service_id, self.service_id],
                    'service_quantities[]': [2.5, 1.5],
                    'product_ids[]': [self.product_id],
                    'batch_ids[]': [self.batch_id],
                    'product_quantities[]': [5.5],
                    'product_prices[]': [15.0],
                    'cgst_rate': 9,
                    'sgst_rate': 9,
                    'is_interstate': False,
                    'discount_type': 'amount',
                    'discount_value': 50,
                    'additional_charges': 25,
                    'tips_amount': 30,
                    'payment_terms': 'net_30',
                    'payment_method': 'mixed'
                })
                
                success = response.status_code == 200
                if success:
                    data = response.get_json()
                    success = data and data.get('success', False)
                    message = data.get('message', '') if data else 'No response data'
                else:
                    message = f"HTTP {response.status_code}"
                
                self.log_test("Multiple Quantities Invoice", success, message)
                return success
                
        except Exception as e:
            self.log_test("Multiple Quantities Invoice", False, f"Exception: {str(e)}")
            return False
    
    def test_case_7_zero_tax_invoice(self):
        """Test Case 7: Create invoice with zero tax"""
        try:
            with app.test_client() as client:
                # Login as admin
                client.post('/login', data={'username': 'admin', 'password': 'admin123'})
                
                # Create zero tax invoice
                response = client.post('/integrated-billing/create-professional', data={
                    'client_id': self.customer_id,
                    'service_ids[]': [self.service_id],
                    'service_quantities[]': [1],
                    'cgst_rate': 0,
                    'sgst_rate': 0,
                    'igst_rate': 0,
                    'is_interstate': False,
                    'discount_type': 'amount',
                    'discount_value': 0,
                    'additional_charges': 0,
                    'tips_amount': 0,
                    'payment_terms': 'immediate',
                    'payment_method': 'cash'
                })
                
                success = response.status_code == 200
                if success:
                    data = response.get_json()
                    success = data and data.get('success', False)
                    message = data.get('message', '') if data else 'No response data'
                else:
                    message = f"HTTP {response.status_code}"
                
                self.log_test("Zero Tax Invoice", success, message)
                return success
                
        except Exception as e:
            self.log_test("Zero Tax Invoice", False, f"Exception: {str(e)}")
            return False
    
    def test_case_8_insufficient_stock(self):
        """Test Case 8: Test insufficient stock validation"""
        try:
            with app.test_client() as client:
                # Login as admin
                client.post('/login', data={'username': 'admin', 'password': 'admin123'})
                
                # Try to create invoice with insufficient stock
                response = client.post('/integrated-billing/create-professional', data={
                    'client_id': self.customer_id,
                    'product_ids[]': [self.product_id],
                    'batch_ids[]': [self.batch_id],
                    'product_quantities[]': [200],  # More than available (100)
                    'product_prices[]': [15.0],
                    'cgst_rate': 9,
                    'sgst_rate': 9,
                    'is_interstate': False,
                    'discount_type': 'amount',
                    'discount_value': 0,
                    'additional_charges': 0,
                    'tips_amount': 0,
                    'payment_terms': 'immediate',
                    'payment_method': 'cash'
                })
                
                if response.status_code == 200:
                    data = response.get_json()
                    # Should fail due to insufficient stock
                    success = data and not data.get('success', True)
                    message = data.get('message', 'No error message') if data else 'No response data'
                else:
                    success = False
                    message = f"HTTP {response.status_code}"
                
                self.log_test("Insufficient Stock Validation", success, f"Correctly rejected: {message}")
                return success
                
        except Exception as e:
            self.log_test("Insufficient Stock Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_case_9_invalid_customer(self):
        """Test Case 9: Test invalid customer validation"""
        try:
            with app.test_client() as client:
                # Login as admin
                client.post('/login', data={'username': 'admin', 'password': 'admin123'})
                
                # Try to create invoice with invalid customer
                response = client.post('/integrated-billing/create-professional', data={
                    'client_id': 99999,  # Non-existent customer
                    'service_ids[]': [self.service_id],
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
                })
                
                if response.status_code == 200:
                    data = response.get_json()
                    # Should fail due to invalid customer
                    success = data and not data.get('success', True)
                    message = data.get('message', 'No error message') if data else 'No response data'
                else:
                    success = False
                    message = f"HTTP {response.status_code}"
                
                self.log_test("Invalid Customer Validation", success, f"Correctly rejected: {message}")
                return success
                
        except Exception as e:
            self.log_test("Invalid Customer Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_case_10_ui_page_load(self):
        """Test Case 10: Test UI page loading"""
        try:
            with app.test_client() as client:
                # Login as admin
                client.post('/login', data={'username': 'admin', 'password': 'admin123'})
                
                # Test billing page load
                response = client.get('/integrated-billing')
                success = response.status_code == 200
                
                if success:
                    html_content = response.get_data(as_text=True)
                    # Check for key UI elements
                    ui_elements = [
                        'Customer',
                        'Services',
                        'Products & Inventory',
                        'Professional Tax & Billing',
                        'Generate Professional Invoice'
                    ]
                    
                    missing_elements = [elem for elem in ui_elements if elem not in html_content]
                    if missing_elements:
                        success = False
                        message = f"Missing UI elements: {missing_elements}"
                    else:
                        message = "All UI elements present"
                else:
                    message = f"HTTP {response.status_code}"
                
                self.log_test("UI Page Load", success, message)
                return success
                
        except Exception as e:
            self.log_test("UI Page Load", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all test cases"""
        print("🚀 Starting Comprehensive Billing Tests...")
        print("=" * 60)
        
        with app.app_context():
            # Setup test data
            if not self.setup_test_data():
                print("❌ Test data setup failed. Aborting tests.")
                return False
            
            # Run all test cases
            test_methods = [
                self.test_case_1_service_only_invoice,
                self.test_case_2_product_only_invoice,
                self.test_case_3_mixed_service_product_invoice,
                self.test_case_4_interstate_invoice,
                self.test_case_5_high_discount_invoice,
                self.test_case_6_multiple_quantities_invoice,
                self.test_case_7_zero_tax_invoice,
                self.test_case_8_insufficient_stock,
                self.test_case_9_invalid_customer,
                self.test_case_10_ui_page_load
            ]
            
            passed = 0
            failed = 0
            
            for test_method in test_methods:
                try:
                    result = test_method()
                    if result:
                        passed += 1
                    else:
                        failed += 1
                except Exception as e:
                    print(f"❌ Test method {test_method.__name__} crashed: {str(e)}")
                    failed += 1
            
            print("\n" + "=" * 60)
            print("📊 Test Results Summary:")
            print(f"✅ Passed: {passed}")
            print(f"❌ Failed: {failed}")
            print(f"📈 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
            
            return passed > failed

def run_comprehensive_billing_tests():
    """Main function to run all billing tests"""
    runner = BillingTestRunner()
    return runner.run_all_tests()

if __name__ == "__main__":
    success = run_comprehensive_billing_tests()
    if success:
        print("\n🎉 Billing system tests completed successfully!")
    else:
        print("\n⚠️ Some billing tests failed. Check the output above.")
