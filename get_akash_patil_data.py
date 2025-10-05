
#!/usr/bin/env python3
"""
Script to fetch Akash Patil's customer data from the API
"""
from app import app, db
from models import Customer, ServicePackageAssignment, Appointment
from sqlalchemy import or_, func
import json

def get_akash_patil_data():
    """Fetch and display Akash Patil's complete data"""
    with app.app_context():
        # Search for Akash Patil
        customer = Customer.query.filter(
            or_(
                func.concat(Customer.first_name, ' ', Customer.last_name).ilike('%akash%patil%'),
                func.concat(Customer.first_name, ' ', Customer.last_name).ilike('%patil%akash%')
            ),
            Customer.is_active == True
        ).first()
        
        if not customer:
            print("❌ Customer 'Akash Patil' not found in database")
            return
        
        # Get customer's packages
        packages = ServicePackageAssignment.query.filter_by(
            customer_id=customer.id,
            status='active'
        ).all()
        
        # Get customer's appointments
        appointments = Appointment.query.filter_by(
            client_id=customer.id
        ).order_by(Appointment.appointment_date.desc()).limit(10).all()
        
        # Build customer data dictionary
        customer_data = {
            'customer_id': customer.id,
            'personal_info': {
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'full_name': customer.full_name,
                'email': customer.email,
                'phone': customer.phone,
                'date_of_birth': customer.date_of_birth.isoformat() if customer.date_of_birth else None,
                'gender': customer.gender,
                'address': customer.address
            },
            'account_info': {
                'total_visits': customer.total_visits or 0,
                'total_spent': float(customer.total_spent or 0),
                'last_visit': customer.last_visit.isoformat() if customer.last_visit else None,
                'loyalty_points': customer.loyalty_points or 0,
                'is_vip': customer.is_vip,
                'status': customer.status,
                'created_at': customer.created_at.isoformat() if customer.created_at else None
            },
            'active_packages': [
                {
                    'package_id': pkg.id,
                    'package_type': pkg.package_type,
                    'total_sessions': pkg.total_sessions,
                    'used_sessions': pkg.used_sessions,
                    'remaining_sessions': pkg.remaining_sessions,
                    'credit_amount': float(pkg.credit_amount or 0),
                    'remaining_credit': float(pkg.remaining_credit or 0),
                    'assigned_on': pkg.assigned_on.isoformat() if pkg.assigned_on else None,
                    'expires_on': pkg.expires_on.isoformat() if pkg.expires_on else None,
                    'status': pkg.status
                } for pkg in packages
            ],
            'recent_appointments': [
                {
                    'appointment_id': apt.id,
                    'appointment_date': apt.appointment_date.isoformat() if apt.appointment_date else None,
                    'service_name': apt.service.name if apt.service else None,
                    'staff_name': apt.staff.full_name if apt.staff else None,
                    'status': apt.status,
                    'amount': float(apt.amount or 0)
                } for apt in appointments
            ]
        }
        
        # Print formatted JSON
        print("=" * 80)
        print("📊 AKASH PATIL - CUSTOMER API DATA")
        print("=" * 80)
        print(json.dumps(customer_data, indent=2, ensure_ascii=False))
        print("=" * 80)
        
        # Also print summary
        print("\n📋 SUMMARY:")
        print(f"   Name: {customer.full_name}")
        print(f"   Phone: {customer.phone}")
        print(f"   Email: {customer.email or 'N/A'}")
        print(f"   Total Visits: {customer.total_visits or 0}")
        print(f"   Total Spent: ₹{customer.total_spent or 0:.2f}")
        print(f"   Active Packages: {len(packages)}")
        print(f"   Recent Appointments: {len(appointments)}")
        
        # API endpoint information
        print("\n🌐 API ENDPOINT:")
        print(f"   GET /api/customer/search/akash%20patil")
        print(f"   GET /api/customer/search/{customer.id}")
        
        return customer_data

if __name__ == "__main__":
    get_akash_patil_data()
