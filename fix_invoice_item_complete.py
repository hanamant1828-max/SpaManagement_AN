
#!/usr/bin/env python3
"""
Complete fix for InvoiceItem table schema - adds all missing columns
"""

from app import app, db
from sqlalchemy import text, inspect
import sys

def fix_invoice_item_complete():
    """Add all missing columns to invoice_item table"""
    
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
            print(f"📊 Current columns: {existing_columns}")
            
            # Required columns with SQLite-compatible definitions
            required_columns = {
                'staff_id': 'INTEGER',
                'staff_name': 'VARCHAR(100)',
                'product_id': 'INTEGER',
                'batch_id': 'INTEGER',
                'batch_name': 'VARCHAR(100)'
            }
            
            columns_added = 0
            for column_name, column_def in required_columns.items():
                if column_name not in existing_columns:
                    try:
                        sql = f"ALTER TABLE invoice_item ADD COLUMN {column_name} {column_def}"
                        print(f"🔧 Adding column: {column_name}")
                        db.session.execute(text(sql))
                        db.session.commit()
                        columns_added += 1
                        print(f"✅ Added column: {column_name}")
                    except Exception as col_error:
                        print(f"⚠️  Error adding {column_name}: {col_error}")
                        db.session.rollback()
                        continue
                else:
                    print(f"✓ Column {column_name} already exists")
            
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
    success = fix_invoice_item_complete()
    if success:
        print("✅ Schema fix completed successfully!")
        print("💡 Please restart the application for changes to take effect")
        sys.exit(0)
    else:
        print("❌ Schema fix failed!")
        sys.exit(1)
