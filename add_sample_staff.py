
#!/usr/bin/env python3
"""
Add 10 sample staff members to the database
"""

from app import app, db
from models import User, Role, Department
from werkzeug.security import generate_password_hash
from datetime import date, datetime, time
import random

def add_sample_staff():
    """Add 10 sample staff members with comprehensive data"""
    
    with app.app_context():
        # Sample staff data
        staff_data = [
            {
                'username': 'sarah_johnson',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'email': 'sarah.johnson@spa.com',
                'phone': '+1-555-0101',
                'role': 'staff',
                'designation': 'Senior Hair Stylist',
                'gender': 'female',
                'commission_percentage': 15.0,
                'hourly_rate': 25.0
            },
            {
                'username': 'mike_wilson',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'email': 'mike.wilson@spa.com',
                'phone': '+1-555-0102',
                'role': 'staff',
                'designation': 'Massage Therapist',
                'gender': 'male',
                'commission_percentage': 12.0,
                'hourly_rate': 30.0
            },
            {
                'username': 'emily_davis',
                'first_name': 'Emily',
                'last_name': 'Davis',
                'email': 'emily.davis@spa.com',
                'phone': '+1-555-0103',
                'role': 'manager',
                'designation': 'Spa Manager',
                'gender': 'female',
                'commission_percentage': 20.0,
                'hourly_rate': 35.0
            },
            {
                'username': 'david_brown',
                'first_name': 'David',
                'last_name': 'Brown',
                'email': 'david.brown@spa.com',
                'phone': '+1-555-0104',
                'role': 'staff',
                'designation': 'Nail Technician',
                'gender': 'male',
                'commission_percentage': 10.0,
                'hourly_rate': 20.0
            },
            {
                'username': 'lisa_garcia',
                'first_name': 'Lisa',
                'last_name': 'Garcia',
                'email': 'lisa.garcia@spa.com',
                'phone': '+1-555-0105',
                'role': 'staff',
                'designation': 'Esthetician',
                'gender': 'female',
                'commission_percentage': 18.0,
                'hourly_rate': 28.0
            },
            {
                'username': 'robert_miller',
                'first_name': 'Robert',
                'last_name': 'Miller',
                'email': 'robert.miller@spa.com',
                'phone': '+1-555-0106',
                'role': 'cashier',
                'designation': 'Front Desk Cashier',
                'gender': 'male',
                'commission_percentage': 5.0,
                'hourly_rate': 18.0
            },
            {
                'username': 'jessica_anderson',
                'first_name': 'Jessica',
                'last_name': 'Anderson',
                'email': 'jessica.anderson@spa.com',
                'phone': '+1-555-0107',
                'role': 'staff',
                'designation': 'Hair Color Specialist',
                'gender': 'female',
                'commission_percentage': 16.0,
                'hourly_rate': 32.0
            },
            {
                'username': 'chris_taylor',
                'first_name': 'Chris',
                'last_name': 'Taylor',
                'email': 'chris.taylor@spa.com',
                'phone': '+1-555-0108',
                'role': 'staff',
                'designation': 'Barber',
                'gender': 'male',
                'commission_percentage': 14.0,
                'hourly_rate': 24.0
            },
            {
                'username': 'amanda_white',
                'first_name': 'Amanda',
                'last_name': 'White',
                'email': 'amanda.white@spa.com',
                'phone': '+1-555-0109',
                'role': 'staff',
                'designation': 'Makeup Artist',
                'gender': 'female',
                'commission_percentage': 17.0,
                'hourly_rate': 26.0
            },
            {
                'username': 'kevin_lee',
                'first_name': 'Kevin',
                'last_name': 'Lee',
                'email': 'kevin.lee@spa.com',
                'phone': '+1-555-0110',
                'role': 'staff',
                'designation': 'Fitness Trainer',
                'gender': 'male',
                'commission_percentage': 13.0,
                'hourly_rate': 22.0
            }
        ]
        
        print("Adding 10 sample staff members...")
        
        # Get or create basic roles if they don't exist
        roles = ['admin', 'manager', 'staff', 'cashier']
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(
                    name=role_name,
                    display_name=role_name.title(),
                    description=f"{role_name.title()} role",
                    is_active=True
                )
                db.session.add(role)
        
        # Get or create basic departments
        departments = ['Hair', 'Nails', 'Spa', 'Fitness', 'Reception']
        for dept_name in departments:
            dept = Department.query.filter_by(name=dept_name).first()
            if not dept:
                dept = Department(
                    name=dept_name,
                    display_name=dept_name,
                    description=f"{dept_name} Department",
                    is_active=True
                )
                db.session.add(dept)
        
        db.session.commit()
        
        # Add staff members
        for i, staff_info in enumerate(staff_data, 1):
            # Check if user already exists
            existing_user = User.query.filter_by(username=staff_info['username']).first()
            if existing_user:
                print(f"Staff member {staff_info['username']} already exists, skipping...")
                continue
            
            # Generate staff code
            staff_code = f"STF{str(i).zfill(3)}"
            
            # Get role
            role = Role.query.filter_by(name=staff_info['role']).first()
            role_id = role.id if role else None
            
            # Assign department based on designation
            department_mapping = {
                'Hair Stylist': 'Hair',
                'Hair Color Specialist': 'Hair',
                'Barber': 'Hair',
                'Massage Therapist': 'Spa',
                'Esthetician': 'Spa',
                'Spa Manager': 'Spa',
                'Nail Technician': 'Nails',
                'Makeup Artist': 'Spa',
                'Fitness Trainer': 'Fitness',
                'Front Desk Cashier': 'Reception'
            }
            
            dept_name = None
            for key, value in department_mapping.items():
                if key in staff_info['designation']:
                    dept_name = value
                    break
            
            department = Department.query.filter_by(name=dept_name).first() if dept_name else None
            department_id = department.id if department else None
            
            # Create staff member
            staff_member = User(
                username=staff_info['username'],
                email=staff_info['email'],
                first_name=staff_info['first_name'],
                last_name=staff_info['last_name'],
                phone=staff_info['phone'],
                role=staff_info['role'],
                role_id=role_id,
                department_id=department_id,
                
                # Enhanced profile details
                staff_code=staff_code,
                designation=staff_info['designation'],
                gender=staff_info['gender'],
                date_of_joining=date.today(),
                
                # Work schedule (Monday to Friday, 9 AM to 6 PM)
                working_days='1111100',  # Mon-Fri
                shift_start_time=time(9, 0),
                shift_end_time=time(18, 0),
                
                # Commission and rates
                commission_percentage=staff_info['commission_percentage'],
                hourly_rate=staff_info['hourly_rate'],
                
                # Default settings
                verification_status=True,
                enable_face_checkin=True,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            # Set default password
            staff_member.password_hash = generate_password_hash('password123')
            
            db.session.add(staff_member)
            print(f"Added staff member: {staff_member.full_name} ({staff_member.staff_code})")
        
        db.session.commit()
        print("\n✅ Successfully added 10 sample staff members!")
        print("\nDefault login credentials for all staff:")
        print("Password: password123")
        print("\nStaff members added:")
        
        # Display added staff
        staff_list = User.query.filter(User.role.in_(['staff', 'manager', 'cashier'])).all()
        for staff in staff_list:
            print(f"- {staff.full_name} ({staff.username}) - {staff.designation} - {staff.staff_code}")

if __name__ == '__main__':
    add_sample_staff()
