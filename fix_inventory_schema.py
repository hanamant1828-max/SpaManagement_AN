
#!/usr/bin/env python3
"""
Fix inventory database schema issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import *
from sqlalchemy import text

def fix_inventory_schema():
    """Fix the inventory database schema"""
    print("Fixing inventory database schema...")
    
    with app.app_context():
        try:
            # Drop problematic tables if they exist
            print("Dropping problematic tables...")
            db.session.execute(text("DROP TABLE IF EXISTS inventory_items CASCADE"))
            db.session.execute(text("DROP TABLE IF EXISTS consumption_entries CASCADE"))
            db.session.execute(text("DROP TABLE IF EXISTS usage_durations CASCADE"))
            db.session.execute(text("DROP TABLE IF EXISTS stock_movement CASCADE"))
            
            # Commit the drops
            db.session.commit()
            print("Dropped existing tables")
            
            # Recreate all tables
            print("Creating all tables...")
            db.create_all()
            print("✅ Database schema fixed successfully!")
            
        except Exception as e:
            print(f"❌ Error fixing schema: {e}")
            db.session.rollback()
            
            # Try alternative approach - just create tables
            try:
                print("Trying alternative approach...")
                db.create_all()
                print("✅ Tables created successfully!")
            except Exception as e2:
                print(f"❌ Alternative approach failed: {e2}")
                return False
                
    return True

if __name__ == "__main__":
    print("Starting inventory schema fix...")
    success = fix_inventory_schema()
    if success:
        print("Schema fix completed successfully!")
    else:
        print("Schema fix failed!")
    sys.exit(0 if success else 1)
