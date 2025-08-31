#!/usr/bin/env python3
"""
Quick fix for appointment database column
"""

import sqlite3

def fix_appointment_table():
    """Add missing inventory_deducted column to appointment table"""
    
    # Connect directly to SQLite database
    db_path = 'instance/spa_management.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE appointment ADD COLUMN inventory_deducted BOOLEAN DEFAULT 0")
        print("✅ Added inventory_deducted column to appointment table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("⚠️  Column inventory_deducted already exists in appointment table")
        else:
            print(f"❌ Error adding column: {e}")
    
    conn.commit()
    conn.close()
    print("✅ Appointment table updated successfully!")

if __name__ == "__main__":
    fix_appointment_table()