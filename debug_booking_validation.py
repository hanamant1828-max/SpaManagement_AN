
from app import app, db
from models import UnakiBooking, User
from modules.bookings.booking_services import validate_booking_for_acceptance
from datetime import datetime

with app.app_context():
    print("\n🔍 BOOKING VALIDATION DIAGNOSTICS")
    print("=" * 60)
    
    # Get all scheduled/pending bookings
    pending_bookings = UnakiBooking.query.filter(
        UnakiBooking.status.in_(['scheduled', 'pending'])
    ).all()
    
    print(f"\n📋 Found {len(pending_bookings)} pending/scheduled bookings\n")
    
    if not pending_bookings:
        print("✅ No pending bookings to validate")
    else:
        for booking in pending_bookings:
            print(f"\n{'='*60}")
            print(f"🎫 Booking #{booking.id}")
            print(f"   👤 Client: {booking.client_name}")
            print(f"   💼 Service: {booking.service_name}")
            print(f"   📅 Date: {booking.appointment_date}")
            print(f"   ⏰ Time: {booking.start_time.strftime('%H:%M')} - {booking.end_time.strftime('%H:%M')}")
            print(f"   🏷️  Status: {booking.status}")
            print(f"   👨‍💼 Staff Assigned: {booking.staff_name or 'Not assigned'}")
            
            # Try validation with different staff members
            staff_members = User.query.filter_by(is_active=True).all()
            print(f"\n   🔍 Testing validation with {len(staff_members)} staff members:")
            
            any_valid = False
            for staff in staff_members:
                validation_errors = validate_booking_for_acceptance(booking, staff.id)
                
                if not validation_errors:
                    print(f"   ✅ VALID with {staff.first_name} {staff.last_name} (ID: {staff.id})")
                    any_valid = True
                else:
                    print(f"   ❌ INVALID with {staff.first_name} {staff.last_name} (ID: {staff.id}):")
                    for error in validation_errors:
                        print(f"      • {error['category']}: {error['message']}")
            
            if not any_valid:
                print(f"\n   ⚠️  WARNING: This booking cannot be accepted with ANY staff member!")
    
    print("\n" + "="*60)
    print("✅ Diagnostics complete")
