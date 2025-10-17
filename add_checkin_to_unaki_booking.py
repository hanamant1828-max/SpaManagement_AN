"""
Migration script to add check-in fields to unaki_bookings table
"""
from app import app, db
from sqlalchemy import text

def add_checkin_fields():
    """Add checked_in and checked_in_at columns to unaki_bookings table"""
    with app.app_context():
        try:
            # Check if columns already exist using SQLite's PRAGMA
            result = db.session.execute(text("PRAGMA table_info(unaki_bookings)"))
            existing_columns = [row[1] for row in result]
            
            # Add checked_in column if it doesn't exist
            if 'checked_in' not in existing_columns:
                print("Adding checked_in column...")
                db.session.execute(text("""
                    ALTER TABLE unaki_bookings 
                    ADD COLUMN checked_in BOOLEAN DEFAULT 0
                """))
                print("✅ Added checked_in column")
            else:
                print("⏭️  checked_in column already exists")
            
            # Add checked_in_at column if it doesn't exist
            if 'checked_in_at' not in existing_columns:
                print("Adding checked_in_at column...")
                db.session.execute(text("""
                    ALTER TABLE unaki_bookings 
                    ADD COLUMN checked_in_at TIMESTAMP
                """))
                print("✅ Added checked_in_at column")
            else:
                print("⏭️  checked_in_at column already exists")
            
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("Adding check-in fields to unaki_bookings table")
    print("=" * 60)
    add_checkin_fields()
