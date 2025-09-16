
#!/usr/bin/env python3
"""
Force clear all records from shift_management and shift_logs tables
"""

import sqlite3
import os
from datetime import datetime

def force_clear_shift_tables():
    """Force delete all records from shift_management and shift_logs tables"""
    db_path = 'instance/spa_management.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🗑️ FORCE CLEARING ALL SHIFT RECORDS...")
        print("=" * 60)
        
        # Disable foreign key constraints temporarily
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Check current record counts before deletion
        cursor.execute("SELECT COUNT(*) FROM shift_logs")
        logs_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM shift_management")
        management_count = cursor.fetchone()[0]
        
        print(f"📊 Records before deletion:")
        print(f"   - shift_logs: {logs_count}")
        print(f"   - shift_management: {management_count}")
        
        # Force delete ALL records from shift_logs
        print("\n🔥 Force deleting ALL records from shift_logs...")
        cursor.execute("DELETE FROM shift_logs")
        deleted_logs = cursor.rowcount
        print(f"✅ Force deleted {deleted_logs} records from shift_logs")
        
        # Force delete ALL records from shift_management
        print("🔥 Force deleting ALL records from shift_management...")
        cursor.execute("DELETE FROM shift_management")
        deleted_management = cursor.rowcount
        print(f"✅ Force deleted {deleted_management} records from shift_management")
        
        # Reset auto-increment counters completely
        print("🔄 Resetting auto-increment counters...")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('shift_logs', 'shift_management')")
        cursor.execute("INSERT OR REPLACE INTO sqlite_sequence (name, seq) VALUES ('shift_logs', 0)")
        cursor.execute("INSERT OR REPLACE INTO sqlite_sequence (name, seq) VALUES ('shift_management', 0)")
        
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Commit all changes
        conn.commit()
        
        # Verify complete deletion
        cursor.execute("SELECT COUNT(*) FROM shift_logs")
        remaining_logs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM shift_management")
        remaining_management = cursor.fetchone()[0]
        
        print(f"\n📊 After force deletion:")
        print(f"   - shift_logs: {remaining_logs}")
        print(f"   - shift_management: {remaining_management}")
        
        # Double check with direct queries
        cursor.execute("SELECT * FROM shift_logs LIMIT 1")
        any_logs = cursor.fetchone()
        
        cursor.execute("SELECT * FROM shift_management LIMIT 1")
        any_management = cursor.fetchone()
        
        if any_logs:
            print("⚠️ WARNING: Found remaining shift_logs records!")
        if any_management:
            print("⚠️ WARNING: Found remaining shift_management records!")
        
        conn.close()
        
        if remaining_logs == 0 and remaining_management == 0 and not any_logs and not any_management:
            print("\n✅ SUCCESS: ALL SHIFT RECORDS COMPLETELY DELETED!")
            print("🎉 Tables are now completely empty and ready for fresh data")
            return True
        else:
            print(f"\n❌ FAILURE: Some records still exist!")
            return False
        
    except Exception as e:
        print(f"❌ Error force clearing shift tables: {e}")
        return False

if __name__ == "__main__":
    print("🔥 FORCE CLEARING ALL SHIFT RECORDS...")
    print("=" * 60)
    print("⚠️ WARNING: This will permanently delete ALL shift data!")
    
    confirm = input("Type 'DELETE ALL' to confirm: ")
    
    if confirm == 'DELETE ALL':
        if force_clear_shift_tables():
            print("\n🎉 FORCE DELETION COMPLETED SUCCESSFULLY!")
            print("All shift management and shift logs records have been permanently deleted.")
            print("The tables are now completely empty.")
        else:
            print("\n❌ FORCE DELETION FAILED!")
    else:
        print("❌ Operation cancelled - confirmation text did not match")
