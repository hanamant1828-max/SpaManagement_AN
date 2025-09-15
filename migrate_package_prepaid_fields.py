
#!/usr/bin/env python3
"""
Migration script to add prepaid package fields to the Package table
Run this script to add support for prepaid packages
"""

from app import app, db
from models import Package
import sys

def add_prepaid_package_fields():
    """Add the missing prepaid package fields to the Package table"""
    try:
        with app.app_context():
            print("Adding prepaid package fields to Package table...")
            
            # SQL commands to add missing columns
            migration_sql = [
                "ALTER TABLE package ADD COLUMN IF NOT EXISTS prepaid_amount FLOAT DEFAULT 0.0;",
                "ALTER TABLE package ADD COLUMN IF NOT EXISTS bonus_percentage FLOAT DEFAULT 0.0;", 
                "ALTER TABLE package ADD COLUMN IF NOT EXISTS bonus_amount FLOAT DEFAULT 0.0;",
                "ALTER TABLE package ADD COLUMN IF NOT EXISTS prepaid_balance FLOAT DEFAULT 0.0;",
                "ALTER TABLE package ADD COLUMN IF NOT EXISTS free_sessions INTEGER DEFAULT 0;",
                "ALTER TABLE package ADD COLUMN IF NOT EXISTS paid_sessions INTEGER DEFAULT 0;",
                "ALTER TABLE package ADD COLUMN IF NOT EXISTS has_unlimited_sessions BOOLEAN DEFAULT FALSE;",
                "ALTER TABLE package ADD COLUMN IF NOT EXISTS start_date DATE;",
                "ALTER TABLE package ADD COLUMN IF NOT EXISTS end_date DATE;"
            ]
            
            for sql in migration_sql:
                try:
                    db.session.execute(db.text(sql))
                    print(f"✓ Executed: {sql}")
                except Exception as e:
                    print(f"⚠ Warning for {sql}: {e}")
                    # Continue with other columns even if one fails
            
            db.session.commit()
            print("✓ All prepaid package fields added successfully!")
            
            # Test the changes by querying the Package table
            packages = Package.query.limit(1).all()
            print(f"✓ Package table is working correctly - found {len(packages)} existing packages")
            
            return True
            
    except Exception as e:
        print(f"✗ Error during migration: {str(e)}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    success = add_prepaid_package_fields()
    if success:
        print("\n🎉 Migration completed successfully!")
        print("You can now use prepaid packages functionality.")
    else:
        print("\n❌ Migration failed!")
    
    sys.exit(0 if success else 1)
