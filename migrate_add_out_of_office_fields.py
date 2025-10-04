
import sqlite3
import os

def migrate_database():
    """Add out_of_office fields to shift_logs table"""
    
    db_path = 'instance/spa_management.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Adding out_of_office fields to shift_logs table...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(shift_logs)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'out_of_office_start' not in columns:
            cursor.execute("ALTER TABLE shift_logs ADD COLUMN out_of_office_start TIME")
            print("✅ Added out_of_office_start column")
        else:
            print("ℹ️ out_of_office_start column already exists")
        
        if 'out_of_office_end' not in columns:
            cursor.execute("ALTER TABLE shift_logs ADD COLUMN out_of_office_end TIME")
            print("✅ Added out_of_office_end column")
        else:
            print("ℹ️ out_of_office_end column already exists")
        
        if 'out_of_office_reason' not in columns:
            cursor.execute("ALTER TABLE shift_logs ADD COLUMN out_of_office_reason VARCHAR(500)")
            print("✅ Added out_of_office_reason column")
        else:
            print("ℹ️ out_of_office_reason column already exists")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    migrate_database()
