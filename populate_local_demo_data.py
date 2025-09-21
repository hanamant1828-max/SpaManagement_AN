
#!/usr/bin/env python3
"""
Populate local SQLite database with comprehensive demo data
"""

import os
import sys
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import *

def create_demo_data():
    """Create comprehensive demo data for the spa management system"""
    
    with app.app_context():
        print("🔄 Creating demo data for local database...")
        
        # Create roles
        roles_data = [
            {'name': 'admin', 'display_name': 'Administrator', 'description': 'Full system access'},
            {'name': 'manager', 'display_name': 'Manager', 'description': 'Management level access'},
            {'name': 'staff', 'display_name': 'Staff Member', 'description': 'Service staff access'},
            {'name': 'receptionist', 'display_name': 'Receptionist', 'description': 'Front desk operations'}
        ]
        
        for role_data in roles_data:
            if not Role.query.filter_by(name=role_data['name']).first():
                role = Role(**role_data)
                db.session.add(role)
        
        # Create departments
        departments_data = [
            {'name': 'management', 'display_name': 'Management', 'description': 'Administrative department'},
            {'name': 'spa_services', 'display_name': 'Spa Services', 'description': 'Body treatments and massages'},
            {'name': 'facial_services', 'display_name': 'Facial Services', 'description': 'Facial treatments and skincare'},
            {'name': 'reception', 'display_name': 'Reception', 'description': 'Front desk and customer service'}
        ]
        
        for dept_data in departments_data:
            if not Department.query.filter_by(name=dept_data['name']).first():
                dept = Department(**dept_data)
                db.session.add(dept)
        
        db.session.commit()
        
        # Create staff members
        staff_data = [
            {
                'username': 'admin', 'email': 'admin@spa.com', 'password': 'admin123',
                'first_name': 'Admin', 'last_name': 'User', 'role': 'admin',
                'phone': '+91-9876543210', 'employee_id': 'EMP001'
            },
            {
                'username': 'sarah_manager', 'email': 'sarah@spa.com', 'password': 'sarah123',
                'first_name': 'Sarah', 'last_name': 'Johnson', 'role': 'manager',
                'phone': '+91-9876543211', 'employee_id': 'EMP002'
            },
            {
                'username': 'priya_therapist', 'email': 'priya@spa.com', 'password': 'priya123',
                'first_name': 'Priya', 'last_name': 'Sharma', 'role': 'staff',
                'phone': '+91-9876543212', 'employee_id': 'EMP003'
            },
            {
                'username': 'maya_receptionist', 'email': 'maya@spa.com', 'password': 'maya123',
                'first_name': 'Maya', 'last_name': 'Patel', 'role': 'receptionist',
                'phone': '+91-9876543213', 'employee_id': 'EMP004'
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
                    is_active=True,
                    hire_date=date.today() - timedelta(days=365)
                )
                db.session.add(user)
        
        # Create service categories
        categories_data = [
            {'name': 'facial_treatments', 'display_name': 'Facial Treatments', 'category_type': 'service', 'color': '#e74c3c'},
            {'name': 'body_treatments', 'display_name': 'Body Treatments', 'category_type': 'service', 'color': '#3498db'},
            {'name': 'massage_therapy', 'display_name': 'Massage Therapy', 'category_type': 'service', 'color': '#2ecc71'},
            {'name': 'wellness', 'display_name': 'Wellness & Relaxation', 'category_type': 'service', 'color': '#9b59b6'}
        ]
        
        for cat_data in categories_data:
            if not Category.query.filter_by(name=cat_data['name']).first():
                category = Category(**cat_data)
                db.session.add(category)
        
        db.session.commit()
        
        # Create services
        services_data = [
            {'name': 'Classic Facial', 'duration': 60, 'price': 2500.00, 'category': 'facial_treatments'},
            {'name': 'Anti-Aging Facial', 'duration': 90, 'price': 3500.00, 'category': 'facial_treatments'},
            {'name': 'Deep Tissue Massage', 'duration': 60, 'price': 3000.00, 'category': 'massage_therapy'},
            {'name': 'Swedish Massage', 'duration': 45, 'price': 2200.00, 'category': 'massage_therapy'},
            {'name': 'Body Scrub & Wrap', 'duration': 120, 'price': 4500.00, 'category': 'body_treatments'},
            {'name': 'Aromatherapy Session', 'duration': 75, 'price': 2800.00, 'category': 'wellness'}
        ]
        
        for service_data in services_data:
            if not Service.query.filter_by(name=service_data['name']).first():
                service = Service(
                    name=service_data['name'],
                    duration=service_data['duration'],
                    price=service_data['price'],
                    category=service_data['category'],
                    description=f"Professional {service_data['name'].lower()} service",
                    is_active=True
                )
                db.session.add(service)
        
        # Create sample customers
        customers_data = [
            {
                'first_name': 'Anita', 'last_name': 'Reddy', 'email': 'anita.reddy@email.com',
                'phone': '+91-9876543220', 'gender': 'female'
            },
            {
                'first_name': 'Rajesh', 'last_name': 'Kumar', 'email': 'rajesh.kumar@email.com',
                'phone': '+91-9876543221', 'gender': 'male'
            },
            {
                'first_name': 'Deepika', 'last_name': 'Singh', 'email': 'deepika.singh@email.com',
                'phone': '+91-9876543222', 'gender': 'female'
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
                    total_visits=5,
                    total_spent=12500.00,
                    loyalty_points=125
                )
                db.session.add(customer)
        
        # Create sample packages
        packages_data = [
            {
                'name': 'Wellness Package', 'duration_months': 3, 'total_sessions': 6,
                'total_price': 15000.00, 'description': '6 sessions of mixed wellness treatments'
            },
            {
                'name': 'Facial Care Package', 'duration_months': 2, 'total_sessions': 4,
                'total_price': 10000.00, 'description': '4 premium facial treatment sessions'
            }
        ]
        
        for package_data in packages_data:
            if not Package.query.filter_by(name=package_data['name']).first():
                package = Package(**package_data)
                db.session.add(package)
        
        db.session.commit()
        
        print("✅ Demo data created successfully!")
        print("\n📊 Summary:")
        print(f"   👥 Staff Members: {User.query.count()}")
        print(f"   👤 Customers: {Customer.query.count()}")
        print(f"   💆 Services: {Service.query.count()}")
        print(f"   📦 Packages: {Package.query.count()}")
        print(f"   🏢 Departments: {Department.query.count()}")
        print(f"   🔐 Roles: {Role.query.count()}")
        
        print("\n🔑 Login Credentials:")
        print("   Username: admin | Password: admin123 (Administrator)")
        print("   Username: sarah_manager | Password: sarah123 (Manager)")
        print("   Username: priya_therapist | Password: priya123 (Staff)")
        print("   Username: maya_receptionist | Password: maya123 (Receptionist)")

if __name__ == "__main__":
    create_demo_data()
