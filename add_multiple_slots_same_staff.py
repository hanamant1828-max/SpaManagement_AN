
#!/usr/bin/env python3
"""
Add Multiple Random Time Slots for Same Staff Member
This script creates several appointments for the same staff member at different random times.
"""

import os
import sys
import random
from datetime import datetime, date, time, timedelta

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import UnakiBooking, User

def add_multiple_slots_same_staff():
    """Add multiple random appointments for the same staff member"""
    
    with app.app_context():
        try:
            print("🚀 Adding multiple random time slots for same staff member...")
            
            # Get an active staff member (let's use Emily Davis - ID 3 from your previous booking)
            target_staff = User.query.filter_by(id=3, is_active=True).first()
            if not target_staff:
                # Try to get any active staff member
                target_staff = User.query.filter_by(is_active=True).first()
                
            if not target_staff:
                print("❌ No active staff members found!")
                return False
            
            print(f"👤 Selected Staff: {target_staff.full_name} (ID: {target_staff.id})")
            
            # Clear existing bookings for today for this staff to avoid conflicts
            today = date.today()
            existing_bookings = UnakiBooking.query.filter_by(
                staff_id=target_staff.id,
                appointment_date=today
            ).all()
            
            print(f"🧹 Clearing {len(existing_bookings)} existing bookings for {target_staff.full_name} on {today}")
            for booking in existing_bookings:
                db.session.delete(booking)
            db.session.commit()
            
            # Sample services with different durations
            sample_services = [
                {'name': 'Quick Eyebrow Touch-up', 'duration': 15, 'price': 25.0},
                {'name': 'Express Facial', 'duration': 30, 'price': 60.0},
                {'name': 'Hair Wash & Blow Dry', 'duration': 45, 'price': 40.0},
                {'name': 'Deep Cleansing Facial', 'duration': 60, 'price': 100.0},
                {'name': 'Relaxing Massage', 'duration': 60, 'price': 120.0},
                {'name': 'Hair Cut & Style', 'duration': 75, 'price': 80.0},
                {'name': 'Full Body Massage', 'duration': 90, 'price': 150.0},
                {'name': 'Deluxe Spa Package', 'duration': 120, 'price': 200.0}
            ]
            
            # Sample clients
            sample_clients = [
                {'name': 'Priya Sharma', 'phone': '+91-9876543210', 'email': 'priya.sharma@example.com'},
                {'name': 'Anita Desai', 'phone': '+91-9876543211', 'email': 'anita.desai@example.com'},
                {'name': 'Kavya Patel', 'phone': '+91-9876543212', 'email': 'kavya.patel@example.com'},
                {'name': 'Meera Gupta', 'phone': '+91-9876543213', 'email': 'meera.gupta@example.com'},
                {'name': 'Sita Rani', 'phone': '+91-9876543214', 'email': 'sita.rani@example.com'},
                {'name': 'Lakshmi Iyer', 'phone': '+91-9876543215', 'email': 'lakshmi.iyer@example.com'},
                {'name': 'Radha Krishna', 'phone': '+91-9876543216', 'email': 'radha.krishna@example.com'},
                {'name': 'Geetha Nair', 'phone': '+91-9876543217', 'email': 'geetha.nair@example.com'}
            ]
            
            # Generate random time slots throughout the day
            working_hours = [
                (8, 0),   # 8:00 AM
                (9, 0),   # 9:00 AM  
                (9, 30),  # 9:30 AM
                (10, 15), # 10:15 AM
                (11, 0),  # 11:00 AM
                (11, 45), # 11:45 AM
                (13, 0),  # 1:00 PM
                (13, 30), # 1:30 PM
                (14, 15), # 2:15 PM
                (15, 0),  # 3:00 PM
                (15, 30), # 3:30 PM
                (16, 0),  # 4:00 PM
            ]
            
            created_bookings = []
            
            # Create 6-8 appointments at random times
            num_appointments = random.randint(6, 8)
            selected_times = random.sample(working_hours, min(num_appointments, len(working_hours)))
            
            for i, (hour, minute) in enumerate(selected_times):
                service = random.choice(sample_services)
                client = random.choice(sample_clients)
                
                # Create start time
                start_time_obj = time(hour, minute)
                
                # Calculate end time
                start_datetime = datetime.combine(today, start_time_obj)
                end_datetime = start_datetime + timedelta(minutes=service['duration'])
                
                # Create booking
                booking = UnakiBooking(
                    client_name=client['name'],
                    client_phone=client['phone'],
                    client_email=client['email'],
                    staff_id=target_staff.id,
                    staff_name=target_staff.full_name,
                    service_name=service['name'],
                    service_duration=service['duration'],
                    service_price=service['price'],
                    appointment_date=today,
                    start_time=start_time_obj,
                    end_time=end_datetime.time(),
                    status=random.choice(['scheduled', 'confirmed']),
                    notes=f'Random appointment #{i+1} for testing multiple slots',
                    booking_source='unaki_system',
                    booking_method='random_generator',
                    amount_charged=service['price'],
                    payment_status=random.choice(['pending', 'paid']),
                    created_at=datetime.utcnow()
                )
                
                db.session.add(booking)
                created_bookings.append({
                    'time': start_time_obj.strftime('%H:%M'),
                    'end_time': end_datetime.time().strftime('%H:%M'),
                    'client': client['name'],
                    'service': service['name'],
                    'duration': service['duration'],
                    'price': service['price']
                })
                
                print(f"   ✅ {i+1}. {start_time_obj.strftime('%H:%M')}-{end_datetime.time().strftime('%H:%M')}: {client['name']} - {service['name']} ({service['duration']}min)")
            
            # Commit all bookings
            db.session.commit()
            
            print(f"\n🎉 Successfully created {len(created_bookings)} appointments for {target_staff.full_name}!")
            print(f"📅 All appointments scheduled for: {today}")
            
            # Display summary
            print(f"\n📊 APPOINTMENT SUMMARY FOR {target_staff.full_name.upper()}:")
            print("=" * 60)
            total_duration = 0
            total_revenue = 0
            
            for booking in sorted(created_bookings, key=lambda x: x['time']):
                total_duration += booking['duration']
                total_revenue += booking['price']
                print(f"🕐 {booking['time']}-{booking['end_time']} | {booking['client']:<20} | {booking['service']:<25} | ₹{booking['price']}")
            
            print("=" * 60)
            print(f"📈 Total Appointments: {len(created_bookings)}")
            print(f"⏱️  Total Service Time: {total_duration} minutes ({total_duration//60}h {total_duration%60}m)")
            print(f"💰 Total Revenue: ₹{total_revenue}")
            print(f"📍 Staff Utilization: {(total_duration/480)*100:.1f}% (assuming 8-hour workday)")
            
            print(f"\n🌐 Visit the Unaki Booking page to see these appointments visualized:")
            print(f"   → http://localhost:5000/unaki-booking")
            print(f"   → Make sure to select today's date: {today}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating multiple appointments: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🎯 Multiple Random Appointments Generator")
    print("This script will create several appointments for the same staff member at random times.")
    print()
    
    success = add_multiple_slots_same_staff()
    
    if success:
        print("\n✅ Script completed successfully!")
        print("💡 Now check the Unaki Booking interface to see all the appointments!")
    else:
        print("\n❌ Script failed. Check the error messages above.")
