
#!/usr/bin/env python3
"""
Script to create comprehensive spa packages for The Gentlemen's Club
Including prepaid packages, service packages, memberships, student offers, etc.
"""

from app import app, db
from models import Package, Service, PackageService, Category
from datetime import datetime

def create_spa_packages():
    """Create all spa packages as specified"""
    
    with app.app_context():
        print("Creating comprehensive spa packages...")
        
        # First, ensure we have some basic services
        create_basic_services()
        
        # 1. PREPAID CREDIT PACKAGES
        print("\n=== Creating Prepaid Credit Packages ===")
        prepaid_packages = [
            {
                'name': 'Prepaid ₹15,000',
                'pay': 15000, 'get': 17500, 'bonus': 15, 'validity': 60,
                'description': 'Pay ₹15,000 and get ₹17,500 credit (15% bonus) - 2 months validity'
            },
            {
                'name': 'Prepaid ₹20,000', 
                'pay': 20000, 'get': 25000, 'bonus': 20, 'validity': 90,
                'description': 'Pay ₹20,000 and get ₹25,000 credit (20% bonus) - 3 months validity'
            },
            {
                'name': 'Prepaid ₹30,000',
                'pay': 30000, 'get': 40000, 'bonus': 25, 'validity': 120,
                'description': 'Pay ₹30,000 and get ₹40,000 credit (25% bonus) - 4 months validity'
            },
            {
                'name': 'Prepaid ₹50,000',
                'pay': 50000, 'get': 70000, 'bonus': 30, 'validity': 180,
                'description': 'Pay ₹50,000 and get ₹70,000 credit (30% bonus) - 6 months validity'
            },
            {
                'name': 'Prepaid ₹1,00,000',
                'pay': 100000, 'get': 150000, 'bonus': 35, 'validity': 365,
                'description': 'Pay ₹1,00,000 and get ₹1,50,000 credit (35% bonus) - 1 year validity'
            }
        ]
        
        for pkg_data in prepaid_packages:
            existing = Package.query.filter_by(name=pkg_data['name']).first()
            if not existing:
                package = Package(
                    name=pkg_data['name'],
                    description=pkg_data['description'],
                    package_type='prepaid_credit',
                    validity_days=pkg_data['validity'],
                    duration_months=pkg_data['validity'] // 30,
                    prepaid_amount=pkg_data['pay'],
                    credit_amount=pkg_data['get'],
                    bonus_percentage=pkg_data['bonus'],
                    bonus_amount=pkg_data['get'] - pkg_data['pay'],
                    total_price=pkg_data['pay'],
                    total_sessions=0,
                    is_active=True
                )
                db.session.add(package)
                print(f"✓ Created: {pkg_data['name']}")
            else:
                print(f"- Already exists: {pkg_data['name']}")
        
        # 2. PREPAID SERVICE PACKAGES
        print("\n=== Creating Prepaid Service Packages ===")
        service_packages = [
            {
                'name': 'Pay for 3 Get 4 Sessions',
                'paid': 3, 'free': 1, 'total': 4, 'bonus': 25,
                'description': 'Pay for 3 sessions, get 4 total (25% benefit)'
            },
            {
                'name': 'Pay for 6 Get 9 Sessions',
                'paid': 6, 'free': 3, 'total': 9, 'bonus': 33,
                'description': 'Pay for 6 sessions, get 9 total (33% benefit)'
            },
            {
                'name': 'Pay for 9 Get 15 Sessions',
                'paid': 9, 'free': 6, 'total': 15, 'bonus': 40,
                'description': 'Pay for 9 sessions, get 15 total (40% benefit)'
            }
        ]
        
        for pkg_data in service_packages:
            existing = Package.query.filter_by(name=pkg_data['name']).first()
            if not existing:
                package = Package(
                    name=pkg_data['name'],
                    description=pkg_data['description'],
                    package_type='prepaid_service',
                    validity_days=90,
                    duration_months=3,
                    paid_sessions=pkg_data['paid'],
                    free_sessions=pkg_data['free'],
                    total_sessions=pkg_data['total'],
                    bonus_percentage=pkg_data['bonus'],
                    total_price=0,
                    is_active=True
                )
                db.session.add(package)
                print(f"✓ Created: {pkg_data['name']}")
            else:
                print(f"- Already exists: {pkg_data['name']}")
        
        # 3. THE GENTLEMEN'S CLUB MEMBERSHIPS
        print("\n=== Creating The Gentlemen's Club Memberships ===")
        memberships = [
            {
                'name': 'Classic Club Membership',
                'price': 75000,
                'description': 'Classic haircut, classic shave, colour, classic manicure & pedicure, classic facial, classic cleanup',
                'benefits': 'Unlimited classic services for 1 year'
            },
            {
                'name': 'Deluxe Club Membership', 
                'price': 90000,
                'description': 'Deluxe haircut, Deluxe shave, colour, Deluxe manicure & pedicure, Deluxe facial, Deluxe cleanup',
                'benefits': 'Unlimited deluxe services for 1 year'
            },
            {
                'name': 'The UNAKI Luxe Club',
                'price': 125000,
                'description': 'All services mentioned on the barber shop menu',
                'benefits': 'Unlimited access to all barber shop services for 1 year'
            }
        ]
        
        for membership in memberships:
            existing = Package.query.filter_by(name=membership['name']).first()
            if not existing:
                package = Package(
                    name=membership['name'],
                    description=membership['description'],
                    package_type='membership',
                    validity_days=365,
                    duration_months=12,
                    total_sessions=0,
                    total_price=membership['price'],
                    discount_percentage=0,
                    membership_benefits=membership['benefits'],
                    has_unlimited_sessions=True,
                    is_active=True
                )
                db.session.add(package)
                print(f"✓ Created: {membership['name']} - ₹{membership['price']:,}")
            else:
                print(f"- Already exists: {membership['name']}")
        
        # 4. STUDENT OFFERS
        print("\n=== Creating Student Offers ===")
        student_offers = [
            {
                'name': 'Student Haircuts/Hair Wash/Blow Dry - 50% Off',
                'discount': 50,
                'description': '50% off on Haircuts, Hair wash, Blow dry (Monday-Friday with valid student ID)',
                'services': 'Haircuts, Hair wash, Blow dry'
            },
            {
                'name': 'Student Colour Streaks - 30% Off',
                'discount': 30,
                'description': '30% off on colour and streaks (Monday-Friday with valid student ID)',
                'services': 'Colour and streaks'
            },
            {
                'name': 'Student Classic Manicure & Pedicure - 30% Off',
                'discount': 30,
                'description': '30% off on classic Manicure & Pedicure (Monday-Friday with valid student ID)',
                'services': 'Classic manicure and pedicure'
            },
            {
                'name': 'Student Deluxe & Luxe Nails - 40% Off',
                'discount': 40,
                'description': '40% off on deluxe and Luxe Manicure & Pedicures (Monday-Friday with valid student ID)',
                'services': 'Deluxe and luxe manicure & pedicures'
            }
        ]
        
        for offer in student_offers:
            existing = Package.query.filter_by(name=offer['name']).first()
            if not existing:
                package = Package(
                    name=offer['name'],
                    description=offer['description'],
                    package_type='student_offer',
                    validity_days=30,
                    duration_months=1,
                    total_sessions=1,
                    total_price=0,
                    discount_percentage=offer['discount'],
                    student_discount=offer['discount'],
                    membership_benefits=f"Valid Monday-Friday with student ID. Services: {offer['services']}",
                    is_active=True
                )
                db.session.add(package)
                print(f"✓ Created: {offer['name']}")
            else:
                print(f"- Already exists: {offer['name']}")
        
        # 5. YEARLY SALON MEMBERSHIP
        print("\n=== Creating Yearly Salon Membership ===")
        yearly_membership = Package.query.filter_by(name='Yearly Salon Membership').first()
        if not yearly_membership:
            yearly_membership = Package(
                name='Yearly Salon Membership',
                description='Pay ₹2000 and get 20% off on all salon services plus additional benefits',
                package_type='yearly_membership',
                validity_days=365,
                duration_months=12,
                total_sessions=17,  # 1 manicure + 1 pedicure + 12 threading + 4 hair wash - 1 (since we count pairs)
                total_price=2000,
                discount_percentage=20,
                membership_benefits='20% off all salon services + Complimentary classic manicure & pedicure + 12 threading sessions + 4 hair washes + 2000 credit points',
                prepaid_amount=2000,
                credit_amount=2000,
                bonus_amount=0,
                free_sessions=17,
                paid_sessions=0,
                is_active=True
            )
            db.session.add(yearly_membership)
            print("✓ Created: Yearly Salon Membership - ₹2,000")
        else:
            print("- Already exists: Yearly Salon Membership")
        
        # 6. KITTY PARTY PACKAGES
        print("\n=== Creating Kitty Party Packages ===")
        kitty_packages = [
            {
                'name': 'Kitty Party Package - Basic',
                'price': 50000,
                'guests': 10,
                'description': 'Fun games, food, hair spa/rituals, mani & pedi services, hand & foot reflexology'
            },
            {
                'name': 'Kitty Party Package - Premium',
                'price': 75000,
                'guests': 15,
                'description': 'Enhanced package with premium services, fun games, gourmet food, luxury hair spa/rituals, premium mani & pedi, hand & foot reflexology'
            },
            {
                'name': 'Kitty Party Package - Deluxe',
                'price': 100000,
                'guests': 20,
                'description': 'Ultimate kitty party experience with all premium services, entertainment, fine dining, luxury treatments'
            }
        ]
        
        for kitty in kitty_packages:
            existing = Package.query.filter_by(name=kitty['name']).first()
            if not existing:
                package = Package(
                    name=kitty['name'],
                    description=kitty['description'],
                    package_type='kitty_party',
                    validity_days=1,  # Single day event
                    duration_months=1,
                    total_sessions=1,
                    total_price=kitty['price'],
                    discount_percentage=0,
                    min_guests=kitty['guests'],
                    membership_benefits=f"Minimum {kitty['guests']} guests. Includes: {kitty['description']}",
                    is_active=True
                )
                db.session.add(package)
                print(f"✓ Created: {kitty['name']} - ₹{kitty['price']:,} (Min {kitty['guests']} guests)")
            else:
                print(f"- Already exists: {kitty['name']}")
        
        # Commit all packages
        try:
            db.session.commit()
            print(f"\n🎉 Successfully created all spa packages!")
            
            # Display summary
            total_packages = Package.query.count()
            prepaid_credit = Package.query.filter_by(package_type='prepaid_credit').count()
            prepaid_service = Package.query.filter_by(package_type='prepaid_service').count()
            memberships = Package.query.filter_by(package_type='membership').count()
            student_offers = Package.query.filter_by(package_type='student_offer').count()
            yearly_memberships = Package.query.filter_by(package_type='yearly_membership').count()
            kitty_parties = Package.query.filter_by(package_type='kitty_party').count()
            
            print(f"\n📊 Package Summary:")
            print(f"Total Packages: {total_packages}")
            print(f"Prepaid Credit: {prepaid_credit}")
            print(f"Prepaid Service: {prepaid_service}")
            print(f"Memberships: {memberships}")
            print(f"Student Offers: {student_offers}")
            print(f"Yearly Membership: {yearly_memberships}")
            print(f"Kitty Party: {kitty_parties}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating packages: {str(e)}")
            return False

def create_basic_services():
    """Create basic services if they don't exist"""
    basic_services = [
        {'name': 'Classic Haircut', 'price': 500, 'duration': 30, 'category': 'hair'},
        {'name': 'Deluxe Haircut', 'price': 800, 'duration': 45, 'category': 'hair'},
        {'name': 'Classic Shave', 'price': 300, 'duration': 20, 'category': 'grooming'},
        {'name': 'Deluxe Shave', 'price': 500, 'duration': 30, 'category': 'grooming'},
        {'name': 'Hair Colour', 'price': 1500, 'duration': 90, 'category': 'hair'},
        {'name': 'Hair Streaks', 'price': 2000, 'duration': 120, 'category': 'hair'},
        {'name': 'Classic Manicure', 'price': 800, 'duration': 45, 'category': 'nails'},
        {'name': 'Classic Pedicure', 'price': 1000, 'duration': 60, 'category': 'nails'},
        {'name': 'Deluxe Manicure', 'price': 1200, 'duration': 60, 'category': 'nails'},
        {'name': 'Deluxe Pedicure', 'price': 1500, 'duration': 75, 'category': 'nails'},
        {'name': 'Luxe Manicure', 'price': 1800, 'duration': 75, 'category': 'nails'},
        {'name': 'Luxe Pedicure', 'price': 2200, 'duration': 90, 'category': 'nails'},
        {'name': 'Classic Facial', 'price': 1500, 'duration': 60, 'category': 'skincare'},
        {'name': 'Deluxe Facial', 'price': 2200, 'duration': 75, 'category': 'skincare'},
        {'name': 'Classic Cleanup', 'price': 800, 'duration': 30, 'category': 'skincare'},
        {'name': 'Deluxe Cleanup', 'price': 1200, 'duration': 45, 'category': 'skincare'},
        {'name': 'Hair Wash', 'price': 200, 'duration': 15, 'category': 'hair'},
        {'name': 'Blow Dry', 'price': 400, 'duration': 20, 'category': 'hair'},
        {'name': 'Threading', 'price': 150, 'duration': 10, 'category': 'grooming'},
        {'name': 'Hair Spa', 'price': 2000, 'duration': 90, 'category': 'hair'},
        {'name': 'Hand Reflexology', 'price': 800, 'duration': 30, 'category': 'wellness'},
        {'name': 'Foot Reflexology', 'price': 1000, 'duration': 45, 'category': 'wellness'}
    ]
    
    created_services = 0
    for service_data in basic_services:
        existing = Service.query.filter_by(name=service_data['name']).first()
        if not existing:
            service = Service(
                name=service_data['name'],
                description=f"{service_data['name']} service",
                duration=service_data['duration'],
                price=service_data['price'],
                category=service_data['category'],
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(service)
            created_services += 1
    
    if created_services > 0:
        print(f"✓ Created {created_services} basic services")
    else:
        print("✓ All basic services already exist")

if __name__ == "__main__":
    try:
        success = create_spa_packages()
        if success:
            print("\n🎉 All spa packages have been successfully created!")
            print("\nYou can now view them in the Packages section of your spa management system.")
        else:
            print("\n❌ Some packages could not be created. Check the error messages above.")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
