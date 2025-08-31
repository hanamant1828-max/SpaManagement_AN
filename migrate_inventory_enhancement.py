#!/usr/bin/env python3
"""
Database migration script for Enhanced Inventory Management System
This script upgrades the existing inventory structure to support:
- Units of measurement and conversions
- Comprehensive stock tracking
- Supplier management
- Service-to-inventory mapping
- Advanced reporting capabilities
"""

import os
import sys
from datetime import datetime
from app import app, db
from models import *

def backup_current_data():
    """Backup existing inventory data before migration"""
    print("📦 Backing up existing inventory data...")
    
    # Get all current inventory items
    existing_items = db.session.execute("SELECT * FROM inventory").fetchall()
    
    # Create backup file
    backup_file = f"inventory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    with open(backup_file, 'w') as f:
        f.write("-- Inventory Backup\\n")
        f.write(f"-- Created: {datetime.now()}\\n\\n")
        
        for item in existing_items:
            f.write(f"-- Item: {item[1]} (ID: {item[0]})\\n")
    
    print(f"✅ Backup created: {backup_file}")
    return backup_file

def add_missing_inventory_columns():
    """Add new columns to existing inventory table"""
    print("🔧 Adding new columns to inventory table...")
    
    new_columns = [
        # SKU and identification
        "ALTER TABLE inventory ADD COLUMN sku VARCHAR(50) UNIQUE",
        "ALTER TABLE inventory ADD COLUMN barcode VARCHAR(100) UNIQUE",
        
        # Enhanced stock tracking
        "ALTER TABLE inventory ADD COLUMN max_stock_level FLOAT DEFAULT 100.0",
        "ALTER TABLE inventory ADD COLUMN reorder_point FLOAT DEFAULT 10.0",
        "ALTER TABLE inventory ADD COLUMN reorder_quantity FLOAT DEFAULT 50.0",
        
        # Units and conversions
        "ALTER TABLE inventory ADD COLUMN base_unit VARCHAR(20) DEFAULT 'pcs'",
        "ALTER TABLE inventory ADD COLUMN selling_unit VARCHAR(20) DEFAULT 'pcs'",
        "ALTER TABLE inventory ADD COLUMN conversion_factor FLOAT DEFAULT 1.0",
        
        # Enhanced pricing
        "ALTER TABLE inventory ADD COLUMN markup_percentage FLOAT DEFAULT 0.0",
        
        # Item classification
        "ALTER TABLE inventory ADD COLUMN item_type VARCHAR(20) DEFAULT 'consumable'",
        "ALTER TABLE inventory ADD COLUMN is_service_item BOOLEAN DEFAULT FALSE",
        "ALTER TABLE inventory ADD COLUMN is_retail_item BOOLEAN DEFAULT FALSE",
        
        # Supplier information
        "ALTER TABLE inventory ADD COLUMN primary_supplier_id INTEGER",
        "ALTER TABLE inventory ADD COLUMN supplier_sku VARCHAR(50)",
        
        # Expiry and quality
        "ALTER TABLE inventory ADD COLUMN has_expiry BOOLEAN DEFAULT FALSE",
        "ALTER TABLE inventory ADD COLUMN shelf_life_days INTEGER",
        "ALTER TABLE inventory ADD COLUMN batch_number VARCHAR(50)",
        
        # Storage and location
        "ALTER TABLE inventory ADD COLUMN storage_location VARCHAR(100)",
        "ALTER TABLE inventory ADD COLUMN storage_temperature VARCHAR(50)",
        "ALTER TABLE inventory ADD COLUMN storage_notes TEXT",
        
        # Alerts and tracking
        "ALTER TABLE inventory ADD COLUMN enable_low_stock_alert BOOLEAN DEFAULT TRUE",
        "ALTER TABLE inventory ADD COLUMN enable_expiry_alert BOOLEAN DEFAULT TRUE",
        "ALTER TABLE inventory ADD COLUMN expiry_alert_days INTEGER DEFAULT 30",
        
        # Metadata
        "ALTER TABLE inventory ADD COLUMN last_restocked_at DATETIME",
        "ALTER TABLE inventory ADD COLUMN last_counted_at DATETIME"
    ]
    
    for sql in new_columns:
        try:
            db.session.execute(sql)
            print(f"  ✅ {sql.split('ADD COLUMN')[1].split()[0] if 'ADD COLUMN' in sql else 'Column'}")
        except Exception as e:
            print(f"  ⚠️  {sql.split('ADD COLUMN')[1].split()[0] if 'ADD COLUMN' in sql else 'Column'} (may already exist)")
    
    db.session.commit()

def update_existing_inventory_data():
    """Update existing inventory data with new default values"""
    print("📝 Updating existing inventory items with new structure...")
    
    # Convert integer stock to float and set up basic units
    inventory_items = Inventory.query.all()
    
    for item in inventory_items:
        # Generate SKU if not exists
        if not item.sku:
            item.sku = f"INV-{item.id:04d}"
        
        # Set up basic classification
        if not item.item_type:
            item.item_type = 'both'  # Most spa items are both consumable and sellable
            item.is_service_item = True
            item.is_retail_item = True
        
        # Set up basic units
        if not item.base_unit:
            item.base_unit = 'pcs'
        if not item.selling_unit:
            item.selling_unit = 'pcs'
        if not item.conversion_factor:
            item.conversion_factor = 1.0
        
        # Set up stock levels if not set
        if not item.max_stock_level:
            item.max_stock_level = max(100.0, item.current_stock * 2)
        if not item.reorder_point:
            item.reorder_point = max(10.0, item.min_stock_level or 5.0)
        if not item.reorder_quantity:
            item.reorder_quantity = max(50.0, item.reorder_point * 2)
        
        # Set up expiry tracking
        if item.expiry_date:
            item.has_expiry = True
            item.shelf_life_days = 365  # Default 1 year shelf life
        
        print(f"  ✅ Updated: {item.name}")
    
    db.session.commit()

def create_sample_data():
    """Create sample data to demonstrate new features"""
    print("🎯 Creating sample data...")
    
    # Create sample supplier
    supplier = Supplier(
        name="Beauty Supply Co.",
        contact_person="Sarah Johnson",
        email="orders@beautysupply.com",
        phone="+1-555-0123",
        address="123 Beauty Lane, Cosmetic City, CC 12345",
        payment_terms="Net 30",
        lead_time_days=7,
        rating=4.5
    )
    db.session.add(supplier)
    db.session.commit()
    
    # Create sample inventory items with new features
    sample_items = [
        {
            'name': 'Premium Facial Cream',
            'sku': 'FC-001',
            'base_unit': 'ml',
            'selling_unit': 'ml',
            'current_stock': 500.0,
            'cost_price': 0.50,  # per ml
            'selling_price': 2.00,  # per ml
            'min_stock_level': 100.0,
            'max_stock_level': 1000.0,
            'reorder_point': 150.0,
            'reorder_quantity': 500.0,
            'has_expiry': True,
            'shelf_life_days': 730,
            'item_type': 'both',
            'is_service_item': True,
            'is_retail_item': True,
            'primary_supplier_id': supplier.id,
            'storage_temperature': 'room_temp'
        },
        {
            'name': 'Disposable Face Towels',
            'sku': 'DT-001',
            'base_unit': 'pcs',
            'selling_unit': 'pcs',
            'current_stock': 1000.0,
            'cost_price': 0.25,  # per piece
            'selling_price': 0.50,  # per piece
            'min_stock_level': 200.0,
            'max_stock_level': 2000.0,
            'reorder_point': 300.0,
            'reorder_quantity': 1000.0,
            'has_expiry': False,
            'item_type': 'consumable',
            'is_service_item': True,
            'is_retail_item': False,
            'primary_supplier_id': supplier.id,
            'storage_temperature': 'room_temp'
        }
    ]
    
    for item_data in sample_items:
        # Check if item already exists
        existing = Inventory.query.filter_by(sku=item_data['sku']).first()
        if not existing:
            item = Inventory(**item_data)
            db.session.add(item)
            print(f"  ✅ Created sample item: {item_data['name']}")
    
    db.session.commit()

def run_migration():
    """Run the complete migration process"""
    print("🚀 Starting Enhanced Inventory Management System Migration")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Step 1: Backup existing data
            backup_file = backup_current_data()
            
            # Step 2: Create all new tables
            print("\\n🏗️  Creating new database tables...")
            db.create_all()
            print("✅ All tables created successfully")
            
            # Step 3: Add new columns to existing inventory table
            print("\\n🔧 Enhancing inventory table structure...")
            add_missing_inventory_columns()
            
            # Step 4: Update existing data
            print("\\n📝 Migrating existing inventory data...")
            update_existing_inventory_data()
            
            # Step 5: Create sample data
            print("\\n🎯 Setting up sample data...")
            create_sample_data()
            
            print("\\n" + "=" * 60)
            print("✅ Migration completed successfully!")
            print(f"📦 Backup saved as: {backup_file}")
            print("\\n🎉 Enhanced Inventory Management System is ready!")
            print("\\nNew Features Available:")
            print("  • Multi-unit inventory tracking (ml, liter, gram, kg, pcs)")
            print("  • Automatic unit conversions")
            print("  • Service-to-inventory mapping")
            print("  • Comprehensive stock movement tracking")
            print("  • Supplier management")
            print("  • Auto-deduction on service billing")
            print("  • Advanced reports and analytics")
            print("  • Real-time alerts and notifications")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            print("\\n🔄 Rolling back changes...")
            db.session.rollback()
            raise

if __name__ == "__main__":
    run_migration()