
"""
Get all bookings done today from the UnakiBooking table
"""
import sqlite3
from datetime import date

# Connect to the database
db_path = 'hanamantdatabase/workspace.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get today's date
today = date.today()
print(f"\n{'='*80}")
print(f"📅 ALL BOOKINGS FOR TODAY: {today.strftime('%Y-%m-%d (%A, %B %d, %Y)')}")
print(f"{'='*80}\n")

# Query all bookings for today
query = """
SELECT 
    id,
    client_name,
    client_phone,
    service_name,
    service_duration,
    service_price,
    staff_name,
    appointment_date,
    start_time,
    end_time,
    status,
    payment_status,
    booking_source,
    booking_method,
    checked_in,
    notes,
    created_at
FROM unaki_bookings
WHERE appointment_date = ?
ORDER BY start_time, staff_name
"""

cursor.execute(query, (today.strftime('%Y-%m-%d'),))
bookings = cursor.fetchall()

if not bookings:
    print("❌ No bookings found for today")
else:
    print(f"✅ Found {len(bookings)} booking(s) for today\n")
    
    for idx, booking in enumerate(bookings, 1):
        (booking_id, client_name, client_phone, service_name, duration, price, 
         staff_name, appt_date, start_time, end_time, status, payment_status,
         booking_source, booking_method, checked_in, notes, created_at) = booking
        
        print(f"\n{'─'*80}")
        print(f"📋 BOOKING #{idx} (ID: {booking_id})")
        print(f"{'─'*80}")
        print(f"👤 Client: {client_name}")
        print(f"📱 Phone: {client_phone or 'N/A'}")
        print(f"💆 Service: {service_name}")
        print(f"⏱️  Duration: {duration} minutes")
        print(f"💰 Price: ₹{price:.2f}")
        print(f"👨‍💼 Staff: {staff_name}")
        print(f"🕐 Time: {start_time} - {end_time}")
        print(f"📊 Status: {status.upper()}")
        print(f"💳 Payment: {payment_status.upper()}")
        print(f"📍 Source: {booking_source}")
        print(f"🔧 Method: {booking_method}")
        print(f"✅ Checked In: {'YES' if checked_in else 'NO'}")
        if notes:
            print(f"📝 Notes: {notes}")
        print(f"🕒 Created: {created_at}")

# Summary by status
print(f"\n{'='*80}")
print("📊 SUMMARY BY STATUS")
print(f"{'='*80}")

cursor.execute("""
    SELECT status, COUNT(*) as count
    FROM unaki_bookings
    WHERE appointment_date = ?
    GROUP BY status
""", (today.strftime('%Y-%m-%d'),))

status_summary = cursor.fetchall()
for status, count in status_summary:
    print(f"  {status.upper()}: {count}")

# Summary by booking source
print(f"\n{'='*80}")
print("📊 SUMMARY BY BOOKING SOURCE")
print(f"{'='*80}")

cursor.execute("""
    SELECT booking_source, COUNT(*) as count
    FROM unaki_bookings
    WHERE appointment_date = ?
    GROUP BY booking_source
""", (today.strftime('%Y-%m-%d'),))

source_summary = cursor.fetchall()
for source, count in source_summary:
    print(f"  {source.upper()}: {count}")

# Summary by staff
print(f"\n{'='*80}")
print("📊 SUMMARY BY STAFF MEMBER")
print(f"{'='*80}")

cursor.execute("""
    SELECT staff_name, COUNT(*) as count, SUM(service_price) as total_revenue
    FROM unaki_bookings
    WHERE appointment_date = ?
    GROUP BY staff_name
    ORDER BY count DESC
""", (today.strftime('%Y-%m-%d'),))

staff_summary = cursor.fetchall()
for staff, count, revenue in staff_summary:
    print(f"  {staff}: {count} booking(s), ₹{revenue:.2f} revenue")

# Total revenue
cursor.execute("""
    SELECT 
        SUM(service_price) as total_revenue,
        COUNT(*) as total_bookings
    FROM unaki_bookings
    WHERE appointment_date = ?
""", (today.strftime('%Y-%m-%d'),))

total_revenue, total_bookings = cursor.fetchone()
print(f"\n{'='*80}")
print(f"💰 TOTAL REVENUE: ₹{total_revenue:.2f}")
print(f"📋 TOTAL BOOKINGS: {total_bookings}")
print(f"{'='*80}\n")

conn.close()
