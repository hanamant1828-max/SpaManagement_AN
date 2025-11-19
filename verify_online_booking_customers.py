
#!/usr/bin/env python3
"""
Verify that online booking customers are visible in Client Management
"""
from app import app, db
from models import Customer, UnakiBooking

def verify_online_booking_customers():
    with app.app_context():
        print("🔍 Verifying Online Booking Customer Visibility")
        print("=" * 60)
        
        # Get all online bookings
        online_bookings = UnakiBooking.query.filter(
            UnakiBooking.booking_source.in_(['online', 'website'])
        ).all()
        
        print(f"📋 Found {len(online_bookings)} online bookings")
        print()
        
        # Check each booking's customer
        issues_found = []
        
        for booking in online_bookings:
            print(f"📅 Booking #{booking.id}: {booking.client_name}")
            print(f"   Phone: {booking.client_phone}")
            print(f"   Client ID: {booking.client_id}")
            
            if not booking.client_id:
                print(f"   ❌ ERROR: No client_id set!")
                issues_found.append(f"Booking #{booking.id} has no client_id")
                continue
            
            # Get the customer
            customer = Customer.query.get(booking.client_id)
            
            if not customer:
                print(f"   ❌ ERROR: Customer ID {booking.client_id} not found in database!")
                issues_found.append(f"Booking #{booking.id} references non-existent customer #{booking.client_id}")
                continue
            
            print(f"   ✅ Customer found: {customer.first_name} {customer.last_name}")
            print(f"      - Active: {customer.is_active}")
            print(f"      - Phone: {customer.phone}")
            print(f"      - Email: {customer.email}")
            
            if not customer.is_active:
                print(f"   ⚠️  WARNING: Customer is marked as INACTIVE!")
                issues_found.append(f"Customer #{customer.id} ({customer.first_name} {customer.last_name}) is inactive")
            
            print()
        
        # Summary
        print("=" * 60)
        print("📊 Summary:")
        print(f"   Total online bookings: {len(online_bookings)}")
        print(f"   Issues found: {len(issues_found)}")
        
        if issues_found:
            print("\n⚠️  Issues:")
            for issue in issues_found:
                print(f"   - {issue}")
        else:
            print("\n✅ All online booking customers are properly linked and active!")
        
        # Check how many active customers total
        total_active_customers = Customer.query.filter_by(is_active=True).count()
        print(f"\n📊 Total active customers in system: {total_active_customers}")
        
        # Get customers from online bookings
        online_customer_ids = set(b.client_id for b in online_bookings if b.client_id)
        online_customers = Customer.query.filter(
            Customer.id.in_(online_customer_ids),
            Customer.is_active == True
        ).all()
        
        print(f"📊 Active customers from online bookings: {len(online_customers)}")
        
        print("\n🔍 Online Booking Customers:")
        for customer in online_customers:
            booking_count = UnakiBooking.query.filter_by(
                client_id=customer.id,
                booking_source='online'
            ).count()
            print(f"   - {customer.first_name} {customer.last_name} (ID: {customer.id})")
            print(f"     Phone: {customer.phone}, Bookings: {booking_count}")

if __name__ == '__main__':
    verify_online_booking_customers()
