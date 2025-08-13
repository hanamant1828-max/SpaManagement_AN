
#!/usr/bin/env python3
"""
Database migration script to add new staff management columns
"""
import sqlite3
from datetime import datetime

def migrate_database():
    """Add missing columns to existing database"""
    conn = sqlite3.connect('instance/spa_management.db')
    cursor = conn.cursor()
    
    # List of new columns to add to User table
    new_columns = [
        ('profile_photo_url', 'TEXT'),
        ('gender', 'TEXT DEFAULT "other"'),
        ('date_of_birth', 'DATE'),
        ('date_of_joining', 'DATE'),
        ('staff_code', 'TEXT'),
        ('notes_bio', 'TEXT'),
        ('designation', 'TEXT'),
        ('aadhaar_number', 'TEXT'),
        ('aadhaar_card_url', 'TEXT'),
        ('pan_number', 'TEXT'),
        ('pan_card_url', 'TEXT'),
        ('verification_status', 'BOOLEAN DEFAULT 0'),
        ('face_image_url', 'TEXT'),
        ('facial_encoding', 'TEXT'),
        ('enable_face_checkin', 'BOOLEAN DEFAULT 1'),
        ('working_days', 'TEXT DEFAULT "1111100"'),
        ('shift_start_time', 'TIME'),
        ('shift_end_time', 'TIME'),
        ('break_time', 'TEXT'),
        ('weekly_off_days', 'TEXT'),
        ('commission_percentage', 'REAL DEFAULT 0.0'),
        ('fixed_commission', 'REAL DEFAULT 0.0'),
        ('total_revenue_generated', 'REAL DEFAULT 0.0'),
        ('last_login', 'DATETIME'),
        ('last_service_performed', 'DATETIME'),
        ('total_sales', 'REAL DEFAULT 0.0'),
        ('total_clients_served', 'INTEGER DEFAULT 0'),
        ('average_rating', 'REAL DEFAULT 0.0'),
        ('work_schedule', 'TEXT'),
        ('specialties', 'TEXT')
    ]
    
    # Check which columns already exist
    cursor.execute("PRAGMA table_info(user)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    
    # Add missing columns
    for column_name, column_type in new_columns:
        if column_name not in existing_columns:
            try:
                cursor.execute(f'ALTER TABLE user ADD COLUMN {column_name} {column_type}')
                print(f"✅ Added column: {column_name}")
            except sqlite3.OperationalError as e:
                print(f"❌ Failed to add {column_name}: {e}")
    
    # Create new tables if they don't exist
    tables_to_create = [
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            check_in_time DATETIME NOT NULL,
            check_out_time DATETIME,
            check_in_method TEXT DEFAULT 'manual',
            total_hours REAL,
            date DATE NOT NULL,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (staff_id) REFERENCES user (id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS leave (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            applied_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            approved_by INTEGER,
            FOREIGN KEY (staff_id) REFERENCES user (id),
            FOREIGN KEY (approved_by) REFERENCES user (id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS staff_service (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            skill_level TEXT DEFAULT 'beginner',
            assigned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (staff_id) REFERENCES user (id),
            FOREIGN KEY (service_id) REFERENCES service (id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS staff_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            services_completed INTEGER DEFAULT 0,
            revenue_generated REAL DEFAULT 0.0,
            client_ratings_avg REAL DEFAULT 0.0,
            attendance_percentage REAL DEFAULT 0.0,
            commission_earned REAL DEFAULT 0.0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (staff_id) REFERENCES user (id)
        )
        """
    ]
    
    for table_sql in tables_to_create:
        try:
            cursor.execute(table_sql)
            print(f"✅ Created/verified table")
        except sqlite3.OperationalError as e:
            print(f"❌ Failed to create table: {e}")
    
    conn.commit()
    conn.close()
    print("🎉 Database migration completed!")

if __name__ == "__main__":
    migrate_database()
