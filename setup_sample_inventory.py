#!/usr/bin/env python3
"""
Setup sample inventory data to demonstrate usage
"""

import sqlite3
from datetime import date, timedelta

def create_sample_data():
    """Create sample inventory and tracking data"""
    
    # Connect to database
    db_path = 'instance/spa_management.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create sample supplier
    cursor.execute("""
        INSERT OR IGNORE INTO supplier (
            name, contact_person, email, phone, payment_terms, lead_time_days, rating, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'Beauty World Supplies', 'Maria Garcia', 'orders@beautyworld.com', 
        '+1-555-9876', 'Net 30', 5, 4.8, 1
    ))
    
    supplier_id = cursor.lastrowid
    
    # Sample inventory items with different units and use cases
    sample_items = [
        # Serum - measured in ml, used 2ml per facial
        {
            'name': 'Premium Anti-Aging Serum',
            'sku': 'SER-001',
            'description': 'Vitamin C serum for facials',
            'base_unit': 'ml',
            'selling_unit': 'ml',
            'current_stock': 500.0,
            'cost_price': 1.50,
            'selling_price': 4.00,
            'min_stock_level': 50.0,
            'reorder_point': 100.0,
            'item_type': 'both',
            'is_service_item': 1,
            'is_retail_item': 1,
            'primary_supplier_id': supplier_id
        },
        # Face masks - counted in pieces, 1 per facial
        {
            'name': 'Organic Clay Face Masks',
            'sku': 'MSK-001', 
            'description': 'Single-use organic masks',
            'base_unit': 'pcs',
            'selling_unit': 'pcs',
            'current_stock': 150.0,
            'cost_price': 2.50,
            'selling_price': 8.00,
            'min_stock_level': 30.0,
            'reorder_point': 50.0,
            'item_type': 'both',
            'is_service_item': 1,
            'is_retail_item': 1,
            'primary_supplier_id': supplier_id
        },
        # Massage oil - stored in liters, used in ml
        {
            'name': 'Lavender Massage Oil',
            'sku': 'OIL-001',
            'description': 'Pure lavender oil for massages',
            'base_unit': 'liter',
            'selling_unit': 'ml',
            'conversion_factor': 1000.0,  # 1 liter = 1000 ml
            'current_stock': 3.5,  # 3.5 liters
            'cost_price': 30.00,   # per liter
            'selling_price': 0.20,  # per ml
            'min_stock_level': 1.0,
            'reorder_point': 2.0,
            'item_type': 'consumable',
            'is_service_item': 1,
            'is_retail_item': 0,
            'primary_supplier_id': supplier_id
        },
        # Disposable towels - bulk purchase in kg, used by pieces
        {
            'name': 'Disposable Face Towels',
            'sku': 'TWL-001',
            'description': 'Soft disposable towels',
            'base_unit': 'pcs',
            'selling_unit': 'pcs', 
            'current_stock': 800.0,
            'cost_price': 0.15,
            'selling_price': 0.50,
            'min_stock_level': 100.0,
            'reorder_point': 200.0,
            'item_type': 'consumable',
            'is_service_item': 1,
            'is_retail_item': 0,
            'primary_supplier_id': supplier_id
        }
    ]
    
    # Insert sample inventory items
    for item in sample_items:
        cursor.execute("""
            INSERT OR REPLACE INTO inventory (
                name, sku, description, base_unit, selling_unit, conversion_factor,
                current_stock, cost_price, selling_price, min_stock_level, reorder_point,
                item_type, is_service_item, is_retail_item, primary_supplier_id,
                is_active, category
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item['name'], item['sku'], item['description'], 
            item['base_unit'], item['selling_unit'], item.get('conversion_factor', 1.0),
            item['current_stock'], item['cost_price'], item['selling_price'],
            item['min_stock_level'], item['reorder_point'],
            item['item_type'], item['is_service_item'], item['is_retail_item'],
            item['primary_supplier_id'], 1, 'skincare'
        ))
        print(f"✅ Added: {item['name']} - {item['current_stock']} {item['base_unit']}")
    
    # Now let's create service-to-inventory mappings
    # First, get service IDs
    cursor.execute("SELECT id, name FROM service WHERE name LIKE '%facial%' OR name LIKE '%massage%' LIMIT 3")
    services = cursor.fetchall()
    
    # Get inventory IDs we just created
    cursor.execute("SELECT id, name, sku FROM inventory WHERE sku IN ('SER-001', 'MSK-001', 'OIL-001', 'TWL-001')")
    inventory_items = cursor.fetchall()
    
    if services and inventory_items:
        # Map "Facial" service to inventory consumption
        facial_service_id = services[0][0]  # Assume first service is facial
        
        # Define what a facial consumes
        facial_consumption = [
            {'sku': 'SER-001', 'quantity': 2.0, 'unit': 'ml'},    # 2ml serum
            {'sku': 'MSK-001', 'quantity': 1.0, 'unit': 'pcs'},   # 1 mask
            {'sku': 'TWL-001', 'quantity': 3.0, 'unit': 'pcs'},   # 3 towels
        ]
        
        for consumption in facial_consumption:
            # Find inventory item
            inventory_item = next((item for item in inventory_items if item[2] == consumption['sku']), None)
            if inventory_item:
                cursor.execute("""
                    INSERT OR REPLACE INTO service_inventory_item (
                        service_id, inventory_id, quantity_per_service, unit, notes
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    facial_service_id, inventory_item[0], 
                    consumption['quantity'], consumption['unit'],
                    f"Consumed per facial service"
                ))
                print(f"✅ Mapped: {inventory_item[1]} -> Facial service ({consumption['quantity']} {consumption['unit']})")
        
        # Map massage service to oil consumption
        if len(services) > 1:
            massage_service_id = services[1][0]
            oil_item = next((item for item in inventory_items if item[2] == 'OIL-001'), None)
            towel_item = next((item for item in inventory_items if item[2] == 'TWL-001'), None)
            
            if oil_item:
                cursor.execute("""
                    INSERT OR REPLACE INTO service_inventory_item (
                        service_id, inventory_id, quantity_per_service, unit, notes
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    massage_service_id, oil_item[0], 15.0, 'ml',
                    "Oil consumed per massage"
                ))
                print(f"✅ Mapped: {oil_item[1]} -> Massage service (15.0 ml)")
            
            if towel_item:
                cursor.execute("""
                    INSERT OR REPLACE INTO service_inventory_item (
                        service_id, inventory_id, quantity_per_service, unit, notes
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    massage_service_id, towel_item[0], 2.0, 'pcs',
                    "Towels used per massage"
                ))
                print(f"✅ Mapped: {towel_item[1]} -> Massage service (2.0 pcs)")
    
    conn.commit()
    conn.close()
    
    print("\\n🎉 Sample inventory data created successfully!")
    print("\\n📋 What was created:")
    print("  • 1 Supplier: Beauty World Supplies")
    print("  • 4 Inventory items with different units (ml, pcs, liter)")
    print("  • Service-to-inventory mappings for automatic deduction")
    print("\\n🔧 Now you can:")
    print("  1. View inventory in the web interface")
    print("  2. Test automatic stock deduction on service completion")
    print("  3. Try the API endpoints for reports and tracking")

if __name__ == "__main__":
    create_sample_data()