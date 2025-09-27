
#!/usr/bin/env python3
"""
Clear UnakiBooking table data and populate with fresh sample data
"""

from app import app, db
from models import UnakiBooking, User, Service, Customer
from datetime import datetime, date, time, timedelta

def clear_and_populate_unaki():
    """Clear existing UnakiBooking data and add fresh sample data"""
    
    with app.app_context():
        try:
            print("🧹 Clearing UnakiBooking table...")
            
            # Clear all existing UnakiBooking records
            existing_count = UnakiBooking.query.count()
            if existing_count > 0:
                UnakiBooking.query.delete()
                db.session.commit()
                print(f"✅ Cleared {existing_count} existing UnakiBooking records")
            else:
                print("📋 No existing records found in UnakiBooking table")
            
            # Get active staff members (ensure we have staff)
            staff_members = User.query.filter_by(is_active=True).all()
            if not staff_members:
                print("⚠️ No active staff members found. Creating sample staff...")
                # Create a sample staff member
                sample_staff = User(
                    username='sample_therapist',
                    first_name='Sarah',
                    last_name='Johnson',
                    email='sarah.johnson@spa.com',
                    role='staff',
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                sample_staff.set_password('demo123')
                db.session.add(sample_staff)
                db.session.commit()
                staff_members = [sample_staff]
            
            print(f"👥 Found {len(staff_members)} active staff members")
            
            # Sample services data
            sample_services = [
                {'name': 'Deep Cleansing Facial', 'duration': 60, 'price': 85.0},
                {'name': 'Relaxing Massage', 'duration': 90, 'price': 120.0},
                {'name': 'Anti-Aging Treatment', 'duration': 75, 'price': 110.0},
                {'name': 'Hot Stone Massage', 'duration': 90, 'price': 140.0},
                {'name': 'Eyebrow Threading', 'duration': 30, 'price': 35.0},
                {'name': 'Full Body Scrub', 'duration': 60, 'price': 95.0},
                {'name': 'Manicure & Pedicure', 'duration': 75, 'price': 65.0},
                {'name': 'Hair Cut & Style', 'duration': 60, 'price': 55.0},
                {'name': 'Aromatherapy Session', 'duration': 45, 'price': 70.0},
                {'name': 'Bridal Makeup', 'duration': 120, 'price': 200.0}
            ]
            
            # Sample customer names
            sample_customers = [
                {'name': 'Emma Watson', 'phone': '+1-555-2001'},
                {'name': 'Olivia Smith', 'phone': '+1-555-2002'},
                {'name': 'Sophia Johnson', 'phone': '+1-555-2003'},
                {'name': 'Isabella Davis', 'phone': '+1-555-2004'},
                {'name': 'Ava Wilson', 'phone': '+1-555-2005'},
                {'name': 'Mia Brown', 'phone': '+1-555-2006'},
                {'name': 'Charlotte Taylor', 'phone': '+1-555-2007'},
                {'name': 'Amelia Anderson', 'phone': '+1-555-2008'},
                {'name': 'Harper Thomas', 'phone': '+1-555-2009'},
                {'name': 'Luna Martinez', 'phone': '+1-555-2010'},
                {'name': 'Ella Garcia', 'phone': '+1-555-2011'},
                {'name': 'Grace Rodriguez', 'phone': '+1-555-2012'},
                {'name': 'Chloe Lopez', 'phone': '+1-555-2013'},
                {'name': 'Zoe Gonzalez', 'phone': '+1-555-2014'},
                {'name': 'Lily Perez', 'phone': '+1-555-2015'}
            ]
            
            # Create appointments for today and next few days
            today = date.today()
            created_count = 0
            
            # Import random for variety
            import random
            
            # Create appointments for the next 5 days
            for day_offset in range(5):
                appointment_date = today + timedelta(days=day_offset)
                
                # Create 8-12 appointments per day
                appointments_per_day = random.randint(8, 12)
                
                for i in range(appointments_per_day):
                    # Select random staff, service, and customer
                    staff = random.choice(staff_members)
                    service_data = random.choice(sample_services)
                    customer_data = random.choice(sample_customers)
                    
                    # Generate random start time between 9 AM and 6 PM
                    start_hour = random.randint(9, 17)
                    start_minute = random.choice([0, 15, 30, 45])
                    start_time_obj = time(start_hour, start_minute)
                    
                    # Calculate end time based on service duration
                    start_datetime = datetime.combine(appointment_date, start_time_obj)
                    end_datetime = start_datetime + timedelta(minutes=service_data['duration'])
                    end_time_obj = end_datetime.time()
                    
                    # Skip if end time goes past 8 PM
                    if end_time_obj > time(20, 0):
                        continue
                    
                    # Check for conflicts with existing appointments for this staff
                    conflict = False
                    existing_appointments = UnakiBooking.query.filter_by(
                        staff_id=staff.id,
                        appointment_date=appointment_date
                    ).all()
                    
                    for existing_apt in existing_appointments:
                        if not (end_time_obj <= existing_apt.start_time or start_time_obj >= existing_apt.end_time):
                            conflict = True
                            break
                    
                    if conflict:
                        continue  # Skip this appointment if there's a conflict
                    
                    # Create the booking
                    booking = UnakiBooking(
                        client_name=customer_data['name'],
                        client_phone=customer_data['phone'],
                        client_email=f"{customer_data['name'].lower().replace(' ', '.')}@email.com",
                        staff_id=staff.id,
                        staff_name=staff.full_name,
                        service_name=service_data['name'],
                        service_duration=service_data['duration'],
                        service_price=service_data['price'],
                        appointment_date=appointment_date,
                        start_time=start_time_obj,
                        end_time=end_time_obj,
                        status=random.choice(['scheduled', 'confirmed', 'completed']),
                        notes=f"Sample booking for {service_data['name']}",
                        booking_source='unaki_system',
                        booking_method='sample_data',
                        amount_charged=service_data['price'],
                        payment_status=random.choice(['pending', 'paid']),
                        created_at=datetime.utcnow()
                    )
                    
                    db.session.add(booking)
                    created_count += 1
            
            # Commit all bookings
            db.session.commit()
            
            print(f"\n🎉 Successfully created {created_count} fresh UnakiBooking records!")
            
            # Print summary by date
            print("\n📊 Summary by date:")
            for day_offset in range(5):
                check_date = today + timedelta(days=day_offset)
                day_count = UnakiBooking.query.filter_by(appointment_date=check_date).count()
                day_name = check_date.strftime('%A')
                print(f"   {day_name} ({check_date}): {day_count} appointments")
            
            # Print summary by staff
            print("\n👥 Summary by staff:")
            for staff in staff_members:
                staff_count = UnakiBooking.query.filter_by(staff_id=staff.id).count()
                print(f"   {staff.full_name}: {staff_count} appointments")
            
            print(f"\n✅ UnakiBooking table refreshed successfully!")
            print(f"📈 Total appointments in system: {UnakiBooking.query.count()}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error clearing and populating UnakiBooking data: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🔄 UNAKI BOOKING TABLE REFRESH")
    print("=" * 50)
    print("This will clear all existing UnakiBooking data and add fresh sample data")
    print()
    
    success = clear_and_populate_unaki()
    
    if success:
        print("\n🎉 UnakiBooking table refresh completed successfully!")
        print("💡 You can now view the fresh data in your Unaki Booking interface")
    else:
        print("\n💥 Refresh failed. Check the error messages above.")
