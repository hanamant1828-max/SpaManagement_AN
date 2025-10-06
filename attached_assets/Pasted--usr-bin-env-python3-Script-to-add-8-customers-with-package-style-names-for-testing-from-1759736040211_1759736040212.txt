
#!/usr/bin/env python3
"""
Script to add 8 customers with package-style names for testing
"""

from app import app, db
from models import Customer
from datetime import date, datetime, timedelta
import random

def add_8_package_customers():
    """Add 8 customers with names like package1, package2, etc."""
    
    customers_data = []
    
    for i in range(1, 9):
        customer_data = {
            'first_name': f'Package{i}',
            'last_name': 'Customer',
            'phone': f'7777777{i}',
            'email': f'package{i}@test.com',
            'date_of_birth': date(1990 + i, 1, 15),
            'gender': 'female' if i % 2 == 0 else 'male',
            'address': f'{i * 100} Test Street, City, State {10000 + i}',
            'preferences': f'Test customer {i} preferences',
            'allergies': 'None' if i % 3 != 0 else 'Test allergy',
            'notes': f'Package test customer {i}',
            'total_visits': random.randint(0, 5),
            'total_spent': random.uniform(100.0, 1000.0),
            'is_active': True,
            'loyalty_points': random.randint(10, 100),
            'is_vip': i <= 2,  # First 2 are VIP
            'preferred_communication': 'sms',
            'marketing_consent': True,
            'referral_source': 'Test',
            'last_visit': datetime.utcnow() - timedelta(days=random.randint(1, 30)) if i % 2 == 0 else None,
            'created_at': datetime.utcnow() - timedelta(days=random.randint(30, 90))
        }
        customers_data.append(customer_data)
    
    with app.app_context():
        try:
            print("🏥 Adding 8 package test customers to the database...")
            
            # Check existing customers to avoid duplicates
            existing_phones = set()
            for customer_data in customers_data:
                existing_customer = Customer.query.filter_by(phone=customer_data['phone']).first()
                if existing_customer:
                    existing_phones.add(customer_data['phone'])
                    print(f"⚠️  Customer with phone {customer_data['phone']} already exists: {existing_customer.first_name} {existing_customer.last_name}")
            
            # Add new customers
            added_count = 0
            for customer_data in customers_data:
                if customer_data['phone'] not in existing_phones:
                    customer = Customer(**customer_data)
                    db.session.add(customer)
                    added_count += 1
                    print(f"✅ Adding customer: {customer_data['first_name']} {customer_data['last_name']} ({customer_data['phone']})")
            
            if added_count > 0:
                db.session.commit()
                print(f"\n🎉 Successfully added {added_count} package test customers to the database!")
            else:
                print("\n⚠️  All package test customers already exist in the database.")
                
            # Display summary
            total_customers = Customer.query.filter_by(is_active=True).count()
            print(f"\n📊 Database Summary:")
            print(f"   • Total active customers: {total_customers}")
            
            # Show the package customers
            package_customers = Customer.query.filter(
                Customer.first_name.like('Package%'),
                Customer.is_active == True
            ).order_by(Customer.first_name).all()
            
            print(f"\n👥 Package test customers in database ({len(package_customers)}):")
            for i, customer in enumerate(package_customers, 1):
                visits = customer.total_visits or 0
                spent = customer.total_spent or 0.0
                print(f"   {i}. {customer.full_name:<20} | {customer.phone:<12} | {customer.email:<25} | Visits: {visits:2d} | Spent: ₹{spent:,.0f}")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding customers: {str(e)}")
            raise

if __name__ == '__main__':
    add_8_package_customers()
