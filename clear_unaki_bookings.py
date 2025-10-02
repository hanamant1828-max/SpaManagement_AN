
#!/usr/bin/env python3
"""
Clear all records from UnakiBooking table
"""

from app import app, db
from models import UnakiBooking

def clear_unaki_bookings():
    """Clear all UnakiBooking records from the database"""
    
    with app.app_context():
        try:
            print("🧹 Clearing UnakiBooking table...")
            
            # Get count of existing records
            existing_count = UnakiBooking.query.count()
            
            if existing_count == 0:
                print("📋 No records found in UnakiBooking table")
                return True
            
            print(f"📊 Found {existing_count} records to delete")
            
            # Delete all records
            UnakiBooking.query.delete()
            db.session.commit()
            
            # Verify deletion
            remaining_count = UnakiBooking.query.count()
            
            if remaining_count == 0:
                print(f"✅ Successfully deleted {existing_count} records from UnakiBooking table")
                print("🎉 UnakiBooking table is now empty")
                return True
            else:
                print(f"⚠️ Warning: {remaining_count} records still remain")
                return False
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error clearing UnakiBooking table: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("=" * 50)
    print("🗑️  CLEAR UNAKI BOOKING TABLE")
    print("=" * 50)
    print()
    
    success = clear_unaki_bookings()
    
    if success:
        print("\n✅ Operation completed successfully!")
    else:
        print("\n💥 Operation failed. Check error messages above.")
