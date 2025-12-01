
"""
Add sample appointments for Bharatiiiii Yallureeee (Customer ID: 128)
"""
from app import app, db
from models import Customer, Appointment, Service, User
from datetime import datetime, timedelta
import random

def add_appointments_for_bharati():
    """Add appointments for Bharatiiiii Yallureeee"""
    with app.app_context():
        # Get the customer
        customer = Customer.query.get(128)
        if not customer:
            print("❌ Customer with ID 128 not found!")
            return
        
        print(f"✅ Found customer: {customer.full_name}")
        
        # Get active services
        services = Service.query.filter_by(is_active=True).all()
        if not services:
            print("❌ No active services found!")
            return
        
        print(f"✅ Found {len(services)} active services")
        
        # Get active staff members
        staff_members = User.query.filter(
            User.role.in_(['staff', 'manager', 'admin']),
            User.is_active == True
        ).all()
        
        if not staff_members:
            print("❌ No active staff members found!")
            return
        
        print(f"✅ Found {len(staff_members)} active staff members")
        
        # Create appointments for today and future dates
        appointments_data = [
            {
                'offset_days': 0,
                'hour': 14,
                'minute': 0,
                'status': 'scheduled',
                'notes': 'Regular appointment - Face recognition check-in'
            },
            {
                'offset_days': 0,
                'hour': 16,
                'minute': 30,
                'status': 'confirmed',
                'notes': 'Confirmed via face recognition'
            },
            {
                'offset_days': 1,
                'hour': 10,
                'minute': 0,
                'status': 'scheduled',
                'notes': 'Tomorrow appointment'
            },
            {
                'offset_days': 2,
                'hour': 15,
                'minute': 0,
                'status': 'scheduled',
                'notes': 'Weekend appointment'
            },
            {
                'offset_days': -1,
                'hour': 11,
                'minute': 0,
                'status': 'completed',
                'notes': 'Completed appointment from yesterday'
            },
            {
                'offset_days': -2,
                'hour': 13,
                'minute': 30,
                'status': 'completed',
                'notes': 'Previous visit - satisfied customer'
            }
        ]
        
        created_count = 0
        
        for apt_data in appointments_data:
            # Select random service and staff
            service = random.choice(services)
            staff = random.choice(staff_members)
            
            # Calculate appointment date/time
            appointment_datetime = datetime.now() + timedelta(days=apt_data['offset_days'])
            appointment_datetime = appointment_datetime.replace(
                hour=apt_data['hour'],
                minute=apt_data['minute'],
                second=0,
                microsecond=0
            )
            
            # Calculate end time based on service duration
            end_time = appointment_datetime + timedelta(minutes=service.duration)
            
            # Create appointment
            appointment = Appointment(
                client_id=customer.id,
                service_id=service.id,
                staff_id=staff.id,
                appointment_date=appointment_datetime,
                end_time=end_time,
                status=apt_data['status'],
                notes=apt_data['notes'],
                amount=service.price,
                payment_status='paid' if apt_data['status'] == 'completed' else 'pending',
                booking_source='manual',
                created_at=datetime.now()
            )
            
            db.session.add(appointment)
            created_count += 1
            
            print(f"✅ Created {apt_data['status']} appointment: {service.name} on {appointment_datetime.strftime('%Y-%m-%d %I:%M %p')}")
        
        # Commit all appointments
        db.session.commit()
        
        print(f"\n🎉 Successfully created {created_count} appointments for {customer.full_name}")
        print(f"📅 Appointments include:")
        print(f"   - 2 for today (scheduled & confirmed)")
        print(f"   - 2 for future dates")
        print(f"   - 2 completed appointments (past dates)")
        
        # Update customer's last visit date
        customer.last_visit = datetime.now() - timedelta(days=1)
        db.session.commit()
        
        print(f"✅ Updated customer's last visit date")

if __name__ == '__main__':
    add_appointments_for_bharati()
