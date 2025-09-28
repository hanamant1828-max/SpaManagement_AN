
#!/usr/bin/env python3
"""
Fix missing client.name column in SQLite database
"""

from app import app, db
from sqlalchemy import text, inspect
from models import Client

def fix_client_name_column():
    """Add name column to client table and migrate data"""
    
    with app.app_context():
        try:
            # Check if name column exists
            inspector = inspect(db.engine)
            columns = inspector.get_columns('client')
            column_names = [col['name'] for col in columns]
            
            print(f"🔍 Current columns in client table: {column_names}")
            
            if 'name' in column_names:
                print("✅ name column already exists in client table")
                return True
            
            print("📝 Adding name column to client table...")
            
            # Add the name column
            db.session.execute(text("""
                ALTER TABLE client 
                ADD COLUMN name VARCHAR(100) NOT NULL DEFAULT ''
            """))
            
            print("✅ name column added successfully")
            
            # Now populate name column from existing first_name and last_name if they exist
            print("🔄 Migrating existing client data...")
            
            # Check if first_name and last_name columns exist
            if 'first_name' in column_names and 'last_name' in column_names:
                # Migrate data from first_name + last_name to name
                db.session.execute(text("""
                    UPDATE client 
                    SET name = TRIM(COALESCE(first_name, '') || ' ' || COALESCE(last_name, ''))
                    WHERE name = '' OR name IS NULL
                """))
                print("✅ Migrated existing first_name + last_name to name column")
            else:
                # If no first_name/last_name, set placeholder names
                db.session.execute(text("""
                    UPDATE client 
                    SET name = 'Client ' || id
                    WHERE name = '' OR name IS NULL
                """))
                print("✅ Set placeholder names for existing clients")
            
            db.session.commit()
            
            # Verify the column was added and populated
            result = db.session.execute(text("SELECT COUNT(*) FROM client WHERE name IS NOT NULL AND name != ''"))
            client_count = result.fetchone()[0]
            
            print(f"✅ Verification successful: {client_count} clients have names")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error fixing client name column: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = fix_client_name_column()
    if success:
        print("\n🎉 Client name column fix completed successfully!")
    else:
        print("\n💥 Fix failed - please check errors above")
