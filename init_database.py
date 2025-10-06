
#!/usr/bin/env python3
"""
Database initialization script for fresh clones
Run this automatically on first startup or manually with: python init_database.py
"""

import os
import sys
from datetime import datetime, date
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize database with all tables and default data"""
    
    # Import app after setting required env vars
    if not os.environ.get("SESSION_SECRET"):
        os.environ["SESSION_SECRET"] = "1578063aca108928c78100b516702a5765d2d05e85b4fb8bb29a75db0bfc34ca"
    
    from app import app, db
    from models import User, Department, Role, Category, Service
    
    with app.app_context():
        try:
            print("🔄 Initializing database...")
            
            # Create all tables
            db.create_all()
            print("✅ All tables created successfully")
            
            # Check if admin user exists
            admin = User.query.filter_by(username='admin').first()
            
            if not admin:
                print("👤 Creating default admin user...")
                admin = User(
                    username='admin',
                    email='admin@spa.com',
                    first_name='System',
                    last_name='Administrator',
                    role='admin',
                    is_active=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created (username: admin, password: admin123)")
            else:
                print("ℹ️  Admin user already exists")
            
            # Create default categories if none exist
            if Category.query.count() == 0:
                print("📁 Creating default categories...")
                categories = [
                    Category(name='facial', display_name='Facial Services', category_type='service', color='#FF6B6B', icon='fas fa-spa'),
                    Category(name='massage', display_name='Massage Services', category_type='service', color='#4ECDC4', icon='fas fa-hands'),
                    Category(name='hair', display_name='Hair Services', category_type='service', color='#45B7D1', icon='fas fa-cut'),
                    Category(name='nails', display_name='Nail Services', category_type='service', color='#FFA07A', icon='fas fa-hand-sparkles'),
                    Category(name='beauty', display_name='Beauty Services', category_type='service', color='#DDA0DD', icon='fas fa-heart'),
                    Category(name='utilities', display_name='Utilities', category_type='expense', color='#6C757D', icon='fas fa-plug'),
                    Category(name='supplies', display_name='Supplies', category_type='expense', color='#28A745', icon='fas fa-box'),
                    Category(name='maintenance', display_name='Maintenance', category_type='expense', color='#FFC107', icon='fas fa-tools'),
                ]
                
                for cat in categories:
                    db.session.add(cat)
                
                db.session.commit()
                print(f"✅ Created {len(categories)} default categories")
            else:
                print("ℹ️  Categories already exist")
            
            # Create sample services if none exist
            if Service.query.count() == 0:
                print("💆 Creating sample services...")
                facial_cat = Category.query.filter_by(name='facial').first()
                massage_cat = Category.query.filter_by(name='massage').first()
                
                services = [
                    Service(name='Classic Facial', description='Relaxing facial treatment', duration=60, price=85.0, category='Facial Services', category_id=facial_cat.id if facial_cat else None),
                    Service(name='Deep Tissue Massage', description='Therapeutic deep tissue massage', duration=90, price=120.0, category='Massage Services', category_id=massage_cat.id if massage_cat else None),
                    Service(name='Swedish Massage', description='Relaxing Swedish massage', duration=60, price=100.0, category='Massage Services', category_id=massage_cat.id if massage_cat else None),
                ]
                
                for service in services:
                    db.session.add(service)
                
                db.session.commit()
                print(f"✅ Created {len(services)} sample services")
            else:
                print("ℹ️  Services already exist")
            
            print("\n✅ Database initialization complete!")
            print(f"📍 Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print("🔐 Login credentials: admin / admin123")
            print("\n🚀 You can now start your application")
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
