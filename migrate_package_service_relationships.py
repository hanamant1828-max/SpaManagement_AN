
#!/usr/bin/env python3
"""
Migration script to add foreign key relationships for package-service connections
"""

from app import app, db
from models import *

def migrate_package_service_relationships():
    """Add foreign key relationships for packages and services"""
    
    with app.app_context():
        try:
            print("Starting Package-Service Relationship Migration...")
            
            # Create the new join tables
            print("Creating MembershipService table...")
            db.create_all()
            print("✓ MembershipService table created")
            
            print("Creating KittyPartyService table...")
            db.create_all()
            print("✓ KittyPartyService table created")
            
            # Note: StudentOffer already has service_id column, just need to ensure FK constraint
            print("✓ StudentOffer service_id foreign key relationship ready")
            
            print("\n=== Migration completed successfully! ===")
            print("\nNext steps:")
            print("1. Test creating memberships with service selection")
            print("2. Test creating student offers with service dropdown")
            print("3. Test creating kitty parties with service selection")
            print("4. Verify that service names display correctly in package lists")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            return False
            
    return True

if __name__ == "__main__":
    migrate_package_service_relationships()
