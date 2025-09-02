#!/usr/bin/env python3
"""
Create simple inventory table manually
"""

import sqlite3
import sys
from datetime import datetime

def create_inventory_table():
    """Create simple_inventory_items table with all required columns"""
    
    try:
        # Connect to database
        conn = sqlite3.connect('spa_management.db')
        cursor = conn.cursor()
        
        # Create the table with all columns
        create_sql = '''
        CREATE TABLE IF NOT EXISTS simple_inventory_items (
            id INTEGER PRIMARY KEY,
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            current_stock REAL NOT NULL DEFAULT 0.0,
            minimum_stock REAL NOT NULL DEFAULT 5.0,
            unit_cost REAL DEFAULT 0.0,
            location TEXT,
            supplier TEXT,
            expiry_date DATE,
            is_active BOOLEAN DEFAULT 1,
            is_serialized BOOLEAN DEFAULT 0,
            is_perishable BOOLEAN DEFAULT 0,
            is_hazardous BOOLEAN DEFAULT 0,
            requires_approval BOOLEAN DEFAULT 0,
            date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_counted_date DATETIME,
            last_purchase_date DATE,
            last_sale_date DATE,
            total_purchased REAL DEFAULT 0.0,
            total_sold REAL DEFAULT 0.0,
            total_adjustments REAL DEFAULT 0.0
        )
        '''
        
        cursor.execute(create_sql)
        
        # Create related tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS simple_stock_transactions (
            id INTEGER PRIMARY KEY,
            item_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            quantity REAL NOT NULL,
            notes TEXT,
            user_id INTEGER,
            date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES simple_inventory_items (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS simple_low_stock_alerts (
            id INTEGER PRIMARY KEY,
            item_id INTEGER NOT NULL,
            current_stock REAL NOT NULL,
            minimum_stock REAL NOT NULL,
            alert_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_acknowledged BOOLEAN DEFAULT 0,
            FOREIGN KEY (item_id) REFERENCES simple_inventory_items (id)
        )
        ''')
        
        # Insert some sample data
        sample_items = [
            ('SPA001', 'Premium Face Cream', 'High-quality moisturizing cream for all skin types', 'Skincare', 25.0, 5.0, 45.0, 'Storage Room A', 'Beauty Supply Co'),
            ('SPA002', 'Aromatherapy Oil - Lavender', 'Pure lavender essential oil for relaxation', 'Aromatherapy', 12.0, 3.0, 25.0, 'Essential Oils Cabinet', 'Natural Essence Ltd'),
            ('SPA003', 'Massage Towels (Pack of 10)', 'Soft cotton towels for massage therapy', 'Linens', 8.0, 2.0, 35.0, 'Linen Storage', 'Spa Supplies Inc')
        ]
        
        for item in sample_items:
            cursor.execute('''
            INSERT OR IGNORE INTO simple_inventory_items 
            (sku, name, description, category, current_stock, minimum_stock, unit_cost, location, supplier)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', item)
        
        # Commit changes
        conn.commit()
        print("✅ Tables created successfully!")
        print("📊 Added sample inventory items")
        
        return True
        
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🏗️ Creating Inventory Tables...")
    print("=" * 50)
    
    success = create_inventory_table()
    
    print("=" * 50)
    if success:
        print("✅ Tables created successfully!")
        sys.exit(0)
    else:
        print("❌ Table creation failed!")
        sys.exit(1)