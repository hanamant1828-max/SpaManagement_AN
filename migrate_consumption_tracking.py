
#!/usr/bin/env python3
"""
Migration script to add consumption tracking tables
"""

from app import app, db
from models import ConsumptionEntry, UsageDuration, InventoryItem
import sqlite3

def migrate_consumption_tracking():
    """Add consumption tracking tables"""
    
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            print("✅ Consumption tracking tables created successfully!")
            
            # Check if tables exist
            db_path = 'instance/spa_management.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check for consumption_entry table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='consumption_entry'")
            if cursor.fetchone():
                print("✅ consumption_entry table exists")
            else:
                print("❌ consumption_entry table missing")
            
            # Check for usage_duration table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usage_duration'")
            if cursor.fetchone():
                print("✅ usage_duration table exists")
            else:
                print("❌ usage_duration table missing")
            
            # Check for inventory_item table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventory_item'")
            if cursor.fetchone():
                print("✅ inventory_item table exists")
            else:
                print("❌ inventory_item table missing")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error creating consumption tracking tables: {e}")
            return False
    
    return True

if __name__ == "__main__":
    migrate_consumption_tracking()
