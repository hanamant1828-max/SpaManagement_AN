
#!/usr/bin/env python3
"""
Script to add sample customers to the spa management system
"""

from app import app, db
from models import Customer
from datetime import date

def add_sample_customers():
    """Add 5 sample customers to the database"""
    
    sample_customers = [
        {
            'first_name': 'Emma',
            'last_name': 'Johnson',
            'phone': '+1234567890',
            'email': 'emma.johnson@email.com',
            'date_of_birth': date(1985, 3, 15),
            'gender': 'female',
            'address': '123 Main Street, New York, NY 10001',
            'preferences': 'Prefers relaxing massages, loves aromatherapy',
            'allergies': 'None known',
            'notes': 'Regular customer, very punctual'
        },
        {
            'first_name': 'Michael',
            'last_name': 'Davis',
            'phone': '+1234567891',
            'email': 'michael.davis@email.com',
            'date_of_birth': date(1990, 7, 22),
            'gender': 'male',
            'address': '456 Oak Avenue, Los Angeles, CA 90210',
            'preferences': 'Deep tissue massage, sports therapy',
            'allergies': 'Sensitive to strong fragrances',
            'notes': 'Athlete, needs intensive treatments'
        },
        {
            'first_name': 'Sarah',
            'last_name': 'Wilson',
            'phone': '+1234567892',
            'email': 'sarah.wilson@email.com',
            'date_of_birth': date(1988, 11, 8),
            'gender': 'female',
            'address': '789 Pine Road, Chicago, IL 60601',
            'preferences': 'Facial treatments, anti-aging services',
            'allergies': 'Allergic to nuts',
            'notes': 'VIP customer, prefers afternoon appointments'
        },
        {
            'first_name': 'David',
            'last_name': 'Brown',
            'phone': '+1234567893',
            'email': 'david.brown@email.com',
            'date_of_birth': date(1982, 5, 30),
            'gender': 'male',
            'address': '321 Elm Street, Houston, TX 77001',
            'preferences': 'Hot stone massage, reflexology',
            'allergies': 'None',
            'notes': 'Businessman, often books last minute'
        },
        {
            'first_name': 'Jessica',
            'last_name': 'Miller',
            'phone': '+1234567894',
            'email': 'jessica.miller@email.com',
            'date_of_birth': date(1992, 12, 12),
            'gender': 'female',
            'address': '654 Maple Drive, Miami, FL 33101',
            'preferences': 'Prenatal massage, gentle treatments',
            'allergies': 'Latex sensitivity',
            'notes': 'Expecting mother, requires special care'
        }
    ]
    
    with app.app_context():
        try:
            # Check if customers already exist to avoid duplicates
            existing_phones = set()
            for customer_data in sample_customers:
                existing_customer = Customer.query.filter_by(phone=customer_data['phone']).first()
                if existing_customer:
                    existing_phones.add(customer_data['phone'])
                    print(f"Customer with phone {customer_data['phone']} already exists: {existing_customer.first_name} {existing_customer.last_name}")
            
            # Add new customers
            added_count = 0
            for customer_data in sample_customers:
                if customer_data['phone'] not in existing_phones:
                    customer = Customer(**customer_data)
                    db.session.add(customer)
                    added_count += 1
                    print(f"Adding customer: {customer_data['first_name']} {customer_data['last_name']}")
            
            if added_count > 0:
                db.session.commit()
                print(f"\n✅ Successfully added {added_count} sample customers to the database!")
            else:
                print("\n⚠️ All sample customers already exist in the database.")
                
            # Display all customers
            all_customers = Customer.query.filter_by(is_active=True).order_by(Customer.first_name).all()
            print(f"\nTotal active customers in database: {len(all_customers)}")
            print("\nAll customers:")
            for customer in all_customers:
                print(f"- {customer.full_name} ({customer.phone}) - {customer.email}")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding customers: {str(e)}")

if __name__ == '__main__':
    add_sample_customers()
