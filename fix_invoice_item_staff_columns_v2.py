
#!/usr/bin/env python3
"""
Add staff_id and staff_name columns to invoice_item table
"""
from app import app, db
from sqlalchemy import text, inspect

def add_staff_columns():
    """Add staff_id and staff_name columns to invoice_item table"""
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            
            # Check if invoice_item table exists
            if 'invoice_item' not in inspector.get_table_names():
                print("❌ invoice_item table doesn't exist. Creating all tables...")
                db.create_all()
                print("✅ All tables created successfully!")
                return True
            
            # Get existing columns
            existing_columns = [col['name'] for col in inspector.get_columns('invoice_item')]
            print(f"📊 Current columns: {', '.join(existing_columns)}")
            
            # Add staff_id if missing
            if 'staff_id' not in existing_columns:
                print("🔧 Adding staff_id column...")
                db.session.execute(text("""
                    ALTER TABLE invoice_item 
                    ADD COLUMN staff_id INTEGER
                """))
                print("✅ staff_id column added")
            else:
                print("ℹ️  staff_id column already exists")
            
            # Add staff_name if missing
            if 'staff_name' not in existing_columns:
                print("🔧 Adding staff_name column...")
                db.session.execute(text("""
                    ALTER TABLE invoice_item 
                    ADD COLUMN staff_name VARCHAR(200)
                """))
                print("✅ staff_name column added")
            else:
                print("ℹ️  staff_name column already exists")
            
            db.session.commit()
            print("\n✅ Database schema updated successfully!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating database schema: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("🔧 Adding staff columns to invoice_item table...")
    success = add_staff_columns()
    if success:
        print("✅ Fix completed successfully!")
    else:
        print("❌ Fix failed!")
