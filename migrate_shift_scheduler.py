
"""
Migration script to update Shift Scheduler to new database schema
"""
from app import app, db
from models import ShiftManagement, ShiftLogs
from sqlalchemy import text
import logging

def migrate_shift_scheduler():
    """Migrate shift scheduler to new database schema"""
    with app.app_context():
        try:
            logging.info("Starting shift scheduler migration...")
            
            # Step 1: Clear existing shift scheduler data
            logging.info("Clearing existing shift scheduler data...")
            
            # Drop old tables if they exist
            try:
                db.session.execute(text("DROP TABLE IF EXISTS staff_daily_schedule"))
                db.session.execute(text("DROP TABLE IF EXISTS staff_schedule_range"))
                logging.info("Dropped old shift scheduler tables")
            except Exception as e:
                logging.warning(f"Error dropping old tables (may not exist): {e}")
            
            # Step 2: Create new tables
            logging.info("Creating new shift scheduler tables...")
            db.create_all()
            
            # Verify tables were created
            try:
                # Test the new tables
                test_query = db.session.execute(text("SELECT COUNT(*) FROM shift_management")).scalar()
                logging.info(f"shift_management table created successfully, count: {test_query}")
                
                test_query = db.session.execute(text("SELECT COUNT(*) FROM shift_logs")).scalar()
                logging.info(f"shift_logs table created successfully, count: {test_query}")
                
            except Exception as e:
                logging.error(f"Error verifying new tables: {e}")
                return False
            
            db.session.commit()
            logging.info("Shift scheduler migration completed successfully!")
            return True
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Migration failed: {e}")
            return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = migrate_shift_scheduler()
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
