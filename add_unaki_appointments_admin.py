
"""
Add sample appointments for admin user in Unaki booking system
"""
import os
import sys
from datetime import datetime, date, time, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import UnakiBooking, User, Service, Customer

def add_sample_unaki_appointments():
    """Add sample appointments for admin user in Unaki booking system"""
    with app.app_context():
        try:
            # Get admin user (assuming ID 11 based on logs)
            admin_user = User.query.filter_by(role='admin').first()
            if not admin_user:
                print("❌ Admin user not found")
                return
            
            print(f"✅ Found admin user: {admin_user.first_name} {admin_user.last_name} (ID: {admin_user.id})")
            
            # Get some services for appointments
            services = Service.query.filter_by(is_active=True).limit(5).all()
            if not services:
                print("❌ No active services found")
                return
            
            print(f"✅ Found {len(services)} active services")
            
            # Get some customers
            customers = Customer.query.filter_by(is_active=True).limit(10).all()
            if not customers:
                print("❌ No active customers found")
                return
            
            print(f"✅ Found {len(customers)} active customers")
            
            # Sample appointment data for today and next few days
            today = date.today()
            sample_appointments = [
                {
                    'date': today,
                    'time': '10:00',
                    'duration': 60,
                    'service': 'Deep Cleansing Facial',
                    'client': 'Sarah Johnson',
                    'phone': '+1-555-0101'
                },
                {
                    'date': today,
                    'time': '11:30',
                    'duration': 90,
                    'service': 'Swedish Massage',
                    'client': 'Michael Chen',
                    'phone': '+1-555-0102'
                },
                {
                    'date': today,
                    'time': '14:00',
                    'duration': 45,
                    'service': 'Classic Manicure',
                    'client': 'Emily Rodriguez',
                    'phone': '+1-555-0103'
                },
                {
                    'date': today + timedelta(days=1),
                    'time': '09:00',
                    'duration': 120,
                    'service': 'Hot Stone Massage',
                    'client': 'David Wilson',
                    'phone': '+1-555-0104'
                },
                {
                    'date': today + timedelta(days=1),
                    'time': '15:30',
                    'duration': 75,
                    'service': 'Anti-Aging Facial',
                    'client': 'Lisa Garcia',
                    'phone': '+1-555-0105'
                },
                {
                    'date': today + timedelta(days=2),
                    'time': '10:30',
                    'duration': 30,
                    'service': 'Eyebrow Threading',
                    'client': 'Jessica Martinez',
                    'phone': '+1-555-0106'
                },
                {
                    'date': today + timedelta(days=2),
                    'time': '13:00',
                    'duration': 105,
                    'service': 'Full Body Massage',
                    'client': 'Robert Taylor',
                    'phone': '+1-555-0107'
                }
            ]
            
            appointments_created = 0
            
            for apt_data in sample_appointments:
                try:
                    # Parse times
                    start_time = datetime.strptime(apt_data['time'], '%H:%M').time()
                    start_datetime = datetime.combine(apt_data['date'], start_time)
                    end_datetime = start_datetime + timedelta(minutes=apt_data['duration'])
                    
                    # Check if appointment already exists for this time slot
                    existing = UnakiBooking.query.filter_by(
                        staff_id=admin_user.id,
                        appointment_date=apt_data['date'],
                        start_time=start_time
                    ).first()
                    
                    if existing:
                        print(f"⚠️ Appointment already exists for {apt_data['date']} at {apt_data['time']}")
                        continue
                    
                    # Try to find existing customer or use first available
                    customer = None
                    for c in customers:
                        if c.full_name == apt_data['client']:
                            customer = c
                            break
                    
                    if not customer and customers:
                        customer = customers[appointments_created % len(customers)]
                    
                    # Get service price (use first service or default)
                    service_price = services[0].price if services else 100.0
                    
                    # Create appointment
                    appointment = UnakiBooking(
                        client_id=customer.id if customer else None,
                        client_name=apt_data['client'],
                        client_phone=apt_data['phone'],
                        client_email=f"{apt_data['client'].lower().replace(' ', '.')}@example.com",
                        staff_id=admin_user.id,
                        staff_name=admin_user.full_name,
                        service_name=apt_data['service'],
                        service_duration=apt_data['duration'],
                        service_price=service_price,
                        appointment_date=apt_data['date'],
                        start_time=start_time,
                        end_time=end_datetime.time(),
                        status='scheduled',
                        notes=f'Sample appointment for {apt_data["client"]}',
                        booking_source='unaki_system',
                        booking_method='admin_created',
                        amount_charged=service_price,
                        payment_status='pending'
                    )
                    
                    db.session.add(appointment)
                    appointments_created += 1
                    
                    print(f"✅ Created appointment: {apt_data['client']} - {apt_data['service']} on {apt_data['date']} at {apt_data['time']}")
                    
                except Exception as e:
                    print(f"❌ Error creating appointment for {apt_data['client']}: {e}")
                    continue
            
            # Commit all appointments
            db.session.commit()
            print(f"\n🎉 Successfully created {appointments_created} appointments for admin user!")
            
            # Show summary
            total_unaki_appointments = UnakiBooking.query.filter_by(staff_id=admin_user.id).count()
            print(f"📊 Total appointments for admin user: {total_unaki_appointments}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding appointments: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Adding sample appointments for admin user in Unaki booking system...")
    add_sample_unaki_appointments()
