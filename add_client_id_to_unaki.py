
#!/usr/bin/env python3
"""
Add client_id column to UnakiBooking table and populate it where possible
"""

from app import app, db
from models import UnakiBooking, Customer
from sqlalchemy import text

def add_client_id_column():
    """Add client_id column to UnakiBooking table"""
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('unaki_booking') 
                WHERE name = 'client_id'
            """))
            column_exists = result.fetchone()[0] > 0
            
            if column_exists:
                print("✅ client_id column already exists in unaki_booking table")
            else:
                print("📝 Adding client_id column to unaki_booking table...")
                
                # Add the client_id column
                db.session.execute(text("""
                    ALTER TABLE unaki_booking 
                    ADD COLUMN client_id INTEGER REFERENCES client(id)
                """))
                
                print("✅ client_id column added successfully")
            
            # Now try to populate client_id for existing records
            print("🔍 Populating client_id for existing bookings...")
            
            bookings = UnakiBooking.query.all()
            updated_count = 0
            
            for booking in bookings:
                if not booking.client_id and booking.client_name:
                    # Try to find matching customer by name
                    customer = Customer.query.filter(
                        (Customer.full_name == booking.client_name) |
                        (Customer.first_name + ' ' + Customer.last_name == booking.client_name)
                    ).first()
                    
                    if customer:
                        booking.client_id = customer.id
                        updated_count += 1
                        print(f"  ✅ Linked booking {booking.id} to customer {customer.full_name} (ID: {customer.id})")
                    else:
                        # Try to find by phone if available
                        if booking.client_phone:
                            customer_by_phone = Customer.query.filter_by(phone=booking.client_phone).first()
                            if customer_by_phone:
                                booking.client_id = customer_by_phone.id
                                updated_count += 1
                                print(f"  ✅ Linked booking {booking.id} to customer {customer_by_phone.full_name} by phone (ID: {customer_by_phone.id})")
            
            db.session.commit()
            
            print(f"\n📊 Migration Summary:")
            print(f"   Total bookings: {len(bookings)}")
            print(f"   Linked to customers: {updated_count}")
            print(f"   Unlinked (new customers): {len(bookings) - updated_count}")
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during migration: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        return True

if __name__ == "__main__":
    success = add_client_id_column()
    if success:
        print("\n🎉 UnakiBooking client_id migration completed!")
    else:
        print("\n💥 Migration failed!")
