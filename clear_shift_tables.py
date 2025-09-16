
#!/usr/bin/env python3
"""
Clear all records from shift_management and shift_logs tables
"""

import sqlite3
import os
from datetime import datetime

def clear_shift_tables():
    """Delete all records from shift_management and shift_logs tables"""
    db_path = 'instance/spa_management.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current record counts before deletion
        cursor.execute("SELECT COUNT(*) FROM shift_logs")
        logs_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM shift_management")
        management_count = cursor.fetchone()[0]
        
        print(f"📊 Current records:")
        print(f"   - shift_logs: {logs_count}")
        print(f"   - shift_management: {management_count}")
        
        if logs_count == 0 and management_count == 0:
            print("✅ Tables are already empty!")
            return True
        
        # Delete all records from shift_logs first (due to foreign key constraint)
        print("\n🗑️ Deleting records from shift_logs...")
        cursor.execute("DELETE FROM shift_logs")
        deleted_logs = cursor.rowcount
        print(f"✅ Deleted {deleted_logs} records from shift_logs")
        
        # Delete all records from shift_management
        print("🗑️ Deleting records from shift_management...")
        cursor.execute("DELETE FROM shift_management")
        deleted_management = cursor.rowcount
        print(f"✅ Deleted {deleted_management} records from shift_management")
        
        # Reset auto-increment counters
        print("🔄 Resetting auto-increment counters...")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='shift_logs'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='shift_management'")
        
        # Commit all changes
        conn.commit()
        
        # Verify deletion
        cursor.execute("SELECT COUNT(*) FROM shift_logs")
        remaining_logs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM shift_management")
        remaining_management = cursor.fetchone()[0]
        
        print(f"\n📊 After deletion:")
        print(f"   - shift_logs: {remaining_logs}")
        print(f"   - shift_management: {remaining_management}")
        
        conn.close()
        
        if remaining_logs == 0 and remaining_management == 0:
            print("\n✅ All records successfully deleted!")
            return True
        else:
            print("\n❌ Some records may not have been deleted!")
            return False
        
    except Exception as e:
        print(f"❌ Error clearing shift tables: {e}")
        return False

if __name__ == "__main__":
    print("🗑️ Clearing shift management and shift logs tables...")
    print("=" * 60)
    
    # Ask for confirmation
    confirm = input("Are you sure you want to delete ALL shift records? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y']:
        if clear_shift_tables():
            print("\n✅ Database cleanup completed successfully!")
            print("All shift management and shift logs records have been deleted.")
        else:
            print("\n❌ Database cleanup failed!")
    else:
        print("❌ Operation cancelled by user")
