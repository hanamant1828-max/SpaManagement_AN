#!/usr/bin/env python3
"""
Script to add precise spa services from the provided menu with exact categories and pricing
"""

from app import app, db
from models import Service, Category
from datetime import datetime

def create_precise_categories():
    """Create exact categories as shown in the service menu"""
    
    categories_data = [
        {
            'name': 'hair_cuts_styling',
            'display_name': 'Hair Cuts & Styling',
            'description': 'Professional hair cutting and styling services',
            'category_type': 'service',
            'color': '#FF6B6B',
            'icon': 'fas fa-cut',
            'sort_order': 1
        },
        {
            'name': 'hair_color_highlights',
            'display_name': 'Hair Color & Highlights',
            'description': 'Hair coloring, highlighting and chemical treatments',
            'category_type': 'service',
            'color': '#FF8C94',
            'icon': 'fas fa-palette',
            'sort_order': 2
        },
        {
            'name': 'hair_treatments',
            'display_name': 'Hair Treatments',
            'description': 'Deep conditioning and specialized hair treatments',
            'category_type': 'service',
            'color': '#A8E6CF',
            'icon': 'fas fa-leaf',
            'sort_order': 3
        },
        {
            'name': 'facial_treatments',
            'display_name': 'Facial Treatments',
            'description': 'Comprehensive facial and skincare treatments',
            'category_type': 'service',
            'color': '#4ECDC4',
            'icon': 'fas fa-spa',
            'sort_order': 4
        },
        {
            'name': 'advanced_facials',
            'display_name': 'Advanced Facial Treatments',
            'description': 'Premium and specialized facial treatments',
            'category_type': 'service',
            'color': '#45B7D1',
            'icon': 'fas fa-star',
            'sort_order': 5
        },
        {
            'name': 'body_massage',
            'display_name': 'Body Massage',
            'description': 'Relaxing and therapeutic massage services',
            'category_type': 'service',
            'color': '#96CEB4',
            'icon': 'fas fa-hands',
            'sort_order': 6
        },
        {
            'name': 'body_treatments',
            'display_name': 'Body Treatments',
            'description': 'Body scrubs, wraps and spa treatments',
            'category_type': 'service',
            'color': '#FFEAA7',
            'icon': 'fas fa-water',
            'sort_order': 7
        },
        {
            'name': 'nail_services',
            'display_name': 'Nail Services',
            'description': 'Manicure, pedicure and nail care services',
            'category_type': 'service',
            'color': '#F39C12',
            'icon': 'fas fa-hand-sparkles',
            'sort_order': 8
        },
        {
            'name': 'waxing_services',
            'display_name': 'Waxing Services',
            'description': 'Hair removal and waxing treatments',
            'category_type': 'service',
            'color': '#E17055',
            'icon': 'fas fa-scissors',
            'sort_order': 9
        },
        {
            'name': 'threading_services',
            'display_name': 'Threading Services',
            'description': 'Eyebrow and facial hair threading',
            'category_type': 'service',
            'color': '#82E0AA',
            'icon': 'fas fa-thread',
            'sort_order': 10
        },
        {
            'name': 'makeup_services',
            'display_name': 'Makeup Services',
            'description': 'Professional makeup and beauty services',
            'category_type': 'service',
            'color': '#AF7AC5',
            'icon': 'fas fa-makeup',
            'sort_order': 11
        },
        {
            'name': 'bridal_packages',
            'display_name': 'Bridal Packages',
            'description': 'Complete bridal makeover packages',
            'category_type': 'service',
            'color': '#F8C471',
            'icon': 'fas fa-crown',
            'sort_order': 12
        },
        {
            'name': 'specialty_treatments',
            'display_name': 'Specialty Treatments',
            'description': 'Advanced medical and specialty treatments',
            'category_type': 'service',
            'color': '#BB8FCE',
            'icon': 'fas fa-medical',
            'sort_order': 13
        }
    ]
    
    categories = {}
    for cat_data in categories_data:
        existing_cat = Category.query.filter_by(name=cat_data['name'], category_type='service').first()
        if not existing_cat:
            category = Category(**cat_data)
            db.session.add(category)
            db.session.flush()
            categories[cat_data['name']] = category.id
            print(f"Created category: {cat_data['display_name']}")
        else:
            categories[cat_data['name']] = existing_cat.id
            print(f"Category already exists: {cat_data['display_name']}")
    
    db.session.commit()
    return categories

def add_precise_spa_services():
    """Add all services from the precise menu with exact pricing"""
    
    with app.app_context():
        try:
            # First create categories
            categories = create_precise_categories()
            
            # Comprehensive services data matching the provided menu
            services_data = [
                # Hair Cuts & Styling
                {'name': 'Haircut (Men)', 'description': 'Professional men\'s haircut', 'duration': 30, 'price': 25.00, 'category': 'hair_cuts_styling'},
                {'name': 'Haircut (Women)', 'description': 'Professional women\'s haircut', 'duration': 45, 'price': 35.00, 'category': 'hair_cuts_styling'},
                {'name': 'Trim & Shape', 'description': 'Hair trimming and shaping', 'duration': 30, 'price': 20.00, 'category': 'hair_cuts_styling'},
                {'name': 'Blow Dry & Style', 'description': 'Professional blow dry and styling', 'duration': 45, 'price': 30.00, 'category': 'hair_cuts_styling'},
                {'name': 'Updo Styling', 'description': 'Elegant updo hair styling', 'duration': 60, 'price': 45.00, 'category': 'hair_cuts_styling'},
                {'name': 'Hair Wash & Style', 'description': 'Hair washing and basic styling', 'duration': 30, 'price': 25.00, 'category': 'hair_cuts_styling'},
                {'name': 'Layered Cut', 'description': 'Professional layered haircut', 'duration': 60, 'price': 40.00, 'category': 'hair_cuts_styling'},
                {'name': 'Bang/Fringe Cut', 'description': 'Bang or fringe cutting service', 'duration': 15, 'price': 15.00, 'category': 'hair_cuts_styling'},
                {'name': 'Beard Trim', 'description': 'Professional beard trimming', 'duration': 20, 'price': 18.00, 'category': 'hair_cuts_styling'},
                {'name': 'Mustache Trim', 'description': 'Mustache trimming and shaping', 'duration': 10, 'price': 12.00, 'category': 'hair_cuts_styling'},

                # Hair Color & Highlights
                {'name': 'Full Hair Color', 'description': 'Complete hair coloring service', 'duration': 120, 'price': 85.00, 'category': 'hair_color_highlights'},
                {'name': 'Root Touch-Up', 'description': 'Root color touch-up service', 'duration': 60, 'price': 55.00, 'category': 'hair_color_highlights'},
                {'name': 'Partial Highlights', 'description': 'Partial hair highlighting', 'duration': 90, 'price': 75.00, 'category': 'hair_color_highlights'},
                {'name': 'Full Highlights', 'description': 'Complete hair highlighting', 'duration': 150, 'price': 120.00, 'category': 'hair_color_highlights'},
                {'name': 'Lowlights', 'description': 'Hair lowlighting service', 'duration': 90, 'price': 80.00, 'category': 'hair_color_highlights'},
                {'name': 'Balayage', 'description': 'Hand-painted balayage highlights', 'duration': 180, 'price': 150.00, 'category': 'hair_color_highlights'},
                {'name': 'Ombre', 'description': 'Gradient ombre coloring', 'duration': 150, 'price': 125.00, 'category': 'hair_color_highlights'},
                {'name': 'Color Correction', 'description': 'Hair color correction service', 'duration': 240, 'price': 200.00, 'category': 'hair_color_highlights'},
                {'name': 'Gray Coverage', 'description': 'Gray hair coverage coloring', 'duration': 90, 'price': 70.00, 'category': 'hair_color_highlights'},
                {'name': 'Toner Application', 'description': 'Hair toner application', 'duration': 45, 'price': 35.00, 'category': 'hair_color_highlights'},

                # Hair Treatments
                {'name': 'Deep Conditioning Treatment', 'description': 'Intensive hair conditioning', 'duration': 45, 'price': 35.00, 'category': 'hair_treatments'},
                {'name': 'Keratin Treatment', 'description': 'Keratin smoothing treatment', 'duration': 180, 'price': 200.00, 'category': 'hair_treatments'},
                {'name': 'Protein Treatment', 'description': 'Hair protein reconstruction', 'duration': 60, 'price': 45.00, 'category': 'hair_treatments'},
                {'name': 'Hot Oil Treatment', 'description': 'Nourishing hot oil treatment', 'duration': 30, 'price': 25.00, 'category': 'hair_treatments'},
                {'name': 'Scalp Treatment', 'description': 'Therapeutic scalp treatment', 'duration': 45, 'price': 40.00, 'category': 'hair_treatments'},
                {'name': 'Hair Mask Treatment', 'description': 'Intensive hair mask therapy', 'duration': 45, 'price': 35.00, 'category': 'hair_treatments'},
                {'name': 'Brazilian Blowout', 'description': 'Brazilian smoothing treatment', 'duration': 150, 'price': 180.00, 'category': 'hair_treatments'},
                {'name': 'Olaplex Treatment', 'description': 'Bond-building hair treatment', 'duration': 60, 'price': 65.00, 'category': 'hair_treatments'},

                # Facial Treatments
                {'name': 'Basic Facial', 'description': 'Essential facial cleansing treatment', 'duration': 60, 'price': 65.00, 'category': 'facial_treatments'},
                {'name': 'Deep Cleansing Facial', 'description': 'Intensive pore cleansing facial', 'duration': 75, 'price': 80.00, 'category': 'facial_treatments'},
                {'name': 'Anti-Aging Facial', 'description': 'Anti-aging skincare treatment', 'duration': 90, 'price': 95.00, 'category': 'facial_treatments'},
                {'name': 'Hydrating Facial', 'description': 'Moisturizing facial treatment', 'duration': 60, 'price': 70.00, 'category': 'facial_treatments'},
                {'name': 'Acne Facial', 'description': 'Acne treatment facial', 'duration': 75, 'price': 85.00, 'category': 'facial_treatments'},
                {'name': 'Brightening Facial', 'description': 'Skin brightening treatment', 'duration': 75, 'price': 85.00, 'category': 'facial_treatments'},
                {'name': 'Sensitive Skin Facial', 'description': 'Gentle facial for sensitive skin', 'duration': 60, 'price': 70.00, 'category': 'facial_treatments'},
                {'name': 'Express Facial', 'description': 'Quick 30-minute facial', 'duration': 30, 'price': 45.00, 'category': 'facial_treatments'},
                {'name': 'Men\'s Facial', 'description': 'Facial treatment designed for men', 'duration': 60, 'price': 65.00, 'category': 'facial_treatments'},
                {'name': 'Teen Facial', 'description': 'Facial treatment for teenagers', 'duration': 45, 'price': 55.00, 'category': 'facial_treatments'},

                # Advanced Facial Treatments
                {'name': 'Microdermabrasion', 'description': 'Professional skin resurfacing', 'duration': 60, 'price': 125.00, 'category': 'advanced_facials'},
                {'name': 'Chemical Peel - Light', 'description': 'Light chemical peel treatment', 'duration': 45, 'price': 85.00, 'category': 'advanced_facials'},
                {'name': 'Chemical Peel - Medium', 'description': 'Medium chemical peel treatment', 'duration': 60, 'price': 125.00, 'category': 'advanced_facials'},
                {'name': 'Oxygen Facial', 'description': 'Oxygen infusion facial', 'duration': 75, 'price': 110.00, 'category': 'advanced_facials'},
                {'name': 'LED Light Therapy', 'description': 'LED skin therapy treatment', 'duration': 30, 'price': 65.00, 'category': 'advanced_facials'},
                {'name': 'Radiofrequency Facial', 'description': 'RF skin tightening', 'duration': 60, 'price': 150.00, 'category': 'advanced_facials'},
                {'name': 'Ultrasonic Facial', 'description': 'Ultrasonic deep cleansing', 'duration': 60, 'price': 95.00, 'category': 'advanced_facials'},
                {'name': 'Gold Facial', 'description': 'Luxury gold facial treatment', 'duration': 90, 'price': 180.00, 'category': 'advanced_facials'},
                {'name': 'Diamond Facial', 'description': 'Premium diamond facial', 'duration': 90, 'price': 200.00, 'category': 'advanced_facials'},
                {'name': 'Vampire Facial', 'description': 'PRP facial treatment', 'duration': 90, 'price': 300.00, 'category': 'advanced_facials'},

                # Body Massage
                {'name': 'Swedish Massage', 'description': 'Classic relaxation massage', 'duration': 60, 'price': 85.00, 'category': 'body_massage'},
                {'name': 'Deep Tissue Massage', 'description': 'Therapeutic deep tissue work', 'duration': 90, 'price': 115.00, 'category': 'body_massage'},
                {'name': 'Hot Stone Massage', 'description': 'Heated stone massage therapy', 'duration': 90, 'price': 125.00, 'category': 'body_massage'},
                {'name': 'Aromatherapy Massage', 'description': 'Essential oil massage', 'duration': 75, 'price': 95.00, 'category': 'body_massage'},
                {'name': 'Sports Massage', 'description': 'Athletic recovery massage', 'duration': 60, 'price': 90.00, 'category': 'body_massage'},
                {'name': 'Prenatal Massage', 'description': 'Safe pregnancy massage', 'duration': 60, 'price': 85.00, 'category': 'body_massage'},
                {'name': 'Couples Massage', 'description': 'Side-by-side massage for two', 'duration': 60, 'price': 170.00, 'category': 'body_massage'},
                {'name': 'Chair Massage', 'description': 'Seated massage therapy', 'duration': 30, 'price': 45.00, 'category': 'body_massage'},
                {'name': 'Reflexology', 'description': 'Therapeutic foot massage', 'duration': 45, 'price': 65.00, 'category': 'body_massage'},
                {'name': 'Head & Neck Massage', 'description': 'Focused head and neck work', 'duration': 30, 'price': 45.00, 'category': 'body_massage'},

                # Body Treatments
                {'name': 'Body Scrub - Salt', 'description': 'Exfoliating salt body scrub', 'duration': 45, 'price': 75.00, 'category': 'body_treatments'},
                {'name': 'Body Scrub - Sugar', 'description': 'Gentle sugar body scrub', 'duration': 45, 'price': 70.00, 'category': 'body_treatments'},
                {'name': 'Body Wrap - Detox', 'description': 'Detoxifying body wrap', 'duration': 75, 'price': 95.00, 'category': 'body_treatments'},
                {'name': 'Body Wrap - Hydrating', 'description': 'Moisturizing body wrap', 'duration': 75, 'price': 90.00, 'category': 'body_treatments'},
                {'name': 'Body Polish', 'description': 'Full body polishing treatment', 'duration': 60, 'price': 85.00, 'category': 'body_treatments'},
                {'name': 'Cellulite Treatment', 'description': 'Targeted cellulite reduction', 'duration': 60, 'price': 110.00, 'category': 'body_treatments'},
                {'name': 'Spray Tan', 'description': 'Professional spray tanning', 'duration': 30, 'price': 45.00, 'category': 'body_treatments'},
                {'name': 'Back Facial', 'description': 'Deep cleansing back treatment', 'duration': 60, 'price': 80.00, 'category': 'body_treatments'},

                # Nail Services
                {'name': 'Basic Manicure', 'description': 'Essential nail care and polish', 'duration': 45, 'price': 25.00, 'category': 'nail_services'},
                {'name': 'Gel Manicure', 'description': 'Long-lasting gel polish', 'duration': 60, 'price': 35.00, 'category': 'nail_services'},
                {'name': 'French Manicure', 'description': 'Classic French tip style', 'duration': 60, 'price': 30.00, 'category': 'nail_services'},
                {'name': 'Spa Manicure', 'description': 'Luxury manicure with extras', 'duration': 75, 'price': 45.00, 'category': 'nail_services'},
                {'name': 'Basic Pedicure', 'description': 'Essential foot care and polish', 'duration': 60, 'price': 35.00, 'category': 'nail_services'},
                {'name': 'Gel Pedicure', 'description': 'Long-lasting gel pedicure', 'duration': 75, 'price': 45.00, 'category': 'nail_services'},
                {'name': 'Spa Pedicure', 'description': 'Luxury pedicure treatment', 'duration': 90, 'price': 55.00, 'category': 'nail_services'},
                {'name': 'Callus Removal', 'description': 'Professional callus treatment', 'duration': 30, 'price': 25.00, 'category': 'nail_services'},
                {'name': 'Nail Art', 'description': 'Creative nail art design', 'duration': 30, 'price': 20.00, 'category': 'nail_services'},
                {'name': 'Nail Repair', 'description': 'Broken nail repair service', 'duration': 15, 'price': 15.00, 'category': 'nail_services'},

                # Waxing Services
                {'name': 'Eyebrow Wax', 'description': 'Eyebrow shaping with wax', 'duration': 15, 'price': 20.00, 'category': 'waxing_services'},
                {'name': 'Upper Lip Wax', 'description': 'Upper lip hair removal', 'duration': 10, 'price': 15.00, 'category': 'waxing_services'},
                {'name': 'Chin Wax', 'description': 'Chin hair removal', 'duration': 15, 'price': 18.00, 'category': 'waxing_services'},
                {'name': 'Full Face Wax', 'description': 'Complete facial hair removal', 'duration': 30, 'price': 35.00, 'category': 'waxing_services'},
                {'name': 'Underarm Wax', 'description': 'Underarm hair removal', 'duration': 15, 'price': 25.00, 'category': 'waxing_services'},
                {'name': 'Half Arm Wax', 'description': 'Lower or upper arm waxing', 'duration': 30, 'price': 35.00, 'category': 'waxing_services'},
                {'name': 'Full Arm Wax', 'description': 'Complete arm hair removal', 'duration': 45, 'price': 55.00, 'category': 'waxing_services'},
                {'name': 'Half Leg Wax', 'description': 'Lower or upper leg waxing', 'duration': 45, 'price': 45.00, 'category': 'waxing_services'},
                {'name': 'Full Leg Wax', 'description': 'Complete leg hair removal', 'duration': 75, 'price': 75.00, 'category': 'waxing_services'},
                {'name': 'Bikini Wax', 'description': 'Bikini area hair removal', 'duration': 30, 'price': 45.00, 'category': 'waxing_services'},
                {'name': 'Brazilian Wax', 'description': 'Complete intimate area waxing', 'duration': 45, 'price': 65.00, 'category': 'waxing_services'},
                {'name': 'Back Wax', 'description': 'Back hair removal', 'duration': 30, 'price': 45.00, 'category': 'waxing_services'},
                {'name': 'Chest Wax', 'description': 'Chest hair removal', 'duration': 30, 'price': 40.00, 'category': 'waxing_services'},

                # Threading Services
                {'name': 'Eyebrow Threading', 'description': 'Precise eyebrow shaping', 'duration': 20, 'price': 18.00, 'category': 'threading_services'},
                {'name': 'Upper Lip Threading', 'description': 'Upper lip hair threading', 'duration': 10, 'price': 12.00, 'category': 'threading_services'},
                {'name': 'Chin Threading', 'description': 'Chin hair removal threading', 'duration': 15, 'price': 15.00, 'category': 'threading_services'},
                {'name': 'Forehead Threading', 'description': 'Forehead hair threading', 'duration': 15, 'price': 15.00, 'category': 'threading_services'},
                {'name': 'Sideburn Threading', 'description': 'Sideburn area threading', 'duration': 15, 'price': 15.00, 'category': 'threading_services'},
                {'name': 'Full Face Threading', 'description': 'Complete facial threading', 'duration': 30, 'price': 35.00, 'category': 'threading_services'},

                # Makeup Services
                {'name': 'Bridal Makeup', 'description': 'Complete bridal makeup', 'duration': 120, 'price': 150.00, 'category': 'makeup_services'},
                {'name': 'Party Makeup', 'description': 'Special occasion makeup', 'duration': 60, 'price': 65.00, 'category': 'makeup_services'},
                {'name': 'Evening Makeup', 'description': 'Elegant evening look', 'duration': 75, 'price': 75.00, 'category': 'makeup_services'},
                {'name': 'Natural Makeup', 'description': 'Subtle everyday makeup', 'duration': 45, 'price': 45.00, 'category': 'makeup_services'},
                {'name': 'Smokey Eye Makeup', 'description': 'Dramatic smokey eye look', 'duration': 60, 'price': 55.00, 'category': 'makeup_services'},
                {'name': 'Makeup Trial', 'description': 'Makeup trial session', 'duration': 90, 'price': 85.00, 'category': 'makeup_services'},
                {'name': 'Makeup Lesson', 'description': 'Personal makeup instruction', 'duration': 60, 'price': 70.00, 'category': 'makeup_services'},
                {'name': 'False Lash Application', 'description': 'Professional lash application', 'duration': 30, 'price': 25.00, 'category': 'makeup_services'},

                # Bridal Packages
                {'name': 'Bridal Package - Basic', 'description': 'Hair, makeup, and manicure', 'duration': 240, 'price': 250.00, 'category': 'bridal_packages'},
                {'name': 'Bridal Package - Premium', 'description': 'Complete bridal makeover', 'duration': 360, 'price': 450.00, 'category': 'bridal_packages'},
                {'name': 'Bridal Package - Luxury', 'description': 'Ultimate bridal experience', 'duration': 480, 'price': 650.00, 'category': 'bridal_packages'},
                {'name': 'Bridal Trial Package', 'description': 'Hair and makeup trial', 'duration': 180, 'price': 125.00, 'category': 'bridal_packages'},
                {'name': 'Engagement Package', 'description': 'Special engagement makeover', 'duration': 180, 'price': 185.00, 'category': 'bridal_packages'},
                {'name': 'Pre-Wedding Glow Package', 'description': 'Pre-wedding skincare package', 'duration': 150, 'price': 165.00, 'category': 'bridal_packages'},

                # Specialty Treatments
                {'name': 'Laser Hair Removal - Small Area', 'description': 'Laser hair removal small area', 'duration': 30, 'price': 85.00, 'category': 'specialty_treatments'},
                {'name': 'Laser Hair Removal - Large Area', 'description': 'Laser hair removal large area', 'duration': 60, 'price': 165.00, 'category': 'specialty_treatments'},
                {'name': 'IPL Treatment', 'description': 'Intense pulsed light therapy', 'duration': 45, 'price': 125.00, 'category': 'specialty_treatments'},
                {'name': 'Cryotherapy', 'description': 'Cold therapy treatment', 'duration': 30, 'price': 75.00, 'category': 'specialty_treatments'},
                {'name': 'Dermaplaning', 'description': 'Exfoliating blade treatment', 'duration': 45, 'price': 95.00, 'category': 'specialty_treatments'},
                {'name': 'HydraFacial', 'description': 'Advanced hydrating facial', 'duration': 60, 'price': 185.00, 'category': 'specialty_treatments'},
                {'name': 'Botox Consultation', 'description': 'Professional botox consultation', 'duration': 30, 'price': 50.00, 'category': 'specialty_treatments'},
                {'name': 'Filler Consultation', 'description': 'Dermal filler consultation', 'duration': 30, 'price': 50.00, 'category': 'specialty_treatments'}
            ]
            
            # Check existing services and add new ones
            existing_services = set()
            for service in Service.query.all():
                existing_services.add(service.name.lower())
            
            added_count = 0
            for service_data in services_data:
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
                    print(f"Adding service: {service_data['name']} - ${service_data['price']}")
                else:
                    print(f"Service already exists: {service_data['name']}")
            
            if added_count > 0:
                db.session.commit()
                print(f"\n✅ Successfully added {added_count} precise spa services to the database!")
                print("🏷️ All services have been properly categorized")
            else:
                print("\n⚠️ All services already exist in the database")
            
            # Print summary by category
            print(f"\n📊 Service Summary by Category:")
            for cat_name, cat_id in categories.items():
                cat = Category.query.get(cat_id)
                service_count = Service.query.filter_by(category_id=cat_id, is_active=True).count()
                print(f"   {cat.display_name}: {service_count} services")
            
            total_services = Service.query.filter_by(is_active=True).count()
            print(f"\n📋 Total Active Services: {total_services}")
            print(f"🆕 Services Added This Run: {added_count}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding services: {str(e)}")
            raise e

if __name__ == "__main__":
    add_precise_spa_services()