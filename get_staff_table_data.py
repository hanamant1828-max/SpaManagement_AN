
#!/usr/bin/env python3
"""
Display all data from the Staff Management (User) table
"""

from app import app, db
from models import User, Role, Department
from datetime import datetime

def display_staff_table():
    """Display all staff members in a formatted table"""
    with app.app_context():
        print("=" * 150)
        print("STAFF MANAGEMENT TABLE - ALL DATA")
        print("=" * 150)
        
        # Get all users (staff members)
        staff_members = User.query.order_by(User.id).all()
        
        if not staff_members:
            print("\n❌ No staff members found in the database")
            return
        
        print(f"\n📊 Total Staff Members: {len(staff_members)}\n")
        
        # Table header
        print(f"{'ID':<5} {'Username':<20} {'Full Name':<25} {'Email':<30} {'Phone':<15} {'Role':<15} {'Department':<20} {'Status':<10}")
        print("-" * 150)
        
        # Display each staff member
        for staff in staff_members:
            staff_id = str(staff.id)
            username = staff.username[:19] if staff.username else "N/A"
            full_name = f"{staff.first_name} {staff.last_name}"[:24]
            email = (staff.email[:29] if staff.email else "N/A")
            phone = (staff.phone[:14] if staff.phone else "N/A")
            
            # Get role display name
            role_display = "N/A"
            if staff.user_role:
                role_display = staff.user_role.display_name[:14]
            elif staff.role:
                role_display = staff.role[:14]
            
            # Get department display name
            dept_display = "N/A"
            if staff.staff_department:
                dept_display = staff.staff_department.display_name[:19]
            
            status = "Active" if staff.is_active else "Inactive"
            
            print(f"{staff_id:<5} {username:<20} {full_name:<25} {email:<30} {phone:<15} {role_display:<15} {dept_display:<20} {status:<10}")
        
        print("-" * 150)
        
        # Additional details section
        print("\n" + "=" * 150)
        print("DETAILED STAFF INFORMATION")
        print("=" * 150)
        
        for staff in staff_members:
            print(f"\n{'─' * 150}")
            print(f"👤 STAFF ID: {staff.id}")
            print(f"{'─' * 150}")
            print(f"  Username:           {staff.username}")
            print(f"  Full Name:          {staff.first_name} {staff.last_name}")
            print(f"  Email:              {staff.email or 'Not provided'}")
            print(f"  Phone:              {staff.phone or 'Not provided'}")
            print(f"  Gender:             {staff.gender or 'Not specified'}")
            
            # Role and Department
            role_name = staff.user_role.display_name if staff.user_role else staff.role
            dept_name = staff.staff_department.display_name if staff.staff_department else "Not assigned"
            print(f"  Role:               {role_name}")
            print(f"  Department:         {dept_name}")
            print(f"  Designation:        {staff.designation or 'Not specified'}")
            print(f"  Staff Code:         {staff.staff_code or 'Not assigned'}")
            
            # Dates
            if staff.date_of_birth:
                print(f"  Date of Birth:      {staff.date_of_birth.strftime('%Y-%m-%d')}")
            if staff.date_of_joining:
                print(f"  Date of Joining:    {staff.date_of_joining.strftime('%Y-%m-%d')}")
            
            # Work Schedule
            if staff.shift_start_time and staff.shift_end_time:
                print(f"  Shift:              {staff.shift_start_time.strftime('%H:%M')} - {staff.shift_end_time.strftime('%H:%M')}")
            
            # Commission and Rates
            if staff.commission_rate:
                print(f"  Commission Rate:    {staff.commission_rate}%")
            if staff.hourly_rate:
                print(f"  Hourly Rate:        ₹{staff.hourly_rate}")
            
            # Performance Metrics
            print(f"  Total Revenue:      ₹{staff.total_revenue_generated or 0}")
            print(f"  Clients Served:     {staff.total_clients_served or 0}")
            if staff.average_rating:
                print(f"  Average Rating:     {staff.average_rating}/5.0")
            
            # Status and Features
            print(f"  Status:             {'✅ Active' if staff.is_active else '❌ Inactive'}")
            print(f"  Verified:           {'✅ Yes' if staff.verification_status else '❌ No'}")
            print(f"  Face Check-in:      {'✅ Enabled' if staff.enable_face_checkin else '❌ Disabled'}")
            
            # Last login
            if staff.last_login:
                print(f"  Last Login:         {staff.last_login.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Created
            if staff.created_at:
                print(f"  Created:            {staff.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Notes
            if staff.notes_bio:
                print(f"  Notes/Bio:          {staff.notes_bio[:100]}{'...' if len(staff.notes_bio) > 100 else ''}")
        
        print("\n" + "=" * 150)
        
        # Summary Statistics
        print("\n📊 SUMMARY STATISTICS")
        print("=" * 150)
        
        active_staff = sum(1 for s in staff_members if s.is_active)
        inactive_staff = len(staff_members) - active_staff
        verified_staff = sum(1 for s in staff_members if s.verification_status)
        face_enabled = sum(1 for s in staff_members if s.enable_face_checkin)
        
        # Count by role
        roles_count = {}
        for staff in staff_members:
            role_name = staff.user_role.display_name if staff.user_role else staff.role
            roles_count[role_name] = roles_count.get(role_name, 0) + 1
        
        # Count by department
        dept_count = {}
        for staff in staff_members:
            dept_name = staff.staff_department.display_name if staff.staff_department else "Unassigned"
            dept_count[dept_name] = dept_count.get(dept_name, 0) + 1
        
        print(f"\n  Total Staff:        {len(staff_members)}")
        print(f"  Active:             {active_staff}")
        print(f"  Inactive:           {inactive_staff}")
        print(f"  Verified:           {verified_staff}")
        print(f"  Face Check-in:      {face_enabled}")
        
        print(f"\n  Staff by Role:")
        for role, count in sorted(roles_count.items()):
            print(f"    {role:<20} {count}")
        
        print(f"\n  Staff by Department:")
        for dept, count in sorted(dept_count.items()):
            print(f"    {dept:<20} {count}")
        
        print("\n" + "=" * 150)

if __name__ == "__main__":
    display_staff_table()
