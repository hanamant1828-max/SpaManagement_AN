
#!/usr/bin/env python3
"""
Comprehensive Inventory Management Module Testing Script
Tests all inventory functionality including consumption tracking
"""

import requests
import json
from datetime import datetime
import sys

class InventoryModuleTester:
    def __init__(self, base_url="http://0.0.0.0:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
        # Login first
        self.login()
    
    def login(self):
        """Login to get session"""
        try:
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            response = self.session.post(f"{self.base_url}/login", data=login_data)
            if response.status_code == 200:
                print("✅ Successfully logged in for testing")
                return True
            else:
                print(f"❌ Login failed with status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def log_result(self, test_name, status, message, priority="Medium"):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {message}")
    
    def test_inventory_page_access(self):
        """Test basic inventory page access"""
        print("\n🧪 Testing Inventory Page Access...")
        
        try:
            response = self.session.get(f"{self.base_url}/inventory")
            if response.status_code == 200:
                self.log_result("Inventory Page Access", "PASS", "Inventory page loads successfully")
                
                content = response.text.lower()
                if "inventory management" in content:
                    self.log_result("Inventory Page Content", "PASS", "Inventory management header found")
                if "add item" in content:
                    self.log_result("Add Item Button", "PASS", "Add item functionality available")
                if "consumption tracking" in content:
                    self.log_result("Consumption Tracking Tab", "PASS", "Consumption tracking tab available")
                    
                return True
            else:
                self.log_result("Inventory Page Access", "FAIL", f"Page returned status {response.status_code}", "High")
                return False
        except Exception as e:
            self.log_result("Inventory Page Access", "FAIL", f"Error accessing page: {str(e)}", "High")
            return False
    
    def test_inventory_api_endpoints(self):
        """Test inventory API endpoints"""
        print("\n🧪 Testing Inventory API Endpoints...")
        
        # Test inventory status endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/inventory/status/all")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.log_result("Inventory Status API", "PASS", f"API returns {len(data.get('items', []))} items")
                else:
                    self.log_result("Inventory Status API", "FAIL", "API response format incorrect", "Medium")
            else:
                self.log_result("Inventory Status API", "FAIL", f"API returned status {response.status_code}", "Medium")
        except Exception as e:
            self.log_result("Inventory Status API", "FAIL", f"API error: {str(e)}", "Medium")
        
        # Test inventory valuation endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/inventory/valuation")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.log_result("Inventory Valuation API", "PASS", "Valuation API working correctly")
                else:
                    self.log_result("Inventory Valuation API", "FAIL", "Valuation API response incorrect", "Medium")
            else:
                self.log_result("Inventory Valuation API", "FAIL", f"API returned status {response.status_code}", "Medium")
        except Exception as e:
            self.log_result("Inventory Valuation API", "FAIL", f"API error: {str(e)}", "Medium")
        
        # Test consumption entries endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/inventory/consumption-entries")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.log_result("Consumption Entries API", "PASS", f"Found {len(data.get('entries', []))} consumption entries")
                else:
                    self.log_result("Consumption Entries API", "FAIL", "Consumption API response incorrect", "Medium")
            else:
                self.log_result("Consumption Entries API", "FAIL", f"API returned status {response.status_code}", "Medium")
        except Exception as e:
            self.log_result("Consumption Entries API", "FAIL", f"API error: {str(e)}", "Medium")
    
    def test_inventory_creation(self):
        """Test inventory item creation"""
        print("\n🧪 Testing Inventory Item Creation...")
        
        test_item_data = {
            'name': 'Test Hair Oil',
            'description': 'Test inventory item for automation',
            'category_id': '',  # Will use fallback
            'current_stock': '50',
            'min_stock_level': '10',
            'cost_price': '25.00',
            'selling_price': '40.00',
            'supplier': 'Test Supplier',
            'expiry_date': '2025-12-31'
        }
        
        try:
            response = self.session.post(f"{self.base_url}/inventory/create", data=test_item_data)
            if response.status_code == 302:  # Redirect after successful creation
                self.log_result("Inventory Creation", "PASS", "Test inventory item created successfully")
                return True
            elif response.status_code == 200:
                # Check if there are validation errors in the response
                if "created successfully" in response.text.lower():
                    self.log_result("Inventory Creation", "PASS", "Inventory item created")
                    return True
                else:
                    self.log_result("Inventory Creation", "FAIL", "Creation form validation failed", "Medium")
                    return False
            else:
                self.log_result("Inventory Creation", "FAIL", f"Creation returned status {response.status_code}", "Medium")
                return False
        except Exception as e:
            self.log_result("Inventory Creation", "FAIL", f"Creation error: {str(e)}", "Medium")
            return False
    
    def test_consumption_tracking_apis(self):
        """Test consumption tracking API endpoints"""
        print("\n🧪 Testing Consumption Tracking APIs...")
        
        # Get first available inventory item
        try:
            response = self.session.get(f"{self.base_url}/api/inventory/status/all")
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                if items:
                    test_item_id = items[0]['id']
                    
                    # Test open inventory item
                    open_data = {
                        'quantity': 1,
                        'reason': 'Test opening',
                        'batch_number': 'TEST001'
                    }
                    
                    try:
                        response = self.session.post(
                            f"{self.base_url}/api/inventory/{test_item_id}/open",
                            json=open_data,
                            headers={'Content-Type': 'application/json'}
                        )
                        if response.status_code == 200:
                            result = response.json()
                            if result.get('status') == 'success':
                                self.log_result("Open Inventory API", "PASS", "Successfully opened inventory item")
                            else:
                                self.log_result("Open Inventory API", "FAIL", f"API error: {result.get('message')}", "Medium")
                        else:
                            self.log_result("Open Inventory API", "FAIL", f"API returned status {response.status_code}", "Medium")
                    except Exception as e:
                        self.log_result("Open Inventory API", "FAIL", f"API error: {str(e)}", "Medium")
                    
                    # Test deduct quantity
                    deduct_data = {
                        'quantity': 0.5,
                        'unit': 'pcs',
                        'reason': 'Test deduction',
                        'reference_type': 'manual'
                    }
                    
                    try:
                        response = self.session.post(
                            f"{self.base_url}/api/inventory/{test_item_id}/deduct",
                            json=deduct_data,
                            headers={'Content-Type': 'application/json'}
                        )
                        if response.status_code == 200:
                            result = response.json()
                            if result.get('status') == 'success':
                                self.log_result("Deduct Inventory API", "PASS", "Successfully deducted inventory")
                            else:
                                self.log_result("Deduct Inventory API", "FAIL", f"API error: {result.get('message')}", "Medium")
                        else:
                            self.log_result("Deduct Inventory API", "FAIL", f"API returned status {response.status_code}", "Medium")
                    except Exception as e:
                        self.log_result("Deduct Inventory API", "FAIL", f"API error: {str(e)}", "Medium")
                        
                else:
                    self.log_result("Consumption Testing", "FAIL", "No inventory items available for testing", "Medium")
            else:
                self.log_result("Consumption Testing", "FAIL", "Could not fetch inventory items", "Medium")
        except Exception as e:
            self.log_result("Consumption Testing", "FAIL", f"Error: {str(e)}", "Medium")
    
    def test_inventory_filters_and_tabs(self):
        """Test inventory filtering and tab functionality"""
        print("\n🧪 Testing Inventory Filters and Tabs...")
        
        # Test different inventory filters
        filters = ['all', 'low_stock', 'expiring']
        
        for filter_type in filters:
            try:
                response = self.session.get(f"{self.base_url}/inventory?filter={filter_type}")
                if response.status_code == 200:
                    self.log_result(f"Filter {filter_type}", "PASS", f"Filter '{filter_type}' loads successfully")
                else:
                    self.log_result(f"Filter {filter_type}", "FAIL", f"Filter returned status {response.status_code}", "Low")
            except Exception as e:
                self.log_result(f"Filter {filter_type}", "FAIL", f"Filter error: {str(e)}", "Low")
        
        # Test search functionality
        try:
            response = self.session.get(f"{self.base_url}/inventory?search=oil")
            if response.status_code == 200:
                self.log_result("Inventory Search", "PASS", "Search functionality working")
            else:
                self.log_result("Inventory Search", "FAIL", f"Search returned status {response.status_code}", "Medium")
        except Exception as e:
            self.log_result("Inventory Search", "FAIL", f"Search error: {str(e)}", "Medium")
    
    def test_inventory_alerts_system(self):
        """Test inventory alerts and notifications"""
        print("\n🧪 Testing Inventory Alerts System...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/inventory/alerts")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    alerts = data.get('alerts', [])
                    alert_counts = data.get('alert_counts', {})
                    self.log_result("Inventory Alerts API", "PASS", f"Found {len(alerts)} alerts")
                    self.log_result("Alert Counts", "PASS", f"Low stock items: {alert_counts.get('low_stock', 0)}")
                else:
                    self.log_result("Inventory Alerts API", "FAIL", "Alerts API response incorrect", "Medium")
            else:
                self.log_result("Inventory Alerts API", "FAIL", f"API returned status {response.status_code}", "Medium")
        except Exception as e:
            self.log_result("Inventory Alerts API", "FAIL", f"API error: {str(e)}", "Medium")
    
    def run_all_tests(self):
        """Run all inventory tests"""
        print("🚀 Starting Comprehensive Inventory Management Module Testing")
        print("=" * 70)
        
        # Run all test methods
        self.test_inventory_page_access()
        self.test_inventory_api_endpoints()
        self.test_inventory_creation()
        self.test_consumption_tracking_apis()
        self.test_inventory_filters_and_tabs()
        self.test_inventory_alerts_system()
        
        # Generate summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate and display test summary"""
        print("\n" + "=" * 70)
        print("📊 INVENTORY MODULE TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  • {result['test']}: {result['message']}")
        
        print(f"\n💾 Detailed results saved to: inventory_test_results.json")
        
        # Save detailed results to file
        with open('inventory_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)

if __name__ == "__main__":
    tester = InventoryModuleTester()
    tester.run_all_tests()
