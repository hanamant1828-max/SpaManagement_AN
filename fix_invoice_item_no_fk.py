
#!/usr/bin/env python3
"""
Fix invoice_item table to remove foreign key constraint on staff_id
"""
from app import app, db
from sqlalchemy import text, inspect

def fix_invoice_item_staff_fk():
    """Remove foreign key constraint from invoice_item.staff_id"""
    
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            
            print("🔧 Fixing invoice_item table - removing staff_id FK constraint...")
            
            # Check if table exists
            if 'invoice_item' not in inspector.get_table_names():
                print("❌ invoice_item table doesn't exist")
                return False
            
            # Backup existing data
            print("📦 Backing up invoice_item data...")
            backup_data = db.session.execute(text("SELECT * FROM invoice_item")).fetchall()
            print(f"   Backed up {len(backup_data)} rows")
            
            # Drop the table
            print("🗑️  Dropping invoice_item table...")
            db.session.execute(text("DROP TABLE IF EXISTS invoice_item"))
            
            # Recreate table WITHOUT foreign key on staff_id
            print("🔨 Creating new invoice_item table without staff_id FK...")
            db.session.execute(text("""
                CREATE TABLE invoice_item (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    FOREIGN KEY (invoice_id) REFERENCES enhanced_invoice(id) ON DELETE CASCADE,
                    FOREIGN KEY (appointment_id) REFERENCES appointment(id) ON DELETE SET NULL,
                    FOREIGN KEY (product_id) REFERENCES inventory_products(id) ON DELETE SET NULL,
                    FOREIGN KEY (batch_id) REFERENCES inventory_batches(id) ON DELETE SET NULL
                )
            """))
            
            # Restore data
            if backup_data:
                print(f"♻️  Restoring {len(backup_data)} rows...")
                for row in backup_data:
                    placeholders = ', '.join(['?' for _ in row])
                    db.session.execute(
                        text(f"INSERT INTO invoice_item VALUES ({placeholders})"),
                        list(row)
                    )
            
            db.session.commit()
            print("✅ invoice_item table fixed successfully - staff_id is now a plain integer column!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("🔧 Fixing invoice_item table FK constraints...")
    success = fix_invoice_item_staff_fk()
    if success:
        print("✅ Fix completed successfully!")
    else:
        print("❌ Fix failed!")
