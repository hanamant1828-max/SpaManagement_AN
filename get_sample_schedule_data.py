
#!/usr/bin/env python3
"""
Get sample data from StaffScheduleRange and StaffDailySchedule tables
"""

import sys
sys.path.append('.')

from app import app, db
from models import StaffScheduleRange, StaffDailySchedule, User

def get_sample_schedule_data():
    """Get sample records from both schedule tables"""
    with app.app_context():
        try:
            print("=" * 80)
            print("STAFF SCHEDULE DATA SAMPLE")
            print("=" * 80)
            
            # Get staff members with schedules
            staff_with_schedules = db.session.query(User).join(
                StaffScheduleRange, User.id == StaffScheduleRange.staff_id
            ).filter(
                StaffScheduleRange.is_active == True,
                User.is_active == True
            ).distinct().all()
            
            for staff in staff_with_schedules:
                print(f"\n📋 STAFF: {staff.first_name} {staff.last_name} (ID: {staff.id})")
                print("─" * 60)
                
                # Get schedule ranges
                schedule_ranges = StaffScheduleRange.query.filter_by(
                    staff_id=staff.id,
                    is_active=True
                ).order_by(StaffScheduleRange.start_date).all()
                
                for schedule_range in schedule_ranges:
                    print(f"  📅 SCHEDULE RANGE: {schedule_range.schedule_name}")
                    print(f"     Date Range: {schedule_range.start_date} to {schedule_range.end_date}")
                    print(f"     General Times: {schedule_range.shift_start_time} - {schedule_range.shift_end_time}")
                    print(f"     General Break: {schedule_range.break_time}")
                    
                    # Get daily schedules for this range
                    daily_schedules = StaffDailySchedule.query.filter(
                        StaffDailySchedule.schedule_range_id == schedule_range.id,
                        StaffDailySchedule.is_active == True
                    ).order_by(StaffDailySchedule.schedule_date).limit(5).all()  # Show first 5 days
                    
                    if daily_schedules:
                        print("     📆 DETAILED DAILY SCHEDULES:")
                        for daily in daily_schedules:
                            status = "✅ Working" if daily.is_working else "❌ Off"
                            times = f"{daily.start_time} - {daily.end_time}" if daily.start_time and daily.end_time else "No times set"
                            break_info = daily.get_break_time_display()
                            
                            print(f"       {daily.schedule_date}: {status}")
                            if daily.is_working:
                                print(f"         Times: {times}")
                                print(f"         Break: {break_info}")
                                if daily.notes:
                                    print(f"         Notes: {daily.notes}")
                    else:
                        print("     (No detailed daily schedules found)")
                    print()
            
            # Summary statistics
            total_ranges = StaffScheduleRange.query.filter_by(is_active=True).count()
            total_daily = StaffDailySchedule.query.filter_by(is_active=True).count()
            
            print("=" * 80)
            print("SUMMARY STATISTICS")
            print("=" * 80)
            print(f"Total Active Staff: {len(staff_with_schedules)}")
            print(f"Total Schedule Ranges: {total_ranges}")
            print(f"Total Daily Schedule Entries: {total_daily}")
            
            return True
                
        except Exception as e:
            print(f"❌ Error fetching sample data: {e}")
            return False

def get_daily_schedule_for_date(staff_id, target_date):
    """Get detailed schedule for a specific staff member and date"""
    with app.app_context():
        try:
            from datetime import datetime
            if isinstance(target_date, str):
                target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            
            daily_schedule = StaffDailySchedule.query.filter(
                StaffDailySchedule.staff_id == staff_id,
                StaffDailySchedule.schedule_date == target_date,
                StaffDailySchedule.is_active == True
            ).first()
            
            if daily_schedule:
                staff = User.query.get(staff_id)
                print(f"\n📋 DAILY SCHEDULE FOR {staff.first_name} {staff.last_name} on {target_date}")
                print("─" * 60)
                print(f"Working: {'Yes' if daily_schedule.is_working else 'No'}")
                if daily_schedule.is_working:
                    print(f"Shift: {daily_schedule.start_time} - {daily_schedule.end_time}")
                    print(f"Break: {daily_schedule.get_break_time_display()}")
                    if daily_schedule.notes:
                        print(f"Notes: {daily_schedule.notes}")
                return daily_schedule
            else:
                print(f"❌ No daily schedule found for staff {staff_id} on {target_date}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching daily schedule: {e}")
            return None

if __name__ == "__main__":
    sample_data = get_sample_schedule_data()
    if sample_data:
        print("\n✅ Sample data retrieved successfully!")
        
        # Test specific date lookup
        print("\n" + "="*50)
        print("TESTING SPECIFIC DATE LOOKUP")
        print("="*50)
        from datetime import date
        today = date.today()
        get_daily_schedule_for_date(1, today)  # Test for staff ID 1, today's date
