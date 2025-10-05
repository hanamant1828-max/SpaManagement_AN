
"""
Add staff_id and staff_name columns to invoice_item table
"""
from app import app, db
from sqlalchemy import text

def add_staff_columns_to_invoice_item():
    """Add staff_id and staff_name columns to invoice_item table"""
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('invoice_item')]
            
            if 'staff_id' not in columns:
                print("Adding staff_id column to invoice_item table...")
                db.session.execute(text("""
                    ALTER TABLE invoice_item 
                    ADD COLUMN staff_id INTEGER REFERENCES users(id) ON DELETE SET NULL
                """))
                print("✅ staff_id column added")
            else:
                print("ℹ️ staff_id column already exists")
            
            if 'staff_name' not in columns:
                print("Adding staff_name column to invoice_item table...")
                db.session.execute(text("""
                    ALTER TABLE invoice_item 
                    ADD COLUMN staff_name VARCHAR(200)
                """))
                print("✅ staff_name column added")
            else:
                print("ℹ️ staff_name column already exists")
            
            db.session.commit()
            print("\n✅ Database schema updated successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating database schema: {str(e)}")
            raise

if __name__ == '__main__':
    add_staff_columns_to_invoice_item()
