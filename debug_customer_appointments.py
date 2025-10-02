
#!/usr/bin/env python3
"""
Debug script to check customer appointment matching in integrated billing
"""

from app import app, db
from models import Customer, UnakiBooking, Service

def debug_customer_appointments():
    with app.app_context():
        print("=" * 80)
        print("CUSTOMER APPOINTMENTS DEBUG")
        print("=" * 80)
        
        # Get all customers
        customers = Customer.query.filter_by(is_active=True).all()
        print(f"\n📊 Total Active Customers: {len(customers)}")
        
        # Get all Unaki bookings
        all_bookings = UnakiBooking.query.filter(
            UnakiBooking.status.in_(['scheduled', 'confirmed'])
        ).all()
        print(f"📅 Total Scheduled/Confirmed Bookings: {len(all_bookings)}\n")
        
        # Check each customer
        for customer in customers[:10]:  # Check first 10 customers
            print(f"\n👤 Customer: {customer.first_name} {customer.last_name}")
            print(f"   ID: {customer.id}")
            print(f"   Phone: {customer.phone}")
            print(f"   Email: {customer.email}")
            
            # Method 1: Match by client_id
            id_matches = UnakiBooking.query.filter(
                UnakiBooking.client_id == customer.id,
                UnakiBooking.status.in_(['scheduled', 'confirmed'])
            ).all()
            
            # Method 2: Match by phone
            phone_matches = []
            if customer.phone:
                phone_matches = UnakiBooking.query.filter(
                    UnakiBooking.client_phone == customer.phone,
                    UnakiBooking.status.in_(['scheduled', 'confirmed'])
                ).all()
                
                # Try partial phone match
                if not phone_matches:
                    phone_digits = ''.join(filter(str.isdigit, customer.phone))
                    if len(phone_digits) >= 10:
                        last_10 = phone_digits[-10:]
                        phone_matches = UnakiBooking.query.filter(
                            UnakiBooking.client_phone.like(f'%{last_10}%'),
                            UnakiBooking.status.in_(['scheduled', 'confirmed'])
                        ).all()
            
            # Method 3: Match by name
            full_name = f"{customer.first_name} {customer.last_name}".strip()
            name_matches = UnakiBooking.query.filter(
                UnakiBooking.client_name.ilike(f'%{full_name}%'),
                UnakiBooking.status.in_(['scheduled', 'confirmed'])
            ).all()
            
            print(f"   📍 Matches by ID: {len(id_matches)}")
            print(f"   📞 Matches by Phone: {len(phone_matches)}")
            print(f"   📝 Matches by Name: {len(name_matches)}")
            
            # Show all unique matches
            all_matches = list(set(id_matches + phone_matches + name_matches))
            if all_matches:
                print(f"   ✅ Total Unique Bookings: {len(all_matches)}")
                for booking in all_matches[:3]:  # Show first 3
                    print(f"      - {booking.service_name} on {booking.appointment_date} at {booking.start_time} (₹{booking.service_price})")
            else:
                print(f"   ❌ No bookings found")
        
        print("\n" + "=" * 80)
        print("DEBUG COMPLETE")
        print("=" * 80)

if __name__ == '__main__':
    debug_customer_appointments()
