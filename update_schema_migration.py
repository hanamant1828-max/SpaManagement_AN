#!/usr/bin/env python3
"""
Database migration script to update existing schema to match Prisma format
"""

from app import app, db
import sqlite3
from decimal import Decimal
from datetime import datetime

def migrate_service_table():
    """Migrate service table to new schema"""
    print("🔄 Migrating Service table...")
    
    # SQLite doesn't support dropping columns easily, so we'll recreate the table
    conn = sqlite3.connect('spa_management.db')
    cursor = conn.cursor()
    
    try:
        # Check if new columns exist
        cursor.execute("PRAGMA table_info(service)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'basePrice' not in columns:
            print("  Adding new columns to service table...")
            
            # Add new columns
            cursor.execute('ALTER TABLE service ADD COLUMN "basePrice" DECIMAL(10,2)')
            cursor.execute('ALTER TABLE service ADD COLUMN "durationMinutes" INTEGER')
            cursor.execute('ALTER TABLE service ADD COLUMN "active" BOOLEAN DEFAULT 1')
            
            # Copy data from old columns to new columns
            cursor.execute('''
                UPDATE service 
                SET "basePrice" = price, 
                    "durationMinutes" = duration,
                    "active" = is_active
                WHERE "basePrice" IS NULL
            ''')
            
            print("  ✅ Service table migrated successfully")
        else:
            print("  ✅ Service table already migrated")
            
    except Exception as e:
        print(f"  ❌ Error migrating service table: {e}")
    finally:
        conn.commit()
        conn.close()

def migrate_package_table():
    """Migrate package table to new schema"""
    print("🔄 Migrating Package table...")
    
    conn = sqlite3.connect('spa_management.db')
    cursor = conn.cursor()
    
    try:
        # Check if new columns exist
        cursor.execute("PRAGMA table_info(package)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'listPrice' not in columns:
            print("  Adding new columns to package table...")
            
            # Add new columns
            cursor.execute('ALTER TABLE package ADD COLUMN "listPrice" DECIMAL(10,2)')
            cursor.execute('ALTER TABLE package ADD COLUMN "discountType" VARCHAR(20) DEFAULT "NONE"')
            cursor.execute('ALTER TABLE package ADD COLUMN "discountValue" DECIMAL(10,2)')
            cursor.execute('ALTER TABLE package ADD COLUMN "totalPrice" DECIMAL(10,2)')
            cursor.execute('ALTER TABLE package ADD COLUMN "validityDays" INTEGER')
            cursor.execute('ALTER TABLE package ADD COLUMN "maxRedemptions" INTEGER')
            cursor.execute('ALTER TABLE package ADD COLUMN "targetAudience" VARCHAR(20) DEFAULT "ALL"')
            cursor.execute('ALTER TABLE package ADD COLUMN "active" BOOLEAN DEFAULT 1')
            cursor.execute('ALTER TABLE package ADD COLUMN "createdAt" DATETIME')
            cursor.execute('ALTER TABLE package ADD COLUMN "updatedAt" DATETIME')
            
            # Copy data from old columns to new columns
            cursor.execute('''
                UPDATE package 
                SET "listPrice" = total_price, 
                    "totalPrice" = total_price,
                    "validityDays" = validity_days,
                    "active" = is_active,
                    "createdAt" = created_at,
                    "updatedAt" = created_at,
                    "discountType" = CASE 
                        WHEN discount_percentage > 0 THEN "PERCENT"
                        ELSE "NONE"
                    END,
                    "discountValue" = discount_percentage
                WHERE "listPrice" IS NULL
            ''')
            
            print("  ✅ Package table migrated successfully")
        else:
            print("  ✅ Package table already migrated")
            
    except Exception as e:
        print(f"  ❌ Error migrating package table: {e}")
    finally:
        conn.commit()
        conn.close()

def create_new_tables():
    """Create new tables for Customer, CustomerPackage, and Redemption"""
    print("🔄 Creating new tables...")
    
    conn = sqlite3.connect('spa_management.db')
    cursor = conn.cursor()
    
    try:
        # Create Customer table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(120)
            )
        ''')
        
        # Create CustomerPackage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_package (
                id VARCHAR(50) PRIMARY KEY,
                "customerId" VARCHAR(50) NOT NULL,
                "packageId" VARCHAR(50) NOT NULL,
                "purchaseDate" DATETIME DEFAULT CURRENT_TIMESTAMP,
                "expiryDate" DATETIME,
                "remainingRedemptions" INTEGER,
                status VARCHAR(20) NOT NULL,
                FOREIGN KEY ("customerId") REFERENCES customer(id),
                FOREIGN KEY ("packageId") REFERENCES package(id)
            )
        ''')
        
        # Create Redemption table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS redemption (
                id VARCHAR(50) PRIMARY KEY,
                "customerPackageId" VARCHAR(50) NOT NULL,
                "serviceId" VARCHAR(50) NOT NULL,
                quantity INTEGER DEFAULT 1,
                "redeemedAt" DATETIME DEFAULT CURRENT_TIMESTAMP,
                "staffId" VARCHAR(50),
                note TEXT,
                FOREIGN KEY ("customerPackageId") REFERENCES customer_package(id),
                FOREIGN KEY ("serviceId") REFERENCES service(id)
            )
        ''')
        
        print("  ✅ New tables created successfully")
        
    except Exception as e:
        print(f"  ❌ Error creating new tables: {e}")
    finally:
        conn.commit()
        conn.close()

def run_migration():
    """Run the complete migration"""
    print("🚀 Starting database schema migration...")
    
    with app.app_context():
        # Ensure all tables exist first
        db.create_all()
        
        # Run migrations
        migrate_service_table()
        migrate_package_table()
        create_new_tables()
        
        print("\n✅ Migration completed successfully!")
        print("🎉 Database is now ready for the new Prisma-style schema!")

if __name__ == "__main__":
    run_migration()