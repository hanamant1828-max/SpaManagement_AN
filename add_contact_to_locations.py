
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Add contact column to locations table
        with db.engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("PRAGMA table_info(locations)"))
            columns = [row[1] for row in result]
            
            if 'contact' not in columns:
                print("Adding 'contact' column to locations table...")
                conn.execute(text("ALTER TABLE locations ADD COLUMN contact VARCHAR(50)"))
                conn.commit()
                print("✅ Contact column added successfully!")
            else:
                print("ℹ️ Contact column already exists")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()
