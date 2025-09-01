
#!/usr/bin/env python3
"""
Test inventory database structure and data
"""

import sqlite3
import os
from datetime import datetime

def test_inventory_database():
    """Test inventory database structure and sample data"""
    
    db_path = 'instance/spa_management.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    print("🗄️  Testing Inventory Database Structure")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Test inventory table structure
        cursor.execute("PRAGMA table_info(inventory)")
        columns = cursor.fetchall()
        
        print(f"✅ Inventory table has {len(columns)} columns:")
        for col in columns:
            print(f"  • {col[1]} ({col[2]})")
        
        # Test inventory data
        cursor.execute("SELECT COUNT(*) FROM inventory WHERE is_active = 1")
        active_count = cursor.fetchone()[0]
        print(f"\n📦 Active inventory items: {active_count}")
        
        if active_count > 0:
            # Show sample items
            cursor.execute("""
                SELECT name, current_stock, base_unit, tracking_type, category 
                FROM inventory 
                WHERE is_active = 1 
                LIMIT 5
            """)
            sample_items = cursor.fetchall()
            
            print("\n📋 Sample inventory items:")
            for item in sample_items:
                name, stock, unit, tracking, category = item
                print(f"  • {name}: {stock} {unit} ({tracking} tracking, {category})")
        
        # Test related tables
        tables_to_check = [
            'stock_movement',
            'inventory_item',
            'consumption_entry',
            'usage_duration',
            'supplier'
        ]
        
        print(f"\n🔗 Related inventory tables:")
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  • {table}: {count} records")
            except sqlite3.OperationalError:
                print(f"  • {table}: ❌ Table not found")
        
        # Test consumption tracking setup
        cursor.execute("""
            SELECT tracking_type, COUNT(*) 
            FROM inventory 
            WHERE is_active = 1 
            GROUP BY tracking_type
        """)
        tracking_types = cursor.fetchall()
        
        print(f"\n📊 Tracking types distribution:")
        for tracking_type, count in tracking_types:
            print(f"  • {tracking_type}: {count} items")
        
        print(f"\n✅ Database structure test completed successfully!")
        
    except Exception as e:
        print(f"❌ Database test error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_inventory_database()
