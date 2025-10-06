
#!/usr/bin/env python3
"""
Export the current working database to a fresh demo database
This ensures the working state is preserved when cloning the project
"""

import os
import shutil
import sqlite3
from datetime import datetime

def export_working_database():
    """Export current working database to a versioned backup"""
    
    # Source database (current working)
    source_db = os.path.join('hanamantdatabase', 'workspace.db')
    
    # Backup database (for git)
    backup_db = os.path.join('hanamantdatabase', 'default.db')
    
    # Timestamped backup (safety)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    timestamped_backup = os.path.join('hanamantdatabase', f'backup_{timestamp}.db')
    
    print("🔄 Exporting Working Database State")
    print("=" * 60)
    
    # Check if source exists
    if not os.path.exists(source_db):
        print(f"❌ Source database not found: {source_db}")
        return False
    
    try:
        # Create timestamped backup first (safety)
        print(f"📦 Creating timestamped backup: {timestamped_backup}")
        shutil.copy2(source_db, timestamped_backup)
        print(f"✅ Timestamped backup created")
        
        # Copy to default.db (this will be in git)
        print(f"\n📦 Creating default database: {backup_db}")
        shutil.copy2(source_db, backup_db)
        print(f"✅ Default database created")
        
        # Verify database integrity
        print("\n🔍 Verifying database integrity...")
        conn = sqlite3.connect(backup_db)
        cursor = conn.cursor()
        
        # Get table counts
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📊 Database Statistics:")
        print(f"   Total tables: {len(tables)}")
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"   - {table_name}: {count} records")
        
        conn.close()
        
        # Create .gitignore entry for workspace.db (keep it local)
        gitignore_path = os.path.join('hanamantdatabase', '.gitignore')
        with open(gitignore_path, 'w') as f:
            f.write("# Ignore local workspace database\n")
            f.write("workspace.db\n")
            f.write("backup_*.db\n")
        
        print(f"\n✅ Database export completed successfully!")
        print(f"\n📋 Summary:")
        print(f"   - Timestamped backup: {timestamped_backup} (local only)")
        print(f"   - Default database: {backup_db} (will be in git)")
        print(f"   - Working database: {source_db} (ignored by git)")
        print(f"\n🎯 Next Steps:")
        print(f"   1. Add and commit the changes:")
        print(f"      git add hanamantdatabase/default.db")
        print(f"      git add hanamantdatabase/.gitignore")
        print(f"      git commit -m 'Add working database snapshot'")
        print(f"   2. When cloning, default.db will be copied to workspace.db automatically")
        
        return True
        
    except Exception as e:
        print(f"❌ Error exporting database: {e}")
        return False

if __name__ == "__main__":
    success = export_working_database()
    exit(0 if success else 1)
