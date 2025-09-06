
#!/usr/bin/env python3
"""
Script to add sample inventory items to the spa management system
"""

from app import app, db
from models import InventoryProduct, InventoryCategory, InventorySupplier
from datetime import datetime, date
import uuid

def create_sample_inventory_items():
    """Add comprehensive sample inventory items for a spa"""
    
    with app.app_context():
        try:
            # First, ensure we have categories
            categories_data = [
                {'category_name': 'Skincare Products', 'description': 'Face creams, cleansers, and skincare items'},
                {'category_name': 'Hair Care Products', 'description': 'Shampoos, conditioners, and hair treatments'},
                {'category_name': 'Massage Oils', 'description': 'Essential oils and massage products'},
                {'category_name': 'Nail Care', 'description': 'Nail polishes, treatments, and tools'},
                {'category_name': 'Equipment & Tools', 'description': 'Professional spa equipment and tools'},
                {'category_name': 'Towels & Linens', 'description': 'Towels, robes, and linen supplies'},
                {'category_name': 'Cleaning Supplies', 'description': 'Sanitizers and cleaning products'}
            ]
            
            categories = {}
            for cat_data in categories_data:
                existing_cat = InventoryCategory.query.filter_by(category_name=cat_data['category_name']).first()
                if not existing_cat:
                    category = InventoryCategory(**cat_data, is_active=True, created_at=datetime.utcnow())
                    db.session.add(category)
                    db.session.flush()
                    categories[cat_data['category_name']] = category.category_id
                    print(f"Created category: {cat_data['category_name']}")
                else:
                    categories[cat_data['category_name']] = existing_cat.category_id
                    print(f"Category already exists: {cat_data['category_name']}")
            
            # Create sample suppliers
            suppliers_data = [
                {
                    'supplier_name': 'Beauty Supplies Co.',
                    'supplier_code': 'BSC001',
                    'contact_person': 'Sarah Johnson',
                    'phone': '+91-9876543210',
                    'email': 'orders@beautysupplies.com',
                    'city': 'Mumbai',
                    'is_active': True
                },
                {
                    'supplier_name': 'Professional Spa Products',
                    'supplier_code': 'PSP002',
                    'contact_person': 'Raj Patel',
                    'phone': '+91-9876543211',
                    'email': 'sales@prospaproducts.com',
                    'city': 'Delhi',
                    'is_active': True
                },
                {
                    'supplier_name': 'Organic Wellness Ltd.',
                    'supplier_code': 'OWL003',
                    'contact_person': 'Priya Sharma',
                    'phone': '+91-9876543212',
                    'email': 'info@organicwellness.com',
                    'city': 'Bangalore',
                    'is_active': True
                }
            ]
            
            suppliers = {}
            for sup_data in suppliers_data:
                existing_sup = InventorySupplier.query.filter_by(supplier_code=sup_data['supplier_code']).first()
                if not existing_sup:
                    supplier = InventorySupplier(**sup_data, created_at=datetime.utcnow())
                    db.session.add(supplier)
                    db.session.flush()
                    suppliers[sup_data['supplier_name']] = supplier.supplier_id
                    print(f"Created supplier: {sup_data['supplier_name']}")
                else:
                    suppliers[sup_data['supplier_name']] = existing_sup.supplier_id
                    print(f"Supplier already exists: {sup_data['supplier_name']}")
            
            # Sample inventory items
            inventory_items = [
                # Skincare Products
                {
                    'name': 'Anti-Aging Face Cream',
                    'category': 'Skincare Products',
                    'supplier': 'Beauty Supplies Co.',
                    'current_stock': 25,
                    'unit': 'bottles',
                    'unit_cost': 450.00,
                    'selling_price': 650.00,
                    'reorder_level': 5,
                    'max_stock_level': 50,
                    'is_expiry_tracked': True,
                    'shelf_life_days': 730
                },
                {
                    'name': 'Vitamin C Serum',
                    'category': 'Skincare Products',
                    'supplier': 'Professional Spa Products',
                    'current_stock': 30,
                    'unit': 'bottles',
                    'unit_cost': 800.00,
                    'selling_price': 1200.00,
                    'reorder_level': 8,
                    'max_stock_level': 60,
                    'is_expiry_tracked': True,
                    'shelf_life_days': 365
                },
                {
                    'name': 'Hydrating Facial Cleanser',
                    'category': 'Skincare Products',
                    'supplier': 'Organic Wellness Ltd.',
                    'current_stock': 40,
                    'unit': 'bottles',
                    'unit_cost': 250.00,
                    'selling_price': 400.00,
                    'reorder_level': 10,
                    'max_stock_level': 80
                },
                
                # Hair Care Products
                {
                    'name': 'Keratin Hair Treatment',
                    'category': 'Hair Care Products',
                    'supplier': 'Professional Spa Products',
                    'current_stock': 15,
                    'unit': 'bottles',
                    'unit_cost': 1200.00,
                    'selling_price': 1800.00,
                    'reorder_level': 3,
                    'max_stock_level': 30,
                    'is_expiry_tracked': True,
                    'shelf_life_days': 1095
                },
                {
                    'name': 'Argan Oil Shampoo',
                    'category': 'Hair Care Products',
                    'supplier': 'Organic Wellness Ltd.',
                    'current_stock': 35,
                    'unit': 'bottles',
                    'unit_cost': 300.00,
                    'selling_price': 500.00,
                    'reorder_level': 8,
                    'max_stock_level': 70
                },
                {
                    'name': 'Deep Conditioning Hair Mask',
                    'category': 'Hair Care Products',
                    'supplier': 'Beauty Supplies Co.',
                    'current_stock': 20,
                    'unit': 'jars',
                    'unit_cost': 400.00,
                    'selling_price': 650.00,
                    'reorder_level': 5,
                    'max_stock_level': 40
                },
                
                # Massage Oils
                {
                    'name': 'Lavender Essential Oil',
                    'category': 'Massage Oils',
                    'supplier': 'Organic Wellness Ltd.',
                    'current_stock': 12,
                    'unit': 'bottles',
                    'unit_cost': 600.00,
                    'selling_price': 900.00,
                    'reorder_level': 3,
                    'max_stock_level': 25,
                    'is_expiry_tracked': True,
                    'shelf_life_days': 1460
                },
                {
                    'name': 'Hot Stone Massage Oil',
                    'category': 'Massage Oils',
                    'supplier': 'Professional Spa Products',
                    'current_stock': 18,
                    'unit': 'bottles',
                    'unit_cost': 350.00,
                    'selling_price': 550.00,
                    'reorder_level': 4,
                    'max_stock_level': 35
                },
                {
                    'name': 'Aromatherapy Blend Oil',
                    'category': 'Massage Oils',
                    'supplier': 'Organic Wellness Ltd.',
                    'current_stock': 22,
                    'unit': 'bottles',
                    'unit_cost': 500.00,
                    'selling_price': 750.00,
                    'reorder_level': 5,
                    'max_stock_level': 40
                },
                
                # Nail Care
                {
                    'name': 'Gel Nail Polish Set',
                    'category': 'Nail Care',
                    'supplier': 'Beauty Supplies Co.',
                    'current_stock': 50,
                    'unit': 'sets',
                    'unit_cost': 150.00,
                    'selling_price': 250.00,
                    'reorder_level': 15,
                    'max_stock_level': 100
                },
                {
                    'name': 'Cuticle Oil',
                    'category': 'Nail Care',
                    'supplier': 'Professional Spa Products',
                    'current_stock': 30,
                    'unit': 'bottles',
                    'unit_cost': 80.00,
                    'selling_price': 150.00,
                    'reorder_level': 10,
                    'max_stock_level': 60
                },
                {
                    'name': 'Nail Art Kit',
                    'category': 'Nail Care',
                    'supplier': 'Beauty Supplies Co.',
                    'current_stock': 8,
                    'unit': 'kits',
                    'unit_cost': 800.00,
                    'selling_price': 1200.00,
                    'reorder_level': 2,
                    'max_stock_level': 15
                },
                
                # Equipment & Tools
                {
                    'name': 'Professional Hair Dryer',
                    'category': 'Equipment & Tools',
                    'supplier': 'Professional Spa Products',
                    'current_stock': 3,
                    'unit': 'pieces',
                    'unit_cost': 3500.00,
                    'selling_price': 0.00,  # Equipment, not sold to customers
                    'reorder_level': 1,
                    'max_stock_level': 5
                },
                {
                    'name': 'Facial Steamer',
                    'category': 'Equipment & Tools',
                    'supplier': 'Professional Spa Products',
                    'current_stock': 2,
                    'unit': 'pieces',
                    'unit_cost': 5500.00,
                    'selling_price': 0.00,
                    'reorder_level': 1,
                    'max_stock_level': 4
                },
                {
                    'name': 'UV Sanitizer Cabinet',
                    'category': 'Equipment & Tools',
                    'supplier': 'Professional Spa Products',
                    'current_stock': 1,
                    'unit': 'pieces',
                    'unit_cost': 8000.00,
                    'selling_price': 0.00,
                    'reorder_level': 1,
                    'max_stock_level': 2
                },
                
                # Towels & Linens
                {
                    'name': 'Luxury Spa Towels',
                    'category': 'Towels & Linens',
                    'supplier': 'Beauty Supplies Co.',
                    'current_stock': 60,
                    'unit': 'pieces',
                    'unit_cost': 200.00,
                    'selling_price': 0.00,  # Operational use
                    'reorder_level': 20,
                    'max_stock_level': 120
                },
                {
                    'name': 'Disposable Spa Slippers',
                    'category': 'Towels & Linens',
                    'supplier': 'Beauty Supplies Co.',
                    'current_stock': 200,
                    'unit': 'pairs',
                    'unit_cost': 25.00,
                    'selling_price': 0.00,
                    'reorder_level': 50,
                    'max_stock_level': 500
                },
                {
                    'name': 'Spa Robes',
                    'category': 'Towels & Linens',
                    'supplier': 'Professional Spa Products',
                    'current_stock': 15,
                    'unit': 'pieces',
                    'unit_cost': 800.00,
                    'selling_price': 1500.00,
                    'reorder_level': 5,
                    'max_stock_level': 30
                },
                
                # Cleaning Supplies
                {
                    'name': 'Hand Sanitizer',
                    'category': 'Cleaning Supplies',
                    'supplier': 'Beauty Supplies Co.',
                    'current_stock': 25,
                    'unit': 'bottles',
                    'unit_cost': 150.00,
                    'selling_price': 250.00,
                    'reorder_level': 8,
                    'max_stock_level': 50
                },
                {
                    'name': 'Surface Disinfectant',
                    'category': 'Cleaning Supplies',
                    'supplier': 'Professional Spa Products',
                    'current_stock': 30,
                    'unit': 'bottles',
                    'unit_cost': 200.00,
                    'selling_price': 0.00,  # Operational use
                    'reorder_level': 10,
                    'max_stock_level': 60
                },
                {
                    'name': 'Equipment Sterilizer',
                    'category': 'Cleaning Supplies',
                    'supplier': 'Professional Spa Products',
                    'current_stock': 20,
                    'unit': 'bottles',
                    'unit_cost': 300.00,
                    'selling_price': 0.00,
                    'reorder_level': 5,
                    'max_stock_level': 40
                }
            ]
            
            # Add inventory items
            added_count = 0
            for item_data in inventory_items:
                # Generate unique product code
                product_code = f"SPA{str(uuid.uuid4())[:8].upper()}"
                
                # Check if item already exists
                existing_item = InventoryProduct.query.filter_by(name=item_data['name']).first()
                if existing_item:
                    print(f"Item already exists: {item_data['name']}")
                    continue
                
                # Get category and supplier IDs
                category_id = categories.get(item_data['category'])
                supplier_id = suppliers.get(item_data['supplier'])
                
                inventory_item = InventoryProduct(
                    product_code=product_code,
                    name=item_data['name'],
                    description=f"Professional spa {item_data['name'].lower()}",
                    category_id=category_id,
                    supplier_id=supplier_id,
                    current_stock=item_data['current_stock'],
                    unit=item_data['unit'],
                    unit_cost=item_data['unit_cost'],
                    cost_price=item_data['unit_cost'],  # Legacy field
                    selling_price=item_data['selling_price'],
                    reorder_level=item_data['reorder_level'],
                    min_stock_level=item_data['reorder_level'],  # Legacy field
                    max_stock_level=item_data['max_stock_level'],
                    is_expiry_tracked=item_data.get('is_expiry_tracked', False),
                    shelf_life_days=item_data.get('shelf_life_days'),
                    is_active=True,
                    created_at=datetime.utcnow(),
                    created_by='system'
                )
                
                db.session.add(inventory_item)
                added_count += 1
                print(f"Adding inventory item: {item_data['name']} - Stock: {item_data['current_stock']} {item_data['unit']}")
            
            if added_count > 0:
                db.session.commit()
                print(f"\n✅ Successfully added {added_count} inventory items to the database!")
                
                # Print summary
                total_items = InventoryProduct.query.filter_by(is_active=True).count()
                total_categories = len(categories)
                total_suppliers = len(suppliers)
                
                print(f"\n📊 Inventory Summary:")
                print(f"   - Total Active Items: {total_items}")
                print(f"   - Total Categories: {total_categories}")
                print(f"   - Total Suppliers: {total_suppliers}")
                print(f"   - Items Added This Run: {added_count}")
                
                # Calculate total inventory value
                total_value = sum(item.current_stock * item.unit_cost for item in InventoryProduct.query.filter_by(is_active=True).all())
                print(f"   - Total Inventory Value: ₹{total_value:,.2f}")
            else:
                print("\n⚠️ All inventory items already exist in the database")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding inventory items: {str(e)}")
            raise e

if __name__ == "__main__":
    create_sample_inventory_items()
