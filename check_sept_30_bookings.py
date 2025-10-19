
#!/usr/bin/env python3
"""
Check for appointment bookings on September 30, 2025
"""

from app import app, db
from models import Appointment, UnakiBooking
from datetime import date, datetime

def check_september_30_bookings():
    """Check for bookings on September 30, 2025"""
    
    with app.app_context():
        target_date = date(2025, 9, 30)
        
        print("=" * 80)
        print(f"📅 CHECKING BOOKINGS FOR: {target_date.strftime('%A, September %d, %Y')}")
        print("=" * 80)
        
        # Check Appointment table
        print("\n🔍 Checking Appointment table...")
        appointments = Appointment.query.filter(
            db.func.date(Appointment.appointment_date) == target_date
        ).all()
        
        if appointments:
            print(f"✅ Found {len(appointments)} appointment(s) in Appointment table:\n")
            for apt in appointments:
                client_name = apt.client.full_name if apt.client else 'Unknown'
                service_name = apt.service.name if apt.service else 'Unknown'
                staff_name = apt.staff.full_name if apt.staff else 'Unknown'
                time_str = apt.appointment_date.strftime('%I:%M %p')
                
                print(f"  • ID: {apt.id}")
                print(f"    Client: {client_name}")
                print(f"    Service: {service_name}")
                print(f"    Staff: {staff_name}")
                print(f"    Time: {time_str}")
                print(f"    Status: {apt.status}")
                print(f"    Payment: {apt.payment_status or 'N/A'}")
                print(f"    Amount: ${apt.amount:.2f}" if apt.amount else "    Amount: N/A")
                print()
        else:
            print("❌ No appointments found in Appointment table")
        
        # Check UnakiBooking table
        print("\n🔍 Checking UnakiBooking table...")
        unaki_bookings = UnakiBooking.query.filter(
            UnakiBooking.appointment_date == target_date
        ).all()
        
        if unaki_bookings:
            print(f"✅ Found {len(unaki_bookings)} booking(s) in UnakiBooking table:\n")
            for booking in unaki_bookings:
                print(f"  • ID: {booking.id}")
                print(f"    Client: {booking.client_name}")
                print(f"    Phone: {booking.client_phone}")
                print(f"    Service: {booking.service_name}")
                print(f"    Staff: {booking.staff_name}")
                print(f"    Time: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}")
                print(f"    Status: {booking.status}")
                print(f"    Payment: {booking.payment_status}")
                print(f"    Amount: ₹{booking.amount_charged:.2f}" if booking.amount_charged else "    Amount: N/A")
                print(f"    Checked In: {'Yes' if booking.checked_in else 'No'}")
                print()
        else:
            print("❌ No bookings found in UnakiBooking table")
        
        # Summary
        total_bookings = len(appointments) + len(unaki_bookings)
        print("\n" + "=" * 80)
        print(f"📊 SUMMARY FOR SEPTEMBER 30, 2025:")
        print(f"  • Appointment table: {len(appointments)} booking(s)")
        print(f"  • UnakiBooking table: {len(unaki_bookings)} booking(s)")
        print(f"  • TOTAL: {total_bookings} booking(s)")
        print("=" * 80)

if __name__ == "__main__":
    check_september_30_bookings()
