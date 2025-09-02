#!/usr/bin/env python3
"""
Fix Inventory Database - Add missing columns to existing table
"""

import sqlite3
import sys
from datetime import datetime

def fix_inventory_table():
    """Add missing columns to simple_inventory_items table"""
    
    try:
        # Connect to database
        conn = sqlite3.connect('spa_management.db')
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='simple_inventory_items'")
        if not cursor.fetchone():
            print("❌ Table simple_inventory_items does not exist yet")
            return False
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(simple_inventory_items)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"📊 Found {len(existing_columns)} existing columns")
        
        # List of columns that should exist
        required_columns = [
            ('is_serialized', 'BOOLEAN DEFAULT 0'),
            ('is_perishable', 'BOOLEAN DEFAULT 0'),
            ('is_hazardous', 'BOOLEAN DEFAULT 0'),
            ('requires_approval', 'BOOLEAN DEFAULT 0'),
            ('date_added', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ('last_updated', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ('last_counted_date', 'DATETIME'),
            ('last_purchase_date', 'DATE'),
            ('last_sale_date', 'DATE'),
            ('total_purchased', 'REAL DEFAULT 0.0'),
            ('total_sold', 'REAL DEFAULT 0.0'),
            ('total_adjustments', 'REAL DEFAULT 0.0')
        ]
        
        # Add missing columns
        added_count = 0
        for column_name, column_def in required_columns:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE simple_inventory_items ADD COLUMN {column_name} {column_def}"
                    cursor.execute(sql)
                    added_count += 1
                    print(f"✅ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"⚠️  Warning: Could not add column {column_name}: {e}")
            else:
                print(f"⏭️  Column {column_name} already exists")
        
        # Commit changes
        conn.commit()
        print(f"\n🎉 Database fix completed!")
        print(f"📊 Added {added_count} new columns")
        
        return True
        
    except Exception as e:
        print(f"❌ Database fix failed: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔧 Fixing Inventory Database...")
    print("=" * 50)
    
    success = fix_inventory_table()
    
    print("=" * 50)
    if success:
        print("✅ Database fix completed successfully!")
        sys.exit(0)
    else:
        print("❌ Database fix failed!")
        sys.exit(1)