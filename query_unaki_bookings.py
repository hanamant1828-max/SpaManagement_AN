
#!/usr/bin/env python3
"""
Query all records from the UnakiBooking table
"""

from app import app, db
from models import UnakiBooking
from datetime import datetime

def query_all_unaki_bookings():
    """Query and display all UnakiBooking records"""
    
    with app.app_context():
        try:
            print("🔍 Querying all UnakiBooking records...")
            
            # Get all bookings ordered by date and time
            bookings = UnakiBooking.query.order_by(
                UnakiBooking.appointment_date.desc(),
                UnakiBooking.start_time.desc()
            ).all()
            
            print(f"📊 Found {len(bookings)} total bookings in the database\n")
            
            if not bookings:
                print("❌ No bookings found in the UnakiBooking table")
                return
            
            # Display header
            print("=" * 120)
            print(f"{'ID':<4} {'Client Name':<20} {'Phone':<15} {'Staff':<15} {'Service':<25} {'Date':<12} {'Time':<12} {'Status':<12} {'Price':<8}")
            print("=" * 120)
            
            # Display each booking
            for booking in bookings:
                time_range = f"{booking.start_time.strftime('%H:%M')}-{booking.end_time.strftime('%H:%M')}"
                
                print(f"{booking.id:<4} {booking.client_name[:19]:<20} {booking.client_phone or 'N/A':<15} "
                      f"{booking.staff_name[:14]:<15} {booking.service_name[:24]:<25} "
                      f"{booking.appointment_date.strftime('%Y-%m-%d'):<12} {time_range:<12} "
                      f"{booking.status:<12} ₹{booking.service_price or 0:<7.1f}")
            
            print("=" * 120)
            
            # Summary statistics
            print(f"\n📈 Summary Statistics:")
            print(f"   Total Bookings: {len(bookings)}")
            
            # Count by status
            status_counts = {}
            total_revenue = 0
            
            for booking in bookings:
                status = booking.status
                status_counts[status] = status_counts.get(status, 0) + 1
                if booking.service_price:
                    total_revenue += booking.service_price
            
            print(f"   Total Revenue: ₹{total_revenue:,.2f}")
            print(f"\n📋 Status Breakdown:")
            for status, count in status_counts.items():
                print(f"   {status.title()}: {count}")
            
            # Recent bookings
            recent_bookings = [b for b in bookings if b.appointment_date >= datetime.now().date()]
            print(f"\n📅 Upcoming/Recent Bookings: {len(recent_bookings)}")
            
            return bookings
            
        except Exception as e:
            print(f"❌ Error querying UnakiBooking table: {e}")
            return None

def query_bookings_by_date(date_str):
    """Query bookings for a specific date (YYYY-MM-DD format)"""
    
    with app.app_context():
        try:
            from datetime import datetime
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            bookings = UnakiBooking.query.filter_by(
                appointment_date=target_date
            ).order_by(UnakiBooking.start_time).all()
            
            print(f"\n🗓️  Bookings for {date_str}:")
            print(f"   Found {len(bookings)} bookings")
            
            for booking in bookings:
                time_range = f"{booking.start_time.strftime('%H:%M')}-{booking.end_time.strftime('%H:%M')}"
                print(f"   {booking.client_name} - {booking.service_name} ({time_range}) with {booking.staff_name}")
            
            return bookings
            
        except Exception as e:
            print(f"❌ Error querying bookings by date: {e}")
            return None

def query_bookings_by_status(status):
    """Query bookings by status"""
    
    with app.app_context():
        try:
            bookings = UnakiBooking.query.filter_by(status=status).all()
            
            print(f"\n📋 Bookings with status '{status}':")
            print(f"   Found {len(bookings)} bookings")
            
            for booking in bookings:
                print(f"   {booking.client_name} - {booking.service_name} on {booking.appointment_date}")
            
            return bookings
            
        except Exception as e:
            print(f"❌ Error querying bookings by status: {e}")
            return None

if __name__ == "__main__":
    print("🚀 UnakiBooking Database Query Tool")
    print("=" * 50)
    
    # Query all bookings
    all_bookings = query_all_unaki_bookings()
    
    # Example queries
    if all_bookings:
        print(f"\n🔍 Additional Query Examples:")
        
        # Query today's bookings
        today = datetime.now().strftime('%Y-%m-%d')
        query_bookings_by_date(today)
        
        # Query confirmed bookings
        query_bookings_by_status('confirmed')
        
        # Query scheduled bookings
        query_bookings_by_status('scheduled')
