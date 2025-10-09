
#!/usr/bin/env python3
"""
Remove unique constraint from email column in client table
Keep only phone number as unique constraint
"""

from app import app, db
from sqlalchemy import text, inspect

def fix_email_constraint():
    """Remove unique constraint from email, keep only phone unique"""
    
    with app.app_context():
        try:
            # Check current constraints
            inspector = inspect(db.engine)
            
            print("🔍 Checking current email column configuration...")
            
            # For SQLite, we need to recreate the table to remove the constraint
            print("📝 Removing unique constraint from email column...")
            
            # Step 1: Create a temporary table without email unique constraint
            db.session.execute(text("""
                CREATE TABLE client_new (
                    id INTEGER PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email VARCHAR(120),
                    phone VARCHAR(20) NOT NULL UNIQUE,
                    date_of_birth DATE,
                    gender VARCHAR(10),
                    address TEXT,
                    created_at DATETIME,
                    last_visit DATETIME,
                    total_visits INTEGER DEFAULT 0,
                    total_spent FLOAT DEFAULT 0.0,
                    is_active BOOLEAN DEFAULT 1,
                    preferences TEXT,
                    allergies TEXT,
                    notes TEXT,
                    face_encoding TEXT,
                    face_image_url VARCHAR(255),
                    loyalty_points INTEGER DEFAULT 0,
                    is_vip BOOLEAN DEFAULT 0,
                    preferred_communication VARCHAR(20) DEFAULT 'email',
                    marketing_consent BOOLEAN DEFAULT 1,
                    reminder_preferences TEXT,
                    referral_source VARCHAR(100),
                    lifetime_value FLOAT DEFAULT 0.0,
                    last_no_show DATETIME,
                    no_show_count INTEGER DEFAULT 0
                )
            """))
            
            # Step 2: Copy data from old table to new table
            db.session.execute(text("""
                INSERT INTO client_new 
                SELECT * FROM client
            """))
            
            # Step 3: Drop old table
            db.session.execute(text("DROP TABLE client"))
            
            # Step 4: Rename new table to original name
            db.session.execute(text("ALTER TABLE client_new RENAME TO client"))
            
            # Step 5: Create index on email for performance (non-unique)
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_client_email ON client(email)
            """))
            
            db.session.commit()
            
            print("✅ Email constraint removed successfully")
            print("✅ Phone number remains unique")
            print("✅ Email can now be NULL or duplicate")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error fixing email constraint: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    import sys
    success = fix_email_constraint()
    sys.exit(0 if success else 1)
