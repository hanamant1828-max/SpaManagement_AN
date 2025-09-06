
#!/usr/bin/env python3
"""
Script to add comprehensive service categories and services to the spa management system
Based on the provided services list
"""

from app import app, db
from models import Service, Category
from datetime import datetime

def create_service_categories():
    """Create comprehensive service categories"""
    
    categories_data = [
        {
            'name': 'hair_services',
            'display_name': 'Hair Services',
            'description': 'Hair cutting, styling, coloring and treatment services',
            'category_type': 'service',
            'color': '#FF6B6B',
            'icon': 'fas fa-cut',
            'sort_order': 1
        },
        {
            'name': 'facial_treatments',
            'display_name': 'Facial Treatments',
            'description': 'Skincare and facial beauty treatments',
            'category_type': 'service',
            'color': '#4ECDC4',
            'icon': 'fas fa-leaf',
            'sort_order': 2
        },
        {
            'name': 'body_treatments',
            'display_name': 'Body Treatments & Spa',
            'description': 'Full body wellness and spa treatments',
            'category_type': 'service',
            'color': '#9B59B6',
            'icon': 'fas fa-spa',
            'sort_order': 3
        },
        {
            'name': 'nail_services',
            'display_name': 'Nail Services',
            'description': 'Manicure, pedicure and nail art services',
            'category_type': 'service',
            'color': '#F39C12',
            'icon': 'fas fa-hand-sparkles',
            'sort_order': 4
        },
        {
            'name': 'massage_therapy',
            'display_name': 'Massage Therapy',
            'description': 'Relaxing and therapeutic massage services',
            'category_type': 'service',
            'color': '#E74C3C',
            'icon': 'fas fa-hands',
            'sort_order': 5
        },
        {
            'name': 'bridal_services',
            'display_name': 'Bridal Services',
            'description': 'Complete bridal makeover and wedding services',
            'category_type': 'service',
            'color': '#F8C471',
            'icon': 'fas fa-crown',
            'sort_order': 6
        },
        {
            'name': 'makeup_services',
            'display_name': 'Makeup Services',
            'description': 'Professional makeup and beauty services',
            'category_type': 'service',
            'color': '#AF7AC5',
            'icon': 'fas fa-palette',
            'sort_order': 7
        },
        {
            'name': 'waxing_services',
            'display_name': 'Waxing Services',
            'description': 'Hair removal and waxing treatments',
            'category_type': 'service',
            'color': '#85C1E9',
            'icon': 'fas fa-scissors',
            'sort_order': 8
        },
        {
            'name': 'threading_services',
            'display_name': 'Threading Services',
            'description': 'Eyebrow and facial hair threading',
            'category_type': 'service',
            'color': '#82E0AA',
            'icon': 'fas fa-thread',
            'sort_order': 9
        },
        {
            'name': 'specialty_treatments',
            'display_name': 'Specialty Treatments',
            'description': 'Special and advanced beauty treatments',
            'category_type': 'service',
            'color': '#F7DC6F',
            'icon': 'fas fa-star',
            'sort_order': 10
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

def add_comprehensive_services():
    """Add all services from the provided list with proper categorization"""
    
    with app.app_context():
        try:
            # First create categories
            categories = create_service_categories()
            
            # Comprehensive services data based on the provided image
            services_data = [
                # Hair Services
                {'name': 'Hair Cut', 'description': 'Professional hair cutting service', 'duration': 45, 'price': 800.00, 'category': 'hair_services'},
                {'name': 'Hair Wash & Blow Dry', 'description': 'Hair washing and blow drying service', 'duration': 30, 'price': 600.00, 'category': 'hair_services'},
                {'name': 'Hair Styling', 'description': 'Professional hair styling', 'duration': 60, 'price': 1000.00, 'category': 'hair_services'},
                {'name': 'Hair Color - Full Head', 'description': 'Complete hair coloring service', 'duration': 120, 'price': 2500.00, 'category': 'hair_services'},
                {'name': 'Hair Color - Touch Up', 'description': 'Root touch up coloring', 'duration': 60, 'price': 1500.00, 'category': 'hair_services'},
                {'name': 'Highlights', 'description': 'Hair highlighting service', 'duration': 180, 'price': 3500.00, 'category': 'hair_services'},
                {'name': 'Hair Treatment', 'description': 'Deep conditioning hair treatment', 'duration': 45, 'price': 1200.00, 'category': 'hair_services'},
                {'name': 'Keratin Treatment', 'description': 'Professional keratin smoothing treatment', 'duration': 240, 'price': 8000.00, 'category': 'hair_services'},
                {'name': 'Hair Straightening', 'description': 'Chemical hair straightening', 'duration': 180, 'price': 4000.00, 'category': 'hair_services'},
                {'name': 'Perming', 'description': 'Hair perming service', 'duration': 150, 'price': 3000.00, 'category': 'hair_services'},
                
                # Facial Treatments
                {'name': 'Basic Facial', 'description': 'Essential facial cleansing and moisturizing', 'duration': 60, 'price': 1500.00, 'category': 'facial_treatments'},
                {'name': 'Deep Cleansing Facial', 'description': 'Intensive facial cleansing treatment', 'duration': 75, 'price': 2000.00, 'category': 'facial_treatments'},
                {'name': 'Anti-Aging Facial', 'description': 'Anti-aging facial treatment', 'duration': 90, 'price': 2500.00, 'category': 'facial_treatments'},
                {'name': 'Hydrating Facial', 'description': 'Moisturizing facial treatment', 'duration': 60, 'price': 1800.00, 'category': 'facial_treatments'},
                {'name': 'Acne Treatment Facial', 'description': 'Specialized acne treatment', 'duration': 75, 'price': 2200.00, 'category': 'facial_treatments'},
                {'name': 'Brightening Facial', 'description': 'Skin brightening facial', 'duration': 75, 'price': 2300.00, 'category': 'facial_treatments'},
                {'name': 'Oxygen Facial', 'description': 'Oxygen infusion facial treatment', 'duration': 60, 'price': 2800.00, 'category': 'facial_treatments'},
                {'name': 'Gold Facial', 'description': 'Luxury gold facial treatment', 'duration': 90, 'price': 3500.00, 'category': 'facial_treatments'},
                {'name': 'Diamond Facial', 'description': 'Premium diamond facial', 'duration': 90, 'price': 4000.00, 'category': 'facial_treatments'},
                {'name': 'Fruit Facial', 'description': 'Natural fruit-based facial', 'duration': 60, 'price': 1600.00, 'category': 'facial_treatments'},
                
                # Body Treatments
                {'name': 'Full Body Massage', 'description': 'Complete body relaxation massage', 'duration': 90, 'price': 2500.00, 'category': 'body_treatments'},
                {'name': 'Back Massage', 'description': 'Focused back and shoulder massage', 'duration': 45, 'price': 1500.00, 'category': 'body_treatments'},
                {'name': 'Head & Neck Massage', 'description': 'Relaxing head and neck massage', 'duration': 30, 'price': 800.00, 'category': 'body_treatments'},
                {'name': 'Hot Stone Massage', 'description': 'Therapeutic hot stone massage', 'duration': 90, 'price': 3000.00, 'category': 'body_treatments'},
                {'name': 'Aromatherapy Massage', 'description': 'Essential oil aromatherapy massage', 'duration': 75, 'price': 2200.00, 'category': 'body_treatments'},
                {'name': 'Body Scrub', 'description': 'Full body exfoliation treatment', 'duration': 45, 'price': 1800.00, 'category': 'body_treatments'},
                {'name': 'Body Wrap', 'description': 'Detoxifying body wrap treatment', 'duration': 75, 'price': 2500.00, 'category': 'body_treatments'},
                {'name': 'Body Polishing', 'description': 'Complete body polishing service', 'duration': 60, 'price': 2000.00, 'category': 'body_treatments'},
                
                # Nail Services
                {'name': 'Basic Manicure', 'description': 'Essential nail care and polish', 'duration': 45, 'price': 800.00, 'category': 'nail_services'},
                {'name': 'Gel Manicure', 'description': 'Long-lasting gel nail polish', 'duration': 60, 'price': 1200.00, 'category': 'nail_services'},
                {'name': 'French Manicure', 'description': 'Classic French tip manicure', 'duration': 60, 'price': 1000.00, 'category': 'nail_services'},
                {'name': 'Basic Pedicure', 'description': 'Essential foot care and polish', 'duration': 60, 'price': 1000.00, 'category': 'nail_services'},
                {'name': 'Gel Pedicure', 'description': 'Long-lasting gel pedicure', 'duration': 75, 'price': 1500.00, 'category': 'nail_services'},
                {'name': 'Spa Pedicure', 'description': 'Luxury spa pedicure treatment', 'duration': 90, 'price': 1800.00, 'category': 'nail_services'},
                {'name': 'Nail Art', 'description': 'Creative nail art design', 'duration': 30, 'price': 500.00, 'category': 'nail_services'},
                {'name': 'Nail Extension', 'description': 'Artificial nail extension service', 'duration': 120, 'price': 2000.00, 'category': 'nail_services'},
                
                # Massage Therapy
                {'name': 'Swedish Massage', 'description': 'Classic Swedish relaxation massage', 'duration': 75, 'price': 2200.00, 'category': 'massage_therapy'},
                {'name': 'Deep Tissue Massage', 'description': 'Therapeutic deep tissue massage', 'duration': 90, 'price': 2800.00, 'category': 'massage_therapy'},
                {'name': 'Sports Massage', 'description': 'Specialized sports recovery massage', 'duration': 60, 'price': 2500.00, 'category': 'massage_therapy'},
                {'name': 'Prenatal Massage', 'description': 'Safe pregnancy massage therapy', 'duration': 60, 'price': 2000.00, 'category': 'massage_therapy'},
                {'name': 'Reflexology', 'description': 'Foot reflexology therapy', 'duration': 45, 'price': 1500.00, 'category': 'massage_therapy'},
                {'name': 'Thai Massage', 'description': 'Traditional Thai massage', 'duration': 90, 'price': 2500.00, 'category': 'massage_therapy'},
                
                # Bridal Services
                {'name': 'Bridal Makeup', 'description': 'Complete bridal makeup service', 'duration': 120, 'price': 5000.00, 'category': 'bridal_services'},
                {'name': 'Bridal Hair Styling', 'description': 'Professional bridal hair styling', 'duration': 90, 'price': 3000.00, 'category': 'bridal_services'},
                {'name': 'Bridal Package - Basic', 'description': 'Basic bridal makeover package', 'duration': 180, 'price': 6000.00, 'category': 'bridal_services'},
                {'name': 'Bridal Package - Premium', 'description': 'Premium bridal package with multiple services', 'duration': 300, 'price': 12000.00, 'category': 'bridal_services'},
                {'name': 'Engagement Makeup', 'description': 'Special engagement ceremony makeup', 'duration': 90, 'price': 3500.00, 'category': 'bridal_services'},
                {'name': 'Mehendi Application', 'description': 'Professional henna/mehendi design', 'duration': 120, 'price': 2000.00, 'category': 'bridal_services'},
                
                # Makeup Services
                {'name': 'Party Makeup', 'description': 'Special occasion makeup', 'duration': 60, 'price': 2000.00, 'category': 'makeup_services'},
                {'name': 'Evening Makeup', 'description': 'Elegant evening makeup', 'duration': 75, 'price': 2500.00, 'category': 'makeup_services'},
                {'name': 'Natural Makeup', 'description': 'Subtle natural look makeup', 'duration': 45, 'price': 1500.00, 'category': 'makeup_services'},
                {'name': 'Smokey Eye Makeup', 'description': 'Dramatic smokey eye look', 'duration': 60, 'price': 2200.00, 'category': 'makeup_services'},
                {'name': 'Makeup Trial', 'description': 'Makeup trial session', 'duration': 90, 'price': 1800.00, 'category': 'makeup_services'},
                
                # Waxing Services
                {'name': 'Full Body Wax', 'description': 'Complete body hair removal', 'duration': 120, 'price': 3500.00, 'category': 'waxing_services'},
                {'name': 'Half Body Wax', 'description': 'Upper or lower body waxing', 'duration': 75, 'price': 2000.00, 'category': 'waxing_services'},
                {'name': 'Arms Wax', 'description': 'Full arms hair removal', 'duration': 30, 'price': 800.00, 'category': 'waxing_services'},
                {'name': 'Legs Wax', 'description': 'Full legs hair removal', 'duration': 45, 'price': 1200.00, 'category': 'waxing_services'},
                {'name': 'Underarm Wax', 'description': 'Underarm hair removal', 'duration': 15, 'price': 400.00, 'category': 'waxing_services'},
                {'name': 'Bikini Wax', 'description': 'Bikini area hair removal', 'duration': 30, 'price': 1000.00, 'category': 'waxing_services'},
                {'name': 'Brazilian Wax', 'description': 'Complete intimate area waxing', 'duration': 45, 'price': 1800.00, 'category': 'waxing_services'},
                {'name': 'Facial Wax', 'description': 'Facial hair removal', 'duration': 20, 'price': 500.00, 'category': 'waxing_services'},
                {'name': 'Eyebrow Wax', 'description': 'Eyebrow shaping with wax', 'duration': 15, 'price': 300.00, 'category': 'waxing_services'},
                {'name': 'Upper Lip Wax', 'description': 'Upper lip hair removal', 'duration': 10, 'price': 200.00, 'category': 'waxing_services'},
                
                # Threading Services
                {'name': 'Eyebrow Threading', 'description': 'Precise eyebrow shaping', 'duration': 20, 'price': 300.00, 'category': 'threading_services'},
                {'name': 'Upper Lip Threading', 'description': 'Upper lip hair threading', 'duration': 10, 'price': 150.00, 'category': 'threading_services'},
                {'name': 'Chin Threading', 'description': 'Chin hair removal threading', 'duration': 15, 'price': 200.00, 'category': 'threading_services'},
                {'name': 'Forehead Threading', 'description': 'Forehead hair threading', 'duration': 15, 'price': 200.00, 'category': 'threading_services'},
                {'name': 'Full Face Threading', 'description': 'Complete facial hair threading', 'duration': 30, 'price': 600.00, 'category': 'threading_services'},
                
                # Specialty Treatments
                {'name': 'Microdermabrasion', 'description': 'Professional skin resurfacing treatment', 'duration': 60, 'price': 3000.00, 'category': 'specialty_treatments'},
                {'name': 'Chemical Peel', 'description': 'Professional chemical peel treatment', 'duration': 45, 'price': 2500.00, 'category': 'specialty_treatments'},
                {'name': 'Laser Hair Removal', 'description': 'Permanent laser hair removal', 'duration': 30, 'price': 3500.00, 'category': 'specialty_treatments'},
                {'name': 'Botox Treatment', 'description': 'Professional botox injection', 'duration': 30, 'price': 8000.00, 'category': 'specialty_treatments'},
                {'name': 'Dermal Fillers', 'description': 'Professional dermal filler treatment', 'duration': 45, 'price': 12000.00, 'category': 'specialty_treatments'},
                {'name': 'Vampire Facial', 'description': 'PRP facial treatment', 'duration': 90, 'price': 8000.00, 'category': 'specialty_treatments'},
                {'name': 'Hydrafacial', 'description': 'Advanced hydrating facial treatment', 'duration': 60, 'price': 4000.00, 'category': 'specialty_treatments'},
                {'name': 'LED Light Therapy', 'description': 'Professional LED skin therapy', 'duration': 30, 'price': 1500.00, 'category': 'specialty_treatments'},
                {'name': 'Radiofrequency Treatment', 'description': 'RF skin tightening treatment', 'duration': 45, 'price': 5000.00, 'category': 'specialty_treatments'},
                {'name': 'Cryotherapy', 'description': 'Cold therapy treatment', 'duration': 30, 'price': 2000.00, 'category': 'specialty_treatments'}
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
                    print(f"Adding service: {service_data['name']} - ₹{service_data['price']}")
                else:
                    print(f"Service already exists: {service_data['name']}")
            
            if added_count > 0:
                db.session.commit()
                print(f"\n✅ Successfully added {added_count} comprehensive services to the database!")
                print("🏷️ All services have been properly categorized")
            else:
                print("\n⚠️ All services already exist in the database")
            
            # Print summary
            total_categories = len(categories)
            total_services = Service.query.count()
            print(f"\n📊 Summary:")
            print(f"   - Total Categories: {total_categories}")
            print(f"   - Total Services: {total_services}")
            print(f"   - Services Added This Run: {added_count}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding services: {str(e)}")
            raise e

if __name__ == "__main__":
    add_comprehensive_services()
