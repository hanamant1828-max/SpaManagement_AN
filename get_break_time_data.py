
#!/usr/bin/env python3
"""
Script to retrieve and display break time data from the database
"""
import sqlite3
from datetime import date, datetime
import json

def get_break_time_data():
    """Retrieve break time data from the StaffScheduleRange table"""
    print("📅 Retrieving Break Time Data from Database")
    print("=" * 60)
    
    try:
        # Connect to the database
        conn = sqlite3.connect('instance/spa_management.db')
        cursor = conn.cursor()
        
        # Query to get all break time data with staff information
        query = """
        SELECT 
            ssr.id as schedule_id,
            u.id as staff_id,
            u.first_name,
            u.last_name,
            ssr.schedule_name,
            ssr.start_date,
            ssr.end_date,
            ssr.shift_start_time,
            ssr.shift_end_time,
            ssr.break_time,
            ssr.monday,
            ssr.tuesday,
            ssr.wednesday,
            ssr.thursday,
            ssr.friday,
            ssr.saturday,
            ssr.sunday,
            ssr.is_active,
            ssr.priority,
            ssr.created_at
        FROM staff_schedule_range ssr
        JOIN user u ON ssr.staff_id = u.id
        WHERE ssr.is_active = 1
        ORDER BY u.first_name, u.last_name, ssr.start_date
        """
        
        cursor.execute(query)
        schedules = cursor.fetchall()
        
        if schedules:
            print(f"🎯 Found {len(schedules)} active schedules with break time data:\n")
            
            current_staff = None
            for schedule in schedules:
                (schedule_id, staff_id, first_name, last_name, schedule_name, 
                 start_date, end_date, shift_start, shift_end, break_time,
                 monday, tuesday, wednesday, thursday, friday, saturday, sunday,
                 is_active, priority, created_at) = schedule
                
                # Group by staff member
                staff_name = f"{first_name} {last_name}"
                if current_staff != staff_name:
                    if current_staff is not None:
                        print("-" * 40)
                    print(f"👤 Staff: {staff_name} (ID: {staff_id})")
                    current_staff = staff_name
                
                # Working days
                working_days = []
                if monday: working_days.append('Mon')
                if tuesday: working_days.append('Tue')
                if wednesday: working_days.append('Wed')
                if thursday: working_days.append('Thu')
                if friday: working_days.append('Fri')
                if saturday: working_days.append('Sat')
                if sunday: working_days.append('Sun')
                
                print(f"  📋 Schedule: {schedule_name}")
                print(f"  📅 Date Range: {start_date} to {end_date}")
                print(f"  🕐 Shift Hours: {shift_start} - {shift_end}")
                print(f"  ☕ Break Time: {break_time if break_time else 'No break scheduled'}")
                print(f"  📆 Working Days: {', '.join(working_days) if working_days else 'None'}")
                print(f"  ⭐ Priority: {priority}")
                print(f"  📝 Created: {created_at}")
                print()
            
        else:
            print("⚠️  No active schedules found in the database")
            print("   You may need to create staff schedules first")
        
        # Additional analysis - Break time patterns
        print("\n" + "=" * 60)
        print("📊 Break Time Analysis")
        print("=" * 60)
        
        # Count schedules with break times
        cursor.execute("""
            SELECT COUNT(*) as total_schedules,
                   COUNT(CASE WHEN break_time IS NOT NULL AND break_time != '' THEN 1 END) as schedules_with_breaks
            FROM staff_schedule_range ssr
            WHERE ssr.is_active = 1
        """)
        
        stats = cursor.fetchone()
        total_schedules, schedules_with_breaks = stats
        
        print(f"📈 Total Active Schedules: {total_schedules}")
        print(f"☕ Schedules with Break Times: {schedules_with_breaks}")
        print(f"📊 Break Time Coverage: {(schedules_with_breaks/total_schedules*100):.1f}%" if total_schedules > 0 else "No data")
        
        # Today's schedules with break times
        today = date.today()
        day_of_week = today.weekday()  # Monday = 0, Sunday = 6
        day_columns = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        today_column = day_columns[day_of_week]
        
        today_query = f"""
        SELECT u.first_name, u.last_name, ssr.break_time, ssr.shift_start_time, ssr.shift_end_time
        FROM staff_schedule_range ssr
        JOIN user u ON ssr.staff_id = u.id
        WHERE ssr.is_active = 1
        AND ssr.start_date <= ?
        AND ssr.end_date >= ?
        AND ssr.{today_column} = 1
        AND ssr.break_time IS NOT NULL
        AND ssr.break_time != ''
        """
        
        today_str = today.strftime('%Y-%m-%d')
        cursor.execute(today_query, (today_str, today_str))
        today_breaks = cursor.fetchall()
        
        print(f"\n🗓️  Staff with Break Times Today ({today.strftime('%A, %B %d, %Y')}):")
        if today_breaks:
            for staff_break in today_breaks:
                first_name, last_name, break_time, shift_start, shift_end = staff_break
                print(f"  👤 {first_name} {last_name}")
                print(f"     🕐 Shift: {shift_start} - {shift_end}")
                print(f"     ☕ Break: {break_time}")
                
                # Try to parse break time for specific hours
                import re
                patterns = [
                    r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})',  # HH:MM - HH:MM
                    r'\((\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\)',  # (HH:MM - HH:MM)
                ]
                
                break_parsed = False
                for pattern in patterns:
                    match = re.search(pattern, break_time)
                    if match:
                        break_start = match.group(1)
                        break_end = match.group(2)
                        print(f"     ⏰ Parsed Break Hours: {break_start} to {break_end}")
                        break_parsed = True
                        break
                
                if not break_parsed:
                    print(f"     ⚠️  Break time format not recognized for parsing")
                print()
        else:
            print("  ⚠️  No staff have break times scheduled for today")
        
        conn.close()
        
        print("\n✅ Break time data retrieval completed!")
        
    except Exception as e:
        print(f"❌ Error retrieving break time data: {e}")
        return False
    
    return True

def get_break_time_json():
    """Get break time data in JSON format"""
    try:
        conn = sqlite3.connect('instance/spa_management.db')
        cursor = conn.cursor()
        
        query = """
        SELECT 
            ssr.id,
            u.id as staff_id,
            u.first_name || ' ' || u.last_name as staff_name,
            ssr.schedule_name,
            ssr.start_date,
            ssr.end_date,
            ssr.shift_start_time,
            ssr.shift_end_time,
            ssr.break_time,
            ssr.monday, ssr.tuesday, ssr.wednesday, ssr.thursday, 
            ssr.friday, ssr.saturday, ssr.sunday
        FROM staff_schedule_range ssr
        JOIN user u ON ssr.staff_id = u.id
        WHERE ssr.is_active = 1 AND ssr.break_time IS NOT NULL AND ssr.break_time != ''
        ORDER BY u.first_name, ssr.start_date
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        columns = ['id', 'staff_id', 'staff_name', 'schedule_name', 'start_date', 'end_date', 
                  'shift_start_time', 'shift_end_time', 'break_time',
                  'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        schedules = []
        for row in results:
            schedule_dict = dict(zip(columns, row))
            schedules.append(schedule_dict)
        
        conn.close()
        
        print("\n📄 Break Time Data (JSON Format):")
        print("=" * 40)
        print(json.dumps(schedules, indent=2, default=str))
        
        return schedules
        
    except Exception as e:
        print(f"❌ Error getting JSON data: {e}")
        return []

if __name__ == "__main__":
    print("🔍 Starting Break Time Data Retrieval...")
    print()
    
    # Get detailed break time data
    success = get_break_time_data()
    
    if success:
        # Also get JSON format
        json_data = get_break_time_json()
        
        print(f"\n📊 Summary: Retrieved break time data for analysis")
        print("💡 This data shows how break times are stored and can be used")
        print("   for the Staff Availability booking system integration.")
    
    print("\n🎯 Use this data to:")
    print("   - Verify break times are properly stored")
    print("   - Check break time formatting")
    print("   - Ensure booking system integration works correctly")
