
#!/usr/bin/env python3
"""
Test script to create consecutive bookings for the same staff member
9:00-9:30 (30 min) → 9:30-10:30 (1 hour) → 10:30-11:30 (1 hour)
"""

import requests
import json
from datetime import datetime, date

# Configuration
BASE_URL = "http://0.0.0.0:5000"  # Use 0.0.0.0 for Replit
TODAY = date.today().strftime('%Y-%m-%d')

def create_consecutive_bookings():
    """Create three consecutive bookings for the same staff member"""
    
    # Booking data for consecutive appointments - ALL FOR SAME STAFF (ID 11)
    bookings = [
        {
            "staffId": 11,  # Admin User (same staff for all)
            "clientName": "Sarah Johnson",
            "clientPhone": "+1-555-0301",
            "serviceType": "Express Facial",
            "startTime": "09:00",
            "endTime": "09:30",
            "date": TODAY,
            "notes": "First consecutive booking - 30 minutes"
        },
        {
            "staffId": 11,  # Same staff member
            "clientName": "Michael Chen", 
            "clientPhone": "+1-555-0302",
            "serviceType": "Swedish Massage",
            "startTime": "09:30",
            "endTime": "10:30", 
            "date": TODAY,
            "notes": "Second consecutive booking - 1 hour right after first"
        },
        {
            "staffId": 11,  # Same staff member
            "clientName": "Emma Rodriguez",
            "clientPhone": "+1-555-0303", 
            "serviceType": "Deep Tissue Massage",
            "startTime": "10:30",
            "endTime": "11:30",
            "date": TODAY,
            "notes": "Third consecutive booking - 1 hour after completion of first booking"
        }
    ]
    
    print("🚀 Creating consecutive bookings for the SAME staff member...")
    print(f"📅 Date: {TODAY}")
    print("👥 Staff: Admin User (ID: 11) - ALL THREE BOOKINGS")
    print("\n📋 Booking Sequence:")
    
    created_bookings = []
    
    for i, booking in enumerate(bookings, 1):
        print(f"\n{i}. {booking['startTime']}-{booking['endTime']} - {booking['clientName']} - {booking['serviceType']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/unaki/create-appointment",
                json=booking,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    booking_id = result.get('appointmentId')
                    created_bookings.append(booking_id)
                    print(f"   ✅ SUCCESS - Booking ID: {booking_id}")
                else:
                    print(f"   ❌ FAILED - {result.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP ERROR - Status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Error: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"   ❌ CONNECTION ERROR - {str(e)}")
    
    print(f"\n🎉 RESULTS:")
    print(f"✅ Successfully created {len(created_bookings)} consecutive bookings")
    print(f"📋 Booking IDs: {created_bookings}")
    
    if len(created_bookings) == 3:
        print("\n🔥 PERFECT! All three consecutive bookings created for THE SAME STAFF!")
        print("📊 Your booking sequence is now active:")
        print("   👤 Staff: Admin User (ID: 11)")
        print("   🕘 9:00-9:30 (30 min) - Sarah Johnson - Express Facial ✅")
        print("   🕘 9:30-10:30 (1 hour) - Michael Chen - Swedish Massage ✅") 
        print("   🕘 10:30-11:30 (1 hour) - Emma Rodriguez - Deep Tissue Massage ✅")
        print(f"\n🌐 View in browser: {BASE_URL}/unaki-booking")
        print("\n✨ All bookings are for the SAME staff member with NO GAPS!")
    else:
        print("\n⚠️  Some bookings failed. Check the errors above.")
    
    return created_bookings

if __name__ == "__main__":
    create_consecutive_bookings()
