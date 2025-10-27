
#!/usr/bin/env python3
"""
Add shift schedules for all active staff members
Creates a 30-day schedule with standard working hours
"""

from app import app, db
from models import User, ShiftManagement, ShiftLogs
from datetime import datetime, date, time, timedelta

def add_shifts_for_all_staff():
    """Add shift schedules for all active staff members"""
    with app.app_context():
        # Get all active users including admin and staff
        staff_members = User.query.filter_by(is_active=True).all()
        
        if not staff_members:
            print("❌ No active users found.")
            return
        
        print(f"📋 Found {len(staff_members)} active users (including admin and staff)")
        print("=" * 80)
        
        # Define shift schedule parameters
        start_date = date.today()
        end_date = start_date + timedelta(days=30)  # 30 days of shifts
        
        shifts_created = 0
        logs_created = 0
        
        for staff in staff_members:
            print(f"\n👤 Processing: {staff.first_name} {staff.last_name} (ID: {staff.id})")
            
            # Check if shift management already exists
            existing_mgmt = ShiftManagement.query.filter_by(staff_id=staff.id).first()
            
            if existing_mgmt:
                print(f"   ⚠️  Shift management already exists (ID: {existing_mgmt.id})")
                print(f"   📅 Current range: {existing_mgmt.from_date} to {existing_mgmt.to_date}")
                
                # Ask if we should extend or skip
                response = input(f"   ❓ Extend schedule to {end_date}? (y/n): ").lower()
                if response == 'y':
                    # Extend the date range
                    existing_mgmt.from_date = min(existing_mgmt.from_date, start_date)
                    existing_mgmt.to_date = max(existing_mgmt.to_date, end_date)
                    existing_mgmt.updated_at = datetime.utcnow()
                    shift_mgmt = existing_mgmt
                    print(f"   ✅ Extended schedule to {shift_mgmt.to_date}")
                else:
                    print(f"   ⏭️  Skipping {staff.first_name} {staff.last_name}")
                    continue
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
            
            # Create shift logs for weekdays (Monday to Friday)
            current_date = start_date
            staff_logs = 0
            
            while current_date <= end_date:
                # Skip weekends (5=Saturday, 6=Sunday)
                if current_date.weekday() < 5:
                    # Check if log already exists for this date
                    existing_log = ShiftLogs.query.filter_by(
                        shift_management_id=shift_mgmt.id,
                        individual_date=current_date
                    ).first()
                    
                    if not existing_log:
                        # Standard 9 AM to 6 PM shift with 1 hour lunch break
                        shift_log = ShiftLogs(
                            shift_management_id=shift_mgmt.id,
                            individual_date=current_date,
                            shift_start_time=time(9, 0),    # 9:00 AM
                            shift_end_time=time(18, 0),     # 6:00 PM
                            break_start_time=time(13, 0),   # 1:00 PM
                            break_end_time=time(14, 0),     # 2:00 PM
                            status='scheduled'
                        )
                        db.session.add(shift_log)
                        logs_created += 1
                        staff_logs += 1
                
                current_date += timedelta(days=1)
            
            print(f"   📅 Created {staff_logs} shift logs (weekdays only)")
            print(f"   ⏰ Shift hours: 9:00 AM - 6:00 PM (1 hour lunch break)")
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ Successfully created:")
        print(f"   - {shifts_created} new shift management entries")
        print(f"   - {logs_created} shift log entries")
        print(f"\n📊 Shift data has been added to the database!")
        print("=" * 80)

if __name__ == '__main__':
    add_shifts_for_all_staff()
