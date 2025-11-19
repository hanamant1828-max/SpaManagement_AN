
#!/usr/bin/env python3
"""
Fix existing online bookings to link them to customer records
This ensures online booking customers appear in Client Management
"""
from app import app, db
from models import UnakiBooking, Customer
from datetime import datetime

def fix_online_booking_customers():
    """Link existing online bookings to customer records"""
    with app.app_context():
        print("🔍 Fixing Online Booking Customer Links")
        print("=" * 60)
        
        # Find all online bookings
        online_bookings = UnakiBooking.query.filter(
            UnakiBooking.booking_source.in_(['online', 'website'])
        ).all()
        
        print(f"📋 Found {len(online_bookings)} online bookings")
        
        fixed_count = 0
        created_count = 0
        already_linked_count = 0
        
        for booking in online_bookings:
            # Skip if already properly linked
            if booking.client_id:
                customer = Customer.query.get(booking.client_id)
                if customer:
                    already_linked_count += 1
                    print(f"✅ Booking #{booking.id} already linked to Customer #{customer.id}")
                    continue
                else:
                    print(f"⚠️ Booking #{booking.id} has invalid client_id {booking.client_id}")
            
            # Try to find customer by phone
            customer = None
            if booking.client_phone:
                customer = Customer.query.filter_by(phone=booking.client_phone).first()
            
            # If not found, create new customer
            if not customer:
                # Parse name
                name_parts = (booking.client_name or 'Guest').strip().split(maxsplit=1)
                first_name = name_parts[0] if name_parts else 'Guest'
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                customer = Customer(
                    first_name=first_name,
                    last_name=last_name,
                    phone=booking.client_phone or '',
                    email=booking.client_email if booking.client_email and '@' in (booking.client_email or '') else None,
                    is_active=True,
                    total_visits=0,
                    total_spent=0.0,
                    created_at=booking.created_at or datetime.utcnow()
                )
                db.session.add(customer)
                db.session.flush()
                
                print(f"✨ Created Customer #{customer.id}: {customer.first_name} {customer.last_name} (Phone: {customer.phone})")
                created_count += 1
            else:
                print(f"🔗 Found existing Customer #{customer.id}: {customer.first_name} {customer.last_name}")
            
            # Link booking to customer
            booking.client_id = customer.id
            booking.client_name = f"{customer.first_name} {customer.last_name}".strip()
            booking.client_phone = customer.phone
            booking.client_email = customer.email
            
            print(f"✅ Linked Booking #{booking.id} to Customer #{customer.id}")
            fixed_count += 1
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("📊 Summary:")
        print(f"   Total online bookings: {len(online_bookings)}")
        print(f"   Already linked: {already_linked_count}")
        print(f"   Newly linked: {fixed_count}")
        print(f"   New customers created: {created_count}")
        print("=" * 60)
        print("✅ All online booking customers are now linked!")

if __name__ == '__main__':
    fix_online_booking_customers()
