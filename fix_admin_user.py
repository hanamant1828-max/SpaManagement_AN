
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def fix_admin_user():
    with app.app_context():
        # Find admin user
        admin_user = User.query.filter_by(username='admin').first()
        
        if not admin_user:
            print("Creating admin user...")
            admin_user = User(
                username='admin',
                email='admin@spa.com',
                first_name='System',
                last_name='Administrator',
                role='admin',
                is_active=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
        else:
            print("Updating admin user password...")
            # Set password using both methods for compatibility
            admin_user.password_hash = generate_password_hash('admin123')
            admin_user.password = 'admin123'  # Fallback for demo
            admin_user.is_active = True
        
        try:
            db.session.commit()
            print("Admin user password fixed successfully!")
            print("Username: admin")
            print("Password: admin123")
        except Exception as e:
            print(f"Error fixing admin user: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_admin_user()
