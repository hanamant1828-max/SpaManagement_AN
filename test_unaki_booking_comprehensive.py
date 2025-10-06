#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing for Unaki Booking System
Tests all booking scenarios, API endpoints, and error handling
"""

import requests
import json
from datetime import datetime, date, timedelta, time
from typing import Dict, List, Any
import sys

class UnakiBookingTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.created_bookings = []
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            'test': test_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if message:
            print(f"   → {message}")
        print()
    
    def login(self, username="admin", password="admin123"):
        """Authenticate with the system"""
        print("=" * 80)
        print("🔐 Authenticating...")
        print("=" * 80)
        
        response = self.session.post(
            f"{self.base_url}/login",
            data={
                'username': username,
                'password': password
            },
            allow_redirects=False
        )
        
        if response.status_code in [200, 302]:
            self.log_test("Authentication", True, "Successfully logged in")
            return True
        else:
            self.log_test("Authentication", False, f"Login failed: {response.status_code}")
            return False
    
    def test_main_page_loads(self):
        """Test 1: Main Unaki booking page loads correctly"""
        print("=" * 80)
        print("📄 Test 1: Main Page Load")
        print("=" * 80)
        
        response = self.session.get(f"{self.base_url}/unaki-booking")
        
        if response.status_code == 200:
            # Check for essential elements in the response
            has_staff = 'staff_members' in response.text or 'staffId' in response.text
            has_services = 'services' in response.text or 'serviceType' in response.text
            has_clients = 'clients' in response.text or 'clientName' in response.text
            
            if has_staff and has_services and has_clients:
                self.log_test("Main page loads with data", True, "Staff, services, and clients data present")
            else:
                missing = []
                if not has_staff: missing.append("staff")
                if not has_services: missing.append("services")
                if not has_clients: missing.append("clients")
                self.log_test("Main page loads with data", False, f"Missing: {', '.join(missing)}")
        else:
            self.log_test("Main page loads", False, f"Status: {response.status_code}")
    
    def test_create_standard_appointment(self):
        """Test 2: Create standard appointment via drag-select"""
        print("=" * 80)
        print("📝 Test 2: Standard Appointment Creation")
        print("=" * 80)
        
        today = date.today()
        start_time = "10:00"
        end_time = "11:00"
        
        appointment_data = {
            'client_name': 'Test Client Standard',
            'client_phone': '555-0001',
            'staff_id': 1,
            'staff_name': 'Test Staff',
            'service_name': 'Swedish Massage',
            'service_duration': 60,
            'service_price': 100.00,
            'appointment_date': today.strftime('%Y-%m-%d'),
            'start_time': start_time,
            'end_time': end_time,
            'booking_method': 'drag_select',
            'booking_source': 'unaki_system'
        }
        
        response = self.session.post(
            f"{self.base_url}/api/unaki/book-appointment",
            json=appointment_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                self.created_bookings.append(data.get('appointment_id'))
                self.log_test("Create standard appointment", True, 
                             f"Appointment ID: {data.get('appointment_id')}")
            else:
                self.log_test("Create standard appointment", False, 
                             f"API returned error: {data.get('error')}")
        else:
            self.log_test("Create standard appointment", False, 
                         f"Status: {response.status_code}, Response: {response.text[:200]}")
    
    def test_create_quick_booking(self):
        """Test 3: Create quick booking"""
        print("=" * 80)
        print("⚡ Test 3: Quick Booking")
        print("=" * 80)
        
        today = date.today()
        
        booking_data = {
            'client_name': 'Walk-in Client',
            'client_phone': '555-0002',
            'staff_id': 1,
            'service_name': 'Quick Facial',
            'service_duration': 30,
            'service_price': 50.00,
            'appointment_date': today.strftime('%Y-%m-%d'),
            'start_time': '11:30',
            'end_time': '12:00',
            'booking_method': 'quick_book',
            'booking_source': 'walk_in'
        }
        
        response = self.session.post(
            f"{self.base_url}/api/unaki/book-appointment",
            json=booking_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                self.created_bookings.append(data.get('appointment_id'))
                self.log_test("Create quick booking", True, 
                             f"Appointment ID: {data.get('appointment_id')}")
            else:
                self.log_test("Create quick booking", False, 
                             f"Error: {data.get('error')}")
        else:
            self.log_test("Create quick booking", False, 
                         f"Status: {response.status_code}")
    
    def test_consecutive_bookings(self):
        """Test 4: Consecutive bookings (back-to-back)"""
        print("=" * 80)
        print("🔗 Test 4: Consecutive Bookings")
        print("=" * 80)
        
        today = date.today()
        bookings = [
            {
                'client_name': 'Client Consecutive 1',
                'staff_id': 2,
                'service_name': 'Manicure',
                'service_duration': 45,
                'start_time': '14:00',
                'end_time': '14:45'
            },
            {
                'client_name': 'Client Consecutive 2',
                'staff_id': 2,
                'service_name': 'Pedicure',
                'service_duration': 60,
                'start_time': '14:45',
                'end_time': '15:45'
            }
        ]
        
        success_count = 0
        for i, booking in enumerate(bookings, 1):
            booking.update({
                'appointment_date': today.strftime('%Y-%m-%d'),
                'service_price': 0.00,
                'booking_method': 'manual'
            })
            
            response = self.session.post(
                f"{self.base_url}/api/unaki/book-appointment",
                json=booking,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    success_count += 1
                    self.created_bookings.append(data.get('appointment_id'))
        
        if success_count == 2:
            self.log_test("Consecutive bookings", True, 
                         "Both back-to-back appointments created successfully")
        else:
            self.log_test("Consecutive bookings", False, 
                         f"Only {success_count}/2 bookings created")
    
    def test_conflict_detection_overlapping(self):
        """Test 5: Conflict detection - overlapping times"""
        print("=" * 80)
        print("⚠️  Test 5: Conflict Detection - Overlapping Times")
        print("=" * 80)
        
        today = date.today()
        
        # First, create a booking
        first_booking = {
            'client_name': 'Original Client',
            'staff_id': 3,
            'service_name': 'Hair Cut',
            'service_duration': 60,
            'appointment_date': today.strftime('%Y-%m-%d'),
            'start_time': '10:00',
            'end_time': '11:00',
            'service_price': 75.00
        }
        
        response1 = self.session.post(
            f"{self.base_url}/api/unaki/book-appointment",
            json=first_booking,
            headers={'Content-Type': 'application/json'}
        )
        
        if response1.status_code == 200 and response1.json().get('success'):
            self.created_bookings.append(response1.json().get('appointment_id'))
            
            # Try to create overlapping booking (should fail)
            overlapping_booking = {
                'client_name': 'Conflicting Client',
                'staff_id': 3,  # Same staff
                'service_name': 'Shampoo',
                'service_duration': 30,
                'appointment_date': today.strftime('%Y-%m-%d'),
                'start_time': '10:30',  # Overlaps with first booking
                'end_time': '11:00',
                'service_price': 25.00
            }
            
            response2 = self.session.post(
                f"{self.base_url}/api/unaki/book-appointment",
                json=overlapping_booking,
                headers={'Content-Type': 'application/json'}
            )
            
            if response2.status_code == 400:
                data = response2.json()
                if 'conflict' in data.get('error', '').lower():
                    self.log_test("Overlap conflict detection", True, 
                                 f"Correctly rejected: {data.get('error')}")
                else:
                    self.log_test("Overlap conflict detection", False, 
                                 "Rejected but no conflict message")
            else:
                self.log_test("Overlap conflict detection", False, 
                             "Overlapping booking was allowed (should be blocked)")
        else:
            self.log_test("Overlap conflict detection", False, 
                         "Failed to create first booking for test")
    
    def test_conflict_check_api(self):
        """Test using the dedicated conflict check API"""
        print("=" * 80)
        print("🔍 Test 6: Conflict Check API")
        print("=" * 80)
        
        today = date.today()
        
        conflict_data = {
            'staff_id': 1,
            'appointment_date': today.strftime('%Y-%m-%d'),
            'start_time': '10:00',
            'end_time': '11:00'
        }
        
        response = self.session.post(
            f"{self.base_url}/api/unaki/check-conflicts",
            json=conflict_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            has_conflicts = data.get('has_conflicts', False)
            self.log_test("Conflict check API", True, 
                         f"API responded successfully. Conflicts: {has_conflicts}")
        else:
            self.log_test("Conflict check API", False, 
                         f"Status: {response.status_code}")
    
    def test_booking_sources(self):
        """Test 9: Different booking sources"""
        print("=" * 80)
        print("📱 Test 9: Booking Sources (phone, walk_in, online)")
        print("=" * 80)
        
        today = date.today()
        sources = ['phone', 'walk_in', 'online', 'unaki_system']
        success_count = 0
        
        for i, source in enumerate(sources):
            booking = {
                'client_name': f'{source.title()} Client',
                'staff_id': 1,
                'service_name': 'Basic Massage',
                'service_duration': 30,
                'appointment_date': today.strftime('%Y-%m-%d'),
                'start_time': f'{12 + i}:00',
                'end_time': f'{12 + i}:30',
                'service_price': 50.00,
                'booking_source': source
            }
            
            response = self.session.post(
                f"{self.base_url}/api/unaki/book-appointment",
                json=booking,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200 and response.json().get('success'):
                success_count += 1
                self.created_bookings.append(response.json().get('appointment_id'))
        
        if success_count == len(sources):
            self.log_test("All booking sources", True, 
                         f"All {len(sources)} booking sources work correctly")
        else:
            self.log_test("All booking sources", False, 
                         f"Only {success_count}/{len(sources)} sources worked")
    
    def test_appointment_statuses(self):
        """Test 10: Different appointment statuses"""
        print("=" * 80)
        print("📊 Test 10: Appointment Status Updates")
        print("=" * 80)
        
        if not self.created_bookings:
            self.log_test("Status updates", False, "No bookings available to test")
            return
        
        booking_id = self.created_bookings[0]
        statuses = ['scheduled', 'confirmed', 'in_progress', 'completed']
        success_count = 0
        
        for status in statuses:
            response = self.session.put(
                f"{self.base_url}/api/unaki/bookings/{booking_id}",
                json={'status': status},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    success_count += 1
        
        if success_count == len(statuses):
            self.log_test("Appointment status updates", True, 
                         f"All {len(statuses)} status transitions successful")
        else:
            self.log_test("Appointment status updates", False, 
                         f"Only {success_count}/{len(statuses)} status updates worked")
    
    def test_update_booking(self):
        """Test 11: Update existing booking"""
        print("=" * 80)
        print("✏️  Test 11: Update Existing Booking")
        print("=" * 80)
        
        if not self.created_bookings:
            self.log_test("Update booking", False, "No bookings available to test")
            return
        
        booking_id = self.created_bookings[-1]
        
        update_data = {
            'client_name': 'Updated Client Name',
            'service_name': 'Updated Service',
            'notes': 'This booking was updated during testing'
        }
        
        response = self.session.put(
            f"{self.base_url}/api/unaki/bookings/{booking_id}",
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                self.log_test("Update booking", True, 
                             f"Successfully updated booking {booking_id}")
            else:
                self.log_test("Update booking", False, 
                             f"Error: {data.get('error')}")
        else:
            self.log_test("Update booking", False, 
                         f"Status: {response.status_code}")
    
    def test_get_booking_details(self):
        """Test getting booking details"""
        print("=" * 80)
        print("🔎 Test: Get Booking Details")
        print("=" * 80)
        
        if not self.created_bookings:
            self.log_test("Get booking details", False, "No bookings available")
            return
        
        booking_id = self.created_bookings[0]
        
        response = self.session.get(
            f"{self.base_url}/api/unaki/bookings/{booking_id}"
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('id') == booking_id:
                self.log_test("Get booking details", True, 
                             f"Retrieved booking {booking_id} successfully")
            else:
                self.log_test("Get booking details", False, 
                             "Booking data mismatch")
        else:
            self.log_test("Get booking details", False, 
                         f"Status: {response.status_code}")
    
    def test_validation_errors(self):
        """Test 13: Error handling and validation"""
        print("=" * 80)
        print("❗ Test 13: Validation & Error Handling")
        print("=" * 80)
        
        # Test missing required fields
        invalid_data = {
            'client_name': 'Test Client'
            # Missing staff_id, service_name, times, etc.
        }
        
        response = self.session.post(
            f"{self.base_url}/api/unaki/book-appointment",
            json=invalid_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 400:
            data = response.json()
            if 'missing' in data.get('error', '').lower() or 'required' in data.get('error', '').lower():
                self.log_test("Validation - missing fields", True, 
                             f"Correctly rejected: {data.get('error')}")
            else:
                self.log_test("Validation - missing fields", False, 
                             "Rejected but no validation message")
        else:
            self.log_test("Validation - missing fields", False, 
                         "Invalid data was accepted (should be rejected)")
        
        # Test invalid date format
        invalid_date_data = {
            'client_name': 'Test',
            'staff_id': 1,
            'service_name': 'Test',
            'appointment_date': 'invalid-date',
            'start_time': '10:00',
            'end_time': '11:00'
        }
        
        response = self.session.post(
            f"{self.base_url}/api/unaki/book-appointment",
            json=invalid_date_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 400:
            self.log_test("Validation - invalid date format", True, 
                         "Correctly rejected invalid date")
        else:
            self.log_test("Validation - invalid date format", False, 
                         "Invalid date was accepted")
        
        # Test non-existent staff
        invalid_staff_data = {
            'client_name': 'Test',
            'staff_id': 99999,  # Non-existent
            'service_name': 'Test',
            'service_duration': 30,
            'appointment_date': date.today().strftime('%Y-%m-%d'),
            'start_time': '10:00',
            'end_time': '10:30'
        }
        
        response = self.session.post(
            f"{self.base_url}/api/unaki/book-appointment",
            json=invalid_staff_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 400:
            self.log_test("Validation - non-existent staff", True, 
                         "Correctly rejected non-existent staff")
        else:
            self.log_test("Validation - non-existent staff", False, 
                         "Non-existent staff was accepted")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['passed'])
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 Summary:")
        print(f"   Total Tests:  {total_tests}")
        print(f"   ✅ Passed:     {passed_tests}")
        print(f"   ❌ Failed:     {failed_tests}")
        print(f"   📈 Pass Rate:  {pass_rate:.1f}%")
        
        print(f"\n📝 Detailed Results:")
        print("-" * 80)
        
        for result in self.test_results:
            status = "✅" if result['passed'] else "❌"
            print(f"{status} {result['test']}")
            if result['message']:
                print(f"   {result['message']}")
        
        print("\n" + "=" * 80)
        
        # Save report to file
        report_file = f"unaki_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'pass_rate': pass_rate
                },
                'results': self.test_results,
                'created_bookings': self.created_bookings
            }, f, indent=2)
        
        print(f"📄 Full report saved to: {report_file}")
        print("=" * 80)
        
        return pass_rate >= 80  # Consider test suite successful if >=80% pass

def main():
    """Main test execution"""
    tester = UnakiBookingTester()
    
    print("\n🧪 UNAKI BOOKING SYSTEM - COMPREHENSIVE END-TO-END TESTING")
    print("=" * 80)
    print()
    
    # Authenticate
    if not tester.login():
        print("❌ Authentication failed. Cannot proceed with tests.")
        sys.exit(1)
    
    # Run all tests
    tester.test_main_page_loads()
    tester.test_create_standard_appointment()
    tester.test_create_quick_booking()
    tester.test_consecutive_bookings()
    tester.test_conflict_detection_overlapping()
    tester.test_conflict_check_api()
    tester.test_booking_sources()
    tester.test_get_booking_details()
    tester.test_appointment_statuses()
    tester.test_update_booking()
    tester.test_validation_errors()
    
    # Generate final report
    success = tester.generate_report()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
