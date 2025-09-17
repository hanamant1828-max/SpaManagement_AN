#!/usr/bin/env python3
"""
Fix admin user login credentials
"""

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def fix_admin_user():
    """Fix admin user login issues and database constraints"""
    with app.app_context():
        try:
            # Get admin user
            admin_user = User.query.filter_by(username='admin').first()

            if admin_user:
                print(f"Found admin user: {admin_user.username}")
                print(f"Current active status: {admin_user.is_active}")
                print(f"Current email: {admin_user.email}")

                # Fix admin user
                admin_user.is_active = True
                admin_user.password_hash = generate_password_hash('admin123')

                # Ensure email is not None
                if not admin_user.email:
                    admin_user.email = 'admin@spa.com'

                db.session.commit()
                print("✅ Admin user fixed successfully")
                print(f"New active status: {admin_user.is_active}")
                print(f"New email: {admin_user.email}")

                # Also fix any other users with null emails
                users_with_null_email = User.query.filter(User.email == None).all()
                if users_with_null_email:
                    print(f"Found {len(users_with_null_email)} users with null emails")
                    for user in users_with_null_email:
                        if not user.email:
                            user.email = f"{user.username}@spa.com"
                            print(f"Fixed email for user: {user.username}")

                    db.session.commit()
                    print("✅ All null emails fixed")

            else:
                print("❌ Admin user not found")

        except Exception as e:
            print(f"❌ Error fixing admin user: {e}")
            db.session.rollback()

if __name__ == '__main__':
    fix_admin_user()