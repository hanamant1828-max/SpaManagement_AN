#!/usr/bin/env python3
"""
Demo Data Script for Spa Management System
Creates comprehensive sample data for client presentation
"""
from app import app, db
from models import (User, Customer, Service, Appointment, Category, 
                   InventoryProduct, InventoryCategory, InventorySupplier, 
                   Package, PackageService, CustomerPackage)
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
import random

def create_demo_data():
    with app.app_context():
        print("🎯 Creating comprehensive demo data...")
        
        # 1. Create Service Categories
        service_categories = [
            {"name": "facial", "display_name": "Facial Treatments", "description": "All facial treatments and skincare", "color": "#e74c3c"},
            {"name": "massage", "display_name": "Massage Therapy", "description": "Relaxing massage services", "color": "#3498db"},
            {"name": "haircare", "display_name": "Hair Care", "description": "Hair treatments and styling", "color": "#f39c12"},
            {"name": "nails", "display_name": "Nail Services", "description": "Manicure and pedicure services", "color": "#9b59b6"},
            {"name": "body", "display_name": "Body Treatments", "description": "Full body wellness treatments", "color": "#1abc9c"}
        ]
        
        for cat_data in service_categories:
            category = Category.query.filter_by(name=cat_data["name"], category_type="service").first()
            if not category:
                category = Category(
                    name=cat_data["name"],
                    display_name=cat_data["display_name"],
                    description=cat_data["description"],
                    category_type="service",
                    color=cat_data["color"]
                )
                db.session.add(category)
        
        db.session.commit()
        
        # 2. Create 12 Premium Services
        services_data = [
            {"name": "Royal Gold Facial", "description": "Luxurious 24k gold facial treatment with anti-aging benefits", "duration": 90, "price": 5500.00, "category": "facial"},
            {"name": "Deep Tissue Massage", "description": "Therapeutic deep tissue massage for muscle tension relief", "duration": 75, "price": 3500.00, "category": "massage"},
            {"name": "Keratin Hair Treatment", "description": "Professional keratin smoothing treatment for silky hair", "duration": 180, "price": 8500.00, "category": "haircare"},
            {"name": "Gel Manicure & Art", "description": "Premium gel manicure with custom nail art design", "duration": 60, "price": 1800.00, "category": "nails"},
            {"name": "Hot Stone Therapy", "description": "Relaxing hot stone massage with aromatherapy oils", "duration": 90, "price": 4200.00, "category": "massage"},
            {"name": "Diamond Pedicure", "description": "Luxury pedicure with diamond scrub and organic treatment", "duration": 75, "price": 2500.00, "category": "nails"},
            {"name": "Anti-Aging Facial", "description": "Advanced anti-aging facial with vitamin C and collagen", "duration": 75, "price": 4500.00, "category": "facial"},
            {"name": "Hair Spa & Styling", "description": "Complete hair spa treatment with professional styling", "duration": 120, "price": 3800.00, "category": "haircare"},
            {"name": "Full Body Scrub", "description": "Exfoliating body scrub with moisturizing treatment", "duration": 60, "price": 3200.00, "category": "body"},
            {"name": "Aromatherapy Massage", "description": "Relaxing aromatherapy massage with essential oils", "duration": 60, "price": 3000.00, "category": "massage"},
            {"name": "Bridal Makeup & Hair", "description": "Complete bridal makeover package with hair styling", "duration": 240, "price": 15000.00, "category": "haircare"},
            {"name": "Express Facial", "description": "Quick refreshing facial perfect for busy schedules", "duration": 45, "price": 2500.00, "category": "facial"}
        ]
        
        for service_data in services_data:
            service = Service.query.filter_by(name=service_data["name"]).first()
            if not service:
                category = Category.query.filter_by(name=service_data["category"], category_type="service").first()
                service = Service(
                    name=service_data["name"],
                    description=service_data["description"],
                    duration=service_data["duration"],
                    price=service_data["price"],
                    category=service_data["category"],
                    category_id=category.id if category else None,
                    is_active=True
                )
                db.session.add(service)
        
        db.session.commit()
        print("✅ Services created successfully!")
        
        # 3. Create Staff Members
        staff_data = [
            {"username": "priya_manager", "email": "priya@spa.com", "first_name": "Priya", "last_name": "Sharma", "role": "manager", "phone": "+91 98765 43210"},
            {"username": "anjali_senior", "email": "anjali@spa.com", "first_name": "Anjali", "last_name": "Mehta", "role": "staff", "phone": "+91 98765 43211"},
            {"username": "ravi_masseur", "email": "ravi@spa.com", "first_name": "Ravi", "last_name": "Kumar", "role": "staff", "phone": "+91 98765 43212"},
            {"username": "sneha_beautician", "email": "sneha@spa.com", "first_name": "Sneha", "last_name": "Patel", "role": "staff", "phone": "+91 98765 43213"},
            {"username": "arjun_hairstylist", "email": "arjun@spa.com", "first_name": "Arjun", "last_name": "Singh", "role": "staff", "phone": "+91 98765 43214"},
            {"username": "kavya_cashier", "email": "kavya@spa.com", "first_name": "Kavya", "last_name": "Reddy", "role": "cashier", "phone": "+91 98765 43215"}
        ]
        
        for staff in staff_data:
            user = User.query.filter_by(username=staff["username"]).first()
            if not user:
                user = User(
                    username=staff["username"],
                    email=staff["email"],
                    first_name=staff["first_name"],
                    last_name=staff["last_name"],
                    role=staff["role"],
                    phone=staff["phone"],
                    is_active=True,
                    commission_rate=15.0 if staff["role"] == "staff" else 0.0,
                    hourly_rate=500.0,
                    date_of_joining=date.today() - timedelta(days=random.randint(30, 365))
                )
                user.set_password("staff123")
                db.session.add(user)
        
        db.session.commit()
        print("✅ Staff members created successfully!")
        
        # 4. Create 12 Premium Customers
        customers_data = [
            {"first_name": "Aisha", "last_name": "Verma", "email": "aisha.verma@email.com", "phone": "+91 9876543201", "gender": "female"},
            {"first_name": "Rohit", "last_name": "Agarwal", "email": "rohit.agarwal@email.com", "phone": "+91 9876543202", "gender": "male"},
            {"first_name": "Meera", "last_name": "Joshi", "email": "meera.joshi@email.com", "phone": "+91 9876543203", "gender": "female"},
            {"first_name": "Vikram", "last_name": "Malhotra", "email": "vikram.malhotra@email.com", "phone": "+91 9876543204", "gender": "male"},
            {"first_name": "Neha", "last_name": "Kapoor", "email": "neha.kapoor@email.com", "phone": "+91 9876543205", "gender": "female"},
            {"first_name": "Arjun", "last_name": "Gupta", "email": "arjun.gupta@email.com", "phone": "+91 9876543206", "gender": "male"},
            {"first_name": "Pooja", "last_name": "Nair", "email": "pooja.nair@email.com", "phone": "+91 9876543207", "gender": "female"},
            {"first_name": "Karan", "last_name": "Sethi", "email": "karan.sethi@email.com", "phone": "+91 9876543208", "gender": "male"},
            {"first_name": "Riya", "last_name": "Bansal", "email": "riya.bansal@email.com", "phone": "+91 9876543209", "gender": "female"},
            {"first_name": "Amit", "last_name": "Rao", "email": "amit.rao@email.com", "phone": "+91 9876543210", "gender": "male"},
            {"first_name": "Shreya", "last_name": "Iyer", "email": "shreya.iyer@email.com", "phone": "+91 9876543211", "gender": "female"},
            {"first_name": "Raj", "last_name": "Thakur", "email": "raj.thakur@email.com", "phone": "+91 9876543212", "gender": "male"}
        ]
        
        for customer_data in customers_data:
            customer = Customer.query.filter_by(email=customer_data["email"]).first()
            if not customer:
                customer = Customer(
                    first_name=customer_data["first_name"],
                    last_name=customer_data["last_name"],
                    email=customer_data["email"],
                    phone=customer_data["phone"],
                    gender=customer_data["gender"],
                    date_of_birth=date(1990, 1, 1) + timedelta(days=random.randint(0, 10950)),
                    address=f"{random.randint(1, 999)} MG Road, Bangalore, Karnataka 560001",
                    total_visits=random.randint(5, 25),
                    total_spent=random.uniform(5000, 50000),
                    loyalty_points=random.randint(50, 500),
                    is_vip=random.choice([True, False]),
                    preferred_communication="whatsapp",
                    last_visit=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(customer)
        
        db.session.commit()
        print("✅ Customers created successfully!")
        
        # 5. Create Inventory Categories and Suppliers
        inv_categories = [
            {"category_name": "Skincare Products", "description": "Face creams, serums, and skincare essentials"},
            {"category_name": "Hair Care", "description": "Shampoos, conditioners, and hair treatments"},
            {"category_name": "Massage Oils", "description": "Essential oils and massage therapy products"},
            {"category_name": "Nail Care", "description": "Nail polishes, tools, and accessories"},
            {"category_name": "Equipment", "description": "Spa and salon equipment and tools"}
        ]
        
        for cat_data in inv_categories:
            category = InventoryCategory.query.filter_by(category_name=cat_data["category_name"]).first()
            if not category:
                category = InventoryCategory(
                    category_name=cat_data["category_name"],
                    description=cat_data["description"],
                    is_active=True,
                    created_by="admin"
                )
                db.session.add(category)
        
        # Create Suppliers
        suppliers_data = [
            {"supplier_name": "Beauty Plus Supplies", "supplier_code": "BPS001", "contact_person": "Rajesh Kumar", "phone": "+91 9876543301"},
            {"supplier_name": "Wellness Products Ltd", "supplier_code": "WPL002", "contact_person": "Sunita Sharma", "phone": "+91 9876543302"},
            {"supplier_name": "Professional Spa Equipment", "supplier_code": "PSE003", "contact_person": "Manoj Gupta", "phone": "+91 9876543303"}
        ]
        
        for supplier_data in suppliers_data:
            supplier = InventorySupplier.query.filter_by(supplier_code=supplier_data["supplier_code"]).first()
            if not supplier:
                supplier = InventorySupplier(
                    supplier_name=supplier_data["supplier_name"],
                    supplier_code=supplier_data["supplier_code"],
                    contact_person=supplier_data["contact_person"],
                    phone=supplier_data["phone"],
                    email=f"{supplier_data['supplier_code'].lower()}@suppliers.com",
                    address="123 Commercial Street, Mumbai, Maharashtra",
                    is_active=True,
                    created_by="admin"
                )
                db.session.add(supplier)
        
        db.session.commit()
        
        # 6. Create 15 Inventory Items
        inventory_data = [
            {"name": "Gold Facial Cream", "product_code": "GFC001", "unit": "bottle", "unit_cost": 850.00, "selling_price": 1200.00, "current_stock": 25, "category": "Skincare Products"},
            {"name": "Keratin Hair Serum", "product_code": "KHS002", "unit": "bottle", "unit_cost": 650.00, "selling_price": 950.00, "current_stock": 18, "category": "Hair Care"},
            {"name": "Aromatherapy Essential Oil", "product_code": "AEO003", "unit": "bottle", "unit_cost": 450.00, "selling_price": 750.00, "current_stock": 30, "category": "Massage Oils"},
            {"name": "Premium Nail Polish Set", "product_code": "PNS004", "unit": "set", "unit_cost": 320.00, "selling_price": 480.00, "current_stock": 12, "category": "Nail Care"},
            {"name": "Professional Hair Dryer", "product_code": "PHD005", "unit": "piece", "unit_cost": 3500.00, "selling_price": 5200.00, "current_stock": 3, "category": "Equipment"},
            {"name": "Anti-Aging Serum", "product_code": "AAS006", "unit": "bottle", "unit_cost": 950.00, "selling_price": 1400.00, "current_stock": 20, "category": "Skincare Products"},
            {"name": "Hot Stone Set", "product_code": "HSS007", "unit": "set", "unit_cost": 2800.00, "selling_price": 4200.00, "current_stock": 5, "category": "Equipment"},
            {"name": "Organic Face Mask", "product_code": "OFM008", "unit": "pack", "unit_cost": 180.00, "selling_price": 280.00, "current_stock": 45, "category": "Skincare Products"},
            {"name": "Hair Color Kit", "product_code": "HCK009", "unit": "kit", "unit_cost": 420.00, "selling_price": 650.00, "current_stock": 15, "category": "Hair Care"},
            {"name": "Massage Table", "product_code": "MT010", "unit": "piece", "unit_cost": 15000.00, "selling_price": 22000.00, "current_stock": 2, "category": "Equipment"},
            {"name": "Cuticle Care Oil", "product_code": "CCO011", "unit": "bottle", "unit_cost": 220.00, "selling_price": 350.00, "current_stock": 28, "category": "Nail Care"},
            {"name": "Vitamin C Facial Kit", "product_code": "VCF012", "unit": "kit", "unit_cost": 380.00, "selling_price": 580.00, "current_stock": 22, "category": "Skincare Products"},
            {"name": "Professional Scissors Set", "product_code": "PSS013", "unit": "set", "unit_cost": 1200.00, "selling_price": 1800.00, "current_stock": 8, "category": "Equipment"},
            {"name": "Lavender Body Oil", "product_code": "LBO014", "unit": "bottle", "unit_cost": 320.00, "selling_price": 480.00, "current_stock": 35, "category": "Massage Oils"},
            {"name": "UV Nail Lamp", "product_code": "UNL015", "unit": "piece", "unit_cost": 2500.00, "selling_price": 3750.00, "current_stock": 4, "category": "Equipment"}
        ]
        
        for inv_data in inventory_data:
            product = InventoryProduct.query.filter_by(product_code=inv_data["product_code"]).first()
            if not product:
                category = InventoryCategory.query.filter_by(category_name=inv_data["category"]).first()
                supplier = InventorySupplier.query.first()
                
                product = InventoryProduct(
                    name=inv_data["name"],
                    product_code=inv_data["product_code"],
                    unit=inv_data["unit"],
                    unit_cost=inv_data["unit_cost"],
                    selling_price=inv_data["selling_price"],
                    current_stock=inv_data["current_stock"],
                    min_stock_level=5,
                    max_stock_level=100,
                    reorder_level=10,
                    category_id=category.category_id if category else None,
                    supplier_id=supplier.supplier_id if supplier else None,
                    is_active=True,
                    created_by="admin"
                )
                db.session.add(product)
        
        db.session.commit()
        print("✅ Inventory items created successfully!")
        
        # 7. Create Sample Appointments for next 7 days
        services = Service.query.all()
        customers = Customer.query.all()
        staff = User.query.filter(User.role.in_(["staff", "manager"])).all()
        
        for day_offset in range(7):
            appointment_date = datetime.now() + timedelta(days=day_offset)
            # Create 3-5 appointments per day
            for _ in range(random.randint(3, 5)):
                hour = random.randint(9, 17)
                minute = random.choice([0, 30])
                appointment_time = appointment_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                service = random.choice(services)
                customer = random.choice(customers)
                staff_member = random.choice(staff)
                
                # Check if appointment already exists
                existing = Appointment.query.filter_by(
                    appointment_date=appointment_time,
                    staff_id=staff_member.id
                ).first()
                
                if not existing:
                    appointment = Appointment(
                        client_id=customer.id,
                        service_id=service.id,
                        staff_id=staff_member.id,
                        appointment_date=appointment_time,
                        end_time=appointment_time + timedelta(minutes=service.duration),
                        status=random.choice(['scheduled', 'confirmed', 'completed']),
                        amount=service.price,
                        discount=random.uniform(0, service.price * 0.1),
                        payment_status=random.choice(['pending', 'paid']),
                        notes=f"Appointment for {service.name}"
                    )
                    db.session.add(appointment)
        
        db.session.commit()
        print("✅ Sample appointments created successfully!")
        
        print("🎉 Demo data creation completed successfully!")
        print("📊 Summary:")
        print(f"   • Services: {Service.query.count()}")
        print(f"   • Customers: {Customer.query.count()}")
        print(f"   • Staff: {User.query.count()}")
        print(f"   • Inventory Items: {InventoryProduct.query.count()}")
        print(f"   • Appointments: {Appointment.query.count()}")
        print("\n🚀 Your spa management system is ready for the client demo!")

if __name__ == "__main__":
    create_demo_data()