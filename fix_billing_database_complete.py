
#!/usr/bin/env python3

import sys
from app import app, db
from sqlalchemy import text, inspect
from models import EnhancedInvoice, InvoiceItem, InvoicePayment

def fix_billing_database():
    """Complete fix for billing database schema"""
    
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            
            print("🔧 Checking and fixing billing database schema...")
            
            # Check if enhanced_invoice table exists
            if 'enhanced_invoice' not in inspector.get_table_names():
                print("📋 Creating enhanced_invoice table...")
                db.create_all()
                print("✅ All tables created successfully!")
                return True
            
            # Get existing columns
            existing_columns = [col['name'] for col in inspector.get_columns('enhanced_invoice')]
            print(f"📊 Existing columns: {len(existing_columns)} columns found")
            
            # Required columns with their definitions
            required_columns = {
                'cgst_rate': 'REAL DEFAULT 0.0',
                'sgst_rate': 'REAL DEFAULT 0.0', 
                'igst_rate': 'REAL DEFAULT 0.0',
                'cgst_amount': 'REAL DEFAULT 0.0',
                'sgst_amount': 'REAL DEFAULT 0.0',
                'igst_amount': 'REAL DEFAULT 0.0',
                'is_interstate': 'BOOLEAN DEFAULT FALSE',
                'additional_charges': 'REAL DEFAULT 0.0',
                'discount_type': 'VARCHAR(20) DEFAULT \'amount\'',
                'discount_rate': 'REAL DEFAULT 0.0',
                'payment_terms': 'VARCHAR(50) DEFAULT \'immediate\'',
                'due_date': 'TIMESTAMP',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            }
            
            # Add missing columns
            columns_added = 0
            for column_name, column_def in required_columns.items():
                if column_name not in existing_columns:
                    try:
                        print(f"➕ Adding column: {column_name}")
                        db.session.execute(text(f"""
                            ALTER TABLE enhanced_invoice 
                            ADD COLUMN {column_name} {column_def}
                        """))
                        db.session.commit()
                        print(f"✅ Added {column_name}")
                        columns_added += 1
                    except Exception as e:
                        print(f"⚠️ Error adding {column_name}: {e}")
                        db.session.rollback()
                        continue
                else:
                    print(f"✓ Column {column_name} already exists")
            
            # Fix email constraint in user table
            print("\n🔧 Fixing user table email constraint...")
            try:
                db.session.execute(text("""
                    ALTER TABLE "user" ALTER COLUMN email DROP NOT NULL
                """))
                db.session.commit()
                print("✅ Email constraint fixed - now nullable")
            except Exception as e:
                print(f"ℹ️ Email constraint already fixed or doesn't need fixing: {e}")
                db.session.rollback()
            
            # Verify invoice_item and invoice_payment tables
            for table_name in ['invoice_item', 'invoice_payment']:
                if table_name not in inspector.get_table_names():
                    print(f"📋 Creating {table_name} table...")
                    db.create_all()
                    break
            
            print(f"\n🎉 Database schema fix completed!")
            print(f"📊 Summary: Added {columns_added} new columns")
            print("💡 The billing system should now work properly.")
            
            return True
            
        except Exception as e:
            print(f"❌ Critical error during database fix: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = fix_billing_database()
    sys.exit(0 if success else 1)
