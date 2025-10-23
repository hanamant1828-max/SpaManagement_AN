#!/usr/bin/env python3
"""
Fix existing bookings with 'pending' status to 'scheduled'
This fixes the LookupError when trying to view online bookings
"""
from app import app, db
from sqlalchemy import text

def fix_pending_status():
    """Update all bookings with 'pending' status to 'scheduled'"""
    with app.app_context():
        try:
            # First, let's check how many bookings have 'pending' status
            result = db.session.execute(
                text("SELECT COUNT(*) as count FROM unaki_booking WHERE status = 'pending'")
            )
            count = result.scalar()
            
            print(f"📋 Found {count} bookings with 'pending' status")
            
            if count == 0:
                print("✅ No bookings to update - all statuses are valid!")
                return
            
            # Show some examples before updating
            result = db.session.execute(
                text("SELECT id, client_name, status, booking_source FROM unaki_booking WHERE status = 'pending' LIMIT 5")
            )
            examples = result.fetchall()
            
            print("\n📋 Examples of bookings to update:")
            for row in examples:
                print(f"  - ID: {row[0]}, Client: {row[1]}, Status: {row[2]}, Source: {row[3]}")
            
            # Update all 'pending' statuses to 'scheduled'
            print(f"\n🔄 Updating {count} bookings from 'pending' to 'scheduled'...")
            
            db.session.execute(
                text("UPDATE unaki_booking SET status = 'scheduled' WHERE status = 'pending'")
            )
            db.session.commit()
            
            print("✅ Successfully updated all bookings!")
            
            # Verify the update
            result = db.session.execute(
                text("SELECT COUNT(*) as count FROM unaki_booking WHERE status = 'pending'")
            )
            remaining = result.scalar()
            
            result = db.session.execute(
                text("SELECT COUNT(*) as count FROM unaki_booking WHERE status = 'scheduled'")
            )
            scheduled_count = result.scalar()
            
            print(f"\n📊 Status after update:")
            print(f"  - Pending: {remaining}")
            print(f"  - Scheduled: {scheduled_count}")
            
            if remaining == 0:
                print("\n🎉 All 'pending' statuses have been successfully converted to 'scheduled'!")
            else:
                print(f"\n⚠️  Warning: {remaining} bookings still have 'pending' status")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating bookings: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    fix_pending_status()
