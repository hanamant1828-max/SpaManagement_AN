
#!/usr/bin/env python3
"""
Fix bookings with invalid 'pending' status
Changes 'pending' to 'scheduled' in the database
"""
import sqlite3
import os

def fix_pending_status():
    db_path = 'hanamantdatabase/workspace.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Find bookings with 'pending' status
        cursor.execute("SELECT id, client_name, status FROM unaki_bookings WHERE status = 'pending'")
        pending_bookings = cursor.fetchall()
        
        print(f"🔍 Found {len(pending_bookings)} bookings with 'pending' status")
        
        if pending_bookings:
            print("\n📋 Bookings to be updated:")
            for booking_id, client_name, status in pending_bookings:
                print(f"  - Booking #{booking_id} ({client_name}): {status} → scheduled")
            
            # Update all 'pending' to 'scheduled'
            cursor.execute("UPDATE unaki_bookings SET status = 'scheduled' WHERE status = 'pending'")
            conn.commit()
            print(f"\n✅ Successfully updated {cursor.rowcount} bookings from 'pending' to 'scheduled'")
        else:
            print("✅ No bookings with 'pending' status found")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    fix_pending_status()
