
#!/usr/bin/env python3
"""
Add shift schedules for all active staff members for December 2025
Creates shifts from December 1-31, 2025 with standard working hours
"""

from app import app, db
from models import User, ShiftManagement, ShiftLogs
from datetime import datetime, date, time, timedelta

def add_december_shifts():
    """Add shift schedules for all active staff for December 2025"""
    with app.app_context():
        # Get all active staff members
        staff_members = User.query.filter_by(is_active=True).all()
        
        if not staff_members:
            print("❌ No active users found.")
            return
        
        print(f"📋 Found {len(staff_members)} active users")
        print("=" * 80)
        
        # Define shift schedule parameters for December 2025
        start_date = date(2025, 12, 1)   # December 1, 2025
        end_date = date(2025, 12, 31)    # December 31, 2025
        
        # Shift times: 9 AM to 10 PM
        shift_start = time(9, 0)   # 9:00 AM
        shift_end = time(22, 0)    # 10:00 PM
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
                print(f"   ⚠️  Shift management exists (ID: {existing_mgmt.id})")
                print(f"   📅 Current range: {existing_mgmt.from_date} to {existing_mgmt.to_date}")
                
                # Extend the date range if needed
                if existing_mgmt.from_date > start_date:
                    existing_mgmt.from_date = start_date
                if existing_mgmt.to_date < end_date:
                    existing_mgmt.to_date = end_date
                existing_mgmt.updated_at = datetime.utcnow()
                shift_mgmt = existing_mgmt
                shifts_updated += 1
                print(f"   ✅ Extended schedule to include December 2025")
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
                print(f"   ✅ Created new shift management (ID: {shift_mgmt.id})")
            
            # Create shift logs for all days in December (including weekends)
            current_date = start_date
            staff_logs = 0
            
            while current_date <= end_date:
                # Check if log already exists for this date
                existing_log = ShiftLogs.query.filter_by(
                    shift_management_id=shift_mgmt.id,
                    individual_date=current_date
                ).first()
                
                if not existing_log:
                    # Create shift log for this day
                    shift_log = ShiftLogs(
                        shift_management_id=shift_mgmt.id,
                        individual_date=current_date,
                        shift_start_time=shift_start,
                        shift_end_time=shift_end,
                        break_start_time=break_start,
                        break_end_time=break_end,
                        status='scheduled',
                        created_at=datetime.utcnow()
                    )
                    db.session.add(shift_log)
                    logs_created += 1
                    staff_logs += 1
                
                current_date += timedelta(days=1)
            
            print(f"   📅 Created {staff_logs} shift logs for December")
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ December 2025 Shift Schedule Complete!")
        print(f"   - New shift management entries: {shifts_created}")
        print(f"   - Updated shift management entries: {shifts_updated}")
        print(f"   - Total shift logs created: {logs_created}")
        print(f"\n📊 Schedule Details:")
        print(f"   Period: December 1-31, 2025 (31 days)")
        print(f"   Shift hours: 9:00 AM - 10:00 PM")
        print(f"   Break time: 1:00 PM - 2:00 PM (60 minutes)")
        print(f"   Working days: All days (including weekends)")
        print("=" * 80)

if __name__ == '__main__':
    add_december_shifts()
