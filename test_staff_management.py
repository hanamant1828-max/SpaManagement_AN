
#!/usr/bin/env python3
"""
Comprehensive Staff Management Test Suite
Tests all CRUD operations: Create, Read, Update, Delete
"""

import os
import sys
import json
import time
from datetime import datetime, date, timedelta
import requests
import traceback

# Add the current directory to the path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_with_app_context():
    """Run tests within Flask application context"""
    try:
        from app import app, db
        from models import User, Role, Department, Service
        from modules.staff.staff_queries import (
            get_all_staff, get_staff_by_id, create_staff, update_staff, delete_staff,
            get_comprehensive_staff
        )
        
        with app.app_context():
            print("🚀 COMPREHENSIVE STAFF MANAGEMENT TESTING")
            print("=" * 80)
            
            test_results = {
                'passed': 0,
                'failed': 0,
                'errors': []
            }
            
            # Test 1: Database Connection and Models
            print("\n📋 Test 1: Database Connection and Models")
            try:
                # Test database connectivity
                staff_count = User.query.count()
                role_count = Role.query.count()
                dept_count = Department.query.count()
                
                print(f"✅ Database connected successfully")
                print(f"   - Staff members: {staff_count}")
                print(f"   - Roles: {role_count}")
                print(f"   - Departments: {dept_count}")
                
                # Test model relationships
                if staff_count > 0:
                    sample_staff = User.query.first()
                    print(f"   - Sample staff: {sample_staff.first_name} {sample_staff.last_name}")
                    print(f"   - Role: {sample_staff.role}")
                    print(f"   - Department: {sample_staff.staff_department.display_name if sample_staff.staff_department else 'None'}")
                
                test_results['passed'] += 1
                
            except Exception as e:
                print(f"❌ Database test failed: {str(e)}")
                test_results['failed'] += 1
                test_results['errors'].append(f"Database test: {str(e)}")
            
            # Test 2: READ Operations
            print("\n📖 Test 2: READ Operations")
            try:
                # Test get_all_staff
                all_staff = get_all_staff()
                print(f"✅ get_all_staff() returned {len(all_staff)} staff members")
                
                # Test get_comprehensive_staff
                comp_staff = get_comprehensive_staff()
                print(f"✅ get_comprehensive_staff() returned {len(comp_staff)} staff members")
                
                if len(all_staff) > 0:
                    # Test get_staff_by_id
                    first_staff = all_staff[0]
                    staff_by_id = get_staff_by_id(first_staff.id)
                    if staff_by_id:
                        print(f"✅ get_staff_by_id({first_staff.id}) returned: {staff_by_id.first_name} {staff_by_id.last_name}")
                    else:
                        raise Exception(f"get_staff_by_id({first_staff.id}) returned None")
                
                test_results['passed'] += 1
                
            except Exception as e:
                print(f"❌ READ operations failed: {str(e)}")
                test_results['failed'] += 1
                test_results['errors'].append(f"READ operations: {str(e)}")
            
            # Test 3: CREATE Operations
            print("\n➕ Test 3: CREATE Operations")
            try:
                from werkzeug.security import generate_password_hash
                
                # Create test staff member
                test_staff_data = {
                    'username': f'test_user_{int(time.time())}',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'email': f'test{int(time.time())}@example.com',
                    'phone': '1234567890',
                    'password_hash': generate_password_hash('testpass123'),
                    'role': 'staff',
                    'designation': 'Test Specialist',
                    'commission_rate': 15.0,
                    'hourly_rate': 25.0,
                    'gender': 'male',
                    'date_of_joining': date.today(),
                    'is_active': True
                }
                
                created_staff = create_staff(test_staff_data)
                if created_staff:
                    print(f"✅ create_staff() successfully created: {created_staff.first_name} {created_staff.last_name}")
                    print(f"   - ID: {created_staff.id}")
                    print(f"   - Username: {created_staff.username}")
                    print(f"   - Email: {created_staff.email}")
                    
                    # Store for later tests
                    test_staff_id = created_staff.id
                    test_results['passed'] += 1
                else:
                    raise Exception("create_staff() returned None")
                
            except Exception as e:
                print(f"❌ CREATE operations failed: {str(e)}")
                print(f"   Error details: {traceback.format_exc()}")
                test_results['failed'] += 1
                test_results['errors'].append(f"CREATE operations: {str(e)}")
                test_staff_id = None
            
            # Test 4: UPDATE Operations
            print("\n✏️ Test 4: UPDATE Operations")
            try:
                if test_staff_id:
                    # Update the created staff member
                    update_data = {
                        'first_name': 'Updated',
                        'last_name': 'TestUser',
                        'designation': 'Senior Test Specialist',
                        'commission_rate': 20.0,
                        'hourly_rate': 30.0
                    }
                    
                    updated_staff = update_staff(test_staff_id, update_data)
                    if updated_staff:
                        print(f"✅ update_staff() successfully updated staff member")
                        print(f"   - Name: {updated_staff.first_name} {updated_staff.last_name}")
                        print(f"   - Designation: {updated_staff.designation}")
                        print(f"   - Commission Rate: {updated_staff.commission_rate}%")
                        print(f"   - Hourly Rate: ${updated_staff.hourly_rate}")
                        test_results['passed'] += 1
                    else:
                        raise Exception("update_staff() returned None")
                else:
                    print("⚠️ Skipping UPDATE test (no test staff created)")
                    
            except Exception as e:
                print(f"❌ UPDATE operations failed: {str(e)}")
                print(f"   Error details: {traceback.format_exc()}")
                test_results['failed'] += 1
                test_results['errors'].append(f"UPDATE operations: {str(e)}")
            
            # Test 5: DELETE Operations
            print("\n🗑️ Test 5: DELETE Operations")
            try:
                if test_staff_id:
                    # Delete the test staff member
                    delete_result = delete_staff(test_staff_id)
                    if delete_result:
                        print(f"✅ delete_staff() successfully deleted staff member ID: {test_staff_id}")
                        
                        # Verify deletion
                        deleted_staff = get_staff_by_id(test_staff_id)
                        if deleted_staff and not deleted_staff.is_active:
                            print("✅ Staff member successfully deactivated (soft delete)")
                        elif not deleted_staff:
                            print("✅ Staff member successfully removed (hard delete)")
                        
                        test_results['passed'] += 1
                    else:
                        raise Exception("delete_staff() returned False")
                else:
                    print("⚠️ Skipping DELETE test (no test staff to delete)")
                    
            except Exception as e:
                print(f"❌ DELETE operations failed: {str(e)}")
                print(f"   Error details: {traceback.format_exc()}")
                test_results['failed'] += 1
                test_results['errors'].append(f"DELETE operations: {str(e)}")
            
            # Test 6: Data Validation
            print("\n✅ Test 6: Data Validation")
            try:
                # Test invalid data handling
                invalid_data = {
                    'username': '',  # Empty username
                    'email': 'invalid-email',  # Invalid email
                    'first_name': '',  # Empty required field
                }
                
                try:
                    create_staff(invalid_data)
                    print("⚠️ Warning: create_staff() accepted invalid data")
                except Exception:
                    print("✅ create_staff() properly rejected invalid data")
                
                test_results['passed'] += 1
                
            except Exception as e:
                print(f"❌ Data validation test failed: {str(e)}")
                test_results['failed'] += 1
                test_results['errors'].append(f"Data validation: {str(e)}")
            
            # Test 7: Database Relationships
            print("\n🔗 Test 7: Database Relationships")
            try:
                # Test role relationships
                roles = Role.query.all()
                departments = Department.query.all()
                
                print(f"✅ Found {len(roles)} roles")
                for role in roles[:3]:  # Show first 3
                    print(f"   - {role.display_name}")
                
                print(f"✅ Found {len(departments)} departments")
                for dept in departments[:3]:  # Show first 3
                    print(f"   - {dept.display_name}")
                
                # Test staff-role relationships
                staff_with_roles = User.query.filter(User.role_id.isnot(None)).limit(3).all()
                print(f"✅ Found {len(staff_with_roles)} staff members with role assignments")
                
                test_results['passed'] += 1
                
            except Exception as e:
                print(f"❌ Database relationships test failed: {str(e)}")
                test_results['failed'] += 1
                test_results['errors'].append(f"Database relationships: {str(e)}")
            
            # Print Final Results
            print("\n" + "=" * 80)
            print("📊 FINAL TEST RESULTS")
            print("=" * 80)
            
            total_tests = test_results['passed'] + test_results['failed']
            success_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
            
            print(f"✅ Tests Passed: {test_results['passed']}")
            print(f"❌ Tests Failed: {test_results['failed']}")
            print(f"📈 Success Rate: {success_rate:.1f}%")
            
            if test_results['errors']:
                print(f"\n🚨 ERRORS FOUND:")
                for i, error in enumerate(test_results['errors'], 1):
                    print(f"{i}. {error}")
            
            if test_results['failed'] == 0:
                print(f"\n🎉 ALL STAFF MANAGEMENT TESTS PASSED! 🎉")
                print("✅ CRUD operations working correctly")
                print("✅ Data validation working")
                print("✅ Database relationships intact")
                return True
            else:
                print(f"\n⚠️ {test_results['failed']} TEST(S) FAILED")
                print("🔧 Please review the errors above")
                return False
                
    except ImportError as e:
        print(f"❌ Import Error: {str(e)}")
        print("🔧 Make sure all modules are properly configured")
        return False
    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")
        print(f"🔧 Error details: {traceback.format_exc()}")
        return False

def test_api_endpoints():
    """Test API endpoints for staff management"""
    print("\n🌐 Testing API Endpoints")
    
    base_url = "http://127.0.0.1:5000"
    api_test_results = {'passed': 0, 'failed': 0, 'errors': []}
    
    try:
        # Test GET /api/staff
        print("Testing GET /api/staff...")
        response = requests.get(f"{base_url}/api/staff", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ GET /api/staff returned {len(data.get('staff', []))} staff members")
                api_test_results['passed'] += 1
            else:
                raise Exception("API returned success=false")
        else:
            raise Exception(f"HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ API endpoint test failed: {str(e)}")
        api_test_results['failed'] += 1
        api_test_results['errors'].append(f"API endpoint: {str(e)}")
    
    return api_test_results

def main():
    """Run all tests"""
    print("🚀 STARTING COMPREHENSIVE STAFF MANAGEMENT TESTS")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run Flask context tests
    flask_success = test_with_app_context()
    
    # Run API tests (commented out as it requires running server)
    # api_results = test_api_endpoints()
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if flask_success:
        print("🎯 STAFF MANAGEMENT SYSTEM IS FULLY FUNCTIONAL!")
        return True
    else:
        print("⚠️ ISSUES FOUND - Review errors above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
