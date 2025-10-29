
#!/usr/bin/env python3
"""
Add shifts from 9 AM to 9 PM for all active staff members
Creates shifts for the next 30 days with standard working hours
"""

from app import app, db
from models import User, ShiftManagement, ShiftLogs
from datetime import datetime, date, time, timedelta

def add_shifts_for_all_staff():
    """Add shift schedules for all active staff members (9 AM to 9 PM)"""
    with app.app_context():
        # Get all active users (staff members)
        staff_members = User.query.filter_by(is_active=True).all()
        
        if not staff_members:
            print("❌ No active users found.")
            return
        
        print(f"📋 Found {len(staff_members)} active users")
        print("=" * 80)
        
        # Define shift schedule parameters
        start_date = date.today()
        end_date = start_date + timedelta(days=30)  # 30 days of shifts
        
        # Shift times: 9 AM to 9 PM
        shift_start = time(9, 0)   # 9:00 AM
        shift_end = time(21, 0)    # 9:00 PM (21:00)
        break_start = time(13, 0)  # 1:00 PM lunch break
        break_end = time(14, 0)    # 2:00 PM
        
        shifts_created = 0
        shifts_updated = 0
        logs_created = 0
        
        for staff in staff_members:
            print(f"\n👤 Processing: {staff.first_name} {staff.last_name} (ID: {staff.id})")
            
            # Check if shift management already exists
            existing_mgmt = ShiftManagement.query.filter_by(staff_id=staff.id).first()
            
            if existing_mgmt:
                print(f"   ⚠️  Shift management already exists (ID: {existing_mgmt.id})")
                print(f"   📅 Current range: {existing_mgmt.from_date} to {existing_mgmt.to_date}")
                
                # Extend the date range and update
                existing_mgmt.from_date = min(existing_mgmt.from_date, start_date)
                existing_mgmt.to_date = max(existing_mgmt.to_date, end_date)
                existing_mgmt.updated_at = datetime.utcnow()
                
                # Delete old shift logs for this management entry
                ShiftLogs.query.filter_by(shift_management_id=existing_mgmt.id).delete()
                
                shift_mgmt = existing_mgmt
                shifts_updated += 1
                print(f"   ✅ Updated schedule to {shift_mgmt.to_date}")
            else:
                # Create new shift management
                shift_mgmt = ShiftManagement(
                    staff_id=staff.id,
                    from_date=start_date,
                    to_date=end_date
                )
                db.session.add(shift_mgmt)
                db.session.flush()
                shifts_created += 1
                print(f"   ✅ Created shift management (ID: {shift_mgmt.id})")
            
            # Create shift logs for all days in the range
            current_date = start_date
            staff_logs = 0
            
            while current_date <= end_date:
                # Create shift log for every day (including weekends)
                shift_log = ShiftLogs(
                    shift_management_id=shift_mgmt.id,
                    individual_date=current_date,
                    shift_start_time=shift_start,     # 9:00 AM
                    shift_end_time=shift_end,         # 9:00 PM
                    break_start_time=break_start,     # 1:00 PM
                    break_end_time=break_end,         # 2:00 PM
                    status='scheduled'
                )
                db.session.add(shift_log)
                logs_created += 1
                staff_logs += 1
                
                current_date += timedelta(days=1)
            
            print(f"   📅 Created {staff_logs} shift logs (all days)")
            print(f"   ⏰ Shift hours: 9:00 AM - 9:00 PM (1 hour lunch break: 1:00 PM - 2:00 PM)")
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ Successfully completed:")
        print(f"   - Created {shifts_created} new shift management entries")
        print(f"   - Updated {shifts_updated} existing shift management entries")
        print(f"   - Created {logs_created} shift log entries")
        print(f"\n📊 All staff members now have shifts from 9:00 AM to 9:00 PM!")
        print(f"📅 Date range: {start_date} to {end_date}")
        print("=" * 80)

if __name__ == '__main__':
    add_shifts_for_all_staff()
