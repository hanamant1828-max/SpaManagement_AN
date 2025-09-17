
#!/usr/bin/env python3
"""
Migration script to update inventory_locations table constraints
Changes from unique constraint on 'name' to composite unique constraint on 'name' and 'type'
"""

from app import app, db
from modules.inventory.models import InventoryLocation
import sys

def migrate_location_constraints():
    """Update location table constraints"""
    try:
        with app.app_context():
            print("Migrating inventory_locations table constraints...")
            
            # Check if we're using SQLite (common in development)
            if 'sqlite' in str(db.engine.url):
                print("SQLite detected - recreating table with new constraints...")
                
                # SQLite doesn't support dropping constraints directly
                # We need to recreate the table
                
                # First, let's backup existing data
                existing_locations = InventoryLocation.query.all()
                location_data = []
                
                for loc in existing_locations:
                    location_data.append({
                        'id': loc.id,
                        'name': loc.name,
                        'type': loc.type,
                        'address': loc.address,
                        'contact_person': loc.contact_person,
                        'phone': loc.phone,
                        'status': loc.status,
                        'created_at': loc.created_at,
                        'updated_at': loc.updated_at
                    })
                
                print(f"Backed up {len(location_data)} locations")
                
                # Drop and recreate the table
                InventoryLocation.__table__.drop(db.engine)
                InventoryLocation.__table__.create(db.engine)
                
                # Restore data
                for loc_data in location_data:
                    new_location = InventoryLocation(**loc_data)
                    db.session.add(new_location)
                
                db.session.commit()
                print(f"Restored {len(location_data)} locations with new constraints")
                
            else:
                print("PostgreSQL/MySQL detected - using ALTER TABLE...")
                
                # For PostgreSQL/MySQL, we can use ALTER TABLE
                db.engine.execute("ALTER TABLE inventory_locations DROP CONSTRAINT IF EXISTS inventory_locations_name_key")
                db.engine.execute("ALTER TABLE inventory_locations ADD CONSTRAINT _name_type_uc UNIQUE (name, type)")
                
                print("Updated constraints using ALTER TABLE")
            
            print("✅ Migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    success = migrate_location_constraints()
    sys.exit(0 if success else 1)
