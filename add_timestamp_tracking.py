
#!/usr/bin/env python3
"""
Add comprehensive timestamp tracking to inventory tables
"""

import sqlite3
from datetime import datetime

def add_timestamp_tracking_columns():
    """Add timestamp tracking columns to existing tables"""
    print("🔧 Adding timestamp tracking columns...")
    
    try:
        conn = sqlite3.connect('instance/spa_management.db')
        cursor = conn.cursor()
        
        # Add columns to simple_inventory_items table
        inventory_columns = [
            "ALTER TABLE simple_inventory_items ADD COLUMN created_by INTEGER",
            "ALTER TABLE simple_inventory_items ADD COLUMN updated_by INTEGER", 
            "ALTER TABLE simple_inventory_items ADD COLUMN deleted_at DATETIME",
            "ALTER TABLE simple_inventory_items ADD COLUMN deleted_by INTEGER"
        ]
        
        for column_sql in inventory_columns:
            try:
                cursor.execute(column_sql)
                column_name = column_sql.split('ADD COLUMN')[1].split()[0]
                print(f"  ✅ Added column to inventory: {column_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"  ❌ Error adding column: {e}")
                else:
                    column_name = column_sql.split('ADD COLUMN')[1].split()[0]
                    print(f"  ⚠️  Column already exists: {column_name}")
        
        # Add columns to simple_stock_transactions table
        transaction_columns = [
            "ALTER TABLE simple_stock_transactions ADD COLUMN created_by INTEGER",
            "ALTER TABLE simple_stock_transactions ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE simple_stock_transactions ADD COLUMN updated_by INTEGER",
            "ALTER TABLE simple_stock_transactions ADD COLUMN is_active BOOLEAN DEFAULT 1",
            "ALTER TABLE simple_stock_transactions ADD COLUMN cancelled_at DATETIME",
            "ALTER TABLE simple_stock_transactions ADD COLUMN cancelled_by INTEGER",
            "ALTER TABLE simple_stock_transactions ADD COLUMN cancellation_reason VARCHAR(200)"
        ]
        
        for column_sql in transaction_columns:
            try:
                cursor.execute(column_sql)
                column_name = column_sql.split('ADD COLUMN')[1].split()[0]
                print(f"  ✅ Added column to transactions: {column_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"  ❌ Error adding column: {e}")
                else:
                    column_name = column_sql.split('ADD COLUMN')[1].split()[0]
                    print(f"  ⚠️  Column already exists: {column_name}")
        
        # Update existing records with current timestamp for created_at if it's NULL
        cursor.execute("""
            UPDATE simple_inventory_items 
            SET created_at = date_added, updated_at = last_updated
            WHERE created_at IS NULL
        """)
        
        cursor.execute("""
            UPDATE simple_stock_transactions 
            SET created_at = date_time, updated_at = date_time
            WHERE created_at IS NULL
        """)
        
        print("  ✅ Updated existing records with timestamps")
        
        conn.commit()
        conn.close()
        
        print("✅ Timestamp tracking columns added successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error adding timestamp tracking: {e}")
        return False

if __name__ == "__main__":
    add_timestamp_tracking_columns()
