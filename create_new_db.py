#!/usr/bin/env python3
"""
Create fresh database with new Prisma-style schema only
"""

from app import app, db
from models import Service, Package, PackageService, Customer, CustomerPackage, Redemption
from decimal import Decimal
from datetime import datetime, timedelta
import sqlite3

def create_fresh_database():
    """Create fresh database with only new schema models"""
    
    # Remove old database
    try:
        import os
        if os.path.exists('spa_management.db'):
            os.remove('spa_management.db')
            print("🗑️ Removed old database")
    except:
        pass
    
    # Create new database with custom schema
    conn = sqlite3.connect('spa_management.db')
    cursor = conn.cursor()
    
    try:
        print("🔨 Creating new database schema...")
        
        # Create Service table with new schema
        cursor.execute('''
            CREATE TABLE service (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                "basePrice" DECIMAL(10,2) NOT NULL,
                "durationMinutes" INTEGER NOT NULL,
                active BOOLEAN DEFAULT 1,
                description TEXT,
                category_id INTEGER,
                category VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create Package table with new schema
        cursor.execute('''
            CREATE TABLE package (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                "listPrice" DECIMAL(10,2) NOT NULL,
                "discountType" VARCHAR(20) NOT NULL,
                "discountValue" DECIMAL(10,2),
                "totalPrice" DECIMAL(10,2) NOT NULL,
                "validityDays" INTEGER,
                "maxRedemptions" INTEGER,
                "targetAudience" VARCHAR(20) NOT NULL,
                category VARCHAR(50),
                active BOOLEAN DEFAULT 1,
                "createdAt" DATETIME DEFAULT CURRENT_TIMESTAMP,
                "updatedAt" DATETIME DEFAULT CURRENT_TIMESTAMP,
                -- Legacy compatibility fields
                package_type VARCHAR(50) DEFAULT 'regular',
                duration_months INTEGER,
                validity_days INTEGER,
                total_sessions INTEGER DEFAULT 1,
                credit_amount REAL DEFAULT 0.0,
                discount_percentage REAL DEFAULT 0.0,
                student_discount REAL DEFAULT 0.0,
                min_guests INTEGER DEFAULT 1,
                membership_benefits TEXT,
                sort_order INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create PackageService table with composite primary key
        cursor.execute('''
            CREATE TABLE package_service (
                "packageId" VARCHAR(50),
                "serviceId" VARCHAR(50),
                quantity INTEGER NOT NULL,
                -- Legacy compatibility fields
                id INTEGER,
                package_id VARCHAR(50),
                service_id VARCHAR(50),
                sessions_included INTEGER,
                service_discount REAL DEFAULT 0.0,
                original_price REAL,
                discounted_price REAL,
                PRIMARY KEY ("packageId", "serviceId"),
                FOREIGN KEY ("packageId") REFERENCES package(id),
                FOREIGN KEY ("serviceId") REFERENCES service(id)
            )
        ''')
        
        # Create Customer table
        cursor.execute('''
            CREATE TABLE customer (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(120)
            )
        ''')
        
        # Create CustomerPackage table
        cursor.execute('''
            CREATE TABLE customer_package (
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
            CREATE TABLE redemption (
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
        
        conn.commit()
        print("✅ Database schema created successfully!")
        
        # Insert sample data
        print("📝 Inserting sample data...")
        
        # Sample service
        service_id = f"srv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        cursor.execute('''
            INSERT INTO service (id, name, "basePrice", "durationMinutes", active)
            VALUES (?, ?, ?, ?, ?)
        ''', (service_id, "Deep Cleansing Facial", 75.00, 60, 1))
        
        # Sample package
        package_id = f"pkg_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        cursor.execute('''
            INSERT INTO package (id, name, description, "listPrice", "discountType", 
                                "discountValue", "totalPrice", "validityDays", 
                                "maxRedemptions", "targetAudience", active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (package_id, "Wellness Package", "Complete wellness experience", 
              150.00, "PERCENT", 20.00, 120.00, 90, 3, "ALL", 1))
        
        # Package-Service relationship
        cursor.execute('''
            INSERT INTO package_service ("packageId", "serviceId", quantity)
            VALUES (?, ?, ?)
        ''', (package_id, service_id, 2))
        
        # Sample customer
        customer_id = f"cust_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        cursor.execute('''
            INSERT INTO customer (id, name, phone, email)
            VALUES (?, ?, ?, ?)
        ''', (customer_id, "Jane Doe", "+1234567890", "jane.doe@example.com"))
        
        conn.commit()
        print("✅ Sample data inserted successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_fresh_database()
    print("\n🎉 Fresh database created with Prisma-style schema!")
    print("Now you can test the new models with: python test_new_schema.py")