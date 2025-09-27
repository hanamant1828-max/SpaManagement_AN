
#!/usr/bin/env python3
"""
Fix overlapping appointments in the Unaki booking system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import UnakiBooking
from datetime import datetime, timedelta
from sqlalchemy import and_

def find_overlapping_appointments():
    """Find all overlapping appointments"""
    with app.app_context():
        overlaps = []
        
        # Get all active appointments
        appointments = UnakiBooking.query.filter_by(status='scheduled').order_by(
            UnakiBooking.staff_id, 
            UnakiBooking.appointment_date,
            UnakiBooking.start_time
        ).all()
        
        print(f"🔍 Checking {len(appointments)} appointments for overlaps...")
        
        for i, apt1 in enumerate(appointments):
            for j, apt2 in enumerate(appointments[i+1:], i+1):
                # Only check appointments for the same staff on the same date
                if (apt1.staff_id == apt2.staff_id and 
                    apt1.appointment_date == apt2.appointment_date):
                    
                    # Create datetime objects for comparison
                    start1 = datetime.combine(apt1.appointment_date, apt1.start_time)
                    end1 = datetime.combine(apt1.appointment_date, apt1.end_time)
                    start2 = datetime.combine(apt2.appointment_date, apt2.start_time)
                    end2 = datetime.combine(apt2.appointment_date, apt2.end_time)
                    
                    # Check for overlap
                    if start1 < end2 and start2 < end1:
                        overlaps.append({
                            'apt1': apt1,
                            'apt2': apt2,
                            'staff_id': apt1.staff_id,
                            'date': apt1.appointment_date,
                            'conflict': f"{apt1.client_name} ({apt1.start_time}-{apt1.end_time}) overlaps with {apt2.client_name} ({apt2.start_time}-{apt2.end_time})"
                        })
        
        return overlaps

def fix_overlapping_appointments():
    """Fix overlapping appointments by adjusting times or canceling duplicates"""
    with app.app_context():
        overlaps = find_overlapping_appointments()
        
        if not overlaps:
            print("✅ No overlapping appointments found!")
            return
        
        print(f"⚠️  Found {len(overlaps)} overlapping appointment conflicts:")
        
        for i, overlap in enumerate(overlaps, 1):
            print(f"\n{i}. Staff ID {overlap['staff_id']} on {overlap['date']}:")
            print(f"   {overlap['conflict']}")
            
            apt1 = overlap['apt1']
            apt2 = overlap['apt2']
            
            # Strategy: Keep the earlier appointment, move or cancel the later one
            if apt1.start_time <= apt2.start_time:
                keep_apt = apt1
                adjust_apt = apt2
            else:
                keep_apt = apt2
                adjust_apt = apt1
            
            print(f"   📌 Keeping: {keep_apt.client_name} ({keep_apt.start_time}-{keep_apt.end_time})")
            
            # Try to move the conflicting appointment to next available slot
            end_time_of_kept = datetime.combine(keep_apt.appointment_date, keep_apt.end_time)
            new_start_time = end_time_of_kept.time()
            
            # Calculate new end time based on service duration
            new_start_datetime = datetime.combine(adjust_apt.appointment_date, new_start_time)
            new_end_datetime = new_start_datetime + timedelta(minutes=adjust_apt.service_duration)
            new_end_time = new_end_datetime.time()
            
            # Check if the new time slot is available (within working hours 8 AM - 8 PM)
            if new_start_time >= datetime.strptime("08:00", "%H:%M").time() and new_end_time <= datetime.strptime("20:00", "%H:%M").time():
                print(f"   🔄 Moving: {adjust_apt.client_name} to {new_start_time}-{new_end_time}")
                adjust_apt.start_time = new_start_time
                adjust_apt.end_time = new_end_time
            else:
                print(f"   ❌ Canceling: {adjust_apt.client_name} (no available slot)")
                adjust_apt.status = 'cancelled'
                adjust_apt.notes = f"Cancelled due to scheduling conflict. Original time: {adjust_apt.start_time}-{adjust_apt.end_time}"
        
        # Save all changes
        try:
            db.session.commit()
            print(f"\n✅ Successfully resolved {len(overlaps)} appointment conflicts!")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error saving changes: {e}")

def main():
    print("🩺 Unaki Booking System - Overlap Fix Tool")
    print("=" * 50)
    
    # First, show current overlaps
    print("\n1. Scanning for overlapping appointments...")
    overlaps = find_overlapping_appointments()
    
    if not overlaps:
        print("✅ No overlapping appointments found!")
        return
    
    print(f"\n⚠️  Found {len(overlaps)} overlapping conflicts")
    
    # Ask user if they want to fix them
    response = input("\nDo you want to automatically fix these conflicts? (y/n): ").lower().strip()
    
    if response == 'y':
        print("\n2. Fixing overlapping appointments...")
        fix_overlapping_appointments()
    else:
        print("\n👋 Overlap fix cancelled. Run the script again when ready.")

if __name__ == "__main__":
    main()
