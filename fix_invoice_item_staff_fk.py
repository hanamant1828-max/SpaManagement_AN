
#!/usr/bin/env python3
"""
Fix InvoiceItem staff_id foreign key constraint
"""
from app import app, db
from sqlalchemy import text, inspect

def fix_staff_fk():
    """Remove foreign key constraint from invoice_item.staff_id"""
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            
            # Check if invoice_item table exists
            if 'invoice_item' not in inspector.get_table_names():
                print("❌ invoice_item table doesn't exist")
                return False
            
            print("🔧 Fixing staff_id foreign key constraint...")
            
            # For SQLite, we need to recreate the table without the FK constraint
            # First, create a temporary table with the correct schema
            db.session.execute(text("""
                CREATE TABLE invoice_item_new (
                    id INTEGER PRIMARY KEY,
                    invoice_id INTEGER NOT NULL,
                    item_type VARCHAR(20) NOT NULL,
                    item_id INTEGER NOT NULL,
                    appointment_id INTEGER,
                    product_id INTEGER,
                    batch_id INTEGER,
                    item_name VARCHAR(200) NOT NULL,
                    description TEXT,
                    batch_name VARCHAR(100),
                    quantity REAL DEFAULT 1.0,
                    unit_price REAL NOT NULL,
                    original_amount REAL NOT NULL,
                    deduction_amount REAL DEFAULT 0.0,
                    final_amount REAL NOT NULL,
                    is_package_deduction BOOLEAN DEFAULT 0,
                    is_subscription_deduction BOOLEAN DEFAULT 0,
                    is_extra_charge BOOLEAN DEFAULT 0,
                    staff_id INTEGER,
                    staff_name VARCHAR(200),
                    FOREIGN KEY (invoice_id) REFERENCES enhanced_invoice(id) ON DELETE CASCADE
                )
            """))
            
            # Copy data from old table
            db.session.execute(text("""
                INSERT INTO invoice_item_new 
                SELECT * FROM invoice_item
            """))
            
            # Drop old table
            db.session.execute(text("DROP TABLE invoice_item"))
            
            # Rename new table
            db.session.execute(text("ALTER TABLE invoice_item_new RENAME TO invoice_item"))
            
            db.session.commit()
            print("✅ Foreign key constraint fixed successfully!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error fixing foreign key: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("🔧 Fixing InvoiceItem staff_id foreign key constraint...")
    success = fix_staff_fk()
    if success:
        print("✅ Fix completed successfully!")
    else:
        print("❌ Fix failed!")
