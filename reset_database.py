
#!/usr/bin/env python3

import os
import sys
from app import app, db
from werkzeug.security import generate_password_hash

def create_default_data():
    """Create default data without importing routes"""
    from models import User, Role, Department
    
    # Create default roles
    roles_data = [
        {'name': 'admin', 'display_name': 'Administrator'},
        {'name': 'manager', 'display_name': 'Manager'},
        {'name': 'staff', 'display_name': 'Staff'},
        {'name': 'receptionist', 'display_name': 'Receptionist'}
    ]
    
    for role_data in roles_data:
        if not Role.query.filter_by(name=role_data['name']).first():
            role = Role(**role_data, is_active=True)
            db.session.add(role)
    
    db.session.commit()
    
    # Create default departments
    departments_data = [
        {'name': 'management', 'display_name': 'Management'},
        {'name': 'reception', 'display_name': 'Reception'},
        {'name': 'spa_therapy', 'display_name': 'Spa & Therapy'},
        {'name': 'beauty', 'display_name': 'Beauty Services'}
    ]
    
    for dept_data in departments_data:
        if not Department.query.filter_by(name=dept_data['name']).first():
            dept = Department(**dept_data, is_active=True)
            db.session.add(dept)
    
    db.session.commit()
    
    # Create default admin user
    if not User.query.filter_by(username='admin').first():
        admin_role = Role.query.filter_by(name='admin').first()
        admin = User(
            username='admin',
            email='admin@spa.com',
            first_name='Admin',
            last_name='User',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            role_id=admin_role.id if admin_role else None,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin user created (username: admin, password: admin123)")

def reset_database():
    """Reset the SQLite database to a fresh state"""
    
    with app.app_context():
        try:
            # Get the database path
            database_path = os.path.join(os.path.dirname(__file__), 'instance', 'spa_management.db')
            
            print(f"Current database location: {database_path}")
            
            # Check if database exists
            if os.path.exists(database_path):
                print("Found existing database. Backing it up...")
                backup_path = database_path + ".backup"
                os.rename(database_path, backup_path)
                print(f"Backup created at: {backup_path}")
            
            # Create fresh database
            print("Creating fresh SQLite database...")
            db.create_all()
            print("✅ Fresh database created successfully!")
            
            # Create default data
            print("Creating default admin user and basic data...")
            create_default_data()
            print("✅ Default data created successfully!")
            
            print(f"\n🎉 Database reset complete!")
            print(f"Database location: {database_path}")
            print("You can now restart your application.")
            
        except Exception as e:
            print(f"❌ Error resetting database: {e}")
            sys.exit(1)

if __name__ == "__main__":
    print("🔄 Resetting SQLite database...")
    reset_database()
