
#!/usr/bin/env python3
"""
Verify that shift tables are cleared and check table structure
"""

import sqlite3
import os
from datetime import datetime

def verify_deletion():
    """Verify deletion and check table structure"""
    db_path = 'instance/spa_management.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking table structure and records...")
        print("=" * 60)
        
        # Check shift_management table structure
        cursor.execute("PRAGMA table_info(shift_management)")
        management_columns = cursor.fetchall()
        print("📋 shift_management table columns:")
        for col in management_columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Check shift_logs table structure  
        cursor.execute("PRAGMA table_info(shift_logs)")
        logs_columns = cursor.fetchall()
        print("\n📋 shift_logs table columns:")
        for col in logs_columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Check current record counts
        cursor.execute("SELECT COUNT(*) FROM shift_management")
        management_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM shift_logs")
        logs_count = cursor.fetchone()[0]
        
        print(f"\n📊 Current record counts:")
        print(f"   - shift_management: {management_count}")
        print(f"   - shift_logs: {logs_count}")
        
        # Check if updated_at column exists
        management_col_names = [col[1] for col in management_columns]
        has_updated_at = 'updated_at' in management_col_names
        
        print(f"\n✅ updated_at column exists: {has_updated_at}")
        
        if not has_updated_at:
            print("🔧 Adding updated_at column...")
            cursor.execute("ALTER TABLE shift_management ADD COLUMN updated_at DATETIME")
            conn.commit()
            print("✅ updated_at column added successfully")
        
        # Show any remaining records
        if management_count > 0:
            cursor.execute("SELECT * FROM shift_management")
            records = cursor.fetchall()
            print(f"\n📋 Remaining shift_management records:")
            for record in records:
                print(f"   ID: {record[0]}, Staff: {record[1]}, From: {record[2]}, To: {record[3]}")
        
        if logs_count > 0:
            cursor.execute("SELECT * FROM shift_logs LIMIT 5")
            records = cursor.fetchall()
            print(f"\n📋 Remaining shift_logs records (first 5):")
            for record in records:
                print(f"   ID: {record[0]}, Management: {record[1]}, Date: {record[2]}")
        
        conn.close()
        
        if management_count == 0 and logs_count == 0:
            print("\n✅ All shift records successfully deleted!")
            return True
        else:
            print(f"\n⚠️ Still has records: {management_count + logs_count} total")
            return False
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verifying shift table deletion and structure...")
    print("=" * 60)
    verify_deletion()
