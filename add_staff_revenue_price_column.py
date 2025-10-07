
#!/usr/bin/env python3
"""
Migration script to add staff_revenue_price column to invoice_item table
This column stores the original service price for staff commission calculation
"""
from app import app, db
from models import InvoiceItem
from sqlalchemy import text

def add_staff_revenue_price_column():
    """Add staff_revenue_price column to invoice_item table"""
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("PRAGMA table_info(invoice_item)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'staff_revenue_price' in columns:
                print("✅ Column 'staff_revenue_price' already exists in invoice_item table")
                return
            
            # Add the new column
            db.session.execute(text("""
                ALTER TABLE invoice_item 
                ADD COLUMN staff_revenue_price FLOAT
            """))
            db.session.commit()
            print("✅ Added 'staff_revenue_price' column to invoice_item table")
            
            # Backfill existing records: set staff_revenue_price = original_amount
            db.session.execute(text("""
                UPDATE invoice_item 
                SET staff_revenue_price = original_amount 
                WHERE staff_revenue_price IS NULL
            """))
            db.session.commit()
            print("✅ Backfilled staff_revenue_price with original_amount for existing records")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding staff_revenue_price column: {str(e)}")
            raise

if __name__ == '__main__':
    print("🔄 Adding staff_revenue_price column to invoice_item table...")
    add_staff_revenue_price_column()
    print("✅ Migration completed successfully")
