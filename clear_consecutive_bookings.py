
#!/usr/bin/env python3
"""
Clear existing consecutive bookings and recreate them
"""

import os
from datetime import datetime, date

# Set required environment variables
if not os.environ.get("SESSION_SECRET"):
    os.environ["SESSION_SECRET"] = "1578063aca108928c78100b516702a5765d2d05e85b4fb8bb29a75db0bfc34ca"

def clear_and_recreate_consecutive_bookings():
    """Clear existing bookings and recreate consecutive ones"""
    try:
        from app import app, db
        from models import UnakiBooking

        with app.app_context():
            print("🧹 Clearing existing consecutive bookings...")
            
            # Target date for consecutive bookings
            target_date = date(2025, 9, 26)
            
            # Delete existing UnakiBooking records for Admin User (ID: 11) on this date
            existing_bookings = UnakiBooking.query.filter(
                UnakiBooking.staff_id == 11,
                UnakiBooking.appointment_date == target_date
            ).all()
            
            print(f"🔍 Found {len(existing_bookings)} existing bookings for Admin User on {target_date}")
            
            for booking in existing_bookings:
                print(f"   ❌ Deleting: {booking.client_name} - {booking.service_name} at {booking.start_time}")
                db.session.delete(booking)
            
            db.session.commit()
            print(f"✅ Cleared {len(existing_bookings)} existing bookings")
            
            # Now create the consecutive bookings
            print("\n🚀 Creating fresh consecutive bookings...")
            
            consecutive_bookings_data = [
                {
                    'client_name': 'Sarah Johnson',
                    'client_phone': '+1-555-0301',
                    'service_name': 'Express Facial',
                    'start_time': '09:00',
                    'end_time': '09:30',
                    'duration': 30,
                    'price': 45.0,
                    'notes': 'First consecutive booking - 30 minutes'
                },
                {
                    'client_name': 'Michael Chen',
                    'client_phone': '+1-555-0302', 
                    'service_name': 'Swedish Massage',
                    'start_time': '09:30',
                    'end_time': '10:30',
                    'duration': 60,
                    'price': 75.0,
                    'notes': 'Second consecutive booking - 1 hour right after first'
                },
                {
                    'client_name': 'Emma Rodriguez',
                    'client_phone': '+1-555-0303',
                    'service_name': 'Deep Tissue Massage',
                    'start_time': '10:30',
                    'end_time': '11:30',
                    'duration': 60,
                    'price': 100.0,
                    'notes': 'Third consecutive booking - 1 hour after completion of first booking'
                }
            ]
            
            created_bookings = []
            
            for i, booking_data in enumerate(consecutive_bookings_data, 1):
                print(f"\n📋 Creating Booking {i}: {booking_data['start_time']}-{booking_data['end_time']} - {booking_data['client_name']}")
                
                # Parse times
                start_time_obj = datetime.strptime(booking_data['start_time'], '%H:%M').time()
                end_time_obj = datetime.strptime(booking_data['end_time'], '%H:%M').time()
                
                # Create UnakiBooking entry
                unaki_booking = UnakiBooking(
                    client_name=booking_data['client_name'],
                    client_phone=booking_data['client_phone'],
                    client_email=f"{booking_data['client_name'].lower().replace(' ', '.')}@example.com",
                    staff_id=11,  # Admin User
                    staff_name='Admin User',
                    service_name=booking_data['service_name'],
                    service_duration=booking_data['duration'],
                    service_price=booking_data['price'],
                    appointment_date=target_date,
                    start_time=start_time_obj,
                    end_time=end_time_obj,
                    status='confirmed',
                    notes=booking_data['notes'],
                    booking_source='unaki_system',
                    booking_method='consecutive_test',
                    amount_charged=booking_data['price'],
                    payment_status='pending',
                    created_at=datetime.utcnow()
                )
                
                db.session.add(unaki_booking)
                db.session.flush()  # Get the ID
                
                created_bookings.append(unaki_booking.id)
                print(f"   ✅ Created Booking ID: {unaki_booking.id}")
            
            db.session.commit()
            
            print(f"\n🎉 SUCCESS! Created {len(created_bookings)} consecutive bookings")
            print(f"📋 Booking IDs: {created_bookings}")
            
            # Verify consecutive nature
            print("\n🔗 CONSECUTIVE VERIFICATION:")
            print("-" * 40)
            
            for i, booking_data in enumerate(consecutive_bookings_data):
                if i < len(consecutive_bookings_data) - 1:
                    current_end = booking_data['end_time']
                    next_start = consecutive_bookings_data[i + 1]['start_time']
                    
                    if current_end == next_start:
                        print(f"✅ Booking {i+1} → Booking {i+2}: {current_end} → {next_start} (CONSECUTIVE)")
                    else:
                        print(f"❌ Booking {i+1} → Booking {i+2}: {current_end} → {next_start} (GAP DETECTED)")
            
            print("\n🔥 PERFECT CONSECUTIVE SEQUENCE CREATED!")
            print("📊 Summary:")
            print("   👤 Staff: Admin User (ID: 11)")
            print("   🕘 9:00-9:30 (30 min) - Sarah Johnson - Express Facial")
            print("   🕘 9:30-10:30 (1 hour) - Michael Chen - Swedish Massage") 
            print("   🕘 10:30-11:30 (1 hour) - Emma Rodriguez - Deep Tissue Massage")
            print(f"   📅 Date: {target_date}")
            print("   ✨ NO GAPS between appointments!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = clear_and_recreate_consecutive_bookings()
    if success:
        print("\n🎊 Consecutive bookings setup completed successfully!")
        print("\n🌐 You can now view them in the Unaki Booking interface!")
    else:
        print("\n💥 Setup failed!")
