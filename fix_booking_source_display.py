
#!/usr/bin/env python3
"""
Fix booking sources for website bookings
"""
from app import app, db
from models import UnakiBooking

def fix_booking_sources():
    """Update booking sources for website bookings"""
    with app.app_context():
        # Find all bookings with booking_method='online_booking' but wrong booking_source
        online_bookings = UnakiBooking.query.filter_by(booking_method='online_booking').all()
        
        print(f"📋 Found {len(online_bookings)} online bookings to check")
        
        updated_count = 0
        for booking in online_bookings:
            if booking.booking_source != 'online':
                print(f"  🔄 Updating booking {booking.id}: '{booking.booking_source}' → 'online'")
                booking.booking_source = 'online'
                updated_count += 1
        
        # Also check for bookings with booking_source='website' and change to 'online'
        website_bookings = UnakiBooking.query.filter_by(booking_source='website').all()
        for booking in website_bookings:
            print(f"  🔄 Updating booking {booking.id}: 'website' → 'online'")
            booking.booking_source = 'online'
            updated_count += 1
        
        if updated_count > 0:
            db.session.commit()
            print(f"✅ Updated {updated_count} bookings to 'online' source")
        else:
            print("✅ All online bookings already have correct source")
        
        # Show current stats
        stats = {
            'online': UnakiBooking.query.filter_by(booking_source='online').count(),
            'manual': UnakiBooking.query.filter_by(booking_source='manual').count(),
            'unaki_system': UnakiBooking.query.filter_by(booking_source='unaki_system').count(),
            'walk_in': UnakiBooking.query.filter_by(booking_source='walk_in').count(),
        }
        
        print("\n📊 Current Booking Source Statistics:")
        for source, count in stats.items():
            print(f"  {source}: {count}")

if __name__ == '__main__':
    fix_booking_sources()
