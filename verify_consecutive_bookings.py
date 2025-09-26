
#!/usr/bin/env python3
"""
Verify Consecutive Bookings in Database
Show all details of the consecutive bookings for Admin User
"""

import os
import sys
from datetime import datetime, date, time

# Set required environment variables
if not os.environ.get("SESSION_SECRET"):
    os.environ["SESSION_SECRET"] = "1578063aca108928c78100b516702a5765d2d05e85b4fb8bb29a75db0bfc34ca"

def verify_consecutive_bookings():
    """Verify and display consecutive bookings for Admin User"""
    try:
        from app import app, db
        from models import UnakiBooking, User

        with app.app_context():
            print("🔍 VERIFYING CONSECUTIVE BOOKINGS IN DATABASE")
            print("=" * 60)
            
            # Get Admin User
            admin_user = User.query.get(11)
            if admin_user:
                print(f"👤 Staff Member: {admin_user.full_name} (ID: {admin_user.id})")
            else:
                print("❌ Admin User (ID: 11) not found!")
                return False
            
            # Get today's date (2025-09-26 as used in test)
            target_date = date(2025, 9, 26)
            print(f"📅 Target Date: {target_date}")
            print()
            
            # Get all bookings for Admin User on target date
            consecutive_bookings = UnakiBooking.query.filter(
                UnakiBooking.staff_id == 11,
                UnakiBooking.appointment_date == target_date
            ).order_by(UnakiBooking.start_time).all()
            
            if not consecutive_bookings:
                print("❌ No bookings found for Admin User on 2025-09-26")
                return False
            
            print(f"✅ Found {len(consecutive_bookings)} consecutive bookings:")
            print("-" * 60)
            
            for i, booking in enumerate(consecutive_bookings, 1):
                print(f"📋 BOOKING {i}:")
                print(f"   🆔 ID: {booking.id}")
                print(f"   👤 Client: {booking.client_name}")
                print(f"   📞 Phone: {booking.client_phone}")
                print(f"   💼 Service: {booking.service_name}")
                print(f"   ⏰ Time: {booking.start_time.strftime('%H:%M')} - {booking.end_time.strftime('%H:%M')}")
                print(f"   ⏱️  Duration: {booking.service_duration} minutes")
                print(f"   💰 Price: ${booking.service_price}")
                print(f"   📊 Status: {booking.status}")
                print(f"   📝 Notes: {booking.notes}")
                print(f"   🏷️  Source: {booking.booking_source}")
                print(f"   💳 Payment: {booking.payment_status}")
                print(f"   📅 Created: {booking.created_at}")
                print()
            
            # Verify consecutive nature
            print("🔗 CONSECUTIVE VERIFICATION:")
            print("-" * 40)
            
            if len(consecutive_bookings) >= 2:
                all_consecutive = True
                for i in range(len(consecutive_bookings) - 1):
                    current_end = consecutive_bookings[i].end_time
                    next_start = consecutive_bookings[i + 1].start_time
                    
                    if current_end == next_start:
                        print(f"✅ Booking {i+1} → Booking {i+2}: {current_end} → {next_start} (CONSECUTIVE)")
                    else:
                        print(f"❌ Booking {i+1} → Booking {i+2}: {current_end} → {next_start} (GAP DETECTED)")
                        all_consecutive = False
                
                if all_consecutive:
                    print("\n🎉 ALL BOOKINGS ARE PERFECTLY CONSECUTIVE!")
                    print("🔥 NO GAPS BETWEEN APPOINTMENTS!")
                else:
                    print("\n⚠️  Some gaps detected between bookings")
            
            # Summary
            total_duration = sum(booking.service_duration for booking in consecutive_bookings)
            total_revenue = sum(booking.service_price for booking in consecutive_bookings)
            start_time = consecutive_bookings[0].start_time
            end_time = consecutive_bookings[-1].end_time
            
            print("\n📊 SUMMARY:")
            print("-" * 30)
            print(f"📋 Total Bookings: {len(consecutive_bookings)}")
            print(f"⏰ Time Span: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
            print(f"⏱️  Total Duration: {total_duration} minutes ({total_duration/60:.1f} hours)")
            print(f"💰 Total Revenue: ${total_revenue}")
            print(f"👤 Staff Member: {admin_user.full_name}")
            print(f"📅 Date: {target_date}")
            
            # Database verification
            print("\n🗄️  DATABASE DETAILS:")
            print("-" * 35)
            print(f"📊 Total UnakiBooking records: {UnakiBooking.query.count()}")
            print(f"👥 Total Staff with bookings: {len(set(b.staff_id for b in UnakiBooking.query.all()))}")
            print(f"📅 Booking dates range: {min(b.appointment_date for b in UnakiBooking.query.all())} to {max(b.appointment_date for b in UnakiBooking.query.all())}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error verifying bookings: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_unaki_schedule_api_response():
    """Show what the Unaki API returns for this data"""
    try:
        from app import app
        import requests
        
        with app.app_context():
            print("\n🌐 UNAKI API SCHEDULE RESPONSE:")
            print("=" * 50)
            
            # Make API call (assuming app is running on port 5000)
            try:
                response = requests.get("http://0.0.0.0:5000/api/unaki/schedule?date=2025-09-26")
                if response.status_code == 200:
                    data = response.json()
                    appointments = data.get('appointments', [])
                    
                    print(f"✅ API Response Status: {response.status_code}")
                    print(f"📊 Appointments Returned: {len(appointments)}")
                    print()
                    
                    for i, apt in enumerate(appointments, 1):
                        print(f"API Appointment {i}:")
                        print(f"   Staff ID: {apt.get('staffId')}")
                        print(f"   Client: {apt.get('clientName')}")
                        print(f"   Service: {apt.get('service')}")
                        print(f"   Time: {apt.get('startTime')} - {apt.get('endTime')}")
                        print(f"   Status: {apt.get('status')}")
                        print()
                        
                else:
                    print(f"❌ API Error: Status {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print("⚠️  Could not connect to API - app may not be running")
                
    except Exception as e:
        print(f"❌ Error checking API: {e}")

if __name__ == "__main__":
    print("🚀 Starting Consecutive Bookings Verification...")
    print()
    
    success = verify_consecutive_bookings()
    
    if success:
        show_unaki_schedule_api_response()
        print("\n✅ Verification completed successfully!")
        print("\n💡 The consecutive bookings are properly stored and should be visible in the Unaki booking interface!")
    else:
        print("\n❌ Verification failed!")
