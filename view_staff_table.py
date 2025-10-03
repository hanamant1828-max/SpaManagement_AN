
#!/usr/bin/env python3
"""
View Staff Management Table Data
Complete schema and current records
"""

from app import app, db
from models import User, Role, Department
from sqlalchemy import inspect

def view_staff_table():
    """Display complete staff table information"""
    with app.app_context():
        print("=" * 150)
        print("STAFF MANAGEMENT TABLE SCHEMA")
        print("=" * 150)
        
        # Get table schema
        inspector = inspect(db.engine)
        columns = inspector.get_columns('user')
        
        print(f"\n{'Column Name':<30} {'Type':<20} {'Nullable':<10} {'Default':<20}")
        print("-" * 150)
        
        for column in columns:
            col_name = column['name']
            col_type = str(column['type'])
            nullable = 'Yes' if column['nullable'] else 'No'
            default = str(column['default']) if column['default'] else '-'
            print(f"{col_name:<30} {col_type:<20} {nullable:<10} {default:<20}")
        
        # Get current staff data
        print("\n" + "=" * 150)
        print("CURRENT STAFF RECORDS")
        print("=" * 150)
        
        staff_members = User.query.filter(
            User.role.in_(['staff', 'manager', 'admin', 'receptionist', 'therapist'])
        ).all()
        
        print(f"\nTotal Staff Members: {len(staff_members)}")
        print("-" * 150)
        
        if staff_members:
            print(f"\n{'ID':<5} {'Username':<20} {'Name':<25} {'Email':<30} {'Phone':<15} {'Role':<15} {'Department':<20} {'Status':<10}")
            print("-" * 150)
            
            for staff in staff_members:
                staff_id = str(staff.id)
                username = staff.username[:19] if staff.username else 'N/A'
                full_name = f"{staff.first_name} {staff.last_name}"[:24]
                email = staff.email[:29] if staff.email else 'N/A'
                phone = staff.phone[:14] if staff.phone else 'N/A'
                
                role_display = staff.user_role.display_name[:14] if staff.user_role else (staff.role[:14] if staff.role else 'N/A')
                dept_display = staff.staff_department.display_name[:19] if staff.staff_department else 'N/A'
                
                status = "Active" if staff.is_active else "Inactive"
                
                print(f"{staff_id:<5} {username:<20} {full_name:<25} {email:<30} {phone:<15} {role_display:<15} {dept_display:<20} {status:<10}")
            
            # Detailed view for first 3 staff
            print("\n" + "=" * 150)
            print("SAMPLE DETAILED RECORDS (First 3)")
            print("=" * 150)
            
            for staff in staff_members[:3]:
                print(f"\n{'─' * 150}")
                print(f"Staff ID: {staff.id}")
                print(f"{'─' * 150}")
                print(f"  Username:              {staff.username}")
                print(f"  Full Name:             {staff.first_name} {staff.last_name}")
                print(f"  Email:                 {staff.email or 'Not provided'}")
                print(f"  Phone:                 {staff.phone or 'Not provided'}")
                print(f"  Staff Code:            {staff.staff_code or 'Not assigned'}")
                print(f"  Designation:           {staff.designation or 'Not specified'}")
                print(f"  Gender:                {staff.gender or 'Not specified'}")
                print(f"  Date of Birth:         {staff.date_of_birth or 'Not provided'}")
                print(f"  Date of Joining:       {staff.date_of_joining or 'Not provided'}")
                print(f"  Commission Rate:       {staff.commission_rate or 0}%")
                print(f"  Hourly Rate:           ${staff.hourly_rate or 0}")
                print(f"  Total Revenue:         ${staff.total_revenue_generated or 0}")
                print(f"  Clients Served:        {staff.total_clients_served or 0}")
                print(f"  Average Rating:        {staff.average_rating or 0}/5")
                print(f"  Face Check-in:         {'Enabled' if staff.enable_face_checkin else 'Disabled'}")
                print(f"  Verification Status:   {'Verified' if staff.verification_status else 'Pending'}")
                print(f"  Status:                {'Active' if staff.is_active else 'Inactive'}")
                print(f"  Created At:            {staff.created_at}")
        else:
            print("\nNo staff members found in database.")
        
        print("\n" + "=" * 150)

if __name__ == "__main__":
    view_staff_table()
