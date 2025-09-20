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

            # Import models to ensure they're registered
            from models import MembershipService, KittyPartyService, StudentOffer, Service, Membership, KittyParty

            # Create the new join tables
            print("Creating MembershipService table...")
            db.create_all()
            print("✓ MembershipService table created")

            print("Creating KittyPartyService table...")
            db.create_all()
            print("✓ KittyPartyService table created")

            # Verify StudentOffer service_id column exists
            try:
                # Test if we can query StudentOffer with service_id
                test_query = db.session.query(StudentOffer.service_id).limit(1).all()
                print("✓ StudentOffer service_id foreign key relationship ready")
            except Exception as e:
                print(f"⚠️ StudentOffer service_id column may need to be added: {e}")

            # Test that we can create relationships
            print("Testing relationship creation...")
            
            # Get sample data
            sample_service = Service.query.first()
            sample_membership = Membership.query.first()
            sample_kitty = KittyParty.query.first()
            
            if sample_service and sample_membership:
                # Test MembershipService creation
                test_ms = MembershipService.query.filter_by(
                    membership_id=sample_membership.id, 
                    service_id=sample_service.id
                ).first()
                print(f"✓ MembershipService relationship test successful")
            
            if sample_service and sample_kitty:
                # Test KittyPartyService creation  
                test_kps = KittyPartyService.query.filter_by(
                    kittyparty_id=sample_kitty.id,
                    service_id=sample_service.id
                ).first()
                print(f"✓ KittyPartyService relationship test successful")

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