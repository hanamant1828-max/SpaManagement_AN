#!/usr/bin/env python3
import sqlite3
import os

# Connect to the SQLite database
db_path = os.path.join(os.getcwd(), 'hanamantdatabase', 'workspace.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Adding missing 'purpose' column to inventory_consumption table...")

try:
    # Add the purpose column
    cursor.execute("ALTER TABLE inventory_consumption ADD COLUMN purpose VARCHAR(200)")
    conn.commit()
    print("✅ Successfully added 'purpose' column")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("ℹ️ Column 'purpose' already exists")
    else:
        print(f"❌ Error: {e}")
        raise

# Verify the column was added
print("\n=== UPDATED CONSUMPTION TABLE SCHEMA ===")
cursor.execute("PRAGMA table_info(inventory_consumption)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
print("\n✅ Database update complete")
