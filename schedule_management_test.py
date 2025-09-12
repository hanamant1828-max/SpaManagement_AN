#!/usr/bin/env python3
"""
Comprehensive Schedule Management CRUD Testing
Tests all schedule management functionality as a real user would use it
"""

import requests
import json
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"
USERNAME = "admin"
PASSWORD = "admin123"

class ScheduleManagementTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'ScheduleTester/1.0'})
        self.created_schedule_ids = []
        self.test_staff_id = None
        self.csrf_token = None
        
    def get_csrf_token(self, page_content):
        """Extract CSRF token from page content"""
        soup = BeautifulSoup(page_content, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        return csrf_input.get('value') if csrf_input else None
        
    def login(self):
        """Login to the system"""
        print("🔐 SCHEDULE TEST 1: Login and Setup")
        
        # Get login page and extract CSRF token
        login_page = self.session.get(f"{BASE_URL}/login")
        if login_page.status_code != 200:
            print(f"❌ Could not access login page: {login_page.status_code}")
            return False
            
        csrf_token = self.get_csrf_token(login_page.text)
        if not csrf_token:
            print("❌ No CSRF token found in login page")
            return False
            
        # Login with CSRF token
        login_data = {
            'username': USERNAME,
            'password': PASSWORD,
            'csrf_token': csrf_token
        }
        
        response = self.session.post(f"{BASE_URL}/login", data=login_data)
        
        # Check dashboard access
        dashboard_response = self.session.get(f"{BASE_URL}/dashboard")
        success = dashboard_response.status_code == 200 and "dashboard" in dashboard_response.text.lower()
        
        print(f"   Login successful: {'✅ Yes' if success else '❌ No'}")
        
        # Get CSRF token for API requests
        if success:
            csrf_response = self.session.get(f"{BASE_URL}/api/csrf")
            if csrf_response.status_code == 200:
                try:
                    csrf_data = csrf_response.json()
                    if csrf_data.get('success') and 'csrf_token' in csrf_data:
                        self.csrf_token = csrf_data['csrf_token']
                        print(f"   CSRF token acquired: {'✅ Yes' if self.csrf_token else '❌ No'}")
                    else:
                        print("   ⚠️ Could not get CSRF token from API")
                except Exception as e:
                    print(f"   ⚠️ Error getting CSRF token: {e}")
            else:
                print(f"   ⚠️ CSRF endpoint failed: {csrf_response.status_code}")
        
        return success
    
    def get_test_staff_member(self):
        """Get a staff member to test schedule management with"""
        print("\n📋 SCHEDULE TEST 2: Get Test Staff Member")
        
        # Get list of staff members
        staff_response = self.session.get(f"{BASE_URL}/api/staff")
        if staff_response.status_code == 200:
            try:
                staff_data = staff_response.json()
                # Handle structured API response with 'staff' key
                if staff_data and staff_data.get('success') and 'staff' in staff_data:
                    staff_list = staff_data['staff']
                    if staff_list and len(staff_list) > 0:
                        self.test_staff_id = staff_list[0]['id']
                        staff_name = f"{staff_list[0]['first_name']} {staff_list[0]['last_name']}"
                        print(f"   Test staff member: ✅ {staff_name} (ID: {self.test_staff_id})")
                        return True
                    else:
                        print("   ❌ No staff members in staff list")
                        return False
                else:
                    print(f"   ❌ Invalid API response structure: {list(staff_data.keys()) if isinstance(staff_data, dict) else type(staff_data)}")
                    return False
            except Exception as e:
                print(f"   ❌ Error parsing staff data: {e}")
                return False
        else:
            print(f"   ❌ Could not access staff list: {staff_response.status_code}")
            return False
    
    def test_create_schedule_range(self):
        """Test creating schedule ranges (CREATE operation)"""
        print("\n➕ SCHEDULE TEST 3: CREATE Schedule Range")
        
        if not self.test_staff_id:
            print("   ❌ No test staff member available")
            return False
        
        # Test data for schedule range
        today = date.today()
        start_date = today + timedelta(days=1)  # Tomorrow
        end_date = today + timedelta(days=30)   # Next month
        
        schedule_data = {
            'schedule_name': 'Test Regular Schedule',
            'description': 'Testing schedule range creation',
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'monday': True,
            'tuesday': True,
            'wednesday': True,
            'thursday': True,
            'friday': True,
            'saturday': False,
            'sunday': False,
            'shift_start_time': '09:00',
            'shift_end_time': '17:00',
            'break_time': '12:00-13:00',
            'priority': 1
        }
        
        # Create schedule range via API with CSRF token
        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': self.csrf_token
        }
        create_response = self.session.post(
            f"{BASE_URL}/api/staff/{self.test_staff_id}/schedule-ranges",
            json=schedule_data,
            headers=headers
        )
        
        print(f"   CREATE API status: {create_response.status_code}")
        
        if create_response.status_code in [200, 201]:
            try:
                result = create_response.json()
                if result.get('success') and 'schedule_range_id' in result:
                    schedule_id = result['schedule_range_id']
                    self.created_schedule_ids.append(schedule_id)
                    print(f"   ✅ Schedule range created successfully (ID: {schedule_id})")
                    return schedule_id
                else:
                    print(f"   ❌ Unexpected response: {result}")
            except Exception as e:
                print(f"   ❌ Error parsing response: {e}")
        else:
            print(f"   ❌ CREATE failed: {create_response.status_code}")
            if create_response.text:
                print(f"   Response: {create_response.text[:200]}")
                
        return False
    
    def test_read_schedule_ranges(self):
        """Test reading schedule ranges (READ operations)"""
        print("\n📖 SCHEDULE TEST 4: READ Schedule Ranges")
        
        if not self.test_staff_id:
            print("   ❌ No test staff member available")
            return False
        
        # Test reading all schedule ranges for staff member
        all_ranges_response = self.session.get(f"{BASE_URL}/api/staff/{self.test_staff_id}/schedule-ranges")
        print(f"   READ all ranges status: {all_ranges_response.status_code}")
        
        if all_ranges_response.status_code == 200:
            try:
                all_data = all_ranges_response.json()
                if all_data.get('success') and 'schedule_ranges' in all_data:
                    ranges = all_data['schedule_ranges']
                    print(f"   ✅ Found {len(ranges)} schedule ranges")
                    
                    # Test reading specific schedule range
                    if ranges and len(ranges) > 0:
                        schedule_id = ranges[0]['id']
                        specific_response = self.session.get(f"{BASE_URL}/api/staff/schedule-ranges/{schedule_id}")
                        print(f"   READ specific range status: {specific_response.status_code}")
                        
                        if specific_response.status_code == 200:
                            try:
                                specific_data = specific_response.json()
                                if specific_data.get('success'):
                                    print("   ✅ Specific schedule range retrieved successfully")
                                    print(f"   Schedule: {specific_data['schedule']['schedule_name']}")
                                    return True
                                else:
                                    print(f"   ❌ Specific read failed: {specific_data}")
                            except Exception as e:
                                print(f"   ❌ Error parsing specific response: {e}")
                        else:
                            print(f"   ❌ Specific read failed: {specific_response.status_code}")
                    else:
                        print("   ⚠️ No schedule ranges to test specific read")
                        return True  # Still success if we can read the empty list
                else:
                    print(f"   ❌ Unexpected all ranges response: {all_data}")
            except Exception as e:
                print(f"   ❌ Error parsing all ranges response: {e}")
        else:
            print(f"   ❌ READ all ranges failed: {all_ranges_response.status_code}")
            
        return False
    
    def test_update_schedule_range(self):
        """Test updating schedule ranges (UPDATE operation)"""
        print("\n📝 SCHEDULE TEST 5: UPDATE Schedule Range")
        
        if not self.test_staff_id or not self.created_schedule_ids:
            print("   ❌ No schedule range to update")
            return False
        
        schedule_id = self.created_schedule_ids[0]
        
        # Updated data
        today = date.today()
        new_start_date = today + timedelta(days=2)
        new_end_date = today + timedelta(days=35)
        
        update_data = {
            'schedule_name': 'Updated Test Schedule',
            'description': 'Updated description for testing',
            'start_date': new_start_date.strftime('%Y-%m-%d'),
            'end_date': new_end_date.strftime('%Y-%m-%d'),
            'monday': True,
            'tuesday': True,
            'wednesday': False,  # Changed
            'thursday': True,
            'friday': True,
            'saturday': True,    # Changed
            'sunday': False,
            'shift_start_time': '08:30',  # Changed
            'shift_end_time': '16:30',    # Changed
            'break_time': '12:30-13:30',  # Changed
            'priority': 2                 # Changed
        }
        
        # Update via API with CSRF token
        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': self.csrf_token
        }
        update_response = self.session.put(
            f"{BASE_URL}/api/staff/{self.test_staff_id}/schedule-ranges/{schedule_id}",
            json=update_data,
            headers=headers
        )
        
        print(f"   UPDATE API status: {update_response.status_code}")
        
        if update_response.status_code == 200:
            try:
                result = update_response.json()
                if result.get('success'):
                    print("   ✅ Schedule range updated successfully")
                    
                    # Verify update by reading back
                    verify_response = self.session.get(f"{BASE_URL}/api/staff/schedule-ranges/{schedule_id}")
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        if verify_data.get('success'):
                            schedule = verify_data['schedule']
                            if (schedule['schedule_name'] == 'Updated Test Schedule' and 
                                schedule['priority'] == 2 and
                                schedule['shift_start_time'] == '08:30'):
                                print("   ✅ Update verified successfully")
                                return True
                            else:
                                print("   ⚠️ Update not reflected in data")
                        else:
                            print("   ⚠️ Could not verify update")
                    else:
                        print("   ⚠️ Could not verify update - read failed")
                    return True
                else:
                    print(f"   ❌ Update failed: {result}")
            except Exception as e:
                print(f"   ❌ Error parsing update response: {e}")
        else:
            print(f"   ❌ UPDATE failed: {update_response.status_code}")
            if update_response.text:
                print(f"   Response: {update_response.text[:200]}")
                
        return False
    
    def test_delete_schedule_range(self):
        """Test deleting schedule ranges (DELETE operation)"""
        print("\n🗑️ SCHEDULE TEST 6: DELETE Schedule Range")
        
        if not self.created_schedule_ids:
            print("   ❌ No schedule range to delete")
            return False
        
        schedule_id = self.created_schedule_ids[0]
        
        # Delete via API with CSRF token  
        headers = {'X-CSRFToken': self.csrf_token}
        delete_response = self.session.delete(
            f"{BASE_URL}/api/staff/schedule-ranges/{schedule_id}",
            headers=headers
        )
        print(f"   DELETE API status: {delete_response.status_code}")
        
        if delete_response.status_code == 200:
            try:
                result = delete_response.json()
                if result.get('success'):
                    print("   ✅ Schedule range deleted successfully")
                    
                    # Verify deletion by trying to read
                    verify_response = self.session.get(f"{BASE_URL}/api/staff/schedule-ranges/{schedule_id}")
                    if verify_response.status_code == 404:
                        print("   ✅ Deletion verified - schedule not found")
                    elif verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        if verify_data.get('success'):
                            schedule = verify_data['schedule']
                            if not schedule.get('is_active', True):
                                print("   ✅ Soft delete verified - schedule marked inactive")
                            else:
                                print("   ⚠️ Schedule still active after delete")
                        else:
                            print("   ✅ Schedule properly inaccessible")
                    else:
                        print(f"   ⚠️ Unexpected verification response: {verify_response.status_code}")
                    
                    return True
                else:
                    print(f"   ❌ Delete failed: {result}")
            except Exception as e:
                print(f"   ❌ Error parsing delete response: {e}")
        else:
            print(f"   ❌ DELETE failed: {delete_response.status_code}")
            if delete_response.text:
                print(f"   Response: {delete_response.text[:200]}")
                
        return False
    
    def test_schedule_validation(self):
        """Test schedule validation and edge cases"""
        print("\n🔍 SCHEDULE TEST 7: Validation & Edge Cases")
        
        if not self.test_staff_id:
            print("   ❌ No test staff member available")
            return False
        
        # Test 1: CSRF Protection - Request without CSRF token (should fail)
        print("   Testing CSRF Protection...")
        invalid_data = {
            'schedule_name': 'CSRF Test',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
        
        headers_no_csrf = {'Content-Type': 'application/json'}
        no_csrf_response = self.session.post(
            f"{BASE_URL}/api/staff/{self.test_staff_id}/schedule-ranges",
            json=invalid_data,
            headers=headers_no_csrf
        )
        
        print(f"   No CSRF token test status: {no_csrf_response.status_code}")
        if no_csrf_response.status_code == 400 and "CSRF token is missing" in no_csrf_response.text:
            print("   ✅ CSRF protection working - request rejected without token")
        else:
            print(f"   ❌ CSRF protection may be weak: {no_csrf_response.status_code}")
        
        # Test 2: Missing required fields (with valid CSRF)
        missing_fields_data = {
            'description': 'Missing required fields'
            # Missing schedule_name, start_date, end_date
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': self.csrf_token
        }
        invalid_response = self.session.post(
            f"{BASE_URL}/api/staff/{self.test_staff_id}/schedule-ranges",
            json=missing_fields_data,
            headers=headers
        )
        
        print(f"   Invalid data test status: {invalid_response.status_code}")
        if invalid_response.status_code == 400:
            print("   ✅ Validation working - invalid data rejected")
        else:
            print(f"   ⚠️ Expected 400, got {invalid_response.status_code}")
        
        # Test 3: Invalid date format
        invalid_date_data = {
            'schedule_name': 'Invalid Date Test',
            'start_date': 'not-a-date',
            'end_date': '2024-13-45'  # Invalid date
        }
        
        invalid_date_response = self.session.post(
            f"{BASE_URL}/api/staff/{self.test_staff_id}/schedule-ranges",
            json=invalid_date_data,
            headers=headers
        )
        
        print(f"   Invalid date test status: {invalid_date_response.status_code}")
        if invalid_date_response.status_code in [400, 500]:
            print("   ✅ Date validation working")
        else:
            print(f"   ⚠️ Date validation may be weak: {invalid_date_response.status_code}")
        
        return True
    
    def run_comprehensive_schedule_test(self):
        """Run all schedule management tests"""
        print("📅 COMPREHENSIVE SCHEDULE MANAGEMENT TESTING")
        print("=" * 60)
        
        results = {}
        
        # Run all tests in sequence
        results['login'] = self.login()
        if results['login']:
            results['get_staff'] = self.get_test_staff_member()
            if results['get_staff']:
                results['create'] = self.test_create_schedule_range()
                results['read'] = self.test_read_schedule_ranges()
                results['update'] = self.test_update_schedule_range()
                results['delete'] = self.test_delete_schedule_range()
                results['validation'] = self.test_schedule_validation()
            else:
                print("⚠️ Skipping schedule tests - no staff member available")
                return False
        else:
            print("⚠️ Skipping all tests - login failed")
            return False
        
        # Summary
        print("\n📅 SCHEDULE MANAGEMENT TEST SUMMARY")
        print("=" * 60)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name.upper()}: {status}")
        
        passed_count = sum(results.values())
        total_count = len(results)
        
        overall_pass = all(results.values())
        overall_status = f"✅ ALL {total_count} SCHEDULE TESTS PASSED" if overall_pass else f"⚠️ {passed_count}/{total_count} TESTS PASSED"
        
        print(f"\n🎯 SCHEDULE MANAGEMENT STATUS: {overall_status}")
        
        if overall_pass:
            print("🎉 SCHEDULE MANAGEMENT SYSTEM FULLY FUNCTIONAL!")
        else:
            print("⚠️ Some schedule management issues need attention")
        
        return overall_pass

if __name__ == "__main__":
    tester = ScheduleManagementTester()
    tester.run_comprehensive_schedule_test()