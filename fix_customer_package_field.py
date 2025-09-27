
#!/usr/bin/env python3
"""
Fix CustomerPackage table - rename client_id to customer_id
"""
import sqlite3
import os

def fix_customer_package_table():
    """Fix the CustomerPackage table field name"""
    db_path = 'instance/spa_management.db'
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the table exists and has the wrong field name
        cursor.execute("PRAGMA table_info(customer_packages)")
        columns = cursor.fetchall()
        
        has_client_id = any(col[1] == 'client_id' for col in columns)
        has_customer_id = any(col[1] == 'customer_id' for col in columns)
        
        if has_client_id and not has_customer_id:
            print("Found client_id field, renaming to customer_id...")
            
            # SQLite doesn't support RENAME COLUMN directly in older versions
            # So we'll create a new table and copy data
            
            # First, get the existing data
            cursor.execute("SELECT * FROM customer_packages")
            existing_data = cursor.fetchall()
            
            # Drop the existing table
            cursor.execute("DROP TABLE IF EXISTS customer_packages_backup")
            cursor.execute("ALTER TABLE customer_packages RENAME TO customer_packages_backup")
            
            # Create the new table with correct field name
            cursor.execute("""
                CREATE TABLE customer_packages (
                    id INTEGER PRIMARY KEY,
                    customer_id INTEGER NOT NULL,
                    package_id INTEGER NOT NULL,
                    package_type VARCHAR(20) NOT NULL,
                    status VARCHAR(20) DEFAULT 'active',
                    assigned_date DATETIME,
                    expiry_date DATETIME,
                    sessions_total INTEGER,
                    sessions_used INTEGER DEFAULT 0,
                    prepaid_balance FLOAT DEFAULT 0.0,
                    prepaid_used FLOAT DEFAULT 0.0,
                    is_unlimited BOOLEAN DEFAULT 0,
                    FOREIGN KEY (customer_id) REFERENCES customers(id)
                )
            """)
            
            # Copy data from backup table to new table
            if existing_data:
                cursor.execute("""
                    INSERT INTO customer_packages 
                    SELECT * FROM customer_packages_backup
                """)
                print(f"Migrated {len(existing_data)} customer package records")
            
            # Drop the backup table
            cursor.execute("DROP TABLE customer_packages_backup")
            
            conn.commit()
            print("✅ Successfully fixed CustomerPackage table field name!")
            
        elif has_customer_id:
            print("✅ CustomerPackage table already has correct field name (customer_id)")
            
        else:
            print("⚠️ CustomerPackage table not found or has unexpected schema")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing CustomerPackage table: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🔧 Fixing CustomerPackage table field name...")
    fix_customer_package_table()
    print("🔧 Migration complete!")
