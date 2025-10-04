#!/usr/bin/env python3
"""
Populate shift logs for all staff members for the week Oct 4-10, 2025
This will create shift management entries and daily shift logs for testing
"""

from app import app, db
from models import User, ShiftManagement, ShiftLogs
from datetime import datetime, date, time, timedelta

def populate_week_shift_data():
    """Create shift management and logs for all active staff for Oct 4-10, 2025"""

    with app.app_context():
        try:
            print("🚀 Starting shift logs population for week Oct 4-10, 2025...")

            # Get all active staff members
            staff_members = User.query.filter_by(is_active=True).all()
            print(f"Found {len(staff_members)} active staff members")

            # Define default shift times
            default_shift_start = time(9, 0)  # 9:00 AM
            default_shift_end = time(22, 0)   # 10:00 PM
            default_break_start = time(13, 0) # 1:00 PM
            default_break_end = time(14, 0)   # 2:00 PM

            # Date range for shifts (Oct 4-10, 2025)
            start_date = date(2025, 10, 4)  # Friday
            end_date = date(2025, 10, 10)   # Thursday

            total_logs_created = 0
            management_entries_created = 0
            staff_processed = 0

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

                # Delete existing logs for this week to avoid duplicates
                ShiftLogs.query.filter(
                    ShiftLogs.shift_management_id == shift_management.id,
                    ShiftLogs.individual_date >= start_date,
                    ShiftLogs.individual_date <= end_date
                ).delete()

                # Create daily shift logs for the week (all 7 days)
                current_date = start_date
                staff_logs_created = 0

                # Define out-of-office scenarios for variety
                import random
                
                ooo_scenarios = [
                    {'start': time(10, 0), 'end': time(11, 30), 'reason': 'Client visit at downtown location'},
                    {'start': time(14, 30), 'end': time(15, 30), 'reason': 'Bank work'},
                    {'start': time(11, 0), 'end': time(12, 0), 'reason': 'Supplier meeting'},
                    {'start': time(15, 0), 'end': time(16, 30), 'reason': 'Product delivery'},
                    {'start': time(9, 30), 'end': time(10, 30), 'reason': 'Field inspection'},
                    {'start': time(13, 30), 'end': time(14, 45), 'reason': 'Training session'},
                    {'start': time(10, 30), 'end': time(12, 0), 'reason': 'Off-site meeting'},
                    {'start': time(15, 30), 'end': time(16, 45), 'reason': 'Inventory audit'},
                ]

                day_index = 0
                while current_date <= end_date:
                    # Randomly assign out-of-office for some staff on some days
                    out_start = None
                    out_end = None
                    out_reason = None

                    # Random 30% chance for any staff to have out-of-office on any day
                    if random.random() < 0.3:
                        scenario = random.choice(ooo_scenarios)
                        out_start = scenario['start']
                        out_end = scenario['end']
                        out_reason = scenario['reason']

                    # Create logs for all days (including weekends for testing)
                    shift_log = ShiftLogs(
                        shift_management_id=shift_management.id,
                        individual_date=current_date,
                        shift_start_time=default_shift_start,
                        shift_end_time=default_shift_end,
                        break_start_time=default_break_start,
                        break_end_time=default_break_end,
                        out_of_office_start=out_start,
                        out_of_office_end=out_end,
                        out_of_office_reason=out_reason,
                        status='scheduled',
                        created_at=datetime.utcnow()
                    )
                    db.session.add(shift_log)
                    staff_logs_created += 1
                    total_logs_created += 1

                    current_date += timedelta(days=1)
                    day_index += 1

                print(f"  - Created {staff_logs_created} shift logs for {staff.full_name}")
                staff_processed += 1

            # Commit all changes
            db.session.commit()

            print(f"\n✅ Successfully populated shift logs!")
            print(f"📊 Summary:")
            print(f"   - Processed {staff_processed} staff members")
            print(f"   - Created/updated {management_entries_created} shift management entries")
            print(f"   - Created {total_logs_created} total shift logs")
            print(f"   - Date range: {start_date} to {end_date}")
            print(f"   - Days included: Friday Oct 4 to Thursday Oct 10, 2025")
            print(f"   - Shift time: 9:00 AM to 10:00 PM")
            print(f"   - Break time: 1:00 PM to 2:00 PM")

            # Show breakdown by day
            print(f"\n📅 Breakdown by day:")
            current_date = start_date
            while current_date <= end_date:
                day_name = current_date.strftime('%A')
                day_logs = ShiftLogs.query.filter_by(individual_date=current_date).count()
                print(f"   - {day_name}, {current_date}: {day_logs} staff scheduled")
                current_date += timedelta(days=1)

            return True

        except Exception as e:
            print(f"❌ Error populating shift logs: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = populate_week_shift_data()
    if success:
        print("\n🎉 Week shift logs population completed successfully!")
    else:
        print("\n💥 Week shift logs population failed!")