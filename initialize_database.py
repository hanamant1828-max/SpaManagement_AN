
#!/usr/bin/env python3
"""
Initialize the database and create admin user
"""
import os
from werkzeug.security import generate_password_hash

# Set environment variables
if not os.environ.get("SESSION_SECRET"):
    os.environ["SESSION_SECRET"] = "1578063aca108928c78100b516702a5765d2d05e85b4fb8bb29a75db0bfc34ca"

if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///instance/spa_management.db"

from app import app, db

def initialize_database():
    """Initialize database with all tables and create admin user"""
    with app.app_context():
        try:
            print("🔧 Creating database tables...")
            
            # Drop all tables first to ensure clean slate
            db.drop_all()
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Import models after tables are created
            from models import User
            
            # Create admin user
            admin_user = User(
                username='admin',
                email='admin@spa.com',
                first_name='Admin',
                last_name='User',
                role='admin',
                is_active=True,
                password_hash=generate_password_hash('admin123')
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Admin user created successfully")
            print("   Username: admin")
            print("   Password: admin123")
            
            # Verify the user was created
            test_user = User.query.filter_by(username='admin').first()
            if test_user and test_user.check_password('admin123'):
                print("✅ Password verification successful")
            else:
                print("❌ Password verification failed")
                
            return True
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Initializing Spa Management Database...")
    if initialize_database():
        print("🎉 Database initialization complete!")
        print("🔑 You can now login with: admin / admin123")
    else:
        print("💥 Database initialization failed!")
