
#!/usr/bin/env python3
"""
Script to add complete inventory data to the spa management system
- 10 Categories
- 10 Suppliers  
- Complete product inventory with all details
"""

from app import app, db
from models import InventoryProduct, InventoryCategory, InventorySupplier
from datetime import datetime, date
import uuid

def create_complete_inventory_data():
    """Add comprehensive inventory data for spa management"""
    
    with app.app_context():
        try:
            print("🏗️ Creating Complete Inventory Data...")
            
            # 1. CREATE 10 COMPREHENSIVE CATEGORIES
            print("\n--- Adding 10 Categories ---")
            categories_data = [
                {
                    'category_name': 'Skincare Products',
                    'description': 'Face creams, serums, cleansers, and anti-aging products'
                },
                {
                    'category_name': 'Hair Care Products', 
                    'description': 'Shampoos, conditioners, hair treatments, and styling products'
                },
                {
                    'category_name': 'Massage Oils & Essentials',
                    'description': 'Essential oils, massage oils, aromatherapy products'
                },
                {
                    'category_name': 'Nail Care Products',
                    'description': 'Nail polishes, treatments, cuticle oils, and nail art supplies'
                },
                {
                    'category_name': 'Professional Equipment',
                    'description': 'Hair dryers, steamers, UV sanitizers, and professional tools'
                },
                {
                    'category_name': 'Spa Linens & Towels',
                    'description': 'Towels, robes, slippers, and spa textile supplies'
                },
                {
                    'category_name': 'Cleaning & Sanitization',
                    'description': 'Hand sanitizers, disinfectants, and cleaning supplies'
                },
                {
                    'category_name': 'Waxing & Threading Supplies',
                    'description': 'Wax, strips, threading tools, and hair removal products'
                },
                {
                    'category_name': 'Makeup & Cosmetics',
                    'description': 'Foundation, lipsticks, eyeshadows, and makeup tools'
                },
                {
                    'category_name': 'Wellness & Supplements',
                    'description': 'Health supplements, herbal products, and wellness items'
                }
            ]
            
            categories = {}
            for cat_data in categories_data:
                existing_cat = InventoryCategory.query.filter_by(category_name=cat_data['category_name']).first()
                if not existing_cat:
                    category = InventoryCategory(
                        category_name=cat_data['category_name'],
                        description=cat_data['description'],
                        is_active=True,
                        created_at=datetime.utcnow(),
                        created_by='admin'
                    )
                    db.session.add(category)
                    db.session.flush()
                    categories[cat_data['category_name']] = category.category_id
                    print(f"✅ Created category: {cat_data['category_name']}")
                else:
                    categories[cat_data['category_name']] = existing_cat.category_id
                    print(f"⚠️ Category already exists: {cat_data['category_name']}")
            
            # 2. CREATE 10 COMPREHENSIVE SUPPLIERS
            print("\n--- Adding 10 Suppliers ---")
            suppliers_data = [
                {
                    'supplier_name': 'Beauty Excellence Ltd.',
                    'supplier_code': 'BEL001',
                    'contact_person': 'Priya Sharma',
                    'phone': '+91-9876543210',
                    'email': 'priya@beautyexcellence.com',
                    'city': 'Mumbai',
                    'address': '123 Beauty Street, Andheri West, Mumbai - 400053'
                },
                {
                    'supplier_name': 'Professional Spa Solutions',
                    'supplier_code': 'PSS002',
                    'contact_person': 'Raj Kumar',
                    'phone': '+91-9876543211',
                    'email': 'raj@prospapolutions.com',
                    'city': 'Delhi',
                    'address': '456 Spa Avenue, Connaught Place, Delhi - 110001'
                },
                {
                    'supplier_name': 'Organic Wellness Pvt Ltd',
                    'supplier_code': 'OWL003',
                    'contact_person': 'Sunita Gupta',
                    'phone': '+91-9876543212',
                    'email': 'sunita@organicwellness.com',
                    'city': 'Bangalore',
                    'address': '789 Wellness Road, Koramangala, Bangalore - 560034'
                },
                {
                    'supplier_name': 'Hair Care Specialists',
                    'supplier_code': 'HCS004',
                    'contact_person': 'Amit Patel',
                    'phone': '+91-9876543213',
                    'email': 'amit@haircarespecialists.com',
                    'city': 'Ahmedabad',
                    'address': '321 Hair Street, Satellite, Ahmedabad - 380015'
                },
                {
                    'supplier_name': 'Equipment Pro India',
                    'supplier_code': 'EPI005',
                    'contact_person': 'Neha Singh',
                    'phone': '+91-9876543214',
                    'email': 'neha@equipmentpro.in',
                    'city': 'Pune',
                    'address': '654 Equipment Plaza, Baner, Pune - 411045'
                },
                {
                    'supplier_name': 'Luxury Linens Co.',
                    'supplier_code': 'LLC006',
                    'contact_person': 'Rahul Joshi',
                    'phone': '+91-9876543215',
                    'email': 'rahul@luxurylinens.com',
                    'city': 'Jaipur',
                    'address': '987 Textile Lane, Malviya Nagar, Jaipur - 302017'
                },
                {
                    'supplier_name': 'Clean & Safe Solutions',
                    'supplier_code': 'CSS007',
                    'contact_person': 'Kavya Reddy',
                    'phone': '+91-9876543216',
                    'email': 'kavya@cleansafe.com',
                    'city': 'Hyderabad',
                    'address': '147 Safety Street, Banjara Hills, Hyderabad - 500034'
                },
                {
                    'supplier_name': 'Nail Art Paradise',
                    'supplier_code': 'NAP008',
                    'contact_person': 'Pooja Agarwal',
                    'phone': '+91-9876543217',
                    'email': 'pooja@nailartparadise.com',
                    'city': 'Kolkata',
                    'address': '258 Nail Street, Park Street, Kolkata - 700016'
                },
                {
                    'supplier_name': 'Cosmetic World Distributors',
                    'supplier_code': 'CWD009',
                    'contact_person': 'Arjun Malhotra',
                    'phone': '+91-9876543218',
                    'email': 'arjun@cosmeticworld.com',
                    'city': 'Chennai',
                    'address': '369 Cosmetic Avenue, T.Nagar, Chennai - 600017'
                },
                {
                    'supplier_name': 'Herbal Health Products',
                    'supplier_code': 'HHP010',
                    'contact_person': 'Deepika Iyer',
                    'phone': '+91-9876543219',
                    'email': 'deepika@herbalhealth.com',
                    'city': 'Kochi',
                    'address': '741 Herbal Road, Marine Drive, Kochi - 682031'
                }
            ]
            
            suppliers = {}
            for sup_data in suppliers_data:
                existing_sup = InventorySupplier.query.filter_by(supplier_code=sup_data['supplier_code']).first()
                if not existing_sup:
                    supplier = InventorySupplier(
                        supplier_name=sup_data['supplier_name'],
                        supplier_code=sup_data['supplier_code'],
                        contact_person=sup_data['contact_person'],
                        phone=sup_data['phone'],
                        email=sup_data['email'],
                        city=sup_data['city'],
                        address=sup_data['address'],
                        is_active=True,
                        created_at=datetime.utcnow(),
                        created_by='admin'
                    )
                    db.session.add(supplier)
                    db.session.flush()
                    suppliers[sup_data['supplier_name']] = supplier.supplier_id
                    print(f"✅ Created supplier: {sup_data['supplier_name']}")
                else:
                    suppliers[sup_data['supplier_name']] = existing_sup.supplier_id
                    print(f"⚠️ Supplier already exists: {sup_data['supplier_name']}")
            
            # 3. CREATE COMPREHENSIVE INVENTORY PRODUCTS (50+ items)
            print("\n--- Adding Comprehensive Inventory Products ---")
            inventory_items = [
                # Skincare Products
                {
                    'name': 'Vitamin C Face Serum',
                    'category': 'Skincare Products',
                    'supplier': 'Beauty Excellence Ltd.',
                    'current_stock': 45,
                    'unit': 'bottles',
                    'unit_cost': 850.00,
                    'selling_price': 1299.00,
                    'reorder_level': 10,
                    'max_stock_level': 100,
                    'is_expiry_tracked': True,
                    'shelf_life_days': 730
                },
                {
                    'name': 'Anti-Aging Night Cream',
                    'category': 'Skincare Products',
                    'supplier': 'Organic Wellness Pvt Ltd',
                    'current_stock': 32,
                    'unit': 'jars',
                    'unit_cost': 1200.00,
                    'selling_price': 1899.00,
                    'reorder_level': 8,
                    'max_stock_level': 80,
                    'is_expiry_tracked': True,
                    'shelf_life_days': 1095
                },
                {
                    'name': 'Hydrating Face Mask',
                    'category': 'Skincare Products',
                    'supplier': 'Beauty Excellence Ltd.',
                    'current_stock': 60,
                    'unit': 'sheets',
                    'unit_cost': 25.00,
                    'selling_price': 75.00,
                    'reorder_level': 20,
                    'max_stock_level': 200
                },
                {
                    'name': 'Gentle Facial Cleanser',
                    'category': 'Skincare Products',
                    'supplier': 'Organic Wellness Pvt Ltd',
                    'current_stock': 38,
                    'unit': 'bottles',
                    'unit_cost': 380.00,
                    'selling_price': 649.00,
                    'reorder_level': 12,
                    'max_stock_level': 90
                },
                {
                    'name': 'Exfoliating Face Scrub',
                    'category': 'Skincare Products',
                    'supplier': 'Beauty Excellence Ltd.',
                    'current_stock': 28,
                    'unit': 'tubes',
                    'unit_cost': 420.00,
                    'selling_price': 699.00,
                    'reorder_level': 8,
                    'max_stock_level': 70
                },
                
                # Hair Care Products
                {
                    'name': 'Keratin Hair Treatment',
                    'category': 'Hair Care Products',
                    'supplier': 'Hair Care Specialists',
                    'current_stock': 18,
                    'unit': 'bottles',
                    'unit_cost': 1800.00,
                    'selling_price': 2899.00,
                    'reorder_level': 5,
                    'max_stock_level': 40,
                    'is_expiry_tracked': True,
                    'shelf_life_days': 1460
                },
                {
                    'name': 'Argan Oil Shampoo',
                    'category': 'Hair Care Products',
                    'supplier': 'Hair Care Specialists',
                    'current_stock': 42,
                    'unit': 'bottles',
                    'unit_cost': 450.00,
                    'selling_price': 749.00,
                    'reorder_level': 15,
                    'max_stock_level': 100
                },
                {
                    'name': 'Deep Conditioning Hair Mask',
                    'category': 'Hair Care Products',
                    'supplier': 'Organic Wellness Pvt Ltd',
                    'current_stock': 25,
                    'unit': 'jars',
                    'unit_cost': 680.00,
                    'selling_price': 1149.00,
                    'reorder_level': 8,
                    'max_stock_level': 60
                },
                {
                    'name': 'Hair Growth Serum',
                    'category': 'Hair Care Products',
                    'supplier': 'Hair Care Specialists',
                    'current_stock': 35,
                    'unit': 'bottles',
                    'unit_cost': 950.00,
                    'selling_price': 1599.00,
                    'reorder_level': 10,
                    'max_stock_level': 80
                },
                {
                    'name': 'Color Protection Conditioner',
                    'category': 'Hair Care Products',
                    'supplier': 'Hair Care Specialists',
                    'current_stock': 48,
                    'unit': 'bottles',
                    'unit_cost': 380.00,
                    'selling_price': 649.00,
                    'reorder_level': 12,
                    'max_stock_level': 100
                },
                
                # Massage Oils & Essentials
                {
                    'name': 'Lavender Essential Oil',
                    'category': 'Massage Oils & Essentials',
                    'supplier': 'Organic Wellness Pvt Ltd',
                    'current_stock': 22,
                    'unit': 'bottles',
                    'unit_cost': 850.00,
                    'selling_price': 1299.00,
                    'reorder_level': 6,
                    'max_stock_level': 50,
                    'is_expiry_tracked': True,
                    'shelf_life_days': 1825
                },
                {
                    'name': 'Hot Stone Massage Oil',
                    'category': 'Massage Oils & Essentials',
                    'supplier': 'Professional Spa Solutions',
                    'current_stock': 30,
                    'unit': 'bottles',
                    'unit_cost': 520.00,
                    'selling_price': 849.00,
                    'reorder_level': 8,
                    'max_stock_level': 70
                },
                {
                    'name': 'Aromatherapy Blend Oil Set',
                    'category': 'Massage Oils & Essentials',
                    'supplier': 'Organic Wellness Pvt Ltd',
                    'current_stock': 15,
                    'unit': 'sets',
                    'unit_cost': 1200.00,
                    'selling_price': 1999.00,
                    'reorder_level': 4,
                    'max_stock_level': 30
                },
                {
                    'name': 'Eucalyptus Massage Oil',
                    'category': 'Massage Oils & Essentials',
                    'supplier': 'Professional Spa Solutions',
                    'current_stock': 28,
                    'unit': 'bottles',
                    'unit_cost': 420.00,
                    'selling_price': 699.00,
                    'reorder_level': 8,
                    'max_stock_level': 60
                },
                {
                    'name': 'Relaxing Massage Candles',
                    'category': 'Massage Oils & Essentials',
                    'supplier': 'Organic Wellness Pvt Ltd',
                    'current_stock': 40,
                    'unit': 'pieces',
                    'unit_cost': 180.00,
                    'selling_price': 349.00,
                    'reorder_level': 15,
                    'max_stock_level': 100
                },
                
                # Nail Care Products
                {
                    'name': 'Gel Nail Polish Set (12 Colors)',
                    'category': 'Nail Care Products',
                    'supplier': 'Nail Art Paradise',
                    'current_stock': 25,
                    'unit': 'sets',
                    'unit_cost': 380.00,
                    'selling_price': 649.00,
                    'reorder_level': 8,
                    'max_stock_level': 60
                },
                {
                    'name': 'Cuticle Nourishing Oil',
                    'category': 'Nail Care Products',
                    'supplier': 'Nail Art Paradise',
                    'current_stock': 45,
                    'unit': 'bottles',
                    'unit_cost': 120.00,
                    'selling_price': 249.00,
                    'reorder_level': 15,
                    'max_stock_level': 100
                },
                {
                    'name': 'Professional Nail Art Kit',
                    'category': 'Nail Care Products',
                    'supplier': 'Nail Art Paradise',
                    'current_stock': 12,
                    'unit': 'kits',
                    'unit_cost': 1500.00,
                    'selling_price': 2499.00,
                    'reorder_level': 3,
                    'max_stock_level': 25
                },
                {
                    'name': 'UV Nail Lamp',
                    'category': 'Nail Care Products',
                    'supplier': 'Equipment Pro India',
                    'current_stock': 4,
                    'unit': 'pieces',
                    'unit_cost': 2800.00,
                    'selling_price': 0.00,  # Equipment not sold
                    'reorder_level': 1,
                    'max_stock_level': 8
                },
                {
                    'name': 'Nail Strengthening Treatment',
                    'category': 'Nail Care Products',
                    'supplier': 'Nail Art Paradise',
                    'current_stock': 30,
                    'unit': 'bottles',
                    'unit_cost': 250.00,
                    'selling_price': 449.00,
                    'reorder_level': 10,
                    'max_stock_level': 70
                },
                
                # Professional Equipment
                {
                    'name': 'Professional Hair Dryer',
                    'category': 'Professional Equipment',
                    'supplier': 'Equipment Pro India',
                    'current_stock': 6,
                    'unit': 'pieces',
                    'unit_cost': 4500.00,
                    'selling_price': 0.00,
                    'reorder_level': 2,
                    'max_stock_level': 12
                },
                {
                    'name': 'Facial Steamer Machine',
                    'category': 'Professional Equipment',
                    'supplier': 'Equipment Pro India',
                    'current_stock': 3,
                    'unit': 'pieces',
                    'unit_cost': 8500.00,
                    'selling_price': 0.00,
                    'reorder_level': 1,
                    'max_stock_level': 6
                },
                {
                    'name': 'UV Sanitizer Cabinet',
                    'category': 'Professional Equipment',
                    'supplier': 'Equipment Pro India',
                    'current_stock': 2,
                    'unit': 'pieces',
                    'unit_cost': 12000.00,
                    'selling_price': 0.00,
                    'reorder_level': 1,
                    'max_stock_level': 4
                },
                {
                    'name': 'Professional Massage Table',
                    'category': 'Professional Equipment',
                    'supplier': 'Equipment Pro India',
                    'current_stock': 4,
                    'unit': 'pieces',
                    'unit_cost': 15000.00,
                    'selling_price': 0.00,
                    'reorder_level': 1,
                    'max_stock_level': 8
                },
                {
                    'name': 'LED Light Therapy Device',
                    'category': 'Professional Equipment',
                    'supplier': 'Equipment Pro India',
                    'current_stock': 2,
                    'unit': 'pieces',
                    'unit_cost': 25000.00,
                    'selling_price': 0.00,
                    'reorder_level': 1,
                    'max_stock_level': 4
                },
                
                # Spa Linens & Towels
                {
                    'name': 'Premium Spa Towels (Set of 10)',
                    'category': 'Spa Linens & Towels',
                    'supplier': 'Luxury Linens Co.',
                    'current_stock': 15,
                    'unit': 'sets',
                    'unit_cost': 1200.00,
                    'selling_price': 0.00,
                    'reorder_level': 5,
                    'max_stock_level': 30
                },
                {
                    'name': 'Disposable Spa Slippers',
                    'category': 'Spa Linens & Towels',
                    'supplier': 'Luxury Linens Co.',
                    'current_stock': 500,
                    'unit': 'pairs',
                    'unit_cost': 35.00,
                    'selling_price': 0.00,
                    'reorder_level': 100,
                    'max_stock_level': 1000
                },
                {
                    'name': 'Luxury Spa Robes',
                    'category': 'Spa Linens & Towels',
                    'supplier': 'Luxury Linens Co.',
                    'current_stock': 20,
                    'unit': 'pieces',
                    'unit_cost': 1500.00,
                    'selling_price': 2499.00,
                    'reorder_level': 5,
                    'max_stock_level': 40
                },
                {
                    'name': 'Face Towels (Cotton)',
                    'category': 'Spa Linens & Towels',
                    'supplier': 'Luxury Linens Co.',
                    'current_stock': 80,
                    'unit': 'pieces',
                    'unit_cost': 150.00,
                    'selling_price': 0.00,
                    'reorder_level': 25,
                    'max_stock_level': 150
                },
                {
                    'name': 'Disposable Bed Sheets',
                    'category': 'Spa Linens & Towels',
                    'supplier': 'Luxury Linens Co.',
                    'current_stock': 200,
                    'unit': 'pieces',
                    'unit_cost': 45.00,
                    'selling_price': 0.00,
                    'reorder_level': 50,
                    'max_stock_level': 500
                },
                
                # Cleaning & Sanitization
                {
                    'name': 'Hand Sanitizer (500ml)',
                    'category': 'Cleaning & Sanitization',
                    'supplier': 'Clean & Safe Solutions',
                    'current_stock': 40,
                    'unit': 'bottles',
                    'unit_cost': 180.00,
                    'selling_price': 299.00,
                    'reorder_level': 15,
                    'max_stock_level': 100
                },
                {
                    'name': 'Surface Disinfectant Spray',
                    'category': 'Cleaning & Sanitization',
                    'supplier': 'Clean & Safe Solutions',
                    'current_stock': 35,
                    'unit': 'bottles',
                    'unit_cost': 220.00,
                    'selling_price': 0.00,
                    'reorder_level': 12,
                    'max_stock_level': 80
                },
                {
                    'name': 'Equipment Sterilizer Solution',
                    'category': 'Cleaning & Sanitization',
                    'supplier': 'Clean & Safe Solutions',
                    'current_stock': 25,
                    'unit': 'bottles',
                    'unit_cost': 380.00,
                    'selling_price': 0.00,
                    'reorder_level': 8,
                    'max_stock_level': 60
                },
                {
                    'name': 'Antibacterial Wipes',
                    'category': 'Cleaning & Sanitization',
                    'supplier': 'Clean & Safe Solutions',
                    'current_stock': 60,
                    'unit': 'packs',
                    'unit_cost': 85.00,
                    'selling_price': 149.00,
                    'reorder_level': 20,
                    'max_stock_level': 150
                },
                {
                    'name': 'Floor Cleaning Solution',
                    'category': 'Cleaning & Sanitization',
                    'supplier': 'Clean & Safe Solutions',
                    'current_stock': 18,
                    'unit': 'bottles',
                    'unit_cost': 320.00,
                    'selling_price': 0.00,
                    'reorder_level': 6,
                    'max_stock_level': 40
                },
                
                # Waxing & Threading Supplies
                {
                    'name': 'Professional Wax Strips',
                    'category': 'Waxing & Threading Supplies',
                    'supplier': 'Beauty Excellence Ltd.',
                    'current_stock': 100,
                    'unit': 'strips',
                    'unit_cost': 5.00,
                    'selling_price': 0.00,
                    'reorder_level': 30,
                    'max_stock_level': 300
                },
                {
                    'name': 'Hot Wax (Hard Wax)',
                    'category': 'Waxing & Threading Supplies',
                    'supplier': 'Beauty Excellence Ltd.',
                    'current_stock': 12,
                    'unit': 'containers',
                    'unit_cost': 650.00,
                    'selling_price': 0.00,
                    'reorder_level': 4,
                    'max_stock_level': 30
                },
                {
                    'name': 'Pre-Wax Cleanser',
                    'category': 'Waxing & Threading Supplies',
                    'supplier': 'Beauty Excellence Ltd.',
                    'current_stock': 20,
                    'unit': 'bottles',
                    'unit_cost': 280.00,
                    'selling_price': 0.00,
                    'reorder_level': 8,
                    'max_stock_level': 50
                },
                {
                    'name': 'Threading Cotton',
                    'category': 'Waxing & Threading Supplies',
                    'supplier': 'Beauty Excellence Ltd.',
                    'current_stock': 50,
                    'unit': 'spools',
                    'unit_cost': 45.00,
                    'selling_price': 0.00,
                    'reorder_level': 15,
                    'max_stock_level': 150
                },
                {
                    'name': 'After-Wax Soothing Lotion',
                    'category': 'Waxing & Threading Supplies',
                    'supplier': 'Beauty Excellence Ltd.',
                    'current_stock': 25,
                    'unit': 'bottles',
                    'unit_cost': 320.00,
                    'selling_price': 549.00,
                    'reorder_level': 8,
                    'max_stock_level': 60
                },
                
                # Makeup & Cosmetics
                {
                    'name': 'Professional Foundation Kit',
                    'category': 'Makeup & Cosmetics',
                    'supplier': 'Cosmetic World Distributors',
                    'current_stock': 8,
                    'unit': 'kits',
                    'unit_cost': 2500.00,
                    'selling_price': 0.00,
                    'reorder_level': 2,
                    'max_stock_level': 20
                },
                {
                    'name': 'Lipstick Collection (24 Shades)',
                    'category': 'Makeup & Cosmetics',
                    'supplier': 'Cosmetic World Distributors',
                    'current_stock': 5,
                    'unit': 'sets',
                    'unit_cost': 1800.00,
                    'selling_price': 0.00,
                    'reorder_level': 2,
                    'max_stock_level': 15
                },
                {
                    'name': 'Eye Shadow Palette Professional',
                    'category': 'Makeup & Cosmetics',
                    'supplier': 'Cosmetic World Distributors',
                    'current_stock': 12,
                    'unit': 'palettes',
                    'unit_cost': 850.00,
                    'selling_price': 0.00,
                    'reorder_level': 4,
                    'max_stock_level': 30
                },
                {
                    'name': 'Makeup Brushes Professional Set',
                    'category': 'Makeup & Cosmetics',
                    'supplier': 'Cosmetic World Distributors',
                    'current_stock': 10,
                    'unit': 'sets',
                    'unit_cost': 1200.00,
                    'selling_price': 0.00,
                    'reorder_level': 3,
                    'max_stock_level': 25
                },
                {
                    'name': 'Setting Spray Professional',
                    'category': 'Makeup & Cosmetics',
                    'supplier': 'Cosmetic World Distributors',
                    'current_stock': 20,
                    'unit': 'bottles',
                    'unit_cost': 480.00,
                    'selling_price': 0.00,
                    'reorder_level': 6,
                    'max_stock_level': 50
                },
                
                # Wellness & Supplements
                {
                    'name': 'Vitamin E Capsules for Skin',
                    'category': 'Wellness & Supplements',
                    'supplier': 'Herbal Health Products',
                    'current_stock': 30,
                    'unit': 'bottles',
                    'unit_cost': 420.00,
                    'selling_price': 699.00,
                    'reorder_level': 10,
                    'max_stock_level': 80,
                    'is_expiry_tracked': True,
                    'shelf_life_days': 730
                },
                {
                    'name': 'Herbal Hair Growth Supplement',
                    'category': 'Wellness & Supplements',
                    'supplier': 'Herbal Health Products',
                    'current_stock': 25,
                    'unit': 'bottles',
                    'unit_cost': 650.00,
                    'selling_price': 999.00,
                    'reorder_level': 8,
                    'max_stock_level': 60,
                    'is_expiry_tracked': True,
                    'shelf_life_days': 1095
                },
                {
                    'name': 'Collagen Powder for Skin Health',
                    'category': 'Wellness & Supplements',
                    'supplier': 'Herbal Health Products',
                    'current_stock': 18,
                    'unit': 'containers',
                    'unit_cost': 1200.00,
                    'selling_price': 1899.00,
                    'reorder_level': 5,
                    'max_stock_level': 40,
                    'is_expiry_tracked': True,
                    'shelf_life_days': 365
                },
                {
                    'name': 'Detox Tea Blend',
                    'category': 'Wellness & Supplements',
                    'supplier': 'Herbal Health Products',
                    'current_stock': 40,
                    'unit': 'packets',
                    'unit_cost': 180.00,
                    'selling_price': 349.00,
                    'reorder_level': 15,
                    'max_stock_level': 100,
                    'is_expiry_tracked': True,
                    'shelf_life_days': 1095
                },
                {
                    'name': 'Omega-3 Fish Oil for Healthy Skin',
                    'category': 'Wellness & Supplements',
                    'supplier': 'Herbal Health Products',
                    'current_stock': 22,
                    'unit': 'bottles',
                    'unit_cost': 850.00,
                    'selling_price': 1299.00,
                    'reorder_level': 8,
                    'max_stock_level': 50,
                    'is_expiry_tracked': True,
                    'shelf_life_days': 730
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
                    print(f"⚠️ Item already exists: {item_data['name']}")
                    continue
                
                # Get category and supplier IDs
                category_id = categories.get(item_data['category'])
                supplier_id = suppliers.get(item_data['supplier'])
                
                inventory_item = InventoryProduct(
                    product_code=product_code,
                    name=item_data['name'],
                    description=f"Premium quality {item_data['name'].lower()} for professional spa use",
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
                    created_by='admin'
                )
                
                db.session.add(inventory_item)
                added_count += 1
                print(f"✅ Adding: {item_data['name']} - Stock: {item_data['current_stock']} {item_data['unit']}")
            
            if added_count > 0:
                db.session.commit()
                print(f"\n🎉 Successfully added {added_count} inventory items to the database!")
                
                # Print comprehensive summary
                total_items = InventoryProduct.query.filter_by(is_active=True).count()
                total_categories = len(categories)
                total_suppliers = len(suppliers)
                
                print(f"\n📊 Complete Inventory Summary:")
                print(f"   - Total Active Items: {total_items}")
                print(f"   - Total Categories: {total_categories}")
                print(f"   - Total Suppliers: {total_suppliers}")
                print(f"   - Items Added This Run: {added_count}")
                
                # Calculate total inventory value
                all_items = InventoryProduct.query.filter_by(is_active=True).all()
                total_cost_value = sum(item.current_stock * item.unit_cost for item in all_items)
                total_selling_value = sum(item.current_stock * item.selling_price for item in all_items if item.selling_price > 0)
                
                print(f"   - Total Inventory Cost Value: ₹{total_cost_value:,.2f}")
                print(f"   - Total Inventory Retail Value: ₹{total_selling_value:,.2f}")
                print(f"   - Potential Profit Margin: ₹{total_selling_value - total_cost_value:,.2f}")
                
                # Category-wise breakdown
                print(f"\n📋 Category-wise Breakdown:")
                for cat_name, cat_id in categories.items():
                    items_in_cat = InventoryProduct.query.filter_by(category_id=cat_id, is_active=True).count()
                    print(f"   - {cat_name}: {items_in_cat} items")
                
                # Supplier-wise breakdown
                print(f"\n🏭 Supplier-wise Breakdown:")
                for sup_name, sup_id in suppliers.items():
                    items_from_sup = InventoryProduct.query.filter_by(supplier_id=sup_id, is_active=True).count()
                    print(f"   - {sup_name}: {items_from_sup} items")
                    
            else:
                print("\n⚠️ All inventory items already exist in the database")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding complete inventory data: {str(e)}")
            raise e

if __name__ == "__main__":
    create_complete_inventory_data()
