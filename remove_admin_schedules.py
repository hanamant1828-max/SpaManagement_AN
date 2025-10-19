
"""
Remove all shift management and shift logs for admin user
"""
from app import app, db
from models import User, ShiftManagement, ShiftLogs

def remove_admin_schedules():
    """Remove all schedules for admin user"""
    with app.app_context():
        # Find admin user (typically user with role='admin' or username='admin')
        admin_user = User.query.filter(
            db.or_(
                User.username == 'admin',
                User.email == 'admin@spa.com',
                User.role == 'admin'
            )
        ).first()
        
        if not admin_user:
            print("❌ Admin user not found")
            return
        
        print(f"✅ Found admin user: {admin_user.username} (ID: {admin_user.id})")
        
        # Find all shift management records for admin
        shift_managements = ShiftManagement.query.filter_by(staff_id=admin_user.id).all()
        
        if not shift_managements:
            print("ℹ️  No shift management records found for admin user")
            return
        
        total_logs_deleted = 0
        total_mgmt_deleted = 0
        
        # Delete shift logs first (due to foreign key constraint)
        for mgmt in shift_managements:
            logs = ShiftLogs.query.filter_by(shift_management_id=mgmt.id).all()
            logs_count = len(logs)
            
            for log in logs:
                db.session.delete(log)
                total_logs_deleted += 1
            
            # Then delete the shift management record
            db.session.delete(mgmt)
            total_mgmt_deleted += 1
            
            print(f"  🗑️  Deleted shift management {mgmt.id} with {logs_count} logs")
        
        # Commit all deletions
        db.session.commit()
        
        print(f"\n✅ Successfully deleted:")
        print(f"   - {total_mgmt_deleted} shift management record(s)")
        print(f"   - {total_logs_deleted} shift log(s)")
        print(f"   for admin user: {admin_user.username}")

if __name__ == '__main__':
    remove_admin_schedules()
