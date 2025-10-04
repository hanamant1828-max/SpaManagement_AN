#!/usr/bin/env python3
import sqlite3
import os
import re
from pathlib import Path

def compute_sqlite_path():
    """Compute SQLite database path matching app.py logic"""
    base_dir = os.path.join(os.getcwd(), 'hanamantdatabase')
    instance = os.environ.get('SPA_DB_INSTANCE') or os.environ.get('REPL_SLUG') or 'default'
    instance = re.sub(r'[^A-Za-z0-9_-]', '_', instance)
    db_path = os.path.abspath(os.path.join(base_dir, f'{instance}.db'))
    return db_path

def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def add_out_of_office_columns():
    """Add out_of_office columns to shift_logs table if they don't exist"""
    db_path = compute_sqlite_path()
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("Creating database will be handled by app initialization")
        return
    
    print(f"🔧 Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        columns_to_add = [
            ('out_of_office_start', 'TIME'),
            ('out_of_office_end', 'TIME'),
            ('out_of_office_reason', 'VARCHAR(200)')
        ]
        
        added_count = 0
        
        for column_name, column_type in columns_to_add:
            if not column_exists(cursor, 'shift_logs', column_name):
                print(f"  ➕ Adding column: {column_name} {column_type}")
                cursor.execute(f"ALTER TABLE shift_logs ADD COLUMN {column_name} {column_type}")
                added_count += 1
            else:
                print(f"  ✓ Column already exists: {column_name}")
        
        conn.commit()
        
        if added_count > 0:
            print(f"✅ Successfully added {added_count} column(s)")
        else:
            print(f"✅ All columns already exist - no changes needed")
            
    except sqlite3.Error as e:
        conn.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting Out of Office Column Migration...")
    add_out_of_office_columns()
    print("✨ Migration complete!")
