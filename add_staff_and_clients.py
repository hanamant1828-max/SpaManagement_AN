from app import app, db
from models import User, Customer
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
import random

def add_staff_and_clients():
    with app.app_context():
        staff_data = [
            {"first_name": "Priya", "last_name": "Sharma", "username": "priya.sharma", "email": "priya.sharma@spa.com", "phone": "9876543210", "designation": "Senior Therapist", "department": "Massage"},
            {"first_name": "Rajesh", "last_name": "Kumar", "username": "rajesh.kumar", "email": "rajesh.kumar@spa.com", "phone": "9876543211", "designation": "Facial Specialist", "department": "Facial"},
            {"first_name": "Anita", "last_name": "Desai", "username": "anita.desai", "email": "anita.desai@spa.com", "phone": "9876543212", "designation": "Hair Stylist", "department": "Hair"},
            {"first_name": "Vikram", "last_name": "Singh", "username": "vikram.singh", "email": "vikram.singh@spa.com", "phone": "9876543213", "designation": "Massage Therapist", "department": "Massage"},
            {"first_name": "Sneha", "last_name": "Patel", "username": "sneha.patel", "email": "sneha.patel@spa.com", "phone": "9876543214", "designation": "Nail Technician", "department": "Nails"},
            {"first_name": "Amit", "last_name": "Verma", "username": "amit.verma", "email": "amit.verma@spa.com", "phone": "9876543215", "designation": "Spa Therapist", "department": "Spa"},
            {"first_name": "Kavya", "last_name": "Reddy", "username": "kavya.reddy", "email": "kavya.reddy@spa.com", "phone": "9876543216", "designation": "Beautician", "department": "Beauty"},
            {"first_name": "Rohit", "last_name": "Mehta", "username": "rohit.mehta", "email": "rohit.mehta@spa.com", "phone": "9876543217", "designation": "Massage Therapist", "department": "Massage"},
            {"first_name": "Neha", "last_name": "Gupta", "username": "neha.gupta", "email": "neha.gupta@spa.com", "phone": "9876543218", "designation": "Facial Expert", "department": "Facial"},
            {"first_name": "Arjun", "last_name": "Nair", "username": "arjun.nair", "email": "arjun.nair@spa.com", "phone": "9876543219", "designation": "Senior Stylist", "department": "Hair"}
        ]

        client_data = [
            {"first_name": "Meera", "last_name": "Kapoor", "email": "meera.kapoor@gmail.com", "phone": "8765432100", "gender": "female"},
            {"first_name": "Sanjay", "last_name": "Agarwal", "email": "sanjay.agarwal@gmail.com", "phone": "8765432101", "gender": "male"},
            {"first_name": "Divya", "last_name": "Iyer", "email": "divya.iyer@gmail.com", "phone": "8765432102", "gender": "female"},
            {"first_name": "Karan", "last_name": "Malhotra", "email": "karan.malhotra@gmail.com", "phone": "8765432103", "gender": "male"},
            {"first_name": "Pooja", "last_name": "Joshi", "email": "pooja.joshi@gmail.com", "phone": "8765432104", "gender": "female"},
            {"first_name": "Rahul", "last_name": "Chopra", "email": "rahul.chopra@gmail.com", "phone": "8765432105", "gender": "male"},
            {"first_name": "Simran", "last_name": "Bhatia", "email": "simran.bhatia@gmail.com", "phone": "8765432106", "gender": "female"},
            {"first_name": "Aditya", "last_name": "Bansal", "email": "aditya.bansal@gmail.com", "phone": "8765432107", "gender": "male"},
            {"first_name": "Ritu", "last_name": "Saxena", "email": "ritu.saxena@gmail.com", "phone": "8765432108", "gender": "female"},
            {"first_name": "Varun", "last_name": "Khanna", "email": "varun.khanna@gmail.com", "phone": "8765432109", "gender": "male"}
        ]

        print("Adding 10 staff members...")
        staff_count = 0
        for i, staff in enumerate(staff_data, 1):
            existing_staff = User.query.filter_by(username=staff['username']).first()
            if not existing_staff:
                new_staff = User(
                    username=staff['username'],
                    email=staff['email'],
                    first_name=staff['first_name'],
                    last_name=staff['last_name'],
                    phone=staff['phone'],
                    designation=staff['designation'],
                    department=staff['department'],
                    role='staff',
                    is_active=True,
                    employee_id=f"EMP{1000 + i}",
                    staff_code=f"ST{1000 + i}",
                    hire_date=date.today() - timedelta(days=random.randint(30, 365)),
                    date_of_joining=date.today() - timedelta(days=random.randint(30, 365)),
                    commission_rate=random.randint(10, 30),
                    hourly_rate=random.randint(200, 500),
                    gender='male' if staff['first_name'] in ['Rajesh', 'Vikram', 'Amit', 'Rohit', 'Arjun'] else 'female'
                )
                new_staff.password_hash = generate_password_hash('staff123')
                db.session.add(new_staff)
                staff_count += 1
                print(f"✅ Added staff: {staff['first_name']} {staff['last_name']} (Username: {staff['username']})")
            else:
                print(f"⚠️ Staff already exists: {staff['username']}")

        print(f"\nAdding 10 clients...")
        client_count = 0
        for client in client_data:
            existing_client = Customer.query.filter_by(phone=client['phone']).first()
            if not existing_client:
                new_client = Customer(
                    first_name=client['first_name'],
                    last_name=client['last_name'],
                    email=client['email'],
                    phone=client['phone'],
                    gender=client['gender'],
                    date_of_birth=date.today() - timedelta(days=random.randint(7300, 14600)),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 180)),
                    total_visits=random.randint(0, 5),
                    total_spent=random.uniform(500, 5000),
                    is_active=True
                )
                db.session.add(new_client)
                client_count += 1
                print(f"✅ Added client: {client['first_name']} {client['last_name']} (Phone: {client['phone']})")
            else:
                print(f"⚠️ Client already exists: {client['phone']}")

        db.session.commit()
        print(f"\n🎉 Successfully added {staff_count} staff members and {client_count} clients!")
        print(f"\n📊 Database Summary:")
        print(f"   Total Staff: {User.query.filter_by(role='staff').count()}")
        print(f"   Total Clients: {Customer.query.count()}")

if __name__ == "__main__":
    add_staff_and_clients()
