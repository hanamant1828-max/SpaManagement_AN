
#!/usr/bin/env python3
"""
Remove client_name column from UnakiBooking table since we only want client_id
"""

from app import app, db
from sqlalchemy import text, inspect

def remove_client_name_column():
    """Remove client_name column from UnakiBooking table"""
    
    with app.app_context():
        try:
            # Check if column exists
            inspector = inspect(db.engine)
            columns = inspector.get_columns('unaki_booking')
            column_names = [col['name'] for col in columns]
            
            print(f"🔍 Current columns in unaki_booking: {column_names}")
            
            if 'client_name' not in column_names:
                print("✅ client_name column already removed from unaki_booking table")
                return True
            
            print("🗑️ Removing client_name column from unaki_booking table...")
            
            # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
            # First, get the current table structure
            print("📋 Creating backup of current data...")
            
            # Create a temporary table with the new structure (without client_name)
            db.session.execute(text("""
                CREATE TABLE unaki_booking_new (
                    id INTEGER PRIMARY KEY,
                    client_id INTEGER REFERENCES client(id),
                    client_phone VARCHAR(20),
                    client_email VARCHAR(120),
                    staff_id INTEGER NOT NULL REFERENCES user(id),
                    staff_name VARCHAR(100) NOT NULL,
                    service_id INTEGER REFERENCES service(id),
                    service_name VARCHAR(100) NOT NULL,
                    service_duration INTEGER NOT NULL,
                    service_price FLOAT DEFAULT 0.0,
                    appointment_date DATE NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME NOT NULL,
                    status VARCHAR(20) DEFAULT 'scheduled',
                    notes TEXT,
                    internal_notes TEXT,
                    booking_source VARCHAR(50) DEFAULT 'unaki_system',
                    booking_method VARCHAR(50) DEFAULT 'drag_select',
                    amount_charged FLOAT DEFAULT 0.0,
                    payment_status VARCHAR(20) DEFAULT 'pending',
                    payment_method VARCHAR(20),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    confirmed_at DATETIME,
                    completed_at DATETIME
                )
            """))
            
            # Copy data from old table to new table (excluding client_name)
            print("📦 Copying data to new table structure...")
            db.session.execute(text("""
                INSERT INTO unaki_booking_new (
                    id, client_id, client_phone, client_email, staff_id, staff_name,
                    service_id, service_name, service_duration, service_price,
                    appointment_date, start_time, end_time, status, notes, internal_notes,
                    booking_source, booking_method, amount_charged, payment_status, payment_method,
                    created_at, updated_at, confirmed_at, completed_at
                )
                SELECT 
                    id, client_id, client_phone, client_email, staff_id, staff_name,
                    service_id, service_name, service_duration, service_price,
                    appointment_date, start_time, end_time, status, notes, internal_notes,
                    booking_source, booking_method, amount_charged, payment_status, payment_method,
                    created_at, updated_at, confirmed_at, completed_at
                FROM unaki_booking
            """))
            
            # Drop the old table
            print("🗑️ Dropping old table...")
            db.session.execute(text("DROP TABLE unaki_booking"))
            
            # Rename the new table
            print("🔄 Renaming new table...")
            db.session.execute(text("ALTER TABLE unaki_booking_new RENAME TO unaki_booking"))
            
            db.session.commit()
            print("✅ client_name column removed successfully")
            
            # Verify the column was removed
            inspector = inspect(db.engine)
            columns = inspector.get_columns('unaki_booking')
            column_names = [col['name'] for col in columns]
            
            if 'client_name' not in column_names:
                print("✅ Verification successful: client_name column removed")
                print(f"📋 Updated columns: {column_names}")
                return True
            else:
                print("❌ Verification failed: client_name column still exists")
                return False
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error removing client_name column: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = remove_client_name_column()
    if success:
        print("\n🎉 UnakiBooking client_name column removal completed successfully!")
        print("💡 The Unaki booking system will now use only client_id for customer references.")
    else:
        print("\n💥 Column removal failed! Please check the error above.")
