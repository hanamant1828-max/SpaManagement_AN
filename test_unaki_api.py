
#!/usr/bin/env python3
"""
Unaki Appointment Booking API Testing Script
Tests all endpoints for the Unaki booking system to ensure proper functionality
"""

import requests
import json
from datetime import datetime, date

# Configuration
BASE_URL = "http://127.0.0.1:5000"
API_BASE = f"{BASE_URL}/api/unaki"

class UnakiAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
    
    def test_health_check(self):
        """Test basic server connectivity"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                self.log_test("Health Check", True, "Server is running")
                return True
            else:
                self.log_test("Health Check", False, f"Server returned {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log_test("Health Check", False, "Cannot connect to server")
            return False
    
    def test_get_staff(self):
        """Test Case 1: Fetching Staff Data"""
        try:
            response = self.session.get(f"{API_BASE}/staff")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Staff", True, f"Retrieved {len(data)} staff members")
                    return True, data
                else:
                    self.log_test("Get Staff", False, "Response is not a list")
                    return False, None
            else:
                self.log_test("Get Staff", False, f"Status code: {response.status_code}")
                return False, None
                
        except Exception as e:
            self.log_test("Get Staff", False, f"Exception: {str(e)}")
            return False, None
    
    def test_get_appointments(self):
        """Test Case 2: Fetching Appointments Data"""
        try:
            response = self.session.get(f"{API_BASE}/appointments")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Appointments", True, f"Retrieved {len(data)} appointments")
                    return True, data
                else:
                    self.log_test("Get Appointments", False, "Response is not a list")
                    return False, None
            else:
                self.log_test("Get Appointments", False, f"Status code: {response.status_code}")
                return False, None
                
        except Exception as e:
            self.log_test("Get Appointments", False, f"Exception: {str(e)}")
            return False, None
    
    def test_get_breaks(self):
        """Test Case 3: Fetching Breaks Data"""
        try:
            response = self.session.get(f"{API_BASE}/breaks")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Breaks", True, f"Retrieved {len(data)} breaks")
                    return True, data
                else:
                    self.log_test("Get Breaks", False, "Response is not a list")
                    return False, None
            else:
                self.log_test("Get Breaks", False, f"Status code: {response.status_code}")
                return False, None
                
        except Exception as e:
            self.log_test("Get Breaks", False, f"Exception: {str(e)}")
            return False, None
    
    def test_load_sample_data(self):
        """Test Case 4: Load Sample Data"""
        try:
            response = self.session.post(f"{API_BASE}/load-sample-data")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("Load Sample Data", True, data.get('message', 'Sample data loaded'))
                    return True, data
                else:
                    self.log_test("Load Sample Data", False, data.get('error', 'Unknown error'))
                    return False, None
            else:
                self.log_test("Load Sample Data", False, f"Status code: {response.status_code}")
                return False, None
                
        except Exception as e:
            self.log_test("Load Sample Data", False, f"Exception: {str(e)}")
            return False, None
    
    def test_successful_appointment_booking(self, staff_data=None):
        """Test Case 5: Successful Appointment Booking"""
        try:
            # Use first available staff member or default to ID 1
            staff_id = 1
            if staff_data and len(staff_data) > 0:
                staff_id = staff_data[0].get('id', 1)
            
            # Create valid appointment data
            appointment_data = {
                "staffId": staff_id,
                "clientName": "Test Client",
                "service": "Test Massage",
                "startTime": "14:00",
                "endTime": "15:00",
                "appointmentDate": date.today().isoformat(),
                "clientPhone": "555-1234",
                "notes": "API Test Appointment"
            }
            
            response = self.session.post(
                f"{API_BASE}/appointments",
                json=appointment_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("Successful Booking", True, data.get('message', 'Appointment created'))
                    return True, data
                else:
                    self.log_test("Successful Booking", False, data.get('error', 'Booking failed'))
                    return False, None
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', f'Status code: {response.status_code}')
                except:
                    error_msg = f'Status code: {response.status_code}'
                self.log_test("Successful Booking", False, error_msg)
                return False, None
                
        except Exception as e:
            self.log_test("Successful Booking", False, f"Exception: {str(e)}")
            return False, None
    
    def test_failed_booking_missing_fields(self):
        """Test Case 6: Failed Booking (Missing Required Fields)"""
        try:
            # Create invalid appointment data (missing required fields)
            invalid_data = {
                "clientName": "Test Client",
                "service": "Test Service"
                # Missing: staffId, startTime, endTime
            }
            
            response = self.session.post(
                f"{API_BASE}/appointments",
                json=invalid_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 400:
                data = response.json()
                if 'Missing required fields' in data.get('error', ''):
                    self.log_test("Failed Booking Validation", True, "Correctly rejected missing fields")
                    return True
                else:
                    self.log_test("Failed Booking Validation", False, f"Unexpected error: {data.get('error')}")
                    return False
            else:
                self.log_test("Failed Booking Validation", False, f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Failed Booking Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_failed_booking_invalid_staff(self):
        """Test Case 7: Failed Booking (Invalid Staff ID)"""
        try:
            # Create appointment data with invalid staff ID
            invalid_data = {
                "staffId": 99999,  # Non-existent staff ID
                "clientName": "Test Client",
                "service": "Test Service",
                "startTime": "14:00",
                "endTime": "15:00",
                "appointmentDate": date.today().isoformat()
            }
            
            response = self.session.post(
                f"{API_BASE}/appointments",
                json=invalid_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 404:
                data = response.json()
                if 'not found' in data.get('error', '').lower():
                    self.log_test("Invalid Staff Validation", True, "Correctly rejected invalid staff ID")
                    return True
                else:
                    self.log_test("Invalid Staff Validation", False, f"Unexpected error: {data.get('error')}")
                    return False
            else:
                self.log_test("Invalid Staff Validation", False, f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Staff Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_failed_booking_invalid_time(self):
        """Test Case 8: Failed Booking (Invalid Time Format)"""
        try:
            # Create appointment data with invalid time format
            invalid_data = {
                "staffId": 1,
                "clientName": "Test Client",
                "service": "Test Service",
                "startTime": "25:00",  # Invalid time
                "endTime": "15:00",
                "appointmentDate": date.today().isoformat()
            }
            
            response = self.session.post(
                f"{API_BASE}/appointments",
                json=invalid_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 400:
                data = response.json()
                if 'time format' in data.get('error', '').lower() or 'invalid' in data.get('error', '').lower():
                    self.log_test("Invalid Time Validation", True, "Correctly rejected invalid time")
                    return True
                else:
                    self.log_test("Invalid Time Validation", False, f"Unexpected error: {data.get('error')}")
                    return False
            else:
                self.log_test("Invalid Time Validation", False, f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Time Validation", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all test cases"""
        print("🧪 Starting Unaki API Test Suite")
        print("=" * 50)
        
        # Test 1: Health Check
        if not self.test_health_check():
            print("\n❌ Server is not running. Please start the Flask application first.")
            return False
        
        # Test 2: Load sample data first
        print("\n📊 Loading sample data...")
        self.test_load_sample_data()
        
        # Test 3: Get staff data
        print("\n👥 Testing staff endpoints...")
        staff_success, staff_data = self.test_get_staff()
        
        # Test 4: Get appointments
        print("\n📅 Testing appointment endpoints...")
        self.test_get_appointments()
        
        # Test 5: Get breaks
        print("\n☕ Testing break endpoints...")
        self.test_get_breaks()
        
        # Test 6: Successful booking
        print("\n✅ Testing successful appointment booking...")
        self.test_successful_appointment_booking(staff_data if staff_success else None)
        
        # Test 7: Failed booking tests
        print("\n❌ Testing validation scenarios...")
        self.test_failed_booking_missing_fields()
        self.test_failed_booking_invalid_staff()
        self.test_failed_booking_invalid_time()
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 All tests passed! The Unaki API is working correctly.")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
            
        return passed == total

def main():
    """Main execution function"""
    print("🚀 Unaki Appointment Booking API Tester")
    print("This script will test all API endpoints for the Unaki booking system.\n")
    
    tester = UnakiAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ API testing completed successfully!")
    else:
        print("\n❌ Some tests failed. Check the server logs for more details.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
