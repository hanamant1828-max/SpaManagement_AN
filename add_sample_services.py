
#!/usr/bin/env python3
"""
Script to add sample services to the spa management system
"""

from app import app, db
from models import Service, Category
from datetime import datetime

def add_sample_services():
    """Add comprehensive sample services to the database"""
    
    with app.app_context():
        try:
            # First, create service categories if they don't exist
            categories_data = [
                {
                    'name': 'massage',
                    'display_name': 'Massage Therapy',
                    'description': 'Relaxing and therapeutic massage services',
                    'category_type': 'service',
                    'color': '#FF6B6B',
                    'icon': 'fas fa-hands',
                    'sort_order': 1
                },
                {
                    'name': 'facial',
                    'display_name': 'Facial Treatments',
                    'description': 'Skincare and facial beauty treatments',
                    'category_type': 'service',
                    'color': '#4ECDC4',
                    'icon': 'fas fa-leaf',
                    'sort_order': 2
                },
                {
                    'name': 'hair',
                    'display_name': 'Hair Services',
                    'description': 'Hair cutting, styling and treatments',
                    'category_type': 'service',
                    'color': '#45B7D1',
                    'icon': 'fas fa-cut',
                    'sort_order': 3
                },
                {
                    'name': 'nails',
                    'display_name': 'Nail Care',
                    'description': 'Manicure, pedicure and nail art services',
                    'category_type': 'service',
                    'color': '#F39C12',
                    'icon': 'fas fa-hand-sparkles',
                    'sort_order': 4
                },
                {
                    'name': 'body',
                    'display_name': 'Body Treatments',
                    'description': 'Full body wellness and beauty treatments',
                    'category_type': 'service',
                    'color': '#9B59B6',
                    'icon': 'fas fa-spa',
                    'sort_order': 5
                }
            ]
            
            # Create categories
            categories = {}
            for cat_data in categories_data:
                existing_cat = Category.query.filter_by(name=cat_data['name'], category_type='service').first()
                if not existing_cat:
                    category = Category(**cat_data)
                    db.session.add(category)
                    db.session.flush()  # Get the ID
                    categories[cat_data['name']] = category.id
                    print(f"Created category: {cat_data['display_name']}")
                else:
                    categories[cat_data['name']] = existing_cat.id
                    print(f"Category already exists: {cat_data['display_name']}")
            
            db.session.commit()
            
            # Sample services data
            sample_services = [
                # Massage Services
                {
                    'name': 'Swedish Massage',
                    'description': 'Classic relaxing full-body Swedish massage with long, flowing strokes',
                    'duration': 60,
                    'price': 75.00,
                    'category': 'massage',
                    'category_id': categories.get('massage')
                },
                {
                    'name': 'Deep Tissue Massage',
                    'description': 'Therapeutic massage targeting deep muscle layers and chronic tension',
                    'duration': 90,
                    'price': 95.00,
                    'category': 'massage',
                    'category_id': categories.get('massage')
                },
                {
                    'name': 'Hot Stone Massage',
                    'description': 'Luxurious massage using heated volcanic stones for ultimate relaxation',
                    'duration': 75,
                    'price': 110.00,
                    'category': 'massage',
                    'category_id': categories.get('massage')
                },
                {
                    'name': 'Prenatal Massage',
                    'description': 'Gentle, safe massage specifically designed for expecting mothers',
                    'duration': 60,
                    'price': 80.00,
                    'category': 'massage',
                    'category_id': categories.get('massage')
                },
                {
                    'name': 'Couples Massage',
                    'description': 'Romantic side-by-side massage experience for two people',
                    'duration': 60,
                    'price': 150.00,
                    'category': 'massage',
                    'category_id': categories.get('massage')
                },
                
                # Facial Services
                {
                    'name': 'Classic European Facial',
                    'description': 'Deep cleansing facial with extraction, mask, and moisturizing',
                    'duration': 60,
                    'price': 65.00,
                    'category': 'facial',
                    'category_id': categories.get('facial')
                },
                {
                    'name': 'Anti-Aging Facial',
                    'description': 'Advanced facial treatment targeting fine lines and age spots',
                    'duration': 75,
                    'price': 85.00,
                    'category': 'facial',
                    'category_id': categories.get('facial')
                },
                {
                    'name': 'Hydrating Facial',
                    'description': 'Intensive moisturizing treatment for dry and dehydrated skin',
                    'duration': 60,
                    'price': 70.00,
                    'category': 'facial',
                    'category_id': categories.get('facial')
                },
                {
                    'name': 'Acne Treatment Facial',
                    'description': 'Specialized facial for acne-prone skin with deep pore cleansing',
                    'duration': 90,
                    'price': 80.00,
                    'category': 'facial',
                    'category_id': categories.get('facial')
                },
                {
                    'name': 'Express Facial',
                    'description': 'Quick 30-minute facial perfect for busy schedules',
                    'duration': 30,
                    'price': 45.00,
                    'category': 'facial',
                    'category_id': categories.get('facial')
                },
                
                # Hair Services
                {
                    'name': 'Haircut & Blow Dry',
                    'description': 'Professional haircut with styling and blow dry finish',
                    'duration': 45,
                    'price': 35.00,
                    'category': 'hair',
                    'category_id': categories.get('hair')
                },
                {
                    'name': 'Hair Color - Full',
                    'description': 'Complete hair coloring service with professional products',
                    'duration': 120,
                    'price': 85.00,
                    'category': 'hair',
                    'category_id': categories.get('hair')
                },
                {
                    'name': 'Hair Highlights',
                    'description': 'Partial highlighting to add dimension and brightness',
                    'duration': 90,
                    'price': 65.00,
                    'category': 'hair',
                    'category_id': categories.get('hair')
                },
                {
                    'name': 'Deep Hair Treatment',
                    'description': 'Intensive conditioning treatment for damaged or dry hair',
                    'duration': 60,
                    'price': 40.00,
                    'category': 'hair',
                    'category_id': categories.get('hair')
                },
                {
                    'name': 'Bridal Hair Styling',
                    'description': 'Elegant updo styling perfect for weddings and special events',
                    'duration': 90,
                    'price': 75.00,
                    'category': 'hair',
                    'category_id': categories.get('hair')
                },
                
                # Nail Services
                {
                    'name': 'Classic Manicure',
                    'description': 'Traditional manicure with nail shaping, cuticle care, and polish',
                    'duration': 45,
                    'price': 25.00,
                    'category': 'nails',
                    'category_id': categories.get('nails')
                },
                {
                    'name': 'Gel Manicure',
                    'description': 'Long-lasting gel polish manicure with UV curing',
                    'duration': 60,
                    'price': 35.00,
                    'category': 'nails',
                    'category_id': categories.get('nails')
                },
                {
                    'name': 'Classic Pedicure',
                    'description': 'Relaxing foot care with soak, scrub, massage, and polish',
                    'duration': 60,
                    'price': 35.00,
                    'category': 'nails',
                    'category_id': categories.get('nails')
                },
                {
                    'name': 'Spa Pedicure',
                    'description': 'Luxurious pedicure with extended massage and premium products',
                    'duration': 75,
                    'price': 50.00,
                    'category': 'nails',
                    'category_id': categories.get('nails')
                },
                {
                    'name': 'Nail Art Design',
                    'description': 'Custom nail art and decorative designs',
                    'duration': 30,
                    'price': 15.00,
                    'category': 'nails',
                    'category_id': categories.get('nails')
                },
                
                # Body Treatments
                {
                    'name': 'Full Body Scrub',
                    'description': 'Exfoliating body treatment to remove dead skin and moisturize',
                    'duration': 45,
                    'price': 60.00,
                    'category': 'body',
                    'category_id': categories.get('body')
                },
                {
                    'name': 'Body Wrap Treatment',
                    'description': 'Detoxifying and hydrating body wrap with natural ingredients',
                    'duration': 90,
                    'price': 85.00,
                    'category': 'body',
                    'category_id': categories.get('body')
                },
                {
                    'name': 'Aromatherapy Session',
                    'description': 'Relaxing treatment using essential oils for mind and body wellness',
                    'duration': 60,
                    'price': 70.00,
                    'category': 'body',
                    'category_id': categories.get('body')
                },
                {
                    'name': 'Reflexology',
                    'description': 'Therapeutic foot massage targeting pressure points',
                    'duration': 45,
                    'price': 55.00,
                    'category': 'body',
                    'category_id': categories.get('body')
                },
                {
                    'name': 'Brazilian Waxing',
                    'description': 'Professional hair removal service for smooth skin',
                    'duration': 30,
                    'price': 45.00,
                    'category': 'body',
                    'category_id': categories.get('body')
                }
            ]
            
            # Check existing services and add new ones
            existing_services = set()
            for service in Service.query.all():
                existing_services.add(service.name.lower())
            
            added_count = 0
            for service_data in sample_services:
                if service_data['name'].lower() not in existing_services:
                    service = Service(
                        name=service_data['name'],
                        description=service_data['description'],
                        duration=service_data['duration'],
                        price=service_data['price'],
                        category=service_data['category'],
                        category_id=service_data['category_id'],
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
                print(f"\n✅ Successfully added {added_count} sample services to the database!")
            else:
                print("\n⚠️ All sample services already exist in the database.")
                
            # Display all services by category
            all_services = Service.query.filter_by(is_active=True).order_by(Service.category, Service.name).all()
            print(f"\nTotal active services in database: {len(all_services)}")
            
            current_category = None
            for service in all_services:
                if service.category != current_category:
                    current_category = service.category
                    print(f"\n📋 {current_category.upper()} SERVICES:")
                print(f"  • {service.name} ({service.duration} min) - ${service.price}")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding services: {str(e)}")

if __name__ == '__main__':
    add_sample_services()
