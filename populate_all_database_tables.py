
#!/usr/bin/env python3
"""
Comprehensive database population script for spa management system
Populates ALL tables with realistic sample data
"""
from app import app, db
from models import *
from datetime import datetime, date, timedelta
import json
import uuid

def generate_sku(name):
    """Generate a unique SKU from item name"""
    prefix = ''.join([word[0].upper() for word in name.split()[:3]])
    suffix = str(uuid.uuid4())[:6].upper()
    return f"{prefix}-{suffix}"

def populate_all_data():
    """Populate all database tables with comprehensive sample data"""
    
    with app.app_context():
        print("🚀 Starting comprehensive database population...")
        
        # 1. Create Categories
        create_categories()
        
        # 2. Create Departments
        create_departments()
        
        # 3. Create Roles (if not exist)
        create_roles()
        
        # 4. Create Staff Users
        create_staff_users()
        
        # 5. Create Customers
        create_customers()
        
        # 6. Create Services
        create_services()
        
        # 7. Create Suppliers
        create_suppliers()
        
        # 8. Create Inventory Items
        create_inventory_items()
        
        # 9. Create Packages
        create_packages()
        
        # 10. Create Customer Packages
        create_customer_packages()
        
        # 11. Create Appointments
        create_appointments()
        
        # 12. Create Expenses
        create_expenses()
        
        # 13. Create Attendance Records
        create_attendance_records()
        
        # 14. Create Performance Records
        create_performance_records()
        
        # 15. Create Reviews
        create_reviews()
        
        # 16. Create Stock Movements
        create_stock_movements()
        
        # 17. Create Business Settings
        create_business_settings()
        
        print("🎉 Database population completed successfully!")

def create_categories():
    """Create comprehensive categories"""
    print("📋 Creating categories...")
    
    categories_data = [
        # Service Categories
        {"name": "facial", "display_name": "Facial Treatments", "type": "service", "color": "#FF6B6B", "description": "Professional facial treatments"},
        {"name": "massage", "display_name": "Massage Therapy", "type": "service", "color": "#4ECDC4", "description": "Relaxing massage services"},
        {"name": "hair", "display_name": "Hair Services", "type": "service", "color": "#45B7D1", "description": "Hair cutting and styling"},
        {"name": "nail", "display_name": "Nail Care", "type": "service", "color": "#96CEB4", "description": "Manicure and pedicure"},
        {"name": "body", "display_name": "Body Treatments", "type": "service", "color": "#FECA57", "description": "Body spa treatments"},
        {"name": "bridal", "display_name": "Bridal Services", "type": "service", "color": "#FFD700", "description": "Wedding beauty services"},
        
        # Inventory Categories
        {"name": "hair_care", "display_name": "Hair Care Products", "type": "inventory", "color": "#45B7D1", "description": "Hair products and tools"},
        {"name": "skincare", "display_name": "Skincare Products", "type": "inventory", "color": "#FF6B6B", "description": "Facial and skincare items"},
        {"name": "nail_care", "display_name": "Nail Care Items", "type": "inventory", "color": "#96CEB4", "description": "Nail polish and tools"},
        {"name": "disposables", "display_name": "Disposable Items", "type": "inventory", "color": "#95A5A6", "description": "Single-use items"},
        {"name": "equipment", "display_name": "Equipment", "type": "inventory", "color": "#34495E", "description": "Salon equipment"},
        
        # Expense Categories
        {"name": "rent", "display_name": "Rent & Utilities", "type": "expense", "color": "#E74C3C", "description": "Monthly rent and utilities"},
        {"name": "supplies", "display_name": "Supplies", "type": "expense", "color": "#F39C12", "description": "Product purchases"},
        {"name": "marketing", "display_name": "Marketing", "type": "expense", "color": "#9B59B6", "description": "Advertising and promotion"},
        {"name": "staff", "display_name": "Staff Expenses", "type": "expense", "color": "#3498DB", "description": "Staff salaries and benefits"},
    ]
    
    for cat_data in categories_data:
        existing = Category.query.filter_by(name=cat_data['name'], category_type=cat_data['type']).first()
        if not existing:
            category = Category(
                name=cat_data['name'],
                display_name=cat_data['display_name'],
                category_type=cat_data['type'],
                color=cat_data['color'],
                description=cat_data['description'],
                is_active=True,
                sort_order=0
            )
            db.session.add(category)
    
    db.session.commit()
    print("✅ Categories created")

def create_departments():
    """Create spa departments"""
    print("🏢 Creating departments...")
    
    departments_data = [
        {"name": "hair", "display_name": "Hair Department", "description": "Hair cutting, styling, and coloring"},
        {"name": "skincare", "display_name": "Skincare Department", "description": "Facial treatments and skincare"},
        {"name": "nail", "display_name": "Nail Care Department", "description": "Manicure and pedicure services"},
        {"name": "massage", "display_name": "Massage Therapy", "description": "Therapeutic and relaxation massage"},
        {"name": "reception", "display_name": "Reception & Customer Service", "description": "Front desk and customer relations"},
        {"name": "management", "display_name": "Management", "description": "Administrative and managerial roles"},
    ]
    
    for dept_data in departments_data:
        existing = Department.query.filter_by(name=dept_data['name']).first()
        if not existing:
            department = Department(
                name=dept_data['name'],
                display_name=dept_data['display_name'],
                description=dept_data['description'],
                is_active=True
            )
            db.session.add(department)
    
    db.session.commit()
    print("✅ Departments created")

def create_roles():
    """Create user roles if they don't exist"""
    print("👥 Creating roles...")
    
    roles_data = [
        {"name": "admin", "display_name": "Administrator", "description": "Full system access"},
        {"name": "manager", "display_name": "Manager", "description": "Management access"},
        {"name": "staff", "display_name": "Staff Member", "description": "Service provider access"},
        {"name": "cashier", "display_name": "Cashier", "description": "Billing and payment access"},
    ]
    
    for role_data in roles_data:
        existing = Role.query.filter_by(name=role_data['name']).first()
        if not existing:
            role = Role(
                name=role_data['name'],
                display_name=role_data['display_name'],
                description=role_data['description'],
                is_active=True
            )
            db.session.add(role)
    
    db.session.commit()
    print("✅ Roles created")

def create_staff_users():
    """Create comprehensive staff users"""
    print("👨‍💼 Creating staff users...")
    
    staff_data = [
        {
            'username': 'admin',
            'email': 'admin@unaki.com',
            'first_name': 'System',
            'last_name': 'Administrator',
            'role': 'admin',
            'department': 'management',
            'phone': '+91-9876543210',
            'designation': 'System Administrator',
            'commission_rate': 0.0,
            'hourly_rate': 0.0
        },
        {
            'username': 'sarah_manager',
            'email': 'sarah@unaki.com',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'role': 'manager',
            'department': 'management',
            'phone': '+91-9876543211',
            'designation': 'Spa Manager',
            'commission_rate': 5.0,
            'hourly_rate': 500.0
        },
        {
            'username': 'priya_hair',
            'email': 'priya@unaki.com',
            'first_name': 'Priya',
            'last_name': 'Sharma',
            'role': 'staff',
            'department': 'hair',
            'phone': '+91-9876543212',
            'designation': 'Senior Hair Stylist',
            'commission_rate': 15.0,
            'hourly_rate': 300.0
        },
        {
            'username': 'anita_facial',
            'email': 'anita@unaki.com',
            'first_name': 'Anita',
            'last_name': 'Verma',
            'role': 'staff',
            'department': 'skincare',
            'phone': '+91-9876543213',
            'designation': 'Facial Specialist',
            'commission_rate': 12.0,
            'hourly_rate': 250.0
        },
        {
            'username': 'ravi_massage',
            'email': 'ravi@unaki.com',
            'first_name': 'Ravi',
            'last_name': 'Kumar',
            'role': 'staff',
            'department': 'massage',
            'phone': '+91-9876543214',
            'designation': 'Massage Therapist',
            'commission_rate': 10.0,
            'hourly_rate': 200.0
        },
        {
            'username': 'meera_nails',
            'email': 'meera@unaki.com',
            'first_name': 'Meera',
            'last_name': 'Patel',
            'role': 'staff',
            'department': 'nail',
            'phone': '+91-9876543215',
            'designation': 'Nail Technician',
            'commission_rate': 8.0,
            'hourly_rate': 180.0
        },
        {
            'username': 'cashier_desk',
            'email': 'cashier@unaki.com',
            'first_name': 'Rekha',
            'last_name': 'Singh',
            'role': 'cashier',
            'department': 'reception',
            'phone': '+91-9876543216',
            'designation': 'Front Desk Cashier',
            'commission_rate': 2.0,
            'hourly_rate': 150.0
        }
    ]
    
    for staff in staff_data:
        existing = User.query.filter_by(username=staff['username']).first()
        if not existing:
            # Get department and role IDs
            department = Department.query.filter_by(name=staff['department']).first()
            role = Role.query.filter_by(name=staff['role']).first()
            
            user = User(
                username=staff['username'],
                email=staff['email'],
                first_name=staff['first_name'],
                last_name=staff['last_name'],
                role=staff['role'],
                role_id=role.id if role else None,
                department=staff['department'],
                department_id=department.id if department else None,
                phone=staff['phone'],
                designation=staff['designation'],
                commission_rate=staff['commission_rate'],
                hourly_rate=staff['hourly_rate'],
                employee_id=f"EMP{1000 + len(User.query.all())}",
                hire_date=date.today() - timedelta(days=30),
                is_active=True,
                gender='other',
                date_of_joining=date.today() - timedelta(days=30),
                working_days='1111100',  # Mon-Fri
                enable_face_checkin=True
            )
            user.set_password('admin123')
            db.session.add(user)
    
    db.session.commit()
    print("✅ Staff users created")

def create_customers():
    """Create sample customers"""
    print("👥 Creating customers...")
    
    customers_data = [
        {'first_name': 'Amita', 'last_name': 'Sharma', 'email': 'amita.sharma@email.com', 'phone': '+91-9876543220', 'gender': 'female'},
        {'first_name': 'Raj', 'last_name': 'Gupta', 'email': 'raj.gupta@email.com', 'phone': '+91-9876543221', 'gender': 'male'},
        {'first_name': 'Sunita', 'last_name': 'Verma', 'email': 'sunita.verma@email.com', 'phone': '+91-9876543222', 'gender': 'female'},
        {'first_name': 'Vikash', 'last_name': 'Singh', 'email': 'vikash.singh@email.com', 'phone': '+91-9876543223', 'gender': 'male'},
        {'first_name': 'Kavita', 'last_name': 'Agarwal', 'email': 'kavita.agarwal@email.com', 'phone': '+91-9876543224', 'gender': 'female'},
        {'first_name': 'Rohit', 'last_name': 'Jain', 'email': 'rohit.jain@email.com', 'phone': '+91-9876543225', 'gender': 'male'},
        {'first_name': 'Deepika', 'last_name': 'Mehta', 'email': 'deepika.mehta@email.com', 'phone': '+91-9876543226', 'gender': 'female'},
        {'first_name': 'Arjun', 'last_name': 'Reddy', 'email': 'arjun.reddy@email.com', 'phone': '+91-9876543227', 'gender': 'male'},
        {'first_name': 'Pooja', 'last_name': 'Khurana', 'email': 'pooja.khurana@email.com', 'phone': '+91-9876543228', 'gender': 'female'},
        {'first_name': 'Manish', 'last_name': 'Tiwari', 'email': 'manish.tiwari@email.com', 'phone': '+91-9876543229', 'gender': 'male'},
    ]
    
    for customer_data in customers_data:
        existing = Customer.query.filter_by(email=customer_data['email']).first()
        if not existing:
            customer = Customer(
                first_name=customer_data['first_name'],
                last_name=customer_data['last_name'],
                email=customer_data['email'],
                phone=customer_data['phone'],
                gender=customer_data['gender'],
                date_of_birth=date(1990, 1, 1) + timedelta(days=int(customer_data['phone'][-2:]) * 10),
                address=f"Sample Address, City - {customer_data['phone'][-6:]}",
                loyalty_points=50,
                total_visits=5,
                total_spent=2500.0,
                last_visit=datetime.now() - timedelta(days=15),
                is_active=True,
                marketing_consent=True,
                preferred_communication='email'
            )
            db.session.add(customer)
    
    db.session.commit()
    print("✅ Customers created")

def create_services():
    """Create comprehensive spa services"""
    print("💆‍♀️ Creating spa services...")
    
    services_data = [
        # Facial Services
        {'name': 'Classic Facial', 'duration': 60, 'price': 800.0, 'category': 'facial', 'description': 'Deep cleansing facial treatment'},
        {'name': 'Anti-Aging Facial', 'duration': 90, 'price': 1500.0, 'category': 'facial', 'description': 'Advanced anti-aging treatment'},
        {'name': 'Hydra Facial', 'duration': 75, 'price': 2000.0, 'category': 'facial', 'description': 'Medical-grade hydrating facial'},
        {'name': 'Gold Facial', 'duration': 90, 'price': 2500.0, 'category': 'facial', 'description': 'Luxury 24k gold facial'},
        {'name': 'Acne Treatment', 'duration': 60, 'price': 1200.0, 'category': 'facial', 'description': 'Specialized acne treatment'},
        
        # Hair Services
        {'name': 'Hair Cut & Style', 'duration': 45, 'price': 500.0, 'category': 'hair', 'description': 'Professional haircut and styling'},
        {'name': 'Hair Color', 'duration': 120, 'price': 2000.0, 'category': 'hair', 'description': 'Full hair coloring service'},
        {'name': 'Hair Highlights', 'duration': 150, 'price': 2500.0, 'category': 'hair', 'description': 'Professional highlighting'},
        {'name': 'Hair Spa Treatment', 'duration': 90, 'price': 1200.0, 'category': 'hair', 'description': 'Deep conditioning treatment'},
        {'name': 'Keratin Treatment', 'duration': 180, 'price': 4000.0, 'category': 'hair', 'description': 'Smoothing keratin treatment'},
        {'name': 'Hair Wash & Blow Dry', 'duration': 30, 'price': 300.0, 'category': 'hair', 'description': 'Professional wash and style'},
        
        # Massage Services
        {'name': 'Swedish Massage', 'duration': 60, 'price': 1000.0, 'category': 'massage', 'description': 'Full body relaxation massage'},
        {'name': 'Deep Tissue Massage', 'duration': 90, 'price': 1500.0, 'category': 'massage', 'description': 'Therapeutic deep muscle massage'},
        {'name': 'Hot Stone Massage', 'duration': 90, 'price': 1800.0, 'category': 'massage', 'description': 'Heated stone massage therapy'},
        {'name': 'Aromatherapy Massage', 'duration': 75, 'price': 1300.0, 'category': 'massage', 'description': 'Essential oil massage'},
        {'name': 'Head & Shoulder Massage', 'duration': 30, 'price': 600.0, 'category': 'massage', 'description': 'Upper body stress relief'},
        
        # Nail Services
        {'name': 'Basic Manicure', 'duration': 45, 'price': 500.0, 'category': 'nail', 'description': 'Classic nail grooming'},
        {'name': 'Gel Manicure', 'duration': 60, 'price': 800.0, 'category': 'nail', 'description': 'Long-lasting gel polish'},
        {'name': 'Basic Pedicure', 'duration': 60, 'price': 600.0, 'category': 'nail', 'description': 'Foot care and polish'},
        {'name': 'Spa Pedicure', 'duration': 90, 'price': 1000.0, 'category': 'nail', 'description': 'Luxury foot spa treatment'},
        {'name': 'Nail Art', 'duration': 30, 'price': 400.0, 'category': 'nail', 'description': 'Creative nail design'},
        
        # Body Treatments
        {'name': 'Body Polish', 'duration': 60, 'price': 1200.0, 'category': 'body', 'description': 'Full body exfoliation'},
        {'name': 'Body Wrap', 'duration': 90, 'price': 1800.0, 'category': 'body', 'description': 'Detoxifying body wrap'},
        {'name': 'Tan Removal', 'duration': 45, 'price': 800.0, 'category': 'body', 'description': 'Professional tan removal'},
        
        # Bridal Services
        {'name': 'Bridal Makeup', 'duration': 120, 'price': 3000.0, 'category': 'bridal', 'description': 'Complete bridal makeup'},
        {'name': 'Bridal Hair Styling', 'duration': 90, 'price': 2500.0, 'category': 'bridal', 'description': 'Wedding hair styling'},
    ]
    
    for service_data in services_data:
        existing = Service.query.filter_by(name=service_data['name']).first()
        if not existing:
            category = Category.query.filter_by(name=service_data['category'], category_type='service').first()
            service = Service(
                name=service_data['name'],
                description=service_data['description'],
                duration=service_data['duration'],
                price=service_data['price'],
                category_id=category.id if category else None,
                category=service_data['category'],
                is_active=True
            )
            db.session.add(service)
    
    db.session.commit()
    print("✅ Services created")

def create_suppliers():
    """Create supplier records"""
    print("🏪 Creating suppliers...")
    
    suppliers_data = [
        {'name': 'Professional Hair Supplies', 'contact': 'Rahul Enterprises', 'email': 'sales@hairsupplies.com', 'phone': '+91-9876501001'},
        {'name': 'Beauty World Cosmetics', 'contact': 'Beauty Distribution', 'email': 'orders@beautyworld.com', 'phone': '+91-9876501002'},
        {'name': 'Spa Equipment Co', 'contact': 'Equipment Suppliers', 'email': 'info@spaequipment.com', 'phone': '+91-9876501003'},
        {'name': 'Natural Beauty Products', 'contact': 'Organic Supplies', 'email': 'natural@beautyproducts.com', 'phone': '+91-9876501004'},
        {'name': 'Aromatherapy Supplies', 'contact': 'Essential Oils Ltd', 'email': 'orders@aromatherapy.com', 'phone': '+91-9876501005'},
    ]
    
    for supplier_data in suppliers_data:
        existing = Supplier.query.filter_by(name=supplier_data['name']).first()
        if not existing:
            supplier = Supplier(
                name=supplier_data['name'],
                contact_person=supplier_data['contact'],
                email=supplier_data['email'],
                phone=supplier_data['phone'],
                address=f"Supplier Address, {supplier_data['name']} Location",
                payment_terms='Net 30',
                lead_time_days=7,
                minimum_order_amount=1000.0,
                rating=4.5,
                is_active=True
            )
            db.session.add(supplier)
    
    db.session.commit()
    print("✅ Suppliers created")

def create_inventory_items():
    """Create comprehensive inventory items"""
    print("📦 Creating inventory items...")
    
    inventory_data = [
        # Hair Care Products
        {'name': 'Professional Shampoo 1L', 'category': 'hair_care', 'stock': 5000.0, 'unit': 'ml', 'cost': 0.02, 'price': 0.08},
        {'name': 'Hair Conditioner 1L', 'category': 'hair_care', 'stock': 3500.0, 'unit': 'ml', 'cost': 0.025, 'price': 0.10},
        {'name': 'Hair Color Tubes', 'category': 'hair_care', 'stock': 50.0, 'unit': 'tube', 'cost': 15.0, 'price': 45.0},
        {'name': 'Hair Serum 100ml', 'category': 'hair_care', 'stock': 200.0, 'unit': 'bottle', 'cost': 8.0, 'price': 25.0},
        
        # Skincare Products
        {'name': 'Vitamin C Serum 30ml', 'category': 'skincare', 'stock': 100.0, 'unit': 'bottle', 'cost': 25.0, 'price': 80.0},
        {'name': 'Clay Face Masks', 'category': 'skincare', 'stock': 200.0, 'unit': 'pcs', 'cost': 3.5, 'price': 12.0},
        {'name': 'Moisturizer 50ml', 'category': 'skincare', 'stock': 150.0, 'unit': 'bottle', 'cost': 12.0, 'price': 35.0},
        {'name': 'Cleanser 200ml', 'category': 'skincare', 'stock': 120.0, 'unit': 'bottle', 'cost': 10.0, 'price': 28.0},
        
        # Nail Care
        {'name': 'Gel Nail Polish', 'category': 'nail_care', 'stock': 80.0, 'unit': 'bottle', 'cost': 8.0, 'price': 25.0},
        {'name': 'Cuticle Oil 15ml', 'category': 'nail_care', 'stock': 100.0, 'unit': 'bottle', 'cost': 4.0, 'price': 15.0},
        {'name': 'Nail Files', 'category': 'nail_care', 'stock': 500.0, 'unit': 'pcs', 'cost': 0.5, 'price': 2.0},
        
        # Disposables
        {'name': 'Disposable Towels', 'category': 'disposables', 'stock': 1000.0, 'unit': 'pcs', 'cost': 0.15, 'price': 0.0},
        {'name': 'Latex Gloves', 'category': 'disposables', 'stock': 500.0, 'unit': 'pcs', 'cost': 0.08, 'price': 0.0},
        {'name': 'Cotton Pads', 'category': 'disposables', 'stock': 2000.0, 'unit': 'pcs', 'cost': 0.05, 'price': 0.0},
        {'name': 'Face Tissues', 'category': 'disposables', 'stock': 100.0, 'unit': 'box', 'cost': 3.0, 'price': 0.0},
        
        # Equipment
        {'name': 'Hair Dryer Professional', 'category': 'equipment', 'stock': 5.0, 'unit': 'pcs', 'cost': 2500.0, 'price': 0.0},
        {'name': 'Facial Steamer', 'category': 'equipment', 'stock': 3.0, 'unit': 'pcs', 'cost': 3500.0, 'price': 0.0},
        {'name': 'Massage Table', 'category': 'equipment', 'stock': 4.0, 'unit': 'pcs', 'cost': 8000.0, 'price': 0.0},
    ]
    
    for item_data in inventory_data:
        existing = Inventory.query.filter_by(name=item_data['name']).first()
        if not existing:
            category = Category.query.filter_by(name=item_data['category'], category_type='inventory').first()
            supplier = Supplier.query.first()  # Use first available supplier
            
            sku = generate_sku(item_data['name'])
            
            inventory_item = Inventory(
                name=item_data['name'],
                sku=sku,
                description=f"Professional {item_data['name']} for spa services",
                category_id=category.id if category else None,
                category=item_data['category'],
                current_stock=item_data['stock'],
                min_stock_level=item_data['stock'] * 0.2,  # 20% of current stock
                max_stock_level=item_data['stock'] * 2,    # 200% of current stock
                reorder_point=item_data['stock'] * 0.3,    # 30% of current stock
                reorder_quantity=item_data['stock'],
                base_unit=item_data['unit'],
                selling_unit=item_data['unit'],
                cost_price=item_data['cost'],
                selling_price=item_data['price'],
                primary_supplier_id=supplier.id if supplier else None,
                supplier_name=supplier.name if supplier else 'Default Supplier',
                item_type='both' if item_data['price'] > 0 else 'consumable',
                is_service_item=True,
                is_retail_item=item_data['price'] > 0,
                has_expiry=item_data['category'] in ['skincare', 'hair_care'],
                expiry_date=date.today() + timedelta(days=730) if item_data['category'] in ['skincare', 'hair_care'] else None,
                is_active=True
            )
            db.session.add(inventory_item)
    
    db.session.commit()
    print("✅ Inventory items created")

def create_packages():
    """Create comprehensive spa packages"""
    print("📦 Creating spa packages...")
    
    packages_data = [
        # Prepaid Packages
        {
            'name': 'Prepaid Spa Package - Bronze',
            'description': 'Pay ₹15,000 get ₹17,500 credit - 15% benefit',
            'type': 'prepaid',
            'price': 15000,
            'credit': 17500,
            'discount': 15.0,
            'validity': 60,
            'sessions': 1
        },
        {
            'name': 'Prepaid Spa Package - Silver',
            'description': 'Pay ₹25,000 get ₹31,250 credit - 25% benefit',
            'type': 'prepaid',
            'price': 25000,
            'credit': 31250,
            'discount': 25.0,
            'validity': 90,
            'sessions': 1
        },
        
        # Service Packages
        {
            'name': 'Facial Package - 3 Sessions',
            'description': 'Three classic facial sessions with 20% discount',
            'type': 'service_package',
            'price': 1920,  # 3 * 800 * 0.8
            'discount': 20.0,
            'validity': 90,
            'sessions': 3
        },
        {
            'name': 'Hair Care Package - 5 Sessions',
            'description': 'Five hair services with 25% discount',
            'type': 'service_package',
            'price': 1875,  # 5 * 500 * 0.75
            'discount': 25.0,
            'validity': 120,
            'sessions': 5
        },
        
        # Membership Packages
        {
            'name': 'Monthly Spa Membership',
            'description': 'Unlimited spa services for one month',
            'type': 'membership',
            'price': 5000,
            'discount': 30.0,
            'validity': 30,
            'sessions': 20
        },
        {
            'name': 'Yearly Salon Membership',
            'description': 'Annual membership with 20% discount on all services',
            'type': 'yearly_membership',
            'price': 12000,
            'credit': 2000,
            'discount': 20.0,
            'validity': 365,
            'sessions': 100
        }
    ]
    
    for pkg_data in packages_data:
        existing = Package.query.filter_by(name=pkg_data['name']).first()
        if not existing:
            package = Package(
                name=pkg_data['name'],
                description=pkg_data['description'],
                package_type=pkg_data['type'],
                total_price=pkg_data['price'],
                credit_amount=pkg_data.get('credit', 0.0),
                discount_percentage=pkg_data['discount'],
                validity_days=pkg_data['validity'],
                duration_months=pkg_data['validity'] // 30,
                total_sessions=pkg_data['sessions'],
                is_active=True
            )
            db.session.add(package)
    
    db.session.commit()
    print("✅ Packages created")

def create_customer_packages():
    """Create customer package purchases"""
    print("🎫 Creating customer packages...")
    
    customers = Customer.query.limit(5).all()
    packages = Package.query.limit(3).all()
    
    for i, customer in enumerate(customers):
        if i < len(packages):
            package = packages[i]
            existing = CustomerPackage.query.filter_by(client_id=customer.id, package_id=package.id).first()
            if not existing:
                customer_package = CustomerPackage(
                    client_id=customer.id,
                    package_id=package.id,
                    purchase_date=datetime.now() - timedelta(days=10),
                    expiry_date=datetime.now() + timedelta(days=package.validity_days),
                    sessions_used=2,
                    total_sessions=package.total_sessions,
                    amount_paid=package.total_price,
                    is_active=True
                )
                db.session.add(customer_package)
    
    db.session.commit()
    print("✅ Customer packages created")

def create_appointments():
    """Create sample appointments"""
    print("📅 Creating appointments...")
    
    customers = Customer.query.all()
    services = Service.query.all()
    staff = User.query.filter(User.role.in_(['staff', 'manager'])).all()
    
    # Create appointments for the last 30 days and next 7 days
    for day_offset in range(-30, 8):
        appointment_date = datetime.now() + timedelta(days=day_offset)
        
        # Skip if weekend for most appointments
        if appointment_date.weekday() < 5:  # Monday to Friday
            num_appointments = 3 if day_offset <= 0 else 2  # More past appointments
            
            for i in range(num_appointments):
                if customers and services and staff:
                    customer = customers[i % len(customers)]
                    service = services[i % len(services)]
                    staff_member = staff[i % len(staff)]
                    
                    # Set appointment time
                    hour = 10 + (i * 2) % 8  # Between 10 AM and 6 PM
                    appointment_time = appointment_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    end_time = appointment_time + timedelta(minutes=service.duration)
                    
                    existing = Appointment.query.filter_by(
                        client_id=customer.id,
                        appointment_date=appointment_time
                    ).first()
                    
                    if not existing:
                        status = 'completed' if day_offset < 0 else 'scheduled'
                        appointment = Appointment(
                            client_id=customer.id,
                            service_id=service.id,
                            staff_id=staff_member.id,
                            appointment_date=appointment_time,
                            end_time=end_time,
                            status=status,
                            amount=service.price,
                            discount=0.0,
                            tips=50.0 if status == 'completed' else 0.0,
                            is_paid=status == 'completed',
                            notes=f"Sample appointment for {service.name}"
                        )
                        db.session.add(appointment)
    
    db.session.commit()
    print("✅ Appointments created")

def create_expenses():
    """Create sample expense records"""
    print("💰 Creating expenses...")
    
    admin_user = User.query.filter_by(role='admin').first()
    rent_category = Category.query.filter_by(name='rent', category_type='expense').first()
    supplies_category = Category.query.filter_by(name='supplies', category_type='expense').first()
    
    if admin_user:
        expenses_data = [
            {'description': 'Monthly Rent Payment', 'amount': 25000.0, 'category': 'rent', 'date': date.today() - timedelta(days=5)},
            {'description': 'Electricity Bill', 'amount': 3500.0, 'category': 'rent', 'date': date.today() - timedelta(days=10)},
            {'description': 'Hair Product Purchase', 'amount': 8000.0, 'category': 'supplies', 'date': date.today() - timedelta(days=15)},
            {'description': 'Skincare Product Restock', 'amount': 12000.0, 'category': 'supplies', 'date': date.today() - timedelta(days=7)},
            {'description': 'Equipment Maintenance', 'amount': 2500.0, 'category': 'supplies', 'date': date.today() - timedelta(days=3)},
        ]
        
        for expense_data in expenses_data:
            category = Category.query.filter_by(name=expense_data['category'], category_type='expense').first()
            expense = Expense(
                description=expense_data['description'],
                amount=expense_data['amount'],
                category_id=category.id if category else None,
                category=expense_data['category'],
                expense_date=expense_data['date'],
                created_by=admin_user.id,
                receipt_number=f"REC{str(uuid.uuid4())[:8].upper()}",
                notes=f"Sample expense for {expense_data['description']}"
            )
            db.session.add(expense)
    
    db.session.commit()
    print("✅ Expenses created")

def create_attendance_records():
    """Create staff attendance records"""
    print("⏰ Creating attendance records...")
    
    staff_members = User.query.filter(User.role.in_(['staff', 'manager'])).all()
    
    for staff in staff_members:
        # Create attendance for last 30 days
        for day_offset in range(-30, 1):
            attendance_date = date.today() + timedelta(days=day_offset)
            
            # Skip weekends for most staff
            if attendance_date.weekday() < 5:  # Monday to Friday
                existing = Attendance.query.filter_by(staff_id=staff.id, date=attendance_date).first()
                if not existing:
                    check_in = datetime.combine(attendance_date, datetime.min.time().replace(hour=9, minute=0))
                    check_out = datetime.combine(attendance_date, datetime.min.time().replace(hour=18, minute=0))
                    
                    attendance = Attendance(
                        staff_id=staff.id,
                        check_in_time=check_in,
                        check_out_time=check_out,
                        total_hours=9.0,
                        date=attendance_date,
                        check_in_method='manual',
                        notes='Regular working day'
                    )
                    db.session.add(attendance)
    
    db.session.commit()
    print("✅ Attendance records created")

def create_performance_records():
    """Create staff performance records"""
    print("📊 Creating performance records...")
    
    staff_members = User.query.filter(User.role.in_(['staff', 'manager'])).all()
    current_date = datetime.now()
    
    for staff in staff_members:
        # Create performance for last 3 months
        for month_offset in range(-3, 1):
            target_date = current_date + timedelta(days=month_offset * 30)
            month = target_date.month
            year = target_date.year
            
            existing = StaffPerformance.query.filter_by(
                staff_id=staff.id, 
                month=month, 
                year=year
            ).first()
            
            if not existing:
                performance = StaffPerformance(
                    staff_id=staff.id,
                    month=month,
                    year=year,
                    services_completed=25 + (month_offset * 5),  # Varying performance
                    revenue_generated=15000.0 + (month_offset * 2000),
                    client_ratings_avg=4.2 + (month_offset * 0.1),
                    attendance_percentage=95.0 + month_offset,
                    commission_earned=staff.commission_rate * 150
                )
                db.session.add(performance)
    
    db.session.commit()
    print("✅ Performance records created")

def create_reviews():
    """Create customer reviews"""
    print("⭐ Creating customer reviews...")
    
    completed_appointments = Appointment.query.filter_by(status='completed').limit(10).all()
    
    review_comments = [
        "Excellent service! Very professional and relaxing.",
        "Great experience, will definitely come back.",
        "Amazing staff and beautiful ambiance.",
        "Very satisfied with the quality of service.",
        "Professional service with attention to detail.",
        "Relaxing environment and skilled therapists.",
        "Good value for money and quality service.",
        "Friendly staff and clean facilities.",
        "Exceptional service quality and hospitality.",
        "Highly recommend this spa to everyone."
    ]
    
    for i, appointment in enumerate(completed_appointments):
        existing = Review.query.filter_by(appointment_id=appointment.id).first()
        if not existing:
            review = Review(
                client_id=appointment.client_id,
                appointment_id=appointment.id,
                staff_id=appointment.staff_id,
                service_id=appointment.service_id,
                rating=4 + (i % 2),  # Ratings between 4-5
                comment=review_comments[i % len(review_comments)],
                is_public=True
            )
            db.session.add(review)
    
    db.session.commit()
    print("✅ Reviews created")

def create_stock_movements():
    """Create stock movement records"""
    print("📈 Creating stock movements...")
    
    inventory_items = Inventory.query.limit(10).all()
    admin_user = User.query.filter_by(role='admin').first()
    
    if admin_user:
        for item in inventory_items:
            # Create purchase movement
            purchase_movement = StockMovement(
                inventory_id=item.id,
                movement_type='purchase',
                quantity=item.current_stock,
                unit=item.base_unit,
                unit_cost=item.cost_price,
                total_cost=item.current_stock * item.cost_price,
                reference_type='purchase_order',
                reason='Initial stock purchase',
                created_by=admin_user.id
            )
            db.session.add(purchase_movement)
            
            # Create some consumption movements
            if item.is_service_item:
                consumption_movement = StockMovement(
                    inventory_id=item.id,
                    movement_type='service_use',
                    quantity=-10.0,  # 10 units consumed
                    unit=item.base_unit,
                    reference_type='service',
                    reason='Service consumption',
                    created_by=admin_user.id
                )
                db.session.add(consumption_movement)
    
    db.session.commit()
    print("✅ Stock movements created")

def create_business_settings():
    """Create business configuration settings"""
    print("⚙️ Creating business settings...")
    
    settings_data = [
        {'key': 'business_name', 'value': 'UNAKI Spa & Salon', 'category': 'business', 'display_name': 'Business Name'},
        {'key': 'business_address', 'value': 'Shop No. 123, Beauty Plaza, Main Road, City - 400001', 'category': 'business', 'display_name': 'Business Address'},
        {'key': 'business_phone', 'value': '+91-9876543210', 'category': 'business', 'display_name': 'Business Phone'},
        {'key': 'business_email', 'value': 'info@unaki.com', 'category': 'business', 'display_name': 'Business Email'},
        {'key': 'tax_rate', 'value': '18.0', 'category': 'business', 'display_name': 'Tax Rate (%)'},
        {'key': 'currency', 'value': 'INR', 'category': 'business', 'display_name': 'Currency'},
        {'key': 'opening_time', 'value': '09:00', 'category': 'business', 'display_name': 'Opening Time'},
        {'key': 'closing_time', 'value': '20:00', 'category': 'business', 'display_name': 'Closing Time'},
        {'key': 'appointment_buffer', 'value': '15', 'category': 'appointments', 'display_name': 'Appointment Buffer (minutes)'},
        {'key': 'max_advance_booking', 'value': '60', 'category': 'appointments', 'display_name': 'Max Advance Booking (days)'},
    ]
    
    for setting_data in settings_data:
        existing = SystemSetting.query.filter_by(key=setting_data['key']).first()
        if not existing:
            setting = SystemSetting(
                key=setting_data['key'],
                value=setting_data['value'],
                category=setting_data['category'],
                display_name=setting_data['display_name'],
                description=f"Configuration for {setting_data['display_name']}",
                data_type='string',
                is_public=True
            )
            db.session.add(setting)
    
    db.session.commit()
    print("✅ Business settings created")

if __name__ == '__main__':
    populate_all_data()
