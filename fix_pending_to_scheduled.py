
#!/usr/bin/env python3
"""
Fix all 'pending' status bookings to 'scheduled' status
This resolves the LookupError when querying online bookings
"""
from app import app, db
from sqlalchemy import text

def fix_pending_statuses():
    """Update all bookings with 'pending' status to 'scheduled'"""
    with app.app_context():
        try:
            # Check for 'pending' status bookings
            result = db.session.execute(
                text("SELECT COUNT(*) as count FROM unaki_booking WHERE status = 'pending'")
            )
            count = result.scalar()
            
            print(f"📋 Found {count} bookings with 'pending' status")
            
            if count == 0:
                print("✅ No bookings to update!")
                return
            
            # Update all 'pending' to 'scheduled'
            print(f"🔄 Updating {count} bookings from 'pending' to 'scheduled'...")
            
            db.session.execute(
                text("UPDATE unaki_booking SET status = 'scheduled' WHERE status = 'pending'")
            )
            db.session.commit()
            
            print("✅ Successfully updated all bookings!")
            
            # Verify
            result = db.session.execute(
                text("SELECT COUNT(*) as count FROM unaki_booking WHERE status = 'pending'")
            )
            remaining = result.scalar()
            
            if remaining == 0:
                print("🎉 All 'pending' statuses converted to 'scheduled'!")
            else:
                print(f"⚠️ Warning: {remaining} bookings still have 'pending' status")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    fix_pending_statuses()
