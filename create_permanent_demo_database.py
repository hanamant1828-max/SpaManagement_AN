
#!/usr/bin/env python3
"""
Create a permanent demo database that will be included in the project structure
This database will be cloned with the project and work immediately
"""

import os
import sys
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import *

def create_permanent_demo_database():
    """Create a permanent demo database with all sample data"""
    
    # Ensure the instance directory exists
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    
    with app.app_context():
        print("🔄 Creating permanent demo database...")
        
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create roles
        roles_data = [
            {'name': 'admin', 'display_name': 'Administrator', 'description': 'Full system access'},
            {'name': 'manager', 'display_name': 'Manager', 'description': 'Management level access'},
            {'name': 'staff', 'display_name': 'Staff Member', 'description': 'Service staff access'},
            {'name': 'receptionist', 'display_name': 'Receptionist', 'description': 'Front desk operations'}
        ]
        
        for role_data in roles_data:
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
            dept = Department(**dept_data)
            db.session.add(dept)
        
        db.session.commit()
        
        # Create comprehensive staff members with realistic data
        staff_data = [
            {
                'username': 'admin', 'email': 'admin@spa.com', 'password': 'admin123',
                'first_name': 'Admin', 'last_name': 'User', 'role': 'admin',
                'phone': '+91-9876543210', 'employee_id': 'SPA001',
                'designation': 'System Administrator', 'gender': 'other'
            },
            {
                'username': 'sarah_manager', 'email': 'sarah@spa.com', 'password': 'sarah123',
                'first_name': 'Sarah', 'last_name': 'Johnson', 'role': 'manager',
                'phone': '+91-9876543211', 'employee_id': 'SPA002',
                'designation': 'Spa Manager', 'gender': 'female'
            },
            {
                'username': 'priya_therapist', 'email': 'priya@spa.com', 'password': 'priya123',
                'first_name': 'Priya', 'last_name': 'Sharma', 'role': 'staff',
                'phone': '+91-9876543212', 'employee_id': 'SPA003',
                'designation': 'Senior Therapist', 'gender': 'female'
            },
            {
                'username': 'maya_receptionist', 'email': 'maya@spa.com', 'password': 'maya123',
                'first_name': 'Maya', 'last_name': 'Patel', 'role': 'receptionist',
                'phone': '+91-9876543213', 'employee_id': 'SPA004',
                'designation': 'Front Desk Executive', 'gender': 'female'
            },
            {
                'username': 'raj_therapist', 'email': 'raj@spa.com', 'password': 'raj123',
                'first_name': 'Raj', 'last_name': 'Kumar', 'role': 'staff',
                'phone': '+91-9876543214', 'employee_id': 'SPA005',
                'designation': 'Massage Therapist', 'gender': 'male'
            }
        ]
        
        for staff in staff_data:
            user = User(
                username=staff['username'],
                email=staff['email'],
                password_hash=generate_password_hash(staff['password']),
                first_name=staff['first_name'],
                last_name=staff['last_name'],
                role=staff['role'],
                phone=staff['phone'],
                employee_id=staff['employee_id'],
                designation=staff['designation'],
                gender=staff['gender'],
                is_active=True,
                hire_date=date.today() - timedelta(days=365),
                commission_rate=15.0,
                hourly_rate=500.0
            )
            db.session.add(user)
        
        # Create service categories
        categories_data = [
            {'name': 'facial_treatments', 'display_name': 'Facial Treatments', 'category_type': 'service', 'color': '#e74c3c', 'icon': 'fas fa-face-smile'},
            {'name': 'body_treatments', 'display_name': 'Body Treatments', 'category_type': 'service', 'color': '#3498db', 'icon': 'fas fa-spa'},
            {'name': 'massage_therapy', 'display_name': 'Massage Therapy', 'category_type': 'service', 'color': '#2ecc71', 'icon': 'fas fa-hands'},
            {'name': 'wellness', 'display_name': 'Wellness & Relaxation', 'category_type': 'service', 'color': '#9b59b6', 'icon': 'fas fa-leaf'}
        ]
        
        for cat_data in categories_data:
            category = Category(**cat_data)
            db.session.add(category)
        
        db.session.commit()
        
        # Create comprehensive services
        services_data = [
            {'name': 'Classic Facial', 'duration': 60, 'price': 2500.00, 'category': 'facial_treatments', 'description': 'Deep cleansing facial with steam and extraction'},
            {'name': 'Anti-Aging Facial', 'duration': 90, 'price': 3500.00, 'category': 'facial_treatments', 'description': 'Premium anti-aging treatment with collagen mask'},
            {'name': 'Gold Facial', 'duration': 75, 'price': 4500.00, 'category': 'facial_treatments', 'description': 'Luxury gold leaf facial treatment'},
            {'name': 'Deep Tissue Massage', 'duration': 60, 'price': 3000.00, 'category': 'massage_therapy', 'description': 'Therapeutic deep tissue massage'},
            {'name': 'Swedish Massage', 'duration': 45, 'price': 2200.00, 'category': 'massage_therapy', 'description': 'Relaxing full body Swedish massage'},
            {'name': 'Hot Stone Massage', 'duration': 90, 'price': 3800.00, 'category': 'massage_therapy', 'description': 'Heated stone therapy massage'},
            {'name': 'Body Scrub & Wrap', 'duration': 120, 'price': 4500.00, 'category': 'body_treatments', 'description': 'Full body exfoliation and nourishing wrap'},
            {'name': 'Aromatherapy Session', 'duration': 75, 'price': 2800.00, 'category': 'wellness', 'description': 'Essential oil aromatherapy treatment'},
            {'name': 'Couples Massage', 'duration': 60, 'price': 5500.00, 'category': 'massage_therapy', 'description': 'Side-by-side couples relaxation massage'}
        ]
        
        for service_data in services_data:
            service = Service(
                name=service_data['name'],
                duration=service_data['duration'],
                price=service_data['price'],
                category=service_data['category'],
                description=service_data['description'],
                is_active=True
            )
            db.session.add(service)
        
        # Create sample customers with realistic data
        customers_data = [
            {'first_name': 'Anita', 'last_name': 'Reddy', 'email': 'anita.reddy@email.com', 'phone': '+91-9876543220', 'gender': 'female', 'visits': 12, 'spent': 28500.00},
            {'first_name': 'Rajesh', 'last_name': 'Kumar', 'email': 'rajesh.kumar@email.com', 'phone': '+91-9876543221', 'gender': 'male', 'visits': 8, 'spent': 18200.00},
            {'first_name': 'Deepika', 'last_name': 'Singh', 'email': 'deepika.singh@email.com', 'phone': '+91-9876543222', 'gender': 'female', 'visits': 15, 'spent': 35600.00},
            {'first_name': 'Arjun', 'last_name': 'Mehta', 'email': 'arjun.mehta@email.com', 'phone': '+91-9876543223', 'gender': 'male', 'visits': 6, 'spent': 14800.00},
            {'first_name': 'Kavya', 'last_name': 'Nair', 'email': 'kavya.nair@email.com', 'phone': '+91-9876543224', 'gender': 'female', 'visits': 20, 'spent': 45300.00}
        ]
        
        for customer_data in customers_data:
            customer = Customer(
                first_name=customer_data['first_name'],
                last_name=customer_data['last_name'],
                email=customer_data['email'],
                phone=customer_data['phone'],
                gender=customer_data['gender'],
                total_visits=customer_data['visits'],
                total_spent=customer_data['spent'],
                loyalty_points=int(customer_data['spent'] / 100),
                is_vip=customer_data['spent'] > 25000,
                last_visit=datetime.now() - timedelta(days=7)
            )
            db.session.add(customer)
        
        # Create sample packages
        packages_data = [
            {
                'name': 'Wellness Premium Package', 'duration_months': 3, 'total_sessions': 8,
                'total_price': 18000.00, 'description': '8 sessions of premium wellness treatments',
                'validity_days': 90
            },
            {
                'name': 'Facial Care Package', 'duration_months': 2, 'total_sessions': 5,
                'total_price': 12500.00, 'description': '5 premium facial treatment sessions',
                'validity_days': 60
            },
            {
                'name': 'Couple Spa Package', 'duration_months': 1, 'total_sessions': 3,
                'total_price': 15000.00, 'description': '3 couples spa sessions',
                'validity_days': 30
            }
        ]
        
        for package_data in packages_data:
            package = Package(**package_data)
            db.session.add(package)
        
        # Create sample appointments (recent and upcoming)
        db.session.commit()
        
        # Get the created users and customers for appointments
        staff_members = User.query.filter(User.role.in_(['staff'])).all()
        customers = Customer.query.all()
        services = Service.query.all()
        
        # Create some sample appointments
        sample_appointments = [
            {
                'client': customers[0], 'service': services[0], 'staff': staff_members[0],
                'date': datetime.now() + timedelta(days=1), 'status': 'scheduled'
            },
            {
                'client': customers[1], 'service': services[3], 'staff': staff_members[0],
                'date': datetime.now() + timedelta(days=2), 'status': 'confirmed'
            },
            {
                'client': customers[2], 'service': services[1], 'staff': staff_members[0],
                'date': datetime.now() - timedelta(days=1), 'status': 'completed'
            }
        ]
        
        for apt_data in sample_appointments:
            appointment = Appointment(
                client_id=apt_data['client'].id,
                service_id=apt_data['service'].id,
                staff_id=apt_data['staff'].id,
                appointment_date=apt_data['date'],
                end_time=apt_data['date'] + timedelta(minutes=apt_data['service'].duration),
                status=apt_data['status'],
                amount=apt_data['service'].price,
                is_paid=(apt_data['status'] == 'completed')
            )
            db.session.add(appointment)
        
        db.session.commit()
        
        print("✅ Permanent demo database created successfully!")
        print(f"\n📊 Database Summary:")
        print(f"   👥 Staff Members: {User.query.count()}")
        print(f"   👤 Customers: {Customer.query.count()}")
        print(f"   💆 Services: {Service.query.count()}")
        print(f"   📦 Packages: {Package.query.count()}")
        print(f"   📅 Appointments: {Appointment.query.count()}")
        print(f"   🏢 Departments: {Department.query.count()}")
        print(f"   🔐 Roles: {Role.query.count()}")
        
        print(f"\n🔑 Login Credentials:")
        print("   Username: admin | Password: admin123 (Administrator)")
        print("   Username: sarah_manager | Password: sarah123 (Manager)")
        print("   Username: priya_therapist | Password: priya123 (Therapist)")
        print("   Username: maya_receptionist | Password: maya123 (Receptionist)")
        print("   Username: raj_therapist | Password: raj123 (Therapist)")
        
        print(f"\n🗃️ Database Location: {os.path.join(instance_dir, 'spa_management.db')}")
        print("   This database will be included in your project structure and work immediately when cloned!")

if __name__ == "__main__":
    create_permanent_demo_database()
