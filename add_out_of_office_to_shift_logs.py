
#!/usr/bin/env python3
"""
Add out of office columns to shift_logs table
"""

from app import app, db
from sqlalchemy import text

def migrate_shift_logs():
    """Add out of office columns to shift_logs table"""
    with app.app_context():
        try:
            print("🔄 Adding out of office columns to shift_logs table...")
            
            # Add the new columns
            with db.engine.connect() as conn:
                # Check if columns already exist
                result = conn.execute(text("PRAGMA table_info(shift_logs)"))
                columns = [row[1] for row in result]
                
                if 'out_of_office_start' not in columns:
                    conn.execute(text("ALTER TABLE shift_logs ADD COLUMN out_of_office_start TIME"))
                    print("✅ Added out_of_office_start column")
                
                if 'out_of_office_end' not in columns:
                    conn.execute(text("ALTER TABLE shift_logs ADD COLUMN out_of_office_end TIME"))
                    print("✅ Added out_of_office_end column")
                
                if 'out_of_office_reason' not in columns:
                    conn.execute(text("ALTER TABLE shift_logs ADD COLUMN out_of_office_reason VARCHAR(200)"))
                    print("✅ Added out_of_office_reason column")
                
                conn.commit()
            
            print("\n✅ Migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False

if __name__ == '__main__':
    migrate_shift_logs()
