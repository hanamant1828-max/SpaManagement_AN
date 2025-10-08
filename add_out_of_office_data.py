
#!/usr/bin/env python3
"""
Add out-of-office time data to some existing shifts
"""

from app import app, db
from models import ShiftLogs, ShiftManagement, User
from datetime import time
import random

def add_out_of_office_data():
    """Add out-of-office time data to some shifts"""
    with app.app_context():
        print("🔄 Adding out-of-office time data to shifts")
        print("=" * 60)
        
        # Out-of-office scenarios with variety
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
        
        # Get all shift logs
        all_shift_logs = ShiftLogs.query.all()
        
        if not all_shift_logs:
            print("⚠️ No shift logs found in database")
            return
        
        print(f"📋 Found {len(all_shift_logs)} shift logs")
        
        # Randomly assign out-of-office to about 30% of shifts
        logs_to_update = random.sample(all_shift_logs, min(len(all_shift_logs) // 3, len(all_shift_logs)))
        
        updated_count = 0
        for shift_log in logs_to_update:
            # Pick a random scenario
            scenario = random.choice(ooo_scenarios)
            
            # Validate times are within shift hours
            if shift_log.shift_start_time and shift_log.shift_end_time:
                if (scenario['start'] >= shift_log.shift_start_time and 
                    scenario['end'] <= shift_log.shift_end_time):
                    
                    shift_log.out_of_office_start = scenario['start']
                    shift_log.out_of_office_end = scenario['end']
                    shift_log.out_of_office_reason = scenario['reason']
                    
                    # Get staff info
                    shift_mgmt = ShiftManagement.query.get(shift_log.shift_management_id)
                    staff = User.query.get(shift_mgmt.staff_id) if shift_mgmt else None
                    staff_name = staff.full_name if staff else "Unknown"
                    
                    print(f"   ✅ {shift_log.individual_date} - {staff_name}")
                    print(f"      Out: {scenario['start'].strftime('%I:%M %p')} - {scenario['end'].strftime('%I:%M %p')}")
                    print(f"      Reason: {scenario['reason']}")
                    
                    updated_count += 1
        
        db.session.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully added out-of-office data to {updated_count} shifts!")
        
        # Show summary
        total_with_ooo = ShiftLogs.query.filter(
            ShiftLogs.out_of_office_start.isnot(None)
        ).count()
        
        print(f"\n📊 Summary:")
        print(f"   Total shifts with out-of-office: {total_with_ooo}")
        print(f"   Total shift logs: {len(all_shift_logs)}")
        print(f"   Coverage: {(total_with_ooo/len(all_shift_logs)*100):.1f}%")
        
        # Show some examples
        print(f"\n📋 Sample Out-of-Office Entries:")
        sample_logs = ShiftLogs.query.filter(
            ShiftLogs.out_of_office_start.isnot(None)
        ).limit(5).all()
        
        for log in sample_logs:
            shift_mgmt = ShiftManagement.query.get(log.shift_management_id)
            staff = User.query.get(shift_mgmt.staff_id) if shift_mgmt else None
            staff_name = staff.full_name if staff else "Unknown"
            
            print(f"   {log.individual_date} | {staff_name}")
            print(f"   {log.out_of_office_start.strftime('%I:%M %p')} - {log.out_of_office_end.strftime('%I:%M %p')}")
            print(f"   Reason: {log.out_of_office_reason}")
            print()

if __name__ == "__main__":
    add_out_of_office_data()
