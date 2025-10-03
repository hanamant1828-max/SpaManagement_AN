
#!/usr/bin/env python3

"""
Migration script to add the 'purpose' column to inventory_consumption table
"""

import sqlite3
import os

def add_purpose_column():
    """Add purpose column to inventory_consumption table"""
    
    # Database path - check multiple locations
    db_path = 'workspace.db'
    if not os.path.exists(db_path):
        db_path = 'hanamantdatabase/workspace.db'
    if not os.path.exists(db_path):
        db_path = '/home/runner/workspace/hanamantdatabase/workspace.db'
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return False
    
    print(f"📂 Using database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if purpose column already exists
        cursor.execute("PRAGMA table_info(inventory_consumption)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📊 Current columns in inventory_consumption: {columns}")
        
        if 'purpose' not in columns:
            print("📝 Adding 'purpose' column to inventory_consumption table...")
            
            # Add the purpose column with a default value
            cursor.execute("""
                ALTER TABLE inventory_consumption 
                ADD COLUMN purpose VARCHAR(100) DEFAULT 'other'
            """)
            
            conn.commit()
            print("✅ Successfully added 'purpose' column to inventory_consumption table")
            
            # Verify the column was added
            cursor.execute("PRAGMA table_info(inventory_consumption)")
            new_columns = [column[1] for column in cursor.fetchall()]
            print(f"📊 Updated columns: {new_columns}")
        else:
            print("ℹ️ Purpose column already exists in inventory_consumption table")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding purpose column: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🔧 Starting database migration...")
    success = add_purpose_column()
    if success:
        print("✅ Migration completed successfully")
        print("⚠️ Please restart your Flask application for changes to take effect")
    else:
        print("❌ Migration failed")
