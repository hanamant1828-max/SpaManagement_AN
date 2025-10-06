from app import app, db
from models import User, ShiftManagement
from sqlalchemy import func

def find_and_fix_duplicate_staff():
    with app.app_context():
        print("🔍 Searching for duplicate staff records based on staff_code...")
        
        duplicates_by_code = db.session.query(
            User.staff_code, 
            func.count(User.id).label('count')
        ).filter(
            User.is_active == True,
            User.staff_code.isnot(None),
            User.staff_code != ''
        ).group_by(
            User.staff_code
        ).having(
            func.count(User.id) > 1
        ).all()
        
        if not duplicates_by_code:
            print("✅ No duplicate staff found by staff_code!")
        else:
            print(f"⚠️  Found {len(duplicates_by_code)} sets of duplicate staff by staff_code:")
            
            for staff_code, count in duplicates_by_code:
                print(f"\n👥 Staff Code: {staff_code} ({count} records)")
                
                users = User.query.filter_by(
                    staff_code=staff_code,
                    is_active=True
                ).order_by(User.created_at).all()
                
                keep_user = users[0]
                print(f"  ✓ Keeping: ID {keep_user.id} - {keep_user.first_name} {keep_user.last_name} (created: {keep_user.created_at})")
                
                for user in users[1:]:
                    print(f"  ✗ Removing: ID {user.id} - {user.first_name} {user.last_name} (created: {user.created_at})")
                    
                    shift_mgmt = ShiftManagement.query.filter_by(staff_id=user.id).first()
                    if shift_mgmt:
                        existing_keep_mgmt = ShiftManagement.query.filter_by(staff_id=keep_user.id).first()
                        if not existing_keep_mgmt:
                            print(f"    → Transferring shift management to ID {keep_user.id}")
                            shift_mgmt.staff_id = keep_user.id
                        else:
                            print(f"    → Deleting duplicate shift management")
                            db.session.delete(shift_mgmt)
                    
                    user.is_active = False
                    print(f"    → Marked as inactive")
        
        print("\n🔍 Checking for duplicates by username (different from staff_code)...")
        
        duplicates_by_username = db.session.query(
            User.username, 
            func.count(User.id).label('count')
        ).filter(
            User.is_active == True
        ).group_by(
            User.username
        ).having(
            func.count(User.id) > 1
        ).all()
        
        if not duplicates_by_username:
            print("✅ No duplicate staff found by username!")
            return
        
        print(f"⚠️  Found {len(duplicates_by_username)} sets of duplicate staff by username:")
        
        for username, count in duplicates_by_username:
            print(f"\n👥 Username: {username} ({count} records)")
            
            users = User.query.filter_by(
                username=username,
                is_active=True
            ).order_by(User.created_at).all()
            
            print(f"  ⚠️  Manual review required - multiple users with same username:")
            for user in users:
                print(f"    - ID {user.id}: {user.first_name} {user.last_name} (staff_code: {user.staff_code or 'N/A'})")
        
        try:
            db.session.commit()
            print("\n✅ Successfully cleaned up duplicate staff records!")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {e}")

if __name__ == '__main__':
    find_and_fix_duplicate_staff()
