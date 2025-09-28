
#!/usr/bin/env python3

"""
Migration script to add the 'purpose' column to inventory_consumption table
"""

import sqlite3
import os

def add_purpose_column():
    """Add purpose column to inventory_consumption table"""
    
    # Database path
    db_path = 'workspace.db'
    if not os.path.exists(db_path):
        db_path = 'hanamantdatabase/workspace.db'
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if purpose column already exists
        cursor.execute("PRAGMA table_info(inventory_consumption)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'purpose' not in columns:
            print("📝 Adding 'purpose' column to inventory_consumption table...")
            
            # Add the purpose column
            cursor.execute("""
                ALTER TABLE inventory_consumption 
                ADD COLUMN purpose VARCHAR(50) DEFAULT 'other'
            """)
            
            conn.commit()
            print("✅ Successfully added 'purpose' column to inventory_consumption table")
        else:
            print("ℹ️ Purpose column already exists in inventory_consumption table")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding purpose column: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🔧 Starting database migration...")
    success = add_purpose_column()
    if success:
        print("✅ Migration completed successfully")
    else:
        print("❌ Migration failed")
