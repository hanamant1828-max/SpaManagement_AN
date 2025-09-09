
#!/usr/bin/env python3
"""
Migration script to create inventory locations table
Run this script to add location support to your inventory system
"""

from app import app, db
from modules.inventory.models import InventoryLocation, InventoryProduct
import sys

def create_inventory_locations_table():
    """Create the inventory locations table and update products table"""
    try:
        with app.app_context():
            print("Creating inventory location tables...")
            
            # Create all tables
            db.create_all()
            
            print("Tables created successfully!")
            
            # Initialize default locations
            from modules.inventory.queries import initialize_default_locations
            if initialize_default_locations():
                print("Default locations initialized successfully!")
            else:
                print("Default locations already exist or failed to create.")
                
            print("Migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_inventory_locations_table()
    sys.exit(0 if success else 1)
