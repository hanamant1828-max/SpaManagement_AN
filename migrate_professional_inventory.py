#!/usr/bin/env python3
"""
Professional Inventory Database Migration
Adds advanced columns to existing SimpleInventoryItem table
"""

import sqlite3
import sys
from datetime import datetime

def migrate_inventory_table():
    """Add professional features to existing inventory table"""
    
    try:
        # Connect to database
        conn = sqlite3.connect('spa_management.db')
        cursor = conn.cursor()
        
        # List of new columns to add
        new_columns = [
            # Basic enhancements
            ('barcode', 'TEXT'),
            ('subcategory', 'TEXT'),
            ('brand', 'TEXT'),
            
            # Advanced stock management
            ('maximum_stock', 'REAL DEFAULT 100.0'),
            ('reorder_point', 'REAL DEFAULT 10.0'),
            ('reorder_quantity', 'REAL DEFAULT 50.0'),
            
            # Multi-location support
            ('bin_location', 'TEXT'),
            ('warehouse_zone', 'TEXT'),
            
            # Advanced pricing
            ('selling_price', 'REAL'),
            ('markup_percentage', 'REAL'),
            ('discount_percentage', 'REAL'),
            ('tax_rate', 'REAL'),
            
            # Supplier enhancements
            ('supplier_code', 'TEXT'),
            ('supplier_contact', 'TEXT'),
            ('lead_time_days', 'INTEGER DEFAULT 7'),
            
            # Product details
            ('unit_of_measure', 'TEXT DEFAULT "pcs"'),
            ('weight', 'REAL'),
            ('dimensions', 'TEXT'),
            ('color', 'TEXT'),
            ('size', 'TEXT'),
            
            # Batch tracking
            ('manufacturing_date', 'DATE'),
            ('batch_number', 'TEXT'),
            ('lot_number', 'TEXT'),
            
            # Product flags
            ('is_serialized', 'BOOLEAN DEFAULT 0'),
            ('is_perishable', 'BOOLEAN DEFAULT 0'),
            ('is_hazardous', 'BOOLEAN DEFAULT 0'),
            ('requires_approval', 'BOOLEAN DEFAULT 0'),
            
            # Enhanced tracking
            ('last_purchase_date', 'DATE'),
            ('last_sale_date', 'DATE'),
            ('last_counted_date', 'DATE'),
            
            # Analytics support
            ('total_purchased', 'REAL DEFAULT 0.0'),
            ('total_sold', 'REAL DEFAULT 0.0'),
            ('total_adjustments', 'REAL DEFAULT 0.0')
        ]
        
        # Check which columns already exist
        cursor.execute("PRAGMA table_info(simple_inventory_items)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        # Add new columns that don't exist
        added_columns = []
        for column_name, column_def in new_columns:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE simple_inventory_items ADD COLUMN {column_name} {column_def}"
                    cursor.execute(sql)
                    added_columns.append(column_name)
                    print(f"✅ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"⚠️  Warning: Could not add column {column_name}: {e}")
            else:
                print(f"⏭️  Column {column_name} already exists")
        
        # Update SimpleStockTransaction table with professional features
        try:
            # Check if transaction table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='simple_stock_transactions'")
            if cursor.fetchone():
                print("\n🔄 Enhancing transaction table...")
                
                transaction_columns = [
                    ('transaction_id', 'TEXT'),
                    ('transaction_subtype', 'TEXT'),
                    ('unit_cost', 'REAL DEFAULT 0.0'),
                    ('total_cost', 'REAL DEFAULT 0.0'),
                    ('previous_stock', 'REAL DEFAULT 0.0'),
                    ('location', 'TEXT'),
                    ('department', 'TEXT'),
                    ('shift', 'TEXT'),
                    ('authorized_by', 'INTEGER'),
                    ('approval_status', 'TEXT DEFAULT "approved"'),
                    ('approval_date', 'DATETIME'),
                    ('document_number', 'TEXT'),
                    ('batch_number', 'TEXT'),
                    ('supplier_name', 'TEXT'),
                    ('customer_name', 'TEXT'),
                    ('notes', 'TEXT'),
                    ('transaction_source', 'TEXT DEFAULT "manual"'),
                    ('currency', 'TEXT DEFAULT "INR"'),
                    ('exchange_rate', 'REAL DEFAULT 1.0'),
                    ('quality_grade', 'TEXT'),
                    ('expiry_date', 'DATE'),
                    ('compliance_checked', 'BOOLEAN DEFAULT 0'),
                    ('is_adjustment', 'BOOLEAN DEFAULT 0'),
                    ('is_correction', 'BOOLEAN DEFAULT 0'),
                    ('parent_transaction_id', 'INTEGER')
                ]
                
                # Check existing transaction columns
                cursor.execute("PRAGMA table_info(simple_stock_transactions)")
                existing_trans_columns = [col[1] for col in cursor.fetchall()]
                
                for col_name, col_def in transaction_columns:
                    if col_name not in existing_trans_columns:
                        try:
                            sql = f"ALTER TABLE simple_stock_transactions ADD COLUMN {col_name} {col_def}"
                            cursor.execute(sql)
                            print(f"✅ Added transaction column: {col_name}")
                        except sqlite3.Error as e:
                            print(f"⚠️  Warning: Could not add transaction column {col_name}: {e}")
        
        except sqlite3.Error as e:
            print(f"⚠️  Warning: Transaction table enhancement failed: {e}")
        
        # Enhance alerts table
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='simple_low_stock_alerts'")
            if cursor.fetchone():
                print("\n🔄 Enhancing alerts table...")
                
                alert_columns = [
                    ('alert_id', 'TEXT'),
                    ('alert_type', 'TEXT DEFAULT "LOW_STOCK"'),
                    ('severity', 'TEXT DEFAULT "medium"'),
                    ('recommended_order_qty', 'REAL'),
                    ('first_triggered', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                    ('last_escalated', 'DATETIME'),
                    ('escalation_count', 'INTEGER DEFAULT 0'),
                    ('acknowledgment_note', 'TEXT'),
                    ('is_resolved', 'BOOLEAN DEFAULT 0'),
                    ('resolved_by', 'INTEGER'),
                    ('resolved_at', 'DATETIME'),
                    ('resolution_note', 'TEXT'),
                    ('resolution_action', 'TEXT'),
                    ('auto_reorder_enabled', 'BOOLEAN DEFAULT 0'),
                    ('reorder_triggered', 'BOOLEAN DEFAULT 0'),
                    ('reorder_date', 'DATETIME'),
                    ('purchase_order_number', 'TEXT'),
                    ('email_sent', 'BOOLEAN DEFAULT 0'),
                    ('sms_sent', 'BOOLEAN DEFAULT 0'),
                    ('notification_count', 'INTEGER DEFAULT 0')
                ]
                
                cursor.execute("PRAGMA table_info(simple_low_stock_alerts)")
                existing_alert_columns = [col[1] for col in cursor.fetchall()]
                
                for col_name, col_def in alert_columns:
                    if col_name not in existing_alert_columns:
                        try:
                            sql = f"ALTER TABLE simple_low_stock_alerts ADD COLUMN {col_name} {col_def}"
                            cursor.execute(sql)
                            print(f"✅ Added alert column: {col_name}")
                        except sqlite3.Error as e:
                            print(f"⚠️  Warning: Could not add alert column {col_name}: {e}")
        
        except sqlite3.Error as e:
            print(f"⚠️  Warning: Alert table enhancement failed: {e}")
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_inventory_barcode ON simple_inventory_items(barcode)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_category ON simple_inventory_items(category)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_supplier ON simple_inventory_items(supplier)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_expiry ON simple_inventory_items(expiry_date)",
            "CREATE INDEX IF NOT EXISTS idx_transaction_date ON simple_stock_transactions(date_time)",
            "CREATE INDEX IF NOT EXISTS idx_transaction_type ON simple_stock_transactions(transaction_type)",
            "CREATE INDEX IF NOT EXISTS idx_alert_date ON simple_low_stock_alerts(alert_date)"
        ]
        
        print("\n📊 Creating performance indexes...")
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"✅ Created index")
            except sqlite3.Error as e:
                print(f"⚠️  Index creation warning: {e}")
        
        # Commit all changes
        conn.commit()
        print(f"\n🎉 Professional inventory migration completed successfully!")
        print(f"📊 Added {len(added_columns)} new columns to inventory table")
        print(f"⚡ Enhanced database with professional features")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Starting Professional Inventory Migration...")
    print("=" * 60)
    
    success = migrate_inventory_table()
    
    print("=" * 60)
    if success:
        print("✅ Migration completed successfully!")
        print("🔄 Please restart the application to use new features")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1)