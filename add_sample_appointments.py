
#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta, date, time
from app import app, db
from models import Appointment, Customer, Service, User

def add_sample_appointments():
    """Add sample appointments to demonstrate booking functionality"""
    
    with app.app_context():
        print("Adding sample appointments...")
        
        # Get existing customers, services, and staff
        customers = Customer.query.filter_by(is_active=True).all()
        services = Service.query.filter_by(is_active=True).all()
        staff = User.query.filter(User.role.in_(['staff', 'manager', 'admin'])).all()
        
        if not customers:
            print("❌ No customers found. Please run add_sample_customers.py first")
            return
        
        if not services:
            print("❌ No services found. Please run add_sample_services.py first")
            return
        
        if not staff:
            print("❌ No staff found. Please create staff members first")
            return
        
        print(f"Found {len(customers)} customers, {len(services)} services, {len(staff)} staff")
        
        # Clear existing appointments to avoid duplicates
        existing_count = Appointment.query.count()
        if existing_count > 0:
            print(f"Clearing {existing_count} existing appointments...")
            Appointment.query.delete()
            db.session.commit()
        
        # Sample appointments for today and upcoming days
        base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        sample_appointments = [
            # Today's appointments
            {
                'client_id': customers[0].id,
                'service_id': services[0].id,  # Swedish Massage
                'staff_id': staff[0].id,
                'appointment_date': base_date,
                'status': 'confirmed',
                'notes': 'Regular customer - prefers medium pressure',
                'amount': services[0].price,
                'payment_status': 'paid'
            },
            {
                'client_id': customers[1].id,
                'service_id': services[5].id,  # Classic European Facial
                'staff_id': staff[0].id if len(staff) == 1 else staff[1].id,
                'appointment_date': base_date + timedelta(hours=2),
                'status': 'scheduled',
                'notes': 'First time client',
                'amount': services[5].price,
                'payment_status': 'pending'
            },
            {
                'client_id': customers[2].id,
                'service_id': services[10].id,  # Haircut & Blow Dry
                'staff_id': staff[0].id,
                'appointment_date': base_date + timedelta(hours=4),
                'status': 'confirmed',
                'notes': 'Wedding preparation',
                'amount': services[10].price,
                'payment_status': 'paid'
            },
            
            # Tomorrow's appointments
            {
                'client_id': customers[3].id,
                'service_id': services[2].id,  # Hot Stone Massage
                'staff_id': staff[0].id,
                'appointment_date': base_date + timedelta(days=1, hours=1),
                'status': 'scheduled',
                'notes': 'Client has back issues',
                'amount': services[2].price,
                'payment_status': 'pending'
            },
            {
                'client_id': customers[4].id,
                'service_id': services[15].id,  # Classic Manicure
                'staff_id': staff[0].id if len(staff) == 1 else staff[1].id,
                'appointment_date': base_date + timedelta(days=1, hours=3),
                'status': 'confirmed',
                'notes': 'Regular weekly appointment',
                'amount': services[15].price,
                'payment_status': 'paid'
            },
            {
                'client_id': customers[0].id,
                'service_id': services[6].id,  # Anti-Aging Facial
                'staff_id': staff[0].id,
                'appointment_date': base_date + timedelta(days=1, hours=5),
                'status': 'scheduled',
                'notes': 'Special occasion preparation',
                'amount': services[6].price,
                'payment_status': 'pending'
            },
            
            # Day after tomorrow
            {
                'client_id': customers[1].id,
                'service_id': services[4].id,  # Couples Massage
                'staff_id': staff[0].id,
                'appointment_date': base_date + timedelta(days=2, hours=2),
                'status': 'scheduled',
                'notes': 'Anniversary celebration',
                'amount': services[4].price,
                'payment_status': 'pending'
            },
            {
                'client_id': customers[2].id,
                'service_id': services[18].id,  # Spa Pedicure
                'staff_id': staff[0].id if len(staff) == 1 else staff[1].id,
                'appointment_date': base_date + timedelta(days=2, hours=4),
                'status': 'confirmed',
                'notes': 'Summer preparation',
                'amount': services[18].price,
                'payment_status': 'paid'
            },
            
            # Past appointments (completed)
            {
                'client_id': customers[3].id,
                'service_id': services[1].id,  # Deep Tissue Massage
                'staff_id': staff[0].id,
                'appointment_date': base_date - timedelta(days=1),
                'status': 'completed',
                'notes': 'Client was very satisfied',
                'amount': services[1].price,
                'payment_status': 'paid'
            },
            {
                'client_id': customers[4].id,
                'service_id': services[7].id,  # Hydrating Facial
                'staff_id': staff[0].id,
                'appointment_date': base_date - timedelta(days=2, hours=3),
                'status': 'completed',
                'notes': 'Excellent results',
                'amount': services[7].price,
                'payment_status': 'paid'
            }
        ]
        
        # Add appointments
        created_count = 0
        for apt_data in sample_appointments:
            try:
                # Calculate end time based on service duration
                service = Service.query.get(apt_data['service_id'])
                if service:
                    apt_data['end_time'] = apt_data['appointment_date'] + timedelta(minutes=service.duration)
                else:
                    apt_data['end_time'] = apt_data['appointment_date'] + timedelta(hours=1)
                
                # Set timestamps
                apt_data['created_at'] = datetime.utcnow()
                apt_data['updated_at'] = datetime.utcnow()
                
                appointment = Appointment(**apt_data)
                db.session.add(appointment)
                created_count += 1
                
            except Exception as e:
                print(f"❌ Error creating appointment: {e}")
                continue
        
        try:
            db.session.commit()
            print(f"✅ Successfully added {created_count} sample appointments!")
            
            # Show summary
            total_appointments = Appointment.query.count()
            today_appointments = Appointment.query.filter(
                db.func.date(Appointment.appointment_date) == date.today()
            ).count()
            
            confirmed_appointments = Appointment.query.filter_by(status='confirmed').count()
            completed_appointments = Appointment.query.filter_by(status='completed').count()
            
            print(f"\n📊 APPOINTMENT SUMMARY:")
            print(f"  • Total appointments: {total_appointments}")
            print(f"  • Today's appointments: {today_appointments}")
            print(f"  • Confirmed appointments: {confirmed_appointments}")
            print(f"  • Completed appointments: {completed_appointments}")
            
            print(f"\n📅 TODAY'S SCHEDULE:")
            today_apts = Appointment.query.filter(
                db.func.date(Appointment.appointment_date) == date.today()
            ).order_by(Appointment.appointment_date).all()
            
            for apt in today_apts:
                time_str = apt.appointment_date.strftime('%I:%M %p')
                client_name = apt.client.full_name if apt.client else 'Unknown'
                service_name = apt.service.name if apt.service else 'Unknown'
                staff_name = apt.staff.full_name if apt.staff else 'Unknown'
                status_emoji = {
                    'scheduled': '⏰',
                    'confirmed': '✅', 
                    'completed': '🎉',
                    'cancelled': '❌'
                }.get(apt.status, '❓')
                
                print(f"  {status_emoji} {time_str} - {client_name} | {service_name} | {staff_name}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error saving appointments: {e}")

if __name__ == '__main__':
    add_sample_appointments()
