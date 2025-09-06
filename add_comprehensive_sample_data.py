#!/usr/bin/env python3
"""
Comprehensive script to add sample data to the spa management system:
- 10 Staff members
- 10 Customers  
- 10 Products
"""

from app import app, db
from models import User, Customer, InventoryProduct, Role, InventoryCategory, InventorySupplier
from werkzeug.security import generate_password_hash
from datetime import date, time
import random

def add_sample_data():
    """Add comprehensive sample data to the database"""
    
    with app.app_context():
        try:
            print("Starting to add comprehensive sample data...")
            
            # First, ensure we have the necessary categories and suppliers for products
            # Add product categories if they don't exist
            categories_data = [
                {"category_name": "Skincare Products", "description": "Face and body skincare products"},
                {"category_name": "Hair Care Products", "description": "Hair treatment and styling products"},
                {"category_name": "Massage Oils & Accessories", "description": "Massage oils and related accessories"},
                {"category_name": "Spa Equipment", "description": "Professional spa equipment and tools"}
            ]
            
            for cat_data in categories_data:
                existing_cat = InventoryCategory.query.filter_by(category_name=cat_data["category_name"]).first()
                if not existing_cat:
                    category = InventoryCategory(**cat_data)
                    db.session.add(category)
            
            # Add suppliers if they don't exist
            suppliers_data = [
                {"supplier_name": "Spa Supply Co", "supplier_code": "SUP001", "contact_person": "John Smith", "phone": "555-0101", "email": "john@spasupply.com"},
                {"supplier_name": "Beauty Products Ltd", "supplier_code": "SUP002", "contact_person": "Sarah Johnson", "phone": "555-0102", "email": "sarah@beautyproducts.com"}
            ]
            
            for sup_data in suppliers_data:
                existing_sup = InventorySupplier.query.filter_by(supplier_name=sup_data["supplier_name"]).first()
                if not existing_sup:
                    supplier = InventorySupplier(**sup_data)
                    db.session.add(supplier)
            
            db.session.commit()
            
            # Get staff role ID (assuming it exists from default data)
            staff_role = Role.query.filter_by(name='staff').first()
            staff_role_id = staff_role.id if staff_role else None
            
            # 1. ADD 10 STAFF MEMBERS
            print("\n--- Adding 10 Staff Members ---")
            staff_data = [
                {
                    "username": "sarah.massage", "email": "sarah.williams@spa.com", "first_name": "Sarah", "last_name": "Williams",
                    "phone": "+1555-0201", "role": "therapist", "designation": "Senior Massage Therapist", 
                    "hourly_rate": 45.0, "commission_rate": 15.0, "gender": "female", "date_of_birth": date(1988, 3, 15)
                },
                {
                    "username": "mike.facial", "email": "mike.chen@spa.com", "first_name": "Mike", "last_name": "Chen",
                    "phone": "+1555-0202", "role": "therapist", "designation": "Facial Specialist", 
                    "hourly_rate": 42.0, "commission_rate": 12.0, "gender": "male", "date_of_birth": date(1992, 7, 22)
                },
                {
                    "username": "lisa.manager", "email": "lisa.rodriguez@spa.com", "first_name": "Lisa", "last_name": "Rodriguez",
                    "phone": "+1555-0203", "role": "manager", "designation": "Spa Manager", 
                    "hourly_rate": 55.0, "commission_rate": 5.0, "gender": "female", "date_of_birth": date(1985, 11, 8)
                },
                {
                    "username": "david.deep", "email": "david.thompson@spa.com", "first_name": "David", "last_name": "Thompson",
                    "phone": "+1555-0204", "role": "therapist", "designation": "Deep Tissue Specialist", 
                    "hourly_rate": 48.0, "commission_rate": 18.0, "gender": "male", "date_of_birth": date(1990, 5, 30)
                },
                {
                    "username": "emily.nail", "email": "emily.davis@spa.com", "first_name": "Emily", "last_name": "Davis",
                    "phone": "+1555-0205", "role": "therapist", "designation": "Nail Technician", 
                    "hourly_rate": 35.0, "commission_rate": 20.0, "gender": "female", "date_of_birth": date(1995, 12, 12)
                },
                {
                    "username": "alex.sports", "email": "alex.martinez@spa.com", "first_name": "Alex", "last_name": "Martinez",
                    "phone": "+1555-0206", "role": "therapist", "designation": "Sports Massage Therapist", 
                    "hourly_rate": 50.0, "commission_rate": 16.0, "gender": "male", "date_of_birth": date(1987, 9, 18)
                },
                {
                    "username": "jessica.beauty", "email": "jessica.lee@spa.com", "first_name": "Jessica", "last_name": "Lee",
                    "phone": "+1555-0207", "role": "therapist", "designation": "Beauty Consultant", 
                    "hourly_rate": 40.0, "commission_rate": 14.0, "gender": "female", "date_of_birth": date(1993, 4, 25)
                },
                {
                    "username": "ryan.wellness", "email": "ryan.wilson@spa.com", "first_name": "Ryan", "last_name": "Wilson",
                    "phone": "+1555-0208", "role": "therapist", "designation": "Wellness Coach", 
                    "hourly_rate": 38.0, "commission_rate": 10.0, "gender": "male", "date_of_birth": date(1991, 8, 14)
                },
                {
                    "username": "maria.reception", "email": "maria.garcia@spa.com", "first_name": "Maria", "last_name": "Garcia",
                    "phone": "+1555-0209", "role": "receptionist", "designation": "Front Desk Coordinator", 
                    "hourly_rate": 22.0, "commission_rate": 0.0, "gender": "female", "date_of_birth": date(1994, 6, 7)
                },
                {
                    "username": "james.hotstone", "email": "james.brown@spa.com", "first_name": "James", "last_name": "Brown",
                    "phone": "+1555-0210", "role": "therapist", "designation": "Hot Stone Massage Specialist", 
                    "hourly_rate": 46.0, "commission_rate": 17.0, "gender": "male", "date_of_birth": date(1989, 1, 20)
                }
            ]
            
            added_staff = 0
            for staff_info in staff_data:
                existing_staff = User.query.filter_by(email=staff_info["email"]).first()
                if not existing_staff:
                    # Generate employee ID
                    staff_code = f"SPA{1001 + added_staff}"
                    
                    staff = User(
                        username=staff_info["username"],
                        email=staff_info["email"],
                        password_hash=generate_password_hash("password123"),
                        first_name=staff_info["first_name"],
                        last_name=staff_info["last_name"],
                        phone=staff_info["phone"],
                        role=staff_info["role"],
                        role_id=staff_role_id,
                        designation=staff_info["designation"],
                        hourly_rate=staff_info["hourly_rate"],
                        commission_rate=staff_info["commission_rate"],
                        gender=staff_info["gender"],
                        date_of_birth=staff_info["date_of_birth"],
                        date_of_joining=date.today(),
                        staff_code=staff_code,
                        employee_id=staff_code,
                        hire_date=date.today(),
                        is_active=True,
                        shift_start_time=time(9, 0),
                        shift_end_time=time(17, 0),
                        working_days="1111100"  # Mon-Fri
                    )
                    db.session.add(staff)
                    added_staff += 1
                    print(f"Adding staff: {staff_info['first_name']} {staff_info['last_name']} - {staff_info['designation']}")
                else:
                    print(f"Staff member {staff_info['email']} already exists")
            
            # 2. ADD 10 CUSTOMERS
            print("\n--- Adding 10 Customers ---")
            customers_data = [
                {
                    "first_name": "Emma", "last_name": "Johnson", "phone": "+1555-1001", "email": "emma.johnson@email.com",
                    "date_of_birth": date(1985, 3, 15), "gender": "female", "address": "123 Main Street, New York, NY 10001",
                    "preferences": "Prefers relaxing massages, loves aromatherapy", "allergies": "None known"
                },
                {
                    "first_name": "Michael", "last_name": "Davis", "phone": "+1555-1002", "email": "michael.davis@email.com",
                    "date_of_birth": date(1990, 7, 22), "gender": "male", "address": "456 Oak Avenue, Los Angeles, CA 90210",
                    "preferences": "Deep tissue massage, sports therapy", "allergies": "Sensitive to strong fragrances"
                },
                {
                    "first_name": "Sarah", "last_name": "Wilson", "phone": "+1555-1003", "email": "sarah.wilson@email.com",
                    "date_of_birth": date(1988, 11, 8), "gender": "female", "address": "789 Pine Road, Chicago, IL 60601",
                    "preferences": "Facial treatments, anti-aging services", "allergies": "Allergic to nuts"
                },
                {
                    "first_name": "David", "last_name": "Brown", "phone": "+1555-1004", "email": "david.brown@email.com",
                    "date_of_birth": date(1982, 5, 30), "gender": "male", "address": "321 Elm Street, Houston, TX 77001",
                    "preferences": "Hot stone massage, reflexology", "allergies": "None"
                },
                {
                    "first_name": "Jessica", "last_name": "Miller", "phone": "+1555-1005", "email": "jessica.miller@email.com",
                    "date_of_birth": date(1992, 12, 12), "gender": "female", "address": "654 Maple Drive, Miami, FL 33101",
                    "preferences": "Prenatal massage, gentle treatments", "allergies": "Latex sensitivity"
                },
                {
                    "first_name": "Robert", "last_name": "Taylor", "phone": "+1555-1006", "email": "robert.taylor@email.com",
                    "date_of_birth": date(1978, 8, 5), "gender": "male", "address": "987 Cedar Lane, Seattle, WA 98101",
                    "preferences": "Swedish massage, stress relief treatments", "allergies": "None known"
                },
                {
                    "first_name": "Amanda", "last_name": "Anderson", "phone": "+1555-1007", "email": "amanda.anderson@email.com",
                    "date_of_birth": date(1986, 2, 18), "gender": "female", "address": "147 Birch Street, Denver, CO 80201",
                    "preferences": "Skin care treatments, body wraps", "allergies": "Sensitive to dairy products"
                },
                {
                    "first_name": "Christopher", "last_name": "White", "phone": "+1555-1008", "email": "chris.white@email.com",
                    "date_of_birth": date(1995, 10, 3), "gender": "male", "address": "258 Spruce Avenue, Portland, OR 97201",
                    "preferences": "Therapeutic massage, injury recovery", "allergies": "None"
                },
                {
                    "first_name": "Megan", "last_name": "Harris", "phone": "+1555-1009", "email": "megan.harris@email.com",
                    "date_of_birth": date(1984, 4, 14), "gender": "female", "address": "369 Willow Road, Austin, TX 78701",
                    "preferences": "Couples massage, romantic packages", "allergies": "Allergic to shellfish"
                },
                {
                    "first_name": "Kevin", "last_name": "Clark", "phone": "+1555-1010", "email": "kevin.clark@email.com",
                    "date_of_birth": date(1991, 9, 27), "gender": "male", "address": "741 Aspen Drive, Phoenix, AZ 85001",
                    "preferences": "Sports massage, muscle recovery", "allergies": "None known"
                }
            ]
            
            added_customers = 0
            for customer_info in customers_data:
                existing_customer = Customer.query.filter_by(phone=customer_info["phone"]).first()
                if not existing_customer:
                    customer = Customer(**customer_info)
                    db.session.add(customer)
                    added_customers += 1
                    print(f"Adding customer: {customer_info['first_name']} {customer_info['last_name']}")
                else:
                    print(f"Customer with phone {customer_info['phone']} already exists")
            
            # Get category and supplier IDs for products
            skincare_cat = InventoryCategory.query.filter_by(category_name="Skincare Products").first()
            haircare_cat = InventoryCategory.query.filter_by(category_name="Hair Care Products").first()
            massage_cat = InventoryCategory.query.filter_by(category_name="Massage Oils & Accessories").first()
            equipment_cat = InventoryCategory.query.filter_by(category_name="Spa Equipment").first()
            
            supplier1 = InventorySupplier.query.filter_by(supplier_name="Spa Supply Co").first()
            supplier2 = InventorySupplier.query.filter_by(supplier_name="Beauty Products Ltd").first()
            
            # 3. ADD 10 PRODUCTS
            print("\n--- Adding 10 Products ---")
            products_data = [
                {
                    "product_code": "SKN001", "name": "Hydrating Facial Serum", "description": "Premium anti-aging serum with hyaluronic acid",
                    "category_id": skincare_cat.category_id if skincare_cat else None, "supplier_id": supplier1.supplier_id if supplier1 else None,
                    "unit": "bottle", "unit_cost": 25.00, "selling_price": 75.00, "current_stock": 50, "reorder_level": 10
                },
                {
                    "product_code": "MSS001", "name": "Relaxing Lavender Massage Oil", "description": "Organic lavender oil for therapeutic massage",
                    "category_id": massage_cat.category_id if massage_cat else None, "supplier_id": supplier1.supplier_id if supplier1 else None,
                    "unit": "bottle", "unit_cost": 15.00, "selling_price": 45.00, "current_stock": 75, "reorder_level": 15
                },
                {
                    "product_code": "SKN002", "name": "Exfoliating Body Scrub", "description": "Dead sea salt scrub with essential oils",
                    "category_id": skincare_cat.category_id if skincare_cat else None, "supplier_id": supplier2.supplier_id if supplier2 else None,
                    "unit": "jar", "unit_cost": 18.00, "selling_price": 55.00, "current_stock": 30, "reorder_level": 8
                },
                {
                    "product_code": "HAIR001", "name": "Nourishing Hair Treatment Mask", "description": "Deep conditioning mask for damaged hair",
                    "category_id": haircare_cat.category_id if haircare_cat else None, "supplier_id": supplier2.supplier_id if supplier2 else None,
                    "unit": "tube", "unit_cost": 12.00, "selling_price": 38.00, "current_stock": 40, "reorder_level": 12
                },
                {
                    "product_code": "MSS002", "name": "Hot Stone Massage Set", "description": "Basalt stones for hot stone therapy",
                    "category_id": equipment_cat.category_id if equipment_cat else None, "supplier_id": supplier1.supplier_id if supplier1 else None,
                    "unit": "set", "unit_cost": 85.00, "selling_price": 180.00, "current_stock": 5, "reorder_level": 2
                },
                {
                    "product_code": "SKN003", "name": "Anti-Aging Eye Cream", "description": "Peptide-rich cream for under-eye care",
                    "category_id": skincare_cat.category_id if skincare_cat else None, "supplier_id": supplier2.supplier_id if supplier2 else None,
                    "unit": "tube", "unit_cost": 22.00, "selling_price": 68.00, "current_stock": 25, "reorder_level": 6
                },
                {
                    "product_code": "MSS003", "name": "Aromatherapy Candle Set", "description": "Soy candles with therapeutic essential oils",
                    "category_id": massage_cat.category_id if massage_cat else None, "supplier_id": supplier1.supplier_id if supplier1 else None,
                    "unit": "set", "unit_cost": 8.00, "selling_price": 28.00, "current_stock": 60, "reorder_level": 20
                },
                {
                    "product_code": "HAIR002", "name": "Scalp Massage Oil", "description": "Stimulating oil blend for scalp health",
                    "category_id": haircare_cat.category_id if haircare_cat else None, "supplier_id": supplier1.supplier_id if supplier1 else None,
                    "unit": "bottle", "unit_cost": 10.00, "selling_price": 32.00, "current_stock": 45, "reorder_level": 10
                },
                {
                    "product_code": "SKN004", "name": "Moisturizing Body Lotion", "description": "Rich hydrating lotion with shea butter",
                    "category_id": skincare_cat.category_id if skincare_cat else None, "supplier_id": supplier2.supplier_id if supplier2 else None,
                    "unit": "pump", "unit_cost": 14.00, "selling_price": 42.00, "current_stock": 35, "reorder_level": 8
                },
                {
                    "product_code": "EQP001", "name": "Professional Towel Warmer", "description": "Electric towel warmer for spa treatments",
                    "category_id": equipment_cat.category_id if equipment_cat else None, "supplier_id": supplier1.supplier_id if supplier1 else None,
                    "unit": "unit", "unit_cost": 120.00, "selling_price": 280.00, "current_stock": 3, "reorder_level": 1
                }
            ]
            
            added_products = 0
            for product_info in products_data:
                existing_product = InventoryProduct.query.filter_by(product_code=product_info["product_code"]).first()
                if not existing_product:
                    product = InventoryProduct(**product_info)
                    db.session.add(product)
                    added_products += 1
                    print(f"Adding product: {product_info['name']} - ${product_info['selling_price']}")
                else:
                    print(f"Product with code {product_info['product_code']} already exists")
            
            # Commit all changes
            db.session.commit()
            
            # Summary
            print(f"\n{'='*60}")
            print("✅ SAMPLE DATA ADDITION COMPLETE!")
            print(f"{'='*60}")
            print(f"📋 Added {added_staff} new staff members")
            print(f"👥 Added {added_customers} new customers")
            print(f"🛒 Added {added_products} new products")
            print(f"{'='*60}")
            
            # Display current totals
            total_staff = User.query.filter_by(is_active=True).count()
            total_customers = Customer.query.filter_by(is_active=True).count()
            total_products = InventoryProduct.query.filter_by(is_active=True).count()
            
            print(f"\n📊 CURRENT DATABASE TOTALS:")
            print(f"👨‍💼 Total Active Staff: {total_staff}")
            print(f"👥 Total Active Customers: {total_customers}")
            print(f"🛒 Total Active Products: {total_products}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding sample data: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    add_sample_data()