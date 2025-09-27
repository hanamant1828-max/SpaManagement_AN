
#!/usr/bin/env python3
"""
Check UnakiBooking table schema and data
"""

from app import app, db
from models import UnakiBooking
from sqlalchemy import inspect

def check_unaki_booking_data():
    """Check UnakiBooking table schema and current data"""
    
    with app.app_context():
        try:
            # Get table schema information
            inspector = inspect(db.engine)
            columns = inspector.get_columns('unaki_booking')
            
            print("🗂️  UNAKI BOOKING TABLE SCHEMA")
            print("=" * 60)
            print(f"{'Column Name':<20} {'Type':<20} {'Nullable':<10} {'Default'}")
            print("-" * 60)
            
            for column in columns:
                column_name = column['name']
                column_type = str(column['type'])
                nullable = "Yes" if column['nullable'] else "No"
                default = column.get('default', 'None')
                print(f"{column_name:<20} {column_type:<20} {nullable:<10} {str(default)}")
            
            print("\n📊 CURRENT DATA IN UNAKI BOOKING TABLE")
            print("=" * 80)
            
            # Get all bookings
            bookings = UnakiBooking.query.order_by(UnakiBooking.appointment_date, UnakiBooking.start_time).all()
            
            if not bookings:
                print("❌ No bookings found in the table")
                return
            
            print(f"📈 Total bookings: {len(bookings)}\n")
            
            # Group by date for better organization
            from collections import defaultdict
            bookings_by_date = defaultdict(list)
            
            for booking in bookings:
                bookings_by_date[booking.appointment_date].append(booking)
            
            for date, date_bookings in bookings_by_date.items():
                print(f"📅 DATE: {date.strftime('%Y-%m-%d (%A)')}")
                print(f"   Total appointments: {len(date_bookings)}")
                print("   " + "-" * 70)
                
                for booking in sorted(date_bookings, key=lambda x: x.start_time):
                    print(f"   ID: {booking.id:3d} | {booking.start_time.strftime('%H:%M')}-{booking.end_time.strftime('%H:%M')} | "
                          f"Staff: {booking.staff_name:<12} | Client: {booking.client_name:<15} | "
                          f"Service: {booking.service_name:<20} | Status: {booking.status}")
                print()
            
            # Summary statistics
            print("📊 SUMMARY STATISTICS")
            print("=" * 40)
            
            # Count by status
            status_counts = {}
            staff_counts = {}
            service_counts = {}
            
            for booking in bookings:
                status_counts[booking.status] = status_counts.get(booking.status, 0) + 1
                staff_counts[booking.staff_name] = staff_counts.get(booking.staff_name, 0) + 1
                service_counts[booking.service_name] = service_counts.get(booking.service_name, 0) + 1
            
            print("By Status:")
            for status, count in status_counts.items():
                print(f"  {status}: {count}")
            
            print("\nBy Staff Member:")
            for staff, count in sorted(staff_counts.items()):
                print(f"  {staff}: {count}")
            
            print("\nBy Service:")
            for service, count in sorted(service_counts.items()):
                print(f"  {service}: {count}")
            
            # Revenue calculation
            total_revenue = sum(booking.amount_charged or 0 for booking in bookings)
            paid_revenue = sum(booking.amount_charged or 0 for booking in bookings if booking.payment_status == 'paid')
            
            print(f"\n💰 Revenue:")
            print(f"  Total Revenue: ${total_revenue:.2f}")
            print(f"  Paid Revenue: ${paid_revenue:.2f}")
            print(f"  Pending Revenue: ${total_revenue - paid_revenue:.2f}")
            
        except Exception as e:
            print(f"❌ Error checking UnakiBooking data: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_unaki_booking_data()
