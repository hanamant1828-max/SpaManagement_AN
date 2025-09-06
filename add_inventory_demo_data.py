#!/usr/bin/env python3
"""
Script to add comprehensive inventory demo data for spa business
Including categories, suppliers, and product master with realistic data
"""

from app import app, db
from modules.hanamantinventory.models import HanamanCategory, HanamanSupplier, HanamanProduct
from datetime import datetime, date, timedelta
import random

def create_inventory_categories():
    """Create comprehensive inventory categories for spa business"""
    
    categories = [
        {
            'name': 'Hair Care Products',
            'description': 'Shampoos, conditioners, hair treatments, and styling products'
        },
        {
            'name': 'Skin Care Products',
            'description': 'Facial cleansers, moisturizers, serums, and anti-aging products'
        },
        {
            'name': 'Body Care Products',
            'description': 'Body lotions, scrubs, wraps, and massage oils'
        },
        {
            'name': 'Nail Care Products',
            'description': 'Nail polishes, base coats, top coats, and nail treatments'
        },
        {
            'name': 'Massage Oils & Lotions',
            'description': 'Essential oils, massage creams, and aromatherapy products'
        },
        {
            'name': 'Facial Equipment',
            'description': 'Steamers, brushes, and professional facial tools'
        },
        {
            'name': 'Disposables & Hygiene',
            'description': 'Towels, cotton pads, gloves, and single-use items'
        },
        {
            'name': 'Waxing Supplies',
            'description': 'Wax, strips, pre and post-wax products'
        },
        {
            'name': 'Professional Tools',
            'description': 'Scissors, combs, brushes, and styling equipment'
        },
        {
            'name': 'Retail Products',
            'description': 'Products for retail sale to customers'
        },
        {
            'name': 'Cleaning & Sanitization',
            'description': 'Disinfectants, sanitizers, and cleaning supplies'
        },
        {
            'name': 'Office Supplies',
            'description': 'Paper, pens, appointment books, and administrative items'
        }
    ]
    
    added_count = 0
    for cat_data in categories:
        existing_cat = HanamanCategory.query.filter_by(name=cat_data['name']).first()
        if not existing_cat:
            category = HanamanCategory(**cat_data)
            db.session.add(category)
            added_count += 1
            print(f"Adding category: {cat_data['name']}")
    
    db.session.commit()
    return added_count

def create_inventory_suppliers():
    """Create realistic suppliers for spa business"""
    
    suppliers = [
        {
            'name': 'Premium Spa Products Ltd.',
            'contact_person': 'Rajesh Kumar',
            'phone': '+91-9876543210',
            'email': 'orders@premiumspaproducts.com',
            'address': '15, Industrial Area, Sector 25',
            'city': 'Gurgaon',
            'state': 'Haryana',
            'pincode': '122001',
            'gst_number': 'GST29ABCDE1234F1Z5',
            'payment_terms': 'Net 30 days'
        },
        {
            'name': 'Natural Beauty Essentials',
            'contact_person': 'Priya Sharma',
            'phone': '+91-9876543211',
            'email': 'supply@naturalbeauty.in',
            'address': '23, Green Park Extension',
            'city': 'New Delhi',
            'state': 'Delhi',
            'pincode': '110016',
            'gst_number': 'GST07FGHIJ5678K2M6',
            'payment_terms': 'Net 15 days'
        },
        {
            'name': 'Professional Salon Equipment Co.',
            'contact_person': 'Amit Singh',
            'phone': '+91-9876543212',
            'email': 'sales@prosalonequip.com',
            'address': '45, Commercial Complex, Lajpat Nagar',
            'city': 'New Delhi',
            'state': 'Delhi',
            'pincode': '110024',
            'gst_number': 'GST07KLMNO9012P3Q7',
            'payment_terms': 'Net 45 days'
        },
        {
            'name': 'Luxury Cosmetics International',
            'contact_person': 'Sunita Patel',
            'phone': '+91-9876543213',
            'email': 'orders@luxurycosmetics.co.in',
            'address': '78, Business Bay, Andheri East',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400069',
            'gst_number': 'GST27RSTUV3456W4X8',
            'payment_terms': 'Net 30 days'
        },
        {
            'name': 'Eco-Friendly Spa Solutions',
            'contact_person': 'Dr. Kavita Menon',
            'phone': '+91-9876543214',
            'email': 'info@ecospasolutions.in',
            'address': '12, Organic Plaza, Koramangala',
            'city': 'Bangalore',
            'state': 'Karnataka',
            'pincode': '560034',
            'gst_number': 'GST29YZABC7890D5E9',
            'payment_terms': 'Net 20 days'
        },
        {
            'name': 'Essential Oils & Aromatherapy Hub',
            'contact_person': 'Ravi Agarwal',
            'phone': '+91-9876543215',
            'email': 'wholesale@essentialoilshub.com',
            'address': '56, Herbal Complex, Rishikesh Road',
            'city': 'Dehradun',
            'state': 'Uttarakhand',
            'pincode': '248001',
            'gst_number': 'GST05FGHIJ1234K6L0',
            'payment_terms': 'Net 15 days'
        }
    ]
    
    added_count = 0
    for sup_data in suppliers:
        existing_sup = HanamanSupplier.query.filter_by(name=sup_data['name']).first()
        if not existing_sup:
            supplier = HanamanSupplier(**sup_data)
            db.session.add(supplier)
            added_count += 1
            print(f"Adding supplier: {sup_data['name']}")
    
    db.session.commit()
    return added_count

def create_product_master():
    """Create comprehensive product master for spa business"""
    
    # Get categories and suppliers for foreign key references
    categories = {cat.name: cat.id for cat in HanamanCategory.query.all()}
    suppliers = list(HanamanSupplier.query.all())
    
    products = [
        # Hair Care Products
        {
            'sku': 'HC001',
            'name': 'Professional Shampoo - Moisturizing',
            'description': 'Premium moisturizing shampoo for dry and damaged hair',
            'category_id': categories.get('Hair Care Products'),
            'supplier_name': suppliers[0].name if suppliers else 'Premium Spa Products Ltd.',
            'supplier_contact': suppliers[0].phone if suppliers else '+91-9876543210',
            'unit': 'bottle',
            'cost_price': 450.00,
            'selling_price': 650.00,
            'current_stock': 25,
            'min_stock_level': 5,
            'max_stock_level': 50,
            'expiry_date': date.today() + timedelta(days=730)
        },
        {
            'sku': 'HC002',
            'name': 'Professional Conditioner - Repair',
            'description': 'Deep repair conditioner for chemically treated hair',
            'category_id': categories.get('Hair Care Products'),
            'supplier_name': suppliers[0].name if suppliers else 'Premium Spa Products Ltd.',
            'supplier_contact': suppliers[0].phone if suppliers else '+91-9876543210',
            'unit': 'bottle',
            'cost_price': 380.00,
            'selling_price': 580.00,
            'current_stock': 20,
            'min_stock_level': 5,
            'max_stock_level': 40,
            'expiry_date': date.today() + timedelta(days=730)
        },
        {
            'sku': 'HC003',
            'name': 'Hair Serum - Anti-Frizz',
            'description': 'Professional anti-frizz serum for smooth hair',
            'category_id': categories.get('Hair Care Products'),
            'supplier_name': suppliers[3].name if len(suppliers) > 3 else 'Luxury Cosmetics International',
            'supplier_contact': suppliers[3].phone if len(suppliers) > 3 else '+91-9876543213',
            'unit': 'bottle',
            'cost_price': 650.00,
            'selling_price': 950.00,
            'current_stock': 15,
            'min_stock_level': 3,
            'max_stock_level': 25,
            'expiry_date': date.today() + timedelta(days=1095)
        },
        
        # Skin Care Products
        {
            'sku': 'SC001',
            'name': 'Vitamin C Facial Cleanser',
            'description': 'Brightening facial cleanser with vitamin C',
            'category_id': categories.get('Skin Care Products'),
            'supplier_name': suppliers[1].name if len(suppliers) > 1 else 'Natural Beauty Essentials',
            'supplier_contact': suppliers[1].phone if len(suppliers) > 1 else '+91-9876543211',
            'unit': 'tube',
            'cost_price': 320.00,
            'selling_price': 480.00,
            'current_stock': 30,
            'min_stock_level': 8,
            'max_stock_level': 50,
            'expiry_date': date.today() + timedelta(days=365)
        },
        {
            'sku': 'SC002',
            'name': 'Hyaluronic Acid Serum',
            'description': 'Intensive hydrating serum with hyaluronic acid',
            'category_id': categories.get('Skin Care Products'),
            'supplier_name': suppliers[3].name if len(suppliers) > 3 else 'Luxury Cosmetics International',
            'supplier_contact': suppliers[3].phone if len(suppliers) > 3 else '+91-9876543213',
            'unit': 'bottle',
            'cost_price': 850.00,
            'selling_price': 1250.00,
            'current_stock': 12,
            'min_stock_level': 3,
            'max_stock_level': 20,
            'expiry_date': date.today() + timedelta(days=365)
        },
        
        # Body Care Products
        {
            'sku': 'BC001',
            'name': 'Aromatic Body Scrub - Lavender',
            'description': 'Exfoliating body scrub with lavender essential oil',
            'category_id': categories.get('Body Care Products'),
            'supplier_name': suppliers[4].name if len(suppliers) > 4 else 'Eco-Friendly Spa Solutions',
            'supplier_contact': suppliers[4].phone if len(suppliers) > 4 else '+91-9876543214',
            'unit': 'jar',
            'cost_price': 480.00,
            'selling_price': 720.00,
            'current_stock': 18,
            'min_stock_level': 5,
            'max_stock_level': 30,
            'expiry_date': date.today() + timedelta(days=365)
        },
        {
            'sku': 'BC002',
            'name': 'Moisturizing Body Lotion',
            'description': 'Deep moisturizing body lotion for all skin types',
            'category_id': categories.get('Body Care Products'),
            'supplier_name': suppliers[1].name if len(suppliers) > 1 else 'Natural Beauty Essentials',
            'supplier_contact': suppliers[1].phone if len(suppliers) > 1 else '+91-9876543211',
            'unit': 'bottle',
            'cost_price': 280.00,
            'selling_price': 420.00,
            'current_stock': 35,
            'min_stock_level': 10,
            'max_stock_level': 60,
            'expiry_date': date.today() + timedelta(days=730)
        },
        
        # Nail Care Products
        {
            'sku': 'NC001',
            'name': 'Gel Nail Polish - Classic Red',
            'description': 'Long-lasting gel nail polish in classic red',
            'category_id': categories.get('Nail Care Products'),
            'supplier_name': suppliers[3].name if len(suppliers) > 3 else 'Luxury Cosmetics International',
            'supplier_contact': suppliers[3].phone if len(suppliers) > 3 else '+91-9876543213',
            'unit': 'bottle',
            'cost_price': 320.00,
            'selling_price': 480.00,
            'current_stock': 22,
            'min_stock_level': 5,
            'max_stock_level': 40,
            'expiry_date': date.today() + timedelta(days=1095)
        },
        {
            'sku': 'NC002',
            'name': 'Cuticle Oil - Vitamin E',
            'description': 'Nourishing cuticle oil with vitamin E',
            'category_id': categories.get('Nail Care Products'),
            'supplier_name': suppliers[1].name if len(suppliers) > 1 else 'Natural Beauty Essentials',
            'supplier_contact': suppliers[1].phone if len(suppliers) > 1 else '+91-9876543211',
            'unit': 'bottle',
            'cost_price': 180.00,
            'selling_price': 280.00,
            'current_stock': 28,
            'min_stock_level': 8,
            'max_stock_level': 50,
            'expiry_date': date.today() + timedelta(days=730)
        },
        
        # Massage Oils & Lotions
        {
            'sku': 'MO001',
            'name': 'Essential Oil - Eucalyptus',
            'description': 'Pure eucalyptus essential oil for aromatherapy',
            'category_id': categories.get('Massage Oils & Lotions'),
            'supplier_name': suppliers[5].name if len(suppliers) > 5 else 'Essential Oils & Aromatherapy Hub',
            'supplier_contact': suppliers[5].phone if len(suppliers) > 5 else '+91-9876543215',
            'unit': 'bottle',
            'cost_price': 450.00,
            'selling_price': 680.00,
            'current_stock': 15,
            'min_stock_level': 3,
            'max_stock_level': 25,
            'expiry_date': date.today() + timedelta(days=1095)
        },
        {
            'sku': 'MO002',
            'name': 'Massage Oil - Relaxing Blend',
            'description': 'Therapeutic massage oil with lavender and chamomile',
            'category_id': categories.get('Massage Oils & Lotions'),
            'supplier_name': suppliers[5].name if len(suppliers) > 5 else 'Essential Oils & Aromatherapy Hub',
            'supplier_contact': suppliers[5].phone if len(suppliers) > 5 else '+91-9876543215',
            'unit': 'bottle',
            'cost_price': 520.00,
            'selling_price': 780.00,
            'current_stock': 20,
            'min_stock_level': 5,
            'max_stock_level': 35,
            'expiry_date': date.today() + timedelta(days=730)
        },
        
        # Professional Tools
        {
            'sku': 'PT001',
            'name': 'Professional Hair Cutting Scissors',
            'description': 'High-quality stainless steel cutting scissors',
            'category_id': categories.get('Professional Tools'),
            'supplier_name': suppliers[2].name if len(suppliers) > 2 else 'Professional Salon Equipment Co.',
            'supplier_contact': suppliers[2].phone if len(suppliers) > 2 else '+91-9876543212',
            'unit': 'piece',
            'cost_price': 1200.00,
            'selling_price': 0.00,  # Not for sale
            'current_stock': 6,
            'min_stock_level': 2,
            'max_stock_level': 10,
            'expiry_date': None
        },
        {
            'sku': 'PT002',
            'name': 'Facial Steamer - Professional',
            'description': 'Professional facial steamer for deep cleansing',
            'category_id': categories.get('Facial Equipment'),
            'supplier_name': suppliers[2].name if len(suppliers) > 2 else 'Professional Salon Equipment Co.',
            'supplier_contact': suppliers[2].phone if len(suppliers) > 2 else '+91-9876543212',
            'unit': 'piece',
            'cost_price': 8500.00,
            'selling_price': 0.00,  # Not for sale
            'current_stock': 2,
            'min_stock_level': 1,
            'max_stock_level': 3,
            'expiry_date': None
        },
        
        # Disposables & Hygiene
        {
            'sku': 'DH001',
            'name': 'Disposable Towels - White',
            'description': 'Soft disposable towels for spa treatments',
            'category_id': categories.get('Disposables & Hygiene'),
            'supplier_name': suppliers[0].name if suppliers else 'Premium Spa Products Ltd.',
            'supplier_contact': suppliers[0].phone if suppliers else '+91-9876543210',
            'unit': 'pack',
            'cost_price': 180.00,
            'selling_price': 0.00,  # Not for sale
            'current_stock': 45,
            'min_stock_level': 15,
            'max_stock_level': 80,
            'expiry_date': None
        },
        {
            'sku': 'DH002',
            'name': 'Cotton Pads - Premium',
            'description': 'Soft cotton pads for makeup removal and treatments',
            'category_id': categories.get('Disposables & Hygiene'),
            'supplier_name': suppliers[0].name if suppliers else 'Premium Spa Products Ltd.',
            'supplier_contact': suppliers[0].phone if suppliers else '+91-9876543210',
            'unit': 'pack',
            'cost_price': 120.00,
            'selling_price': 0.00,  # Not for sale
            'current_stock': 38,
            'min_stock_level': 12,
            'max_stock_level': 60,
            'expiry_date': None
        },
        
        # Waxing Supplies
        {
            'sku': 'WS001',
            'name': 'Hot Wax - Honey Base',
            'description': 'Premium honey-based hot wax for sensitive skin',
            'category_id': categories.get('Waxing Supplies'),
            'supplier_name': suppliers[0].name if suppliers else 'Premium Spa Products Ltd.',
            'supplier_contact': suppliers[0].phone if suppliers else '+91-9876543210',
            'unit': 'can',
            'cost_price': 320.00,
            'selling_price': 0.00,  # Not for sale
            'current_stock': 12,
            'min_stock_level': 3,
            'max_stock_level': 20,
            'expiry_date': date.today() + timedelta(days=730)
        },
        {
            'sku': 'WS002',
            'name': 'Waxing Strips - Professional',
            'description': 'High-quality waxing strips for clean removal',
            'category_id': categories.get('Waxing Supplies'),
            'supplier_name': suppliers[0].name if suppliers else 'Premium Spa Products Ltd.',
            'supplier_contact': suppliers[0].phone if suppliers else '+91-9876543210',
            'unit': 'pack',
            'cost_price': 280.00,
            'selling_price': 0.00,  # Not for sale
            'current_stock': 25,
            'min_stock_level': 8,
            'max_stock_level': 40,
            'expiry_date': None
        },
        
        # Cleaning & Sanitization
        {
            'sku': 'CS001',
            'name': 'Multi-Surface Disinfectant',
            'description': 'Hospital-grade disinfectant for all surfaces',
            'category_id': categories.get('Cleaning & Sanitization'),
            'supplier_name': suppliers[0].name if suppliers else 'Premium Spa Products Ltd.',
            'supplier_contact': suppliers[0].phone if suppliers else '+91-9876543210',
            'unit': 'bottle',
            'cost_price': 180.00,
            'selling_price': 0.00,  # Not for sale
            'current_stock': 32,
            'min_stock_level': 10,
            'max_stock_level': 50,
            'expiry_date': date.today() + timedelta(days=1095)
        },
        {
            'sku': 'CS002',
            'name': 'Hand Sanitizer - 70% Alcohol',
            'description': 'Antibacterial hand sanitizer for staff and clients',
            'category_id': categories.get('Cleaning & Sanitization'),
            'supplier_name': suppliers[0].name if suppliers else 'Premium Spa Products Ltd.',
            'supplier_contact': suppliers[0].phone if suppliers else '+91-9876543210',
            'unit': 'bottle',
            'cost_price': 120.00,
            'selling_price': 180.00,
            'current_stock': 28,
            'min_stock_level': 8,
            'max_stock_level': 45,
            'expiry_date': date.today() + timedelta(days=730)
        }
    ]
    
    added_count = 0
    for prod_data in products:
        existing_prod = HanamanProduct.query.filter_by(sku=prod_data['sku']).first()
        if not existing_prod:
            product = HanamanProduct(**prod_data)
            db.session.add(product)
            added_count += 1
            print(f"Adding product: {prod_data['name']} ({prod_data['sku']})")
    
    db.session.commit()
    return added_count

def add_inventory_demo_data():
    """Main function to add all inventory demo data"""
    
    with app.app_context():
        try:
            print("🏪 Starting inventory demo data creation...")
            
            # 1. Create categories
            print("\n1️⃣ Creating inventory categories...")
            categories_added = create_inventory_categories()
            
            # 2. Create suppliers
            print("\n2️⃣ Creating suppliers...")
            suppliers_added = create_inventory_suppliers()
            
            # 3. Create product master
            print("\n3️⃣ Creating product master...")
            products_added = create_product_master()
            
            # Summary
            print(f"\n✅ Inventory Demo Data Creation Complete!")
            print(f"📊 Summary:")
            print(f"   - Categories Added: {categories_added}")
            print(f"   - Suppliers Added: {suppliers_added}")
            print(f"   - Products Added: {products_added}")
            
            # Display inventory overview
            print(f"\n📋 Inventory Overview:")
            total_categories = HanamanCategory.query.filter_by(is_active=True).count()
            total_suppliers = HanamanSupplier.query.filter_by(is_active=True).count()
            total_products = HanamanProduct.query.filter_by(is_active=True).count()
            total_stock_value = db.session.query(db.func.sum(HanamanProduct.current_stock * HanamanProduct.cost_price)).scalar() or 0
            
            print(f"   - Total Categories: {total_categories}")
            print(f"   - Total Suppliers: {total_suppliers}")
            print(f"   - Total Products: {total_products}")
            print(f"   - Total Stock Value: ₹{total_stock_value:,.2f}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating inventory data: {str(e)}")
            raise e

if __name__ == "__main__":
    add_inventory_demo_data()