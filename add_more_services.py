
#!/usr/bin/env python3
"""
Add comprehensive spa/salon services to the database
"""
from app import app, db
from models import Service, Category

def add_comprehensive_services():
    """Add comprehensive spa/salon services"""
    
    with app.app_context():
        # Define comprehensive spa/salon services
        services_data = [
            # Hair Services
            {
                'name': 'Hair Wash & Blow Dry',
                'description': 'Professional hair wash with conditioning and blow dry styling',
                'duration': 30,
                'price': 300.00,
                'category_name': 'hair'
            },
            {
                'name': 'Hair Color - Single Process',
                'description': 'Full hair coloring with professional color products',
                'duration': 120,
                'price': 2500.00,
                'category_name': 'hair'
            },
            {
                'name': 'Hair Highlights',
                'description': 'Professional highlighting technique for natural-looking dimension',
                'duration': 150,
                'price': 3500.00,
                'category_name': 'hair'
            },
            {
                'name': 'Hair Straightening Treatment',
                'description': 'Keratin treatment for smooth, frizz-free hair',
                'duration': 180,
                'price': 4500.00,
                'category_name': 'hair'
            },
            {
                'name': 'Bridal Hair Styling',
                'description': 'Complete bridal hairstyling with accessories',
                'duration': 90,
                'price': 2000.00,
                'category_name': 'hair'
            },
            
            # Facial Services
            {
                'name': 'Deep Cleansing Facial',
                'description': 'Intensive facial treatment for deep pore cleansing',
                'duration': 60,
                'price': 800.00,
                'category_name': 'facial'
            },
            {
                'name': 'Anti-Aging Facial',
                'description': 'Specialized facial treatment to reduce signs of aging',
                'duration': 75,
                'price': 1500.00,
                'category_name': 'facial'
            },
            {
                'name': 'Hydrating Facial',
                'description': 'Moisturizing facial for dry and dehydrated skin',
                'duration': 60,
                'price': 1000.00,
                'category_name': 'facial'
            },
            {
                'name': 'Acne Treatment Facial',
                'description': 'Specialized treatment for acne-prone skin',
                'duration': 70,
                'price': 1200.00,
                'category_name': 'facial'
            },
            {
                'name': 'Gold Facial',
                'description': 'Luxury facial treatment with 24k gold for radiant skin',
                'duration': 90,
                'price': 2500.00,
                'category_name': 'facial'
            },
            
            # Body Services
            {
                'name': 'Full Body Massage',
                'description': 'Relaxing full body massage with aromatherapy oils',
                'duration': 90,
                'price': 1800.00,
                'category_name': 'massage'
            },
            {
                'name': 'Swedish Massage',
                'description': 'Classic Swedish massage for stress relief and relaxation',
                'duration': 60,
                'price': 1200.00,
                'category_name': 'massage'
            },
            {
                'name': 'Deep Tissue Massage',
                'description': 'Therapeutic massage targeting muscle tension and knots',
                'duration': 75,
                'price': 1500.00,
                'category_name': 'massage'
            },
            {
                'name': 'Hot Stone Massage',
                'description': 'Relaxing massage using heated stones for deep relaxation',
                'duration': 90,
                'price': 2000.00,
                'category_name': 'massage'
            },
            {
                'name': 'Body Scrub & Wrap',
                'description': 'Exfoliating body scrub followed by nourishing wrap',
                'duration': 75,
                'price': 1600.00,
                'category_name': 'massage'
            },
            
            # Nail Services
            {
                'name': 'Gel Manicure',
                'description': 'Long-lasting gel polish manicure with nail art options',
                'duration': 60,
                'price': 600.00,
                'category_name': 'nail'
            },
            {
                'name': 'Gel Pedicure',
                'description': 'Professional gel pedicure with foot massage',
                'duration': 75,
                'price': 700.00,
                'category_name': 'nail'
            },
            {
                'name': 'Nail Art Design',
                'description': 'Creative nail art with custom designs',
                'duration': 45,
                'price': 800.00,
                'category_name': 'nail'
            },
            {
                'name': 'Nail Extension - Acrylic',
                'description': 'Acrylic nail extensions with shaping and polish',
                'duration': 120,
                'price': 1200.00,
                'category_name': 'nail'
            },
            {
                'name': 'French Manicure',
                'description': 'Classic French manicure with white tips',
                'duration': 50,
                'price': 500.00,
                'category_name': 'nail'
            },
            
            # Waxing Services
            {
                'name': 'Full Leg Waxing',
                'description': 'Complete leg hair removal with premium wax',
                'duration': 60,
                'price': 800.00,
                'category_name': 'waxing'
            },
            {
                'name': 'Half Leg Waxing',
                'description': 'Lower leg hair removal treatment',
                'duration': 30,
                'price': 400.00,
                'category_name': 'waxing'
            },
            {
                'name': 'Bikini Waxing',
                'description': 'Professional bikini area hair removal',
                'duration': 30,
                'price': 600.00,
                'category_name': 'waxing'
            },
            {
                'name': 'Underarm Waxing',
                'description': 'Quick and effective underarm hair removal',
                'duration': 15,
                'price': 200.00,
                'category_name': 'waxing'
            },
            {
                'name': 'Eyebrow Shaping',
                'description': 'Professional eyebrow shaping and grooming',
                'duration': 20,
                'price': 250.00,
                'category_name': 'waxing'
            },
            
            # Threading Services
            {
                'name': 'Eyebrow Threading',
                'description': 'Precise eyebrow shaping using threading technique',
                'duration': 15,
                'price': 150.00,
                'category_name': 'threading'
            },
            {
                'name': 'Upper Lip Threading',
                'description': 'Upper lip hair removal using threading',
                'duration': 10,
                'price': 100.00,
                'category_name': 'threading'
            },
            {
                'name': 'Full Face Threading',
                'description': 'Complete facial hair removal using threading',
                'duration': 30,
                'price': 400.00,
                'category_name': 'threading'
            },
            
            # Bridal Services
            {
                'name': 'Bridal Makeup',
                'description': 'Complete bridal makeup with trial session',
                'duration': 120,
                'price': 3500.00,
                'category_name': 'bridal'
            },
            {
                'name': 'Bridal Package - Full Day',
                'description': 'Complete bridal package including hair, makeup, and touch-ups',
                'duration': 240,
                'price': 8000.00,
                'category_name': 'bridal'
            },
            {
                'name': 'Pre-Bridal Treatment',
                'description': 'Comprehensive pre-bridal skin and hair treatment package',
                'duration': 180,
                'price': 4500.00,
                'category_name': 'bridal'
            }
        ]
        
        print("🔄 Adding comprehensive spa/salon services...")
        services_added = 0
        
        for service_data in services_data:
            # Check if service already exists
            existing_service = Service.query.filter_by(name=service_data['name']).first()
            if existing_service:
                print(f"⚠️  Service '{service_data['name']}' already exists, skipping...")
                continue
            
            # Get category by name
            category = Category.query.filter_by(
                name=service_data['category_name'], 
                category_type='service'
            ).first()
            
            # Create the service
            service = Service(
                name=service_data['name'],
                description=service_data['description'],
                duration=service_data['duration'],
                price=service_data['price'],
                category_id=category.id if category else None,
                category=service_data['category_name'],  # Fallback
                is_active=True
            )
            
            db.session.add(service)
            services_added += 1
            print(f"✅ Added service: {service_data['name']} - ₹{service_data['price']}")
        
        # Commit all services
        db.session.commit()
        print(f"\n🎉 Successfully added {services_added} services to the database!")
        
        # Display summary
        total_services = Service.query.count()
        print(f"📊 Total services in database: {total_services}")
        
        # Show services by category
        print("\n📋 Services by Category:")
        categories = Category.query.filter_by(category_type='service').all()
        for category in categories:
            service_count = Service.query.filter_by(category_id=category.id).count()
            print(f"   {category.display_name}: {service_count} services")

if __name__ == '__main__':
    add_comprehensive_services()
