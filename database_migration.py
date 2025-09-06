
#!/usr/bin/env python3
"""
Migration script to export SQLite data to Replit Key-Value Store
This allows data to persist when sharing Repls across accounts
"""

import json
from datetime import datetime, date
from replit import db
from app import app, db as sqlalchemy_db
from models import *

def serialize_datetime(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def export_to_replit_db():
    """Export all SQLite data to Replit Key-Value Store"""
    with app.app_context():
        print("🔄 Starting migration from SQLite to Replit DB...")
        
        # Export Users
        users = User.query.all()
        user_data = []
        for user in users:
            user_dict = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'password_hash': user.password_hash,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'phone': user.phone,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'commission_rate': user.commission_rate,
                'hourly_rate': user.hourly_rate
            }
            user_data.append(user_dict)
        
        db['users'] = user_data
        print(f"✅ Exported {len(user_data)} users")
        
        # Export Customers
        customers = Customer.query.all()
        customer_data = []
        for customer in customers:
            customer_dict = {
                'id': customer.id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'email': customer.email,
                'phone': customer.phone,
                'date_of_birth': customer.date_of_birth.isoformat() if customer.date_of_birth else None,
                'gender': customer.gender,
                'address': customer.address,
                'created_at': customer.created_at.isoformat() if customer.created_at else None,
                'last_visit': customer.last_visit.isoformat() if customer.last_visit else None,
                'total_visits': customer.total_visits,
                'total_spent': customer.total_spent,
                'is_active': customer.is_active,
                'loyalty_points': customer.loyalty_points,
                'is_vip': customer.is_vip
            }
            customer_data.append(customer_dict)
        
        db['customers'] = customer_data
        print(f"✅ Exported {len(customer_data)} customers")
        
        # Export Services
        services = Service.query.all()
        service_data = []
        for service in services:
            service_dict = {
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'duration': service.duration,
                'price': service.price,
                'category': service.category,
                'is_active': service.is_active,
                'created_at': service.created_at.isoformat() if service.created_at else None
            }
            service_data.append(service_dict)
        
        db['services'] = service_data
        print(f"✅ Exported {len(service_data)} services")
        
        # Export Packages
        packages = Package.query.all()
        package_data = []
        for package in packages:
            package_dict = {
                'id': package.id,
                'name': package.name,
                'description': package.description,
                'package_type': package.package_type,
                'duration_months': package.duration_months,
                'validity_days': package.validity_days,
                'total_sessions': package.total_sessions,
                'total_price': package.total_price,
                'credit_amount': package.credit_amount,
                'discount_percentage': package.discount_percentage,
                'is_active': package.is_active,
                'created_at': package.created_at.isoformat() if package.created_at else None
            }
            package_data.append(package_dict)
        
        db['packages'] = package_data
        print(f"✅ Exported {len(package_data)} packages")
        
        # Export Appointments
        appointments = Appointment.query.all()
        appointment_data = []
        for appointment in appointments:
            appointment_dict = {
                'id': appointment.id,
                'client_id': appointment.client_id,
                'service_id': appointment.service_id,
                'staff_id': appointment.staff_id,
                'appointment_date': appointment.appointment_date.isoformat() if appointment.appointment_date else None,
                'end_time': appointment.end_time.isoformat() if appointment.end_time else None,
                'status': appointment.status,
                'notes': appointment.notes,
                'amount': appointment.amount,
                'discount': appointment.discount,
                'is_paid': appointment.is_paid
            }
            appointment_data.append(appointment_dict)
        
        db['appointments'] = appointment_data
        print(f"✅ Exported {len(appointment_data)} appointments")
        
        print("🎉 Migration to Replit DB completed successfully!")
        print("📋 Data exported:")
        print(f"   - Users: {len(user_data)}")
        print(f"   - Customers: {len(customer_data)}")
        print(f"   - Services: {len(service_data)}")
        print(f"   - Packages: {len(package_data)}")
        print(f"   - Appointments: {len(appointment_data)}")

def import_from_replit_db():
    """Import data from Replit Key-Value Store to SQLite"""
    with app.app_context():
        print("🔄 Starting import from Replit DB to SQLite...")
        
        # Clear existing data
        sqlalchemy_db.session.query(Appointment).delete()
        sqlalchemy_db.session.query(CustomerPackage).delete()
        sqlalchemy_db.session.query(PackageService).delete()
        sqlalchemy_db.session.query(Package).delete()
        sqlalchemy_db.session.query(Service).delete()
        sqlalchemy_db.session.query(Customer).delete()
        sqlalchemy_db.session.query(User).delete()
        
        # Import Users
        if 'users' in db:
            users_data = db['users']
            for user_dict in users_data:
                user = User(
                    username=user_dict['username'],
                    email=user_dict['email'],
                    password_hash=user_dict['password_hash'],
                    first_name=user_dict['first_name'],
                    last_name=user_dict['last_name'],
                    role=user_dict['role'],
                    phone=user_dict.get('phone'),
                    is_active=user_dict.get('is_active', True),
                    commission_rate=user_dict.get('commission_rate', 0.0),
                    hourly_rate=user_dict.get('hourly_rate', 0.0)
                )
                if user_dict.get('created_at'):
                    user.created_at = datetime.fromisoformat(user_dict['created_at'])
                sqlalchemy_db.session.add(user)
            print(f"✅ Imported {len(users_data)} users")
        
        # Import Customers
        if 'customers' in db:
            customers_data = db['customers']
            for customer_dict in customers_data:
                customer = Customer(
                    first_name=customer_dict['first_name'],
                    last_name=customer_dict['last_name'],
                    email=customer_dict.get('email'),
                    phone=customer_dict['phone'],
                    gender=customer_dict.get('gender'),
                    address=customer_dict.get('address'),
                    total_visits=customer_dict.get('total_visits', 0),
                    total_spent=customer_dict.get('total_spent', 0.0),
                    is_active=customer_dict.get('is_active', True),
                    loyalty_points=customer_dict.get('loyalty_points', 0),
                    is_vip=customer_dict.get('is_vip', False)
                )
                if customer_dict.get('date_of_birth'):
                    customer.date_of_birth = datetime.fromisoformat(customer_dict['date_of_birth']).date()
                if customer_dict.get('created_at'):
                    customer.created_at = datetime.fromisoformat(customer_dict['created_at'])
                if customer_dict.get('last_visit'):
                    customer.last_visit = datetime.fromisoformat(customer_dict['last_visit'])
                sqlalchemy_db.session.add(customer)
            print(f"✅ Imported {len(customers_data)} customers")
        
        # Import Services
        if 'services' in db:
            services_data = db['services']
            for service_dict in services_data:
                service = Service(
                    name=service_dict['name'],
                    description=service_dict.get('description'),
                    duration=service_dict['duration'],
                    price=service_dict['price'],
                    category=service_dict['category'],
                    is_active=service_dict.get('is_active', True)
                )
                if service_dict.get('created_at'):
                    service.created_at = datetime.fromisoformat(service_dict['created_at'])
                sqlalchemy_db.session.add(service)
            print(f"✅ Imported {len(services_data)} services")
        
        # Import Packages
        if 'packages' in db:
            packages_data = db['packages']
            for package_dict in packages_data:
                package = Package(
                    name=package_dict['name'],
                    description=package_dict.get('description'),
                    package_type=package_dict.get('package_type', 'regular'),
                    duration_months=package_dict['duration_months'],
                    validity_days=package_dict['validity_days'],
                    total_sessions=package_dict['total_sessions'],
                    total_price=package_dict['total_price'],
                    credit_amount=package_dict.get('credit_amount', 0.0),
                    discount_percentage=package_dict.get('discount_percentage', 0.0),
                    is_active=package_dict.get('is_active', True)
                )
                if package_dict.get('created_at'):
                    package.created_at = datetime.fromisoformat(package_dict['created_at'])
                sqlalchemy_db.session.add(package)
            print(f"✅ Imported {len(packages_data)} packages")
        
        sqlalchemy_db.session.commit()
        print("🎉 Import from Replit DB completed successfully!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'import':
        import_from_replit_db()
    else:
        export_to_replit_db()
