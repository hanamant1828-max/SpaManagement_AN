
#!/usr/bin/env python3

import os
from werkzeug.security import generate_password_hash

# Set environment variables
os.environ["SESSION_SECRET"] = "1578063aca108928c78100b516702a5765d2d05e85b4fb8bb29a75db0bfc34ca"
# Use SQLite database (comment out PostgreSQL)
# os.environ["DATABASE_URL"] = "postgresql://replit:postgres@localhost:5432/spa_management"

from app import app, db

def fix_login_issue():
    """Fix the login issue by ensuring admin user exists"""
    with app.app_context():
        try:
            # Import models
            from models import User
            
            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                print("Creating admin user...")
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
                print("✅ Admin user created")
            else:
                print("Admin user exists, updating password...")
                admin_user.password_hash = generate_password_hash('admin123')
                admin_user.is_active = True
                admin_user.role = 'admin'
                print("✅ Admin user updated")
            
            db.session.commit()
            print("✅ Database changes committed")
            
            # Verify the user can be found
            test_user = User.query.filter_by(username='admin').first()
            if test_user and test_user.is_active:
                print("✅ Admin user verification successful")
                print(f"   Username: {test_user.username}")
                print(f"   Email: {test_user.email}")
                print(f"   Active: {test_user.is_active}")
                print(f"   Has password hash: {bool(test_user.password_hash)}")
            else:
                print("❌ Admin user verification failed")
                
        except Exception as e:
            print(f"❌ Error fixing login issue: {e}")
            db.session.rollback()

if __name__ == "__main__":
    print("🔧 Fixing login issue...")
    fix_login_issue()
    print("🚀 Login fix complete. Try logging in with admin/admin123")
