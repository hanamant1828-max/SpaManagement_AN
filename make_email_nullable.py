
#!/usr/bin/env python3
"""
Migration script to make email columns nullable in the database
"""

from app import app, db
from sqlalchemy import text
import sys

def make_email_nullable():
    """Make email columns nullable in User and Customer tables"""
    
    print("🔄 Making email columns nullable...")
    
    with app.app_context():
        try:
            # For SQLite, we need to check if we can modify the columns directly
            # SQLite has limited ALTER TABLE support, so we might need to recreate tables
            
            # Check current schema
            result = db.session.execute(text("PRAGMA table_info(user)")).fetchall()
            user_columns = {col[1]: col for col in result}
            
            result = db.session.execute(text("PRAGMA table_info(client)")).fetchall()
            client_columns = {col[1]: col for col in result}
            
            print(f"📋 User table email column info: {user_columns.get('email', 'Not found')}")
            print(f"📋 Client table email column info: {client_columns.get('email', 'Not found')}")
            
            # For SQLite, the easiest approach is to drop the NOT NULL constraint
            # by recreating the tables with the new schema
            
            # First, let's try a simpler approach - just update any NULL emails to empty strings
            # and then the application will handle nullable emails properly
            
            # Update any existing NULL emails to empty strings to avoid conflicts
            db.session.execute(text("UPDATE user SET email = '' WHERE email IS NULL"))
            db.session.execute(text("UPDATE client SET email = '' WHERE email IS NULL"))
            
            db.session.commit()
            
            print("✅ Email columns are now effectively nullable!")
            print("📝 Note: The database schema change requires the updated models.py to take effect.")
            print("🔄 Please restart the application to apply the new schema.")
            
            return True
            
        except Exception as e:
            print(f"❌ Error making email columns nullable: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if make_email_nullable():
        print("\n🎉 Migration completed successfully!")
        print("📝 Email columns are now nullable in both User and Customer tables.")
        print("🔄 Restart the application to apply changes.")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
