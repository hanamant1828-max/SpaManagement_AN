
#!/usr/bin/env python3
"""
Script to add 25 customers with names radhika1-radhika25 and sequential phone numbers
"""

from app import app, db
from models import Customer
from datetime import date, datetime, timedelta
import random

def add_25_radhika_customers():
    """Add 25 customers named radhika1 to radhika25"""
    
    with app.app_context():
        try:
            print("🏥 Adding 25 Radhika customers to the database...")
            
            added_count = 0
            
            for i in range(1, 26):
                # Create customer data
                customer_name = f'radhika{i}'
                phone_number = f'{i:05d}'  # Format as 00001, 00002, etc.
                
                # Check if customer already exists
                existing_customer = Customer.query.filter_by(phone=phone_number).first()
                if existing_customer:
                    print(f"⚠️  Customer with phone {phone_number} already exists: {existing_customer.first_name} {existing_customer.last_name}")
                    continue
                
                customer_data = {
                    'first_name': customer_name,
                    'last_name': 'Customer',
                    'phone': phone_number,
                    'email': f'{customer_name}@example.com',
                    'date_of_birth': date(1990 + (i % 20), (i % 12) + 1, (i % 28) + 1),
                    'gender': 'female',
                    'address': f'{i * 10} Test Street, City, State {10000 + i}',
                    'preferences': f'Customer {i} preferences',
                    'allergies': 'None' if i % 3 != 0 else 'Sensitive skin',
                    'notes': f'Radhika test customer {i}',
                    'total_visits': random.randint(0, 10),
                    'total_spent': random.uniform(100.0, 5000.0),
                    'is_active': True,
                    'loyalty_points': random.randint(10, 200),
                    'is_vip': i <= 5,  # First 5 are VIP
                    'preferred_communication': 'sms',
                    'marketing_consent': True,
                    'referral_source': 'Walk-in',
                    'last_visit': datetime.utcnow() - timedelta(days=random.randint(1, 60)) if i % 2 == 0 else None,
                    'created_at': datetime.utcnow() - timedelta(days=random.randint(30, 180))
                }
                
                customer = Customer(**customer_data)
                db.session.add(customer)
                added_count += 1
                print(f"✅ Adding customer: {customer_name} Customer ({phone_number})")
            
            if added_count > 0:
                db.session.commit()
                print(f"\n🎉 Successfully added {added_count} Radhika customers to the database!")
            else:
                print("\n⚠️  All Radhika customers already exist in the database.")
                
            # Display summary
            total_customers = Customer.query.filter_by(is_active=True).count()
            print(f"\n📊 Database Summary:")
            print(f"   • Total active customers: {total_customers}")
            
            # Show the Radhika customers
            radhika_customers = Customer.query.filter(
                Customer.first_name.like('radhika%'),
                Customer.is_active == True
            ).order_by(Customer.first_name).all()
            
            print(f"\n👥 Radhika customers in database ({len(radhika_customers)}):")
            for i, customer in enumerate(radhika_customers, 1):
                visits = customer.total_visits or 0
                spent = customer.total_spent or 0.0
                print(f"   {i:2d}. {customer.full_name:<25} | {customer.phone:<10} | {customer.email:<30} | Visits: {visits:2d} | Spent: ₹{spent:,.0f}")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding customers: {str(e)}")
            raise

if __name__ == '__main__':
    add_25_radhika_customers()
