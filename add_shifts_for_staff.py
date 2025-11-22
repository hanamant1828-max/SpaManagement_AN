from app import app, db
from models import User, ShiftManagement, ShiftLogs
from datetime import datetime, date, time, timedelta

def add_shifts_for_all_staff():
    with app.app_context():
        staff_members = User.query.filter_by(role='staff').all()
        
        if not staff_members:
            print("❌ No staff members found!")
            return
        
        print(f"Found {len(staff_members)} staff members")
        print("Adding shifts for all staff members...\n")
        
        from_date = date.today()
        to_date = from_date + timedelta(days=30)
        
        shift_start_time = time(9, 0)
        shift_end_time = time(18, 0)
        break_start_time = time(13, 0)
        break_end_time = time(14, 0)
        
        shifts_added = 0
        logs_added = 0
        
        for staff in staff_members:
            existing_shift = ShiftManagement.query.filter_by(staff_id=staff.id).first()
            
            if existing_shift:
                print(f"⚠️ Shift management already exists for {staff.first_name} {staff.last_name}")
                db.session.delete(existing_shift)
                db.session.commit()
                print(f"   Deleted old shift management, creating new one...")
            
            shift_management = ShiftManagement(
                staff_id=staff.id,
                from_date=from_date,
                to_date=to_date
            )
            db.session.add(shift_management)
            db.session.flush()
            
            current_date = from_date
            staff_logs_count = 0
            
            while current_date <= to_date:
                if current_date.weekday() < 6:
                    shift_log = ShiftLogs(
                        shift_management_id=shift_management.id,
                        individual_date=current_date,
                        shift_start_time=shift_start_time,
                        shift_end_time=shift_end_time,
                        break_start_time=break_start_time,
                        break_end_time=break_end_time,
                        status='scheduled'
                    )
                    db.session.add(shift_log)
                    staff_logs_count += 1
                    logs_added += 1
                
                current_date += timedelta(days=1)
            
            shifts_added += 1
            print(f"✅ Added shift for {staff.first_name} {staff.last_name}")
            print(f"   - Shift period: {from_date} to {to_date}")
            print(f"   - Daily hours: {shift_start_time.strftime('%I:%M %p')} to {shift_end_time.strftime('%I:%M %p')}")
            print(f"   - Break time: {break_start_time.strftime('%I:%M %p')} to {break_end_time.strftime('%I:%M %p')}")
            print(f"   - Total shift days: {staff_logs_count}\n")
        
        db.session.commit()
        
        print(f"\n🎉 Successfully added shifts for {shifts_added} staff members!")
        print(f"📊 Total shift log entries created: {logs_added}")
        print(f"\n📅 Shift Schedule:")
        print(f"   Period: {from_date} to {to_date}")
        print(f"   Working hours: 9:00 AM to 6:00 PM")
        print(f"   Break time: 1:00 PM to 2:00 PM (1 hour)")
        print(f"   Working days: Monday to Saturday")
        print(f"   Weekly off: Sunday")

if __name__ == "__main__":
    add_shifts_for_all_staff()
