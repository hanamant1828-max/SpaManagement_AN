"""
Create comprehensive spa packages based on the user requirements:
- Prepaid packages (5 tiers)
- Service packages (3 tiers)
- Memberships (3 clubs)
- Student offers
- Yearly salon membership
- Kitty party packages
"""
from app import app, db
from models import Package, Service, PackageService
from datetime import datetime
import json

def create_comprehensive_spa_packages():
    with app.app_context():
        print("Creating comprehensive spa packages...")
        
        # Ensure we have some basic services first
        ensure_basic_services()
        
        # 1. PREPAID PACKAGES (Spa Only)
        create_prepaid_packages()
        
        # 2. SERVICE PACKAGES (Pay for X get Y)
        create_service_packages()
        
        # 3. MEMBERSHIP PACKAGES (The Gentlemen's Club)
        create_membership_packages()
        
        # 4. STUDENT OFFERS
        create_student_offers()
        
        # 5. YEARLY SALON MEMBERSHIP
        create_yearly_salon_membership()
        
        # 6. KITTY PARTY PACKAGES
        create_kitty_party_packages()
        
        print("✅ All comprehensive spa packages created successfully!")

def ensure_basic_services():
    """Ensure basic services exist in the database"""
    basic_services = [
        {"name": "Classic Haircut", "price": 500, "duration": 45, "category": "Hair Services"},
        {"name": "Deluxe Haircut", "price": 800, "duration": 60, "category": "Hair Services"},
        {"name": "Classic Shave", "price": 300, "duration": 30, "category": "Grooming"},
        {"name": "Deluxe Shave", "price": 500, "duration": 45, "category": "Grooming"},
        {"name": "Hair Colour", "price": 1500, "duration": 90, "category": "Hair Services"},
        {"name": "Hair Colour Streaks", "price": 2000, "duration": 120, "category": "Hair Services"},
        {"name": "Classic Manicure", "price": 600, "duration": 45, "category": "Nail Care"},
        {"name": "Classic Pedicure", "price": 800, "duration": 60, "category": "Nail Care"},
        {"name": "Deluxe Manicure", "price": 1000, "duration": 60, "category": "Nail Care"},
        {"name": "Deluxe Pedicure", "price": 1200, "duration": 75, "category": "Nail Care"},
        {"name": "Luxe Manicure", "price": 1500, "duration": 90, "category": "Nail Care"},
        {"name": "Luxe Pedicure", "price": 1800, "duration": 120, "category": "Nail Care"},
        {"name": "Classic Facial", "price": 1200, "duration": 60, "category": "Facial"},
        {"name": "Deluxe Facial", "price": 1800, "duration": 90, "category": "Facial"},
        {"name": "Classic Cleanup", "price": 800, "duration": 45, "category": "Facial"},
        {"name": "Deluxe Cleanup", "price": 1200, "duration": 60, "category": "Facial"},
        {"name": "Hair Wash", "price": 200, "duration": 20, "category": "Hair Services"},
        {"name": "Blow Dry", "price": 400, "duration": 30, "category": "Hair Services"},
        {"name": "Hair Spa", "price": 2000, "duration": 120, "category": "Hair Services"},
        {"name": "Hair Ritual", "price": 2500, "duration": 150, "category": "Hair Services"},
        {"name": "Hand Reflexology", "price": 800, "duration": 45, "category": "Wellness"},
        {"name": "Foot Reflexology", "price": 1000, "duration": 60, "category": "Wellness"},
        {"name": "Threading", "price": 150, "duration": 15, "category": "Grooming"},
        {"name": "Full Body Massage", "price": 3000, "duration": 120, "category": "Wellness"},
    ]
    
    for service_data in basic_services:
        existing_service = Service.query.filter_by(name=service_data['name']).first()
        if not existing_service:
            service = Service(
                name=service_data['name'],
                description=f"Professional {service_data['name'].lower()}",
                price=service_data['price'],
                duration=service_data['duration'],
                category=service_data['category'],
                is_active=True
            )
            db.session.add(service)
    
    db.session.commit()
    print("✅ Basic services ensured in database")

def create_prepaid_packages():
    """Create 5 prepaid spa packages"""
    prepaid_packages = [
        {
            "name": "Prepaid Spa Package - Bronze",
            "description": "Pay ₹15,000 get ₹17,500 credit - 15% benefit with 2 months validity",
            "total_price": 15000,
            "credit_amount": 17500,
            "discount_percentage": 15.0,
            "validity_days": 60,  # 2 months
            "package_type": "prepaid"
        },
        {
            "name": "Prepaid Spa Package - Silver", 
            "description": "Pay ₹20,000 get ₹25,000 credit - 20% benefit with 3 months validity",
            "total_price": 20000,
            "credit_amount": 25000,
            "discount_percentage": 20.0,
            "validity_days": 90,  # 3 months
            "package_type": "prepaid"
        },
        {
            "name": "Prepaid Spa Package - Gold",
            "description": "Pay ₹30,000 get ₹40,000 credit - 25% benefit with 4 months validity", 
            "total_price": 30000,
            "credit_amount": 40000,
            "discount_percentage": 25.0,
            "validity_days": 120,  # 4 months
            "package_type": "prepaid"
        },
        {
            "name": "Prepaid Spa Package - Platinum",
            "description": "Pay ₹50,000 get ₹70,000 credit - 30% benefit with 6 months validity",
            "total_price": 50000,
            "credit_amount": 70000,
            "discount_percentage": 30.0,
            "validity_days": 180,  # 6 months
            "package_type": "prepaid"
        },
        {
            "name": "Prepaid Spa Package - Diamond",
            "description": "Pay ₹1,00,000 get ₹1,50,000 credit - 35% benefit with 1 year validity",
            "total_price": 100000,
            "credit_amount": 150000,
            "discount_percentage": 35.0,
            "validity_days": 365,  # 1 year
            "package_type": "prepaid"
        }
    ]
    
    for pkg_data in prepaid_packages:
        existing_pkg = Package.query.filter_by(name=pkg_data['name']).first()
        if not existing_pkg:
            package = Package(
                name=pkg_data['name'],
                description=pkg_data['description'],
                package_type=pkg_data['package_type'],
                total_price=pkg_data['total_price'],
                credit_amount=pkg_data['credit_amount'],
                discount_percentage=pkg_data['discount_percentage'],
                validity_days=pkg_data['validity_days'],
                duration_months=pkg_data['validity_days'] // 30,
                total_sessions=1,  # Unlimited sessions within credit limit
                is_active=True
            )
            db.session.add(package)
    
    db.session.commit()
    print("✅ Prepaid packages created")

def create_service_packages():
    """Create service-based packages (Pay for X get Y)"""
    service_packages = [
        {
            "name": "Service Package - Basic (Pay 3 Get 4)",
            "description": "Pay for 3 services, get 1 free - 25% benefit",
            "total_price": 3000,  # Average service price
            "discount_percentage": 25.0,
            "validity_days": 90,
            "total_sessions": 4,
            "package_type": "service_package"
        },
        {
            "name": "Service Package - Premium (Pay 6 Get 9)",
            "description": "Pay for 6 services, get 3 free - 33% benefit",
            "total_price": 6000,
            "discount_percentage": 33.0,
            "validity_days": 120,
            "total_sessions": 9,
            "package_type": "service_package"
        },
        {
            "name": "Service Package - Elite (Pay 9 Get 15)",
            "description": "Pay for 9 services, get 6 free - 40% benefit",
            "total_price": 9000,
            "discount_percentage": 40.0,
            "validity_days": 180,
            "total_sessions": 15,
            "package_type": "service_package"
        }
    ]
    
    for pkg_data in service_packages:
        existing_pkg = Package.query.filter_by(name=pkg_data['name']).first()
        if not existing_pkg:
            package = Package(
                name=pkg_data['name'],
                description=pkg_data['description'],
                package_type=pkg_data['package_type'],
                total_price=pkg_data['total_price'],
                discount_percentage=pkg_data['discount_percentage'],
                validity_days=pkg_data['validity_days'],
                duration_months=pkg_data['validity_days'] // 30,
                total_sessions=pkg_data['total_sessions'],
                is_active=True
            )
            db.session.add(package)
    
    db.session.commit()
    print("✅ Service packages created")

def create_membership_packages():
    """Create The Gentlemen's Club membership packages"""
    membership_benefits = {
        "classic": [
            "Classic haircut", "Classic shave", "Hair colour", 
            "Classic manicure & pedicure", "Classic facial", "Classic cleanup"
        ],
        "deluxe": [
            "Deluxe haircut", "Deluxe shave", "Hair colour",
            "Deluxe manicure & pedicure", "Deluxe facial", "Deluxe cleanup"
        ],
        "luxe": [
            "All services from the barber shop menu", "Premium treatments",
            "Priority booking", "Complimentary refreshments"
        ]
    }
    
    membership_packages = [
        {
            "name": "The Gentlemen's Club - Classic Membership",
            "description": "One year validity with classic services included",
            "total_price": 75000,
            "validity_days": 365,
            "package_type": "membership",
            "membership_benefits": json.dumps(membership_benefits["classic"]),
            "total_sessions": 50  # Generous session allowance
        },
        {
            "name": "The Gentlemen's Club - Deluxe Membership",
            "description": "One year validity with deluxe services included",
            "total_price": 90000,
            "validity_days": 365,
            "package_type": "membership", 
            "membership_benefits": json.dumps(membership_benefits["deluxe"]),
            "total_sessions": 60
        },
        {
            "name": "The Gentlemen's Club - UNAKI Luxe Membership",
            "description": "One year validity with all premium services included",
            "total_price": 125000,
            "validity_days": 365,
            "package_type": "membership",
            "membership_benefits": json.dumps(membership_benefits["luxe"]),
            "total_sessions": 100  # Unlimited-like experience
        }
    ]
    
    for pkg_data in membership_packages:
        existing_pkg = Package.query.filter_by(name=pkg_data['name']).first()
        if not existing_pkg:
            package = Package(
                name=pkg_data['name'],
                description=pkg_data['description'],
                package_type=pkg_data['package_type'],
                total_price=pkg_data['total_price'],
                validity_days=pkg_data['validity_days'],
                duration_months=12,
                total_sessions=pkg_data['total_sessions'],
                membership_benefits=pkg_data['membership_benefits'],
                is_active=True
            )
            db.session.add(package)
    
    db.session.commit()
    print("✅ Membership packages created")

def create_student_offers():
    """Create student discount packages"""
    student_offers = [
        {
            "name": "Student Offer - Hair Services (Monday-Friday)",
            "description": "50% off on Haircuts, Hair wash, Blow dry with valid student ID",
            "total_price": 500,  # Base price before discount
            "student_discount": 50.0,
            "validity_days": 30,
            "package_type": "student_offer"
        },
        {
            "name": "Student Offer - Hair Colour (Monday-Friday)", 
            "description": "30% off on Colour Streaks with valid student ID",
            "total_price": 2000,
            "student_discount": 30.0,
            "validity_days": 30,
            "package_type": "student_offer"
        },
        {
            "name": "Student Offer - Classic Manicure & Pedicure (Monday-Friday)",
            "description": "30% off on Classic Manicure & Pedicure with valid student ID", 
            "total_price": 1400,
            "student_discount": 30.0,
            "validity_days": 30,
            "package_type": "student_offer"
        },
        {
            "name": "Student Offer - Deluxe/Luxe Manicure & Pedicure (Monday-Friday)",
            "description": "40% off on Deluxe and Luxe Manicure & Pedicures with valid student ID",
            "total_price": 2200,
            "student_discount": 40.0,
            "validity_days": 30,
            "package_type": "student_offer"
        }
    ]
    
    for pkg_data in student_offers:
        existing_pkg = Package.query.filter_by(name=pkg_data['name']).first()
        if not existing_pkg:
            package = Package(
                name=pkg_data['name'],
                description=pkg_data['description'],
                package_type=pkg_data['package_type'],
                total_price=pkg_data['total_price'],
                student_discount=pkg_data['student_discount'],
                validity_days=pkg_data['validity_days'],
                duration_months=1,
                total_sessions=5,  # Multiple uses per month
                is_active=True
            )
            db.session.add(package)
    
    db.session.commit()
    print("✅ Student offers created")

def create_yearly_salon_membership():
    """Create yearly salon membership"""
    yearly_benefits = {
        "benefits": [
            "20% discount on all salon services",
            "Complimentary classic manicure and pedicure",
            "12 complimentary threading sessions",
            "4 complimentary hair washes",
            "2000 credit points"
        ]
    }
    
    yearly_membership = Package(
        name="Yearly Salon Membership",
        description="Pay ₹2000 and get 20% off on all salon services with additional complimentary benefits",
        package_type="yearly_membership",
        total_price=2000,
        credit_amount=2000,  # Credit points
        discount_percentage=20.0,
        validity_days=365,
        duration_months=12,
        total_sessions=100,  # High session count for year-long usage
        membership_benefits=json.dumps(yearly_benefits["benefits"]),
        is_active=True
    )
    
    existing_pkg = Package.query.filter_by(name="Yearly Salon Membership").first()
    if not existing_pkg:
        db.session.add(yearly_membership)
        db.session.commit()
        print("✅ Yearly salon membership created")

def create_kitty_party_packages():
    """Create kitty party packages"""
    kitty_benefits = {
        "inclusions": [
            "Fun games and activities",
            "Food and refreshments", 
            "Hair spa and hair rituals",
            "Manicure & pedicure services",
            "Hand & foot reflexology"
        ]
    }
    
    kitty_packages = [
        {
            "name": "Kitty Party Package - Classic",
            "description": "₹50,000 package for minimum 10 guests with fun games, food, spa treatments",
            "total_price": 50000,
            "min_guests": 10,
            "validity_days": 30,
            "package_type": "kitty_party"
        },
        {
            "name": "Kitty Party Package - Deluxe",
            "description": "₹75,000 package for minimum 10 guests with premium treatments and extended services",
            "total_price": 75000,
            "min_guests": 10,
            "validity_days": 30,
            "package_type": "kitty_party"
        },
        {
            "name": "Kitty Party Package - Luxe",
            "description": "₹100,000 package for minimum 10 guests with luxury treatments and full-day experience",
            "total_price": 100000,
            "min_guests": 10,
            "validity_days": 30,
            "package_type": "kitty_party"
        }
    ]
    
    for pkg_data in kitty_packages:
        existing_pkg = Package.query.filter_by(name=pkg_data['name']).first()
        if not existing_pkg:
            package = Package(
                name=pkg_data['name'],
                description=pkg_data['description'],
                package_type=pkg_data['package_type'],
                total_price=pkg_data['total_price'],
                min_guests=pkg_data['min_guests'],
                validity_days=pkg_data['validity_days'],
                duration_months=1,
                total_sessions=1,  # One-time event
                membership_benefits=json.dumps(kitty_benefits["inclusions"]),
                is_active=True
            )
            db.session.add(package)
    
    db.session.commit()
    print("✅ Kitty party packages created")

if __name__ == "__main__":
    create_comprehensive_spa_packages()