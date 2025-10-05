import sqlite3
import os
import sys

DB_PATH = "/home/runner/workspace/hanamantdatabase/workspace.db"

def col_exists(c, table, col):
    c.execute(f"PRAGMA table_info({table})")
    return any(r[1] == col for r in c.fetchall())

def main():
    print(f"Using database: {DB_PATH}")
    
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        # package_name (display name for the assignment)
        if not col_exists(c, "service_package_assignment", "package_name"):
            print("Adding package_name column...")
            c.execute("ALTER TABLE service_package_assignment ADD COLUMN package_name TEXT")
            print("✅ Added package_name column")
        else:
            print("✅ package_name column already exists")
        
        # optional: store service name for service-packages to show alongside
        if not col_exists(c, "service_package_assignment", "service_name"):
            print("Adding service_name column...")
            c.execute("ALTER TABLE service_package_assignment ADD COLUMN service_name TEXT")
            print("✅ Added service_name column")
        else:
            print("✅ service_name column already exists")
        
        conn.commit()
    
    print("✅ OK: columns ensured.")

if __name__ == "__main__":
    main()
