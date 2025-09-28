
#!/usr/bin/env python3
"""
Setup SQLite database with demo data
"""
import os
from werkzeug.security import generate_password_hash
from datetime import datetime, date, time, timedelta

# Remove PostgreSQL environment variables
if 'DATABASE_URL' in os.environ:
    del os.environ['DATABASE_URL']

from app import app, db
from models import User, Customer, Service, Category

def setup_demo_data():
    """Create demo data in SQLite database"""
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            print("📋 Tables created")
            
            # Create admin user
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@spa.com',
                    first_name='System',
                    last_name='Administrator',
                    role='admin',
                    is_active=True,
                    password_hash=generate_password_hash('admin123')
                )
                db.session.add(admin_user)
                print("👤 Admin user created")
            
            # Create sample staff
            staff_members = [
                {'username': 'sarah_therapist', 'first_name': 'Sarah', 'last_name': 'Johnson', 'role': 'staff'},
                {'username': 'mike_massage', 'first_name': 'Mike', 'last_name': 'Wilson', 'role': 'staff'},
                {'username': 'emily_facial', 'first_name': 'Emily', 'last_name': 'Davis', 'role': 'manager'},
            ]
            
            for staff_data in staff_members:
                existing = User.query.filter_by(username=staff_data['username']).first()
                if not existing:
                    staff = User(
                        username=staff_data['username'],
                        email=f"{staff_data['first_name'].lower()}@spa.com",
                        first_name=staff_data['first_name'],
                        last_name=staff_data['last_name'],
                        role=staff_data['role'],
                        is_active=True,
                        password_hash=generate_password_hash('password123')
                    )
                    db.session.add(staff)
            
            print("👥 Staff members created")
            
            # Create sample categories
            categories = [
                {'name': 'facial', 'display_name': 'Facial Services', 'category_type': 'service'},
                {'name': 'massage', 'display_name': 'Massage Services', 'category_type': 'service'},
                {'name': 'beauty', 'display_name': 'Beauty Services', 'category_type': 'service'},
            ]
            
            for cat_data in categories:
                existing = Category.query.filter_by(name=cat_data['name']).first()
                if not existing:
                    category = Category(**cat_data)
                    db.session.add(category)
            
            print("📁 Categories created")
            
            # Create sample services
            services = [
                {'name': 'Classic Facial', 'price': 65.0, 'duration': 60, 'category': 'facial'},
                {'name': 'Deep Tissue Massage', 'price': 95.0, 'duration': 90, 'category': 'massage'},
                {'name': 'Manicure & Pedicure', 'price': 45.0, 'duration': 60, 'category': 'beauty'},
                {'name': 'Hair Styling', 'price': 75.0, 'duration': 90, 'category': 'beauty'},
                {'name': 'Anti-Aging Facial', 'price': 85.0, 'duration': 75, 'category': 'facial'},
            ]
            
            for service_data in services:
                existing = Service.query.filter_by(name=service_data['name']).first()
                if not existing:
                    service = Service(**service_data, is_active=True)
                    db.session.add(service)
            
            print("💅 Services created")
            
            # Create sample customers
            customers = [
                {'name': 'Emma Watson', 'phone': '+1-555-1001'},
                {'name': 'Olivia Smith', 'phone': '+1-555-1002'},
                {'name': 'Sophia Johnson', 'phone': '+1-555-1003'},
                {'name': 'Isabella Brown', 'phone': '+1-555-1004'},
                {'name': 'Karan Gupta', 'phone': '+91-9876543217'},
            ]
            
            for customer_data in customers:
                existing = Customer.query.filter_by(phone=customer_data['phone']).first()
                if not existing:
                    customer = Customer(**customer_data, is_active=True)
                    db.session.add(customer)
            
            print("👥 Customers created")
            
            db.session.commit()
            print("✅ SQLite demo database setup complete!")
            print("Login credentials: admin / admin123")
            print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
        except Exception as e:
            print(f"❌ Error setting up demo data: {e}")
            db.session.rollback()

if __name__ == "__main__":
    setup_demo_data()
