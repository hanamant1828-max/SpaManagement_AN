
#!/usr/bin/env python3
"""
Fix admin user login credentials
"""

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def fix_admin_user():
    with app.app_context():
        try:
            # Get admin user
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                # Create new admin user
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
                print("✅ Created new admin user")
            else:
                # Update existing admin user
                admin_user.password_hash = generate_password_hash('admin123')
                admin_user.is_active = True
                admin_user.role = 'admin'
                print("✅ Updated existing admin user")
            
            db.session.commit()
            print("✅ Admin user credentials fixed!")
            print("Username: admin")
            print("Password: admin123")
            
            # Verify the fix
            if admin_user.check_password('admin123'):
                print("✅ Password verification successful!")
            else:
                print("❌ Password verification failed!")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error fixing admin user: {e}")

if __name__ == '__main__':
    fix_admin_user()
