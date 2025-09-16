
#!/usr/bin/env python3
"""
Add 5 Staff Members to Staff Management System
"""

from app import app, db
from models import User, Role, Department
from werkzeug.security import generate_password_hash
from datetime import date, datetime
import random

def add_5_staff_members():
    """Add 5 diverse staff members to the system"""
    with app.app_context():
        print("🧑‍💼 Adding 5 Staff Members to Staff Management System")
        print("=" * 60)
        
        # Get available roles and departments
        roles = Role.query.filter_by(is_active=True).all()
        departments = Department.query.filter_by(is_active=True).all()
        
        print(f"📋 Available Roles: {[r.display_name for r in roles]}")
        print(f"🏢 Available Departments: {[d.display_name for d in departments]}")
        
        # Staff members data
        staff_data = [
            {
                'username': 'sarah_therapist',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'email': 'sarah.johnson@spa.com',
                'phone': '555-0101',
                'gender': 'female',
                'designation': 'Senior Massage Therapist',
                'role_name': 'Staff',
                'department_name': 'Spa Services',
                'commission_rate': 15.0,
                'hourly_rate': 35.0,
                'notes_bio': 'Specialized in Swedish and deep tissue massage with 8 years experience.'
            },
            {
                'username': 'mike_stylist',
                'first_name': 'Michael',
                'last_name': 'Rodriguez',
                'email': 'mike.rodriguez@spa.com',
                'phone': '555-0102',
                'gender': 'male',
                'designation': 'Hair Stylist & Colorist',
                'role_name': 'Staff',
                'department_name': 'Hair Salon',
                'commission_rate': 20.0,
                'hourly_rate': 40.0,
                'notes_bio': 'Expert in modern cuts and advanced coloring techniques.'
            },
            {
                'username': 'emma_manager',
                'first_name': 'Emma',
                'last_name': 'Davis',
                'email': 'emma.davis@spa.com',
                'phone': '555-0103',
                'gender': 'female',
                'designation': 'Spa Manager',
                'role_name': 'Manager',
                'department_name': 'Management',
                'commission_rate': 10.0,
                'hourly_rate': 45.0,
                'notes_bio': 'Manages daily operations and staff coordination with 10+ years in hospitality.'
            },
            {
                'username': 'alex_receptionist',
                'first_name': 'Alex',
                'last_name': 'Thompson',
                'email': 'alex.thompson@spa.com',
                'phone': '555-0104',
                'gender': 'other',
                'designation': 'Front Desk Receptionist',
                'role_name': 'Cashier',
                'department_name': 'Reception',
                'commission_rate': 5.0,
                'hourly_rate': 18.0,
                'notes_bio': 'Friendly and professional reception services, appointment scheduling specialist.'
            },
            {
                'username': 'lisa_esthetician',
                'first_name': 'Lisa',
                'last_name': 'Wilson',
                'email': 'lisa.wilson@spa.com',
                'phone': '555-0105',
                'gender': 'female',
                'designation': 'Licensed Esthetician',
                'role_name': 'Staff',
                'department_name': 'Spa Services',
                'commission_rate': 18.0,
                'hourly_rate': 32.0,
                'notes_bio': 'Skincare specialist with expertise in facials, chemical peels, and anti-aging treatments.'
            }
        ]
        
        added_count = 0
        
        for i, staff_info in enumerate(staff_data, 1):
            try:
                print(f"\n👤 Adding Staff Member {i}: {staff_info['first_name']} {staff_info['last_name']}")
                
                # Check if user already exists
                existing_user = User.query.filter(
                    (User.username == staff_info['username']) | 
                    (User.email == staff_info['email'])
                ).first()
                
                if existing_user:
                    print(f"   ⚠️ Staff member already exists: {staff_info['username']}")
                    continue
                
                # Find role and department
                role = None
                department = None
                
                for r in roles:
                    if r.name.lower() == staff_info['role_name'].lower() or r.display_name.lower() == staff_info['role_name'].lower():
                        role = r
                        break
                
                for d in departments:
                    if d.name.lower() == staff_info['department_name'].lower() or d.display_name.lower() == staff_info['department_name'].lower():
                        department = d
                        break
                
                # Generate staff code
                existing_codes = [u.staff_code for u in User.query.filter(User.staff_code.isnot(None)).all()]
                staff_code = f"STF{str(len(existing_codes) + i).zfill(3)}"
                while staff_code in existing_codes:
                    staff_code = f"STF{str(len(existing_codes) + i + random.randint(1, 100)).zfill(3)}"
                
                # Create new staff member
                new_staff = User(
                    username=staff_info['username'],
                    first_name=staff_info['first_name'],
                    last_name=staff_info['last_name'],
                    email=staff_info['email'],
                    phone=staff_info['phone'],
                    password_hash=generate_password_hash('password123'),  # Default password
                    role=staff_info['role_name'].lower(),
                    role_id=role.id if role else None,
                    department_id=department.id if department else None,
                    designation=staff_info['designation'],
                    staff_code=staff_code,
                    gender=staff_info['gender'],
                    date_of_joining=date.today(),
                    commission_rate=staff_info['commission_rate'],
                    hourly_rate=staff_info['hourly_rate'],
                    notes_bio=staff_info['notes_bio'],
                    is_active=True,
                    enable_face_checkin=True,
                    verification_status=False,
                    total_revenue_generated=0.0,
                    total_clients_served=0,
                    average_rating=0.0,
                    created_at=datetime.utcnow()
                )
                
                db.session.add(new_staff)
                db.session.flush()  # Get the ID
                
                print(f"   ✅ Created: {new_staff.first_name} {new_staff.last_name}")
                print(f"      🆔 Staff Code: {staff_code}")
                print(f"      📧 Email: {staff_info['email']}")
                print(f"      🏷️ Role: {staff_info['role_name']}")
                print(f"      🏢 Department: {staff_info['department_name']}")
                print(f"      💼 Designation: {staff_info['designation']}")
                print(f"      💰 Commission: {staff_info['commission_rate']}%")
                print(f"      ⏰ Hourly Rate: ${staff_info['hourly_rate']}")
                
                added_count += 1
                
            except Exception as e:
                print(f"   ❌ Error adding {staff_info['first_name']} {staff_info['last_name']}: {e}")
                db.session.rollback()
                continue
        
        if added_count > 0:
            try:
                db.session.commit()
                print(f"\n🎉 Successfully added {added_count} staff members!")
                print("\n📋 Staff Login Details:")
                print("   👤 Username: [staff_username]")
                print("   🔐 Password: password123")
                print("   ⚠️ Staff should change passwords on first login")
                
                # Display summary
                print(f"\n📊 Staff Management Summary:")
                total_staff = User.query.filter(User.role.in_(['staff', 'manager', 'admin'])).count()
                active_staff = User.query.filter(
                    User.role.in_(['staff', 'manager', 'admin']),
                    User.is_active == True
                ).count()
                print(f"   📈 Total Staff: {total_staff}")
                print(f"   ✅ Active Staff: {active_staff}")
                
                return True
                
            except Exception as e:
                print(f"\n❌ Error committing to database: {e}")
                db.session.rollback()
                return False
        else:
            print("\n⚠️ No new staff members were added (all already exist)")
            return False

if __name__ == "__main__":
    success = add_5_staff_members()
    if success:
        print(f"\n✨ Staff addition completed successfully!")
        print("   🌐 Visit /comprehensive_staff to see all staff members")
        print("   🔄 Refresh your staff management page to see the new additions")
    else:
        print(f"\n💔 Staff addition failed or incomplete")
