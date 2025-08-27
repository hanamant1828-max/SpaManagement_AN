#!/usr/bin/env python3
"""
Add sample clients to the spa/salon management system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Customer # Corrected import statement
from datetime import datetime, date

def add_sample_clients():
    """Add diverse sample clients to the database"""

    sample_clients = [
        {
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'email': 'sarah.johnson@email.com',
            'phone': '+1-555-0101',
            'date_of_birth': date(1985, 3, 15),
            'gender': 'female',
            'address': '123 Main St, Downtown City, NY 10001',
            'preferences': 'Prefers relaxing spa treatments, loves aromatherapy',
            'allergies': 'Sensitive to strong fragrances',
            'notes': 'Regular client, prefers afternoon appointments',
            'preferred_communication': 'email',
            'marketing_consent': True,
            'referral_source': 'google',
            'total_visits': 8,
            'total_spent': 650.00,
            'loyalty_points': 65,
            'is_vip': False
        },
        {
            'first_name': 'Maria',
            'last_name': 'Rodriguez',
            'email': 'maria.rodriguez@email.com',
            'phone': '+1-555-0102',
            'date_of_birth': date(1992, 7, 22),
            'gender': 'female',
            'address': '456 Oak Ave, Riverside, CA 92501',
            'preferences': 'Facial treatments, anti-aging services',
            'allergies': 'None known',
            'notes': 'Works flexible hours, available weekends',
            'preferred_communication': 'sms',
            'marketing_consent': True,
            'referral_source': 'friend_referral',
            'total_visits': 12,
            'total_spent': 890.00,
            'loyalty_points': 89,
            'is_vip': True
        },
        {
            'first_name': 'Jennifer',
            'last_name': 'Smith',
            'email': 'jen.smith@email.com',
            'phone': '+1-555-0103',
            'date_of_birth': date(1978, 11, 8),
            'gender': 'female',
            'address': '789 Pine St, Mountain View, CO 80424',
            'preferences': 'Hair coloring, styling, spa packages',
            'allergies': 'Allergic to latex gloves',
            'notes': 'Busy mom, prefers quick services during school hours',
            'preferred_communication': 'whatsapp',
            'marketing_consent': False,
            'referral_source': 'social_media',
            'total_visits': 15,
            'total_spent': 1250.00,
            'loyalty_points': 125,
            'is_vip': True
        },
        {
            'first_name': 'Ashley',
            'last_name': 'Davis',
            'email': 'ashley.davis@email.com',
            'phone': '+1-555-0104',
            'date_of_birth': date(1996, 1, 30),
            'gender': 'female',
            'address': '321 Elm Dr, Sunset Beach, FL 33426',
            'preferences': 'Manicures, pedicures, eyebrow threading',
            'allergies': 'Sensitive skin, no harsh chemicals',
            'notes': 'College student, budget-conscious',
            'preferred_communication': 'email',
            'marketing_consent': True,
            'referral_source': 'walk_in',
            'total_visits': 4,
            'total_spent': 180.00,
            'loyalty_points': 18,
            'is_vip': False
        },
        {
            'first_name': 'Lisa',
            'last_name': 'Thompson',
            'email': 'lisa.thompson@email.com',
            'phone': '+1-555-0105',
            'date_of_birth': date(1988, 9, 12),
            'gender': 'female',
            'address': '654 Maple Ln, Green Valley, AZ 85614',
            'preferences': 'Full body massages, hot stone therapy',
            'allergies': 'None',
            'notes': 'Stress relief treatments, works in healthcare',
            'preferred_communication': 'phone',
            'marketing_consent': True,
            'referral_source': 'advertisement',
            'total_visits': 6,
            'total_spent': 420.00,
            'loyalty_points': 42,
            'is_vip': False
        },
        {
            'first_name': 'Amanda',
            'last_name': 'Wilson',
            'email': 'amanda.wilson@email.com',
            'phone': '+1-555-0106',
            'date_of_birth': date(1983, 5, 25),
            'gender': 'female',
            'address': '987 Cedar St, Lake Town, MI 49230',
            'preferences': 'Bridal packages, special event styling',
            'allergies': 'Shellfish allergy (affects some skincare products)',
            'notes': 'Getting married next year, planning wedding beauty timeline',
            'preferred_communication': 'email',
            'marketing_consent': True,
            'referral_source': 'friend_referral',
            'total_visits': 3,
            'total_spent': 275.00,
            'loyalty_points': 28,
            'is_vip': False
        },
        {
            'first_name': 'Rachel',
            'last_name': 'Brown',
            'email': 'rachel.brown@email.com',
            'phone': '+1-555-0107',
            'date_of_birth': date(1975, 12, 3),
            'gender': 'female',
            'address': '147 Birch Rd, Hillside, TX 75001',
            'preferences': 'Anti-aging treatments, luxury spa experiences',
            'allergies': 'No known allergies',
            'notes': 'Executive, values premium services and privacy',
            'preferred_communication': 'email',
            'marketing_consent': True,
            'referral_source': 'repeat_client',
            'total_visits': 20,
            'total_spent': 2100.00,
            'loyalty_points': 210,
            'is_vip': True
        },
        {
            'first_name': 'Emma',
            'last_name': 'Taylor',
            'email': 'emma.taylor@email.com',
            'phone': '+1-555-0108',
            'date_of_birth': date(1990, 4, 18),
            'gender': 'female',
            'address': '258 Willow Way, Riverside, WA 98052',
            'preferences': 'Organic and natural treatments only',
            'allergies': 'Multiple chemical sensitivities',
            'notes': 'Prefers eco-friendly products, very health-conscious',
            'preferred_communication': 'sms',
            'marketing_consent': False,
            'referral_source': 'google',
            'total_visits': 7,
            'total_spent': 490.00,
            'loyalty_points': 49,
            'is_vip': False
        },
        {
            'first_name': 'Michelle',
            'last_name': 'Anderson',
            'email': 'michelle.anderson@email.com',
            'phone': '+1-555-0109',
            'date_of_birth': date(1987, 8, 7),
            'gender': 'female',
            'address': '369 Spruce Ave, Mountain Ridge, UT 84003',
            'preferences': 'Hair treatments, scalp therapy, hair extensions',
            'allergies': 'Allergic to PPD in hair dyes',
            'notes': 'Hair loss concerns, needs gentle treatments',
            'preferred_communication': 'whatsapp',
            'marketing_consent': True,
            'referral_source': 'social_media',
            'total_visits': 9,
            'total_spent': 720.00,
            'loyalty_points': 72,
            'is_vip': False
        },
        {
            'first_name': 'Nicole',
            'last_name': 'Garcia',
            'email': 'nicole.garcia@email.com',
            'phone': '+1-555-0110',
            'date_of_birth': date(1994, 2, 14),
            'gender': 'female',
            'address': '741 Poplar St, Sunny Hills, NV 89015',
            'preferences': 'Acne treatments, skin rejuvenation',
            'allergies': 'Sensitive to retinoids',
            'notes': 'Young professional, interested in preventative skincare',
            'preferred_communication': 'email',
            'marketing_consent': True,
            'referral_source': 'walk_in',
            'total_visits': 5,
            'total_spent': 325.00,
            'loyalty_points': 33,
            'is_vip': False
        }
    ]

    with app.app_context():
        added_count = 0

        for client_data in sample_clients:
            # Check if client already exists (by phone number)
            existing_client = Customer.query.filter_by(phone=client_data['phone']).first() # Corrected to Customer

            if not existing_client:
                try:
                    client = Customer(**client_data) # Corrected to Customer
                    client.created_at = datetime.utcnow()
                    client.is_active = True

                    db.session.add(client)
                    db.session.commit()

                    print(f"✓ Added client: {client.full_name} ({client.phone})")
                    added_count += 1

                except Exception as e:
                    print(f"✗ Error adding {client_data['first_name']} {client_data['last_name']}: {e}")
                    db.session.rollback()
            else:
                print(f"- Client {client_data['first_name']} {client_data['last_name']} already exists")

        print(f"\n📊 Summary: Added {added_count} new clients to the database")

        # Show total client count
        total_clients = Customer.query.filter_by(is_active=True).count() # Corrected to Customer
        print(f"📈 Total active clients in database: {total_clients}")

if __name__ == "__main__":
    print("🏥 Adding Sample Clients to Spa/Salon Management System")
    print("=" * 55)
    add_sample_clients()
    print("=" * 55)
    print("✅ Sample clients addition completed!")