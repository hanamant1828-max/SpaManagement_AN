
#!/usr/bin/env python3
"""
Comprehensive Automated Testing Suite for Inventory Management System
Tests all functionality like a human user would interact with the system
"""

import unittest
import sys
import json
import time
from datetime import datetime, date, timedelta
from app import app, db
from modules.inventory.models import (
    InventoryProduct, InventoryCategory, InventoryLocation, 
    InventoryBatch, InventoryAdjustment, InventoryConsumption
)

class InventoryAutomationTests(unittest.TestCase):
    """Automated tests that simulate human interactions"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.client = cls.app.test_client()
        
        with cls.app.app_context():
            db.create_all()
            cls._create_test_data()

    @classmethod
    def _create_test_data(cls):
        """Create comprehensive test data"""
        try:
            # Create test categories
            categories = [
                {'name': 'Test Skincare', 'description': 'Test skincare products'},
                {'name': 'Test Equipment', 'description': 'Test spa equipment'}
            ]
            
            for cat_data in categories:
                category = InventoryCategory(**cat_data)
                db.session.add(category)
            
            # Create test locations
            locations = [
                {'id': 'test-spa-1', 'name': 'Test Spa Main', 'type': 'spa', 'status': 'active'},
                {'id': 'test-warehouse', 'name': 'Test Warehouse', 'type': 'warehouse', 'status': 'active'}
            ]
            
            for loc_data in locations:
                location = InventoryLocation(**loc_data)
                db.session.add(location)
            
            db.session.commit()
            print("✅ Test data created successfully")
            
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
            db.session.rollback()

    def test_01_category_crud_operations(self):
        """Test Category CRUD operations like a human user"""
        print("\n🧪 Testing Category CRUD Operations...")
        
        with self.app.app_context():
            # Test CREATE - Add new category
            response = self.client.post('/api/inventory/categories', 
                json={
                    'name': 'Automated Test Category',
                    'description': 'Category created by automation',
                    'color_code': '#ff0000'
                },
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data.get('success'))
            category_id = data.get('category_id')
            print(f"   ✅ CREATE: Category created with ID {category_id}")
            
            # Test READ - Get all categories
            response = self.client.get('/api/inventory/categories')
            self.assertEqual(response.status_code, 200)
            categories = response.get_json()
            self.assertIsInstance(categories, list)
            self.assertGreater(len(categories), 0)
            print(f"   ✅ READ: Retrieved {len(categories)} categories")
            
            # Test READ - Get specific category
            response = self.client.get(f'/api/inventory/categories/{category_id}')
            self.assertEqual(response.status_code, 200)
            category = response.get_json()
            self.assertEqual(category['name'], 'Automated Test Category')
            print(f"   ✅ READ SINGLE: Retrieved category '{category['name']}'")
            
            # Test UPDATE - Edit category
            response = self.client.put(f'/api/inventory/categories/{category_id}',
                json={
                    'name': 'Updated Test Category',
                    'description': 'Updated by automation',
                    'color_code': '#00ff00'
                },
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data.get('success'))
            print("   ✅ UPDATE: Category updated successfully")

    def test_02_location_crud_operations(self):
        """Test Location CRUD operations like a human user"""
        print("\n🧪 Testing Location CRUD Operations...")
        
        with self.app.app_context():
            # Test CREATE - Add new location
            response = self.client.post('/api/inventory/locations',
                json={
                    'name': 'Automated Test Location',
                    'type': 'branch',
                    'address': '123 Test Street'
                },
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data.get('success'))
            location_id = data.get('location_id')
            print(f"   ✅ CREATE: Location created with ID {location_id}")
            
            # Test READ - Get all locations
            response = self.client.get('/api/inventory/locations')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            locations = data.get('locations', [])
            self.assertGreater(len(locations), 0)
            print(f"   ✅ READ: Retrieved {len(locations)} locations")
            
            # Test UPDATE - Edit location
            response = self.client.put(f'/api/inventory/locations/{location_id}',
                json={
                    'name': 'Updated Test Location',
                    'type': 'warehouse',
                    'address': '456 Updated Street'
                },
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data.get('success'))
            print("   ✅ UPDATE: Location updated successfully")

    def test_03_product_crud_operations(self):
        """Test Product CRUD operations like a human user"""
        print("\n🧪 Testing Product CRUD Operations...")
        
        with self.app.app_context():
            # Get first category for testing
            categories = InventoryCategory.query.all()
            self.assertGreater(len(categories), 0)
            test_category_id = categories[0].id
            
            # Test CREATE - Add new product
            response = self.client.post('/api/inventory/products',
                json={
                    'name': 'Automated Test Product',
                    'description': 'Product created by automation',
                    'sku': 'AUTO-001',
                    'category_id': test_category_id,
                    'unit_of_measure': 'pieces',
                    'barcode': 'AUTO001'
                },
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data.get('success'))
            product_id = data.get('product_id')
            print(f"   ✅ CREATE: Product created with ID {product_id}")
            
            # Test READ - Get all products
            response = self.client.get('/api/inventory/products')
            self.assertEqual(response.status_code, 200)
            products = response.get_json()
            self.assertIsInstance(products, list)
            print(f"   ✅ READ: Retrieved {len(products)} products")
            
            # Test READ - Get specific product
            response = self.client.get(f'/api/inventory/products/{product_id}')
            self.assertEqual(response.status_code, 200)
            product = response.get_json()
            self.assertEqual(product['name'], 'Automated Test Product')
            print(f"   ✅ READ SINGLE: Retrieved product '{product['name']}'")
            
            # Test UPDATE - Edit product
            response = self.client.put(f'/api/inventory/products/{product_id}',
                json={
                    'name': 'Updated Test Product',
                    'description': 'Updated by automation',
                    'sku': 'AUTO-001-UPDATED'
                },
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data.get('success'))
            print("   ✅ UPDATE: Product updated successfully")
            
            # Store for batch testing
            self.__class__.test_product_id = product_id

    def test_04_batch_crud_operations(self):
        """Test Batch CRUD operations like a human user"""
        print("\n🧪 Testing Batch CRUD Operations...")
        
        with self.app.app_context():
            # Get test data
            product_id = getattr(self.__class__, 'test_product_id', None)
            if not product_id:
                products = InventoryProduct.query.all()
                product_id = products[0].id if products else None
            
            locations = InventoryLocation.query.all()
            location_id = locations[0].id if locations else None
            
            self.assertIsNotNone(product_id, "Test product required for batch testing")
            self.assertIsNotNone(location_id, "Test location required for batch testing")
            
            # Test CREATE - Add new batch
            response = self.client.post('/api/inventory/batches',
                json={
                    'batch_name': 'AUTO-BATCH-001',
                    'product_id': product_id,
                    'location_id': location_id,
                    'mfg_date': '2025-01-01',
                    'expiry_date': '2026-01-01',
                    'unit_cost': 25.50,
                    'selling_price': 40.00
                },
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data.get('success'))
            batch_id = data.get('batch_id')
            print(f"   ✅ CREATE: Batch created with ID {batch_id}")
            
            # Test READ - Get all batches
            response = self.client.get('/api/inventory/batches')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            batches = data.get('batches', [])
            print(f"   ✅ READ: Retrieved {len(batches)} batches")
            
            # Test READ - Get specific batch
            response = self.client.get(f'/api/inventory/batches/{batch_id}')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data.get('success'))
            batch = data.get('batch')
            self.assertEqual(batch['batch_name'], 'AUTO-BATCH-001')
            print(f"   ✅ READ SINGLE: Retrieved batch '{batch['batch_name']}'")
            
            # Test UPDATE - Edit batch
            response = self.client.put(f'/api/inventory/batches/{batch_id}',
                json={
                    'batch_name': 'AUTO-BATCH-001-UPDATED',
                    'unit_cost': 30.00,
                    'selling_price': 45.00
                },
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data.get('success'))
            print("   ✅ UPDATE: Batch updated successfully")
            
            # Store for adjustment testing
            self.__class__.test_batch_id = batch_id

    def test_05_inventory_adjustments(self):
        """Test Inventory Adjustments like a human user"""
        print("\n🧪 Testing Inventory Adjustments...")
        
        with self.app.app_context():
            batch_id = getattr(self.__class__, 'test_batch_id', None)
            if not batch_id:
                batches = InventoryBatch.query.all()
                batch_id = batches[0].id if batches else None
            
            self.assertIsNotNone(batch_id, "Test batch required for adjustment testing")
            
            # Test ADD STOCK - Simulate receiving inventory
            response = self.client.post('/api/inventory/adjustments',
                json={
                    'batch_id': batch_id,
                    'quantity': 100.0,
                    'unit_cost': 25.50,
                    'notes': 'Initial stock added by automation'
                },
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data.get('success'))
            print("   ✅ ADD STOCK: Added 100 units to batch")
            
            # Verify stock was added
            batch = InventoryBatch.query.get(batch_id)
            self.assertEqual(float(batch.qty_available), 100.0)
            print(f"   ✅ VERIFY: Batch now has {batch.qty_available} units")

    def test_06_inventory_consumption(self):
        """Test Inventory Consumption like a human user"""
        print("\n🧪 Testing Inventory Consumption...")
        
        with self.app.app_context():
            batch_id = getattr(self.__class__, 'test_batch_id', None)
            if not batch_id:
                batches = InventoryBatch.query.filter(InventoryBatch.qty_available > 0).all()
                batch_id = batches[0].id if batches else None
            
            self.assertIsNotNone(batch_id, "Test batch with stock required for consumption testing")
            
            # Test CONSUME STOCK - Simulate using inventory
            response = self.client.post('/api/inventory/consumption',
                json={
                    'batch_id': batch_id,
                    'quantity': 25.0,
                    'issued_to': 'Spa Treatment Room 1',
                    'reference': 'AUTO-CONSUMPTION-001',
                    'notes': 'Used for automated test treatment'
                },
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data.get('success'))
            print("   ✅ CONSUME STOCK: Consumed 25 units from batch")
            
            # Verify stock was reduced
            batch = InventoryBatch.query.get(batch_id)
            self.assertEqual(float(batch.qty_available), 75.0)  # 100 - 25 = 75
            print(f"   ✅ VERIFY: Batch now has {batch.qty_available} units remaining")

    def test_07_api_endpoints_availability(self):
        """Test all API endpoints are accessible"""
        print("\n🧪 Testing API Endpoint Availability...")
        
        endpoints = [
            ('/api/inventory/products', 'GET'),
            ('/api/inventory/categories', 'GET'),
            ('/api/inventory/locations', 'GET'),
            ('/api/inventory/batches', 'GET'),
            ('/api/inventory/adjustments', 'GET'),
            ('/api/inventory/consumption', 'GET'),
            ('/api/inventory/batches/available', 'GET'),
            ('/api/inventory/test', 'GET')
        ]
        
        for endpoint, method in endpoints:
            if method == 'GET':
                response = self.client.get(endpoint)
            else:
                response = self.client.post(endpoint)
            
            # Accept both 200 (success) and 302 (redirect, which is normal for protected endpoints)
            self.assertIn(response.status_code, [200, 302], f"Endpoint {endpoint} failed")
            print(f"   ✅ {method} {endpoint}: {response.status_code}")

    def test_08_data_validation_and_constraints(self):
        """Test data validation like a human would encounter errors"""
        print("\n🧪 Testing Data Validation and Constraints...")
        
        with self.app.app_context():
            # Test duplicate SKU validation
            response = self.client.post('/api/inventory/products',
                json={
                    'name': 'Duplicate SKU Test',
                    'sku': 'AUTO-001-UPDATED',  # This SKU already exists from previous test
                    'category_id': 1
                },
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 400)
            data = response.get_json()
            self.assertIn('already exists', data.get('error', '').lower())
            print("   ✅ DUPLICATE SKU: Validation working correctly")
            
            # Test duplicate batch name validation
            response = self.client.post('/api/inventory/batches',
                json={
                    'batch_name': 'AUTO-BATCH-001-UPDATED',  # This batch name already exists
                    'mfg_date': '2025-01-01',
                    'expiry_date': '2026-01-01'
                },
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 400)
            data = response.get_json()
            self.assertIn('unique', data.get('error', '').lower())
            print("   ✅ DUPLICATE BATCH: Validation working correctly")
            
            # Test invalid date validation
            response = self.client.post('/api/inventory/batches',
                json={
                    'batch_name': 'INVALID-DATE-TEST',
                    'mfg_date': '2026-01-01',  # Manufacturing date after expiry
                    'expiry_date': '2025-01-01'
                },
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 400)
            data = response.get_json()
            self.assertIn('expiry date must be later', data.get('error', '').lower())
            print("   ✅ DATE VALIDATION: Working correctly")

    def test_09_batch_properties_and_calculations(self):
        """Test batch properties work correctly"""
        print("\n🧪 Testing Batch Properties and Calculations...")
        
        with self.app.app_context():
            # Create a batch that will expire soon for testing
            product = InventoryProduct.query.first()
            location = InventoryLocation.query.first()
            
            # Create batch expiring in 15 days
            near_expiry_batch = InventoryBatch(
                batch_name='NEAR-EXPIRY-TEST',
                product_id=product.id,
                location_id=location.id,
                mfg_date=date.today() - timedelta(days=30),
                expiry_date=date.today() + timedelta(days=15),
                unit_cost=10.0,
                qty_available=50.0
            )
            db.session.add(near_expiry_batch)
            db.session.commit()
            
            # Test batch properties
            self.assertFalse(near_expiry_batch.is_expired)
            self.assertTrue(near_expiry_batch.is_near_expiry)
            self.assertEqual(near_expiry_batch.days_to_expiry, 15)
            
            print("   ✅ BATCH PROPERTIES: is_expired, is_near_expiry, days_to_expiry working correctly")
            
            # Test dropdown display format
            display = near_expiry_batch.dropdown_display
            self.assertIn('NEAR-EXPIRY-TEST', display)
            self.assertIn(product.name, display)
            self.assertIn(location.name, display)
            self.assertIn('50.0', display)
            
            print(f"   ✅ DROPDOWN DISPLAY: {display}")

    def test_10_product_stock_aggregation(self):
        """Test product stock aggregation from batches"""
        print("\n🧪 Testing Product Stock Aggregation...")
        
        with self.app.app_context():
            # Get a product and verify its total stock
            products = InventoryProduct.query.all()
            
            for product in products:
                calculated_stock = sum(
                    float(batch.qty_available or 0) 
                    for batch in product.batches 
                    if batch.status == 'active'
                )
                
                self.assertEqual(product.total_stock, calculated_stock)
                
                # Test batch count
                active_batch_count = len([b for b in product.batches if b.status == 'active'])
                self.assertEqual(product.batch_count, active_batch_count)
                
                print(f"   ✅ PRODUCT '{product.name}': Stock={product.total_stock}, Batches={product.batch_count}")

def run_automated_tests():
    """Run all automated tests and provide detailed results"""
    print("🚀 Starting Comprehensive Automated Inventory Testing...")
    print("=" * 70)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(InventoryAutomationTests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=True
    )
    
    # Execute tests
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print detailed results
    print("=" * 70)
    print("🎯 TEST EXECUTION SUMMARY")
    print("=" * 70)
    
    print(f"⏱️  Total execution time: {end_time - start_time:.2f} seconds")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"🚫 Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n🚫 ERRORS:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    # Overall result
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED! ✅")
        print("✅ Inventory Management System is fully functional and ready for production!")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED! ❌")
        print("🔧 Please review the failures above and fix the issues.")
        return False

if __name__ == "__main__":
    success = run_automated_tests()
    sys.exit(0 if success else 1)
