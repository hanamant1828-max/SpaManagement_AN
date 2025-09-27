
#!/usr/bin/env python3
"""
Debug script to check appointment to customer mapping issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Customer, UnakiBooking

def debug_appointment_customer_mapping():
    """Debug appointment to customer mapping"""
    with app.app_context():
        print("🔍 Debugging Appointment to Customer Mapping")
        print("=" * 60)
        
        # Get all UnakiBookings
        bookings = UnakiBooking.query.all()
        
        print(f"📅 Total UnakiBookings: {len(bookings)}")
        print()
        
        for booking in bookings[:15]:  # Show first 15
            print(f"🎯 Booking ID: {booking.id}")
            print(f"   Client Name: {booking.client_name}")
            print(f"   Client Phone: {booking.client_phone}")
            print(f"   Current client_id: {booking.client_id}")
            print(f"   Service: {booking.service_name}")
            print(f"   Date: {booking.appointment_date}")
            
            # Check if client_id exists and is valid
            if booking.client_id:
                customer = Customer.query.get(booking.client_id)
                if customer:
                    print(f"   ✅ Valid Customer: {customer.full_name} (ID: {customer.id})")
                else:
                    print(f"   ❌ Invalid client_id: {booking.client_id} (customer not found)")
            else:
                print(f"   ⚠️ No client_id set")
                
                # Try to find matching customer
                matches = []
                
                # Try phone match
                if booking.client_phone:
                    phone_match = Customer.query.filter_by(phone=booking.client_phone).first()
                    if phone_match:
                        matches.append(f"Phone: {phone_match.full_name} (ID: {phone_match.id})")
                
                # Try name match
                if booking.client_name:
                    name_parts = booking.client_name.strip().split(' ', 1)
                    first_name = name_parts[0] if name_parts else ''
                    
                    if first_name:
                        name_match = Customer.query.filter(
                            Customer.first_name.ilike(f'%{first_name}%')
                        ).first()
                        if name_match:
                            matches.append(f"Name: {name_match.full_name} (ID: {name_match.id})")
                
                if matches:
                    print(f"   🔗 Potential matches: {', '.join(matches)}")
                else:
                    print(f"   🚫 No matching customers found")
            
            print("-" * 40)

if __name__ == "__main__":
    debug_appointment_customer_mapping()
