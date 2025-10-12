
"""
Add missing deducted_from_account column to expense table
"""
from app import app, db
from sqlalchemy import text

def add_deducted_from_account_column():
    """Add deducted_from_account column to expense table"""
    with app.app_context():
        try:
            # Check if column exists
            result = db.session.execute(text("PRAGMA table_info(expense)")).fetchall()
            columns = [row[1] for row in result]
            
            if 'deducted_from_account' not in columns:
                print("Adding deducted_from_account column to expense table...")
                db.session.execute(text(
                    "ALTER TABLE expense ADD COLUMN deducted_from_account BOOLEAN DEFAULT 0"
                ))
                db.session.commit()
                print("✅ Successfully added deducted_from_account column")
            else:
                print("ℹ️ Column deducted_from_account already exists")
                
        except Exception as e:
            print(f"❌ Error adding column: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    add_deducted_from_account_column()
