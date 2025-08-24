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
from models import Package, Service, PackageService, Category
from datetime import datetime
import json

def create_comprehensive_spa_packages():
    with app.app_context():
        print("Creating comprehensive spa packages...")

        # Ensure we have some basic services first
        ensure_comprehensive_services()

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

def ensure_comprehensive_services():
    """Create comprehensive spa services with categories"""

    # First create service categories
    categories = [
        {"name": "facial", "display_name": "Facial Treatments", "color": "#FF6B6B", "description": "Professional facial and skincare treatments"},
        {"name": "massage", "display_name": "Massage Therapy", "color": "#4ECDC4", "description": "Relaxing and therapeutic massage services"},
        {"name": "hair", "display_name": "Hair Services", "color": "#45B7D1", "description": "Hair cutting, styling, and treatments"},
        {"name": "nail", "display_name": "Nail Care", "color": "#96CEB4", "description": "Manicure, pedicure, and nail treatments"},
        {"name": "body", "display_name": "Body Treatments", "color": "#FECA57", "description": "Body wraps, scrubs, and spa treatments"},
        {"name": "skin", "display_name": "Skin Treatments", "color": "#FF9FF3", "description": "Advanced skin care and dermatology"},
        {"name": "wellness", "display_name": "Wellness & Therapy", "color": "#54A0FF", "description": "Holistic wellness and therapeutic treatments"},
        {"name": "bridal", "display_name": "Bridal Packages", "color": "#FFD700", "description": "Special bridal and wedding packages"}
    ]

    for cat_data in categories:
        existing_cat = Category.query.filter_by(name=cat_data['name'], category_type='service').first()
        if not existing_cat:
            category = Category(
                name=cat_data['name'],
                display_name=cat_data['display_name'],
                description=cat_data['description'],
                category_type='service',
                color=cat_data['color'],
                is_active=True,
                sort_order=0
            )
            db.session.add(category)

    db.session.commit()

    # Comprehensive spa services based on typical salon/spa offerings
    services = [
        # Facial Treatments
        {"name": "Classic Facial", "duration": 60, "price": 800.0, "category": "facial", "description": "Deep cleansing and hydrating facial treatment"},
        {"name": "Anti-Aging Facial", "duration": 90, "price": 1500.0, "category": "facial", "description": "Advanced anti-aging treatment with collagen boost"},
        {"name": "Acne Treatment Facial", "duration": 75, "price": 1200.0, "category": "facial", "description": "Specialized treatment for acne-prone skin"},
        {"name": "Hydra Facial", "duration": 60, "price": 2000.0, "category": "facial", "description": "Medical-grade hydra dermabrasion facial"},
        {"name": "Gold Facial", "duration": 90, "price": 2500.0, "category": "facial", "description": "Luxury 24k gold anti-aging facial"},
        {"name": "Fruit Facial", "duration": 60, "price": 900.0, "category": "facial", "description": "Natural fruit enzyme facial"},
        {"name": "Diamond Facial", "duration": 75, "price": 1800.0, "category": "facial", "description": "Diamond microdermabrasion facial"},
        {"name": "Oxygen Facial", "duration": 60, "price": 1600.0, "category": "facial", "description": "Oxygen infusion facial for glowing skin"},

        # Massage Therapy
        {"name": "Swedish Massage", "duration": 60, "price": 1000.0, "category": "massage", "description": "Classic relaxing full body massage"},
        {"name": "Deep Tissue Massage", "duration": 90, "price": 1500.0, "category": "massage", "description": "Therapeutic deep muscle massage"},
        {"name": "Hot Stone Massage", "duration": 90, "price": 1800.0, "category": "massage", "description": "Relaxing massage with heated stones"},
        {"name": "Thai Massage", "duration": 90, "price": 1400.0, "category": "massage", "description": "Traditional Thai stretching massage"},
        {"name": "Aromatherapy Massage", "duration": 75, "price": 1300.0, "category": "massage", "description": "Essential oil therapeutic massage"},
        {"name": "Head & Shoulder Massage", "duration": 30, "price": 600.0, "category": "massage", "description": "Focused upper body massage"},
        {"name": "Prenatal Massage", "duration": 60, "price": 1200.0, "category": "massage", "description": "Safe pregnancy massage therapy"},
        {"name": "Sports Massage", "duration": 60, "price": 1100.0, "category": "massage", "description": "Athletic recovery massage"},

        # Hair Services
        {"name": "Hair Cut & Blow Dry", "duration": 60, "price": 800.0, "category": "hair", "description": "Professional hair cut and styling"},
        {"name": "Hair Color (Full)", "duration": 120, "price": 2000.0, "category": "hair", "description": "Complete hair coloring service"},
        {"name": "Hair Highlights", "duration": 150, "price": 2500.0, "category": "hair", "description": "Professional hair highlighting"},
        {"name": "Hair Straightening", "duration": 180, "price": 3000.0, "category": "hair", "description": "Chemical hair straightening treatment"},
        {"name": "Hair Spa Treatment", "duration": 90, "price": 1200.0, "category": "hair", "description": "Deep conditioning hair treatment"},
        {"name": "Keratin Treatment", "duration": 180, "price": 4000.0, "category": "hair", "description": "Smoothing keratin hair treatment"},
        {"name": "Hair Extensions", "duration": 120, "price": 3500.0, "category": "hair", "description": "Professional hair extension application"},
        {"name": "Scalp Treatment", "duration": 45, "price": 700.0, "category": "hair", "description": "Therapeutic scalp treatment"},

        # Nail Care
        {"name": "Basic Manicure", "duration": 45, "price": 500.0, "category": "nail", "description": "Classic nail grooming and polish"},
        {"name": "Gel Manicure", "duration": 60, "price": 800.0, "category": "nail", "description": "Long-lasting gel polish manicure"},
        {"name": "Basic Pedicure", "duration": 60, "price": 600.0, "category": "nail", "description": "Foot care and nail grooming"},
        {"name": "Spa Pedicure", "duration": 90, "price": 1000.0, "category": "nail", "description": "Luxury foot spa treatment"},
        {"name": "Nail Art", "duration": 30, "price": 400.0, "category": "nail", "description": "Creative nail art design"},
        {"name": "French Manicure", "duration": 60, "price": 700.0, "category": "nail", "description": "Classic French tip manicure"},
        {"name": "Nail Extensions", "duration": 90, "price": 1200.0, "category": "nail", "description": "Acrylic or gel nail extensions"},

        # Body Treatments
        {"name": "Body Polish", "duration": 60, "price": 1200.0, "category": "body", "description": "Full body exfoliation treatment"},
        {"name": "Body Wrap", "duration": 90, "price": 1800.0, "category": "body", "description": "Detoxifying body wrap treatment"},
        {"name": "Cellulite Treatment", "duration": 60, "price": 1500.0, "category": "body", "description": "Targeted cellulite reduction therapy"},
        {"name": "Slimming Treatment", "duration": 90, "price": 2000.0, "category": "body", "description": "Body contouring and slimming"},
        {"name": "Tan Removal", "duration": 45, "price": 800.0, "category": "body", "description": "Professional tan removal treatment"},
        {"name": "Body Bleaching", "duration": 75, "price": 1000.0, "category": "body", "description": "Full body skin lightening"},

        # Advanced Skin Treatments
        {"name": "Chemical Peel", "duration": 60, "price": 1800.0, "category": "skin", "description": "Professional skin peeling treatment"},
        {"name": "Microdermabrasion", "duration": 45, "price": 1500.0, "category": "skin", "description": "Diamond tip skin resurfacing"},
        {"name": "LED Light Therapy", "duration": 30, "price": 1000.0, "category": "skin", "description": "LED phototherapy treatment"},
        {"name": "Radio Frequency", "duration": 60, "price": 2200.0, "category": "skin", "description": "RF skin tightening treatment"},
        {"name": "Vampire Facial", "duration": 90, "price": 5000.0, "category": "skin", "description": "PRP facial rejuvenation"},
        {"name": "Laser Hair Removal", "duration": 30, "price": 1500.0, "category": "skin", "description": "Permanent hair reduction laser"},

        # Wellness & Therapy
        {"name": "Reflexology", "duration": 60, "price": 900.0, "category": "wellness", "description": "Therapeutic foot pressure point massage"},
        {"name": "Acupuncture", "duration": 45, "price": 1200.0, "category": "wellness", "description": "Traditional Chinese acupuncture"},
        {"name": "Cupping Therapy", "duration": 45, "price": 800.0, "category": "wellness", "description": "Traditional cupping treatment"},
        {"name": "Meditation Session", "duration": 30, "price": 500.0, "category": "wellness", "description": "Guided meditation and relaxation"},
        {"name": "Yoga Session", "duration": 60, "price": 600.0, "category": "wellness", "description": "Private yoga instruction"},

        # Bridal Packages
        {"name": "Bridal Makeup", "duration": 120, "price": 3000.0, "category": "bridal", "description": "Professional bridal makeup"},
        {"name": "Bridal Hair Styling", "duration": 90, "price": 2500.0, "category": "bridal", "description": "Bridal hair styling and updo"},
        {"name": "Pre-Wedding Facial", "duration": 90, "price": 1800.0, "category": "bridal", "description": "Special bridal glow facial"},
        {"name": "Bridal Mehendi", "duration": 180, "price": 2000.0, "category": "bridal", "description": "Intricate bridal henna design"},
        {"name": "Bridal Full Package", "duration": 300, "price": 8000.0, "category": "bridal", "description": "Complete bridal beauty package"},
    ]

    # Create services with proper category assignment
    for service_data in services:
        existing_service = Service.query.filter_by(name=service_data['name']).first()
        if not existing_service:
            # Get category ID
            category = Category.query.filter_by(name=service_data['category'], category_type='service').first()

            service = Service(
                name=service_data['name'],
                description=service_data['description'],
                duration=service_data['duration'],
                price=service_data['price'],
                category_id=category.id if category else None,
                category=service_data['category'],  # Fallback
                is_active=True
            )
            db.session.add(service)

    db.session.commit()
    print("Comprehensive spa services created")

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
            "description": "₹50,000 package for minimum 10 guests with fun games, spa treatments",
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