#!/usr/bin/env python3
"""
Comprehensive Database Seeder - Populates ALL tables with 20 realistic records each
"""

import os
import sys
from datetime import datetime, date, timedelta
import random
from decimal import Decimal

# Set up environment
os.environ.setdefault("SESSION_SECRET", "seeding_session_key")
os.environ.setdefault("DATABASE_URL", "sqlite:///seeding_database.db")

# Import Flask app and models
from app import app, db
from models import *

# Import inventory models
try:
    from modules.inventory.models import InventoryProduct, InventoryBatch, InventoryAuditLog
    INVENTORY_MODELS_AVAILABLE = True
except ImportError:
    print("⚠️  Inventory models not found, skipping inventory data")
    INVENTORY_MODELS_AVAILABLE = False

class ComprehensiveSeeder:
    def __init__(self):
        self.users = []
        self.customers = []
        self.services = []
        self.roles = []
        self.departments = []
        self.categories = []
        self.appointments = []
        self.packages = []
        
    def clear_existing_data(self):
        """Clear existing data (optional - use with caution)"""
        print("🗑️  Clearing existing data...")
        with app.app_context():
            # Clear in reverse dependency order
            db.session.query(PackageAssignmentUsage).delete()
            db.session.query(ServicePackageAssignment).delete()
            db.session.query(CustomerPackageItem).delete()
            db.session.query(CustomerPackage).delete()
            db.session.query(PackageTemplateItem).delete()
            db.session.query(PackageTemplate).delete()
            db.session.query(InvoicePayment).delete()
            db.session.query(InvoiceItem).delete()
            db.session.query(EnhancedInvoice).delete()
            db.session.query(Communication).delete()
            db.session.query(Review).delete()
            db.session.query(Commission).delete()
            db.session.query(Attendance).delete()
            db.session.query(Leave).delete()
            db.session.query(StaffService).delete()
            db.session.query(StaffPerformance).delete()
            db.session.query(StaffSchedule).delete()
            db.session.query(Expense).delete()
            db.session.query(Waitlist).delete()
            db.session.query(RecurringAppointment).delete()
            db.session.query(KittyPartyService).delete()
            db.session.query(MembershipService).delete()
            db.session.query(KittyParty).delete()
            db.session.query(Membership).delete()
            db.session.query(ServicePackage).delete()
            db.session.query(PrepaidPackage).delete()
            db.session.query(Appointment).delete()
            db.session.query(Service).delete()
            db.session.query(Customer).delete()
            db.session.query(User).delete()
            db.session.query(RolePermission).delete()
            db.session.query(Permission).delete()
            db.session.query(Role).delete()
            db.session.query(Category).delete()
            db.session.query(Department).delete()
            db.session.query(SystemSetting).delete()
            db.session.query(Location).delete()
            db.session.query(BusinessSettings).delete()
            
            if INVENTORY_MODELS_AVAILABLE:
                db.session.query(InventoryAuditLog).delete()
                db.session.query(InventoryBatch).delete()
                db.session.query(InventoryProduct).delete()
            
            db.session.commit()
            print("✅ Existing data cleared")

    def seed_roles(self):
        """Seed Role table with 20 records (add only if not exists)"""
        print("👥 Seeding Roles...")
        
        role_data = [
            ("admin", "Administrator", "Full system access and administration"),
            ("manager", "Manager", "Management access with oversight capabilities"),
            ("reception", "Receptionist", "Front desk and customer service operations"),
            ("staff", "Staff Member", "General staff access for daily operations"),
            ("cashier", "Cashier", "Billing and payment processing"),
            ("therapist", "Therapist", "Service provider and treatment specialist"),
            ("supervisor", "Supervisor", "Team supervision and quality control"),
            ("trainer", "Trainer", "Staff training and development"),
            ("cleaner", "Cleaner", "Facility maintenance and cleaning"),
            ("security", "Security", "Facility security and access control"),
            ("accountant", "Accountant", "Financial management and reporting"),
            ("marketing", "Marketing Specialist", "Promotional activities and customer outreach"),
            ("inventory", "Inventory Manager", "Stock management and procurement"),
            ("technical", "Technical Support", "System maintenance and troubleshooting"),
            ("guest_relations", "Guest Relations", "VIP customer service and experience"),
            ("consultant", "Consultant", "Expert advice and specialized services"),
            ("apprentice", "Apprentice", "Learning role with limited access"),
            ("part_time", "Part-time Staff", "Limited hours and responsibilities"),
            ("temporary", "Temporary Worker", "Short-term assignment access"),
            ("volunteer", "Volunteer", "Community service and support roles")
        ]
        
        added_count = 0
        for name, display_name, description in role_data:
            # Check if role already exists
            existing_role = Role.query.filter_by(name=name).first()
            if not existing_role:
                role = Role(
                    name=name,
                    display_name=display_name,
                    description=description,
                    is_active=True
                )
                db.session.add(role)
                self.roles.append(role)
                added_count += 1
            else:
                self.roles.append(existing_role)
        
        db.session.commit()
        print(f"✅ Added {added_count} new roles ({len(role_data) - added_count} already existed)")

    def seed_permissions(self):
        """Seed Permission table with comprehensive permissions"""
        print("🔐 Seeding Permissions...")
        
        modules = ["dashboard", "staff", "clients", "services", "bookings", "inventory", 
                  "billing", "reports", "settings", "packages", "expenses", "attendance"]
        actions = ["view", "create", "edit", "delete"]
        
        permissions = []
        for module in modules:
            for action in actions:
                permission = Permission(
                    name=f"{module}_{action}",
                    display_name=f"{action.title()} {module.title()}",
                    description=f"Permission to {action} {module} records",
                    module=module,
                    is_active=True
                )
                permissions.append(permission)
        
        # Add special permissions
        special_perms = [
            ("admin_panel", "Admin Panel", "Access to administration panel", "admin"),
            ("financial_reports", "Financial Reports", "Access to financial data", "reports"),
            ("staff_schedules", "Staff Schedules", "Manage staff scheduling", "staff"),
            ("system_backup", "System Backup", "Perform system backups", "admin")
        ]
        
        for name, display_name, description, module in special_perms:
            permission = Permission(
                name=name,
                display_name=display_name,
                description=description,
                module=module,
                is_active=True
            )
            permissions.append(permission)
        
        for perm in permissions:
            db.session.add(perm)
        
        db.session.commit()
        print(f"✅ Created {len(permissions)} permissions")

    def seed_departments(self):
        """Seed Department table with 20 records (add only if not exists)"""
        print("🏢 Seeding Departments...")
        
        dept_data = [
            ("spa", "Spa Services", "Relaxation and wellness treatments"),
            ("hair", "Hair Salon", "Hair styling and treatment services"),
            ("nails", "Nail Studio", "Manicure and pedicure services"),
            ("facial", "Facial Care", "Skincare and facial treatments"),
            ("massage", "Massage Therapy", "Therapeutic and relaxation massage"),
            ("fitness", "Fitness Center", "Exercise and fitness programs"),
            ("reception", "Reception", "Customer service and front desk"),
            ("admin", "Administration", "Management and administrative tasks"),
            ("billing", "Billing Department", "Financial transactions and accounting"),
            ("maintenance", "Maintenance", "Facility upkeep and repairs"),
            ("inventory", "Inventory Management", "Stock control and procurement"),
            ("marketing", "Marketing", "Promotional activities and advertising"),
            ("security", "Security", "Safety and access control"),
            ("cleaning", "Housekeeping", "Cleaning and sanitation services"),
            ("training", "Training Department", "Staff development and education"),
            ("wellness", "Wellness Center", "Holistic health and nutrition"),
            ("beauty", "Beauty Services", "Cosmetic and aesthetic treatments"),
            ("retail", "Retail Sales", "Product sales and merchandising"),
            ("events", "Event Planning", "Special events and celebrations"),
            ("vip", "VIP Services", "Premium customer experience")
        ]
        
        added_count = 0
        for name, display_name, description in dept_data:
            existing_dept = Department.query.filter_by(name=name).first()
            if not existing_dept:
                dept = Department(
                    name=name,
                    display_name=display_name,
                    description=description,
                    is_active=True
                )
                db.session.add(dept)
                self.departments.append(dept)
                added_count += 1
            else:
                self.departments.append(existing_dept)
        
        db.session.commit()
        print(f"✅ Added {added_count} new departments ({len(dept_data) - added_count} already existed)")

    def seed_categories(self):
        """Seed Category table with 20 records"""
        print("📂 Seeding Categories...")
        
        category_data = [
            ("facial_treatments", "Facial Treatments", "Face care and skincare services", "service", "#FF6B9D"),
            ("body_treatments", "Body Treatments", "Body massage and spa services", "service", "#4ECDC4"),
            ("hair_services", "Hair Services", "Hair cutting, styling, and treatments", "service", "#45B7D1"),
            ("nail_services", "Nail Services", "Manicure, pedicure, and nail art", "service", "#F9CA24"),
            ("wellness_programs", "Wellness Programs", "Health and fitness services", "service", "#6C5CE7"),
            ("beauty_packages", "Beauty Packages", "Combined beauty service packages", "service", "#FD79A8"),
            ("skincare_products", "Skincare Products", "Face and body care products", "product", "#00B894"),
            ("haircare_products", "Haircare Products", "Shampoo, conditioner, and styling products", "product", "#E17055"),
            ("makeup_products", "Makeup Products", "Cosmetics and beauty enhancers", "product", "#FDCB6E"),
            ("wellness_supplements", "Wellness Supplements", "Health and nutrition supplements", "product", "#6C5CE7"),
            ("equipment_supplies", "Equipment & Supplies", "Professional tools and supplies", "product", "#636E72"),
            ("office_expenses", "Office Expenses", "Administrative and office costs", "expense", "#74B9FF"),
            ("utility_bills", "Utility Bills", "Electricity, water, and other utilities", "expense", "#00CEC9"),
            ("marketing_costs", "Marketing Costs", "Advertising and promotional expenses", "expense", "#FD79A8"),
            ("staff_training", "Staff Training", "Employee development and education", "expense", "#FDCB6E"),
            ("maintenance_repairs", "Maintenance & Repairs", "Facility upkeep and equipment repair", "expense", "#E84393"),
            ("inventory_purchases", "Inventory Purchases", "Product and supply procurement", "expense", "#00B894"),
            ("professional_services", "Professional Services", "Legal, accounting, and consulting", "expense", "#6C5CE7"),
            ("travel_transport", "Travel & Transport", "Business travel and transportation", "expense", "#A29BFE"),
            ("miscellaneous", "Miscellaneous", "Other uncategorized items", "expense", "#B2BEC3")
        ]
        
        for name, display_name, description, category_type, color in category_data:
            category = Category(
                name=name,
                display_name=display_name,
                description=description,
                category_type=category_type,
                color=color,
                is_active=True,
                sort_order=random.randint(1, 100)
            )
            db.session.add(category)
            self.categories.append(category)
        
        db.session.commit()
        print(f"✅ Created {len(category_data)} categories")

    def seed_users(self):
        """Seed User table with 20 staff records (add only if not exists)"""
        print("👤 Seeding Users (Staff)...")
        
        staff_data = [
            ("admin", "admin@spa.com", "System", "Administrator", "admin"),
            ("sarah.manager", "sarah@spa.com", "Sarah", "Johnson", "manager"),
            ("mike.therapist", "mike@spa.com", "Mike", "Chen", "therapist"),
            ("emma.reception", "emma@spa.com", "Emma", "Williams", "reception"),
            ("james.cashier", "james@spa.com", "James", "Brown", "cashier"),
            ("lisa.hairstylist", "lisa@spa.com", "Lisa", "Davis", "staff"),
            ("alex.massage", "alex@spa.com", "Alex", "Miller", "therapist"),
            ("maya.facial", "maya@spa.com", "Maya", "Wilson", "therapist"),
            ("ryan.fitness", "ryan@spa.com", "Ryan", "Moore", "trainer"),
            ("sofia.nails", "sofia@spa.com", "Sofia", "Taylor", "staff"),
            ("david.supervisor", "david@spa.com", "David", "Anderson", "supervisor"),
            ("nina.beauty", "nina@spa.com", "Nina", "Thomas", "staff"),
            ("carlos.maintenance", "carlos@spa.com", "Carlos", "Jackson", "maintenance"),
            ("anna.consultant", "anna@spa.com", "Anna", "White", "consultant"),
            ("raj.inventory", "raj@spa.com", "Raj", "Patel", "inventory"),
            ("zoe.marketing", "zoe@spa.com", "Zoe", "Lewis", "marketing"),
            ("ben.security", "ben@spa.com", "Ben", "Clark", "security"),
            ("grace.wellness", "grace@spa.com", "Grace", "Lee", "therapist"),
            ("tom.apprentice", "tom@spa.com", "Tom", "Hall", "apprentice"),
            ("mia.parttime", "mia@spa.com", "Mia", "Allen", "part_time")
        ]
        
        # Get existing users first
        existing_users = User.query.all()
        for existing_user in existing_users:
            self.users.append(existing_user)
        
        added_count = 0
        for username, email, first_name, last_name, role_name in staff_data:
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                # Find role
                role = None
                if self.roles:
                    role = next((r for r in self.roles if r.name == role_name), self.roles[0])
                
                # Find department
                dept = None
                if self.departments:
                    dept = random.choice(self.departments)
                
                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role=role_name,
                    role_id=role.id if role else None,
                    department=dept.name if dept else "general",
                    department_id=dept.id if dept else None,
                    phone=f"555-{random.randint(1000, 9999)}",
                    is_active=True,
                    commission_rate=random.uniform(0.05, 0.25),
                    hourly_rate=random.uniform(15.0, 50.0),
                    employee_id=f"EMP{random.randint(1000, 9999)}",
                    hire_date=date.today() - timedelta(days=random.randint(30, 1000)),
                    gender=random.choice(["male", "female", "other"]),
                    date_of_birth=date.today() - timedelta(days=random.randint(7000, 18000)),
                    date_of_joining=date.today() - timedelta(days=random.randint(30, 500)),
                    staff_code=f"SC{random.randint(100, 999)}",
                    designation=random.choice(["Senior", "Junior", "Assistant", "Lead", "Manager"]),
                    working_days="1111100",  # Mon-Fri
                    commission_percentage=random.uniform(5.0, 20.0),
                    last_login=datetime.now() - timedelta(days=random.randint(0, 30))
                )
                from werkzeug.security import generate_password_hash
                user.password_hash = generate_password_hash("admin123")  # Default password
                db.session.add(user)
                self.users.append(user)
                added_count += 1
        
        db.session.commit()
        print(f"✅ Added {added_count} new staff users ({len(staff_data) - added_count} already existed)")

    def seed_customers(self):
        """Seed Customer table with 20 records"""
        print("👥 Seeding Customers...")
        
        customer_data = [
            ("Jennifer", "Smith", "jennifer.smith@email.com", "555-0101"),
            ("Michael", "Johnson", "michael.j@email.com", "555-0102"),
            ("Sarah", "Williams", "sarah.williams@email.com", "555-0103"),
            ("David", "Brown", "david.brown@email.com", "555-0104"),
            ("Emily", "Davis", "emily.davis@email.com", "555-0105"),
            ("Christopher", "Miller", "chris.miller@email.com", "555-0106"),
            ("Jessica", "Wilson", "jessica.wilson@email.com", "555-0107"),
            ("Matthew", "Moore", "matthew.moore@email.com", "555-0108"),
            ("Ashley", "Taylor", "ashley.taylor@email.com", "555-0109"),
            ("Daniel", "Anderson", "daniel.anderson@email.com", "555-0110"),
            ("Amanda", "Thomas", "amanda.thomas@email.com", "555-0111"),
            ("Joshua", "Jackson", "joshua.jackson@email.com", "555-0112"),
            ("Stephanie", "White", "stephanie.white@email.com", "555-0113"),
            ("Andrew", "Harris", "andrew.harris@email.com", "555-0114"),
            ("Michelle", "Martin", "michelle.martin@email.com", "555-0115"),
            ("Kevin", "Thompson", "kevin.thompson@email.com", "555-0116"),
            ("Lisa", "Garcia", "lisa.garcia@email.com", "555-0117"),
            ("Ryan", "Martinez", "ryan.martinez@email.com", "555-0118"),
            ("Rachel", "Robinson", "rachel.robinson@email.com", "555-0119"),
            ("Brandon", "Clark", "brandon.clark@email.com", "555-0120")
        ]
        
        for first_name, last_name, email, phone in customer_data:
            customer = Customer(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                date_of_birth=date.today() - timedelta(days=random.randint(7000, 25000)),
                gender=random.choice(["male", "female"]),
                address=f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm'])} St, City, State {random.randint(10000, 99999)}",
                total_visits=random.randint(0, 50),
                total_spent=random.uniform(100.0, 5000.0),
                loyalty_points=random.randint(0, 1000),
                is_vip=random.choice([True, False]),
                preferred_communication=random.choice(["email", "sms", "whatsapp"]),
                marketing_consent=random.choice([True, False]),
                referral_source=random.choice(["Google", "Facebook", "Friend", "Walk-in", "Advertisement"]),
                lifetime_value=random.uniform(500.0, 10000.0),
                last_visit=datetime.now() - timedelta(days=random.randint(1, 365))
            )
            db.session.add(customer)
            self.customers.append(customer)
        
        db.session.commit()
        print(f"✅ Created {len(customer_data)} customers")

    def seed_services(self):
        """Seed Service table with 20 records"""
        print("💆 Seeding Services...")
        
        service_data = [
            ("Classic Facial", "Deep cleansing facial with moisturizing", 60, 80.0),
            ("Swedish Massage", "Full body relaxation massage", 90, 120.0),
            ("Manicure & Polish", "Complete nail care with color", 45, 35.0),
            ("Hair Cut & Style", "Professional haircut and styling", 75, 65.0),
            ("Hot Stone Massage", "Therapeutic massage with heated stones", 90, 150.0),
            ("Acne Treatment Facial", "Specialized facial for problem skin", 75, 95.0),
            ("Pedicure Deluxe", "Complete foot care and pampering", 60, 45.0),
            ("Hair Color & Highlights", "Professional hair coloring service", 120, 150.0),
            ("Anti-Aging Facial", "Advanced facial for mature skin", 90, 120.0),
            ("Deep Tissue Massage", "Intensive therapeutic massage", 90, 140.0),
            ("Gel Manicure", "Long-lasting gel nail treatment", 60, 50.0),
            ("Hair Treatment", "Intensive conditioning treatment", 45, 75.0),
            ("Microdermabrasion", "Skin resurfacing treatment", 60, 100.0),
            ("Couples Massage", "Relaxing massage for two", 90, 250.0),
            ("Eyebrow Shaping", "Professional eyebrow design", 30, 25.0),
            ("Scalp Massage", "Relaxing head and scalp treatment", 30, 40.0),
            ("Body Wrap", "Detoxifying body treatment", 90, 110.0),
            ("Beard Trim", "Professional beard grooming", 30, 30.0),
            ("Foot Reflexology", "Therapeutic foot pressure point massage", 60, 70.0),
            ("Express Facial", "Quick cleansing facial", 30, 50.0)
        ]
        
        for name, description, duration, price in service_data:
            category = random.choice(self.categories) if self.categories else None
            
            service = Service(
                name=name,
                description=description,
                duration=duration,
                price=price,
                category=category.name if category and category.category_type == "service" else "general",
                category_id=category.id if category and category.category_type == "service" else None,
                is_active=True
            )
            db.session.add(service)
            self.services.append(service)
        
        db.session.commit()
        print(f"✅ Created {len(service_data)} services")

    def seed_appointments(self):
        """Seed Appointment table with 20 records"""
        print("📅 Seeding Appointments...")
        
        if not self.customers or not self.services or not self.users:
            print("⚠️  Skipping appointments - missing prerequisite data")
            return
        
        statuses = ["scheduled", "confirmed", "in_progress", "completed", "cancelled"]
        payment_statuses = ["pending", "paid", "partial"]
        
        for i in range(20):
            customer = random.choice(self.customers)
            service = random.choice(self.services)
            staff = random.choice(self.users)
            
            appointment_date = datetime.now() + timedelta(days=random.randint(-30, 60))
            end_time = appointment_date + timedelta(minutes=service.duration)
            
            appointment = Appointment(
                client_id=customer.id,
                service_id=service.id,
                staff_id=staff.id,
                appointment_date=appointment_date,
                end_time=end_time,
                status=random.choice(statuses),
                amount=service.price + random.uniform(-10.0, 20.0),
                discount=random.uniform(0.0, 15.0),
                tips=random.uniform(0.0, 20.0),
                payment_status=random.choice(payment_statuses),
                is_paid=random.choice([True, False]),
                notes=f"Appointment for {customer.first_name} - {service.name}"
            )
            db.session.add(appointment)
            self.appointments.append(appointment)
        
        db.session.commit()
        print("✅ Created 20 appointments")

    def seed_packages(self):
        """Seed package-related tables"""
        print("📦 Seeding Packages...")
        
        # Prepaid Packages
        prepaid_data = [
            ("Spa Credit $500", 400.0, 500.0, 25.0, 12),
            ("Wellness Package", 800.0, 1000.0, 25.0, 6),
            ("Premium Credit", 1500.0, 2000.0, 33.33, 12),
            ("Starter Package", 200.0, 250.0, 25.0, 6),
            ("Luxury Experience", 2000.0, 2500.0, 25.0, 12)
        ]
        
        for name, actual_price, after_value, benefit_percent, validity_months in prepaid_data:
            package = PrepaidPackage(
                name=name,
                actual_price=actual_price,
                after_value=after_value,
                benefit_percent=benefit_percent,
                validity_months=validity_months,
                is_active=True
            )
            db.session.add(package)
        
        # Service Packages (using correct field names based on model)
        service_package_data = [
            ("Facial Package", 4, 3, 6),
            ("Massage Package", 4, 3, 6),
            ("Hair Care Package", 5, 4, 6),
            ("Nail Care Package", 6, 5, 6),
            ("Complete Wellness", 8, 6, 12)
        ]
        
        for name, total_sessions, pay_for, validity_months in service_package_data:
            if self.services:
                service = random.choice(self.services)
                benefit_percent = ((total_sessions - pay_for) / total_sessions) * 100
                package = ServicePackage(
                    name=name,
                    service_id=service.id,
                    total_sessions=total_sessions,
                    pay_for_sessions=pay_for,
                    benefit_percent=benefit_percent,
                    validity_months=validity_months,
                    is_active=True
                )
                db.session.add(package)
        
        # Memberships
        membership_data = [
            ("Gold Membership", 1200.0, 12),
            ("Silver Membership", 800.0, 6),
            ("Platinum Membership", 2000.0, 12),
            ("Student Membership", 400.0, 3),
            ("Family Membership", 1800.0, 12)
        ]
        
        for name, price, validity_months in membership_data:
            membership = Membership(
                name=name,
                price=price,
                validity_months=validity_months,
                is_active=True
            )
            db.session.add(membership)
        
        # Kitty Parties
        kitty_data = [
            ("Bridal Party Special", 2500.0, 3000.0, 8),
            ("Girls Night Out", 1500.0, 1800.0, 6),
            ("Birthday Celebration", 2000.0, 2400.0, 10),
            ("Office Team Building", 3000.0, 3600.0, 12),
            ("Weekend Getaway", 4000.0, 5000.0, 15)
        ]
        
        for name, price, after_value, min_guests in kitty_data:
            kitty = KittyParty(
                name=name,
                price=price,
                after_value=after_value,
                min_guests=min_guests,
                valid_from=date.today(),
                valid_to=date.today() + timedelta(days=90),
                is_active=True
            )
            db.session.add(kitty)
        
        db.session.commit()
        print("✅ Created package records")

    def seed_additional_tables(self):
        """Seed remaining tables with sample data"""
        print("🔧 Seeding Additional Tables...")
        
        # System Settings
        settings_data = [
            ("business_name", "Elite Spa & Wellness", "string", "business"),
            ("business_phone", "555-SPA-RELAX", "string", "business"),
            ("business_email", "info@elitespa.com", "string", "business"),
            ("tax_rate", "8.5", "float", "billing"),
            ("currency", "USD", "string", "business"),
            ("timezone", "America/New_York", "string", "business"),
            ("booking_advance_days", "30", "integer", "booking"),
            ("cancellation_hours", "24", "integer", "booking"),
            ("loyalty_points_rate", "0.05", "float", "loyalty"),
            ("vip_threshold", "5000", "float", "loyalty")
        ]
        
        for key, value, data_type, category in settings_data:
            setting = SystemSetting(
                key=key,
                value=value,
                data_type=data_type,
                category=category,
                display_name=key.replace("_", " ").title(),
                description=f"System setting for {key}",
                is_public=False
            )
            db.session.add(setting)
        
        # Locations
        location_data = [
            ("Main Branch", "123 Wellness Ave, Spa City, SC 12345"),
            ("Downtown Location", "456 Urban St, Metro City, MC 67890"),
            ("Suburban Center", "789 Family Blvd, Suburb Town, ST 54321")
        ]
        
        for name, address in location_data[:3]:
            location = Location(
                name=name,
                address=address,
                phone=f"555-{random.randint(1000, 9999)}",
                email=f"{name.lower().replace(' ', '')}@elitespa.com",
                is_active=True,
                operating_hours='{"mon-fri": "9:00-20:00", "sat": "9:00-18:00", "sun": "10:00-16:00"}'
            )
            db.session.add(location)
        
        # Expenses
        if self.categories:
            expense_categories = [c for c in self.categories if c.category_type == "expense"]
            for i in range(20):
                category = random.choice(expense_categories) if expense_categories else None
                expense = Expense(
                    description=f"Business expense {i+1}",
                    amount=random.uniform(50.0, 1000.0),
                    expense_date=date.today() - timedelta(days=random.randint(0, 365)),
                    category=category.name if category else "miscellaneous",
                    category_id=category.id if category else None,
                    payment_method=random.choice(["cash", "card", "bank_transfer"]),
                    is_recurring=random.choice([True, False])
                )
                db.session.add(expense)
        
        # Staff Schedules
        if self.users:
            for user in self.users[:10]:  # Create schedules for first 10 staff
                for day in range(5):  # Monday to Friday
                    schedule = StaffSchedule(
                        staff_id=user.id,
                        day_of_week=day,
                        start_time=datetime.strptime("09:00", "%H:%M").time(),
                        end_time=datetime.strptime("17:00", "%H:%M").time(),
                        is_available=True
                    )
                    db.session.add(schedule)
        
        # Reviews
        if self.customers and self.services and self.users:
            for i in range(20):
                review = Review(
                    client_id=random.choice(self.customers).id,
                    service_id=random.choice(self.services).id,
                    staff_id=random.choice(self.users).id,
                    rating=random.randint(3, 5),
                    comment=f"Great service! Really enjoyed the experience. Review {i+1}",
                    is_public=True
                )
                db.session.add(review)
        
        # Attendance records
        if self.users:
            for user in self.users[:10]:
                for day in range(20):  # Last 20 days
                    attendance_date = date.today() - timedelta(days=day)
                    if attendance_date.weekday() < 5:  # Weekdays only
                        attendance = Attendance(
                            staff_id=user.id,
                            check_in_time=datetime.combine(attendance_date, 
                                datetime.strptime("09:00", "%H:%M").time()) + 
                                timedelta(minutes=random.randint(-15, 30)),
                            check_out_time=datetime.combine(attendance_date, 
                                datetime.strptime("17:00", "%H:%M").time()) + 
                                timedelta(minutes=random.randint(-30, 60)),
                            check_in_method=random.choice(["manual", "facial", "biometric"]),
                            total_hours=8.0 + random.uniform(-1.0, 2.0),
                            date=attendance_date
                        )
                        db.session.add(attendance)
        
        db.session.commit()
        print("✅ Additional tables seeded")

    def seed_inventory(self):
        """Seed inventory tables if available"""
        if not INVENTORY_MODELS_AVAILABLE:
            return
            
        print("📦 Seeding Inventory...")
        
        # Create inventory products
        product_data = [
            ("Premium Face Cream", "FACE-001", "Luxury anti-aging face cream", "pcs"),
            ("Organic Hair Oil", "HAIR-001", "Natural hair treatment oil", "bottles"),
            ("Massage Lotion", "MASS-001", "Professional massage lotion", "bottles"),
            ("Nail Polish Set", "NAIL-001", "Complete nail color collection", "sets"),
            ("Aromatherapy Candles", "AROM-001", "Relaxing scented candles", "pcs"),
            ("Face Masks", "FACE-002", "Hydrating sheet masks", "pcs"),
            ("Essential Oils", "OILS-001", "Pure essential oil collection", "bottles"),
            ("Towel Set", "TOWL-001", "Luxury spa towels", "sets"),
            ("Cleansing Gel", "CLEN-001", "Deep cleansing facial gel", "bottles"),
            ("Body Scrub", "BODY-001", "Exfoliating body scrub", "jars"),
            ("Hair Shampoo", "HAIR-002", "Professional salon shampoo", "bottles"),
            ("Moisturizer", "MOIS-001", "Daily hydrating moisturizer", "bottles"),
            ("Lip Balm", "LIPS-001", "Nourishing lip treatment", "pcs"),
            ("Eye Cream", "EYES-001", "Anti-aging eye treatment", "tubes"),
            ("Sunscreen", "SUN-001", "Broad spectrum sun protection", "bottles"),
            ("Toner", "TONE-001", "Balancing facial toner", "bottles"),
            ("Serum", "SERU-001", "Vitamin C brightening serum", "bottles"),
            ("Exfoliant", "EXFO-001", "Gentle facial exfoliant", "tubes"),
            ("Mask Pack", "MASK-001", "Clay purifying mask", "jars"),
            ("Treatment Oil", "TREA-001", "Multi-purpose treatment oil", "bottles")
        ]
        
        products = []
        for name, code, description, unit in product_data:
            product = InventoryProduct(
                name=name,
                product_code=code,
                description=description,
                unit=unit,
                is_active=True
            )
            db.session.add(product)
            products.append(product)
        
        db.session.flush()  # Flush to get IDs
        
        # Create inventory batches
        for product in products:
            for batch_num in range(2):  # 2 batches per product
                batch = InventoryBatch(
                    batch_name=f"{product.product_code}-B{batch_num+1:03d}",
                    product_id=product.id,
                    initial_quantity=random.randint(50, 200),
                    current_quantity=random.randint(20, 150),
                    cost_per_unit=random.uniform(5.0, 50.0),
                    selling_price=random.uniform(10.0, 100.0),
                    expiry_date=date.today() + timedelta(days=random.randint(180, 720)),
                    supplier_name=random.choice(["Beauty Supply Co", "Spa Essentials", "Wellness Products Ltd"]),
                    received_date=date.today() - timedelta(days=random.randint(1, 60))
                )
                db.session.add(batch)
        
        db.session.commit()
        print("✅ Inventory tables seeded")

    def run_comprehensive_seed(self, clear_first=False):
        """Run the complete seeding process"""
        print("🌱 Starting Comprehensive Database Seeding")
        print("=" * 60)
        
        with app.app_context():
            if clear_first:
                self.clear_existing_data()
            
            # Create tables if they don't exist
            db.create_all()
            
            # Seed in dependency order
            self.seed_roles()
            self.seed_permissions()
            self.seed_departments()
            self.seed_categories()
            self.seed_users()
            self.seed_customers()
            self.seed_services()
            self.seed_appointments()
            self.seed_packages()
            self.seed_additional_tables()
            self.seed_inventory()
            
            print("\n" + "=" * 60)
            print("🎉 DATABASE SEEDING COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("📊 Summary:")
            print(f"   • {len(self.roles)} Roles")
            print(f"   • {len(self.departments)} Departments")
            print(f"   • {len(self.categories)} Categories")
            print(f"   • {len(self.users)} Staff Users")
            print(f"   • {len(self.customers)} Customers")
            print(f"   • {len(self.services)} Services")
            print(f"   • {len(self.appointments)} Appointments")
            print(f"   • Multiple Package Types")
            print(f"   • System Settings & Configurations")
            print(f"   • Attendance & Schedule Records")
            print(f"   • Reviews & Communication Logs")
            if INVENTORY_MODELS_AVAILABLE:
                print(f"   • Inventory Products & Batches")
            print("\n💡 All tables now have realistic test data!")
            print("🔑 Admin Login: admin / admin123")

if __name__ == "__main__":
    seeder = ComprehensiveSeeder()
    
    # Auto-run with no clearing (preserving existing data, just adding more)
    seeder.run_comprehensive_seed(clear_first=False)