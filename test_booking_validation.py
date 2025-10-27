#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing for Booking Acceptance Validation
Tests all scenarios: staff availability, schedule conflicts, and client overlaps
"""

import sys
from datetime import datetime, time, date, timedelta
from app import app, db
from models import UnakiBooking, User, ShiftManagement, ShiftLogs, Service, Customer
from modules.bookings.online_booking_queries import accept_booking
from sqlalchemy import text

def print_header(text):
    """Print formatted test section header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_test(num, description):
    """Print test description"""
    print(f"\n[TEST {num}] {description}")
    print("-" * 80)

def print_result(success, message):
    """Print test result"""
    if success:
        print(f"✅ PASS: {message}")
    else:
        print(f"❌ FAIL: {message}")
    return success

def setup_test_data():
    """Create comprehensive test data for all scenarios"""
    print_header("SETTING UP TEST DATA")
    
    with app.app_context():
        # Get or create test staff members
        staff1 = User.query.filter_by(username='staff1_test').first()
        if not staff1:
            from werkzeug.security import generate_password_hash
            staff1 = User(
                username='staff1_test',
                first_name='Test',
                last_name='Staff1',
                email='staff1@test.com',
                password_hash=generate_password_hash('test123'),
                role='staff',
                is_active=True
            )
            db.session.add(staff1)
            db.session.commit()
        
        staff2 = User.query.filter_by(username='staff2_test').first()
        if not staff2:
            from werkzeug.security import generate_password_hash
            staff2 = User(
                username='staff2_test',
                first_name='Test',
                last_name='Staff2',
                email='staff2@test.com',
                password_hash=generate_password_hash('test123'),
                role='staff',
                is_active=True
            )
            db.session.add(staff2)
            db.session.commit()
        
        # Get an existing service from the database
        service = Service.query.filter_by(is_active=True).first()
        if not service:
            # If no services exist, create one with required fields
            service = Service(
                name='Test Service',
                duration=60,
                price=100.0,
                category='Test',
                is_active=True
            )
            db.session.add(service)
            db.session.commit()
        
        # Create test client
        client = Customer.query.filter_by(phone='1234567890').first()
        if not client:
            client = Customer(
                first_name='Test',
                last_name='Client',
                phone='1234567890',
                email='client@test.com'
            )
            db.session.add(client)
            db.session.commit()
        
        # Create staff schedule for tomorrow (to avoid conflicts with today)
        tomorrow = date.today() + timedelta(days=1)
        
        # Create or get shift management for staff
        shift_mgmt = ShiftManagement.query.filter_by(staff_id=staff1.id).first()
        if not shift_mgmt:
            shift_mgmt = ShiftManagement(
                staff_id=staff1.id,
                from_date=tomorrow,
                to_date=tomorrow + timedelta(days=30)
            )
            db.session.add(shift_mgmt)
            db.session.commit()
        
        # Delete existing test shift logs for tomorrow
        ShiftLogs.query.filter_by(
            shift_management_id=shift_mgmt.id,
            individual_date=tomorrow
        ).delete()
        
        # Create shift log for tomorrow
        schedule = ShiftLogs(
            shift_management_id=shift_mgmt.id,
            individual_date=tomorrow,
            shift_start_time=time(9, 0),
            shift_end_time=time(18, 0),
            break_start_time=time(12, 0),
            break_end_time=time(13, 0),
            status='scheduled'
        )
        db.session.add(schedule)
        db.session.commit()
        
        print(f"✅ Test data created:")
        print(f"   - Staff: {staff1.first_name} {staff1.last_name} (ID: {staff1.id})")
        print(f"   - Staff: {staff2.first_name} {staff2.last_name} (ID: {staff2.id})")
        print(f"   - Service: {service.name} (ID: {service.id})")
        print(f"   - Client: {client.first_name} {client.last_name} (ID: {client.id})")
        print(f"   - Schedule for {tomorrow}: 9:00 AM - 6:00 PM (Break: 12:00 PM - 1:00 PM)")
        
        return {
            'staff1': staff1,
            'staff2': staff2,
            'service': service,
            'client': client,
            'tomorrow': tomorrow,
            'schedule': schedule
        }

def create_test_booking(client_name, client_phone, client_email, service_name, service_price, 
                       service_duration, appointment_date, start_time, end_time, client_id=None):
    """Helper to create a test booking"""
    booking = UnakiBooking(
        client_name=client_name,
        client_phone=client_phone,
        client_email=client_email,
        service_name=service_name,
        service_price=service_price,
        service_duration=service_duration,
        appointment_date=appointment_date,
        start_time=start_time,
        end_time=end_time,
        status='scheduled',
        booking_source='online',
        client_id=client_id
    )
    db.session.add(booking)
    db.session.commit()
    return booking

def cleanup_test_bookings():
    """Remove all test bookings"""
    with app.app_context():
        UnakiBooking.query.filter_by(booking_source='online', status='scheduled').delete()
        db.session.commit()

def test_successful_acceptance(test_data):
    """TEST 1: Successful booking acceptance (all validations pass)"""
    print_test(1, "Successful Booking Acceptance")
    
    with app.app_context():
        # Create a valid booking
        tomorrow = test_data['tomorrow']
        booking = create_test_booking(
            client_name='Happy Customer',
            client_phone='9999999999',
            client_email='happy@test.com',
            service_name='Test Service',
            service_price=100.0,
            service_duration=60,
            appointment_date=tomorrow,
            start_time=time(10, 0),  # 10:00 AM - within shift hours, not during break
            end_time=time(11, 0)
        )
        
        # Try to accept it
        result, error = accept_booking(booking.id, test_data['staff1'].id)
        
        if result and not error:
            return print_result(True, f"Booking #{booking.id} accepted successfully")
        else:
            return print_result(False, f"Expected success, got error: {error}")

def test_outside_shift_hours(test_data):
    """TEST 2: Booking outside staff shift hours"""
    print_test(2, "Validation: Outside Shift Hours")
    
    with app.app_context():
        tomorrow = test_data['tomorrow']
        booking = create_test_booking(
            client_name='Early Bird',
            client_phone='8888888888',
            client_email='early@test.com',
            service_name='Test Service',
            service_price=100.0,
            service_duration=60,
            appointment_date=tomorrow,
            start_time=time(8, 0),  # 8:00 AM - before shift starts at 9:00 AM
            end_time=time(9, 0)
        )
        
        result, error = accept_booking(booking.id, test_data['staff1'].id)
        
        if not result and error and 'shift hours' in error.lower():
            return print_result(True, f"Correctly rejected: {error}")
        else:
            return print_result(False, f"Expected shift hours error, got: {error}")

def test_during_break_time(test_data):
    """TEST 3: Booking during staff break time"""
    print_test(3, "Validation: During Break Time")
    
    with app.app_context():
        tomorrow = test_data['tomorrow']
        booking = create_test_booking(
            client_name='Lunch Time Customer',
            client_phone='7777777777',
            client_email='lunch@test.com',
            service_name='Test Service',
            service_price=100.0,
            service_duration=60,
            appointment_date=tomorrow,
            start_time=time(12, 0),  # 12:00 PM - during break (12:00 PM - 1:00 PM)
            end_time=time(13, 0)
        )
        
        result, error = accept_booking(booking.id, test_data['staff1'].id)
        
        if not result and error and 'break' in error.lower():
            return print_result(True, f"Correctly rejected: {error}")
        else:
            return print_result(False, f"Expected break time error, got: {error}")

def test_staff_schedule_conflict(test_data):
    """TEST 4: Staff already has another appointment"""
    print_test(4, "Validation: Staff Schedule Conflict")
    
    with app.app_context():
        tomorrow = test_data['tomorrow']
        
        # First, create and accept a booking
        booking1 = create_test_booking(
            client_name='First Customer',
            client_phone='6666666666',
            client_email='first@test.com',
            service_name='Test Service',
            service_price=100.0,
            service_duration=60,
            appointment_date=tomorrow,
            start_time=time(14, 0),  # 2:00 PM
            end_time=time(15, 0)
        )
        result1, _ = accept_booking(booking1.id, test_data['staff1'].id)
        
        if not result1:
            return print_result(False, "Failed to set up first booking")
        
        # Now try to book overlapping time with same staff
        booking2 = create_test_booking(
            client_name='Second Customer',
            client_phone='5555555555',
            client_email='second@test.com',
            service_name='Test Service',
            service_price=100.0,
            service_duration=60,
            appointment_date=tomorrow,
            start_time=time(14, 30),  # 2:30 PM - overlaps with 2:00-3:00 PM
            end_time=time(15, 30)
        )
        
        result2, error = accept_booking(booking2.id, test_data['staff1'].id)
        
        if not result2 and error and 'conflict' in error.lower():
            return print_result(True, f"Correctly rejected: {error}")
        else:
            return print_result(False, f"Expected staff conflict error, got: {error}")

def test_client_schedule_conflict(test_data):
    """TEST 5: Client already has another appointment"""
    print_test(5, "Validation: Client Schedule Conflict")
    
    with app.app_context():
        tomorrow = test_data['tomorrow']
        client = test_data['client']
        
        # Create and accept first booking for client
        booking1 = create_test_booking(
            client_name=f'{client.first_name} {client.last_name}',
            client_phone=client.phone,
            client_email=client.email,
            service_name='First Service',
            service_price=100.0,
            service_duration=60,
            appointment_date=tomorrow,
            start_time=time(15, 0),  # 3:00 PM
            end_time=time(16, 0),
            client_id=client.id
        )
        result1, _ = accept_booking(booking1.id, test_data['staff1'].id)
        
        if not result1:
            return print_result(False, "Failed to set up first client booking")
        
        # Try to book same client at overlapping time with different staff
        booking2 = create_test_booking(
            client_name=f'{client.first_name} {client.last_name}',
            client_phone=client.phone,
            client_email=client.email,
            service_name='Second Service',
            service_price=100.0,
            service_duration=60,
            appointment_date=tomorrow,
            start_time=time(15, 30),  # 3:30 PM - overlaps with 3:00-4:00 PM
            end_time=time(16, 30),
            client_id=client.id
        )
        
        result2, error = accept_booking(booking2.id, test_data['staff2'].id)
        
        if not result2 and error and 'client' in error.lower() and 'conflict' in error.lower():
            return print_result(True, f"Correctly rejected: {error}")
        else:
            return print_result(False, f"Expected client conflict error, got: {error}")

def test_multiple_validation_failures(test_data):
    """TEST 6: Multiple validation failures at once"""
    print_test(6, "Validation: Multiple Issues Simultaneously")
    
    with app.app_context():
        tomorrow = test_data['tomorrow']
        
        # Create booking that violates multiple rules:
        # 1. Outside shift hours (before 9 AM)
        # 2. Could also overlap with break if we make it span long enough
        booking = create_test_booking(
            client_name='Problem Customer',
            client_phone='4444444444',
            client_email='problem@test.com',
            service_name='Test Service',
            service_price=100.0,
            service_duration=240,  # 4 hours long
            appointment_date=tomorrow,
            start_time=time(7, 0),  # 7:00 AM - before shift
            end_time=time(11, 0)
        )
        
        result, error = accept_booking(booking.id, test_data['staff1'].id)
        
        if not result and error:
            # Should have at least one error
            return print_result(True, f"Correctly rejected with errors: {error}")
        else:
            return print_result(False, f"Expected validation errors, got: {error}")

def test_bulk_acceptance_mixed_results(test_data):
    """TEST 7: Bulk acceptance with some passing, some failing"""
    print_test(7, "Bulk Acceptance: Mixed Results")
    
    with app.app_context():
        tomorrow = test_data['tomorrow']
        
        # Create multiple bookings
        valid_booking = create_test_booking(
            client_name='Valid Customer',
            client_phone='3333333333',
            client_email='valid@test.com',
            service_name='Test Service',
            service_price=100.0,
            service_duration=60,
            appointment_date=tomorrow,
            start_time=time(16, 0),  # 4:00 PM - valid time
            end_time=time(17, 0)
        )
        
        invalid_booking = create_test_booking(
            client_name='Invalid Customer',
            client_phone='2222222222',
            client_email='invalid@test.com',
            service_name='Test Service',
            service_price=100.0,
            service_duration=60,
            appointment_date=tomorrow,
            start_time=time(19, 0),  # 7:00 PM - after shift ends
            end_time=time(20, 0)
        )
        
        result1, error1 = accept_booking(valid_booking.id, test_data['staff1'].id)
        result2, error2 = accept_booking(invalid_booking.id, test_data['staff1'].id)
        
        if result1 and not result2:
            return print_result(True, f"Valid accepted ✓, Invalid rejected ✓: {error2}")
        else:
            return print_result(False, f"Expected mixed results - Valid: {error1}, Invalid: {error2}")

def run_all_tests():
    """Execute all test scenarios"""
    print_header("BOOKING ACCEPTANCE VALIDATION - COMPREHENSIVE END-TO-END TESTING")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Setup
        test_data = setup_test_data()
        
        # Cleanup any existing test bookings
        cleanup_test_bookings()
        
        # Run all tests
        results = []
        results.append(test_successful_acceptance(test_data))
        
        cleanup_test_bookings()
        results.append(test_outside_shift_hours(test_data))
        
        cleanup_test_bookings()
        results.append(test_during_break_time(test_data))
        
        cleanup_test_bookings()
        results.append(test_staff_schedule_conflict(test_data))
        
        cleanup_test_bookings()
        results.append(test_client_schedule_conflict(test_data))
        
        cleanup_test_bookings()
        results.append(test_multiple_validation_failures(test_data))
        
        cleanup_test_bookings()
        results.append(test_bulk_acceptance_mixed_results(test_data))
        
        # Summary
        print_header("TEST SUMMARY")
        passed = sum(results)
        total = len(results)
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: ✅ {passed}")
        print(f"Failed: ❌ {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! The booking validation system is working correctly.")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Final cleanup
        cleanup_test_bookings()
        
        return passed == total
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
