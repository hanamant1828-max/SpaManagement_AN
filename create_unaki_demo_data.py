
#!/usr/bin/env python3
"""
Create demo data for Unaki booking system
"""

from app import app, db
from models import User, Service, Customer, Category
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_unaki_demo_data():
    """Create demo data for Unaki booking system"""
    with app.app_context():
        try:
            # Create service categories
            categories = [
                {'name': 'massage', 'display_name': 'Massage Therapy', 'category_type': 'service'},
                {'name': 'facial', 'display_name': 'Facial Treatments', 'category_type': 'service'},
                {'name': 'nails', 'display_name': 'Nail Care', 'category_type': 'service'}
            ]
            
            for cat_data in categories:
                existing = Category.query.filter_by(name=cat_data['name'], category_type='service').first()
                if not existing:
                    category = Category(**cat_data, is_active=True)
                    db.session.add(category)
            
            # Create sample services
            services = [
                {'name': 'Swedish Massage', 'duration': 60, 'price': 75.00, 'category': 'massage'},
                {'name': 'Deep Tissue Massage', 'duration': 90, 'price': 95.00, 'category': 'massage'},
                {'name': 'Classic Facial', 'duration': 60, 'price': 65.00, 'category': 'facial'},
                {'name': 'Anti-Aging Facial', 'duration': 75, 'price': 85.00, 'category': 'facial'},
                {'name': 'Manicure', 'duration': 45, 'price': 35.00, 'category': 'nails'},
                {'name': 'Pedicure', 'duration': 60, 'price': 40.00, 'category': 'nails'}
            ]
            
            for service_data in services:
                existing = Service.query.filter_by(name=service_data['name']).first()
                if not existing:
                    service = Service(**service_data, is_active=True, created_at=datetime.utcnow())
                    db.session.add(service)
            
            # Create sample staff
            staff_members = [
                {'username': 'sarah_therapist', 'first_name': 'Sarah', 'last_name': 'Johnson', 'designation': 'Senior Therapist'},
                {'username': 'mike_masseur', 'first_name': 'Mike', 'last_name': 'Wilson', 'designation': 'Massage Therapist'},
                {'username': 'emily_esthetician', 'first_name': 'Emily', 'last_name': 'Davis', 'designation': 'Esthetician'},
                {'username': 'david_stylist', 'first_name': 'David', 'last_name': 'Brown', 'designation': 'Nail Technician'}
            ]
            
            for staff_data in staff_members:
                existing = User.query.filter_by(username=staff_data['username']).first()
                if not existing:
                    staff = User(
                        username=staff_data['username'],
                        first_name=staff_data['first_name'],
                        last_name=staff_data['last_name'],
                        email=f"{staff_data['username']}@spa.com",
                        designation=staff_data['designation'],
                        role='staff',
                        is_active=True,
                        password_hash=generate_password_hash('demo123'),
                        created_at=datetime.utcnow()
                    )
                    db.session.add(staff)
            
            # Create sample customers
            customers = [
                {'first_name': 'Emma', 'last_name': 'Wilson', 'phone': '+1-555-0201', 'email': 'emma.wilson@email.com'},
                {'first_name': 'Olivia', 'last_name': 'Brown', 'phone': '+1-555-0202', 'email': 'olivia.brown@email.com'},
                {'first_name': 'Sophia', 'last_name': 'Davis', 'phone': '+1-555-0203', 'email': 'sophia.davis@email.com'},
                {'first_name': 'Isabella', 'last_name': 'Miller', 'phone': '+1-555-0204', 'email': 'isabella.miller@email.com'}
            ]
            
            for customer_data in customers:
                existing = Customer.query.filter_by(phone=customer_data['phone']).first()
                if not existing:
                    customer = Customer(**customer_data, is_active=True, created_at=datetime.utcnow())
                    db.session.add(customer)
            
            db.session.commit()
            print("✅ Unaki demo data created successfully!")
            
            # Print summary
            print(f"Services: {Service.query.count()}")
            print(f"Staff: {User.query.filter_by(is_active=True).count()}")
            print(f"Customers: {Customer.query.count()}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating demo data: {e}")

if __name__ == '__main__':
    create_unaki_demo_data()
