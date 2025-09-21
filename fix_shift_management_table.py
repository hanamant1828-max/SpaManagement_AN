
#!/usr/bin/env python3
"""
Fix shift_management table by adding missing updated_at column
"""

import sqlite3
from datetime import datetime
import os

def fix_shift_management_table():
    """Add updated_at column to shift_management table"""
    db_path = 'instance/spa_management.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if updated_at column exists
        cursor.execute("PRAGMA table_info(shift_management)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"📋 Current columns in shift_management: {column_names}")
        
        if 'updated_at' not in column_names:
            print("🔧 Adding updated_at column to shift_management table...")
            
            # Add the updated_at column with default value
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"""
                ALTER TABLE shift_management 
                ADD COLUMN updated_at TIMESTAMP DEFAULT '{current_time}'
            """)
            
            # Update existing records to have the current timestamp
            cursor.execute(f"""
                UPDATE shift_management 
                SET updated_at = '{current_time}' 
                WHERE updated_at IS NULL
            """)
            
            conn.commit()
            print("✅ Successfully added updated_at column")
            
            # Verify the column was added
            cursor.execute("PRAGMA table_info(shift_management)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            print(f"📋 Updated columns in shift_management: {column_names}")
            
        else:
            print("✅ updated_at column already exists")
        
        # Show current records count
        cursor.execute("SELECT COUNT(*) FROM shift_management")
        count = cursor.fetchone()[0]
        print(f"📊 Total shift_management records: {count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing shift_management table: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing shift_management table...")
    print("=" * 50)
    
    if fix_shift_management_table():
        print("\n✅ Database fix completed successfully!")
        print("You can now restart the application.")
    else:
        print("\n❌ Database fix failed!")
