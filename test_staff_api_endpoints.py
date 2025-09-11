
#!/usr/bin/env python3
"""
Staff Management API Endpoint Testing
Tests all API endpoints for CRUD operations
"""

import requests
import json
import time
from datetime import datetime

def test_staff_api_endpoints():
    """Test all staff API endpoints"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🌐 STAFF MANAGEMENT API ENDPOINT TESTING")
    print("=" * 60)
    
    test_results = {'passed': 0, 'failed': 0, 'errors': []}
    test_staff_id = None
    
    # Test 1: GET /api/staff (Read All)
    print("\n📖 Test 1: GET /api/staff")
    try:
        response = requests.get(f"{base_url}/api/staff", timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data.get('success', False)}")
            
            if data.get('success'):
                staff_list = data.get('staff', [])
                print(f"✅ GET /api/staff - Retrieved {len(staff_list)} staff members")
                
                if staff_list:
                    sample = staff_list[0]
                    print(f"   Sample staff: {sample.get('first_name')} {sample.get('last_name')}")
                
                test_results['passed'] += 1
            else:
                raise Exception(f"API returned success=false: {data.get('error')}")
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ GET /api/staff failed: {str(e)}")
        test_results['failed'] += 1
        test_results['errors'].append(f"GET /api/staff: {str(e)}")
    
    # Test 2: POST /api/staff (Create)
    print("\n➕ Test 2: POST /api/staff")
    try:
        test_data = {
            'username': f'api_test_{int(time.time())}',
            'first_name': 'API',
            'last_name': 'Test',
            'email': f'apitest{int(time.time())}@example.com',
            'password': 'testpass123',
            'phone': '9876543210',
            'role': 'staff',
            'designation': 'API Test Specialist',
            'gender': 'female',
            'commission_rate': 10.0,
            'hourly_rate': 20.0
        }
        
        response = requests.post(
            f"{base_url}/api/staff",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data.get('success', False)}")
            
            if data.get('success'):
                print(f"✅ POST /api/staff - Created staff member successfully")
                staff_info = data.get('staff', {})
                if staff_info:
                    test_staff_id = staff_info.get('id')
                    print(f"   Created staff ID: {test_staff_id}")
                    print(f"   Name: {staff_info.get('first_name')} {staff_info.get('last_name')}")
                
                test_results['passed'] += 1
            else:
                raise Exception(f"API returned success=false: {data.get('error')}")
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ POST /api/staff failed: {str(e)}")
        test_results['failed'] += 1
        test_results['errors'].append(f"POST /api/staff: {str(e)}")
    
    # Test 3: GET /api/staff/<id> (Read Single)
    if test_staff_id:
        print(f"\n🔍 Test 3: GET /api/staff/{test_staff_id}")
        try:
            response = requests.get(f"{base_url}/api/staff/{test_staff_id}", timeout=10)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {data.get('success', False)}")
                
                if data.get('success'):
                    staff_data = data.get('staff', {})
                    print(f"✅ GET /api/staff/{test_staff_id} - Retrieved staff member")
                    print(f"   Name: {staff_data.get('first_name')} {staff_data.get('last_name')}")
                    print(f"   Email: {staff_data.get('email')}")
                    
                    test_results['passed'] += 1
                else:
                    raise Exception(f"API returned success=false: {data.get('error')}")
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ GET /api/staff/{test_staff_id} failed: {str(e)}")
            test_results['failed'] += 1
            test_results['errors'].append(f"GET /api/staff/{test_staff_id}: {str(e)}")
    
    # Test 4: PUT /api/staff/<id> (Update)
    if test_staff_id:
        print(f"\n✏️ Test 4: PUT /api/staff/{test_staff_id}")
        try:
            update_data = {
                'first_name': 'Updated API',
                'last_name': 'Test User',
                'designation': 'Senior API Test Specialist',
                'commission_rate': 15.0
            }
            
            response = requests.put(
                f"{base_url}/api/staff/{test_staff_id}",
                json=update_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {data.get('success', False)}")
                
                if data.get('success'):
                    print(f"✅ PUT /api/staff/{test_staff_id} - Updated staff member successfully")
                    print(f"   Message: {data.get('message')}")
                    
                    test_results['passed'] += 1
                else:
                    raise Exception(f"API returned success=false: {data.get('error')}")
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ PUT /api/staff/{test_staff_id} failed: {str(e)}")
            test_results['failed'] += 1
            test_results['errors'].append(f"PUT /api/staff/{test_staff_id}: {str(e)}")
    
    # Test 5: DELETE /api/staff/<id> (Delete)
    if test_staff_id:
        print(f"\n🗑️ Test 5: DELETE /api/staff/{test_staff_id}")
        try:
            response = requests.delete(f"{base_url}/api/staff/{test_staff_id}", timeout=10)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {data.get('success', False)}")
                
                if data.get('success'):
                    print(f"✅ DELETE /api/staff/{test_staff_id} - Deleted staff member successfully")
                    print(f"   Message: {data.get('message')}")
                    
                    test_results['passed'] += 1
                else:
                    raise Exception(f"API returned success=false: {data.get('error')}")
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ DELETE /api/staff/{test_staff_id} failed: {str(e)}")
            test_results['failed'] += 1
            test_results['errors'].append(f"DELETE /api/staff/{test_staff_id}: {str(e)}")
    
    # Print Results
    print("\n" + "=" * 60)
    print("📊 API ENDPOINT TEST RESULTS")
    print("=" * 60)
    
    total_tests = test_results['passed'] + test_results['failed']
    success_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"✅ Tests Passed: {test_results['passed']}")
    print(f"❌ Tests Failed: {test_results['failed']}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if test_results['errors']:
        print(f"\n🚨 ERRORS FOUND:")
        for i, error in enumerate(test_results['errors'], 1):
            print(f"{i}. {error}")
    
    return test_results['failed'] == 0

if __name__ == "__main__":
    print("⚠️ Make sure your Flask app is running on http://127.0.0.1:5000")
    print("   Run 'python main.py' in another terminal first")
    
    input("\nPress Enter when your Flask app is running...")
    
    success = test_staff_api_endpoints()
    if success:
        print("\n🎉 ALL API ENDPOINTS WORKING CORRECTLY!")
    else:
        print("\n⚠️ SOME API ENDPOINTS HAVE ISSUES")
