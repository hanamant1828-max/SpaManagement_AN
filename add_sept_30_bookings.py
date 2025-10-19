
#!/usr/bin/env python3
"""
Add 10 sample bookings on September 30, 2025
"""

from app import app, db
from models import UnakiBooking, User, Service, Customer
from datetime import date, time, datetime

def add_september_30_bookings():
    """Add 10 bookings on September 30, 2025"""
    
    with app.app_context():
        target_date = date(2025, 9, 30)
        
        print("=" * 80)
        print(f"📅 ADDING 10 BOOKINGS FOR: {target_date.strftime('%A, September %d, %Y')}")
        print("=" * 80)
        
        # Get active staff members
        staff_members = User.query.filter_by(is_active=True).limit(5).all()
        if not staff_members:
            print("❌ No active staff found")
            return
        
        print(f"✅ Found {len(staff_members)} active staff members")
        
        # Get active services
        services = Service.query.filter_by(is_active=True).limit(10).all()
        if not services:
            print("❌ No active services found")
            return
        
        print(f"✅ Found {len(services)} active services")
        
        # Sample booking data
        sample_bookings = [
            {
                'client_name': 'Emma Watson',
                'client_phone': '+1-555-0901',
                'service_name': 'Deep Tissue Massage',
                'duration': 60,
                'staff_id': staff_members[0].id,
                'start_time': '09:00',
                'end_time': '10:00'
            },
            {
                'client_name': 'Olivia Brown',
                'client_phone': '+1-555-0902',
                'service_name': 'Anti-Aging Facial',
                'duration': 75,
                'staff_id': staff_members[1 % len(staff_members)].id,
                'start_time': '10:30',
                'end_time': '11:45'
            },
            {
                'client_name': 'Sophia Martinez',
                'client_phone': '+1-555-0903',
                'service_name': 'Swedish Massage',
                'duration': 60,
                'staff_id': staff_members[0].id,
                'start_time': '11:00',
                'end_time': '12:00'
            },
            {
                'client_name': 'Ava Johnson',
                'client_phone': '+1-555-0904',
                'service_name': 'Hot Stone Massage',
                'duration': 90,
                'staff_id': staff_members[2 % len(staff_members)].id,
                'start_time': '13:00',
                'end_time': '14:30'
            },
            {
                'client_name': 'Isabella Garcia',
                'client_phone': '+1-555-0905',
                'service_name': 'Spa Pedicure',
                'duration': 60,
                'staff_id': staff_members[1 % len(staff_members)].id,
                'start_time': '13:30',
                'end_time': '14:30'
            },
            {
                'client_name': 'Mia Davis',
                'client_phone': '+1-555-0906',
                'service_name': 'Classic Manicure',
                'duration': 45,
                'staff_id': staff_members[3 % len(staff_members)].id,
                'start_time': '14:00',
                'end_time': '14:45'
            },
            {
                'client_name': 'Charlotte Wilson',
                'client_phone': '+1-555-0907',
                'service_name': 'Aromatherapy Massage',
                'duration': 60,
                'staff_id': staff_members[0].id,
                'start_time': '14:00',
                'end_time': '15:00'
            },
            {
                'client_name': 'Amelia Moore',
                'client_phone': '+1-555-0908',
                'service_name': 'Hydrating Facial',
                'duration': 60,
                'staff_id': staff_members[2 % len(staff_members)].id,
                'start_time': '15:00',
                'end_time': '16:00'
            },
            {
                'client_name': 'Harper Taylor',
                'client_phone': '+1-555-0909',
                'service_name': 'Gel Manicure',
                'duration': 50,
                'staff_id': staff_members[4 % len(staff_members)].id,
                'start_time': '15:30',
                'end_time': '16:20'
            },
            {
                'client_name': 'Evelyn Anderson',
                'client_phone': '+1-555-0910',
                'service_name': 'Couples Massage',
                'duration': 90,
                'staff_id': staff_members[1 % len(staff_members)].id,
                'start_time': '16:00',
                'end_time': '17:30'
            }
        ]
        
        created_count = 0
        
        for booking_data in sample_bookings:
            # Find or create customer
            customer = Customer.query.filter_by(phone=booking_data['client_phone']).first()
            if not customer:
                customer = Customer(
                    full_name=booking_data['client_name'],
                    phone=booking_data['client_phone'],
                    email=f"{booking_data['client_name'].lower().replace(' ', '.')}@example.com",
                    is_active=True
                )
                db.session.add(customer)
                db.session.flush()
            
            # Find service by name or use first available
            service = Service.query.filter_by(name=booking_data['service_name'], is_active=True).first()
            if not service and services:
                service = services[created_count % len(services)]
            
            service_price = float(service.price) if service and service.price else 100.0
            
            # Parse times
            start_time_obj = datetime.strptime(booking_data['start_time'], '%H:%M').time()
            end_time_obj = datetime.strptime(booking_data['end_time'], '%H:%M').time()
            
            # Get staff
            staff = User.query.get(booking_data['staff_id'])
            
            # Create booking
            unaki_booking = UnakiBooking(
                client_id=customer.id,
                client_name=booking_data['client_name'],
                client_phone=booking_data['client_phone'],
                client_email=customer.email,
                staff_id=booking_data['staff_id'],
                staff_name=staff.full_name if staff else f'Staff {booking_data["staff_id"]}',
                service_id=service.id if service else None,
                service_name=booking_data['service_name'],
                service_duration=booking_data['duration'],
                service_price=service_price,
                appointment_date=target_date,
                start_time=start_time_obj,
                end_time=end_time_obj,
                status='confirmed',
                notes=f'Sample booking for September 30',
                booking_source='unaki_system',
                booking_method='script_created',
                amount_charged=service_price,
                payment_status='pending',
                created_at=datetime.utcnow()
            )
            
            db.session.add(unaki_booking)
            created_count += 1
            
            print(f"✅ Created: {booking_data['client_name']} - {booking_data['service_name']} at {booking_data['start_time']}")
        
        db.session.commit()
        
        print("\n" + "=" * 80)
        print(f"🎉 Successfully created {created_count} bookings for September 30, 2025")
        print("=" * 80)
        
        # Verify
        total_bookings = UnakiBooking.query.filter_by(appointment_date=target_date).count()
        print(f"📊 Total bookings on September 30, 2025: {total_bookings}")

if __name__ == "__main__":
    add_september_30_bookings()
