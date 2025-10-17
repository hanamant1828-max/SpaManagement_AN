#!/usr/bin/env python3
"""
Add shifts for all staff members for October 2025
Creates shift management entries and daily shift logs for all active staff
"""

from app import app, db
from models import User, ShiftManagement, ShiftLogs
from datetime import datetime, date, time, timedelta

def add_october_shifts():
    """Create shift management and logs for all active staff for October 2025"""
    
    with app.app_context():
        try:
            print("🚀 Starting October 2025 shift creation...")
            
            # Get all active staff members
            staff_members = User.query.filter_by(is_active=True).all()
            print(f"Found {len(staff_members)} active staff members")
            
            # Define default shift times
            default_shift_start = time(9, 0)  # 9:00 AM
            default_shift_end = time(18, 0)   # 6:00 PM
            default_break_start = time(13, 0) # 1:00 PM
            default_break_end = time(14, 0)   # 2:00 PM
            
            # October 2025 date range
            start_date = date(2025, 10, 1)   # October 1, 2025
            end_date = date(2025, 10, 31)     # October 31, 2025
            
            total_logs_created = 0
            management_entries_created = 0
            management_entries_updated = 0
            
            for staff in staff_members:
                print(f"\n📋 Processing staff: {staff.full_name} (ID: {staff.id})")
                
                # Check if shift management already exists
                existing_management = ShiftManagement.query.filter_by(staff_id=staff.id).first()
                
                if existing_management:
                    print(f"  ✏️  Shift management exists, extending date range...")
                    # Update date range to include October 2025
                    if existing_management.from_date > start_date:
                        existing_management.from_date = start_date
                    if existing_management.to_date < end_date:
                        existing_management.to_date = end_date
                    existing_management.updated_at = datetime.utcnow()
                    shift_management = existing_management
                    management_entries_updated += 1
                else:
                    print(f"  ➕ Creating new shift management...")
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
                
                # Create daily shift logs for October 2025
                current_date = start_date
                staff_logs_created = 0
                
                while current_date <= end_date:
                    # Check if log already exists for this date
                    existing_log = ShiftLogs.query.filter_by(
                        shift_management_id=shift_management.id,
                        individual_date=current_date
                    ).first()
                    
                    if not existing_log:
                        # Create log for all days (Monday to Sunday)
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
                
                print(f"  ✅ Created {staff_logs_created} new shift logs for {staff.full_name}")
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n✅ Successfully created October 2025 shifts!")
            print(f"\n📊 Summary:")
            print(f"   - Processed {len(staff_members)} staff members")
            print(f"   - Created {management_entries_created} new shift management entries")
            print(f"   - Updated {management_entries_updated} existing shift management entries")
            print(f"   - Created {total_logs_created} total new shift logs")
            print(f"   - Date range: October 1, 2025 to October 31, 2025")
            print(f"   - Working all days (Monday to Sunday)")
            print(f"   - Shift time: 9:00 AM to 6:00 PM")
            print(f"   - Break time: 1:00 PM to 2:00 PM")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating October shifts: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = add_october_shifts()
    if success:
        print("\n🎉 October 2025 shift creation completed successfully!")
    else:
        print("\n💥 October 2025 shift creation failed!")
