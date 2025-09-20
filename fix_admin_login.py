
#!/usr/bin/env python3
"""
Fix admin user login credentials with comprehensive debugging
"""

from app import app, db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

def fix_admin_user():
    """Fix admin user login issues and database constraints"""
    with app.app_context():
        try:
            # First, let's check all users
            all_users = User.query.all()
            print(f"Total users in database: {len(all_users)}")
            
            for user in all_users:
                print(f"User: {user.username}, Email: {user.email}, Active: {user.is_active}")
            
            # Get admin user
            admin_user = User.query.filter_by(username='admin').first()

            if admin_user:
                print(f"\n✅ Found admin user: {admin_user.username}")
                print(f"Current active status: {admin_user.is_active}")
                print(f"Current email: {admin_user.email}")
                print(f"Has password hash: {bool(admin_user.password_hash)}")

                # Test current password
                if admin_user.password_hash:
                    test_result = check_password_hash(admin_user.password_hash, 'admin123')
                    print(f"Password 'admin123' test: {test_result}")

                # Update admin user with new password
                admin_user.is_active = True
                admin_user.password_hash = generate_password_hash('admin123')
                admin_user.role = 'admin'  # Ensure admin role

                # Ensure email is not None
                if not admin_user.email:
                    admin_user.email = 'admin@spa.com'

                db.session.commit()
                print("✅ Admin user updated successfully")
                
                # Test new password
                new_test_result = check_password_hash(admin_user.password_hash, 'admin123')
                print(f"New password test: {new_test_result}")

            else:
                print("❌ Admin user not found, creating new one...")
                # Create new admin user
                admin_user = User(
                    username='admin',
                    email='admin@spa.com',
                    first_name='Admin',
                    last_name='User',
                    role='admin',
                    is_active=True
                )
                admin_user.set_password('admin123')
                
                db.session.add(admin_user)
                db.session.commit()
                print("✅ New admin user created successfully")

            # Also create a test user for debugging
            test_user = User.query.filter_by(username='test').first()
            if not test_user:
                test_user = User(
                    username='test',
                    email='test@spa.com',
                    first_name='Test',
                    last_name='User',
                    role='staff',
                    is_active=True
                )
                test_user.set_password('test123')
                db.session.add(test_user)
                db.session.commit()
                print("✅ Test user created: test/test123")

            # Fix any other users with null emails
            users_with_null_email = User.query.filter(User.email == None).all()
            if users_with_null_email:
                print(f"Found {len(users_with_null_email)} users with null emails")
                for user in users_with_null_email:
                    if not user.email:
                        user.email = f"{user.username}@spa.com"
                        print(f"Fixed email for user: {user.username}")

                db.session.commit()
                print("✅ All null emails fixed")

            print("\n🔧 Final user verification:")
            final_admin = User.query.filter_by(username='admin').first()
            if final_admin:
                print(f"Admin username: {final_admin.username}")
                print(f"Admin email: {final_admin.email}")
                print(f"Admin active: {final_admin.is_active}")
                print(f"Admin role: {final_admin.role}")
                print(f"Password test with 'admin123': {final_admin.check_password('admin123')}")

        except Exception as e:
            print(f"❌ Error fixing admin user: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == '__main__':
    fix_admin_user()
