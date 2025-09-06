
#!/usr/bin/env python3
"""
Script to add specific packages for spa management system
- Prepaid packages with credit amounts
- Selected service packages with session benefits
- Membership packages
- Student offers
- Yearly salon membership
- Kitty party packages
"""

from app import app, db
from models import Package, PackageService, Service, Category, CustomerPackage
from datetime import datetime

def clear_existing_packages():
    """Remove all existing packages"""
    print("🧹 Clearing existing packages...")
    
    # Delete customer packages first (foreign key constraint)
    CustomerPackage.query.delete()
    
    # Delete package services
    PackageService.query.delete()
    
    # Delete packages
    Package.query.delete()
    
    db.session.commit()
    print("✅ All existing packages cleared")

def create_prepaid_packages():
    """Create prepaid packages with credit amounts"""
    print("💳 Creating Prepaid Packages...")
    
    prepaid_packages = [
        {
            'name': 'Prepaid Package - 15K',
            'description': 'Pay 15,000 and get 17,500 credit with 15% benefit',
            'package_type': 'prepaid',
            'validity_days': 60,  # 2 months
            'total_price': 15000.0,
            'credit_amount': 17500.0,
            'discount_percentage': 15.0,
            'total_sessions': 1  # Prepaid packages are credit-based
        },
        {
            'name': 'Prepaid Package - 20K',
            'description': 'Pay 20,000 and get 25,000 credit with 20% benefit',
            'package_type': 'prepaid',
            'validity_days': 90,  # 3 months
            'total_price': 20000.0,
            'credit_amount': 25000.0,
            'discount_percentage': 20.0,
            'total_sessions': 1
        },
        {
            'name': 'Prepaid Package - 30K',
            'description': 'Pay 30,000 and get 40,000 credit with 25% benefit',
            'package_type': 'prepaid',
            'validity_days': 120,  # 4 months
            'total_price': 30000.0,
            'credit_amount': 40000.0,
            'discount_percentage': 25.0,
            'total_sessions': 1
        },
        {
            'name': 'Prepaid Package - 50K',
            'description': 'Pay 50,000 and get 70,000 credit with 30% benefit',
            'package_type': 'prepaid',
            'validity_days': 180,  # 6 months
            'total_price': 50000.0,
            'credit_amount': 70000.0,
            'discount_percentage': 30.0,
            'total_sessions': 1
        },
        {
            'name': 'Prepaid Package - 1 Lakh',
            'description': 'Pay 1,00,000 and get 1,50,000 credit with 35% benefit',
            'package_type': 'prepaid',
            'validity_days': 365,  # 1 year
            'total_price': 100000.0,
            'credit_amount': 150000.0,
            'discount_percentage': 35.0,
            'total_sessions': 1
        }
    ]
    
    for pkg_data in prepaid_packages:
        package = Package(
            name=pkg_data['name'],
            description=pkg_data['description'],
            package_type=pkg_data['package_type'],
            validity_days=pkg_data['validity_days'],
            duration_months=pkg_data['validity_days'] // 30,
            total_sessions=pkg_data['total_sessions'],
            total_price=pkg_data['total_price'],
            credit_amount=pkg_data['credit_amount'],
            discount_percentage=pkg_data['discount_percentage'],
            is_active=True
        )
        db.session.add(package)
    
    print(f"✅ Created {len(prepaid_packages)} prepaid packages")

def create_service_packages():
    """Create packages for selected services with session benefits"""
    print("🎯 Creating Service Packages...")
    
    service_packages = [
        {
            'name': 'Pay for 3 Get 1 Free',
            'description': 'Pay for 3 services and get 1 free - 25% benefit',
            'package_type': 'service_package',
            'validity_days': 90,
            'total_sessions': 4,  # Pay for 3, get 4 total
            'discount_percentage': 25.0,
            'sessions_paid': 3,
            'sessions_free': 1
        },
        {
            'name': 'Pay for 6 Get 3 Free',
            'description': 'Pay for 6 services and get 3 free - 33% benefit',
            'package_type': 'service_package',
            'validity_days': 120,
            'total_sessions': 9,  # Pay for 6, get 9 total
            'discount_percentage': 33.0,
            'sessions_paid': 6,
            'sessions_free': 3
        },
        {
            'name': 'Pay for 9 Get 6 Free',
            'description': 'Pay for 9 services and get 6 free - 40% benefit',
            'package_type': 'service_package',
            'validity_days': 180,
            'total_sessions': 15,  # Pay for 9, get 15 total
            'discount_percentage': 40.0,
            'sessions_paid': 9,
            'sessions_free': 6
        }
    ]
    
    for pkg_data in service_packages:
        # Calculate base price (will be updated when services are selected)
        base_price = pkg_data['sessions_paid'] * 2000  # Average service price
        
        package = Package(
            name=pkg_data['name'],
            description=pkg_data['description'],
            package_type=pkg_data['package_type'],
            validity_days=pkg_data['validity_days'],
            duration_months=pkg_data['validity_days'] // 30,
            total_sessions=pkg_data['total_sessions'],
            total_price=base_price,
            discount_percentage=pkg_data['discount_percentage'],
            is_active=True
        )
        db.session.add(package)
    
    print(f"✅ Created {len(service_packages)} service packages")

def create_membership_packages():
    """Create membership packages for The Gentlemen's Club"""
    print("👑 Creating Membership Packages...")
    
    # Get some services for membership packages
    classic_services = ['Hair Cut', 'Basic Facial', 'Basic Manicure', 'Basic Pedicure']
    deluxe_services = ['Hair Styling', 'Anti-Aging Facial', 'Gel Manicure', 'Spa Pedicure']
    
    membership_packages = [
        {
            'name': 'Classic Club Membership',
            'description': 'Classic haircut, shave, colour, manicure & pedicure, facial, cleanup - One year validity',
            'package_type': 'membership',
            'validity_days': 365,
            'total_price': 75000.0,
            'total_sessions': 50,  # Generous sessions for a year
            'membership_benefits': 'Classic services with priority booking and exclusive offers'
        },
        {
            'name': 'Deluxe Club Membership',
            'description': 'Deluxe haircut, shave, colour, manicure & pedicure, facial, cleanup - One year validity',
            'package_type': 'membership',
            'validity_days': 365,
            'total_price': 90000.0,
            'total_sessions': 60,
            'membership_benefits': 'Deluxe services with VIP treatment and premium products'
        },
        {
            'name': 'The UNAKI Luxe Club',
            'description': 'All services mentioned on the menu - One year validity',
            'package_type': 'membership',
            'validity_days': 365,
            'total_price': 125000.0,
            'total_sessions': 999,  # Unlimited access
            'has_unlimited_sessions': True,
            'membership_benefits': 'Unlimited access to all services with luxury experience'
        }
    ]
    
    for pkg_data in membership_packages:
        package = Package(
            name=pkg_data['name'],
            description=pkg_data['description'],
            package_type=pkg_data['package_type'],
            validity_days=pkg_data['validity_days'],
            duration_months=12,  # All memberships are yearly
            total_sessions=pkg_data['total_sessions'],
            total_price=pkg_data['total_price'],
            membership_benefits=pkg_data['membership_benefits'],
            has_unlimited_sessions=pkg_data.get('has_unlimited_sessions', False),
            is_active=True
        )
        db.session.add(package)
    
    print(f"✅ Created {len(membership_packages)} membership packages")

def create_student_offers():
    """Create student offer packages"""
    print("🎓 Creating Student Offers...")
    
    student_offers = [
        {
            'name': 'Student Haircut Offer',
            'description': '50% off on Haircuts, Hair wash, Blow dry (Monday-Friday with valid ID)',
            'package_type': 'student_offer',
            'validity_days': 30,
            'total_sessions': 5,
            'discount_percentage': 50.0,
            'student_discount': 50.0,
            'total_price': 2000.0  # Discounted rate
        },
        {
            'name': 'Student Color & Streaks Offer',
            'description': '30% off on colour and streaks (Monday-Friday with valid ID)',
            'package_type': 'student_offer',
            'validity_days': 30,
            'total_sessions': 3,
            'discount_percentage': 30.0,
            'student_discount': 30.0,
            'total_price': 5250.0  # Discounted rate
        },
        {
            'name': 'Student Classic Mani-Pedi Offer',
            'description': '30% off on classic Manicure & Pedicure (Monday-Friday with valid ID)',
            'package_type': 'student_offer',
            'validity_days': 30,
            'total_sessions': 4,
            'discount_percentage': 30.0,
            'student_discount': 30.0,
            'total_price': 5040.0  # Discounted rate
        },
        {
            'name': 'Student Deluxe Mani-Pedi Offer',
            'description': '40% off on deluxe and Luxe Manicure & Pedicures (Monday-Friday with valid ID)',
            'package_type': 'student_offer',
            'validity_days': 30,
            'total_sessions': 3,
            'discount_percentage': 40.0,
            'student_discount': 40.0,
            'total_price': 5400.0  # Discounted rate
        }
    ]
    
    for pkg_data in student_offers:
        package = Package(
            name=pkg_data['name'],
            description=pkg_data['description'],
            package_type=pkg_data['package_type'],
            validity_days=pkg_data['validity_days'],
            duration_months=1,
            total_sessions=pkg_data['total_sessions'],
            total_price=pkg_data['total_price'],
            discount_percentage=pkg_data['discount_percentage'],
            student_discount=pkg_data['student_discount'],
            is_active=True
        )
        db.session.add(package)
    
    print(f"✅ Created {len(student_offers)} student offer packages")

def create_yearly_salon_membership():
    """Create yearly salon membership"""
    print("💎 Creating Yearly Salon Membership...")
    
    yearly_membership = Package(
        name='Yearly Salon Membership',
        description='Pay 2000 and get 20% off on all salon services + complimentary benefits',
        package_type='yearly_membership',
        validity_days=365,
        duration_months=12,
        total_sessions=20,  # Includes complimentary services
        total_price=2000.0,
        credit_amount=2000.0,  # Credit points
        discount_percentage=20.0,
        membership_benefits='Complimentary classic manicure & pedicure, 12 threading sessions, 4 hair washes, 2000 credit points',
        is_active=True
    )
    
    db.session.add(yearly_membership)
    print("✅ Created yearly salon membership")

def create_kitty_party_packages():
    """Create kitty party packages"""
    print("🎉 Creating Kitty Party Packages...")
    
    kitty_packages = [
        {
            'name': 'Kitty Party Package - Basic',
            'description': 'Hair spa/rituals, mani & pedi services, hand & foot reflexology (Min 10 guests)',
            'package_type': 'kitty_party',
            'validity_days': 1,  # Single event
            'total_price': 50000.0,
            'min_guests': 10,
            'total_sessions': 10  # Per guest
        },
        {
            'name': 'Kitty Party Package - Deluxe',
            'description': 'Premium hair spa/rituals, luxury mani & pedi, reflexology + fun games/food (Min 10 guests)',
            'package_type': 'kitty_party',
            'validity_days': 1,
            'total_price': 75000.0,
            'min_guests': 10,
            'total_sessions': 15
        },
        {
            'name': 'Kitty Party Package - Premium',
            'description': 'Complete spa experience with all services, premium food & entertainment (Min 10 guests)',
            'package_type': 'kitty_party',
            'validity_days': 1,
            'total_price': 100000.0,
            'min_guests': 10,
            'total_sessions': 20
        }
    ]
    
    for pkg_data in kitty_packages:
        package = Package(
            name=pkg_data['name'],
            description=pkg_data['description'],
            package_type=pkg_data['package_type'],
            validity_days=pkg_data['validity_days'],
            duration_months=1,
            total_sessions=pkg_data['total_sessions'],
            total_price=pkg_data['total_price'],
            min_guests=pkg_data['min_guests'],
            is_active=True
        )
        db.session.add(package)
    
    print(f"✅ Created {len(kitty_packages)} kitty party packages")

def main():
    """Main function to create all specific packages"""
    with app.app_context():
        print("🚀 Starting specific package creation...")
        
        # Clear existing packages first
        clear_existing_packages()
        
        # Create all new package types
        create_prepaid_packages()
        create_service_packages()
        create_membership_packages()
        create_student_offers()
        create_yearly_salon_membership()
        create_kitty_party_packages()
        
        # Commit all changes
        db.session.commit()
        
        # Summary
        total_packages = Package.query.count()
        print(f"\n🎯 Package creation completed!")
        print(f"📊 Total packages created: {total_packages}")
        
        # Print package breakdown
        package_types = {}
        for package in Package.query.all():
            pkg_type = package.package_type
            if pkg_type not in package_types:
                package_types[pkg_type] = 0
            package_types[pkg_type] += 1
        
        print("\n📋 Package breakdown:")
        for pkg_type, count in package_types.items():
            print(f"   - {pkg_type.replace('_', ' ').title()}: {count} packages")
        
        print("\n✅ All specific packages have been created successfully!")
        print("🎉 Your spa package management is now ready with the exact packages you specified!")

if __name__ == "__main__":
    main()
