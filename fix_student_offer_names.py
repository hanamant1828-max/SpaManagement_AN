
#!/usr/bin/env python3
"""
Migration script to add name column to student_offers table
"""
import os
import sys
from app import app, db

def fix_student_offer_names():
    """Add name column and populate with default values"""
    with app.app_context():
        try:
            # Check if name column exists
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('student_offers')]
            
            if 'name' not in columns:
                print("Adding 'name' column to student_offers table...")
                db.session.execute(text("ALTER TABLE student_offers ADD COLUMN name VARCHAR(200)"))
                db.session.commit()
                print("✅ Column added successfully")
            else:
                print("ℹ️ Column 'name' already exists")
            
            # Update existing offers with default names
            from models import StudentOffer
            offers = StudentOffer.query.filter(
                (StudentOffer.name == None) | (StudentOffer.name == '')
            ).all()
            
            if offers:
                print(f"\nUpdating {len(offers)} student offers with default names...")
                for offer in offers:
                    offer.name = f"Student Discount {offer.discount_percentage}%"
                
                db.session.commit()
                print("✅ All student offers updated with names")
            else:
                print("ℹ️ All student offers already have names")
            
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during migration: {str(e)}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    fix_student_offer_names()
