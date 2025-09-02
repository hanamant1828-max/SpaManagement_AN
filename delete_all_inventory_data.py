
#!/usr/bin/env python3
"""
Delete all inventory-related data and tables
"""

import sqlite3
import os
from datetime import datetime

def delete_all_inventory_data():
    """Delete all inventory-related data and tables"""
    
    db_path = 'instance/spa_management.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    print("🗑️  Deleting All Inventory Data")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List of inventory-related tables to drop
        inventory_tables = [
            'simple_inventory_items',
            'simple_stock_transactions', 
            'simple_low_stock_alerts',
            'transaction_types',
            'inventory',
            'inventory_master',
            'inventory_transaction',
            'stock_movement',
            'inventory_item',
            'consumption_entry',
            'usage_duration',
            'service_inventory_item',
            'purchase_order',
            'purchase_order_item',
            'inventory_adjustment',
            'product_sale',
            'supplier'
        ]
        
        # Delete all inventory-related tables
        for table in inventory_tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"  ✅ Deleted table: {table}")
            except Exception as e:
                print(f"  ⚠️  Could not delete {table}: {e}")
        
        # Clean up any remaining inventory-related data from other tables
        
        # Remove inventory references from services
        try:
            cursor.execute("UPDATE service SET inventory_deducted = 0 WHERE inventory_deducted = 1")
            print("  ✅ Cleaned service inventory references")
        except:
            print("  ⚠️  Service table not found or already clean")
        
        # Remove inventory-related appointments data
        try:
            cursor.execute("UPDATE appointment SET inventory_deducted = 0 WHERE inventory_deducted = 1")
            print("  ✅ Cleaned appointment inventory references")
        except:
            print("  ⚠️  Appointment table not found or already clean")
        
        # Remove inventory categories
        try:
            cursor.execute("DELETE FROM category WHERE category_type IN ('product', 'inventory', 'consumable')")
            print("  ✅ Deleted inventory categories")
        except:
            print("  ⚠️  Category table not found or already clean")
        
        # Remove inventory-related system settings
        try:
            cursor.execute("DELETE FROM system_setting WHERE category = 'inventory'")
            cursor.execute("DELETE FROM business_settings WHERE setting_key LIKE 'inventory_%'")
            print("  ✅ Cleaned inventory settings")
        except:
            print("  ⚠️  Settings tables not found or already clean")
        
        # Commit all changes
        conn.commit()
        print("\n✅ All inventory data deleted successfully!")
        print("🎯 Ready for fresh inventory implementation!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deleting inventory data: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚨 WARNING: This will delete ALL inventory data!")
    print("This action cannot be undone!")
    print("=" * 50)
    
    # Ask for confirmation
    confirm = input("Type 'DELETE_ALL_INVENTORY' to confirm: ")
    
    if confirm == 'DELETE_ALL_INVENTORY':
        success = delete_all_inventory_data()
        
        if success:
            print("=" * 50)
            print("✅ All inventory data deleted successfully!")
            print("📝 You can now implement your fresh inventory plan!")
        else:
            print("=" * 50)
            print("❌ Failed to delete all inventory data!")
    else:
        print("❌ Operation cancelled - confirmation text did not match")
