
#!/usr/bin/env python3
"""
Create UnakiBooking table and populate with sample data
"""

from app import app, db
from models import UnakiBooking, User
from datetime import datetime, date, time, timedelta

def create_unaki_booking_table():
    """Create UnakiBooking table and populate with sample data"""
    
    with app.app_context():
        try:
            print("🚀 Creating UnakiBooking table...")
            
            # Create the table
            db.create_all()
            print("✅ UnakiBooking table created successfully!")
            
            # Check if sample data already exists
            existing_bookings = UnakiBooking.query.count()
            if existing_bookings > 0:
                print(f"📊 Found {existing_bookings} existing bookings in UnakiBooking table")
                return True
            
            # Get active staff members
            staff_members = User.query.filter_by(is_active=True).limit(5).all()
            if not staff_members:
                print("⚠️ No active staff members found. Cannot create sample bookings.")
                return False
            
            print(f"👥 Found {len(staff_members)} active staff members")
            
            # Create sample bookings for the next 7 days
            today = date.today()
            created_count = 0
            
            sample_services = [
                {'name': 'Deep Cleansing Facial', 'duration': 90, 'price': 150.0},
                {'name': 'Swedish Massage', 'duration': 60, 'price': 120.0},
                {'name': 'Hot Stone Massage', 'duration': 90, 'price': 160.0},
                {'name': 'Hair Cut & Style', 'duration': 75, 'price': 85.0},
                {'name': 'Aromatherapy Massage', 'duration': 75, 'price': 140.0},
                {'name': 'Express Facial', 'duration': 45, 'price': 75.0},
                {'name': 'Manicure & Pedicure', 'duration': 90, 'price': 95.0},
                {'name': 'Body Scrub Treatment', 'duration': 60, 'price': 110.0}
            ]
            
            sample_clients = [
                {'name': 'Jessica Williams', 'phone': '+1-555-0101', 'email': 'jessica.williams@email.com'},
                {'name': 'David Brown', 'phone': '+1-555-0102', 'email': 'david.brown@email.com'},
                {'name': 'Emma Thompson', 'phone': '+1-555-0103', 'email': 'emma.thompson@email.com'},
                {'name': 'Michael Johnson', 'phone': '+1-555-0104', 'email': 'michael.johnson@email.com'},
                {'name': 'Sarah Davis', 'phone': '+1-555-0105', 'email': 'sarah.davis@email.com'},
                {'name': 'James Wilson', 'phone': '+1-555-0106', 'email': 'james.wilson@email.com'},
                {'name': 'Lisa Anderson', 'phone': '+1-555-0107', 'email': 'lisa.anderson@email.com'},
                {'name': 'Robert Garcia', 'phone': '+1-555-0108', 'email': 'robert.garcia@email.com'}
            ]
            
            # Create bookings for the next 7 days
            for day_offset in range(7):
                booking_date = today + timedelta(days=day_offset)
                
                # Skip weekends for this example
                if booking_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                    continue
                
                # Create 3-5 bookings per day
                import random
                daily_bookings = random.randint(3, 5)
                
                for booking_num in range(daily_bookings):
                    # Select random staff, service, and client
                    staff = random.choice(staff_members)
                    service = random.choice(sample_services)
                    client = random.choice(sample_clients)
                    
                    # Generate random time between 9 AM and 5 PM
                    start_hour = random.randint(9, 16)
                    start_minute = random.choice([0, 30])
                    start_time_obj = time(start_hour, start_minute)
                    
                    # Calculate end time
                    start_datetime = datetime.combine(booking_date, start_time_obj)
                    end_datetime = start_datetime + timedelta(minutes=service['duration'])
                    
                    # Check for conflicts
                    existing_conflict = UnakiBooking.query.filter(
                        UnakiBooking.staff_id == staff.id,
                        UnakiBooking.appointment_date == booking_date,
                        UnakiBooking.start_time == start_time_obj
                    ).first()
                    
                    if existing_conflict:
                        continue  # Skip if conflict exists
                    
                    # Create booking
                    booking = UnakiBooking(
                        client_name=client['name'],
                        client_phone=client['phone'],
                        client_email=client['email'],
                        staff_id=staff.id,
                        staff_name=staff.full_name,
                        service_name=service['name'],
                        service_duration=service['duration'],
                        service_price=service['price'],
                        appointment_date=booking_date,
                        start_time=start_time_obj,
                        end_time=end_datetime.time(),
                        status=random.choice(['scheduled', 'confirmed', 'completed']),
                        notes=f'Sample booking created on {datetime.now().strftime("%Y-%m-%d")}',
                        booking_source='unaki_system',
                        booking_method='sample_data',
                        amount_charged=service['price'],
                        payment_status=random.choice(['pending', 'paid', 'partial']),
                        created_at=datetime.utcnow()
                    )
                    
                    db.session.add(booking)
                    created_count += 1
            
            # Commit all changes
            db.session.commit()
            
            print(f"✅ Successfully created {created_count} sample UnakiBooking entries!")
            print(f"📅 Bookings created for the next 7 days (weekdays only)")
            print(f"👥 {len(staff_members)} staff members assigned")
            print(f"🎯 {len(sample_services)} different services used")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating UnakiBooking table: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = create_unaki_booking_table()
    if success:
        print("\n🎉 UnakiBooking table setup completed successfully!")
    else:
        print("\n💥 UnakiBooking table setup failed!")
