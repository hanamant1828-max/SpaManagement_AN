
#!/usr/bin/env python3
"""
Fix simple inventory table structure
"""

import sqlite3
from datetime import datetime

def fix_simple_inventory_table():
    """Create or fix the simple_inventory_items table"""
    print("🔧 Fixing simple inventory table structure...")
    
    try:
        conn = sqlite3.connect('instance/spa_management.db')
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='simple_inventory_items'
        """)
        
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("  📝 Creating simple_inventory_items table...")
            cursor.execute("""
                CREATE TABLE simple_inventory_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sku VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    category VARCHAR(50),
                    current_stock FLOAT DEFAULT 0.0 NOT NULL,
                    minimum_stock FLOAT DEFAULT 5.0 NOT NULL,
                    unit_cost FLOAT DEFAULT 0.0,
                    location VARCHAR(100),
                    supplier VARCHAR(100),
                    expiry_date DATE,
                    is_active BOOLEAN DEFAULT 1,
                    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("  ✅ Table created successfully")
        else:
            print("  ✅ Table already exists")
            
            # Check for missing columns and add them
            cursor.execute("PRAGMA table_info(simple_inventory_items)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            
            required_columns = {
                'id', 'sku', 'name', 'description', 'category',
                'current_stock', 'minimum_stock', 'unit_cost',
                'location', 'supplier', 'expiry_date', 'is_active',
                'date_added', 'last_updated'
            }
            
            missing_columns = required_columns - existing_columns
            
            if missing_columns:
                print(f"  📝 Adding missing columns: {missing_columns}")
                
                column_definitions = {
                    'date_added': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
                    'last_updated': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
                }
                
                for column in missing_columns:
                    if column in column_definitions:
                        try:
                            cursor.execute(f"ALTER TABLE simple_inventory_items ADD COLUMN {column} {column_definitions[column]}")
                            print(f"    ✅ Added {column}")
                        except sqlite3.OperationalError as e:
                            print(f"    ⚠️  Column {column} might already exist: {e}")
            else:
                print("  ✅ All required columns exist")
        
        # Add some sample data if table is empty
        cursor.execute("SELECT COUNT(*) FROM simple_inventory_items")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("  📝 Adding sample inventory items...")
            sample_items = [
                ('SKU001', 'Facial Cleanser', 'Gentle daily cleanser', 'Skin Care', 25.0, 5.0, 15.50, 'Storage Room A', 'Beauty Supplies Co'),
                ('SKU002', 'Hair Shampoo', 'Professional grade shampoo', 'Hair Care', 18.0, 3.0, 22.00, 'Storage Room B', 'Hair Products Ltd'),
                ('SKU003', 'Massage Oil', 'Relaxing aromatherapy oil', 'Body Care', 12.0, 2.0, 35.00, 'Storage Room A', 'Wellness Supplies'),
                ('SKU004', 'Nail Polish', 'Long-lasting nail color', 'Nail Care', 30.0, 5.0, 8.50, 'Nail Station', 'Color Cosmetics Inc'),
                ('SKU005', 'Face Mask', 'Hydrating face treatment', 'Skin Care', 15.0, 3.0, 12.75, 'Treatment Room', 'Skincare Solutions')
            ]
            
            for item in sample_items:
                cursor.execute("""
                    INSERT INTO simple_inventory_items 
                    (sku, name, description, category, current_stock, minimum_stock, unit_cost, location, supplier)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, item)
            
            print(f"  ✅ Added {len(sample_items)} sample items")
        
        conn.commit()
        conn.close()
        
        print("✅ Simple inventory table structure fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing table: {e}")
        return False

if __name__ == "__main__":
    fix_simple_inventory_table()
