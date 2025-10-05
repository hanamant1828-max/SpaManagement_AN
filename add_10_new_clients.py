
#!/usr/bin/env python3
"""
Script to add 10 new diverse clients to the spa management system
"""

from app import app, db
from models import Customer
from datetime import date, datetime
import random

def add_10_new_clients():
    """Add 10 new diverse clients to the database"""
    
    clients_data = [
        {
            'first_name': 'Sophia',
            'last_name': 'Martinez',
            'phone': '+1-555-2001',
            'email': 'sophia.martinez@email.com',
            'date_of_birth': date(1992, 6, 18),
            'gender': 'female',
            'address': '789 Sunset Boulevard, Los Angeles, CA 90028',
            'preferences': 'Prefers organic products, loves aromatherapy sessions',
            'allergies': 'Sensitive to artificial fragrances',
            'notes': 'VIP client, prefers weekend appointments'
        },
        {
            'first_name': 'Oliver',
            'last_name': 'Thompson',
            'phone': '+1-555-2002',
            'email': 'oliver.thompson@email.com',
            'date_of_birth': date(1988, 9, 25),
            'gender': 'male',
            'address': '456 Park Avenue, New York, NY 10022',
            'preferences': 'Deep tissue massage, sports recovery treatments',
            'allergies': 'None known',
            'notes': 'Athlete, requires intensive muscle therapy'
        },
        {
            'first_name': 'Isabella',
            'last_name': 'Chen',
            'phone': '+1-555-2003',
            'email': 'isabella.chen@email.com',
            'date_of_birth': date(1995, 3, 12),
            'gender': 'female',
            'address': '123 Michigan Avenue, Chicago, IL 60601',
            'preferences': 'Anti-aging facials, premium skincare treatments',
            'allergies': 'Allergic to nuts in products',
            'notes': 'Fashion industry professional, image-conscious'
        },
        {
            'first_name': 'Liam',
            'last_name': 'O\'Brien',
            'phone': '+1-555-2004',
            'email': 'liam.obrien@email.com',
            'date_of_birth': date(1980, 11, 30),
            'gender': 'male',
            'address': '567 Market Street, San Francisco, CA 94102',
            'preferences': 'Hot stone massage, stress relief treatments',
            'allergies': 'None',
            'notes': 'Tech executive, often books last-minute appointments'
        },
        {
            'first_name': 'Ava',
            'last_name': 'Rodriguez',
            'phone': '+1-555-2005',
            'email': 'ava.rodriguez@email.com',
            'date_of_birth': date(1993, 7, 8),
            'gender': 'female',
            'address': '890 Ocean Drive, Miami, FL 33139',
            'preferences': 'Prenatal massage, gentle body treatments',
            'allergies': 'Latex sensitivity, avoid essential oils',
            'notes': 'Expecting mother, requires special positioning'
        },
        {
            'first_name': 'Noah',
            'last_name': 'Kim',
            'phone': '+1-555-2006',
            'email': 'noah.kim@email.com',
            'date_of_birth': date(1987, 2, 14),
            'gender': 'male',
            'address': '234 Peachtree Street, Atlanta, GA 30303',
            'preferences': 'Classic massage, beard grooming services',
            'allergies': 'None',
            'notes': 'Business professional, prefers early morning slots'
        },
        {
            'first_name': 'Mia',
            'last_name': 'Patel',
            'phone': '+1-555-2007',
            'email': 'mia.patel@email.com',
            'date_of_birth': date(1996, 10, 22),
            'gender': 'female',
            'address': '678 Main Street, Boston, MA 02108',
            'preferences': 'Nail art, gel manicures, creative designs',
            'allergies': 'None',
            'notes': 'Social media influencer, books regularly for content'
        },
        {
            'first_name': 'Ethan',
            'last_name': 'Davis',
            'phone': '+1-555-2008',
            'email': 'ethan.davis@email.com',
            'date_of_birth': date(1991, 4, 5),
            'gender': 'male',
            'address': '345 Broadway, Seattle, WA 98101',
            'preferences': 'Hair styling, scalp treatments',
            'allergies': 'Sensitive to hair dyes',
            'notes': 'Creative professional, experimental with styles'
        },
        {
            'first_name': 'Charlotte',
            'last_name': 'Anderson',
            'phone': '+1-555-2009',
            'email': 'charlotte.anderson@email.com',
            'date_of_birth': date(1985, 12, 16),
            'gender': 'female',
            'address': '901 Congress Avenue, Austin, TX 78701',
            'preferences': 'Full body massage, wellness packages',
            'allergies': 'None',
            'notes': 'Loyal customer for 2+ years, refers many friends'
        },
        {
            'first_name': 'Lucas',
            'last_name': 'White',
            'phone': '+1-555-2010',
            'email': 'lucas.white@email.com',
            'date_of_birth': date(1994, 8, 28),
            'gender': 'male',
            'address': '567 Colfax Avenue, Denver, CO 80202',
            'preferences': 'Couples massage, relaxation treatments',
            'allergies': 'None',
            'notes': 'Often books with partner, prefers weekend evenings'
        }
    ]
    
    with app.app_context():
        try:
            print("🏥 Adding 10 new clients to the spa management database...")
            
            # Check existing clients to avoid duplicates
            existing_phones = set()
            for client_data in clients_data:
                existing_client = Customer.query.filter_by(phone=client_data['phone']).first()
                if existing_client:
                    existing_phones.add(client_data['phone'])
                    print(f"⚠️  Client with phone {client_data['phone']} already exists: {existing_client.first_name} {existing_client.last_name}")
            
            # Add new clients with enhanced data
            added_count = 0
            for client_data in clients_data:
                if client_data['phone'] not in existing_phones:
                    # Add additional realistic data
                    client_data.update({
                        'total_visits': random.randint(1, 12),
                        'total_spent': random.uniform(500.0, 6000.0),
                        'is_active': True,
                        'loyalty_points': random.randint(50, 400),
                        'is_vip': random.choice([True, False]),
                        'preferred_communication': random.choice(['email', 'sms', 'whatsapp']),
                        'marketing_consent': random.choice([True, False]),
                        'referral_source': random.choice(['Google', 'Facebook', 'Instagram', 'Friend Referral', 'Walk-in', 'Yelp']),
                        'last_visit': datetime.utcnow() - timedelta(days=random.randint(1, 45)) if random.choice([True, False]) else None,
                        'created_at': datetime.utcnow() - timedelta(days=random.randint(30, 400))
                    })
                    
                    client = Customer(**client_data)
                    db.session.add(client)
                    added_count += 1
                    print(f"✅ Adding client: {client_data['first_name']} {client_data['last_name']} ({client_data['phone']})")
            
            if added_count > 0:
                db.session.commit()
                print(f"\n🎉 Successfully added {added_count} new clients to the database!")
            else:
                print("\n⚠️  All clients already exist in the database.")
                
            # Display summary
            total_clients = Customer.query.filter_by(is_active=True).count()
            print(f"\n📊 Database Summary:")
            print(f"   • Total active clients: {total_clients}")
            
            # Show all clients
            all_clients = Customer.query.filter_by(is_active=True).order_by(Customer.first_name).all()
            print(f"\n👥 All clients in database:")
            for i, client in enumerate(all_clients, 1):
                visits = client.total_visits or 0
                spent = client.total_spent or 0.0
                print(f"   {i:2d}. {client.full_name:<30} | {client.phone:<15} | {client.email or 'No email':<30} | Visits: {visits:2d} | Spent: ${spent:,.0f}")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding clients: {str(e)}")
            raise

if __name__ == '__main__':
    # Import timedelta here to avoid import errors
    from datetime import timedelta
    add_10_new_clients()
