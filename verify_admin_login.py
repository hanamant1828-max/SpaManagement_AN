
#!/usr/bin/env python3
"""
Verify and reset admin login credentials
"""
import os
os.environ["SESSION_SECRET"] = "1578063aca108928c78100b516702a5765d2d05e85b4fb8bb29a75db0bfc34ca"

from app import app, db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

def verify_admin():
    """Verify admin user exists and credentials work"""
    with app.app_context():
        # Find admin user (case-insensitive)
        admin = User.query.filter(func.lower(User.username) == 'admin').first()
        
        if not admin:
            print("❌ Admin user not found!")
            print("Creating new admin user...")
            admin = User(
                username='admin',
                email='admin@spa.com',
                first_name='Admin',
                last_name='User',
                role='admin',
                is_active=True
            )
            admin.password_hash = generate_password_hash('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created successfully")
        else:
            print(f"✅ Admin user found: {admin.username}")
            print(f"   Email: {admin.email}")
            print(f"   Active: {admin.is_active}")
            print(f"   Role: {admin.role}")
            
            # Test password
            test_password = 'admin123'
            if check_password_hash(admin.password_hash, test_password):
                print(f"✅ Password verification successful for '{test_password}'")
            else:
                print(f"❌ Password verification FAILED!")
                print("Resetting password to 'admin123'...")
                admin.password_hash = generate_password_hash('admin123')
                admin.is_active = True
                admin.role = 'admin'
                db.session.commit()
                print("✅ Password reset successfully")
        
        print("\n" + "="*50)
        print("Login Credentials:")
        print("Username: admin")
        print("Password: admin123")
        print("="*50)

if __name__ == '__main__':
    verify_admin()
