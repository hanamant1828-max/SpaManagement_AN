
#!/usr/bin/env python3
"""
Create transaction types table for inventory management
"""

import sqlite3

def create_transaction_types_table():
    """Create transaction_types table"""
    print("🔧 Creating transaction types table...")
    
    try:
        conn = sqlite3.connect('instance/spa_management.db')
        cursor = conn.cursor()
        
        # Create transaction_types table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) UNIQUE NOT NULL,
                display_name VARCHAR(100) NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                sort_order INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert default transaction types
        default_types = [
            ('Purchase', 'Purchase', 'Items purchased from suppliers', 1, 1),
            ('Sale', 'Sale', 'Items sold to customers', 1, 2),
            ('Adjustment', 'Stock Adjustment', 'Manual stock adjustments', 1, 3),
            ('Transfer', 'Transfer', 'Stock transfers between locations', 1, 4),
            ('Return', 'Return', 'Items returned from customers', 1, 5),
            ('Treatment', 'Treatment (Facial/Service)', 'Items used in treatments', 1, 6),
            ('Waste', 'Waste/Damage', 'Items wasted or damaged', 1, 7)
        ]
        
        for type_data in default_types:
            cursor.execute("""
                INSERT OR IGNORE INTO transaction_types 
                (name, display_name, description, is_active, sort_order)
                VALUES (?, ?, ?, ?, ?)
            """, type_data)
        
        # Create stock transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simple_stock_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                transaction_type VARCHAR(50) NOT NULL,
                quantity_change FLOAT NOT NULL,
                previous_stock FLOAT,
                new_stock_level FLOAT NOT NULL,
                unit_cost FLOAT,
                total_cost FLOAT,
                user_id INTEGER,
                reason TEXT,
                reference_number VARCHAR(100),
                document_number VARCHAR(100),
                date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES simple_inventory_items (id),
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        """)
        
        # Create low stock alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simple_low_stock_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                alert_type VARCHAR(20) DEFAULT 'low_stock',
                severity VARCHAR(20) DEFAULT 'medium',
                current_stock FLOAT NOT NULL,
                minimum_stock FLOAT NOT NULL,
                priority_score INTEGER DEFAULT 50,
                is_acknowledged BOOLEAN DEFAULT 0,
                is_resolved BOOLEAN DEFAULT 0,
                acknowledged_by INTEGER,
                acknowledged_at DATETIME,
                alert_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES simple_inventory_items (id),
                FOREIGN KEY (acknowledged_by) REFERENCES user (id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Transaction types and related tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    create_transaction_types_table()
