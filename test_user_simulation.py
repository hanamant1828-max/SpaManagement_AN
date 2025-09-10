
#!/usr/bin/env python3
"""
User Interaction Simulation Tests
These tests simulate exactly how a human user would interact with the system
"""

import time
import json
from app import app, db
from modules.inventory.models import InventoryProduct, InventoryCategory, InventoryLocation, InventoryBatch

class UserSimulator:
    """Simulates human user interactions with the inventory system"""
    
    def __init__(self):
        self.app = app
        self.client = app.test_client()
        self.results = []
    
    def log_action(self, action, success, details=""):
        """Log user action results"""
        result = {
            'timestamp': time.time(),
            'action': action,
            'success': success,
            'details': details
        }
        self.results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} USER ACTION: {action} - {details}")
    
    def simulate_add_product_workflow(self):
        """Simulate: User opens Product Master, clicks Add Product, fills form, saves"""
        print("\n👤 SIMULATING: User wants to add a new product...")
        
        # Step 1: User navigates to inventory dashboard
        with self.app.app_context():
            # Step 2: User loads categories for dropdown
            response = self.client.get('/api/inventory/categories')
            if response.status_code == 200:
                categories = response.get_json()
                self.log_action("Load Categories", True, f"Found {len(categories)} categories")
            else:
                self.log_action("Load Categories", False, f"Status: {response.status_code}")
                return False
            
            # Step 3: User fills product form and submits
            new_product_data = {
                'name': 'User Simulation Product',
                'description': 'Added through user simulation',
                'sku': f'SIM-{int(time.time())}',
                'category_id': categories[0]['id'],
                'unit_of_measure': 'bottle',
                'barcode': f'SIM{int(time.time())}'
            }
            
            response = self.client.post('/api/inventory/products',
                json=new_product_data,
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    self.log_action("Create Product", True, f"Product ID: {data.get('product_id')}")
                    return data.get('product_id')
                else:
                    self.log_action("Create Product", False, data.get('error', 'Unknown error'))
            else:
                self.log_action("Create Product", False, f"Status: {response.status_code}")
        
        return False
    
    def simulate_edit_product_workflow(self, product_id):
        """Simulate: User clicks Edit on a product, modifies data, saves"""
        print(f"\n👤 SIMULATING: User wants to edit product ID {product_id}...")
        
        with self.app.app_context():
            # Step 1: User clicks edit - system loads product data
            response = self.client.get(f'/api/inventory/products/{product_id}')
            if response.status_code == 200:
                product = response.get_json()
                self.log_action("Load Product for Edit", True, f"Product: {product['name']}")
            else:
                self.log_action("Load Product for Edit", False, f"Status: {response.status_code}")
                return False
            
            # Step 2: User modifies data and saves
            updated_data = {
                'name': product['name'] + ' (Updated)',
                'description': product['description'] + ' - Modified by simulation'
            }
            
            response = self.client.put(f'/api/inventory/products/{product_id}',
                json=updated_data,
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    self.log_action("Update Product", True, "Product updated successfully")
                    return True
                else:
                    self.log_action("Update Product", False, data.get('error', 'Unknown error'))
            else:
                self.log_action("Update Product", False, f"Status: {response.status_code}")
        
        return False
    
    def simulate_add_batch_workflow(self, product_id):
        """Simulate: User wants to add a batch for a product"""
        print(f"\n👤 SIMULATING: User wants to add batch for product ID {product_id}...")
        
        with self.app.app_context():
            # Step 1: User loads locations for dropdown
            response = self.client.get('/api/inventory/locations')
            if response.status_code == 200:
                data = response.get_json()
                locations = data.get('locations', [])
                self.log_action("Load Locations", True, f"Found {len(locations)} locations")
            else:
                self.log_action("Load Locations", False, f"Status: {response.status_code}")
                return False
            
            if not locations:
                self.log_action("Add Batch", False, "No locations available")
                return False
            
            # Step 2: User fills batch form
            batch_data = {
                'batch_name': f'SIM-BATCH-{int(time.time())}',
                'product_id': product_id,
                'location_id': locations[0]['id'],
                'mfg_date': '2025-01-15',
                'expiry_date': '2026-01-15',
                'unit_cost': 15.75,
                'selling_price': 25.00
            }
            
            response = self.client.post('/api/inventory/batches',
                json=batch_data,
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    batch_id = data.get('batch_id')
                    self.log_action("Create Batch", True, f"Batch ID: {batch_id}")
                    return batch_id
                else:
                    self.log_action("Create Batch", False, data.get('error', 'Unknown error'))
            else:
                self.log_action("Create Batch", False, f"Status: {response.status_code}")
        
        return False
    
    def simulate_stock_adjustment_workflow(self, batch_id):
        """Simulate: User adds stock to a batch"""
        print(f"\n👤 SIMULATING: User wants to add stock to batch ID {batch_id}...")
        
        with self.app.app_context():
            # User adds stock via adjustment
            adjustment_data = {
                'batch_id': batch_id,
                'quantity': 50.0,
                'unit_cost': 15.75,
                'notes': 'Initial stock added via user simulation'
            }
            
            response = self.client.post('/api/inventory/adjustments',
                json=adjustment_data,
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    self.log_action("Add Stock", True, "Added 50 units to batch")
                    return True
                else:
                    self.log_action("Add Stock", False, data.get('error', 'Unknown error'))
            else:
                self.log_action("Add Stock", False, f"Status: {response.status_code}")
        
        return False
    
    def simulate_stock_consumption_workflow(self, batch_id):
        """Simulate: User consumes stock from a batch"""
        print(f"\n👤 SIMULATING: User wants to consume stock from batch ID {batch_id}...")
        
        with self.app.app_context():
            # User consumes stock
            consumption_data = {
                'batch_id': batch_id,
                'quantity': 10.0,
                'issued_to': 'Spa Treatment Room A',
                'reference': f'SIM-CONSUMPTION-{int(time.time())}',
                'notes': 'Used for facial treatment - simulation'
            }
            
            response = self.client.post('/api/inventory/consumption',
                json=consumption_data,
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    self.log_action("Consume Stock", True, "Consumed 10 units from batch")
                    return True
                else:
                    self.log_action("Consume Stock", False, data.get('error', 'Unknown error'))
            else:
                self.log_action("Consume Stock", False, f"Status: {response.status_code}")
        
        return False
    
    def simulate_view_reports_workflow(self):
        """Simulate: User views various reports and data"""
        print("\n👤 SIMULATING: User wants to view inventory reports...")
        
        with self.app.app_context():
            # User views products list
            response = self.client.get('/api/inventory/products')
            if response.status_code == 200:
                products = response.get_json()
                self.log_action("View Products Report", True, f"Found {len(products)} products")
            else:
                self.log_action("View Products Report", False, f"Status: {response.status_code}")
                return False
            
            # User views batches list
            response = self.client.get('/api/inventory/batches')
            if response.status_code == 200:
                data = response.get_json()
                batches = data.get('batches', [])
                self.log_action("View Batches Report", True, f"Found {len(batches)} batches")
            else:
                self.log_action("View Batches Report", False, f"Status: {response.status_code}")
                return False
            
            # User views consumption records
            response = self.client.get('/api/inventory/consumption')
            if response.status_code == 200:
                consumption = response.get_json()
                self.log_action("View Consumption Report", True, f"Found {len(consumption)} records")
                return True
            else:
                self.log_action("View Consumption Report", False, f"Status: {response.status_code}")
        
        return False
    
    def run_complete_user_simulation(self):
        """Run complete user workflow simulation"""
        print("🎭 STARTING COMPLETE USER WORKFLOW SIMULATION")
        print("=" * 60)
        
        # Simulate complete user journey
        product_id = self.simulate_add_product_workflow()
        if not product_id:
            return False
        
        if not self.simulate_edit_product_workflow(product_id):
            return False
        
        batch_id = self.simulate_add_batch_workflow(product_id)
        if not batch_id:
            return False
        
        if not self.simulate_stock_adjustment_workflow(batch_id):
            return False
        
        if not self.simulate_stock_consumption_workflow(batch_id):
            return False
        
        if not self.simulate_view_reports_workflow():
            return False
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 USER SIMULATION SUMMARY")
        print("=" * 60)
        
        total_actions = len(self.results)
        successful_actions = len([r for r in self.results if r['success']])
        
        print(f"📊 Total User Actions: {total_actions}")
        print(f"✅ Successful Actions: {successful_actions}")
        print(f"❌ Failed Actions: {total_actions - successful_actions}")
        print(f"📈 Success Rate: {(successful_actions/total_actions*100):.1f}%")
        
        if successful_actions == total_actions:
            print("\n🎉 USER SIMULATION COMPLETED SUCCESSFULLY!")
            print("✅ All user workflows are working perfectly!")
            return True
        else:
            print(f"\n⚠️ {total_actions - successful_actions} USER ACTIONS FAILED")
            print("🔧 Please review the failed actions above")
            return False

def run_user_simulation():
    """Main function to run user simulation"""
    simulator = UserSimulator()
    return simulator.run_complete_user_simulation()

if __name__ == "__main__":
    import sys
    success = run_user_simulation()
    sys.exit(0 if success else 1)
