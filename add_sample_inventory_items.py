
#!/usr/bin/env python3
"""
Add sample inventory items to the spa management system
"""
import sqlite3
from datetime import date, timedelta
import uuid

def generate_sku(name):
    """Generate a unique SKU from item name"""
    prefix = ''.join([word[0].upper() for word in name.split()[:3]])
    suffix = str(uuid.uuid4())[:6].upper()
    return f"{prefix}-{suffix}"

def add_sample_inventory():
    """Add comprehensive sample inventory items"""
    
    # Connect to database
    db_path = 'instance/spa_management.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🎯 Adding sample inventory items...")
    
    # Sample inventory items for spa/salon
    sample_items = [
        # Hair Care Products
        {
            'name': 'Professional Shampoo 1L',
            'description': 'Premium sulfate-free shampoo for all hair types',
            'category': 'hair_care',
            'base_unit': 'ml',
            'selling_unit': 'ml',
            'current_stock': 5000.0,  # 5 liters
            'min_stock_level': 1000.0,
            'max_stock_level': 10000.0,
            'cost_price': 0.02,  # per ml
            'selling_price': 0.08,  # per ml
            'reorder_point': 1500.0,
            'reorder_quantity': 5000.0,
            'has_expiry': True,
            'expiry_date': (date.today() + timedelta(days=730)).isoformat(),
            'supplier_name': 'Professional Hair Supplies',
            'is_service_item': True,
            'is_retail_item': True,
            'item_type': 'both'
        },
        {
            'name': 'Hair Conditioner 1L',
            'description': 'Moisturizing conditioner with argan oil',
            'category': 'hair_care',
            'base_unit': 'ml',
            'selling_unit': 'ml',
            'current_stock': 3500.0,
            'min_stock_level': 500.0,
            'max_stock_level': 8000.0,
            'cost_price': 0.025,
            'selling_price': 0.10,
            'reorder_point': 1000.0,
            'reorder_quantity': 4000.0,
            'has_expiry': True,
            'expiry_date': (date.today() + timedelta(days=730)).isoformat(),
            'supplier_name': 'Professional Hair Supplies',
            'is_service_item': True,
            'is_retail_item': True,
            'item_type': 'both'
        },
        # Facial Care Products
        {
            'name': 'Vitamin C Serum 30ml',
            'description': 'Anti-aging vitamin C serum for facials',
            'category': 'skincare',
            'base_unit': 'ml',
            'selling_unit': 'ml',
            'current_stock': 500.0,
            'min_stock_level': 100.0,
            'max_stock_level': 1000.0,
            'cost_price': 2.50,
            'selling_price': 8.00,
            'reorder_point': 150.0,
            'reorder_quantity': 500.0,
            'has_expiry': True,
            'expiry_date': (date.today() + timedelta(days=365)).isoformat(),
            'supplier_name': 'Beauty World Cosmetics',
            'is_service_item': True,
            'is_retail_item': True,
            'item_type': 'both'
        },
        {
            'name': 'Clay Face Masks',
            'description': 'Detoxifying clay masks - single use',
            'category': 'skincare',
            'base_unit': 'pcs',
            'selling_unit': 'pcs',
            'current_stock': 200.0,
            'min_stock_level': 50.0,
            'max_stock_level': 500.0,
            'cost_price': 3.50,
            'selling_price': 12.00,
            'reorder_point': 75.0,
            'reorder_quantity': 200.0,
            'has_expiry': True,
            'expiry_date': (date.today() + timedelta(days=365)).isoformat(),
            'supplier_name': 'Natural Beauty Products',
            'is_service_item': True,
            'is_retail_item': False,
            'item_type': 'consumable'
        },
        # Massage Products
        {
            'name': 'Lavender Massage Oil 1L',
            'description': 'Premium lavender essential oil for massages',
            'category': 'massage',
            'base_unit': 'ml',
            'selling_unit': 'ml',
            'current_stock': 2000.0,
            'min_stock_level': 500.0,
            'max_stock_level': 5000.0,
            'cost_price': 0.05,
            'selling_price': 0.20,
            'reorder_point': 750.0,
            'reorder_quantity': 2000.0,
            'has_expiry': False,
            'supplier_name': 'Aromatherapy Supplies',
            'is_service_item': True,
            'is_retail_item': True,
            'item_type': 'both'
        },
        {
            'name': 'Hot Stone Set',
            'description': 'Professional hot stone massage set',
            'category': 'massage',
            'base_unit': 'set',
            'selling_unit': 'set',
            'current_stock': 5.0,
            'min_stock_level': 2.0,
            'max_stock_level': 10.0,
            'cost_price': 150.00,
            'selling_price': 0.00,  # Not for retail
            'reorder_point': 3.0,
            'reorder_quantity': 5.0,
            'has_expiry': False,
            'supplier_name': 'Massage Equipment Co',
            'is_service_item': True,
            'is_retail_item': False,
            'item_type': 'consumable'
        },
        # Nail Care Products
        {
            'name': 'Gel Nail Polish Set',
            'description': 'Professional gel polish - various colors',
            'category': 'nail_care',
            'base_unit': 'bottle',
            'selling_unit': 'bottle',
            'current_stock': 50.0,
            'min_stock_level': 15.0,
            'max_stock_level': 100.0,
            'cost_price': 8.00,
            'selling_price': 25.00,
            'reorder_point': 20.0,
            'reorder_quantity': 50.0,
            'has_expiry': True,
            'expiry_date': (date.today() + timedelta(days=1095)).isoformat(),
            'supplier_name': 'Nail Art Supplies',
            'is_service_item': True,
            'is_retail_item': True,
            'item_type': 'both'
        },
        {
            'name': 'Cuticle Oil 15ml',
            'description': 'Nourishing cuticle oil with vitamin E',
            'category': 'nail_care',
            'base_unit': 'ml',
            'selling_unit': 'bottle',
            'conversion_factor': 15.0,  # 15ml per bottle
            'current_stock': 300.0,  # 300ml total
            'min_stock_level': 75.0,
            'max_stock_level': 600.0,
            'cost_price': 0.50,  # per ml
            'selling_price': 2.00,  # per bottle (15ml)
            'reorder_point': 100.0,
            'reorder_quantity': 300.0,
            'has_expiry': True,
            'expiry_date': (date.today() + timedelta(days=730)).isoformat(),
            'supplier_name': 'Nail Care Essentials',
            'is_service_item': True,
            'is_retail_item': True,
            'item_type': 'both'
        },
        # Disposable Items
        {
            'name': 'Disposable Towels',
            'description': 'Soft disposable face towels',
            'category': 'disposables',
            'base_unit': 'pcs',
            'selling_unit': 'pcs',
            'current_stock': 1000.0,
            'min_stock_level': 200.0,
            'max_stock_level': 2000.0,
            'cost_price': 0.15,
            'selling_price': 0.00,  # Not for retail
            'reorder_point': 300.0,
            'reorder_quantity': 1000.0,
            'has_expiry': False,
            'supplier_name': 'Hygiene Supplies Ltd',
            'is_service_item': True,
            'is_retail_item': False,
            'item_type': 'consumable'
        },
        {
            'name': 'Latex Gloves',
            'description': 'Disposable latex gloves - medium size',
            'category': 'disposables',
            'base_unit': 'pcs',
            'selling_unit': 'box',
            'conversion_factor': 100.0,  # 100 gloves per box
            'current_stock': 500.0,  # 500 individual gloves
            'min_stock_level': 100.0,
            'max_stock_level': 1000.0,
            'cost_price': 0.08,  # per glove
            'selling_price': 0.00,  # Not for retail
            'reorder_point': 150.0,
            'reorder_quantity': 500.0,
            'has_expiry': True,
            'expiry_date': (date.today() + timedelta(days=1825)).isoformat(),
            'supplier_name': 'Medical Supplies Direct',
            'is_service_item': True,
            'is_retail_item': False,
            'item_type': 'consumable'
        },
        # Retail Products
        {
            'name': 'Premium Hand Cream 50ml',
            'description': 'Luxury hand cream with shea butter',
            'category': 'retail',
            'base_unit': 'tube',
            'selling_unit': 'tube',
            'current_stock': 75.0,
            'min_stock_level': 20.0,
            'max_stock_level': 150.0,
            'cost_price': 8.00,
            'selling_price': 24.00,
            'reorder_point': 30.0,
            'reorder_quantity': 75.0,
            'has_expiry': True,
            'expiry_date': (date.today() + timedelta(days=1095)).isoformat(),
            'supplier_name': 'Luxury Cosmetics',
            'is_service_item': False,
            'is_retail_item': True,
            'item_type': 'sellable'
        }
    ]
    
    # Insert each item
    for item in sample_items:
        # Generate SKU
        sku = generate_sku(item['name'])
        
        # Insert inventory item
        cursor.execute("""
            INSERT OR REPLACE INTO inventory (
                name, sku, description, category, base_unit, selling_unit, 
                conversion_factor, current_stock, min_stock_level, max_stock_level,
                cost_price, selling_price, reorder_point, reorder_quantity,
                has_expiry, expiry_date, supplier_name, is_service_item, 
                is_retail_item, item_type, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item['name'], sku, item['description'], item['category'],
            item['base_unit'], item['selling_unit'], 
            item.get('conversion_factor', 1.0), item['current_stock'],
            item['min_stock_level'], item['max_stock_level'],
            item['cost_price'], item['selling_price'],
            item['reorder_point'], item['reorder_quantity'],
            item['has_expiry'], item.get('expiry_date'),
            item['supplier_name'], item['is_service_item'],
            item['is_retail_item'], item['item_type'], True,
            date.today().isoformat(), date.today().isoformat()
        ))
        
        print(f"✅ Added: {item['name']} - {item['current_stock']} {item['base_unit']}")
    
    # Create some sample stock movements for demonstration
    cursor.execute("SELECT id, name FROM inventory LIMIT 5")
    inventory_items = cursor.fetchall()
    
    for item_id, item_name in inventory_items:
        # Add a purchase movement
        cursor.execute("""
            INSERT INTO stock_movement (
                inventory_id, movement_type, quantity, unit, 
                reference_type, reason, created_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id, 'purchase', 100.0, 'units',
            'purchase_order', f'Initial stock for {item_name}', 1,
            date.today().isoformat()
        ))
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Successfully added {len(sample_items)} inventory items!")
    print("\n📦 Items added include:")
    print("  • Hair care products (shampoo, conditioner)")
    print("  • Skincare items (serum, face masks)")
    print("  • Massage supplies (oils, hot stones)")
    print("  • Nail care products (polish, cuticle oil)")
    print("  • Disposable items (towels, gloves)")
    print("  • Retail products (hand cream)")
    print("\n💡 You can now view these items in your inventory management system!")

if __name__ == "__main__":
    add_sample_inventory()
