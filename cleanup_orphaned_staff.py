
#!/usr/bin/env python3
"""
Cleanup script to remove orphaned staff records that were partially created
"""
from app import app, db
from models import User

def cleanup_orphaned_staff():
    """Remove staff records with duplicate staff codes or missing required fields"""
    with app.app_context():
        print("🧹 Cleaning up orphaned staff records...")
        
        try:
            # Find staff with no staff_code (orphaned during creation)
            orphaned = User.query.filter(User.staff_code.is_(None)).all()
            
            for staff in orphaned:
                print(f"   Removing orphaned staff: {staff.username} (ID: {staff.id})")
                db.session.delete(staff)
            
            # Check for duplicate staff codes
            all_staff = User.query.filter(User.staff_code.isnot(None)).all()
            staff_codes = {}
            
            for staff in all_staff:
                if staff.staff_code in staff_codes:
                    print(f"   ⚠️ Duplicate staff code found: {staff.staff_code}")
                    print(f"      Staff 1: {staff_codes[staff.staff_code].username} (ID: {staff_codes[staff.staff_code].id})")
                    print(f"      Staff 2: {staff.username} (ID: {staff.id})")
                else:
                    staff_codes[staff.staff_code] = staff
            
            db.session.commit()
            print(f"✅ Cleanup completed. Removed {len(orphaned)} orphaned records.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Cleanup failed: {e}")
            print("⚠️ This may be due to database schema issues. Please run database migrations.")

if __name__ == '__main__':
    cleanup_orphaned_staff()
