#!/usr/bin/env python3
"""
Script to add comprehensive spa packages, memberships, and offers
Including prepaid packages, memberships, student offers, and kitty party packages
"""

from app import app, db
from models import Service, Package, PackageService, Category
from datetime import datetime, timedelta
import json

def add_missing_services():
    """Add services specifically mentioned in packages but might be missing"""
    
    missing_services = [
        # Classic Services
        {'name': 'Classic Haircut', 'description': 'Traditional classic haircut', 'duration': 30, 'price': 25.00, 'category': 'hair_cuts_styling'},
        {'name': 'Classic Shave', 'description': 'Traditional classic shave', 'duration': 30, 'price': 20.00, 'category': 'hair_cuts_styling'},
        {'name': 'Classic Cleanup', 'description': 'Basic facial cleanup', 'duration': 45, 'price': 40.00, 'category': 'facial_treatments'},
        
        # Deluxe Services
        {'name': 'Deluxe Haircut', 'description': 'Premium deluxe haircut with styling', 'duration': 45, 'price': 40.00, 'category': 'hair_cuts_styling'},
        {'name': 'Deluxe Shave', 'description': 'Premium deluxe shave with hot towel', 'duration': 45, 'price': 35.00, 'category': 'hair_cuts_styling'},
        {'name': 'Deluxe Cleanup', 'description': 'Advanced facial cleanup treatment', 'duration': 60, 'price': 60.00, 'category': 'facial_treatments'},
        
        # Hair Services
        {'name': 'Hair Wash', 'description': 'Professional hair washing service', 'duration': 20, 'price': 15.00, 'category': 'hair_cuts_styling'},
        {'name': 'Hair Spa', 'description': 'Complete hair spa treatment', 'duration': 90, 'price': 80.00, 'category': 'hair_treatments'},
        {'name': 'Hair Rituals', 'description': 'Specialized hair ritual treatment', 'duration': 120, 'price': 100.00, 'category': 'hair_treatments'},
        
        # Body Services
        {'name': 'Hand Reflexology', 'description': 'Therapeutic hand reflexology', 'duration': 30, 'price': 30.00, 'category': 'body_massage'},
        {'name': 'Foot Reflexology', 'description': 'Therapeutic foot reflexology', 'duration': 45, 'price': 40.00, 'category': 'body_massage'},
    ]
    
    # Get category mappings
    categories = {}
    for cat in Category.query.filter_by(category_type='service').all():
        categories[cat.name] = cat.id
    
    added_count = 0
    existing_services = set(s.name.lower() for s in Service.query.all())
    
    for service_data in missing_services:
        if service_data['name'].lower() not in existing_services:
            category_id = categories.get(service_data['category'])
            service = Service(
                name=service_data['name'],
                description=service_data['description'],
                duration=service_data['duration'],
                price=service_data['price'],
                category=service_data['category'],
                category_id=category_id,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(service)
            added_count += 1
            print(f"Adding missing service: {service_data['name']} - ${service_data['price']}")
    
    if added_count > 0:
        db.session.commit()
        print(f"✅ Added {added_count} missing services")
    
    return added_count

def create_prepaid_packages():
    """Create prepaid credit packages with bonus amounts"""
    
    prepaid_packages = [
        {
            'name': 'Prepaid Spa Credits - ₹15K',
            'description': 'Pay ₹15,000 and get ₹17,500 in spa credits (15% bonus)',
            'package_type': 'prepaid',
            'total_price': 15000.00,
            'credit_amount': 17500.00,
            'validity_days': 60,  # 2 months
            'duration_months': 2,
            'discount_percentage': 15.0,
            'has_unlimited_sessions': True,
            'membership_benefits': json.dumps({
                'credit_amount': 17500,
                'bonus_percentage': 15,
                'validity_months': 2,
                'usage_terms': 'Can be used for any spa services'
            })
        },
        {
            'name': 'Prepaid Spa Credits - ₹20K',
            'description': 'Pay ₹20,000 and get ₹25,000 in spa credits (20% bonus)',
            'package_type': 'prepaid',
            'total_price': 20000.00,
            'credit_amount': 25000.00,
            'validity_days': 90,  # 3 months
            'duration_months': 3,
            'discount_percentage': 20.0,
            'has_unlimited_sessions': True,
            'membership_benefits': json.dumps({
                'credit_amount': 25000,
                'bonus_percentage': 20,
                'validity_months': 3,
                'usage_terms': 'Can be used for any spa services'
            })
        },
        {
            'name': 'Prepaid Spa Credits - ₹30K',
            'description': 'Pay ₹30,000 and get ₹40,000 in spa credits (25% bonus)',
            'package_type': 'prepaid',
            'total_price': 30000.00,
            'credit_amount': 40000.00,
            'validity_days': 120,  # 4 months
            'duration_months': 4,
            'discount_percentage': 25.0,
            'has_unlimited_sessions': True,
            'membership_benefits': json.dumps({
                'credit_amount': 40000,
                'bonus_percentage': 25,
                'validity_months': 4,
                'usage_terms': 'Can be used for any spa services'
            })
        },
        {
            'name': 'Prepaid Spa Credits - ₹50K',
            'description': 'Pay ₹50,000 and get ₹70,000 in spa credits (30% bonus)',
            'package_type': 'prepaid',
            'total_price': 50000.00,
            'credit_amount': 70000.00,
            'validity_days': 180,  # 6 months
            'duration_months': 6,
            'discount_percentage': 30.0,
            'has_unlimited_sessions': True,
            'membership_benefits': json.dumps({
                'credit_amount': 70000,
                'bonus_percentage': 30,
                'validity_months': 6,
                'usage_terms': 'Can be used for any spa services'
            })
        },
        {
            'name': 'Prepaid Spa Credits - ₹1L',
            'description': 'Pay ₹1,00,000 and get ₹1,50,000 in spa credits (35% bonus)',
            'package_type': 'prepaid',
            'total_price': 100000.00,
            'credit_amount': 150000.00,
            'validity_days': 365,  # 1 year
            'duration_months': 12,
            'discount_percentage': 35.0,
            'has_unlimited_sessions': True,
            'membership_benefits': json.dumps({
                'credit_amount': 150000,
                'bonus_percentage': 35,
                'validity_months': 12,
                'usage_terms': 'Can be used for any spa services'
            })
        }
    ]
    
    added_count = 0
    for pkg_data in prepaid_packages:
        existing_pkg = Package.query.filter_by(name=pkg_data['name']).first()
        if not existing_pkg:
            package = Package(**pkg_data)
            db.session.add(package)
            added_count += 1
            print(f"Adding prepaid package: {pkg_data['name']}")
    
    db.session.commit()
    return added_count

def create_service_packages():
    """Create service packages (pay for X get Y)"""
    
    service_packages = [
        {
            'name': 'Service Package - Pay 3 Get 4',
            'description': 'Pay for 3 services and get 1 free (25% benefit)',
            'package_type': 'regular',
            'total_sessions': 4,
            'validity_days': 90,
            'duration_months': 3,
            'discount_percentage': 25.0,
            'total_price': 0.0,  # Will be calculated based on selected services
            'membership_benefits': json.dumps({
                'pay_sessions': 3,
                'get_sessions': 4,
                'benefit_percentage': 25,
                'terms': 'Select any 3 services and get 4th service free'
            })
        },
        {
            'name': 'Service Package - Pay 6 Get 9',
            'description': 'Pay for 6 services and get 3 free (33% benefit)',
            'package_type': 'regular',
            'total_sessions': 9,
            'validity_days': 120,
            'duration_months': 4,
            'discount_percentage': 33.0,
            'total_price': 0.0,  # Will be calculated based on selected services
            'membership_benefits': json.dumps({
                'pay_sessions': 6,
                'get_sessions': 9,
                'benefit_percentage': 33,
                'terms': 'Select any 6 services and get 3 additional services free'
            })
        },
        {
            'name': 'Service Package - Pay 9 Get 15',
            'description': 'Pay for 9 services and get 6 free (40% benefit)',
            'package_type': 'regular',
            'total_sessions': 15,
            'validity_days': 180,
            'duration_months': 6,
            'discount_percentage': 40.0,
            'total_price': 0.0,  # Will be calculated based on selected services
            'membership_benefits': json.dumps({
                'pay_sessions': 9,
                'get_sessions': 15,
                'benefit_percentage': 40,
                'terms': 'Select any 9 services and get 6 additional services free'
            })
        }
    ]
    
    added_count = 0
    for pkg_data in service_packages:
        existing_pkg = Package.query.filter_by(name=pkg_data['name']).first()
        if not existing_pkg:
            package = Package(**pkg_data)
            db.session.add(package)
            added_count += 1
            print(f"Adding service package: {pkg_data['name']}")
    
    db.session.commit()
    return added_count

def create_membership_packages():
    """Create The Gentlemen's Club membership packages"""
    
    # Get service IDs for membership packages
    service_map = {s.name.lower(): s for s in Service.query.all()}
    
    membership_packages = [
        {
            'name': 'Classic Club Membership',
            'description': 'One year validity - Classic haircut, shave, color, manicure & pedicure, facial, cleanup',
            'package_type': 'membership',
            'total_price': 75000.00,
            'validity_days': 365,
            'duration_months': 12,
            'has_unlimited_sessions': True,
            'membership_benefits': json.dumps({
                'validity': '1 year',
                'services_included': [
                    'Classic Haircut', 'Classic Shave', 'Hair Color', 
                    'Basic Manicure', 'Basic Pedicure', 'Basic Facial', 'Classic Cleanup'
                ],
                'terms': 'Unlimited access to classic services for one year'
            }),
            'services': [
                {'service_name': 'classic haircut', 'sessions': -1, 'is_unlimited': True},
                {'service_name': 'classic shave', 'sessions': -1, 'is_unlimited': True},
                {'service_name': 'full hair color', 'sessions': -1, 'is_unlimited': True},
                {'service_name': 'basic manicure', 'sessions': -1, 'is_unlimited': True},
                {'service_name': 'basic pedicure', 'sessions': -1, 'is_unlimited': True},
                {'service_name': 'basic facial', 'sessions': -1, 'is_unlimited': True},
                {'service_name': 'classic cleanup', 'sessions': -1, 'is_unlimited': True}
            ]
        },
        {
            'name': 'Deluxe Club Membership',
            'description': 'One year validity - Deluxe haircut, shave, color, manicure & pedicure, facial, cleanup',
            'package_type': 'membership',
            'total_price': 90000.00,
            'validity_days': 365,
            'duration_months': 12,
            'has_unlimited_sessions': True,
            'membership_benefits': json.dumps({
                'validity': '1 year',
                'services_included': [
                    'Deluxe Haircut', 'Deluxe Shave', 'Hair Color', 
                    'Spa Manicure', 'Spa Pedicure', 'Anti-Aging Facial', 'Deluxe Cleanup'
                ],
                'terms': 'Unlimited access to deluxe services for one year'
            }),
            'services': [
                {'service_name': 'deluxe haircut', 'sessions': -1, 'is_unlimited': True},
                {'service_name': 'deluxe shave', 'sessions': -1, 'is_unlimited': True},
                {'service_name': 'full hair color', 'sessions': -1, 'is_unlimited': True},
                {'service_name': 'spa manicure', 'sessions': -1, 'is_unlimited': True},
                {'service_name': 'spa pedicure', 'sessions': -1, 'is_unlimited': True},
                {'service_name': 'anti-aging facial', 'sessions': -1, 'is_unlimited': True},
                {'service_name': 'deluxe cleanup', 'sessions': -1, 'is_unlimited': True}
            ]
        },
        {
            'name': 'The UNAKI Luxe Club',
            'description': 'One year validity - All services mentioned on the spa menu',
            'package_type': 'membership',
            'total_price': 125000.00,
            'validity_days': 365,
            'duration_months': 12,
            'has_unlimited_sessions': True,
            'membership_benefits': json.dumps({
                'validity': '1 year',
                'services_included': 'All spa services',
                'terms': 'Unlimited access to ALL spa services for one year'
            }),
            'services': []  # Will include all services
        }
    ]
    
    added_count = 0
    for pkg_data in membership_packages:
        existing_pkg = Package.query.filter_by(name=pkg_data['name']).first()
        if not existing_pkg:
            services_list = pkg_data.pop('services', [])
            package = Package(**pkg_data)
            db.session.add(package)
            db.session.flush()  # Get package ID
            
            # Add services to package
            if pkg_data['name'] == 'The UNAKI Luxe Club':
                # Add all services for Luxe Club
                for service in Service.query.filter_by(is_active=True).all():
                    package_service = PackageService(
                        package_id=package.id,
                        service_id=service.id,
                        sessions_included=999,  # High number for unlimited
                        is_unlimited=True,
                        original_price=service.price,
                        discounted_price=0.0,
                        service_discount=100.0
                    )
                    db.session.add(package_service)
            else:
                # Add specific services for Classic and Deluxe
                for svc in services_list:
                    service = service_map.get(svc['service_name'])
                    if service:
                        package_service = PackageService(
                            package_id=package.id,
                            service_id=service.id,
                            sessions_included=999,  # High number for unlimited
                            is_unlimited=svc['is_unlimited'],
                            original_price=service.price,
                            discounted_price=0.0,
                            service_discount=100.0
                        )
                        db.session.add(package_service)
            
            added_count += 1
            print(f"Adding membership: {pkg_data['name']}")
    
    db.session.commit()
    return added_count

def create_student_offers():
    """Create student discount packages"""
    
    student_packages = [
        {
            'name': 'Student Haircut Offer',
            'description': '50% off on Haircuts/Hair wash/Blow dry (Mon-Fri with valid student ID)',
            'package_type': 'student_offer',
            'total_price': 0.0,  # Dynamic pricing based on service
            'validity_days': 365,
            'duration_months': 12,
            'student_discount': 50.0,
            'membership_benefits': json.dumps({
                'discount': '50% off',
                'services': ['Haircuts', 'Hair wash', 'Blow dry'],
                'validity': 'Monday to Friday only',
                'requirements': 'Valid student ID required'
            })
        },
        {
            'name': 'Student Color & Streaks Offer',
            'description': '30% off on Color Streaks (Mon-Fri with valid student ID)',
            'package_type': 'student_offer',
            'total_price': 0.0,
            'validity_days': 365,
            'duration_months': 12,
            'student_discount': 30.0,
            'membership_benefits': json.dumps({
                'discount': '30% off',
                'services': ['Color Streaks'],
                'validity': 'Monday to Friday only',
                'requirements': 'Valid student ID required'
            })
        },
        {
            'name': 'Student Classic Mani-Pedi Offer',
            'description': '30% off on Classic Manicure & Pedicure (Mon-Fri with valid student ID)',
            'package_type': 'student_offer',
            'total_price': 0.0,
            'validity_days': 365,
            'duration_months': 12,
            'student_discount': 30.0,
            'membership_benefits': json.dumps({
                'discount': '30% off',
                'services': ['Classic Manicure', 'Classic Pedicure'],
                'validity': 'Monday to Friday only',
                'requirements': 'Valid student ID required'
            })
        },
        {
            'name': 'Student Deluxe Mani-Pedi Offer',
            'description': '40% off on Deluxe and Luxe Manicure & Pedicures (Mon-Fri with valid student ID)',
            'package_type': 'student_offer',
            'total_price': 0.0,
            'validity_days': 365,
            'duration_months': 12,
            'student_discount': 40.0,
            'membership_benefits': json.dumps({
                'discount': '40% off',
                'services': ['Deluxe Manicure', 'Deluxe Pedicure', 'Spa Manicure', 'Spa Pedicure'],
                'validity': 'Monday to Friday only',
                'requirements': 'Valid student ID required'
            })
        }
    ]
    
    added_count = 0
    for pkg_data in student_packages:
        existing_pkg = Package.query.filter_by(name=pkg_data['name']).first()
        if not existing_pkg:
            package = Package(**pkg_data)
            db.session.add(package)
            added_count += 1
            print(f"Adding student offer: {pkg_data['name']}")
    
    db.session.commit()
    return added_count

def create_yearly_salon_membership():
    """Create yearly salon membership with benefits"""
    
    yearly_membership = {
        'name': 'Yearly Salon Membership',
        'description': 'Pay ₹2000 and get 20% off on all salon services plus complimentary benefits',
        'package_type': 'membership',
        'total_price': 2000.00,
        'validity_days': 365,
        'duration_months': 12,
        'discount_percentage': 20.0,
        'has_unlimited_sessions': True,
        'membership_benefits': json.dumps({
            'annual_fee': 2000,
            'discount_on_services': '20% off all salon services',
            'complimentary_benefits': [
                'Classic manicure and pedicure',
                '12 Threading sessions',
                '4 Hair wash sessions',
                '2000 credit points'
            ],
            'validity': '1 year from purchase date'
        })
    }
    
    existing_pkg = Package.query.filter_by(name=yearly_membership['name']).first()
    if not existing_pkg:
        package = Package(**yearly_membership)
        db.session.add(package)
        db.session.commit()
        print(f"Adding yearly membership: {yearly_membership['name']}")
        return 1
    
    return 0

def create_kitty_party_packages():
    """Create kitty party packages"""
    
    kitty_packages = [
        {
            'name': 'Kitty Party Package - Basic',
            'description': 'Fun games, food, hair spa/rituals, mani & pedi services, hand & foot reflexology (Min 10 guests)',
            'package_type': 'kitty_party',
            'total_price': 50000.00,
            'validity_days': 30,
            'duration_months': 1,
            'min_guests': 10,
            'total_sessions': 10,  # Per guest
            'membership_benefits': json.dumps({
                'minimum_guests': 10,
                'starting_price': 50000,
                'includes': [
                    'Fun games and activities',
                    'Food and refreshments',
                    'Hair spa/rituals for all guests',
                    'Manicure & pedicure services',
                    'Hand & foot reflexology'
                ],
                'terms': 'Minimum 10 guests required, advance booking necessary'
            })
        },
        {
            'name': 'Kitty Party Package - Premium',
            'description': 'Enhanced kitty party with premium services and extended activities (Min 10 guests)',
            'package_type': 'kitty_party',
            'total_price': 75000.00,
            'validity_days': 30,
            'duration_months': 1,
            'min_guests': 10,
            'total_sessions': 10,
            'membership_benefits': json.dumps({
                'minimum_guests': 10,
                'starting_price': 75000,
                'includes': [
                    'Premium fun games and activities',
                    'Enhanced food and refreshments',
                    'Deluxe hair spa/rituals',
                    'Premium manicure & pedicure services',
                    'Extended hand & foot reflexology',
                    'Complimentary group photo session'
                ],
                'terms': 'Minimum 10 guests required, advance booking necessary'
            })
        },
        {
            'name': 'Kitty Party Package - Luxury',
            'description': 'Ultimate kitty party experience with luxury services and VIP treatment (Min 10 guests)',
            'package_type': 'kitty_party',
            'total_price': 100000.00,
            'validity_days': 30,
            'duration_months': 1,
            'min_guests': 10,
            'total_sessions': 10,
            'membership_benefits': json.dumps({
                'minimum_guests': 10,
                'starting_price': 100000,
                'includes': [
                    'Luxury games and entertainment',
                    'Gourmet food and premium refreshments',
                    'Luxury hair spa with premium products',
                    'Luxury manicure & pedicure with gel',
                    'Full body hand & foot reflexology',
                    'Professional group photo session',
                    'Personalized party favors',
                    'VIP lounge access'
                ],
                'terms': 'Minimum 10 guests required, advance booking necessary'
            })
        }
    ]
    
    added_count = 0
    for pkg_data in kitty_packages:
        existing_pkg = Package.query.filter_by(name=pkg_data['name']).first()
        if not existing_pkg:
            package = Package(**pkg_data)
            db.session.add(package)
            added_count += 1
            print(f"Adding kitty party package: {pkg_data['name']}")
    
    db.session.commit()
    return added_count

def add_all_packages():
    """Main function to add all packages"""
    
    with app.app_context():
        try:
            print("🚀 Starting comprehensive package creation...")
            
            # 1. Add missing services
            print("\n1️⃣ Adding missing services...")
            services_added = add_missing_services()
            
            # 2. Create prepaid packages
            print("\n2️⃣ Creating prepaid credit packages...")
            prepaid_added = create_prepaid_packages()
            
            # 3. Create service packages
            print("\n3️⃣ Creating service packages...")
            service_pkg_added = create_service_packages()
            
            # 4. Create membership packages
            print("\n4️⃣ Creating membership packages...")
            membership_added = create_membership_packages()
            
            # 5. Create student offers
            print("\n5️⃣ Creating student offers...")
            student_added = create_student_offers()
            
            # 6. Create yearly salon membership
            print("\n6️⃣ Creating yearly salon membership...")
            yearly_added = create_yearly_salon_membership()
            
            # 7. Create kitty party packages
            print("\n7️⃣ Creating kitty party packages...")
            kitty_added = create_kitty_party_packages()
            
            # Summary
            total_packages_added = (prepaid_added + service_pkg_added + membership_added + 
                                  student_added + yearly_added + kitty_added)
            
            print(f"\n✅ Package Creation Complete!")
            print(f"📊 Summary:")
            print(f"   - Missing Services Added: {services_added}")
            print(f"   - Prepaid Packages: {prepaid_added}")
            print(f"   - Service Packages: {service_pkg_added}")
            print(f"   - Membership Packages: {membership_added}")
            print(f"   - Student Offers: {student_added}")
            print(f"   - Yearly Membership: {yearly_added}")
            print(f"   - Kitty Party Packages: {kitty_added}")
            print(f"   - Total Packages Added: {total_packages_added}")
            
            # Display all packages by type
            print(f"\n📋 All Packages in Database:")
            for pkg_type in ['prepaid', 'regular', 'membership', 'student_offer', 'kitty_party']:
                packages = Package.query.filter_by(package_type=pkg_type, is_active=True).all()
                if packages:
                    print(f"   {pkg_type.title()}: {len(packages)} packages")
                    for pkg in packages:
                        print(f"     - {pkg.name}: ₹{pkg.total_price}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating packages: {str(e)}")
            raise e

if __name__ == "__main__":
    add_all_packages()