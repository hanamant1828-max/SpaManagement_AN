
"""
Check existing staff schedules and break times
"""
import sqlite3
from datetime import date, datetime

def check_schedules():
    """Check current staff schedules in the database"""
    print("🗓️  Checking Staff Schedules and Break Times")
    print("=" * 50)
    
    try:
        # Connect to the database
        conn = sqlite3.connect('instance/spa_management.db')
        cursor = conn.cursor()
        
        # Check if staff schedule tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE '%schedule%'
        """)
        tables = cursor.fetchall()
        print(f"📋 Schedule-related tables: {[t[0] for t in tables]}")
        
        # Check staff schedule range data
        if any('staff_schedule_range' in str(t) for t in tables):
            cursor.execute("""
                SELECT ssr.id, ssr.staff_id, u.first_name, u.last_name,
                       ssr.schedule_name, ssr.start_date, ssr.end_date,
                       ssr.shift_start_time, ssr.shift_end_time, ssr.break_time,
                       ssr.monday, ssr.tuesday, ssr.wednesday, ssr.thursday, ssr.friday
                FROM staff_schedule_range ssr
                JOIN user u ON ssr.staff_id = u.id
                WHERE ssr.is_active = 1
                ORDER BY u.first_name, ssr.start_date
            """)
            
            schedules = cursor.fetchall()
            
            if schedules:
                print(f"\n📊 Found {len(schedules)} active schedules:")
                print("-" * 60)
                
                for schedule in schedules:
                    (id, staff_id, first_name, last_name, schedule_name, 
                     start_date, end_date, shift_start, shift_end, break_time,
                     mon, tue, wed, thu, fri) = schedule
                    
                    print(f"👤 {first_name} {last_name} (ID: {staff_id})")
                    print(f"   📅 Schedule: {schedule_name}")
                    print(f"   📅 Date Range: {start_date} to {end_date}")
                    print(f"   🕐 Shift: {shift_start} - {shift_end}")
                    print(f"   ☕ Break: {break_time if break_time else 'No break set'}")
                    
                    working_days = []
                    if mon: working_days.append('Mon')
                    if tue: working_days.append('Tue')
                    if wed: working_days.append('Wed')
                    if thu: working_days.append('Thu')
                    if fri: working_days.append('Fri')
                    
                    print(f"   📅 Working Days: {', '.join(working_days)}")
                    print("-" * 60)
                
                # Check for today's schedules
                today = date.today()
                today_str = today.strftime('%Y-%m-%d')
                day_of_week = today.weekday()  # Monday = 0
                
                print(f"\n📅 Today ({today_str}) is day {day_of_week} (Monday=0)")
                
                # Find schedules covering today
                day_columns = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                today_column = day_columns[day_of_week]
                
                cursor.execute(f"""
                    SELECT ssr.id, u.first_name, u.last_name, ssr.break_time
                    FROM staff_schedule_range ssr
                    JOIN user u ON ssr.staff_id = u.id
                    WHERE ssr.is_active = 1
                    AND ssr.start_date <= ?
                    AND ssr.end_date >= ?
                    AND ssr.{today_column} = 1
                """, (today_str, today_str))
                
                today_schedules = cursor.fetchall()
                
                if today_schedules:
                    print(f"\n🎯 Staff scheduled for today with break times:")
                    for schedule in today_schedules:
                        id, first_name, last_name, break_time = schedule
                        print(f"   👤 {first_name} {last_name}: {break_time if break_time else 'No break'}")
                else:
                    print(f"\n⚠️  No staff scheduled for today ({today_column})")
                    print("   This might be why you're not seeing break times!")
                    
            else:
                print("\n⚠️  No active schedules found")
                print("   You need to create schedules with break times first")
        else:
            print("\n❌ No staff_schedule_range table found")
            print("   The shift scheduler might not be set up yet")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking schedules: {e}")
    
    print("\n🎯 Recommendations:")
    print("1. If no schedules exist, create them via Shift Scheduler")
    print("2. Ensure break_time field has format like '60 minutes (13:00 - 14:00)'")
    print("3. Make sure staff are scheduled for today's day of week")
    print("4. Verify break times are within shift hours")

if __name__ == "__main__":
    check_schedules()
