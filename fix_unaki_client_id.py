
#!/usr/bin/env python3
"""
Fix missing client_id column in UnakiBooking table
"""

from app import app, db
from sqlalchemy import text, inspect

def fix_unaki_client_id():
    """Add client_id column to UnakiBooking table if missing"""
    
    with app.app_context():
        try:
            # Check if column already exists
            inspector = inspect(db.engine)
            columns = inspector.get_columns('unaki_booking')
            column_names = [col['name'] for col in columns]
            
            print(f"🔍 Current columns in unaki_booking: {column_names}")
            
            if 'client_id' in column_names:
                print("✅ client_id column already exists in unaki_booking table")
                return True
            
            print("📝 Adding client_id column to unaki_booking table...")
            
            # Add the client_id column
            db.session.execute(text("""
                ALTER TABLE unaki_booking 
                ADD COLUMN client_id INTEGER REFERENCES client(id)
            """))
            
            db.session.commit()
            print("✅ client_id column added successfully")
            
            # Verify the column was added
            inspector = inspect(db.engine)
            columns = inspector.get_columns('unaki_booking')
            column_names = [col['name'] for col in columns]
            
            if 'client_id' in column_names:
                print("✅ Verification successful: client_id column exists")
                return True
            else:
                print("❌ Verification failed: client_id column not found after addition")
                return False
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error fixing client_id column: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = fix_unaki_client_id()
    if success:
        print("\n🎉 UnakiBooking client_id fix completed successfully!")
        print("💡 The Unaki booking system should now work properly.")
    else:
        print("\n💥 Fix failed! Please check the error above.")
