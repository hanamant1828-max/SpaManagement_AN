#!/usr/bin/env python3
"""
Test online booking functionality with the fixed 'scheduled' status
"""
from app import app, db
from models import UnakiBooking, Customer, Service, User
from datetime import datetime, date, timedelta, time as dt_time

def create_test_bookings():
    """Create 4 test online bookings"""
    with app.app_context():
        # Get or create a test service
        service = Service.query.filter_by(is_active=True).first()
        if not service:
            print("❌ No active services found. Please create a service first.")
            return
        
        # Get or create staff
        staff = User.query.filter_by(is_active=True).first()
        if not staff:
            print("❌ No active staff found. Please create a staff member first.")
            return
        
        print(f"✅ Using service: {service.name} (${service.price})")
        print(f"✅ Using staff: {staff.first_name} {staff.last_name}")
        
        # Test booking data
        test_bookings = [
            {
                'client_name': 'John Smith',
                'client_phone': '555-0101',
                'client_email': 'john.smith@test.com',
                'date': date.today() + timedelta(days=1),
                'time': dt_time(10, 0)
            },
            {
                'client_name': 'Sarah Johnson',
                'client_phone': '555-0102',
                'client_email': 'sarah.j@test.com',
                'date': date.today() + timedelta(days=2),
                'time': dt_time(14, 30)
            },
            {
                'client_name': 'Michael Brown',
                'client_phone': '555-0103',
                'client_email': 'mbrown@test.com',
                'date': date.today() + timedelta(days=3),
                'time': dt_time(11, 0)
            },
            {
                'client_name': 'Emma Davis',
                'client_phone': '555-0104',
                'client_email': 'emma.davis@test.com',
                'date': date.today() + timedelta(days=4),
                'time': dt_time(16, 0)
            }
        ]
        
        created_bookings = []
        
        for i, booking_data in enumerate(test_bookings, 1):
            try:
                # Create or get customer
                customer = Customer.query.filter_by(phone=booking_data['client_phone']).first()
                if not customer:
                    name_parts = booking_data['client_name'].split(' ', 1)
                    customer = Customer(
                        first_name=name_parts[0],
                        last_name=name_parts[1] if len(name_parts) > 1 else '',
                        phone=booking_data['client_phone'],
                        email=booking_data['client_email'],
                        created_at=datetime.utcnow()
                    )
                    db.session.add(customer)
                    db.session.flush()
                
                # Calculate end time
                start_datetime = datetime.combine(booking_data['date'], booking_data['time'])
                end_datetime = start_datetime + timedelta(minutes=service.duration)
                
                # Create booking with 'scheduled' status (not 'pending')
                booking = UnakiBooking(
                    client_id=customer.id,
                    client_name=booking_data['client_name'],
                    client_phone=booking_data['client_phone'],
                    client_email=booking_data['client_email'],
                    staff_id=staff.id,
                    staff_name=f"{staff.first_name} {staff.last_name}",
                    service_id=service.id,
                    service_name=service.name,
                    service_duration=service.duration,
                    service_price=service.price,
                    appointment_date=booking_data['date'],
                    start_time=booking_data['time'],
                    end_time=end_datetime.time(),
                    status='scheduled',  # Using valid enum value
                    notes=f'Test online booking #{i}',
                    booking_source='online',
                    booking_method='website',
                    amount_charged=service.price,
                    payment_status='pending',
                    created_at=datetime.utcnow()
                )
                
                db.session.add(booking)
                created_bookings.append(booking)
                
                print(f"✅ Created booking #{i}: {booking_data['client_name']} - {booking_data['date']} at {booking_data['time']}")
                
            except Exception as e:
                print(f"❌ Error creating booking #{i}: {e}")
                import traceback
                traceback.print_exc()
        
        # Commit all bookings
        try:
            db.session.commit()
            print(f"\n🎉 Successfully created {len(created_bookings)} test bookings!")
            
            # Verify bookings
            print("\n📊 Booking Details:")
            for booking in created_bookings:
                print(f"  - ID: {booking.id}")
                print(f"    Client: {booking.client_name}")
                print(f"    Service: {booking.service_name}")
                print(f"    Date/Time: {booking.appointment_date} at {booking.start_time}")
                print(f"    Status: {booking.status} ✅")
                print(f"    Payment Status: {booking.payment_status}")
                print()
            
            # Show statistics
            from modules.bookings.online_booking_queries import get_online_booking_stats
            stats = get_online_booking_stats()
            print("📊 Online Booking Statistics:")
            print(f"  Total: {stats['total']}")
            print(f"  Pending (Scheduled): {stats['pending']}")
            print(f"  Accepted (Confirmed): {stats['accepted']}")
            print(f"  Rejected (Cancelled): {stats['rejected']}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error committing bookings: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    create_test_bookings()
