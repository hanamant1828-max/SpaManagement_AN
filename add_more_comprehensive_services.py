
#!/usr/bin/env python3
"""
Add more comprehensive spa/salon services to the database
"""
from main import app
from models import db, Service, Category
from datetime import datetime

def add_comprehensive_services():
    """Add a comprehensive list of spa/salon services"""
    
    with app.app_context():
        print("🔄 Adding comprehensive spa/salon services...")
        
        # Enhanced service list with better categorization
        comprehensive_services = [
            # Hair Services
            {
                'name': 'Basic Hair Cut & Styling',
                'description': 'Professional hair cut with basic styling and blow dry',
                'price': 500.0,
                'duration': 60,
                'category_name': 'Hair Services'
            },
            {
                'name': 'Hair Wash & Deep Conditioning',
                'description': 'Thorough hair wash with deep conditioning treatment',
                'price': 400.0,
                'duration': 45,
                'category_name': 'Hair Services'
            },
            {
                'name': 'Professional Hair Color - Full',
                'description': 'Complete hair coloring with professional products',
                'price': 3500.0,
                'duration': 180,
                'category_name': 'Hair Services'
            },
            {
                'name': 'Hair Highlights - Partial',
                'description': 'Partial highlighting for accent and dimension',
                'price': 2500.0,
                'duration': 120,
                'category_name': 'Hair Services'
            },
            {
                'name': 'Keratin Hair Treatment',
                'description': 'Professional keratin treatment for smooth, manageable hair',
                'price': 5500.0,
                'duration': 240,
                'category_name': 'Hair Services'
            },
            
            # Facial Services
            {
                'name': 'Classic European Facial',
                'description': 'Traditional European facial with cleansing and moisturizing',
                'price': 1200.0,
                'duration': 75,
                'category_name': 'Facial Services'
            },
            {
                'name': 'Anti-Aging Diamond Facial',
                'description': 'Luxury anti-aging facial with diamond particles',
                'price': 2800.0,
                'duration': 90,
                'category_name': 'Facial Services'
            },
            {
                'name': 'Acne Treatment Facial',
                'description': 'Specialized facial for acne-prone skin',
                'price': 1800.0,
                'duration': 60,
                'category_name': 'Facial Services'
            },
            {
                'name': 'Hydrating Collagen Facial',
                'description': 'Deep hydrating facial with collagen mask',
                'price': 2200.0,
                'duration': 80,
                'category_name': 'Facial Services'
            },
            {
                'name': 'Vitamin C Brightening Facial',
                'description': 'Brightening facial with vitamin C serum',
                'price': 1600.0,
                'duration': 70,
                'category_name': 'Facial Services'
            },
            
            # Massage Services
            {
                'name': 'Relaxing Swedish Massage',
                'description': 'Classic Swedish massage for relaxation and stress relief',
                'price': 1800.0,
                'duration': 90,
                'category_name': 'Massage Services'
            },
            {
                'name': 'Deep Tissue Therapeutic Massage',
                'description': 'Intensive massage targeting muscle knots and tension',
                'price': 2200.0,
                'duration': 90,
                'category_name': 'Massage Services'
            },
            {
                'name': 'Hot Stone Massage Therapy',
                'description': 'Relaxing massage using heated volcanic stones',
                'price': 2800.0,
                'duration': 105,
                'category_name': 'Massage Services'
            },
            {
                'name': 'Aromatherapy Massage',
                'description': 'Therapeutic massage with essential oils',
                'price': 2000.0,
                'duration': 85,
                'category_name': 'Massage Services'
            },
            {
                'name': 'Couple\'s Massage Session',
                'description': 'Relaxing massage session for couples',
                'price': 4000.0,
                'duration': 90,
                'category_name': 'Massage Services'
            },
            
            # Body Treatments
            {
                'name': 'Full Body Exfoliation & Wrap',
                'description': 'Complete body scrub with nourishing wrap',
                'price': 2500.0,
                'duration': 120,
                'category_name': 'Body Treatments'
            },
            {
                'name': 'Detoxifying Mud Wrap',
                'description': 'Purifying mud wrap for body detox',
                'price': 2200.0,
                'duration': 90,
                'category_name': 'Body Treatments'
            },
            {
                'name': 'Anti-Cellulite Body Treatment',
                'description': 'Specialized treatment for cellulite reduction',
                'price': 3000.0,
                'duration': 105,
                'category_name': 'Body Treatments'
            },
            
            # Nail Services
            {
                'name': 'Classic Manicure',
                'description': 'Traditional manicure with nail shaping and polish',
                'price': 600.0,
                'duration': 45,
                'category_name': 'Nail Services'
            },
            {
                'name': 'Luxury Spa Pedicure',
                'description': 'Complete pedicure with foot massage and treatment',
                'price': 800.0,
                'duration': 60,
                'category_name': 'Nail Services'
            },
            {
                'name': 'Gel Polish Manicure',
                'description': 'Long-lasting gel polish application',
                'price': 900.0,
                'duration': 50,
                'category_name': 'Nail Services'
            },
            {
                'name': 'Nail Art & Design',
                'description': 'Custom nail art and decorative designs',
                'price': 1200.0,
                'duration': 75,
                'category_name': 'Nail Services'
            },
            {
                'name': 'Acrylic Nail Extension',
                'description': 'Professional acrylic nail extensions',
                'price': 1500.0,
                'duration': 90,
                'category_name': 'Nail Services'
            },
            
            # Waxing & Hair Removal
            {
                'name': 'Full Leg Waxing',
                'description': 'Complete leg waxing service',
                'price': 1000.0,
                'duration': 60,
                'category_name': 'Waxing Services'
            },
            {
                'name': 'Brazilian Waxing',
                'description': 'Complete bikini area waxing',
                'price': 1200.0,
                'duration': 45,
                'category_name': 'Waxing Services'
            },
            {
                'name': 'Underarm Waxing',
                'description': 'Quick and efficient underarm waxing',
                'price': 300.0,
                'duration': 15,
                'category_name': 'Waxing Services'
            },
            {
                'name': 'Full Body Waxing',
                'description': 'Complete body waxing service',
                'price': 3500.0,
                'duration': 150,
                'category_name': 'Waxing Services'
            },
            
            # Threading & Eyebrow
            {
                'name': 'Eyebrow Threading & Shaping',
                'description': 'Precise eyebrow shaping using threading technique',
                'price': 200.0,
                'duration': 20,
                'category_name': 'Threading Services'
            },
            {
                'name': 'Full Face Threading',
                'description': 'Complete facial hair removal using threading',
                'price': 500.0,
                'duration': 30,
                'category_name': 'Threading Services'
            },
            {
                'name': 'Upper Lip Threading',
                'description': 'Quick upper lip hair removal',
                'price': 100.0,
                'duration': 10,
                'category_name': 'Threading Services'
            },
            
            # Makeup Services
            {
                'name': 'Bridal Makeup - Full',
                'description': 'Complete bridal makeup with trial session',
                'price': 5000.0,
                'duration': 180,
                'category_name': 'Makeup Services'
            },
            {
                'name': 'Party Makeup',
                'description': 'Glamorous makeup for special occasions',
                'price': 2500.0,
                'duration': 90,
                'category_name': 'Makeup Services'
            },
            {
                'name': 'Natural Day Makeup',
                'description': 'Light, natural makeup for everyday wear',
                'price': 1200.0,
                'duration': 45,
                'category_name': 'Makeup Services'
            },
            
            # Specialized Packages
            {
                'name': 'Pre-Wedding Glow Package',
                'description': 'Complete beauty preparation for brides-to-be',
                'price': 8500.0,
                'duration': 300,
                'category_name': 'Special Packages'
            },
            {
                'name': 'Mother\'s Day Spa Special',
                'description': 'Relaxing spa day package for mothers',
                'price': 4500.0,
                'duration': 240,
                'category_name': 'Special Packages'
            },
            {
                'name': 'Men\'s Grooming Package',
                'description': 'Complete grooming package designed for men',
                'price': 2800.0,
                'duration': 120,
                'category_name': 'Men\'s Services'
            }
        ]
        
        services_added = 0
        
        for service_data in comprehensive_services:
            # Check if service already exists
            existing_service = Service.query.filter_by(name=service_data['name']).first()
            if existing_service:
                print(f"⏭️  Service already exists: {service_data['name']}")
                continue
            
            # Find or create category
            category = None
            if service_data.get('category_name'):
                category = Category.query.filter_by(
                    name=service_data['category_name'], 
                    category_type='service'
                ).first()
                
                if not category:
                    category = Category(
                        name=service_data['category_name'],
                        display_name=service_data['category_name'],
                        category_type='service',
                        is_active=True,
                        created_at=datetime.utcnow()
                    )
                    db.session.add(category)
                    db.session.flush()
            
            # Create service
            service = Service(
                name=service_data['name'],
                description=service_data['description'],
                price=service_data['price'],
                duration=service_data['duration'],
                category_id=category.id if category else None,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(service)
            services_added += 1
            print(f"✅ Added service: {service_data['name']} - ₹{service_data['price']}")
        
        try:
            db.session.commit()
            print(f"\n🎉 Successfully added {services_added} new services to the database!")
            
            # Print summary
            total_services = Service.query.filter_by(is_active=True).count()
            print(f"📊 Total services in database: {total_services}")
            
            # Services by category
            categories = Category.query.filter_by(category_type='service', is_active=True).all()
            print(f"\n📋 Services by Category:")
            for category in categories:
                service_count = Service.query.filter_by(category_id=category.id, is_active=True).count()
                print(f"   {category.display_name}: {service_count} services")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding services: {str(e)}")

if __name__ == "__main__":
    add_comprehensive_services()
