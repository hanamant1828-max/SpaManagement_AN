
"""
Fix bookings with invalid 'pending' status
Changes 'pending' to 'scheduled' for online bookings
"""
import sqlite3

def fix_pending_bookings():
    conn = sqlite3.connect('hanamantdatabase/workspace.db')
    cursor = conn.cursor()
    
    # Find bookings with 'pending' status
    cursor.execute("SELECT id, client_name, status FROM unaki_booking WHERE status = 'pending'")
    pending_bookings = cursor.fetchall()
    
    print(f"Found {len(pending_bookings)} bookings with 'pending' status")
    
    if pending_bookings:
        for booking_id, client_name, status in pending_bookings:
            print(f"  - Booking #{booking_id} ({client_name}): {status} -> scheduled")
        
        # Update all 'pending' to 'scheduled'
        cursor.execute("UPDATE unaki_booking SET status = 'scheduled' WHERE status = 'pending'")
        conn.commit()
        print(f"\n✅ Updated {cursor.rowcount} bookings from 'pending' to 'scheduled'")
    else:
        print("✅ No bookings with 'pending' status found")
    
    conn.close()

if __name__ == '__main__':
    fix_pending_bookings()
