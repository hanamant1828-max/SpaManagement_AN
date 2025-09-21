
#!/usr/bin/env python3

from app import app, db
from sqlalchemy import text
import sys

def add_missing_columns():
    """Add missing GST and professional billing columns to enhanced_invoice table"""
    
    with app.app_context():
        try:
            # List of columns to add with PostgreSQL-compatible syntax
            columns_to_add = [
                ('cgst_rate', 'REAL DEFAULT 0.0'),
                ('sgst_rate', 'REAL DEFAULT 0.0'),
                ('igst_rate', 'REAL DEFAULT 0.0'),
                ('cgst_amount', 'REAL DEFAULT 0.0'),
                ('sgst_amount', 'REAL DEFAULT 0.0'),
                ('igst_amount', 'REAL DEFAULT 0.0'),
                ('is_interstate', 'BOOLEAN DEFAULT FALSE'),
                ('additional_charges', 'REAL DEFAULT 0.0'),
                ('discount_type', 'VARCHAR(20) DEFAULT \'amount\''),
                ('discount_rate', 'REAL DEFAULT 0.0'),
                ('payment_terms', 'VARCHAR(50) DEFAULT \'immediate\'')
            ]
            
            # Check if table exists
            result = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'enhanced_invoice'
                );
            """)).fetchone()
            
            if not result[0]:
                print("enhanced_invoice table doesn't exist. Creating all tables...")
                db.create_all()
                print("All tables created successfully!")
                return
            
            # Check which columns already exist
            existing_columns = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = 'enhanced_invoice'
            """)).fetchall()
            
            existing_column_names = [col[0] for col in existing_columns]
            print(f"Existing columns: {existing_column_names}")
            
            # Add missing columns one by one with proper error handling
            columns_added = 0
            for column_name, column_def in columns_to_add:
                if column_name not in existing_column_names:
                    try:
                        print(f"Adding column: {column_name}")
                        db.session.execute(text(f"""
                            ALTER TABLE enhanced_invoice 
                            ADD COLUMN {column_name} {column_def}
                        """))
                        db.session.commit()
                        print(f"✓ Added {column_name}")
                        columns_added += 1
                    except Exception as col_error:
                        print(f"⚠️ Error adding {column_name}: {col_error}")
                        db.session.rollback()
                        # Continue with other columns
                        continue
                else:
                    print(f"✓ Column {column_name} already exists")
            
            print(f"\n✅ Database schema update completed!")
            print(f"Added {columns_added} new columns to enhanced_invoice table.")
            print("The billing system should now work properly.")
            
        except Exception as e:
            print(f"❌ Error updating database schema: {e}")
            db.session.rollback()
            
            # Try creating all tables if schema update fails
            try:
                print("Attempting to create all missing tables...")
                db.create_all()
                print("✅ All tables created successfully!")
            except Exception as create_error:
                print(f"❌ Error creating tables: {create_error}")
                sys.exit(1)

if __name__ == "__main__":
    add_missing_columns()
