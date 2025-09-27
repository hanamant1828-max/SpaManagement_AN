
#!/usr/bin/env python3
"""
Debug script to check UnakiBooking to Customer matching
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Customer, UnakiBooking

def debug_customer_booking_match():
    with app.app_context():
        print("🔍 DEBUG: Customer to UnakiBooking Matching Analysis")
        print("=" * 60)
        
        # Get all customers
        customers = Customer.query.filter_by(is_active=True).all()
        print(f"📊 Total active customers: {len(customers)}")
        
        # Get all UnakiBookings
        unaki_bookings = UnakiBooking.query.filter(
            UnakiBooking.status.in_(['scheduled', 'confirmed'])
        ).all()
        print(f"📅 Total ready-to-bill UnakiBookings: {len(unaki_bookings)}")
        print()
        
        # Check each customer for matching bookings
        for customer in customers:
            print(f"👤 Customer: {customer.first_name} {customer.last_name} (ID: {customer.id})")
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
            
            # Method 3: Match by name
            full_name = f"{customer.first_name} {customer.last_name}".strip()
            name_matches = UnakiBooking.query.filter(
                UnakiBooking.client_name.ilike(f'%{full_name}%'),
                UnakiBooking.status.in_(['scheduled', 'confirmed'])
            ).all()
            
            print(f"   💎 ID Matches: {len(id_matches)}")
            print(f"   📞 Phone Matches: {len(phone_matches)}")
            print(f"   📝 Name Matches: {len(name_matches)}")
            
            if id_matches or phone_matches or name_matches:
                print("   ✅ HAS READY-TO-BILL BOOKINGS")
                # Show the matching bookings
                all_matches = list(set(id_matches + phone_matches + name_matches))
                for booking in all_matches[:3]:  # Show first 3
                    print(f"      - {booking.service_name} on {booking.appointment_date} ({booking.status})")
            else:
                print("   ❌ NO READY-TO-BILL BOOKINGS")
            print()
        
        print("🔍 UnakiBooking Records Without Customer Match:")
        print("=" * 50)
        
        # Show UnakiBookings that don't match any customer
        for booking in unaki_bookings[:10]:  # Show first 10
            print(f"📅 Booking: {booking.client_name} - {booking.service_name}")
            print(f"   Phone: {booking.client_phone}")
            print(f"   Client ID: {booking.client_id}")
            print(f"   Date: {booking.appointment_date}")
            print(f"   Status: {booking.status}")
            
            # Check if this booking has a matching customer
            customer_match = None
            if booking.client_id:
                customer_match = Customer.query.get(booking.client_id)
            elif booking.client_phone:
                customer_match = Customer.query.filter_by(phone=booking.client_phone).first()
            
            if customer_match:
                print(f"   ✅ Matches Customer: {customer_match.first_name} {customer_match.last_name}")
            else:
                print(f"   ❌ NO MATCHING CUSTOMER FOUND")
            print()

if __name__ == "__main__":
    debug_customer_booking_match()
