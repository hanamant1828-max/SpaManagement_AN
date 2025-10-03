
#!/usr/bin/env python3
"""
Fix InvoiceItem table schema by adding missing batch_name column
"""

from app import app, db
from sqlalchemy import text, inspect
import sys

def fix_invoice_item_schema():
    """Add missing batch_name column to invoice_item table"""
    
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
            print(f"📊 Existing columns in invoice_item: {existing_columns}")
            
            # Required columns with their definitions
            required_columns = {
                'product_id': 'INTEGER REFERENCES inventory_products(id)',
                'batch_id': 'INTEGER REFERENCES inventory_batches(id)',
                'batch_name': 'VARCHAR(100)',
                'staff_id': 'INTEGER REFERENCES user(id)',
                'staff_name': 'VARCHAR(100)'
            }
            
            columns_added = 0
            for column_name, column_def in required_columns.items():
                if column_name not in existing_columns:
                    try:
                        sql = f"ALTER TABLE invoice_item ADD COLUMN {column_name} {column_def};"
                        print(f"🔧 Adding column: {column_name}")
                        db.session.execute(text(sql))
                        db.session.commit()
                        columns_added += 1
                        print(f"✅ Added column: {column_name}")
                    except Exception as col_error:
                        print(f"⚠️  Could not add {column_name}: {col_error}")
                        db.session.rollback()
                        continue
                else:
                    print(f"✅ Column {column_name} already exists")
            
            print(f"\n🎯 Schema fix completed! Added {columns_added} columns.")
            
            # Verify the fix
            updated_columns = [col['name'] for col in inspector.get_columns('invoice_item')]
            print(f"📋 Updated columns: {updated_columns}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fixing invoice_item schema: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🔧 Fixing InvoiceItem table schema...")
    success = fix_invoice_item_schema()
    if success:
        print("✅ Schema fix completed successfully!")
        sys.exit(0)
    else:
        print("❌ Schema fix failed!")
        sys.exit(1)
