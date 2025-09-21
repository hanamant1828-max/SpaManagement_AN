#!/usr/bin/env python3
"""
Make email field nullable in User table - Fixed Version
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def make_email_nullable():
    """Make the email column nullable"""
    try:
        with app.app_context():
            print("🔧 Checking email column constraints...")

            # Check current constraint
            result = db.session.execute(text("""
                SELECT column_name, is_nullable, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user' AND column_name = 'email'
            """))

            current_info = result.fetchone()
            print(f"Current email column info: {current_info}")

            if current_info and current_info[1] == 'NO':
                print("📧 Email column is currently NOT NULL. Making it nullable...")

                # Step 1: Update any existing NULL values to empty string temporarily
                db.session.execute(text("UPDATE \"user\" SET email = '' WHERE email IS NULL"))

                # Step 2: Make email column nullable
                db.session.execute(text("ALTER TABLE \"user\" ALTER COLUMN email DROP NOT NULL"))

                # Step 3: Remove unique constraint if it exists
                try:
                    db.session.execute(text("ALTER TABLE \"user\" DROP CONSTRAINT IF EXISTS user_email_key"))
                    print("Removed unique constraint on email")
                except Exception as e:
                    print(f"Note: Could not remove unique constraint (may not exist): {e}")

                # Step 4: Create partial unique index (unique only for non-null values)
                try:
                    db.session.execute(text("""
                        CREATE UNIQUE INDEX IF NOT EXISTS user_email_unique_partial 
                        ON "user" (email) 
                        WHERE email IS NOT NULL AND email != ''
                    """))
                    print("Created partial unique index for email")
                except Exception as e:
                    print(f"Note: Could not create partial unique index: {e}")

                db.session.commit()

                print("✅ Email column is now nullable")

                # Verify the change
                result = db.session.execute(text("""
                    SELECT column_name, is_nullable, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'user' AND column_name = 'email'
                """))

                new_info = result.fetchone()
                print(f"Updated email column info: {new_info}")

            else:
                print("✅ Email column is already nullable")

            # Final test - try inserting a user without email
            print("\n🧪 Testing insertion without email...")
            test_result = db.session.execute(text("""
                INSERT INTO "user" (username, first_name, last_name, password_hash, role, is_active, created_at)
                VALUES ('test_no_email', 'Test', 'User', 'dummy_hash', 'staff', true, NOW())
                RETURNING id
            """))
            test_id = test_result.fetchone()[0]
            print(f"✅ Successfully inserted user without email, ID: {test_id}")

            # Clean up test user
            db.session.execute(text("DELETE FROM \"user\" WHERE id = :id"), {"id": test_id})
            db.session.commit()
            print("🧹 Cleaned up test user")

    except Exception as e:
        print(f"❌ Error making email nullable: {e}")
        db.session.rollback()
        return False

    return True

if __name__ == "__main__":
    success = make_email_nullable()
    if success:
        print("\n🎉 Email field is now properly nullable!")
    else:
        print("\n❌ Failed to make email field nullable")