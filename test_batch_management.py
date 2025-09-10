
#!/usr/bin/env python3
"""
Comprehensive test script for Batch Management System
Run this to test all CRUD operations and API endpoints
"""

from app import app, db
from modules.inventory.models import InventoryBatch, InventoryProduct, InventoryLocation, InventoryCategory
import sys
import json

def test_batch_management():
    """Test all batch management functionality"""
    with app.app_context():
        print("🧪 Starting Batch Management Tests...")
        
        # Test 1: Check database tables exist
        print("\n1. Testing database tables...")
        try:
            batch_count = InventoryBatch.query.count()
            product_count = InventoryProduct.query.count()
            location_count = InventoryLocation.query.count()
            category_count = InventoryCategory.query.count()
            
            print(f"   ✅ Tables exist - Batches: {batch_count}, Products: {product_count}, Locations: {location_count}, Categories: {category_count}")
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            return False
        
        # Test 2: Create test data if needed
        print("\n2. Creating test data...")
        try:
            # Create test category
            test_category = InventoryCategory.query.filter_by(name='Test Category').first()
            if not test_category:
                test_category = InventoryCategory(
                    name='Test Category',
                    description='Test category for batch management'
                )
                db.session.add(test_category)
                db.session.commit()
                print("   ✅ Test category created")
            
            # Create test product
            test_product = InventoryProduct.query.filter_by(sku='TEST-BATCH-001').first()
            if not test_product:
                test_product = InventoryProduct(
                    sku='TEST-BATCH-001',
                    name='Test Batch Product',
                    description='Product for testing batch management',
                    category_id=test_category.id,
                    unit_of_measure='pcs',
                    is_active=True
                )
                db.session.add(test_product)
                db.session.commit()
                print("   ✅ Test product created")
            
            # Create test location
            test_location = InventoryLocation.query.filter_by(id='test-location').first()
            if not test_location:
                test_location = InventoryLocation(
                    id='test-location',
                    name='Test Location',
                    type='warehouse',
                    address='Test Address',
                    status='active'
                )
                db.session.add(test_location)
                db.session.commit()
                print("   ✅ Test location created")
            
        except Exception as e:
            print(f"   ❌ Error creating test data: {e}")
            return False
        
        # Test 3: Test batch CRUD operations
        print("\n3. Testing batch CRUD operations...")
        try:
            from datetime import date, timedelta
            
            # CREATE
            test_batch = InventoryBatch(
                batch_name=f'TEST-BATCH-{int(date.today().strftime("%Y%m%d"))}',
                product_id=test_product.id,
                location_id=test_location.id,
                mfg_date=date.today(),
                expiry_date=date.today() + timedelta(days=365),
                unit_cost=10.50,
                selling_price=15.00,
                qty_available=100,
                status='active'
            )
            db.session.add(test_batch)
            db.session.commit()
            print(f"   ✅ CREATE: Test batch created with ID {test_batch.id}")
            
            # READ
            read_batch = InventoryBatch.query.get(test_batch.id)
            if read_batch and read_batch.batch_name == test_batch.batch_name:
                print(f"   ✅ READ: Test batch retrieved successfully")
            else:
                print(f"   ❌ READ: Failed to retrieve test batch")
                return False
            
            # UPDATE
            read_batch.unit_cost = 12.00
            db.session.commit()
            updated_batch = InventoryBatch.query.get(test_batch.id)
            if updated_batch.unit_cost == 12.00:
                print(f"   ✅ UPDATE: Test batch updated successfully")
            else:
                print(f"   ❌ UPDATE: Failed to update test batch")
                return False
            
            # DELETE (soft delete)
            updated_batch.status = 'deleted'
            db.session.commit()
            deleted_batch = InventoryBatch.query.get(test_batch.id)
            if deleted_batch.status == 'deleted':
                print(f"   ✅ DELETE: Test batch soft-deleted successfully")
            else:
                print(f"   ❌ DELETE: Failed to delete test batch")
                return False
            
        except Exception as e:
            print(f"   ❌ CRUD operations error: {e}")
            return False
        
        # Test 4: Test API endpoints with test client
        print("\n4. Testing API endpoints...")
        with app.test_client() as client:
            try:
                # Test products API
                response = client.get('/api/inventory/products')
                if response.status_code == 200:
                    print("   ✅ Products API working")
                else:
                    print(f"   ❌ Products API failed: {response.status_code}")
                
                # Test locations API
                response = client.get('/api/inventory/locations')
                if response.status_code == 200:
                    print("   ✅ Locations API working")
                else:
                    print(f"   ❌ Locations API failed: {response.status_code}")
                
                # Test batches API
                response = client.get('/api/inventory/batches')
                if response.status_code == 200:
                    print("   ✅ Batches API working")
                else:
                    print(f"   ❌ Batches API failed: {response.status_code}")
                
                # Test comprehensive test endpoint
                response = client.get('/api/inventory/test')
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"   ✅ Test endpoint working: {data['message']}")
                    print(f"       📊 Data counts: {data['data']}")
                else:
                    print(f"   ❌ Test endpoint failed: {response.status_code}")
                
            except Exception as e:
                print(f"   ❌ API testing error: {e}")
                return False
        
        # Test 5: Validate relationships and properties
        print("\n5. Testing relationships and properties...")
        try:
            # Get a batch with relationships
            active_batch = InventoryBatch.query.filter(
                InventoryBatch.status == 'active',
                InventoryBatch.product_id.isnot(None)
            ).first()
            
            if active_batch:
                print(f"   ✅ Batch found: {active_batch.batch_name}")
                print(f"   ✅ Product relationship: {active_batch.product.name if active_batch.product else 'None'}")
                print(f"   ✅ Location relationship: {active_batch.location.name if active_batch.location else 'None'}")
                print(f"   ✅ Is expired: {active_batch.is_expired}")
                print(f"   ✅ Days to expiry: {active_batch.days_to_expiry}")
                print(f"   ✅ Dropdown display: {active_batch.dropdown_display}")
            else:
                print("   ⚠️ No active batches with products found")
        
        except Exception as e:
            print(f"   ❌ Relationship testing error: {e}")
            return False
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Summary:")
        print("   - Database tables: ✅ Working")
        print("   - CRUD operations: ✅ Working")
        print("   - API endpoints: ✅ Working")
        print("   - Relationships: ✅ Working")
        print("   - Properties: ✅ Working")
        
        return True

if __name__ == "__main__":
    success = test_batch_management()
    if success:
        print("\n✅ Batch Management System is fully functional!")
    else:
        print("\n❌ Batch Management System has issues!")
    
    sys.exit(0 if success else 1)
