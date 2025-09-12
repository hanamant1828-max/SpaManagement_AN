
#!/usr/bin/env python3
"""
Test script to add a sample staff member and verify the save functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Role, Department
from werkzeug.security import generate_password_hash
from datetime import date, time, datetime

def test_add_staff():
    """Add a test staff member to verify save functionality"""
    
    with app.app_context():
        print("🧪 Testing Staff Creation...")
        
        # Get or create a role
        role = Role.query.filter_by(name='staff').first()
        if not role:
            role = Role(
                name='staff',
                display_name='Staff Member',
                is_active=True
            )
            db.session.add(role)
            db.session.commit()
            print("✅ Created staff role")
        
        # Get or create a department
        department = Department.query.filter_by(name='Spa').first()
        if not department:
            department = Department(
                name='Spa',
                display_name='Spa Services',
                is_active=True
            )
            db.session.add(department)
            db.session.commit()
            print("✅ Created spa department")
        
        # Create test staff member
        test_staff = User(
            username=f'test_staff_{int(datetime.now().timestamp())}',
            first_name='Test',
            last_name='Employee',
            email=f'test.employee.{int(datetime.now().timestamp())}@spa.com',
            phone='555-0123',
            password_hash=generate_password_hash('password123'),
            
            # Role and department
            role='staff',
            role_id=role.id,
            department_id=department.id,
            
            # Profile details
            staff_code=f'TST{int(datetime.now().timestamp()) % 1000:03d}',
            designation='Test Specialist',
            gender='other',
            date_of_birth=date(1990, 1, 1),
            date_of_joining=date.today(),
            
            # Work schedule
            working_days='1111100',  # Monday to Friday
            shift_start_time=time(9, 0),
            shift_end_time=time(17, 0),
            
            # Commission and rates
            commission_rate=15.0,
            hourly_rate=25.0,
            
            # Features
            verification_status=True,
            enable_face_checkin=True,
            is_active=True,
            
            # Bio
            notes_bio='Test staff member created for testing save functionality',
            
            created_at=datetime.utcnow()
        )
        
        try:
            db.session.add(test_staff)
            db.session.commit()
            
            print(f"✅ Successfully created test staff member!")
            print(f"   Name: {test_staff.first_name} {test_staff.last_name}")
            print(f"   Username: {test_staff.username}")
            print(f"   Email: {test_staff.email}")
            print(f"   Staff Code: {test_staff.staff_code}")
            print(f"   Role: {test_staff.role}")
            print(f"   Department: {department.display_name}")
            print(f"   ID: {test_staff.id}")
            
            # Test retrieval
            retrieved_staff = User.query.get(test_staff.id)
            if retrieved_staff:
                print(f"✅ Staff member successfully retrieved from database")
                print(f"   Full Name: {retrieved_staff.full_name}")
                print(f"   Is Active: {retrieved_staff.is_active}")
                
                return test_staff.id
            else:
                print("❌ Error: Could not retrieve staff member after creation")
                return None
                
        except Exception as e:
            print(f"❌ Error creating staff member: {str(e)}")
            db.session.rollback()
            return None

def test_staff_api():
    """Test the staff API endpoints"""
    import requests
    import json
    
    print("\n🔌 Testing Staff API Endpoints...")
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Test GET /api/staff
        print("Testing GET /api/staff...")
        response = requests.get(f"{base_url}/api/staff", timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API returned {len(data.get('staff', []))} staff members")
        else:
            print(f"❌ API error: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Connection error: {str(e)}")
        print("💡 Make sure the Flask app is running on port 5000")

if __name__ == '__main__':
    print("🚀 Starting Staff Management Test")
    print("=" * 50)
    
    # Add test staff member
    staff_id = test_add_staff()
    
    if staff_id:
        print(f"\n✅ Test completed successfully!")
        print(f"📝 You can now test the staff management UI with staff ID: {staff_id}")
        print("\n🌐 To test the web interface:")
        print("1. Go to http://127.0.0.1:5000/comprehensive_staff")
        print("2. Click 'Add New Staff' to test the form")
        print("3. Edit the test staff member to test updates")
        print("4. Try the schedule management features")
        
        # Test API endpoints
        test_staff_api()
        
    else:
        print("\n❌ Test failed - could not create staff member")
        
    print("\n" + "=" * 50)
    print("🏁 Test completed")
