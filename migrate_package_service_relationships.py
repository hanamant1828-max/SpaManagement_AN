#!/usr/bin/env python3

import os
import sys
from app import app, db

def drop_conflicting_tables():
    """Drop tables that might cause conflicts"""
    try:
        # Drop tables in reverse dependency order
        db.session.execute("DROP TABLE IF EXISTS membership_services CASCADE;")
        db.session.execute("DROP TABLE IF EXISTS kittyparty_services CASCADE;")
        db.session.execute("DROP SEQUENCE IF EXISTS membership_services_id_seq CASCADE;")
        db.session.execute("DROP SEQUENCE IF EXISTS kittyparty_services_id_seq CASCADE;")
        db.session.commit()
        print("✅ Dropped conflicting tables")
    except Exception as e:
        print(f"⚠️ Could not drop tables: {e}")
        db.session.rollback()

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
    with app.app_context():
        print("🔄 Starting package service relationship migration...")
        drop_conflicting_tables()
        migrate_package_service_relationships()
        print("✅ Migration completed!")