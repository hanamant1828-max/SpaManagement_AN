
#!/usr/bin/env python3
"""
Populate complete demo data for the Spa Management System
This data will be saved in the local SQLite database and persist with the project
"""

import os
import sys
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash
import random

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import *

def create_complete_demo_data():
    """Create comprehensive demo data that will persist in the local database"""
    
    with app.app_context():
        print("🔄 Creating comprehensive demo data for local SQLite database...")
        print("📍 This data will be saved in instance/spa_management.db and pushed to GitHub")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        # db.drop_all()
        # db.create_all()
        
        # Create roles and departments first
        roles_data = [
            {'name': 'admin', 'display_name': 'Administrator', 'description': 'Full system access'},
            {'name': 'manager', 'display_name': 'Manager', 'description': 'Management level access'},
            {'name': 'staff', 'display_name': 'Staff Member', 'description': 'Service staff access'},
            {'name': 'receptionist', 'display_name': 'Receptionist', 'description': 'Front desk operations'},
            {'name': 'therapist', 'display_name': 'Therapist', 'description': 'Spa therapy specialist'}
        ]
        
        for role_data in roles_data:
            if not Role.query.filter_by(name=role_data['name']).first():
                role = Role(**role_data)
                db.session.add(role)
        
        departments_data = [
            {'name': 'management', 'display_name': 'Management', 'description': 'Administrative department'},
            {'name': 'spa_services', 'display_name': 'Spa Services', 'description': 'Body treatments and massages'},
            {'name': 'facial_services', 'display_name': 'Facial Services', 'description': 'Facial treatments and skincare'},
            {'name': 'reception', 'display_name': 'Reception', 'description': 'Front desk and customer service'},
            {'name': 'wellness', 'display_name': 'Wellness Center', 'description': 'Holistic wellness treatments'}
        ]
        
        for dept_data in departments_data:
            if not Department.query.filter_by(name=dept_data['name']).first():
                dept = Department(**dept_data)
                db.session.add(dept)
        
        db.session.commit()
        
        # Create comprehensive staff members
        staff_data = [
            {
                'username': 'admin', 'email': 'admin@spa.com', 'password': 'admin123',
                'first_name': 'Admin', 'last_name': 'User', 'role': 'admin',
                'phone': '+91-9876543210', 'employee_id': 'EMP001', 'department': 'management'
            },
            {
                'username': 'sarah_manager', 'email': 'sarah@spa.com', 'password': 'sarah123',
                'first_name': 'Sarah', 'last_name': 'Johnson', 'role': 'manager',
                'phone': '+91-9876543211', 'employee_id': 'EMP002', 'department': 'management'
            },
            {
                'username': 'priya_therapist', 'email': 'priya@spa.com', 'password': 'priya123',
                'first_name': 'Priya', 'last_name': 'Sharma', 'role': 'therapist',
                'phone': '+91-9876543212', 'employee_id': 'EMP003', 'department': 'spa_services'
            },
            {
                'username': 'maya_receptionist', 'email': 'maya@spa.com', 'password': 'maya123',
                'first_name': 'Maya', 'last_name': 'Patel', 'role': 'receptionist',
                'phone': '+91-9876543213', 'employee_id': 'EMP004', 'department': 'reception'
            },
            {
                'username': 'arjun_therapist', 'email': 'arjun@spa.com', 'password': 'arjun123',
                'first_name': 'Arjun', 'last_name': 'Kumar', 'role': 'therapist',
                'phone': '+91-9876543214', 'employee_id': 'EMP005', 'department': 'spa_services'
            },
            {
                'username': 'neha_facial', 'email': 'neha@spa.com', 'password': 'neha123',
                'first_name': 'Neha', 'last_name': 'Gupta', 'role': 'staff',
                'phone': '+91-9876543215', 'employee_id': 'EMP006', 'department': 'facial_services'
            }
        ]
        
        for staff in staff_data:
            if not User.query.filter_by(username=staff['username']).first():
                user = User(
                    username=staff['username'],
                    email=staff['email'],
                    password_hash=generate_password_hash(staff['password']),
                    first_name=staff['first_name'],
                    last_name=staff['last_name'],
                    role=staff['role'],
                    phone=staff['phone'],
                    employee_id=staff['employee_id'],
                    department=staff['department'],
                    is_active=True,
                    hire_date=date.today() - timedelta(days=random.randint(30, 365)),
                    commission_rate=random.uniform(10.0, 25.0),
                    hourly_rate=random.uniform(200.0, 500.0)
                )
                db.session.add(user)
        
        # Create service categories
        categories_data = [
            {'name': 'facial_treatments', 'display_name': 'Facial Treatments', 'category_type': 'service', 'color': '#e74c3c'},
            {'name': 'body_treatments', 'display_name': 'Body Treatments', 'category_type': 'service', 'color': '#3498db'},
            {'name': 'massage_therapy', 'display_name': 'Massage Therapy', 'category_type': 'service', 'color': '#2ecc71'},
            {'name': 'wellness', 'display_name': 'Wellness & Relaxation', 'category_type': 'service', 'color': '#9b59b6'},
            {'name': 'hair_care', 'display_name': 'Hair Care', 'category_type': 'service', 'color': '#f39c12'},
            {'name': 'nail_care', 'display_name': 'Nail Care', 'category_type': 'service', 'color': '#e67e22'}
        ]
        
        for cat_data in categories_data:
            if not Category.query.filter_by(name=cat_data['name']).first():
                category = Category(**cat_data)
                db.session.add(category)
        
        db.session.commit()
        
        # Create comprehensive services
        services_data = [
            # Facial Treatments
            {'name': 'Classic Facial', 'duration': 60, 'price': 2500.00, 'category': 'facial_treatments'},
            {'name': 'Anti-Aging Facial', 'duration': 90, 'price': 3500.00, 'category': 'facial_treatments'},
            {'name': 'Hydrating Facial', 'duration': 75, 'price': 3000.00, 'category': 'facial_treatments'},
            {'name': 'Acne Treatment Facial', 'duration': 60, 'price': 2800.00, 'category': 'facial_treatments'},
            
            # Massage Therapy
            {'name': 'Deep Tissue Massage', 'duration': 60, 'price': 3000.00, 'category': 'massage_therapy'},
            {'name': 'Swedish Massage', 'duration': 45, 'price': 2200.00, 'category': 'massage_therapy'},
            {'name': 'Hot Stone Massage', 'duration': 90, 'price': 4000.00, 'category': 'massage_therapy'},
            {'name': 'Aromatherapy Massage', 'duration': 75, 'price': 3500.00, 'category': 'massage_therapy'},
            
            # Body Treatments
            {'name': 'Body Scrub & Wrap', 'duration': 120, 'price': 4500.00, 'category': 'body_treatments'},
            {'name': 'Detox Body Wrap', 'duration': 90, 'price': 3800.00, 'category': 'body_treatments'},
            {'name': 'Moisturizing Body Treatment', 'duration': 60, 'price': 2800.00, 'category': 'body_treatments'},
            
            # Wellness
            {'name': 'Aromatherapy Session', 'duration': 75, 'price': 2800.00, 'category': 'wellness'},
            {'name': 'Meditation & Relaxation', 'duration': 45, 'price': 1800.00, 'category': 'wellness'},
            
            # Hair Care
            {'name': 'Hair Spa Treatment', 'duration': 120, 'price': 3200.00, 'category': 'hair_care'},
            {'name': 'Hair Styling', 'duration': 60, 'price': 1500.00, 'category': 'hair_care'},
            
            # Nail Care
            {'name': 'Manicure', 'duration': 45, 'price': 1200.00, 'category': 'nail_care'},
            {'name': 'Pedicure', 'duration': 60, 'price': 1500.00, 'category': 'nail_care'}
        ]
        
        for service_data in services_data:
            if not Service.query.filter_by(name=service_data['name']).first():
                service = Service(
                    name=service_data['name'],
                    duration=service_data['duration'],
                    price=service_data['price'],
                    category=service_data['category'],
                    description=f"Professional {service_data['name'].lower()} service for ultimate relaxation and wellness",
                    is_active=True
                )
                db.session.add(service)
        
        # Create diverse customers
        customers_data = [
            {
                'first_name': 'Anita', 'last_name': 'Reddy', 'email': 'anita.reddy@email.com',
                'phone': '+91-9876543220', 'gender': 'female', 'city': 'Mumbai'
            },
            {
                'first_name': 'Rajesh', 'last_name': 'Kumar', 'email': 'rajesh.kumar@email.com',
                'phone': '+91-9876543221', 'gender': 'male', 'city': 'Delhi'
            },
            {
                'first_name': 'Deepika', 'last_name': 'Singh', 'email': 'deepika.singh@email.com',
                'phone': '+91-9876543222', 'gender': 'female', 'city': 'Bangalore'
            },
            {
                'first_name': 'Amit', 'last_name': 'Sharma', 'email': 'amit.sharma@email.com',
                'phone': '+91-9876543223', 'gender': 'male', 'city': 'Chennai'
            },
            {
                'first_name': 'Kavya', 'last_name': 'Nair', 'email': 'kavya.nair@email.com',
                'phone': '+91-9876543224', 'gender': 'female', 'city': 'Hyderabad'
            },
            {
                'first_name': 'Rohan', 'last_name': 'Mehta', 'email': 'rohan.mehta@email.com',
                'phone': '+91-9876543225', 'gender': 'male', 'city': 'Pune'
            },
            {
                'first_name': 'Sneha', 'last_name': 'Iyer', 'email': 'sneha.iyer@email.com',
                'phone': '+91-9876543226', 'gender': 'female', 'city': 'Kochi'
            },
            {
                'first_name': 'Vikram', 'last_name': 'Joshi', 'email': 'vikram.joshi@email.com',
                'phone': '+91-9876543227', 'gender': 'male', 'city': 'Ahmedabad'
            }
        ]
        
        for customer_data in customers_data:
            if not Customer.query.filter_by(email=customer_data['email']).first():
                customer = Customer(
                    first_name=customer_data['first_name'],
                    last_name=customer_data['last_name'],
                    email=customer_data['email'],
                    phone=customer_data['phone'],
                    gender=customer_data['gender'],
                    address=f"123 Main Street, {customer_data['city']}",
                    total_visits=random.randint(1, 15),
                    total_spent=random.uniform(5000.0, 50000.0),
                    loyalty_points=random.randint(50, 500),
                    date_of_birth=date.today() - timedelta(days=random.randint(7300, 18250))  # 20-50 years old
                )
                db.session.add(customer)
        
        # Create comprehensive packages
        packages_data = [
            {
                'name': 'Wellness Starter Package', 'duration_months': 3, 'total_sessions': 6,
                'total_price': 15000.00, 'description': '6 sessions of mixed wellness treatments perfect for beginners'
            },
            {
                'name': 'Facial Care Premium', 'duration_months': 2, 'total_sessions': 4,
                'total_price': 12000.00, 'description': '4 premium facial treatment sessions for glowing skin'
            },
            {
                'name': 'Complete Spa Experience', 'duration_months': 6, 'total_sessions': 12,
                'total_price': 35000.00, 'description': '12 sessions covering all spa services - the ultimate package'
            },
            {
                'name': 'Massage Therapy Package', 'duration_months': 4, 'total_sessions': 8,
                'total_price': 20000.00, 'description': '8 therapeutic massage sessions for stress relief'
            },
            {
                'name': 'Bridal Special Package', 'duration_months': 1, 'total_sessions': 5,
                'total_price': 18000.00, 'description': 'Pre-wedding beauty package with facial, body treatments'
            }
        ]
        
        for package_data in packages_data:
            if not Package.query.filter_by(name=package_data['name']).first():
                package = Package(
                    name=package_data['name'],
                    duration_months=package_data['duration_months'],
                    total_sessions=package_data['total_sessions'],
                    total_price=package_data['total_price'],
                    description=package_data['description'],
                    discount_percentage=random.uniform(10.0, 25.0),
                    validity_days=package_data['duration_months'] * 30,
                    is_active=True
                )
                db.session.add(package)
        
        # Create sample appointments (recent and upcoming)
        db.session.commit()  # Commit to get IDs
        
        customers = Customer.query.all()
        services = Service.query.all()
        staff_members = User.query.filter(User.role.in_(['staff', 'therapist'])).all()
        
        if customers and services and staff_members:
            for i in range(20):  # Create 20 sample appointments
                appointment_date = datetime.now() + timedelta(days=random.randint(-30, 30))
                service = random.choice(services)
                
                appointment = Appointment(
                    client_id=random.choice(customers).id,
                    service_id=service.id,
                    staff_id=random.choice(staff_members).id,
                    appointment_date=appointment_date,
                    end_time=appointment_date + timedelta(minutes=service.duration),
                    status=random.choice(['scheduled', 'completed', 'confirmed']),
                    amount=service.price,
                    notes=f"Demo appointment for {service.name}"
                )
                db.session.add(appointment)
        
        # Create sample expenses
        expense_categories = ['utilities', 'supplies', 'marketing', 'maintenance', 'staff_training']
        admin_user = User.query.filter_by(role='admin').first()
        
        if admin_user:
            for i in range(15):  # Create 15 sample expenses
                expense = Expense(
                    description=f"Demo expense item #{i+1}",
                    amount=random.uniform(500.0, 5000.0),
                    category=random.choice(expense_categories),
                    expense_date=date.today() - timedelta(days=random.randint(1, 60)),
                    created_by=admin_user.id,
                    receipt_number=f"RCP-{1000+i}",
                    notes="Sample expense for demonstration"
                )
                db.session.add(expense)
        
        db.session.commit()
        
        print("✅ Comprehensive demo data created successfully!")
        print("\n📊 Demo Data Summary:")
        print(f"   👥 Staff Members: {User.query.count()}")
        print(f"   👤 Customers: {Customer.query.count()}")
        print(f"   💆 Services: {Service.query.count()}")
        print(f"   📦 Packages: {Package.query.count()}")
        print(f"   📅 Appointments: {Appointment.query.count()}")
        print(f"   💰 Expenses: {Expense.query.count()}")
        print(f"   🏢 Departments: {Department.query.count()}")
        print(f"   🔐 Roles: {Role.query.count()}")
        print(f"   📋 Categories: {Category.query.count()}")
        
        print("\n🔑 Login Credentials:")
        print("   Username: admin | Password: admin123 (Administrator)")
        print("   Username: sarah_manager | Password: sarah123 (Manager)")
        print("   Username: priya_therapist | Password: priya123 (Therapist)")
        print("   Username: maya_receptionist | Password: maya123 (Receptionist)")
        print("   Username: arjun_therapist | Password: arjun123 (Therapist)")
        print("   Username: neha_facial | Password: neha123 (Facial Specialist)")
        
        print(f"\n💾 Database Location: {os.path.join(os.path.dirname(__file__), 'instance', 'spa_management.db')}")
        print("🚀 This database file will be included when you push to GitHub!")

if __name__ == "__main__":
    create_complete_demo_data()
