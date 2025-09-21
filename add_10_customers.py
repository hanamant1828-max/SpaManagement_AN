
#!/usr/bin/env python3
"""
Script to add 10 diverse customers to the spa management system
"""

from app import app, db
from models import Customer
from datetime import date, datetime
import random

def add_10_customers():
    """Add 10 diverse customers to the database"""
    
    customers_data = [
        {
            'first_name': 'Priya',
            'last_name': 'Sharma',
            'phone': '+91-9876543210',
            'email': 'priya.sharma@gmail.com',
            'date_of_birth': date(1990, 5, 15),
            'gender': 'female',
            'address': 'A-101, Green Valley Apartments, Mumbai, Maharashtra 400001',
            'preferences': 'Prefers aromatherapy massage, loves herbal facials',
            'allergies': 'Allergic to synthetic fragrances',
            'notes': 'Regular customer, books monthly appointments, prefers evening slots'
        },
        {
            'first_name': 'Rahul',
            'last_name': 'Kumar',
            'phone': '+91-9876543211',
            'email': 'rahul.kumar@yahoo.com',
            'date_of_birth': date(1985, 8, 22),
            'gender': 'male',
            'address': 'B-205, Royal Heights, Delhi, NCR 110001',
            'preferences': 'Deep tissue massage, sports therapy',
            'allergies': 'None known',
            'notes': 'Fitness enthusiast, needs therapeutic treatments'
        },
        {
            'first_name': 'Anita',
            'last_name': 'Patel',
            'phone': '+91-9876543212',
            'email': 'anita.patel@hotmail.com',
            'date_of_birth': date(1988, 12, 8),
            'gender': 'female',
            'address': '15, Lotus Colony, Ahmedabad, Gujarat 380001',
            'preferences': 'Anti-aging facials, gold treatments',
            'allergies': 'Sensitive to strong chemicals',
            'notes': 'Business owner, prefers premium services, VIP treatment'
        },
        {
            'first_name': 'Vikram',
            'last_name': 'Singh',
            'phone': '+91-9876543213',
            'email': 'vikram.singh@gmail.com',
            'date_of_birth': date(1982, 3, 30),
            'gender': 'male',
            'address': 'C-45, Officers Colony, Jaipur, Rajasthan 302001',
            'preferences': 'Hot stone massage, reflexology',
            'allergies': 'None',
            'notes': 'Government officer, books appointments 2 weeks in advance'
        },
        {
            'first_name': 'Kavya',
            'last_name': 'Reddy',
            'phone': '+91-9876543214',
            'email': 'kavya.reddy@outlook.com',
            'date_of_birth': date(1992, 7, 12),
            'gender': 'female',
            'address': 'Plot 78, Banjara Hills, Hyderabad, Telangana 500001',
            'preferences': 'Prenatal massage, organic treatments only',
            'allergies': 'Latex sensitivity, chemical allergies',
            'notes': 'Pregnant customer, requires gentle treatments and special care'
        },
        {
            'first_name': 'Arjun',
            'last_name': 'Nair',
            'phone': '+91-9876543215',
            'email': 'arjun.nair@tech.com',
            'date_of_birth': date(1987, 11, 18),
            'gender': 'male',
            'address': '22, Tech Park Road, Bangalore, Karnataka 560001',
            'preferences': 'Stress relief massage, head massage',
            'allergies': 'None',
            'notes': 'Software engineer, high stress job, books weekly sessions'
        },
        {
            'first_name': 'Meera',
            'last_name': 'Joshi',
            'phone': '+91-9876543216',
            'email': 'meera.joshi@fashion.com',
            'date_of_birth': date(1994, 4, 25),
            'gender': 'female',
            'address': '33, Fashion Street, Pune, Maharashtra 411001',
            'preferences': 'Bridal packages, nail art, hair styling',
            'allergies': 'None',
            'notes': 'Fashion designer, image conscious, books complete makeover packages'
        },
        {
            'first_name': 'Karan',
            'last_name': 'Gupta',
            'phone': '+91-9876543217',
            'email': 'karan.gupta@business.com',
            'date_of_birth': date(1975, 9, 14),
            'gender': 'male',
            'address': '88, Business District, Gurgaon, Haryana 122001',
            'preferences': 'Executive grooming, beard styling',
            'allergies': 'Sensitive to hair products',
            'notes': 'Business executive, pays premium for quick services'
        },
        {
            'first_name': 'Shreya',
            'last_name': 'Iyer',
            'phone': '+91-9876543218',
            'email': 'shreya.iyer@college.edu',
            'date_of_birth': date(1998, 1, 20),
            'gender': 'female',
            'address': '12, Student Housing, Chennai, Tamil Nadu 600001',
            'preferences': 'Budget facials, basic manicure',
            'allergies': 'None',
            'notes': 'College student, price-sensitive, books during student discount offers'
        },
        {
            'first_name': 'Rajesh',
            'last_name': 'Agarwal',
            'phone': '+91-9876543219',
            'email': 'rajesh.agarwal@trade.com',
            'date_of_birth': date(1978, 6, 10),
            'gender': 'male',
            'address': '56, Trade Center, Kolkata, West Bengal 700001',
            'preferences': 'Traditional Ayurvedic treatments',
            'allergies': 'None',
            'notes': 'Traditional businessman, loyal customer for 3+ years, refers family'
        }
    ]
    
    with app.app_context():
        try:
            print("🏥 Adding 10 customers to the spa management database...")
            
            # Check existing customers to avoid duplicates
            existing_phones = set()
            for customer_data in customers_data:
                existing_customer = Customer.query.filter_by(phone=customer_data['phone']).first()
                if existing_customer:
                    existing_phones.add(customer_data['phone'])
                    print(f"⚠️  Customer with phone {customer_data['phone']} already exists: {existing_customer.first_name} {existing_customer.last_name}")
            
            # Add new customers with enhanced data
            added_count = 0
            for customer_data in customers_data:
                if customer_data['phone'] not in existing_phones:
                    # Add additional realistic data
                    customer_data.update({
                        'total_visits': random.randint(1, 15),
                        'total_spent': random.uniform(500.0, 8000.0),
                        'is_active': True,
                        'loyalty_points': random.randint(50, 500),
                        'is_vip': random.choice([True, False]),
                        'preferred_communication': random.choice(['email', 'sms', 'whatsapp']),
                        'marketing_consent': random.choice([True, False]),
                        'referral_source': random.choice(['Google', 'Facebook', 'Friend Referral', 'Walk-in', 'Instagram', 'Website']),
                        'last_visit': datetime.utcnow() - timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
                        'created_at': datetime.utcnow() - timedelta(days=random.randint(30, 365))
                    })
                    
                    customer = Customer(**customer_data)
                    db.session.add(customer)
                    added_count += 1
                    print(f"✅ Adding customer: {customer_data['first_name']} {customer_data['last_name']} ({customer_data['phone']})")
            
            if added_count > 0:
                db.session.commit()
                print(f"\n🎉 Successfully added {added_count} customers to the database!")
            else:
                print("\n⚠️  All customers already exist in the database.")
                
            # Display summary
            total_customers = Customer.query.filter_by(is_active=True).count()
            print(f"\n📊 Database Summary:")
            print(f"   • Total active customers: {total_customers}")
            
            # Show all customers
            all_customers = Customer.query.filter_by(is_active=True).order_by(Customer.first_name).all()
            print(f"\n👥 All customers in database:")
            for i, customer in enumerate(all_customers, 1):
                visits = customer.total_visits or 0
                spent = customer.total_spent or 0.0
                print(f"   {i:2d}. {customer.full_name:<25} | {customer.phone:<15} | {customer.email or 'No email':<25} | Visits: {visits:2d} | Spent: ₹{spent:,.0f}")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding customers: {str(e)}")
            raise

if __name__ == '__main__':
    # Import timedelta here to avoid import errors
    from datetime import timedelta
    add_10_customers()
