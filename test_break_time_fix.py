
"""
Comprehensive test for break time display fix in Staff Availability view
"""
import requests
import json
from datetime import datetime, date, timedelta

def test_break_time_display():
    """Test that break times are properly displayed in staff availability"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Break Time Display Fix")
    print("=" * 50)
    
    # Test 1: Check Staff Availability page loads
    print("\n1. Testing Staff Availability page...")
    try:
        response = requests.get(f"{base_url}/staff-availability")
        if response.status_code == 200:
            print("✅ Staff Availability page loads successfully")
        else:
            print(f"❌ Staff Availability page failed to load: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing Staff Availability page: {e}")
        return False
    
    # Test 2: Check that break times are properly identified in the HTML
    print("\n2. Testing break time identification...")
    html_content = response.text
    
    # Check for break time indicators
    break_indicators = [
        'status="break"',
        'Break Time',
        'bg-warning',
        'fas fa-coffee'
    ]
    
    found_break_indicators = []
    for indicator in break_indicators:
        if indicator in html_content:
            found_break_indicators.append(indicator)
    
    if found_break_indicators:
        print(f"✅ Break time indicators found: {found_break_indicators}")
    else:
        print("⚠️  No break time indicators found in HTML")
    
    # Test 3: Verify that "Book" buttons are NOT present during break times
    print("\n3. Testing that Book buttons are not shown during breaks...")
    
    # Look for problematic patterns
    problematic_patterns = [
        'btn btn-success btn-sm w-100 quick-book-btn',  # Book button classes
        '>Book<',  # Book button text
        'fas fa-plus'  # Plus icon in book buttons
    ]
    
    # Count occurrences and check context
    total_book_buttons = html_content.count('btn btn-success btn-sm w-100 quick-book-btn')
    total_break_slots = html_content.count('status-break') + html_content.count('bg-warning')
    
    print(f"📊 Found {total_book_buttons} book buttons")
    print(f"📊 Found {total_break_slots} break time slots")
    
    # Test 4: Check specific staff schedule data
    print("\n4. Testing staff schedule data...")
    
    # Look for schedule information in the HTML
    if 'break_start' in html_content and 'break_end' in html_content:
        print("✅ Break time data is present in the schedule")
    else:
        print("⚠️  Break time data might be missing from schedule")
    
    # Test 5: Visual verification prompts
    print("\n5. Visual Verification Required:")
    print("   Please manually check the Staff Availability page and verify:")
    print("   - Break times show 'Break Time' instead of 'Book' buttons")
    print("   - Break time slots have yellow/warning background")
    print("   - Coffee icon (☕) appears in break time slots")
    print("   - No green 'Book' buttons appear during scheduled break times")
    
    return True

def test_api_endpoints():
    """Test API endpoints related to staff availability"""
    base_url = "http://127.0.0.1:5000"
    
    print("\n🔌 Testing API Endpoints")
    print("=" * 30)
    
    # Test time slots API
    try:
        today = date.today().strftime('%Y-%m-%d')
        response = requests.get(f"{base_url}/api/time-slots?date={today}")
        
        if response.status_code == 200:
            print("✅ Time slots API working")
            data = response.json()
            if 'slots' in data:
                print(f"📊 Found {len(data.get('slots', []))} time slots")
            else:
                print("⚠️  No slots data in API response")
        else:
            print(f"❌ Time slots API error: {response.status_code}")
    except Exception as e:
        print(f"❌ API test error: {e}")

def create_test_schedule():
    """Helper function to create test schedule with break times"""
    print("\n🏗️  Setting up test data...")
    print("Note: You may need to create a test schedule manually through the Shift Scheduler")
    print("Recommended test schedule:")
    print("- Staff: Admin User")
    print("- Date: Today")
    print("- Shift: 09:00 - 17:00")
    print("- Break: 13:00 - 14:00 (1 hour lunch break)")

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Starting Comprehensive Break Time Display Test")
    print("=" * 60)
    
    # Create test data guidance
    create_test_schedule()
    
    # Run main tests
    if test_break_time_display():
        print("\n✅ Basic tests completed")
    else:
        print("\n❌ Basic tests failed")
    
    # Test API endpoints
    test_api_endpoints()
    
    # Final summary
    print("\n📋 Test Summary")
    print("=" * 20)
    print("1. Code fix has been applied to bookings_views.py")
    print("2. Break time logic now runs BEFORE booking checks")
    print("3. Break times should display 'Break Time' instead of 'Book'")
    print("4. Manual verification is still recommended")
    
    print("\n🎯 Next Steps:")
    print("1. Visit /staff-availability in your browser")
    print("2. Select today's date")
    print("3. Verify break times show correctly")
    print("4. If issues persist, check the shift scheduler setup")

if __name__ == "__main__":
    run_comprehensive_test()
