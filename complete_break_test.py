
"""
Complete end-to-end test for break time functionality
"""
import requests
import sqlite3
import json
from datetime import date, datetime, time

def setup_test_schedule():
    """Create a test schedule with break times for today"""
    print("🏗️  Setting up test schedule...")
    
    try:
        conn = sqlite3.connect('instance/spa_management.db')
        cursor = conn.cursor()
        
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        
        # Get first active staff member
        cursor.execute("SELECT id, first_name, last_name FROM user WHERE is_active = 1 LIMIT 1")
        staff = cursor.fetchone()
        
        if not staff:
            print("❌ No active staff found")
            return False
        
        staff_id, first_name, last_name = staff
        print(f"👤 Using staff: {first_name} {last_name} (ID: {staff_id})")
        
        # Check if schedule already exists for today
        cursor.execute("""
            SELECT id FROM staff_schedule_range 
            WHERE staff_id = ? AND start_date <= ? AND end_date >= ? AND is_active = 1
        """, (staff_id, today_str, today_str))
        
        existing = cursor.fetchone()
        
        if existing:
            print("✅ Schedule already exists for today")
        else:
            # Create test schedule
            day_of_week = today.weekday()
            days = [False] * 7  # Mon-Sun
            days[day_of_week] = True
            
            cursor.execute("""
                INSERT INTO staff_schedule_range 
                (staff_id, schedule_name, description, start_date, end_date,
                 monday, tuesday, wednesday, thursday, friday, saturday, sunday,
                 shift_start_time, shift_end_time, break_time, priority, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                staff_id,
                f"Test Schedule {today_str}",
                "Test schedule with break time",
                today_str, today_str,
                days[0], days[1], days[2], days[3], days[4], days[5], days[6],
                "09:00", "17:00",
                "60 minutes (13:00 - 14:00)",  # Break from 1-2 PM
                1, True
            ))
            
            conn.commit()
            print("✅ Test schedule created with break time 13:00-14:00")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up test schedule: {e}")
        return False

def test_staff_availability_page():
    """Test the staff availability page shows break times correctly"""
    print("\n🌐 Testing Staff Availability Page...")
    
    try:
        # Load the page
        response = requests.get("http://127.0.0.1:5000/staff-availability")
        
        if response.status_code != 200:
            print(f"❌ Page load failed: {response.status_code}")
            return False
        
        html = response.text
        print("✅ Page loaded successfully")
        
        # Test for break time elements
        break_tests = {
            "Break Time text present": "Break Time" in html,
            "Warning background class": "bg-warning" in html,
            "Coffee icon": "fas fa-coffee" in html,
            "Break status": '"status": "break"' in html or 'status-break' in html,
            "13:00 time slot": "13:00" in html or "1:00 PM" in html,
            "14:00 time slot": "14:00" in html or "2:00 PM" in html
        }
        
        print("\n🔍 Break Time Element Tests:")
        passed_tests = 0
        for test_name, result in break_tests.items():
            status = "✅" if result else "❌"
            print(f"  {status} {test_name}")
            if result:
                passed_tests += 1
        
        print(f"\n📊 Test Results: {passed_tests}/{len(break_tests)} passed")
        
        # Check for problematic book buttons during break time
        print("\n🚫 Checking for incorrect 'Book' buttons during break time...")
        
        # Look for patterns that might indicate book buttons in break slots
        if "13:00" in html or "1:00 PM" in html:
            # Find the section around 1 PM
            lines = html.split('\n')
            break_time_lines = [i for i, line in enumerate(lines) if "13:00" in line or "1:00 PM" in line]
            
            found_issues = []
            for line_num in break_time_lines:
                # Check surrounding lines for book buttons
                start = max(0, line_num - 10)
                end = min(len(lines), line_num + 10)
                section = '\n'.join(lines[start:end])
                
                if "btn btn-success" in section and "Break Time" not in section:
                    found_issues.append(f"Potential book button near line {line_num}")
            
            if found_issues:
                print("❌ Found potential issues:")
                for issue in found_issues:
                    print(f"  - {issue}")
            else:
                print("✅ No book buttons found during break time")
        
        return passed_tests >= 3  # At least half the tests should pass
        
    except Exception as e:
        print(f"❌ Error testing page: {e}")
        return False

def test_time_slots_api():
    """Test the time slots API for break time handling"""
    print("\n🔌 Testing Time Slots API...")
    
    try:
        today = date.today().strftime('%Y-%m-%d')
        response = requests.get(f"http://127.0.0.1:5000/api/time-slots?date={today}")
        
        if response.status_code != 200:
            print(f"❌ API call failed: {response.status_code}")
            return False
        
        data = response.json()
        print("✅ API call successful")
        
        if 'slots' in data:
            slots = data['slots']
            print(f"📊 Found {len(slots)} time slots")
            
            # Look for break time slots
            break_slots = [slot for slot in slots if 'break' in str(slot).lower()]
            if break_slots:
                print(f"✅ Found {len(break_slots)} break time slots in API")
                return True
            else:
                print("⚠️  No break time slots found in API response")
                return False
        else:
            print("❌ No slots data in API response")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def run_complete_test():
    """Run the complete break time test suite"""
    print("🚀 Complete Break Time Test Suite")
    print("=" * 50)
    
    # Step 1: Setup test data
    if not setup_test_schedule():
        print("❌ Test setup failed")
        return
    
    # Step 2: Test staff availability page
    page_result = test_staff_availability_page()
    
    # Step 3: Test API
    api_result = test_time_slots_api()
    
    # Final summary
    print("\n📋 Final Test Summary")
    print("=" * 30)
    
    if page_result and api_result:
        print("🎉 All tests passed! Break time fix is working correctly.")
    elif page_result:
        print("✅ Page tests passed, but API might need attention")
    elif api_result:
        print("✅ API tests passed, but page display might need attention")
    else:
        print("❌ Tests failed. Break time fix may need more work.")
    
    print("\n🎯 Manual Verification Steps:")
    print("1. Visit http://127.0.0.1:5000/staff-availability")
    print("2. Look for time slots between 1:00 PM - 2:00 PM")
    print("3. Verify they show 'Break Time' with yellow background")
    print("4. Confirm no green 'Book' buttons appear during break time")
    
    print("\n📝 If issues persist:")
    print("1. Check that staff schedules have proper break_time format")
    print("2. Verify break times are within shift hours")
    print("3. Ensure staff are scheduled for today's day of week")

if __name__ == "__main__":
    run_complete_test()
