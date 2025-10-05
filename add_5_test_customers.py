
#!/usr/bin/env python3
"""
Script to add 5 test customers with names abc1, abc2, etc.
"""

from app import app, db
from models import Customer
from datetime import date

def add_test_customers():
    """Add 5 test customers to the database"""
    
    customers_data = [
        {
            'first_name': 'abc1',
            'last_name': 'Test',
            'phone': '+91-9900000001',
            'email': 'abc1@test.com',
            'date_of_birth': date(1990, 1, 1),
            'gender': 'male',
            'address': '123 Test Street, Test City',
            'preferences': 'Test customer 1',
            'allergies': 'None',
            'notes': 'Test customer abc1'
        },
        {
            'first_name': 'abc2',
            'last_name': 'Test',
            'phone': '+91-9900000002',
            'email': 'abc2@test.com',
            'date_of_birth': date(1991, 2, 2),
            'gender': 'female',
            'address': '124 Test Street, Test City',
            'preferences': 'Test customer 2',
            'allergies': 'None',
            'notes': 'Test customer abc2'
        },
        {
            'first_name': 'abc3',
            'last_name': 'Test',
            'phone': '+91-9900000003',
            'email': 'abc3@test.com',
            'date_of_birth': date(1992, 3, 3),
            'gender': 'male',
            'address': '125 Test Street, Test City',
            'preferences': 'Test customer 3',
            'allergies': 'None',
            'notes': 'Test customer abc3'
        },
        {
            'first_name': 'abc4',
            'last_name': 'Test',
            'phone': '+91-9900000004',
            'email': 'abc4@test.com',
            'date_of_birth': date(1993, 4, 4),
            'gender': 'female',
            'address': '126 Test Street, Test City',
            'preferences': 'Test customer 4',
            'allergies': 'None',
            'notes': 'Test customer abc4'
        },
        {
            'first_name': 'abc5',
            'last_name': 'Test',
            'phone': '+91-9900000005',
            'email': 'abc5@test.com',
            'date_of_birth': date(1994, 5, 5),
            'gender': 'male',
            'address': '127 Test Street, Test City',
            'preferences': 'Test customer 5',
            'allergies': 'None',
            'notes': 'Test customer abc5'
        }
    ]
    
    with app.app_context():
        try:
            print("🧪 Adding 5 test customers to the database...")
            
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
                print(f"\n🎉 Successfully added {added_count} test customers to the database!")
            else:
                print("\n⚠️  All test customers already exist in the database.")
                
            # Display summary
            total_customers = Customer.query.filter_by(is_active=True).count()
            print(f"\n📊 Database Summary:")
            print(f"   • Total active customers: {total_customers}")
            
            # Show the test customers
            test_customers = Customer.query.filter(
                Customer.first_name.like('abc%')
            ).order_by(Customer.first_name).all()
            
            print(f"\n👥 Test customers in database:")
            for i, customer in enumerate(test_customers, 1):
                print(f"   {i}. {customer.full_name:<25} | {customer.phone:<15} | {customer.email}")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding customers: {str(e)}")
            raise

if __name__ == '__main__':
    add_test_customers()
