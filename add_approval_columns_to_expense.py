
"""
Add approval workflow columns to expense table
"""
from app import app, db
from sqlalchemy import text

def add_approval_columns():
    """Add approval workflow columns to expense table"""
    with app.app_context():
        try:
            # Check existing columns
            result = db.session.execute(text("PRAGMA table_info(expense)")).fetchall()
            columns = [row[1] for row in result]
            
            # Add vendor_name if missing
            if 'vendor_name' not in columns:
                print("Adding vendor_name column...")
                db.session.execute(text(
                    "ALTER TABLE expense ADD COLUMN vendor_name VARCHAR(200)"
                ))
            
            # Add approval_status if missing
            if 'approval_status' not in columns:
                print("Adding approval_status column...")
                db.session.execute(text(
                    "ALTER TABLE expense ADD COLUMN approval_status VARCHAR(20) DEFAULT 'pending'"
                ))
            
            # Add approved_by if missing
            if 'approved_by' not in columns:
                print("Adding approved_by column...")
                db.session.execute(text(
                    "ALTER TABLE expense ADD COLUMN approved_by INTEGER"
                ))
            
            # Add approved_at if missing
            if 'approved_at' not in columns:
                print("Adding approved_at column...")
                db.session.execute(text(
                    "ALTER TABLE expense ADD COLUMN approved_at DATETIME"
                ))
            
            # Add rejection_reason if missing
            if 'rejection_reason' not in columns:
                print("Adding rejection_reason column...")
                db.session.execute(text(
                    "ALTER TABLE expense ADD COLUMN rejection_reason TEXT"
                ))
            
            db.session.commit()
            print("✅ Successfully added approval workflow columns")
                
        except Exception as e:
            print(f"❌ Error adding columns: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    add_approval_columns()
