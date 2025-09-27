
import sys
sys.path.append('.')

from app import app, db
from models import UnakiBooking, Service
from sqlalchemy import text

def add_service_id_column():
    """Add service_id column to unaki_booking table and populate it"""
    
    with app.app_context():
        print("📝 Adding service_id column to unaki_booking table...")
        
        try:
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('unaki_booking')]
            
            if 'service_id' not in columns:
                # Add the service_id column
                db.engine.execute(text('ALTER TABLE unaki_booking ADD COLUMN service_id INTEGER'))
                print("✅ service_id column added successfully")
            else:
                print("✅ service_id column already exists")
            
            # Populate service_id for existing bookings
            print("🔍 Populating service_id for existing bookings...")
            
            bookings = UnakiBooking.query.filter(UnakiBooking.service_id.is_(None)).all()
            updated_count = 0
            
            for booking in bookings:
                if booking.service_name:
                    # Find matching service by name
                    service = Service.query.filter_by(name=booking.service_name, is_active=True).first()
                    if service:
                        booking.service_id = service.id
                        updated_count += 1
                    else:
                        print(f"⚠️ No matching service found for: {booking.service_name}")
            
            db.session.commit()
            print(f"✅ Updated {updated_count} bookings with service_id")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during migration: {e}")
            raise
        
        print("🎉 UnakiBooking service_id migration completed successfully!")

if __name__ == '__main__':
    add_service_id_column()
