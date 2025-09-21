
#!/usr/bin/env python3
"""
Migration script to update student offers schema
"""

from app import app, db
from models import StudentOffer, StudentOfferService
import sqlite3

def migrate_student_offers():
    """Migrate existing student offers to new schema"""
    with app.app_context():
        try:
            # Check if new tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("Current tables:", tables)
            
            # Create new tables if they don't exist
            if 'student_offer_services' not in tables:
                print("Creating student_offer_services table...")
                StudentOfferService.__table__.create(db.engine, checkfirst=True)
                print("✅ student_offer_services table created")
            
            # Check current student_offers table structure
            conn = sqlite3.connect('hanamantdatabase/workspace.db')
            cursor = conn.cursor()
            
            # Get current column names
            cursor.execute("PRAGMA table_info(student_offers)")
            columns = [column[1] for column in cursor.fetchall()]
            print(f"Current student_offers columns: {columns}")
            
            # Backup existing data if old schema exists
            old_offers = []
            if 'service_id' in columns:
                print("Backing up existing student offers...")
                cursor.execute("SELECT * FROM student_offers")
                old_offers = cursor.fetchall()
                print(f"Backed up {len(old_offers)} existing offers")
            
            # Drop and recreate table with new schema
            print("Recreating student_offers table with new schema...")
            cursor.execute("DROP TABLE IF EXISTS student_offers")
            conn.commit()
            
            # Create new table
            StudentOffer.__table__.create(db.engine, checkfirst=True)
            print("✅ student_offers table recreated with new schema")
            
            # Migrate old data to new schema if we had any
            if old_offers:
                print("Migrating old data to new schema...")
                for offer in old_offers:
                    # Create new offer with converted data
                    new_offer = StudentOffer(
                        discount_percentage=offer[4] if len(offer) > 4 else 10.0,  # old discount_percent
                        valid_from=db.func.date('now'),  # Default to today
                        valid_to=db.func.date('now', '+6 months'),  # Default to 6 months from now
                        valid_days=offer[6] if len(offer) > 6 else 'Mon-Fri',  # old valid_days
                        conditions='Valid with Student ID',
                        is_active=offer[7] if len(offer) > 7 else True
                    )
                    db.session.add(new_offer)
                    db.session.flush()
                    
                    # Add service mapping if we had a service_id
                    if len(offer) > 1 and offer[1]:  # old service_id
                        service_mapping = StudentOfferService(
                            offer_id=new_offer.id,
                            service_id=offer[1]
                        )
                        db.session.add(service_mapping)
                
                db.session.commit()
                print(f"✅ Migrated {len(old_offers)} offers to new schema")
            
            conn.close()
            print("✅ Student offers migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_student_offers()
