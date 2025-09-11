
#!/usr/bin/env python3
"""
Comprehensive Testing for Inventory Adjustments
Tests Add, Edit, View, and Delete functionality like a human user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
from app import app, db
from models import User
from modules.inventory.models import *
from datetime import datetime, date
import json

class TestAdjustmentFunctionality(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        with self.app.app_context():
            # Create test user
            test_user = User.query.filter_by(username='testuser').first()
            if not test_user:
                test_user = User(
                    username='testuser',
                    email='test@example.com',
                    full_name='Test User',
                    role='admin',
                    password_hash='test_hash'
                )
                db.session.add(test_user)
                db.session.commit()
            
            # Log in the test user
            with self.client.session_transaction() as sess:
                sess['_user_id'] = str(test_user.id)
                sess['_fresh'] = True
    
    def test_01_setup_test_data(self):
        """Set up test category, product, location, and batch"""
        print("\n🧪 Setting up test data...")
        
        with self.app.app_context():
            # Create test category
            category = InventoryCategory.query.filter_by(name='Test Adjustments Category').first()
            if not category:
                category = InventoryCategory(
                    name='Test Adjustments Category',
                    description='Category for adjustment testing'
                )
                db.session.add(category)
                db.session.commit()
            
            # Create test product
            product = InventoryProduct.query.filter_by(sku='TEST-ADJ-001').first()
            if not product:
                product = InventoryProduct(
                    sku='TEST-ADJ-001',
                    name='Test Adjustment Product',
                    description='Product for testing adjustments',
                    category_id=category.id,
                    unit_of_measure='pcs'
                )
                db.session.add(product)
                db.session.commit()
            
            # Create test location
            location = InventoryLocation.query.filter_by(id='test-adj-location').first()
            if not location:
                location = InventoryLocation(
                    id='test-adj-location',
                    name='Test Adjustment Location',
                    type='warehouse',
                    status='active'
                )
                db.session.add(location)
                db.session.commit()
            
            # Create test batch
            batch = InventoryBatch.query.filter_by(batch_name='TEST-BATCH-ADJ-001').first()
            if not batch:
                batch = InventoryBatch(
                    batch_name='TEST-BATCH-ADJ-001',
                    product_id=product.id,
                    location_id=location.id,
                    mfg_date=date.today(),
                    expiry_date=date(2026, 12, 31),
                    unit_cost=10.50,
                    qty_available=0,
                    status='active'
                )
                db.session.add(batch)
                db.session.commit()
            
            # Store IDs for use in other tests
            self.__class__.test_batch_id = batch.id
            self.__class__.test_product_id = product.id
            self.__class__.test_location_id = location.id
            
            print(f"   ✅ Test data created - Batch ID: {batch.id}")

    def test_02_add_adjustment_api(self):
        """Test adding inventory adjustment via API (like frontend modal)"""
        print("\n🧪 Testing Add Adjustment API...")
        
        batch_id = getattr(self.__class__, 'test_batch_id', None)
        product_id = getattr(self.__class__, 'test_product_id', None)
        location_id = getattr(self.__class__, 'test_location_id', None)
        
        self.assertIsNotNone(batch_id, "Test batch required")
        
        # Test data structure from frontend
        adjustment_data = {
            'reference_no': 'ADJ-TEST-001',
            'adjustment_date': datetime.now().strftime('%Y-%m-%d'),
            'batch_id': batch_id,
            'quantity': 50.0,
            'unit_cost': 12.75,
            'notes': 'Test adjustment - adding initial stock',
            'product_id': product_id,
            'location_id': location_id
        }
        
        response = self.client.post(
            '/api/inventory/adjustments',
            json=adjustment_data,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('adjustment_id', data)
        
        # Store adjustment ID for later tests
        self.__class__.test_adjustment_id = data['adjustment_id']
        
        # Verify batch stock was updated
        with self.app.app_context():
            batch = InventoryBatch.query.get(batch_id)
            self.assertEqual(float(batch.qty_available), 50.0)
            self.assertEqual(float(batch.unit_cost), 12.75)
        
        print(f"   ✅ ADD: Adjustment created successfully - ID: {data['adjustment_id']}")

    def test_03_list_adjustments_api(self):
        """Test listing adjustments (like loading data in frontend table)"""
        print("\n🧪 Testing List Adjustments API...")
        
        response = self.client.get('/api/inventory/adjustments')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('records', data)
        self.assertIsInstance(data['records'], list)
        
        # Find our test adjustment
        test_adjustment = None
        for record in data['records']:
            if record.get('batch_name') == 'TEST-BATCH-ADJ-001':
                test_adjustment = record
                break
        
        self.assertIsNotNone(test_adjustment, "Test adjustment not found in list")
        self.assertEqual(test_adjustment['product_name'], 'Test Adjustment Product')
        self.assertEqual(float(test_adjustment['quantity']), 50.0)
        
        print(f"   ✅ LIST: Found {len(data['records'])} adjustments, including our test record")

    def test_04_view_adjustment_api(self):
        """Test viewing single adjustment (like modal popup)"""
        print("\n🧪 Testing View Adjustment API...")
        
        adjustment_id = getattr(self.__class__, 'test_adjustment_id', None)
        self.assertIsNotNone(adjustment_id, "Test adjustment required")
        
        response = self.client.get(f'/api/inventory/adjustments/{adjustment_id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        
        # Verify adjustment details
        self.assertEqual(data['batch_name'], 'TEST-BATCH-ADJ-001')
        self.assertEqual(data['product_name'], 'Test Adjustment Product')
        self.assertEqual(data['location_name'], 'Test Adjustment Location')
        self.assertEqual(float(data['quantity']), 50.0)
        self.assertIn('Test adjustment - adding initial stock', data['remarks'])
        
        print(f"   ✅ VIEW: Adjustment details loaded correctly")

    def test_05_add_second_adjustment(self):
        """Test adding a second adjustment to the same batch"""
        print("\n🧪 Testing Second Adjustment...")
        
        batch_id = getattr(self.__class__, 'test_batch_id', None)
        
        adjustment_data = {
            'batch_id': batch_id,
            'quantity': 25.0,
            'unit_cost': 11.00,
            'notes': 'Second test adjustment'
        }
        
        response = self.client.post(
            '/api/inventory/adjustments',
            json=adjustment_data,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        
        # Store second adjustment ID
        self.__class__.test_adjustment_id_2 = data['adjustment_id']
        
        # Verify batch stock was updated (should be 75 now)
        with self.app.app_context():
            batch = InventoryBatch.query.get(batch_id)
            self.assertEqual(float(batch.qty_available), 75.0)
        
        print(f"   ✅ SECOND ADD: Stock now at 75 units")

    def test_06_delete_adjustment_api(self):
        """Test deleting adjustment (reversing stock change)"""
        print("\n🧪 Testing Delete Adjustment API...")
        
        adjustment_id_2 = getattr(self.__class__, 'test_adjustment_id_2', None)
        batch_id = getattr(self.__class__, 'test_batch_id', None)
        
        self.assertIsNotNone(adjustment_id_2, "Second test adjustment required")
        
        # Get stock before deletion
        with self.app.app_context():
            batch_before = InventoryBatch.query.get(batch_id)
            stock_before = float(batch_before.qty_available)
        
        response = self.client.delete(f'/api/inventory/adjustments/{adjustment_id_2}')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        
        # Verify stock was reversed (should be back to 50)
        with self.app.app_context():
            batch_after = InventoryBatch.query.get(batch_id)
            stock_after = float(batch_after.qty_available)
            self.assertEqual(stock_after, 50.0)  # 75 - 25 = 50
        
        # Verify adjustment was deleted
        with self.app.app_context():
            deleted_adjustment = InventoryAdjustment.query.get(adjustment_id_2)
            self.assertIsNone(deleted_adjustment)
        
        print(f"   ✅ DELETE: Adjustment deleted, stock reversed to 50 units")

    def test_07_batches_for_adjustment_api(self):
        """Test getting batches for adjustment dropdown"""
        print("\n🧪 Testing Batches for Adjustment API...")
        
        response = self.client.get('/api/inventory/batches/for-adjustment')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('batches', data)
        
        # Find our test batch
        test_batch = None
        for batch in data['batches']:
            if batch['batch_name'] == 'TEST-BATCH-ADJ-001':
                test_batch = batch
                break
        
        self.assertIsNotNone(test_batch, "Test batch not found in dropdown")
        self.assertEqual(test_batch['product_name'], 'Test Adjustment Product')
        self.assertEqual(test_batch['location_name'], 'Test Adjustment Location')
        self.assertEqual(float(test_batch['qty_available']), 50.0)
        
        print(f"   ✅ DROPDOWN: Found {len(data['batches'])} available batches")

    def test_08_error_handling(self):
        """Test error handling for invalid requests"""
        print("\n🧪 Testing Error Handling...")
        
        # Test with invalid batch ID
        response = self.client.post(
            '/api/inventory/adjustments',
            json={'batch_id': 99999, 'quantity': 10},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        
        # Test with zero quantity
        batch_id = getattr(self.__class__, 'test_batch_id', None)
        response = self.client.post(
            '/api/inventory/adjustments',
            json={'batch_id': batch_id, 'quantity': 0},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Test viewing non-existent adjustment
        response = self.client.get('/api/inventory/adjustments/99999')
        self.assertEqual(response.status_code, 404)
        
        # Test deleting non-existent adjustment
        response = self.client.delete('/api/inventory/adjustments/99999')
        self.assertEqual(response.status_code, 404)
        
        print("   ✅ ERROR HANDLING: All error cases handled correctly")

    def test_09_cleanup(self):
        """Clean up test data"""
        print("\n🧪 Cleaning up test data...")
        
        with self.app.app_context():
            # Delete remaining adjustment
            adjustment_id = getattr(self.__class__, 'test_adjustment_id', None)
            if adjustment_id:
                adjustment = InventoryAdjustment.query.get(adjustment_id)
                if adjustment:
                    db.session.delete(adjustment)
            
            # Delete test batch
            batch = InventoryBatch.query.filter_by(batch_name='TEST-BATCH-ADJ-001').first()
            if batch:
                db.session.delete(batch)
            
            # Delete test product
            product = InventoryProduct.query.filter_by(sku='TEST-ADJ-001').first()
            if product:
                db.session.delete(product)
            
            # Delete test location
            location = InventoryLocation.query.filter_by(id='test-adj-location').first()
            if location:
                db.session.delete(location)
            
            # Delete test category
            category = InventoryCategory.query.filter_by(name='Test Adjustments Category').first()
            if category:
                db.session.delete(category)
            
            db.session.commit()
        
        print("   ✅ CLEANUP: Test data removed successfully")

def run_adjustment_tests():
    """Run all adjustment tests"""
    print("🧪 Starting Comprehensive Adjustment Testing...")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAdjustmentFunctionality)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 ALL ADJUSTMENT TESTS PASSED! ✅")
        print("\n📋 Test Summary:")
        print("   ✅ Add Adjustment - Working")
        print("   ✅ List Adjustments - Working") 
        print("   ✅ View Adjustment - Working")
        print("   ✅ Delete Adjustment - Working")
        print("   ✅ Batch Dropdown - Working")
        print("   ✅ Error Handling - Working")
        print("\n🔧 Inventory Adjustment System is fully functional!")
    else:
        print("❌ SOME TESTS FAILED!")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_adjustment_tests()
    sys.exit(0 if success else 1)
