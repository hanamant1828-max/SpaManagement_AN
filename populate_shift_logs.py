
#!/usr/bin/env python3
"""
Populate shift logs for existing staff members
This will create shift management entries and daily shift logs for all active staff
"""

from app import app, db
from models import User, ShiftManagement, ShiftLogs
from datetime import datetime, date, time, timedelta

def populate_shift_logs():
    """Create shift management and logs for all active staff members"""
    
    with app.app_context():
        try:
            print("🚀 Starting shift logs population...")
            
            # Get all active staff members
            staff_members = User.query.filter_by(is_active=True).all()
            print(f"Found {len(staff_members)} active staff members")
            
            # Define default shift times
            default_shift_start = time(9, 0)  # 9:00 AM
            default_shift_end = time(17, 0)   # 5:00 PM
            default_break_start = time(13, 0) # 1:00 PM
            default_break_end = time(14, 0)   # 2:00 PM
            
            # Date range for shifts (past 30 days to next 30 days)
            today = date.today()
            start_date = today - timedelta(days=30)
            end_date = today + timedelta(days=30)
            
            total_logs_created = 0
            management_entries_created = 0
            
            for staff in staff_members:
                print(f"\nProcessing staff: {staff.full_name} (ID: {staff.id})")
                
                # Check if shift management already exists
                existing_management = ShiftManagement.query.filter_by(staff_id=staff.id).first()
                
                if existing_management:
                    print(f"  - Shift management exists, updating date range...")
                    # Update date range to include our new range
                    if existing_management.from_date > start_date:
                        existing_management.from_date = start_date
                    if existing_management.to_date < end_date:
                        existing_management.to_date = end_date
                    existing_management.updated_at = datetime.utcnow()
                    shift_management = existing_management
                else:
                    print(f"  - Creating new shift management...")
                    # Create new shift management
                    shift_management = ShiftManagement(
                        staff_id=staff.id,
                        from_date=start_date,
                        to_date=end_date,
                        created_at=datetime.utcnow()
                    )
                    db.session.add(shift_management)
                    db.session.flush()  # Get the ID
                    management_entries_created += 1
                
                # Clear existing shift logs for this staff to avoid duplicates
                existing_logs = ShiftLogs.query.filter_by(shift_management_id=shift_management.id).all()
                for log in existing_logs:
                    db.session.delete(log)
                
                # Create daily shift logs for weekdays (Monday to Friday)
                current_date = start_date
                staff_logs_created = 0
                
                while current_date <= end_date:
                    # Only create logs for weekdays (0=Monday, 6=Sunday)
                    if current_date.weekday() < 5:  # Monday to Friday
                        shift_log = ShiftLogs(
                            shift_management_id=shift_management.id,
                            individual_date=current_date,
                            shift_start_time=default_shift_start,
                            shift_end_time=default_shift_end,
                            break_start_time=default_break_start,
                            break_end_time=default_break_end,
                            status='scheduled',
                            created_at=datetime.utcnow()
                        )
                        db.session.add(shift_log)
                        staff_logs_created += 1
                        total_logs_created += 1
                    
                    current_date += timedelta(days=1)
                
                print(f"  - Created {staff_logs_created} shift logs for {staff.full_name}")
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n✅ Successfully populated shift logs!")
            print(f"📊 Summary:")
            print(f"   - Processed {len(staff_members)} staff members")
            print(f"   - Created/updated {management_entries_created} shift management entries")
            print(f"   - Created {total_logs_created} total shift logs")
            print(f"   - Date range: {start_date} to {end_date}")
            print(f"   - Working days: Monday to Friday")
            print(f"   - Shift time: 9:00 AM to 5:00 PM")
            print(f"   - Break time: 1:00 PM to 2:00 PM")
            
            return True
            
        except Exception as e:
            print(f"❌ Error populating shift logs: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = populate_shift_logs()
    if success:
        print("\n🎉 Shift logs population completed successfully!")
    else:
        print("\n💥 Shift logs population failed!")
