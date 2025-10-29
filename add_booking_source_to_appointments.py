
"""
Migration script to add booking_source column to appointments table
"""

import sqlite3
from datetime import datetime

def migrate_database():
    """Add booking_source column to appointments table"""
    db_path = 'hanamantdatabase/workspace.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(appointment)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'booking_source' not in columns:
            print("Adding booking_source column to appointment table...")
            cursor.execute("""
                ALTER TABLE appointment 
                ADD COLUMN booking_source VARCHAR(50) DEFAULT 'manual'
            """)
            conn.commit()
            print("✅ booking_source column added successfully")
        else:
            print("✅ booking_source column already exists")
        
        # Update existing appointments to have 'manual' as default source
        cursor.execute("""
            UPDATE appointment 
            SET booking_source = 'manual' 
            WHERE booking_source IS NULL
        """)
        conn.commit()
        print(f"✅ Updated existing appointments with default booking_source")
        
        conn.close()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    migrate_database()
