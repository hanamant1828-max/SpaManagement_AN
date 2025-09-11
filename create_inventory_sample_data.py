#!/usr/bin/env python3
"""
Create comprehensive sample inventory data for spa/salon business
"""
import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from modules.inventory.models import (
    InventoryCategory, InventoryLocation, InventoryProduct, 
    InventoryBatch, InventoryAuditLog
)
from models import User

def create_sample_categories():
    """Create sample inventory categories for spa/salon"""
    categories_data = [
        {
            'name': 'Hair Care Products',
            'description': 'Shampoos, conditioners, hair treatments, styling products',
            'color_code': '#FF6B6B'
        },
        {
            'name': 'Skin Care Products', 
            'description': 'Facial cleansers, moisturizers, serums, masks',
            'color_code': '#4ECDC4'
        },
        {
            'name': 'Body Care Products',
            'description': 'Body lotions, scrubs, oils, massage products',
            'color_code': '#45B7D1'
        },
        {
            'name': 'Nail Care Products',
            'description': 'Nail polishes, base coats, top coats, nail treatments',
            'color_code': '#F39C12'
        },
        {
            'name': 'Spa Equipment',
            'description': 'Towels, robes, disposable items, tools',
            'color_code': '#9B59B6'
        },
        {
            'name': 'Essential Oils',
            'description': 'Aromatherapy oils, carrier oils, fragrance oils',
            'color_code': '#27AE60'
        },
        {
            'name': 'Makeup Products',
            'description': 'Foundation, lipstick, eyeshadow, makeup tools',
            'color_code': '#E74C3C'
        },
        {
            'name': 'Cleaning Supplies',
            'description': 'Disinfectants, cleaning tools, sanitizers',
            'color_code': '#34495E'
        }
    ]
    
    created_categories = []
    for cat_data in categories_data:
        existing = InventoryCategory.query.filter_by(name=cat_data['name']).first()
        if not existing:
            category = InventoryCategory(**cat_data)
            db.session.add(category)
            created_categories.append(category)
            print(f"✅ Created category: {cat_data['name']}")
        else:
            created_categories.append(existing)
            print(f"ℹ️  Category already exists: {cat_data['name']}")
    
    db.session.commit()
    return created_categories

def create_sample_locations():
    """Create sample inventory locations"""
    locations_data = [
        {
            'id': 'MAIN_STORE',
            'name': 'Main Store Front',
            'type': 'branch',
            'address': '123 Beauty Street, Wellness District',
            'contact_person': 'Sarah Johnson',
            'phone': '+1-555-0101'
        },
        {
            'id': 'WAREHOUSE',
            'name': 'Storage Warehouse',
            'type': 'warehouse', 
            'address': '456 Storage Ave, Industrial Area',
            'contact_person': 'Mike Chen',
            'phone': '+1-555-0102'
        },
        {
            'id': 'SERVICE_ROOM_1',
            'name': 'Treatment Room 1',
            'type': 'room',
            'address': 'Main Floor, Room 101',
            'contact_person': 'Lisa Martinez',
            'phone': '+1-555-0103'
        },
        {
            'id': 'SERVICE_ROOM_2',
            'name': 'Treatment Room 2', 
            'type': 'room',
            'address': 'Main Floor, Room 102',
            'contact_person': 'Emma Davis',
            'phone': '+1-555-0104'
        },
        {
            'id': 'NAIL_STATION',
            'name': 'Nail Care Station',
            'type': 'room',
            'address': 'Main Floor, Nail Area',
            'contact_person': 'Jessica Brown',
            'phone': '+1-555-0105'
        },
        {
            'id': 'HAIR_SALON',
            'name': 'Hair Salon Area',
            'type': 'room',
            'address': 'Second Floor, Hair Section',
            'contact_person': 'David Wilson',
            'phone': '+1-555-0106'
        }
    ]
    
    created_locations = []
    for loc_data in locations_data:
        existing = InventoryLocation.query.get(loc_data['id'])
        if not existing:
            location = InventoryLocation(**loc_data)
            db.session.add(location)
            created_locations.append(location)
            print(f"✅ Created location: {loc_data['name']}")
        else:
            created_locations.append(existing)
            print(f"ℹ️  Location already exists: {loc_data['name']}")
    
    db.session.commit()
    return created_locations

def create_sample_products(categories):
    """Create sample products for each category"""
    products_data = {
        'Hair Care Products': [
            {'name': 'Premium Argan Oil Shampoo', 'sku': 'HC001', 'description': 'Nourishing shampoo with argan oil for dry hair', 'unit_of_measure': 'ml'},
            {'name': 'Keratin Repair Conditioner', 'sku': 'HC002', 'description': 'Deep conditioning treatment with keratin', 'unit_of_measure': 'ml'},
            {'name': 'Volumizing Hair Mousse', 'sku': 'HC003', 'description': 'Lightweight mousse for volume and hold', 'unit_of_measure': 'ml'},
            {'name': 'Heat Protection Spray', 'sku': 'HC004', 'description': 'Thermal protection for heat styling', 'unit_of_measure': 'ml'},
            {'name': 'Hair Growth Serum', 'sku': 'HC005', 'description': 'Intensive serum to promote hair growth', 'unit_of_measure': 'ml'}
        ],
        'Skin Care Products': [
            {'name': 'Gentle Foaming Cleanser', 'sku': 'SC001', 'description': 'Daily facial cleanser for all skin types', 'unit_of_measure': 'ml'},
            {'name': 'Vitamin C Brightening Serum', 'sku': 'SC002', 'description': 'Anti-aging serum with vitamin C', 'unit_of_measure': 'ml'},
            {'name': 'Hyaluronic Acid Moisturizer', 'sku': 'SC003', 'description': 'Hydrating face cream with hyaluronic acid', 'unit_of_measure': 'ml'},
            {'name': 'Clay Purifying Mask', 'sku': 'SC004', 'description': 'Deep cleaning clay mask for oily skin', 'unit_of_measure': 'g'},
            {'name': 'Retinol Night Cream', 'sku': 'SC005', 'description': 'Anti-aging night cream with retinol', 'unit_of_measure': 'ml'}
        ],
        'Body Care Products': [
            {'name': 'Lavender Body Lotion', 'sku': 'BC001', 'description': 'Relaxing body lotion with lavender', 'unit_of_measure': 'ml'},
            {'name': 'Sea Salt Body Scrub', 'sku': 'BC002', 'description': 'Exfoliating scrub with sea salt', 'unit_of_measure': 'g'},
            {'name': 'Massage Oil Blend', 'sku': 'BC003', 'description': 'Premium massage oil with essential oils', 'unit_of_measure': 'ml'},
            {'name': 'Shea Butter Hand Cream', 'sku': 'BC004', 'description': 'Intensive hand cream with shea butter', 'unit_of_measure': 'ml'},
            {'name': 'Anti-Cellulite Gel', 'sku': 'BC005', 'description': 'Firming gel for body contouring', 'unit_of_measure': 'ml'}
        ],
        'Nail Care Products': [
            {'name': 'Base Coat Nail Polish', 'sku': 'NC001', 'description': 'Clear base coat for nail protection', 'unit_of_measure': 'ml'},
            {'name': 'Classic Red Nail Polish', 'sku': 'NC002', 'description': 'Long-lasting red nail polish', 'unit_of_measure': 'ml'},
            {'name': 'Quick Dry Top Coat', 'sku': 'NC003', 'description': 'Fast-drying glossy top coat', 'unit_of_measure': 'ml'},
            {'name': 'Cuticle Oil Treatment', 'sku': 'NC004', 'description': 'Nourishing oil for cuticle care', 'unit_of_measure': 'ml'},
            {'name': 'Nail Strengthener', 'sku': 'NC005', 'description': 'Treatment for weak and brittle nails', 'unit_of_measure': 'ml'}
        ],
        'Spa Equipment': [
            {'name': 'Luxury Bath Towels', 'sku': 'SE001', 'description': 'Premium cotton bath towels', 'unit_of_measure': 'pcs'},
            {'name': 'Disposable Face Masks', 'sku': 'SE002', 'description': 'Single-use face masks for treatments', 'unit_of_measure': 'pcs'},
            {'name': 'Bamboo Facial Brushes', 'sku': 'SE003', 'description': 'Eco-friendly facial cleansing brushes', 'unit_of_measure': 'pcs'},
            {'name': 'Spa Headbands', 'sku': 'SE004', 'description': 'Soft headbands for treatments', 'unit_of_measure': 'pcs'},
            {'name': 'Massage Stones Set', 'sku': 'SE005', 'description': 'Hot stone massage therapy set', 'unit_of_measure': 'set'}
        ],
        'Essential Oils': [
            {'name': 'Pure Lavender Essential Oil', 'sku': 'EO001', 'description': '100% pure lavender oil for relaxation', 'unit_of_measure': 'ml'},
            {'name': 'Eucalyptus Essential Oil', 'sku': 'EO002', 'description': 'Refreshing eucalyptus oil', 'unit_of_measure': 'ml'},
            {'name': 'Tea Tree Essential Oil', 'sku': 'EO003', 'description': 'Antibacterial tea tree oil', 'unit_of_measure': 'ml'},
            {'name': 'Rose Essential Oil', 'sku': 'EO004', 'description': 'Luxurious rose oil for anti-aging', 'unit_of_measure': 'ml'},
            {'name': 'Jojoba Carrier Oil', 'sku': 'EO005', 'description': 'Premium carrier oil for blending', 'unit_of_measure': 'ml'}
        ],
        'Makeup Products': [
            {'name': 'HD Foundation Light', 'sku': 'MU001', 'description': 'High-definition foundation in light shade', 'unit_of_measure': 'ml'},
            {'name': 'HD Foundation Medium', 'sku': 'MU002', 'description': 'High-definition foundation in medium shade', 'unit_of_measure': 'ml'},
            {'name': 'Long-Wear Lipstick', 'sku': 'MU003', 'description': 'Long-lasting matte lipstick', 'unit_of_measure': 'pcs'},
            {'name': 'Eyeshadow Palette', 'sku': 'MU004', 'description': 'Professional eyeshadow palette', 'unit_of_measure': 'pcs'},
            {'name': 'Makeup Brush Set', 'sku': 'MU005', 'description': 'Professional makeup brush collection', 'unit_of_measure': 'set'}
        ],
        'Cleaning Supplies': [
            {'name': 'Surface Disinfectant', 'sku': 'CS001', 'description': 'Hospital-grade surface disinfectant', 'unit_of_measure': 'ml'},
            {'name': 'Hand Sanitizer Gel', 'sku': 'CS002', 'description': '70% alcohol hand sanitizer', 'unit_of_measure': 'ml'},
            {'name': 'Equipment Cleaning Wipes', 'sku': 'CS003', 'description': 'Disinfecting wipes for equipment', 'unit_of_measure': 'pcs'},
            {'name': 'Floor Cleaner Concentrate', 'sku': 'CS004', 'description': 'Concentrated floor cleaning solution', 'unit_of_measure': 'ml'},
            {'name': 'Glass Cleaner Spray', 'sku': 'CS005', 'description': 'Streak-free glass and mirror cleaner', 'unit_of_measure': 'ml'}
        ]
    }
    
    created_products = []
    category_dict = {cat.name: cat for cat in categories}
    
    for category_name, products in products_data.items():
        category = category_dict.get(category_name)
        if not category:
            print(f"⚠️  Category not found: {category_name}")
            continue
            
        for product_data in products:
            existing = InventoryProduct.query.filter_by(sku=product_data['sku']).first()
            if not existing:
                product = InventoryProduct(
                    sku=product_data['sku'],
                    name=product_data['name'],
                    description=product_data['description'],
                    unit_of_measure=product_data['unit_of_measure'],
                    category_id=category.id,
                    is_service_item=True,
                    is_retail_item=True,
                    is_active=True
                )
                db.session.add(product)
                created_products.append(product)
                print(f"✅ Created product: {product_data['name']}")
            else:
                created_products.append(existing)
                print(f"ℹ️  Product already exists: {product_data['name']}")
    
    db.session.commit()
    return created_products

def create_sample_batches(products, locations):
    """Create sample batches with stock for all products"""
    import random
    from datetime import datetime, date, timedelta
    
    created_batches = []
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        print("⚠️  Admin user not found, creating batches without user reference")
        admin_user_id = None
    else:
        admin_user_id = admin_user.id
    
    # Distribution of products across locations
    location_weights = {
        'WAREHOUSE': 0.4,      # 40% of stock in warehouse
        'MAIN_STORE': 0.3,     # 30% in main store
        'SERVICE_ROOM_1': 0.1, # 10% in service rooms
        'SERVICE_ROOM_2': 0.1,
        'NAIL_STATION': 0.05,
        'HAIR_SALON': 0.05
    }
    
    for product in products:
        # Create 2-4 batches per product
        num_batches = random.randint(2, 4)
        
        for i in range(num_batches):
            # Generate batch dates
            mfg_days_ago = random.randint(30, 365)
            mfg_date = date.today() - timedelta(days=mfg_days_ago)
            expiry_days_future = random.randint(90, 730)  # 3 months to 2 years
            expiry_date = date.today() + timedelta(days=expiry_days_future)
            
            # Select location based on weights
            location_id = random.choices(
                list(location_weights.keys()),
                weights=list(location_weights.values())
            )[0]
            
            # Generate quantities based on product type
            if product.unit_of_measure in ['ml', 'g']:
                base_qty = random.randint(500, 5000)  # 500ml to 5L for liquids
            elif product.unit_of_measure == 'pcs':
                base_qty = random.randint(10, 100)    # 10-100 pieces
            else:
                base_qty = random.randint(5, 50)      # 5-50 sets/other units
            
            # Generate pricing
            if 'Premium' in product.name or 'Luxury' in product.name:
                unit_cost = round(random.uniform(25, 100), 2)
            elif 'Essential Oil' in product.category.name:
                unit_cost = round(random.uniform(15, 75), 2)
            else:
                unit_cost = round(random.uniform(5, 50), 2)
            
            selling_price = round(unit_cost * random.uniform(1.5, 3.0), 2)
            
            batch_name = f"{product.sku}-B{i+1:02d}-{mfg_date.strftime('%m%y')}"
            
            existing = InventoryBatch.query.filter_by(batch_name=batch_name).first()
            if not existing:
                batch = InventoryBatch(
                    batch_name=batch_name,
                    mfg_date=mfg_date,
                    expiry_date=expiry_date,
                    product_id=product.id,
                    location_id=location_id,
                    qty_available=Decimal(str(base_qty)),
                    unit_cost=Decimal(str(unit_cost)),
                    selling_price=Decimal(str(selling_price)),
                    status='active'
                )
                db.session.add(batch)
                
                # Create audit log entry for initial stock
                if admin_user_id:
                    audit_log = InventoryAuditLog(
                        batch_id=None,  # Will be set after batch is committed
                        product_id=product.id,
                        user_id=admin_user_id,
                        action_type='adjustment_add',
                        quantity_delta=Decimal(str(base_qty)),
                        stock_before=Decimal('0'),
                        stock_after=Decimal(str(base_qty)),
                        reference_type='initial_stock',
                        notes=f'Initial stock for batch {batch_name}'
                    )
                    db.session.add(audit_log)
                
                created_batches.append(batch)
                print(f"✅ Created batch: {batch_name} ({base_qty} {product.unit_of_measure})")
            else:
                created_batches.append(existing)
                print(f"ℹ️  Batch already exists: {batch_name}")
    
    db.session.commit()
    
    # Update audit log batch_ids after commit
    if admin_user_id:
        for batch in created_batches:
            audit_log = InventoryAuditLog.query.filter_by(
                product_id=batch.product_id,
                reference_type='initial_stock'
            ).filter(InventoryAuditLog.batch_id.is_(None)).first()
            
            if audit_log:
                audit_log.batch_id = batch.id
        
        db.session.commit()
    
    return created_batches

def main():
    """Main function to create all sample inventory data"""
    print("🚀 Creating comprehensive inventory sample data...")
    
    with app.app_context():
        try:
            # Create categories
            print("\n📁 Creating inventory categories...")
            categories = create_sample_categories()
            
            # Create locations
            print("\n📍 Creating inventory locations...")
            locations = create_sample_locations()
            
            # Create products
            print("\n📦 Creating inventory products...")
            products = create_sample_products(categories)
            
            # Create batches
            print("\n🏷️  Creating inventory batches...")
            batches = create_sample_batches(products, locations)
            
            print(f"\n✅ Successfully created sample inventory data:")
            print(f"   📁 Categories: {len(categories)}")
            print(f"   📍 Locations: {len(locations)}")
            print(f"   📦 Products: {len(products)}")
            print(f"   🏷️  Batches: {len(batches)}")
            print(f"\n🎉 Inventory system is now populated with sample data!")
            
        except Exception as e:
            print(f"❌ Error creating sample data: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)