
#!/usr/bin/env python3
"""
Setup admin user for SQLite database
"""
import os
from werkzeug.security import generate_password_hash

# Remove PostgreSQL environment variables for this session
if 'DATABASE_URL' in os.environ:
    del os.environ['DATABASE_URL']

from app import app, db
from models import User

def setup_admin():
    """Create admin user in SQLite database"""
    with app.app_context():
        try:
            # Create tables if they don't exist
            db.create_all()
            
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
            print("✅ SQLite database setup complete")
            print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print("Login credentials: admin / admin123")
            
        except Exception as e:
            print(f"❌ Error setting up SQLite database: {e}")
            db.session.rollback()

if __name__ == "__main__":
    setup_admin()
