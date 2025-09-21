
#!/usr/bin/env python3
"""
Comprehensive Demo Data Generator for Spa Management System
Creates realistic sample data for all modules when cloning to client machines
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, date, timedelta, time
from app import app, db
from models import *
from werkzeug.security import generate_password_hash
import random

class DemoDataGenerator:
    """Generate comprehensive demo data for spa management system"""
    
    def __init__(self):
        self.created_data = {
            'roles': [],
            'departments': [],
            'categories': [], 
            'staff': [],
            'customers': [],
            'services': [],
            'packages': [],
            'appointments': [],
            'inventory': [],
            'expenses': [],
            'invoices': []
        }
    
    def generate_all_demo_data(self):
        """Generate all demo data in proper order"""
        print("🎬 Starting Comprehensive Demo Data Generation...")
        
        with app.app_context():
            try:
                # Clear existing data (optional - comment out if you want to keep existing)
                self.clear_existing_data()
                
                # Generate data in dependency order
                self.create_system_data()
                self.create_staff_data()
                self.create_customer_data()
                self.create_service_data()
                self.create_package_data()
                self.create_appointment_data()
                self.create_inventory_data()
                self.create_expense_data()
                self.create_invoice_data()
                
                # Commit all changes
                db.session.commit()
                
                self.print_summary()
                print("\n🎉 Demo Data Generation Complete!")
                print("Your spa management system is now ready with comprehensive sample data.")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error generating demo data: {e}")
                raise
    
    def clear_existing_data(self):
        """Clear existing data for fresh demo"""
        print("🧹 Clearing existing data...")
        
        # Clear in reverse dependency order
        EnhancedInvoice.query.delete()
        Invoice.query.delete()
        Appointment.query.delete()
        CustomerPackage.query.delete()
        Package.query.delete()
        Service.query.delete()
        Customer.query.delete()
        User.query.filter(User.username != 'admin').delete()
        Expense.query.delete()
        
        # Clear inventory if exists
        try:
            from modules.inventory.models import InventoryConsumption, InventoryBatch, InventoryProduct, InventoryCategory, InventoryLocation
            InventoryConsumption.query.delete()
            InventoryBatch.query.delete() 
            InventoryProduct.query.delete()
            InventoryLocation.query.delete()
            InventoryCategory.query.delete()
        except ImportError:
            pass
        
        db.session.commit()
        print("✅ Existing data cleared")
    
    def create_system_data(self):
        """Create roles, departments, categories"""
        print("⚙️ Creating system configuration data...")
        
        # Create Roles
        roles_data = [
            {'name': 'admin', 'display_name': 'Administrator', 'description': 'Full system access'},
            {'name': 'manager', 'display_name': 'Spa Manager', 'description': 'Management level access'},
            {'name': 'staff', 'display_name': 'Spa Staff', 'description': 'Service staff access'},
            {'name': 'cashier', 'display_name': 'Cashier', 'description': 'Billing and payment access'},
            {'name': 'receptionist', 'display_name': 'Receptionist', 'description': 'Front desk operations'}
        ]
        
        for role_data in roles_data:
            role = Role.query.filter_by(name=role_data['name']).first()
            if not role:
                role = Role(**role_data)
                db.session.add(role)
                self.created_data['roles'].append(role)
        
        # Create Departments
        departments_data = [
            {'name': 'massage', 'display_name': 'Massage Therapy', 'description': 'Massage and body treatments'},
            {'name': 'skincare', 'display_name': 'Skincare & Facials', 'description': 'Facial and skincare services'},
            {'name': 'hair', 'display_name': 'Hair Styling', 'description': 'Hair cutting, coloring, and styling'},
            {'name': 'nails', 'display_name': 'Nail Care', 'description': 'Manicure, pedicure, and nail art'},
            {'name': 'wellness', 'display_name': 'Wellness & Fitness', 'description': 'Wellness and fitness services'},
            {'name': 'reception', 'display_name': 'Reception', 'description': 'Front desk and customer service'}
        ]
        
        for dept_data in departments_data:
            dept = Department.query.filter_by(name=dept_data['name']).first()
            if not dept:
                dept = Department(**dept_data)
                db.session.add(dept)
                self.created_data['departments'].append(dept)
        
        # Create Service Categories
        categories_data = [
            {'name': 'massage', 'display_name': 'Massage Therapy', 'description': 'Relaxing and therapeutic massage services', 'category_type': 'service', 'color': '#FF6B6B', 'icon': 'fas fa-hands'},
            {'name': 'facial', 'display_name': 'Facial Treatments', 'description': 'Skincare and facial beauty treatments', 'category_type': 'service', 'color': '#4ECDC4', 'icon': 'fas fa-leaf'},
            {'name': 'hair', 'display_name': 'Hair Services', 'description': 'Hair cutting, styling and treatments', 'category_type': 'service', 'color': '#45B7D1', 'icon': 'fas fa-cut'},
            {'name': 'nails', 'display_name': 'Nail Care', 'description': 'Manicure, pedicure and nail art services', 'category_type': 'service', 'color': '#F39C12', 'icon': 'fas fa-hand-sparkles'},
            {'name': 'wellness', 'display_name': 'Wellness', 'description': 'Fitness and wellness services', 'category_type': 'service', 'color': '#9B59B6', 'icon': 'fas fa-spa'},
            {'name': 'office', 'display_name': 'Office Expenses', 'description': 'Administrative and office expenses', 'category_type': 'expense', 'color': '#34495E', 'icon': 'fas fa-building'},
            {'name': 'supplies', 'display_name': 'Supplies', 'description': 'Product and supply expenses', 'category_type': 'expense', 'color': '#E74C3C', 'icon': 'fas fa-box'}
        ]
        
        for cat_data in categories_data:
            category = Category.query.filter_by(name=cat_data['name'], category_type=cat_data['category_type']).first()
            if not category:
                category = Category(**cat_data)
                db.session.add(category)
                self.created_data['categories'].append(category)
        
        db.session.flush()  # Get IDs for relationships
        print(f"✅ Created {len(self.created_data['roles'])} roles, {len(self.created_data['departments'])} departments, {len(self.created_data['categories'])} categories")
    
    def create_staff_data(self):
        """Create comprehensive staff data"""
        print("👥 Creating staff members...")
        
        # Get departments for assignment
        massage_dept = Department.query.filter_by(name='massage').first()
        skincare_dept = Department.query.filter_by(name='skincare').first()
        hair_dept = Department.query.filter_by(name='hair').first()
        nails_dept = Department.query.filter_by(name='nails').first()
        reception_dept = Department.query.filter_by(name='reception').first()
        
        # Get roles
        manager_role = Role.query.filter_by(name='manager').first()
        staff_role = Role.query.filter_by(name='staff').first()
        cashier_role = Role.query.filter_by(name='cashier').first()
        
        staff_data = [
            # Manager
            {
                'username': 'spa_manager',
                'email': 'manager@spa.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'manager',
                'role_id': manager_role.id if manager_role else None,
                'department_id': skincare_dept.id if skincare_dept else None,
                'phone': '+1-555-0001',
                'staff_code': 'MGR001',
                'designation': 'Spa Manager',
                'gender': 'female',
                'commission_percentage': 20.0,
                'hourly_rate': 40.0
            },
            
            # Massage Therapists
            {
                'username': 'mike_therapist',
                'email': 'mike@spa.com',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'role': 'staff',
                'role_id': staff_role.id if staff_role else None,
                'department_id': massage_dept.id if massage_dept else None,
                'phone': '+1-555-0002',
                'staff_code': 'MST001',
                'designation': 'Senior Massage Therapist',
                'gender': 'male',
                'commission_percentage': 15.0,
                'hourly_rate': 35.0
            },
            {
                'username': 'anna_massage',
                'email': 'anna@spa.com',
                'first_name': 'Anna',
                'last_name': 'Rodriguez',
                'role': 'staff',
                'role_id': staff_role.id if staff_role else None,
                'department_id': massage_dept.id if massage_dept else None,
                'phone': '+1-555-0003',
                'staff_code': 'MST002',
                'designation': 'Massage Therapist',
                'gender': 'female',
                'commission_percentage': 12.0,
                'hourly_rate': 30.0
            },
            
            # Skincare Specialists
            {
                'username': 'emily_facial',
                'email': 'emily@spa.com',
                'first_name': 'Emily',
                'last_name': 'Davis',
                'role': 'staff',
                'role_id': staff_role.id if staff_role else None,
                'department_id': skincare_dept.id if skincare_dept else None,
                'phone': '+1-555-0004',
                'staff_code': 'SKC001',
                'designation': 'Senior Esthetician',
                'gender': 'female',
                'commission_percentage': 18.0,
                'hourly_rate': 32.0
            },
            
            # Hair Stylists
            {
                'username': 'david_hair',
                'email': 'david@spa.com',
                'first_name': 'David',
                'last_name': 'Brown',
                'role': 'staff',
                'role_id': staff_role.id if staff_role else None,
                'department_id': hair_dept.id if hair_dept else None,
                'phone': '+1-555-0005',
                'staff_code': 'HST001',
                'designation': 'Hair Stylist',
                'gender': 'male',
                'commission_percentage': 14.0,
                'hourly_rate': 28.0
            },
            
            # Nail Technician
            {
                'username': 'lisa_nails',
                'email': 'lisa@spa.com',
                'first_name': 'Lisa',
                'last_name': 'Garcia',
                'role': 'staff',
                'role_id': staff_role.id if staff_role else None,
                'department_id': nails_dept.id if nails_dept else None,
                'phone': '+1-555-0006',
                'staff_code': 'NTC001',
                'designation': 'Nail Technician',
                'gender': 'female',
                'commission_percentage': 10.0,
                'hourly_rate': 25.0
            },
            
            # Cashier
            {
                'username': 'james_cashier',
                'email': 'cashier@spa.com',
                'first_name': 'James',
                'last_name': 'Miller',
                'role': 'cashier',
                'role_id': cashier_role.id if cashier_role else None,
                'department_id': reception_dept.id if reception_dept else None,
                'phone': '+1-555-0007',
                'staff_code': 'CSH001',
                'designation': 'Cashier',
                'gender': 'male',
                'commission_percentage': 5.0,
                'hourly_rate': 20.0
            }
        ]
        
        for staff_info in staff_data:
            # Check if staff exists
            existing_staff = User.query.filter_by(username=staff_info['username']).first()
            if existing_staff:
                continue
            
            # Create staff member with enhanced details
            staff_member = User(
                username=staff_info['username'],
                email=staff_info['email'],
                password_hash=generate_password_hash('password123'),
                first_name=staff_info['first_name'],
                last_name=staff_info['last_name'],
                role=staff_info['role'],
                role_id=staff_info['role_id'],
                department_id=staff_info['department_id'],
                phone=staff_info['phone'],
                staff_code=staff_info['staff_code'],
                designation=staff_info['designation'],
                gender=staff_info['gender'],
                date_of_joining=date.today() - timedelta(days=random.randint(30, 365)),
                working_days='1111100',  # Monday to Friday
                shift_start_time=time(9, 0),
                shift_end_time=time(18, 0),
                commission_percentage=staff_info['commission_percentage'],
                hourly_rate=staff_info['hourly_rate'],
                verification_status=True,
                enable_face_checkin=True,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(staff_member)
            self.created_data['staff'].append(staff_member)
        
        db.session.flush()
        print(f"✅ Created {len(self.created_data['staff'])} staff members")
    
    def create_customer_data(self):
        """Create diverse customer data"""
        print("👤 Creating customers...")
        
        customers_data = [
            {
                'first_name': 'Emma',
                'last_name': 'Thompson',
                'phone': '+1-555-1001',
                'email': 'emma.thompson@email.com',
                'date_of_birth': date(1985, 3, 15),
                'gender': 'female',
                'address': '123 Oak Street, Downtown, NY 10001',
                'preferences': 'Prefers Swedish massage, loves aromatherapy',
                'allergies': 'None known',
                'notes': 'VIP customer, very punctual, prefers afternoon appointments',
                'is_vip': True,
                'loyalty_points': 450
            },
            {
                'first_name': 'Michael',
                'last_name': 'Johnson',
                'phone': '+1-555-1002', 
                'email': 'michael.j@email.com',
                'date_of_birth': date(1990, 7, 22),
                'gender': 'male',
                'address': '456 Pine Avenue, Midtown, NY 10002',
                'preferences': 'Deep tissue massage, sports therapy',
                'allergies': 'Sensitive to strong fragrances',
                'notes': 'Athlete, needs intensive treatments, regular monthly visits',
                'is_vip': False,
                'loyalty_points': 280
            },
            {
                'first_name': 'Sarah',
                'last_name': 'Williams',
                'phone': '+1-555-1003',
                'email': 'sarah.w@email.com', 
                'date_of_birth': date(1988, 11, 8),
                'gender': 'female',
                'address': '789 Maple Road, Uptown, NY 10003',
                'preferences': 'Anti-aging facials, hydrating treatments',
                'allergies': 'Allergic to nuts and shellfish',
                'notes': 'Business executive, prefers early morning or evening slots',
                'is_vip': True,
                'loyalty_points': 720
            },
            {
                'first_name': 'David',
                'last_name': 'Anderson',
                'phone': '+1-555-1004',
                'email': 'david.anderson@email.com',
                'date_of_birth': date(1982, 5, 30),
                'gender': 'male',
                'address': '321 Elm Street, Brooklyn, NY 11201',
                'preferences': 'Hot stone massage, reflexology',
                'allergies': 'None',
                'notes': 'Businessman, often books last minute, pays promptly',
                'is_vip': False,
                'loyalty_points': 180
            },
            {
                'first_name': 'Jessica',
                'last_name': 'Martinez',
                'phone': '+1-555-1005',
                'email': 'jessica.m@email.com',
                'date_of_birth': date(1992, 12, 12),
                'gender': 'female',
                'address': '654 Cedar Drive, Queens, NY 11375',
                'preferences': 'Gentle treatments, organic products only',
                'allergies': 'Latex sensitivity, fragrance allergies',
                'notes': 'Expecting mother, requires special care and positioning',
                'is_vip': False,
                'loyalty_points': 95
            },
            {
                'first_name': 'Robert',
                'last_name': 'Taylor',
                'phone': '+1-555-1006',
                'email': 'rob.taylor@email.com',
                'date_of_birth': date(1975, 8, 18),
                'gender': 'male',
                'address': '987 Birch Lane, Staten Island, NY 10301',
                'preferences': 'Classic massage, scalp treatments',
                'allergies': 'None',
                'notes': 'Senior customer, loyal for 5+ years, refers many clients',
                'is_vip': True,
                'loyalty_points': 1250
            },
            {
                'first_name': 'Amanda',
                'last_name': 'Wilson',
                'phone': '+1-555-1007',
                'email': 'amanda.wilson@email.com',
                'date_of_birth': date(1994, 4, 25),
                'gender': 'female',
                'address': '147 Spruce Street, Bronx, NY 10451',
                'preferences': 'Nail art, gel manicures, pedicures',
                'allergies': 'None',
                'notes': 'Young professional, social media influencer, books regularly',
                'is_vip': False,
                'loyalty_points': 320
            },
            {
                'first_name': 'Christopher',
                'last_name': 'Lee',
                'phone': '+1-555-1008',
                'email': 'chris.lee@email.com',
                'date_of_birth': date(1987, 9, 14),
                'gender': 'male',
                'address': '258 Willow Avenue, Manhattan, NY 10012',
                'preferences': 'Hair styling, beard grooming',
                'allergies': 'Sensitive to hair dyes',
                'notes': 'Fashion industry professional, image-conscious, premium services',
                'is_vip': True,
                'loyalty_points': 890
            }
        ]
        
        for customer_data in customers_data:
            # Check if customer exists
            existing_customer = Customer.query.filter_by(phone=customer_data['phone']).first()
            if existing_customer:
                continue
            
            # Enhanced customer creation
            customer_data.update({
                'total_visits': random.randint(3, 25),
                'total_spent': random.uniform(200.0, 2500.0),
                'is_active': True,
                'preferred_communication': random.choice(['email', 'sms', 'whatsapp']),
                'marketing_consent': random.choice([True, False]),
                'referral_source': random.choice(['Google', 'Facebook', 'Friend Referral', 'Walk-in', 'Instagram']),
                'created_at': datetime.utcnow() - timedelta(days=random.randint(30, 800))
            })
            
            customer = Customer(**customer_data)
            db.session.add(customer)
            self.created_data['customers'].append(customer)
        
        db.session.flush()
        print(f"✅ Created {len(self.created_data['customers'])} customers")
    
    def create_service_data(self):
        """Create comprehensive service catalog"""
        print("💆 Creating services...")
        
        # Get categories
        massage_cat = Category.query.filter_by(name='massage', category_type='service').first()
        facial_cat = Category.query.filter_by(name='facial', category_type='service').first()
        hair_cat = Category.query.filter_by(name='hair', category_type='service').first()
        nails_cat = Category.query.filter_by(name='nails', category_type='service').first()
        wellness_cat = Category.query.filter_by(name='wellness', category_type='service').first()
        
        services_data = [
            # Massage Services
            {
                'name': 'Swedish Massage (60 min)',
                'description': 'Classic relaxing full-body Swedish massage with long, flowing strokes to reduce stress and promote circulation',
                'duration': 60,
                'price': 75.00,
                'category': 'massage',
                'category_id': massage_cat.id if massage_cat else None
            },
            {
                'name': 'Deep Tissue Massage (90 min)',
                'description': 'Therapeutic massage targeting deep muscle layers and chronic tension areas using firm pressure',
                'duration': 90,
                'price': 95.00,
                'category': 'massage',
                'category_id': massage_cat.id if massage_cat else None
            },
            {
                'name': 'Hot Stone Massage (75 min)',
                'description': 'Luxurious massage using heated volcanic stones for ultimate relaxation and muscle relief',
                'duration': 75,
                'price': 110.00,
                'category': 'massage',
                'category_id': massage_cat.id if massage_cat else None
            },
            {
                'name': 'Aromatherapy Massage (60 min)',
                'description': 'Relaxing massage with essential oils chosen to suit your mood and therapeutic needs',
                'duration': 60,
                'price': 85.00,
                'category': 'massage',
                'category_id': massage_cat.id if massage_cat else None
            },
            {
                'name': 'Couples Massage (60 min)',
                'description': 'Romantic side-by-side massage experience for two people in our couples suite',
                'duration': 60,
                'price': 150.00,
                'category': 'massage',
                'category_id': massage_cat.id if massage_cat else None
            },
            
            # Facial Services
            {
                'name': 'European Facial (75 min)',
                'description': 'Deep cleansing facial with extraction, exfoliation, mask, and moisturizing treatment',
                'duration': 75,
                'price': 80.00,
                'category': 'facial',
                'category_id': facial_cat.id if facial_cat else None
            },
            {
                'name': 'Anti-Aging Facial (90 min)',
                'description': 'Advanced facial treatment targeting fine lines, wrinkles, and age spots with peptides',
                'duration': 90,
                'price': 120.00,
                'category': 'facial',
                'category_id': facial_cat.id if facial_cat else None
            },
            {
                'name': 'Hydrating Facial (60 min)',
                'description': 'Intensive moisturizing treatment for dry and dehydrated skin using hyaluronic acid',
                'duration': 60,
                'price': 70.00,
                'category': 'facial',
                'category_id': facial_cat.id if facial_cat else None
            },
            {
                'name': 'Acne Treatment Facial (75 min)',
                'description': 'Specialized facial for acne-prone skin with deep pore cleansing and antibacterial treatment',
                'duration': 75,
                'price': 85.00,
                'category': 'facial',
                'category_id': facial_cat.id if facial_cat else None
            },
            {
                'name': 'Express Facial (30 min)',
                'description': 'Quick facial treatment perfect for busy schedules - cleanse, tone, and moisturize',
                'duration': 30,
                'price': 45.00,
                'category': 'facial',
                'category_id': facial_cat.id if facial_cat else None
            },
            
            # Hair Services
            {
                'name': 'Haircut & Style (45 min)',
                'description': 'Professional haircut with consultation, wash, cut, and styling finish',
                'duration': 45,
                'price': 55.00,
                'category': 'hair',
                'category_id': hair_cat.id if hair_cat else None
            },
            {
                'name': 'Hair Color - Full (120 min)',
                'description': 'Complete hair coloring service with premium products and professional application',
                'duration': 120,
                'price': 95.00,
                'category': 'hair',
                'category_id': hair_cat.id if hair_cat else None
            },
            {
                'name': 'Hair Highlights (90 min)',
                'description': 'Partial highlighting to add dimension and brightness to your hair',
                'duration': 90,
                'price': 75.00,
                'category': 'hair',
                'category_id': hair_cat.id if hair_cat else None
            },
            {
                'name': 'Hair Treatment & Mask (60 min)',
                'description': 'Deep conditioning treatment for damaged or chemically processed hair',
                'duration': 60,
                'price': 65.00,
                'category': 'hair',
                'category_id': hair_cat.id if hair_cat else None
            },
            
            # Nail Services
            {
                'name': 'Classic Manicure (45 min)',
                'description': 'Traditional manicure with nail shaping, cuticle care, and polish application',
                'duration': 45,
                'price': 35.00,
                'category': 'nails',
                'category_id': nails_cat.id if nails_cat else None
            },
            {
                'name': 'Gel Manicure (60 min)',
                'description': 'Long-lasting gel polish manicure with UV curing for chip-free nails',
                'duration': 60,
                'price': 45.00,
                'category': 'nails',
                'category_id': nails_cat.id if nails_cat else None
            },
            {
                'name': 'Classic Pedicure (60 min)',
                'description': 'Relaxing foot care with soak, scrub, callus removal, massage, and polish',
                'duration': 60,
                'price': 40.00,
                'category': 'nails',
                'category_id': nails_cat.id if nails_cat else None
            },
            {
                'name': 'Spa Pedicure (75 min)',
                'description': 'Luxurious pedicure with extended massage, premium products, and paraffin treatment',
                'duration': 75,
                'price': 60.00,
                'category': 'nails',
                'category_id': nails_cat.id if nails_cat else None
            },
            {
                'name': 'Nail Art & Design (30 min)',
                'description': 'Custom nail art and decorative designs to complement your manicure',
                'duration': 30,
                'price': 25.00,
                'category': 'nails',
                'category_id': nails_cat.id if nails_cat else None
            }
        ]
        
        for service_data in services_data:
            # Check if service exists
            existing_service = Service.query.filter_by(name=service_data['name']).first()
            if existing_service:
                continue
            
            service = Service(
                name=service_data['name'],
                description=service_data['description'],
                duration=service_data['duration'],
                price=service_data['price'],
                category=service_data['category'],
                category_id=service_data['category_id'],
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(service)
            self.created_data['services'].append(service)
        
        db.session.flush()
        print(f"✅ Created {len(self.created_data['services'])} services")
    
    def create_package_data(self):
        """Create attractive package deals"""
        print("📦 Creating packages...")
        
        services = self.created_data['services']
        if not services:
            services = Service.query.all()
        
        packages_data = [
            {
                'name': 'Bridal Bliss Package',
                'description': 'Complete bridal preparation with facial, hair, and nail services for your special day',
                'package_type': 'regular',
                'validity_days': 45,
                'total_sessions': 4,
                'total_price': 280.00,
                'discount_percentage': 15.0,
                'services_included': ['European Facial (75 min)', 'Hair Color - Full (120 min)', 'Gel Manicure (60 min)', 'Spa Pedicure (75 min)']
            },
            {
                'name': 'Relaxation Retreat',
                'description': 'Monthly wellness package for ultimate stress relief and relaxation',
                'package_type': 'membership',
                'validity_days': 90,
                'total_sessions': 6,
                'total_price': 450.00,
                'discount_percentage': 20.0,
                'services_included': ['Swedish Massage (60 min)', 'Deep Tissue Massage (90 min)', 'Aromatherapy Massage (60 min)']
            },
            {
                'name': 'Beauty Boost Package',
                'description': 'Complete beauty makeover with skincare, hair, and nail treatments',
                'package_type': 'regular',
                'validity_days': 60,
                'total_sessions': 5,
                'total_price': 320.00,
                'discount_percentage': 18.0,
                'services_included': ['Anti-Aging Facial (90 min)', 'Haircut & Style (45 min)', 'Hair Treatment & Mask (60 min)', 'Gel Manicure (60 min)']
            },
            {
                'name': 'Couples Spa Experience',
                'description': 'Romantic spa day for couples with massage and champagne',
                'package_type': 'regular',
                'validity_days': 30,
                'total_sessions': 2,
                'total_price': 300.00,
                'discount_percentage': 10.0,
                'services_included': ['Couples Massage (60 min)', 'European Facial (75 min)']
            }
        ]
        
        for pkg_data in packages_data:
            # Check if package exists
            existing_package = Package.query.filter_by(name=pkg_data['name']).first()
            if existing_package:
                continue
            
            # Calculate base pricing
            original_price = sum(service.price for service in services if service.name in pkg_data['services_included'])
            discount_amount = original_price * (pkg_data['discount_percentage'] / 100)
            final_price = original_price - discount_amount
            
            package = Package(
                name=pkg_data['name'],
                description=pkg_data['description'],
                package_type=pkg_data['package_type'],
                validity_days=pkg_data['validity_days'],
                duration_months=max(1, pkg_data['validity_days'] // 30),
                total_sessions=pkg_data['total_sessions'],
                total_price=pkg_data['total_price'],
                discount_percentage=pkg_data['discount_percentage'],
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(package)
            db.session.flush()  # Get package ID
            
            # Add package services
            for service_name in pkg_data['services_included']:
                service = next((s for s in services if s.name == service_name), None)
                if service:
                    package_service = PackageService(
                        package_id=package.id,
                        service_id=service.id,
                        sessions_included=1,  # Default to 1 session per service
                        service_discount=pkg_data['discount_percentage'],
                        original_price=service.price,
                        discounted_price=service.price * (1 - pkg_data['discount_percentage']/100)
                    )
                    db.session.add(package_service)
            
            self.created_data['packages'].append(package)
        
        db.session.flush()
        print(f"✅ Created {len(self.created_data['packages'])} packages")
    
    def create_appointment_data(self):
        """Create realistic appointment history and upcoming bookings"""
        print("📅 Creating appointments...")
        
        customers = self.created_data['customers'] if self.created_data['customers'] else Customer.query.all()
        services = self.created_data['services'] if self.created_data['services'] else Service.query.all()
        staff = self.created_data['staff'] if self.created_data['staff'] else User.query.filter(User.role.in_(['staff', 'manager'])).all()
        
        if not all([customers, services, staff]):
            print("⚠️ Missing required data for appointments")
            return
        
        # Generate appointments for past 30 days and next 30 days
        base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Past appointments (completed)
        for days_ago in range(30, 0, -1):
            apt_date = base_date - timedelta(days=days_ago)
            if apt_date.weekday() < 5:  # Monday-Friday
                num_appointments = random.randint(3, 8)
                
                for _ in range(num_appointments):
                    hour_offset = random.randint(0, 8)  # 9 AM to 5 PM
                    appointment_time = apt_date + timedelta(hours=hour_offset)
                    
                    customer = random.choice(customers)
                    service = random.choice(services)
                    staff_member = random.choice(staff)
                    
                    appointment = Appointment(
                        client_id=customer.id,
                        service_id=service.id,
                        staff_id=staff_member.id,
                        appointment_date=appointment_time,
                        end_time=appointment_time + timedelta(minutes=service.duration),
                        status='completed',
                        notes=random.choice([
                            'Great session, customer very satisfied',
                            'Regular customer, knows preferences',
                            'First time client, provided service explanation',
                            'Customer requested specific technique',
                            'Excellent results, customer happy'
                        ]),
                        amount=service.price,
                        discount=random.choice([0.0, 0.0, 0.0, 5.0, 10.0]),  # Mostly no discount
                        tips=random.choice([0.0, 0.0, 5.0, 10.0, 15.0, 20.0]),
                        payment_status='paid',
                        is_paid=True,
                        created_at=appointment_time - timedelta(hours=random.randint(1, 48)),
                        updated_at=appointment_time + timedelta(hours=2)
                    )
                    
                    db.session.add(appointment)
                    self.created_data['appointments'].append(appointment)
        
        # Today's appointments
        today_appointments = [
            {
                'client_id': customers[0].id,
                'service_id': services[0].id,
                'staff_id': staff[0].id,
                'time_offset': 1,  # 10 AM
                'status': 'confirmed',
                'notes': 'Regular customer, prefers medium pressure'
            },
            {
                'client_id': customers[1].id,
                'service_id': services[5].id,
                'staff_id': staff[1].id if len(staff) > 1 else staff[0].id,
                'time_offset': 3,  # 12 PM
                'status': 'in_progress',
                'notes': 'Customer arrived on time'
            },
            {
                'client_id': customers[2].id,
                'service_id': services[10].id,
                'staff_id': staff[0].id,
                'time_offset': 6,  # 3 PM
                'status': 'scheduled',
                'notes': 'New customer, first appointment'
            }
        ]
        
        for apt_data in today_appointments:
            service = Service.query.get(apt_data['service_id'])
            appointment_time = base_date + timedelta(hours=apt_data['time_offset'])
            
            appointment = Appointment(
                client_id=apt_data['client_id'],
                service_id=apt_data['service_id'],
                staff_id=apt_data['staff_id'],
                appointment_date=appointment_time,
                end_time=appointment_time + timedelta(minutes=service.duration),
                status=apt_data['status'],
                notes=apt_data['notes'],
                amount=service.price,
                payment_status='pending' if apt_data['status'] != 'completed' else 'paid',
                is_paid=apt_data['status'] == 'completed',
                created_at=datetime.utcnow()
            )
            
            db.session.add(appointment)
            self.created_data['appointments'].append(appointment)
        
        # Future appointments (next 2 weeks)
        for days_ahead in range(1, 15):
            apt_date = base_date + timedelta(days=days_ahead)
            if apt_date.weekday() < 5:  # Monday-Friday
                num_appointments = random.randint(2, 6)
                
                for _ in range(num_appointments):
                    hour_offset = random.randint(0, 8)
                    appointment_time = apt_date + timedelta(hours=hour_offset)
                    
                    customer = random.choice(customers)
                    service = random.choice(services)
                    staff_member = random.choice(staff)
                    
                    appointment = Appointment(
                        client_id=customer.id,
                        service_id=service.id,
                        staff_id=staff_member.id,
                        appointment_date=appointment_time,
                        end_time=appointment_time + timedelta(minutes=service.duration),
                        status=random.choice(['scheduled', 'confirmed']),
                        notes=random.choice([
                            'Regular appointment',
                            'Customer requested specific staff member',
                            'Booking made online',
                            'Phone booking',
                            'Walk-in converted to appointment'
                        ]),
                        amount=service.price,
                        payment_status='pending',
                        is_paid=False,
                        created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72))
                    )
                    
                    db.session.add(appointment)
                    self.created_data['appointments'].append(appointment)
        
        db.session.flush()
        print(f"✅ Created {len(self.created_data['appointments'])} appointments")
    
    def create_inventory_data(self):
        """Create inventory data if module exists"""
        print("📦 Creating inventory data...")
        
        try:
            from modules.inventory.models import InventoryCategory, InventoryLocation, InventoryProduct, InventoryBatch
            
            # Create inventory categories
            inv_categories_data = [
                {'name': 'Facial Products', 'description': 'Products for facial treatments'},
                {'name': 'Massage Oils', 'description': 'Oils and lotions for massage'},
                {'name': 'Hair Products', 'description': 'Hair care and styling products'},
                {'name': 'Nail Products', 'description': 'Nail care and polish products'},
                {'name': 'Disposables', 'description': 'Single-use items and supplies'}
            ]
            
            for cat_data in inv_categories_data:
                category = InventoryCategory(**cat_data, is_active=True)
                db.session.add(category)
                db.session.flush()
                
                # Create products for each category
                if cat_data['name'] == 'Facial Products':
                    products = [
                        {'sku': 'FAC001', 'name': 'Vitamin C Serum', 'unit_of_measure': 'ml'},
                        {'sku': 'FAC002', 'name': 'Hyaluronic Acid Cream', 'unit_of_measure': 'ml'},
                        {'sku': 'FAC003', 'name': 'Clay Mask', 'unit_of_measure': 'g'}
                    ]
                elif cat_data['name'] == 'Massage Oils':
                    products = [
                        {'sku': 'MAS001', 'name': 'Aromatherapy Oil', 'unit_of_measure': 'ml'},
                        {'sku': 'MAS002', 'name': 'Hot Stone Oil', 'unit_of_measure': 'ml'}
                    ]
                else:
                    continue  # Skip other categories for demo
                
                for prod_data in products:
                    product = InventoryProduct(
                        sku=prod_data['sku'],
                        name=prod_data['name'],
                        description=f"Professional grade {prod_data['name'].lower()}",
                        category_id=category.id,
                        unit_of_measure=prod_data['unit_of_measure'],
                        is_active=True
                    )
                    db.session.add(product)
                    db.session.flush()
                    
                    # Create batch for each product
                    batch = InventoryBatch(
                        batch_name=f"{prod_data['sku']}-{datetime.now().strftime('%Y%m')}-01",
                        product_id=product.id,
                        location_id='MAIN',
                        qty_available=random.randint(50, 200),
                        mfg_date=date.today() - timedelta(days=random.randint(30, 90)),
                        expiry_date=date.today() + timedelta(days=random.randint(180, 365)),
                        unit_cost=random.uniform(5.0, 25.0),
                        status='active'
                    )
                    db.session.add(batch)
            
            print("✅ Created inventory demo data")
            
        except ImportError:
            print("⚠️ Inventory module not available, skipping inventory data")
    
    def create_expense_data(self):
        """Create realistic expense records"""
        print("💰 Creating expenses...")
        
        office_cat = Category.query.filter_by(name='office', category_type='expense').first()
        supplies_cat = Category.query.filter_by(name='supplies', category_type='expense').first()
        admin_user = User.query.filter_by(role='admin').first()
        manager_user = next((u for u in self.created_data['staff'] if u.role == 'manager'), None)
        
        if not admin_user:
            admin_user = User.query.first()
        
        expenses_data = [
            {
                'description': 'Office rent for spa facility',
                'amount': 2500.00,
                'category': 'office',
                'category_id': office_cat.id if office_cat else None,
                'expense_date': date.today().replace(day=1),
                'receipt_number': 'RENT-2024-001',
                'notes': 'Monthly rent payment'
            },
            {
                'description': 'Massage oils and lotions supply',
                'amount': 450.00,
                'category': 'supplies',
                'category_id': supplies_cat.id if supplies_cat else None,
                'expense_date': date.today() - timedelta(days=5),
                'receipt_number': 'SUP-2024-023',
                'notes': 'Bulk purchase for massage therapy'
            },
            {
                'description': 'Electricity bill',
                'amount': 280.00,
                'category': 'office',
                'category_id': office_cat.id if office_cat else None,
                'expense_date': date.today() - timedelta(days=3),
                'receipt_number': 'ELEC-2024-012',
                'notes': 'Monthly electricity charges'
            },
            {
                'description': 'Facial product inventory',
                'amount': 680.00,
                'category': 'supplies',
                'category_id': supplies_cat.id if supplies_cat else None,
                'expense_date': date.today() - timedelta(days=7),
                'receipt_number': 'INV-2024-045',
                'notes': 'Premium facial products for treatments'
            },
            {
                'description': 'Marketing and advertising',
                'amount': 320.00,
                'category': 'office',
                'category_id': office_cat.id if office_cat else None,
                'expense_date': date.today() - timedelta(days=10),
                'receipt_number': 'MKT-2024-008',
                'notes': 'Social media advertising campaign'
            }
        ]
        
        for expense_data in expenses_data:
            expense_data['created_by'] = (manager_user or admin_user).id
            expense = Expense(**expense_data, created_at=datetime.utcnow())
            db.session.add(expense)
            self.created_data['expenses'].append(expense)
        
        # Generate more historical expenses
        for i in range(15):
            expense_date = date.today() - timedelta(days=random.randint(1, 60))
            expense = Expense(
                description=random.choice([
                    'Cleaning supplies', 'Towel laundry service', 'Equipment maintenance',
                    'Staff training materials', 'Insurance payment', 'Phone and internet',
                    'Water bill', 'Product samples', 'Reception supplies'
                ]),
                amount=random.uniform(25.0, 500.0),
                category=random.choice(['office', 'supplies']),
                category_id=random.choice([office_cat.id, supplies_cat.id]) if office_cat and supplies_cat else None,
                expense_date=expense_date,
                receipt_number=f'EXP-2024-{str(i+100).zfill(3)}',
                created_by=(manager_user or admin_user).id,
                created_at=datetime.utcnow()
            )
            db.session.add(expense)
            self.created_data['expenses'].append(expense)
        
        db.session.flush()
        print(f"✅ Created {len(self.created_data['expenses'])} expenses")
    
    def create_invoice_data(self):
        """Create sample invoices"""
        print("🧾 Creating invoices...")
        
        # Create a few sample invoices from recent appointments
        recent_appointments = [apt for apt in self.created_data['appointments'] if apt.status == 'completed'][:5]
        
        for i, appointment in enumerate(recent_appointments, 1):
            invoice = Invoice(
                invoice_number=f'INV-2024-{str(i).zfill(4)}',
                client_id=appointment.client_id,
                appointment_id=appointment.id,
                invoice_date=appointment.appointment_date + timedelta(hours=1),
                due_date=appointment.appointment_date + timedelta(days=30),
                subtotal=appointment.amount,
                tax_amount=appointment.amount * 0.08,  # 8% tax
                discount_amount=appointment.discount or 0.0,
                tips_amount=appointment.tips or 0.0,
                total_amount=appointment.amount + (appointment.amount * 0.08) - (appointment.discount or 0.0) + (appointment.tips or 0.0),
                payment_status='paid',
                payment_method='cash',
                notes='Service completed satisfactorily',
                created_at=appointment.appointment_date + timedelta(hours=1)
            )
            db.session.add(invoice)
            self.created_data['invoices'].append(invoice)
        
        db.session.flush()
        print(f"✅ Created {len(self.created_data['invoices'])} invoices")
    
    def print_summary(self):
        """Print comprehensive summary of created data"""
        print(f"""
🎊 DEMO DATA GENERATION SUMMARY:

📊 SYSTEM DATA:
   • {len(self.created_data['roles'])} Roles created
   • {len(self.created_data['departments'])} Departments created  
   • {len(self.created_data['categories'])} Categories created

👥 PEOPLE:
   • {len(self.created_data['staff'])} Staff members created
   • {len(self.created_data['customers'])} Customers created

💼 BUSINESS DATA:
   • {len(self.created_data['services'])} Services created
   • {len(self.created_data['packages'])} Packages created
   • {len(self.created_data['appointments'])} Appointments created
   • {len(self.created_data['expenses'])} Expenses created
   • {len(self.created_data['invoices'])} Invoices created

🔐 LOGIN CREDENTIALS:
   • Admin: admin / admin123
   • Manager: spa_manager / password123
   • Staff: mike_therapist / password123
   • All staff: password123

📱 DEMO FEATURES READY:
   ✅ Staff Management with roles and departments
   ✅ Customer database with preferences and history  
   ✅ Complete service catalog with pricing
   ✅ Package deals and memberships
   ✅ Appointment scheduling with history
   ✅ Expense tracking and reporting
   ✅ Invoice generation and billing
   ✅ Inventory management (if module available)

🚀 Your spa management system is now production-ready for demonstrations!
        """)

def main():
    """Main function to run demo data generation"""
    generator = DemoDataGenerator()
    generator.generate_all_demo_data()

if __name__ == "__main__":
    main()
