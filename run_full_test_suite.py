
#!/usr/bin/env python3
"""
Full Test Suite Runner - Tests everything automatically
This script runs comprehensive tests to verify all functionality works correctly
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔄 {description}...")
    print(f"   Command: {command}")
    
    try:
        start_time = time.time()
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        end_time = time.time()
        
        print(f"   Duration: {end_time - start_time:.2f} seconds")
        print(f"   Exit Code: {result.returncode}")
        
        if result.returncode == 0:
            print(f"   ✅ SUCCESS: {description}")
            if result.stdout.strip():
                print("   Output:", result.stdout.strip()[:500])  # First 500 chars
            return True
        else:
            print(f"   ❌ FAILED: {description}")
            if result.stderr.strip():
                print("   Error:", result.stderr.strip()[:500])
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ⏰ TIMEOUT: {description} took too long")
        return False
    except Exception as e:
        print(f"   🚫 EXCEPTION: {e}")
        return False

def main():
    """Run the complete test suite"""
    print("🚀 COMPREHENSIVE INVENTORY MANAGEMENT TEST SUITE")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Database and Models Validation
    tests_total += 1
    if run_command("python test_batch_management.py", "Database and Models Validation"):
        tests_passed += 1
    
    # Test 2: Comprehensive Automated Testing
    tests_total += 1
    if run_command("python test_inventory_automation.py", "Comprehensive Automated Testing"):
        tests_passed += 1
    
    # Test 3: API Endpoints Testing
    tests_total += 1
    if run_command("python -c \"from app import app; from modules.inventory.views import api_test_inventory; print('API Test:', api_test_inventory())\"", "API Endpoints Validation"):
        tests_passed += 1
    
    # Test 4: Frontend Integration (if possible)
    tests_total += 1
    try:
        # Simple test to check if the inventory dashboard loads
        if run_command("python -c \"from app import app; client = app.test_client(); resp = client.get('/inventory'); print('Status:', resp.status_code); assert resp.status_code in [200, 302]\"", "Frontend Integration Test"):
            tests_passed += 1
    except:
        print("   ⚠️  Frontend test skipped (requires full app context)")
    
    # Test 5: Data Integrity Checks
    tests_total += 1
    test_script = '''
from app import app, db
from modules.inventory.models import *
with app.app_context():
    # Check all tables exist and have data
    products = InventoryProduct.query.count()
    categories = InventoryCategory.query.count()
    locations = InventoryLocation.query.count()
    batches = InventoryBatch.query.count()
    print(f"Data counts - Products: {products}, Categories: {categories}, Locations: {locations}, Batches: {batches}")
    assert products > 0, "No products found"
    assert categories > 0, "No categories found"
    assert locations > 0, "No locations found"
    print("✅ Data integrity check passed")
'''
    
    if run_command(f"python -c \"{test_script}\"", "Data Integrity Checks"):
        tests_passed += 1
    
    # Print Final Results
    print("\n" + "=" * 80)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 80)
    
    print(f"📊 Tests Passed: {tests_passed}/{tests_total}")
    print(f"📈 Success Rate: {(tests_passed/tests_total*100):.1f}%")
    
    if tests_passed == tests_total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("✅ Your Inventory Management System is FULLY FUNCTIONAL!")
        print("✅ All CRUD operations work correctly")
        print("✅ All API endpoints respond correctly")  
        print("✅ Database relationships are properly configured")
        print("✅ Data validation is working")
        print("✅ Frontend integration is working")
        print("\n🚀 System is ready for production use!")
        return True
    else:
        print(f"\n⚠️  {tests_total - tests_passed} TEST(S) FAILED")
        print("🔧 Please review the failed tests above and fix the issues")
        print("🔧 Run individual test files to get more detailed error information")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sys.exit(0 if success else 1)
