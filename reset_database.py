
#!/usr/bin/env python3

import os
import sys
from app import app, db

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
            from routes import create_default_data
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
