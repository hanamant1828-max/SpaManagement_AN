
#!/usr/bin/env python3
"""
Setup demo data for Unaki booking system
"""
from app import app, db
from models import UnakiStaff, UnakiAppointment, UnakiBreak, Service, Customer
from datetime import datetime, date, time, timedelta
import random

def setup_unaki_demo_data():
    """Setup demo data for Unaki booking system"""
    with app.app_context():
        print("🌸 Setting up Unaki Booking System demo data...")
        
        # Create demo staff if they don't exist
        staff_data = [
            {'name': 'Priya Sharma', 'specialty': 'Facial Treatments'},
            {'name': 'Anita Patel', 'specialty': 'Body Massage'},
            {'name': 'Meera Singh', 'specialty': 'Hair Treatments'},
            {'name': 'Kavya Reddy', 'specialty': 'Nail Art'},
            {'name': 'Sneha Gupta', 'specialty': 'Wellness Therapy'}
        ]
        
        for staff_info in staff_data:
            existing_staff = UnakiStaff.query.filter_by(name=staff_info['name']).first()
            if not existing_staff:
                staff = UnakiStaff(
                    name=staff_info['name'],
                    specialty=staff_info['specialty'],
                    active=True
                )
                db.session.add(staff)
                print(f"✅ Added staff: {staff_info['name']} - {staff_info['specialty']}")
        
        # Create demo services if they don't exist
        services_data = [
            {'name': 'Deep Cleansing Facial', 'duration': 60, 'price': 1500, 'category': 'Facial'},
            {'name': 'Aromatherapy Massage', 'duration': 90, 'price': 2500, 'category': 'Massage'},
            {'name': 'Hair Spa Treatment', 'duration': 75, 'price': 1800, 'category': 'Hair'},
            {'name': 'Manicure & Pedicure', 'duration': 120, 'price': 1200, 'category': 'Nails'},
            {'name': 'Hot Stone Therapy', 'duration': 75, 'price': 2200, 'category': 'Therapy'},
            {'name': 'Gold Facial', 'duration': 90, 'price': 3000, 'category': 'Facial'},
            {'name': 'Swedish Massage', 'duration': 60, 'price': 2000, 'category': 'Massage'},
            {'name': 'Hair Color & Style', 'duration': 150, 'price': 2800, 'category': 'Hair'},
            {'name': 'Gel Nail Extensions', 'duration': 90, 'price': 1500, 'category': 'Nails'},
            {'name': 'Reflexology', 'duration': 45, 'price': 1000, 'category': 'Therapy'}
        ]
        
        for service_info in services_data:
            existing_service = Service.query.filter_by(name=service_info['name']).first()
            if not existing_service:
                service = Service(
                    name=service_info['name'],
                    duration=service_info['duration'],
                    price=service_info['price'],
                    category=service_info['category'],
                    description=f"Professional {service_info['name'].lower()} service",
                    is_active=True
                )
                db.session.add(service)
                print(f"✅ Added service: {service_info['name']} - {service_info['duration']} min - ₹{service_info['price']}")
        
        # Create demo customers if they don't exist
        customers_data = [
            {'first_name': 'Aisha', 'last_name': 'Khan', 'phone': '9876543210', 'email': 'aisha.khan@email.com'},
            {'first_name': 'Rhea', 'last_name': 'Sharma', 'phone': '9876543211', 'email': 'rhea.sharma@email.com'},
            {'first_name': 'Pooja', 'last_name': 'Patel', 'phone': '9876543212', 'email': 'pooja.patel@email.com'},
            {'first_name': 'Neha', 'last_name': 'Singh', 'phone': '9876543213', 'email': 'neha.singh@email.com'},
            {'first_name': 'Sana', 'last_name': 'Gupta', 'phone': '9876543214', 'email': 'sana.gupta@email.com'},
            {'first_name': 'Divya', 'last_name': 'Reddy', 'phone': '9876543215', 'email': 'divya.reddy@email.com'},
            {'first_name': 'Kritika', 'last_name': 'Jain', 'phone': '9876543216', 'email': 'kritika.jain@email.com'},
            {'first_name': 'Riya', 'last_name': 'Verma', 'phone': '9876543217', 'email': 'riya.verma@email.com'}
        ]
        
        for customer_info in customers_data:
            existing_customer = Customer.query.filter_by(phone=customer_info['phone']).first()
            if not existing_customer:
                customer = Customer(
                    first_name=customer_info['first_name'],
                    last_name=customer_info['last_name'],
                    phone=customer_info['phone'],
                    email=customer_info['email'],
                    gender='female',
                    is_active=True,
                    total_visits=random.randint(1, 10),
                    total_spent=random.uniform(1000, 10000)
                )
                db.session.add(customer)
                print(f"✅ Added customer: {customer_info['first_name']} {customer_info['last_name']} - {customer_info['phone']}")
        
        db.session.commit()
        
        # Create demo appointments for today and tomorrow
        staff_list = UnakiStaff.query.filter_by(active=True).all()
        service_list = Service.query.filter_by(is_active=True).all()
        customer_list = Customer.query.filter_by(is_active=True).all()
        
        if staff_list and service_list and customer_list:
            today = date.today()
            tomorrow = today + timedelta(days=1)
            
            # Clear existing demo appointments for today and tomorrow
            UnakiAppointment.query.filter(
                UnakiAppointment.appointment_date.in_([today, tomorrow])
            ).delete()
            
            # Create appointments for today
            appointment_times = [
                time(9, 0), time(10, 30), time(12, 0), time(14, 0), time(15, 30)
            ]
            
            for i, appointment_time in enumerate(appointment_times):
                if i < len(staff_list) and i < len(service_list) and i < len(customer_list):
                    staff = staff_list[i]
                    service = service_list[i]
                    customer = customer_list[i]
                    
                    start_datetime = datetime.combine(today, appointment_time)
                    end_datetime = start_datetime + timedelta(minutes=service.duration)
                    
                    appointment = UnakiAppointment(
                        staff_id=staff.id,
                        client_name=f"{customer.first_name} {customer.last_name}",
                        service=service.name,
                        start_time=start_datetime,
                        end_time=end_datetime,
                        phone=customer.phone,
                        notes=f"Regular {service.name.lower()} appointment",
                        appointment_date=today
                    )
                    db.session.add(appointment)
            
            # Create appointments for tomorrow
            tomorrow_times = [
                time(10, 0), time(11, 30), time(13, 0), time(15, 0), time(16, 30)
            ]
            
            for i, appointment_time in enumerate(tomorrow_times):
                if i < len(staff_list) and i < len(service_list) and i < len(customer_list):
                    staff = staff_list[(i + 1) % len(staff_list)]
                    service = service_list[(i + 2) % len(service_list)]
                    customer = customer_list[(i + 1) % len(customer_list)]
                    
                    start_datetime = datetime.combine(tomorrow, appointment_time)
                    end_datetime = start_datetime + timedelta(minutes=service.duration)
                    
                    appointment = UnakiAppointment(
                        staff_id=staff.id,
                        client_name=f"{customer.first_name} {customer.last_name}",
                        service=service.name,
                        start_time=start_datetime,
                        end_time=end_datetime,
                        phone=customer.phone,
                        notes=f"Scheduled {service.name.lower()}",
                        appointment_date=tomorrow
                    )
                    db.session.add(appointment)
            
            # Create some breaks
            break_times = [time(13, 0), time(13, 30), time(14, 0)]
            break_types = ['Lunch Break', 'Tea Break', 'Rest Break']
            
            for i, (break_time, break_type) in enumerate(zip(break_times, break_types)):
                if i < len(staff_list):
                    staff = staff_list[i]
                    
                    start_datetime = datetime.combine(today, break_time)
                    end_datetime = start_datetime + timedelta(minutes=30)
                    
                    break_entry = UnakiBreak(
                        staff_id=staff.id,
                        break_type=break_type,
                        start_time=start_datetime,
                        end_time=end_datetime,
                        break_date=today,
                        notes=f"Scheduled {break_type.lower()}"
                    )
                    db.session.add(break_entry)
            
            db.session.commit()
            print(f"✅ Created demo appointments and breaks for {today} and {tomorrow}")
        
        print("\n🎉 Unaki Booking System demo data setup complete!")
        print("📱 You can now test the multiple booking system with:")
        print("   - Search clients by phone number")
        print("   - Add multiple services for the same client")
        print("   - View the schedule grid with appointments")
        print("   - Create new clients if needed")

if __name__ == '__main__':
    setup_unaki_demo_data()
