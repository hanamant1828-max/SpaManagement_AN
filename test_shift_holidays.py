#!/usr/bin/env python3
"""
Test script to add sample shift data with holidays and off-days
"""
import sys
from datetime import datetime, date, time, timedelta

# Setup Flask app context
from app import app, db
from models import ShiftManagement, ShiftLogs, User

def add_test_shift_data():
    """Add sample shift data with various statuses including holidays"""
    with app.app_context():
        print("🔍 Adding test shift data with holidays and off-days...")
        
        # Get first 5 staff members (users with is_staff=True or all users)
        staff_members = User.query.filter_by(is_active=True).limit(5).all()
        
        if not staff_members:
            print("❌ No staff members found. Please create staff members first.")
            return
        
        print(f"Found {len(staff_members)} staff members")
        
        # Get today's date and upcoming dates
        today = date.today()
        tomorrow = today + timedelta(days=1)
        day_after = today + timedelta(days=2)
        
        # Create shift management entries for next 7 days
        from_date = today
        to_date = today + timedelta(days=6)
        
        for i, staff in enumerate(staff_members):
            print(f"\n👤 Creating shifts for {staff.first_name} {staff.last_name}")
            
            # Check if shift management already exists (staff_id is unique)
            existing = ShiftManagement.query.filter_by(staff_id=staff.id).first()
            
            if not existing:
                shift_mgmt = ShiftManagement(
                    staff_id=staff.id,
                    from_date=from_date,
                    to_date=to_date
                )
                db.session.add(shift_mgmt)
                db.session.flush()
                print(f"  ✅ Created ShiftManagement (ID: {shift_mgmt.id})")
            else:
                # Update dates if needed
                existing.from_date = from_date
                existing.to_date = to_date
                shift_mgmt = existing
                print(f"  ℹ️ Using existing ShiftManagement (ID: {shift_mgmt.id})")
            
            # Create shift logs with different statuses for testing
            # For holidays/off-days, we use dummy times (00:00-00:00) as the status determines behavior
            test_dates = [
                (today, 'scheduled', time(9, 0), time(17, 0), time(12, 0), time(13, 0)),
                (tomorrow, 'holiday', time(0, 0), time(0, 0), None, None),  # Holiday
                (day_after, 'absent', time(0, 0), time(0, 0), None, None),   # Off day
                (today + timedelta(days=3), 'scheduled', time(10, 0), time(18, 0), time(13, 0), time(14, 0)),
                (today + timedelta(days=4), 'scheduled', time(9, 0), time(17, 0), None, None),
                (today + timedelta(days=5), 'leave', time(0, 0), time(0, 0), None, None),  # Off day (leave)
            ]
            
            for test_date, status, shift_start, shift_end, break_start, break_end in test_dates:
                # Delete existing shift log for this date
                existing_log = ShiftLogs.query.filter(
                    ShiftLogs.shift_management_id == shift_mgmt.id,
                    ShiftLogs.individual_date == test_date
                ).first()
                
                if existing_log:
                    db.session.delete(existing_log)
                    print(f"  🗑️ Deleted existing log for {test_date}")
                
                # Create new shift log
                shift_log = ShiftLogs(
                    shift_management_id=shift_mgmt.id,
                    individual_date=test_date,
                    shift_start_time=shift_start,
                    shift_end_time=shift_end,
                    break_start_time=break_start,
                    break_end_time=break_end,
                    out_of_office_start=None,
                    out_of_office_end=None,
                    out_of_office_reason=None,
                    status=status
                )
                db.session.add(shift_log)
                
                status_emoji = '🏖️' if status == 'holiday' else '📅' if status in ['absent', 'leave'] else '✅'
                print(f"  {status_emoji} Added {status} shift log for {test_date}")
        
        # Commit all changes
        db.session.commit()
        print("\n✅ All test shift data added successfully!")
        print(f"\n📌 Test dates:")
        print(f"  - Today ({today}): Scheduled shifts")
        print(f"  - Tomorrow ({tomorrow}): HOLIDAYS for all staff")
        print(f"  - Day after ({day_after}): OFF DAYS (absent) for all staff")
        print(f"  - {today + timedelta(days=3)}: Scheduled shifts")
        print(f"  - {today + timedelta(days=4)}: Scheduled shifts (no breaks)")
        print(f"  - {today + timedelta(days=5)}: OFF DAYS (leave) for all staff")

if __name__ == '__main__':
    try:
        add_test_shift_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
