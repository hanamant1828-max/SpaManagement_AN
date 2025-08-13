"""
Migrate Package model to add new fields for comprehensive spa packages
"""
from app import app, db
from sqlalchemy import text

def migrate_package_model():
    with app.app_context():
        print("Migrating Package model...")
        
        # Add new columns to the package table
        migrations = [
            "ALTER TABLE package ADD COLUMN IF NOT EXISTS package_type VARCHAR(50) DEFAULT 'regular';",
            "ALTER TABLE package ADD COLUMN IF NOT EXISTS credit_amount FLOAT DEFAULT 0.0;",
            "ALTER TABLE package ADD COLUMN IF NOT EXISTS student_discount FLOAT DEFAULT 0.0;", 
            "ALTER TABLE package ADD COLUMN IF NOT EXISTS min_guests INTEGER DEFAULT 1;",
            "ALTER TABLE package ADD COLUMN IF NOT EXISTS membership_benefits TEXT;"
        ]
        
        for migration in migrations:
            try:
                db.session.execute(text(migration))
                db.session.commit()
                print(f"✅ Applied: {migration}")
            except Exception as e:
                print(f"⚠️  Migration already applied or error: {migration} - {e}")
                db.session.rollback()
        
        print("✅ Package model migration completed!")

if __name__ == "__main__":
    migrate_package_model()