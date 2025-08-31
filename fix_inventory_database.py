#!/usr/bin/env python3
"""
Quick fix for inventory database columns
"""

import sqlite3
from app import app

def fix_inventory_table():
    """Add missing columns to inventory table"""
    
    # Connect directly to SQLite database
    db_path = 'instance/spa_management.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List of columns to add
    new_columns = [
        "ALTER TABLE inventory ADD COLUMN sku VARCHAR(50)",
        "ALTER TABLE inventory ADD COLUMN barcode VARCHAR(100)",
        "ALTER TABLE inventory ADD COLUMN max_stock_level REAL DEFAULT 100.0",
        "ALTER TABLE inventory ADD COLUMN reorder_point REAL DEFAULT 10.0", 
        "ALTER TABLE inventory ADD COLUMN reorder_quantity REAL DEFAULT 50.0",
        "ALTER TABLE inventory ADD COLUMN base_unit VARCHAR(20) DEFAULT 'pcs'",
        "ALTER TABLE inventory ADD COLUMN selling_unit VARCHAR(20) DEFAULT 'pcs'",
        "ALTER TABLE inventory ADD COLUMN conversion_factor REAL DEFAULT 1.0",
        "ALTER TABLE inventory ADD COLUMN cost_price REAL DEFAULT 0.0",
        "ALTER TABLE inventory ADD COLUMN selling_price REAL DEFAULT 0.0",
        "ALTER TABLE inventory ADD COLUMN markup_percentage REAL DEFAULT 0.0",
        "ALTER TABLE inventory ADD COLUMN item_type VARCHAR(20) DEFAULT 'consumable'",
        "ALTER TABLE inventory ADD COLUMN is_service_item BOOLEAN DEFAULT 0",
        "ALTER TABLE inventory ADD COLUMN is_retail_item BOOLEAN DEFAULT 0",
        "ALTER TABLE inventory ADD COLUMN primary_supplier_id INTEGER",
        "ALTER TABLE inventory ADD COLUMN supplier_sku VARCHAR(50)",
        "ALTER TABLE inventory ADD COLUMN has_expiry BOOLEAN DEFAULT 0",
        "ALTER TABLE inventory ADD COLUMN shelf_life_days INTEGER",
        "ALTER TABLE inventory ADD COLUMN batch_number VARCHAR(50)",
        "ALTER TABLE inventory ADD COLUMN storage_location VARCHAR(100)",
        "ALTER TABLE inventory ADD COLUMN storage_temperature VARCHAR(50)",
        "ALTER TABLE inventory ADD COLUMN storage_notes TEXT",
        "ALTER TABLE inventory ADD COLUMN enable_low_stock_alert BOOLEAN DEFAULT 1",
        "ALTER TABLE inventory ADD COLUMN enable_expiry_alert BOOLEAN DEFAULT 1",
        "ALTER TABLE inventory ADD COLUMN expiry_alert_days INTEGER DEFAULT 30",
        "ALTER TABLE inventory ADD COLUMN last_restocked_at DATETIME",
        "ALTER TABLE inventory ADD COLUMN last_counted_at DATETIME"
    ]
    
    # Add each column, ignoring errors if column already exists
    for sql in new_columns:
        try:
            cursor.execute(sql)
            column_name = sql.split("ADD COLUMN")[1].split()[0]
            print(f"✅ Added column: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                column_name = sql.split("ADD COLUMN")[1].split()[0]
                print(f"⚠️  Column already exists: {column_name}")
            else:
                print(f"❌ Error adding column: {e}")
    
    # Update existing inventory items with default values
    cursor.execute("""
        UPDATE inventory 
        SET sku = 'INV-' || PRINTF('%04d', id),
            base_unit = 'pcs',
            selling_unit = 'pcs', 
            conversion_factor = 1.0,
            item_type = 'consumable',
            is_service_item = 1,
            is_retail_item = 1
        WHERE sku IS NULL OR sku = ''
    """)
    
    # Update stock levels where not set
    cursor.execute("""
        UPDATE inventory 
        SET max_stock_level = CASE 
                WHEN current_stock * 2 > 100 THEN current_stock * 2 
                ELSE 100 
            END,
            reorder_point = CASE 
                WHEN min_stock_level > 10 THEN min_stock_level 
                ELSE 10 
            END,
            reorder_quantity = CASE 
                WHEN min_stock_level * 5 > 50 THEN min_stock_level * 5 
                ELSE 50 
            END
        WHERE max_stock_level IS NULL OR max_stock_level = 0
    """)
    
    # Set expiry flag for items with expiry dates
    cursor.execute("""
        UPDATE inventory 
        SET has_expiry = 1, shelf_life_days = 365
        WHERE expiry_date IS NOT NULL AND has_expiry IS NULL
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Inventory table updated successfully!")

if __name__ == "__main__":
    fix_inventory_table()