#!/usr/bin/env python3
"""
Upgrade database to support advanced inventory tracking
"""

import sqlite3
from datetime import datetime

def upgrade_inventory_tracking():
    """Add new columns and tables for advanced tracking"""
    
    db_path = 'instance/spa_management.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 Upgrading inventory tracking database...")
    
    try:
        # Add new columns to inventory table
        new_columns = [
            "ALTER TABLE inventory ADD COLUMN tracking_type TEXT DEFAULT 'piece_wise'",
            "ALTER TABLE inventory ADD COLUMN supports_batches BOOLEAN DEFAULT 0",
            "ALTER TABLE inventory ADD COLUMN requires_open_close BOOLEAN DEFAULT 0"
        ]
        
        for query in new_columns:
            try:
                cursor.execute(query)
                print(f"✅ Added column: {query.split('ADD COLUMN')[1].split(' ')[1]}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"⚠️  Column already exists: {query.split('ADD COLUMN')[1].split(' ')[1]}")
                else:
                    print(f"❌ Error adding column: {e}")
        
        # Create new tables for advanced tracking
        tables = [
            # Individual item instances for lifecycle tracking
            """
            CREATE TABLE IF NOT EXISTS inventory_item (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER NOT NULL,
                item_code TEXT UNIQUE NOT NULL,
                batch_number TEXT,
                expiry_date DATE,
                status TEXT DEFAULT 'in_stock',
                quantity REAL NOT NULL,
                remaining_quantity REAL NOT NULL,
                issued_at DATETIME,
                issued_by INTEGER,
                consumed_at DATETIME,
                consumed_by INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inventory_id) REFERENCES inventory(id),
                FOREIGN KEY (issued_by) REFERENCES user(id),
                FOREIGN KEY (consumed_by) REFERENCES user(id)
            )
            """,
            
            # Consumption entries for all tracking types
            """
            CREATE TABLE IF NOT EXISTS consumption_entry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER NOT NULL,
                inventory_item_id INTEGER,
                entry_type TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                reason TEXT NOT NULL,
                notes TEXT,
                reference_id INTEGER,
                reference_type TEXT,
                created_by INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                batch_number TEXT,
                cost_impact REAL DEFAULT 0.0,
                FOREIGN KEY (inventory_id) REFERENCES inventory(id),
                FOREIGN KEY (inventory_item_id) REFERENCES inventory_item(id),
                FOREIGN KEY (created_by) REFERENCES user(id)
            )
            """,
            
            # Usage duration tracking
            """
            CREATE TABLE IF NOT EXISTS usage_duration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER NOT NULL,
                inventory_item_id INTEGER,
                opened_at DATETIME NOT NULL,
                finished_at DATETIME,
                duration_hours REAL,
                opened_by INTEGER NOT NULL,
                finished_by INTEGER,
                FOREIGN KEY (inventory_id) REFERENCES inventory(id),
                FOREIGN KEY (inventory_item_id) REFERENCES inventory_item(id),
                FOREIGN KEY (opened_by) REFERENCES user(id),
                FOREIGN KEY (finished_by) REFERENCES user(id)
            )
            """
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
            table_name = table_sql.split('CREATE TABLE IF NOT EXISTS')[1].split('(')[0].strip()
            print(f"✅ Created table: {table_name}")
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_inventory_item_inventory_id ON inventory_item(inventory_id)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_item_status ON inventory_item(status)",
            "CREATE INDEX IF NOT EXISTS idx_consumption_entry_inventory_id ON consumption_entry(inventory_id)",
            "CREATE INDEX IF NOT EXISTS idx_consumption_entry_type ON consumption_entry(entry_type)",
            "CREATE INDEX IF NOT EXISTS idx_consumption_entry_created_at ON consumption_entry(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_usage_duration_inventory_id ON usage_duration(inventory_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
            index_name = index_sql.split('CREATE INDEX IF NOT EXISTS')[1].split(' ON')[0].strip()
            print(f"✅ Created index: {index_name}")
        
        # Update existing inventory with tracking types
        updates = [
            # Set container/lifecycle tracking for bottles, jars, tubes
            """UPDATE inventory 
               SET tracking_type = 'container_lifecycle', 
                   requires_open_close = 1, 
                   supports_batches = 1 
               WHERE LOWER(name) LIKE '%bottle%' 
                  OR LOWER(name) LIKE '%jar%' 
                  OR LOWER(name) LIKE '%tube%'
                  OR LOWER(name) LIKE '%serum%'
                  OR LOWER(name) LIKE '%cream%'
                  OR LOWER(name) LIKE '%lotion%'""",
            
            # Set piece-wise tracking for towels, masks, pads
            """UPDATE inventory 
               SET tracking_type = 'piece_wise' 
               WHERE LOWER(name) LIKE '%towel%' 
                  OR LOWER(name) LIKE '%mask%' 
                  OR LOWER(name) LIKE '%pad%'
                  OR LOWER(name) LIKE '%cotton%'
                  OR base_unit = 'pcs'""",
            
            # Set manual entry for special items
            """UPDATE inventory 
               SET tracking_type = 'manual_entry' 
               WHERE LOWER(name) LIKE '%custom%' 
                  OR LOWER(name) LIKE '%special%'"""
        ]
        
        for update_sql in updates:
            cursor.execute(update_sql)
            rows_affected = cursor.rowcount
            print(f"✅ Updated {rows_affected} inventory items with tracking types")
        
        conn.commit()
        print("\\n🎉 Database upgrade completed successfully!")
        
        # Show summary
        cursor.execute("SELECT tracking_type, COUNT(*) FROM inventory GROUP BY tracking_type")
        tracking_summary = cursor.fetchall()
        
        print("\\n📊 Tracking Type Summary:")
        for tracking_type, count in tracking_summary:
            print(f"  • {tracking_type}: {count} items")
        
    except Exception as e:
        print(f"❌ Error during database upgrade: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    upgrade_inventory_tracking()