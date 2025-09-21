
#!/usr/bin/env python3
"""
Script to create The Gentlemen's Club membership packages and student offers
"""

from app import app, db
from models import Package, Service, PackageService
from datetime import datetime

def create_gentlemens_club_packages():
    """Create The Gentlemen's Club membership packages"""
    
    with app.app_context():
        print("Creating The Gentlemen's Club membership packages...")
        
        # 1. Classic Club Membership - ₹75,000
        classic_membership = Package(
            name="Classic Club Membership",
            description="Classic haircut, classic shave, colour, classic manicure & pedicure, classic facial, classic cleanup - One year validity",
            package_type="membership",
            validity_days=365,
            duration_months=12,
            total_sessions=0,  # Unlimited sessions for membership
            total_price=75000.0,
            discount_percentage=0.0,
            membership_benefits="Classic services included: haircut, shave, colour, manicure & pedicure, facial, cleanup",
            has_unlimited_sessions=True,
            is_active=True
        )
        
        # 2. Deluxe Club Membership - ₹90,000
        deluxe_membership = Package(
            name="Deluxe Club Membership",
            description="Deluxe haircut, Deluxe shave, colour, Deluxe manicure & pedicure, Deluxe facial, Deluxe cleanup - One year validity",
            package_type="membership",
            validity_days=365,
            duration_months=12,
            total_sessions=0,  # Unlimited sessions for membership
            total_price=90000.0,
            discount_percentage=0.0,
            membership_benefits="Deluxe services included: haircut, shave, colour, manicure & pedicure, facial, cleanup",
            has_unlimited_sessions=True,
            is_active=True
        )
        
        # 3. The UNAKI Luxe Club - ₹1,25,000
        luxe_membership = Package(
            name="The UNAKI Luxe Club",
            description="All services mentioned on the barber shop menu - One year validity",
            package_type="membership",
            validity_days=365,
            duration_months=12,
            total_sessions=0,  # Unlimited sessions for membership
            total_price=125000.0,
            discount_percentage=0.0,
            membership_benefits="All barber shop services included - Complete luxury experience",
            has_unlimited_sessions=True,
            is_active=True
        )
        
        # Student Offer Packages (Monday-Friday)
        student_haircut_offer = Package(
            name="Student Haircut/Hair Wash/Blow Dry - 50% Off",
            description="50% discount on haircuts, hair wash, and blow dry services (Monday-Friday with valid student ID)",
            package_type="student_offer",
            validity_days=30,
            duration_months=1,
            total_sessions=1,
            total_price=0.0,  # Price calculated based on service selection
            discount_percentage=50.0,
            student_discount=50.0,
            membership_benefits="Valid Monday-Friday with student ID",
            is_active=True
        )
        
        student_colour_offer = Package(
            name="Student Colour Streaks - 30% Off",
            description="30% discount on colour and streaks (Monday-Friday with valid student ID)",
            package_type="student_offer",
            validity_days=30,
            duration_months=1,
            total_sessions=1,
            total_price=0.0,
            discount_percentage=30.0,
            student_discount=30.0,
            membership_benefits="Valid Monday-Friday with student ID",
            is_active=True
        )
        
        student_classic_nails_offer = Package(
            name="Student Classic Manicure & Pedicure - 30% Off",
            description="30% discount on classic manicure & pedicure (Monday-Friday with valid student ID)",
            package_type="student_offer",
            validity_days=30,
            duration_months=1,
            total_sessions=1,
            total_price=0.0,
            discount_percentage=30.0,
            student_discount=30.0,
            membership_benefits="Valid Monday-Friday with student ID",
            is_active=True
        )
        
        student_premium_nails_offer = Package(
            name="Student Deluxe & Luxe Nails - 40% Off",
            description="40% discount on deluxe and luxe manicure & pedicures (Monday-Friday with valid student ID)",
            package_type="student_offer",
            validity_days=30,
            duration_months=1,
            total_sessions=1,
            total_price=0.0,
            discount_percentage=40.0,
            student_discount=40.0,
            membership_benefits="Valid Monday-Friday with student ID",
            is_active=True
        )
        
        # Yearly Salon Membership
        yearly_salon_membership = Package(
            name="Yearly Salon Membership",
            description="Pay ₹2000 and get 20% off on all salon services plus additional benefits",
            package_type="yearly_membership",
            validity_days=365,
            duration_months=12,
            total_sessions=0,  # Based on specific included services
            total_price=2000.0,
            discount_percentage=20.0,
            membership_benefits="20% off all salon services + Complimentary classic manicure & pedicure + 12 threading sessions + 4 hair washes + 2000 credit points",
            prepaid_amount=2000.0,
            credit_amount=2000.0,  # Credit points
            bonus_amount=0.0,
            free_sessions=17,  # 1 manicure + 1 pedicure + 12 threading + 4 hair wash = 18 total
            paid_sessions=0,
            is_active=True
        )
        
        # Add all packages to database
        packages = [
            classic_membership,
            deluxe_membership,
            luxe_membership,
            student_haircut_offer,
            student_colour_offer,
            student_classic_nails_offer,
            student_premium_nails_offer,
            yearly_salon_membership
        ]
        
        created_count = 0
        for package in packages:
            # Check if package already exists
            existing = Package.query.filter_by(name=package.name).first()
            if not existing:
                db.session.add(package)
                created_count += 1
                print(f"✓ Created: {package.name}")
            else:
                print(f"⚠ Already exists: {package.name}")
        
        if created_count > 0:
            db.session.commit()
            print(f"\n🎉 Successfully created {created_count} new membership packages!")
        else:
            print("\n✅ All packages already exist in the database.")
        
        return True

def create_barber_services():
    """Create essential barber shop services if they don't exist"""
    
    with app.app_context():
        print("Creating essential barber shop services...")
        
        essential_services = [
            # Classic Services
            {'name': 'Classic Haircut', 'description': 'Traditional men\'s haircut', 'duration': 30, 'price': 500.0, 'category': 'hair'},
            {'name': 'Classic Shave', 'description': 'Traditional wet shave with razor', 'duration': 20, 'price': 300.0, 'category': 'grooming'},
            {'name': 'Classic Facial', 'description': 'Basic facial cleansing and moisturizing', 'duration': 45, 'price': 800.0, 'category': 'skincare'},
            {'name': 'Classic Cleanup', 'description': 'Basic face cleanup and grooming', 'duration': 30, 'price': 400.0, 'category': 'grooming'},
            {'name': 'Classic Manicure', 'description': 'Basic hand and nail care', 'duration': 30, 'price': 600.0, 'category': 'nails'},
            {'name': 'Classic Pedicure', 'description': 'Basic foot and nail care', 'duration': 45, 'price': 700.0, 'category': 'nails'},
            
            # Deluxe Services
            {'name': 'Deluxe Haircut', 'description': 'Premium styling and haircut', 'duration': 45, 'price': 800.0, 'category': 'hair'},
            {'name': 'Deluxe Shave', 'description': 'Premium shave with hot towel treatment', 'duration': 30, 'price': 500.0, 'category': 'grooming'},
            {'name': 'Deluxe Facial', 'description': 'Premium facial with advanced treatment', 'duration': 60, 'price': 1200.0, 'category': 'skincare'},
            {'name': 'Deluxe Cleanup', 'description': 'Premium cleanup with additional treatments', 'duration': 45, 'price': 600.0, 'category': 'grooming'},
            {'name': 'Deluxe Manicure', 'description': 'Premium hand care with spa treatment', 'duration': 45, 'price': 900.0, 'category': 'nails'},
            {'name': 'Deluxe Pedicure', 'description': 'Premium foot care with spa treatment', 'duration': 60, 'price': 1000.0, 'category': 'nails'},
            
            # Hair Services
            {'name': 'Hair Wash', 'description': 'Professional hair washing', 'duration': 15, 'price': 200.0, 'category': 'hair'},
            {'name': 'Blow Dry', 'description': 'Professional hair blow drying and styling', 'duration': 20, 'price': 300.0, 'category': 'hair'},
            {'name': 'Hair Colour', 'description': 'Professional hair coloring', 'duration': 90, 'price': 1500.0, 'category': 'hair'},
            {'name': 'Colour Streaks', 'description': 'Hair highlights and streaks', 'duration': 120, 'price': 2000.0, 'category': 'hair'},
            {'name': 'Threading', 'description': 'Eyebrow and facial hair threading', 'duration': 15, 'price': 150.0, 'category': 'grooming'},
            
            # Luxe Services
            {'name': 'Luxe Manicure', 'description': 'Luxury hand treatment with premium products', 'duration': 60, 'price': 1200.0, 'category': 'nails'},
            {'name': 'Luxe Pedicure', 'description': 'Luxury foot treatment with premium products', 'duration': 75, 'price': 1400.0, 'category': 'nails'},
        ]
        
        created_count = 0
        for service_data in essential_services:
            existing = Service.query.filter_by(name=service_data['name']).first()
            if not existing:
                service = Service(
                    name=service_data['name'],
                    description=service_data['description'],
                    duration=service_data['duration'],
                    price=service_data['price'],
                    category=service_data['category'],
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.session.add(service)
                created_count += 1
                print(f"✓ Created service: {service_data['name']}")
            else:
                print(f"⚠ Service already exists: {service_data['name']}")
        
        if created_count > 0:
            db.session.commit()
            print(f"\n🎉 Successfully created {created_count} new services!")
        else:
            print("\n✅ All services already exist in the database.")
        
        return True

if __name__ == "__main__":
    try:
        # First create essential services
        create_barber_services()
        print("\n" + "="*50 + "\n")
        
        # Then create membership packages
        create_gentlemens_club_packages()
        
        print("\n🎉 All membership packages and services have been set up successfully!")
        print("\nThe following packages are now available:")
        print("1. Classic Club Membership - ₹75,000 (1 year)")
        print("2. Deluxe Club Membership - ₹90,000 (1 year)")
        print("3. The UNAKI Luxe Club - ₹1,25,000 (1 year)")
        print("4. Student Offers (50%, 30%, 40% discounts)")
        print("5. Yearly Salon Membership - ₹2,000 (20% off + benefits)")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
