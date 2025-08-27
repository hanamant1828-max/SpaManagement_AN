#!/usr/bin/env python3
"""
Migration script to add unlimited sessions and date range support to packages
"""

from app import app, db
from sqlalchemy import text

def migrate_package_unlimited_features():
    """Add new columns for unlimited sessions and date ranges"""
    
    with app.app_context():
        print("🔄 Migrating package table for unlimited sessions and date ranges...")
        
        try:
            # Add new columns to Package table
            migrations = [
                "ALTER TABLE package ADD COLUMN has_unlimited_sessions BOOLEAN DEFAULT FALSE;",
                "ALTER TABLE package ADD COLUMN start_date DATE;",
                "ALTER TABLE package ADD COLUMN end_date DATE;",
                "ALTER TABLE package_service ADD COLUMN is_unlimited BOOLEAN DEFAULT FALSE;",
                "ALTER TABLE client_package_session ADD COLUMN is_unlimited BOOLEAN DEFAULT FALSE;"
            ]
            
            for migration in migrations:
                try:
                    db.session.execute(text(migration))
                    print(f"✓ Executed: {migration}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                        print(f"⚠️  Column already exists: {migration}")
                    else:
                        print(f"✗ Error: {migration} - {e}")
            
            db.session.commit()
            print("✅ Package table migration completed successfully!")
            
            # Test the new functionality
            print("\n🧪 Testing unlimited package creation...")
            
            from models import Package, PackageService, Service
            
            # Create a test unlimited package
            unlimited_package = Package(
                name='Unlimited Weekly Wellness Package',
                description='Unlimited wellness services for one week - perfect for retreats',
                package_type='membership',
                duration_months=1,
                validity_days=7,
                total_sessions=999,
                total_price=2999.00,
                discount_percentage=20.0,
                has_unlimited_sessions=True,
                is_active=True
            )
            
            db.session.add(unlimited_package)
            db.session.flush()
            
            # Add services with unlimited sessions
            services = Service.query.limit(2).all()
            for service in services:
                package_service = PackageService(
                    package_id=unlimited_package.id,
                    service_id=service.id,
                    sessions_included=999,
                    service_discount=15.0,
                    original_price=service.price,
                    discounted_price=service.price * 0.85,
                    is_unlimited=True
                )
                db.session.add(package_service)
            
            db.session.commit()
            
            print(f"✅ Created test unlimited package: '{unlimited_package.name}'")
            print(f"   - Package ID: {unlimited_package.id}")
            print(f"   - Has unlimited sessions: {unlimited_package.has_unlimited_sessions}")
            print(f"   - Services: {len(unlimited_package.services)} with unlimited sessions")
            
            # Also create a date range package
            from datetime import datetime, timedelta
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=30)
            
            date_range_package = Package(
                name='Monthly Premium Spa Package (Date Range)',
                description='Premium spa package valid for specific dates',
                package_type='regular',
                duration_months=1,
                validity_days=30,
                total_sessions=10,
                total_price=4500.00,
                discount_percentage=10.0,
                has_unlimited_sessions=False,
                start_date=start_date,
                end_date=end_date,
                is_active=True
            )
            
            db.session.add(date_range_package)
            db.session.commit()
            
            print(f"✅ Created test date range package: '{date_range_package.name}'")
            print(f"   - Valid from: {date_range_package.start_date}")
            print(f"   - Valid until: {date_range_package.end_date}")
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_package_unlimited_features()