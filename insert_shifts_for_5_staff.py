
#!/usr/bin/env python3
"""
Insert shift data for 5 staff members from October 8-16, 2025
"""

from app import app, db
from models import User, ShiftManagement, ShiftLogs
from datetime import date, time, datetime
import pytz

def insert_shifts_for_staff():
    """Insert shift management and logs for 5 staff members"""
    with app.app_context():
        print("🔄 Inserting shifts for 5 staff members (Oct 8-16, 2025)")
        print("=" * 60)
        
        # Get 5 active staff members
        staff_members = User.query.filter_by(is_active=True).limit(5).all()
        
        if len(staff_members) < 5:
            print(f"⚠️ Only found {len(staff_members)} staff members")
            print("Adding sample staff first...")
            # You can add staff creation logic here if needed
            return
        
        # Date range
        from_date = date(2025, 10, 8)
        to_date = date(2025, 10, 16)
        
        # Shift times
        shift_start = time(9, 0)  # 9:00 AM
        shift_end = time(21, 0)   # 9:00 PM
        break_start = time(13, 0)  # 1:00 PM
        break_end = time(14, 0)    # 2:00 PM
        
        # Working days (Monday to Friday = 0,1,2,3,4)
        working_days = [0, 1, 2, 3, 4]  # Mon-Fri
        
        for staff in staff_members[:5]:
            print(f"\n👤 Processing: {staff.full_name} (ID: {staff.id})")
            
            # Check if shift management already exists
            existing_shift = ShiftManagement.query.filter_by(staff_id=staff.id).first()
            
            if existing_shift:
                print(f"   ⚠️ Shift management already exists for {staff.full_name}")
                # Delete existing to recreate
                ShiftLogs.query.filter_by(shift_management_id=existing_shift.id).delete()
                db.session.delete(existing_shift)
                db.session.commit()
                print(f"   🗑️ Deleted existing shift data")
            
            # Create shift management entry
            shift_mgmt = ShiftManagement(
                staff_id=staff.id,
                from_date=from_date,
                to_date=to_date,
                created_at=datetime.now(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None),
                updated_at=datetime.now(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None)
            )
            
            db.session.add(shift_mgmt)
            db.session.flush()  # Get the ID
            
            # Create shift logs for each day
            current_date = from_date
            logs_created = 0
            
            while current_date <= to_date:
                # Only create logs for working days (Mon-Fri)
                if current_date.weekday() in working_days:
                    shift_log = ShiftLogs(
                        shift_management_id=shift_mgmt.id,
                        individual_date=current_date,
                        shift_start_time=shift_start,
                        shift_end_time=shift_end,
                        break_start_time=break_start,
                        break_end_time=break_end,
                        status='scheduled',
                        created_at=datetime.now(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None)
                    )
                    db.session.add(shift_log)
                    logs_created += 1
                
                # Move to next day
                from datetime import timedelta
                current_date = current_date + timedelta(days=1)
            
            db.session.commit()
            
            print(f"   ✅ Created shift management (ID: {shift_mgmt.id})")
            print(f"   ✅ Created {logs_created} shift logs (Mon-Fri only)")
            print(f"   📅 Date range: {from_date} to {to_date}")
            print(f"   ⏰ Shift: {shift_start.strftime('%I:%M %p')} - {shift_end.strftime('%I:%M %p')}")
            print(f"   ☕ Break: {break_start.strftime('%I:%M %p')} - {break_end.strftime('%I:%M %p')}")
        
        print("\n" + "=" * 60)
        print("✅ Shift insertion completed successfully!")
        
        # Summary
        total_shift_mgmt = ShiftManagement.query.count()
        total_shift_logs = ShiftLogs.query.count()
        
        print(f"\n📊 Database Summary:")
        print(f"   Total Shift Management entries: {total_shift_mgmt}")
        print(f"   Total Shift Logs: {total_shift_logs}")
        
        # Show sample data
        print(f"\n📋 Sample Shift Logs:")
        sample_logs = ShiftLogs.query.limit(3).all()
        for log in sample_logs:
            print(f"   {log.individual_date} | {log.shift_start_time.strftime('%I:%M %p')} - {log.shift_end_time.strftime('%I:%M %p')} | Status: {log.status}")

if __name__ == "__main__":
    insert_shifts_for_staff()
