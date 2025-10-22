
#!/usr/bin/env python3
"""
Fix existing online bookings to have 'pending' status
"""
from app import app, db
from models import UnakiBooking
from datetime import datetime

def fix_online_booking_status():
    """Update all online bookings from 'scheduled' to 'pending'"""
    with app.app_context():
        # Find all online bookings that are currently 'scheduled'
        bookings = UnakiBooking.query.filter_by(
            booking_source='website',
            status='scheduled'
        ).all()
        
        if not bookings:
            print("✅ No bookings to update - all online bookings are already in correct status")
            return
        
        print(f"📋 Found {len(bookings)} online bookings with 'scheduled' status")
        print("🔄 Updating to 'pending' status...")
        
        updated_count = 0
        for booking in bookings:
            # Only update if it wasn't manually accepted by staff
            # Check if there are any acceptance notes
            if booking.notes and 'Booking accepted' in booking.notes:
                print(f"  ⏭️  Skipping booking #{booking.id} - was manually accepted")
                continue
            
            booking.status = 'pending'
            updated_count += 1
        
        db.session.commit()
        print(f"✅ Updated {updated_count} bookings to 'pending' status")
        print(f"⏭️  Skipped {len(bookings) - updated_count} bookings (manually accepted)")
        
        # Show current stats
        total = UnakiBooking.query.filter_by(booking_source='website').count()
        pending = UnakiBooking.query.filter_by(booking_source='website', status='pending').count()
        scheduled = UnakiBooking.query.filter_by(booking_source='website', status='scheduled').count()
        cancelled = UnakiBooking.query.filter_by(booking_source='website', status='cancelled').count()
        
        print("\n📊 Current Online Booking Statistics:")
        print(f"  Total: {total}")
        print(f"  Pending: {pending}")
        print(f"  Accepted: {scheduled}")
        print(f"  Rejected: {cancelled}")

if __name__ == '__main__':
    fix_online_booking_status()
