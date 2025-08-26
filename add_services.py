
#!/usr/bin/env python3
"""
Add 10 comprehensive spa services to the database
"""
from app import app, db
from models import Service, Category

def add_comprehensive_services():
    """Add 10 comprehensive spa services"""
    
    with app.app_context():
        # Define 10 comprehensive spa services
        services_data = [
            {
                'name': 'Classic Haircut & Style',
                'description': 'Professional haircut with wash, cut, and basic styling',
                'duration': 45,
                'price': 500.00,
                'category_name': 'hair'
            },
            {
                'name': 'Premium Facial Treatment',
                'description': 'Deep cleansing facial with moisturizing and anti-aging treatment',
                'duration': 75,
                'price': 1200.00,
                'category_name': 'facial'
            },
            {
                'name': 'Classic Manicure',
                'description': 'Complete nail care with cuticle treatment, filing, and polish',
                'duration': 45,
                'price': 400.00,
                'category_name': 'nail'
            },
            {
                'name': 'Classic Pedicure', 
                'description': 'Relaxing foot care with exfoliation, massage, and polish',
                'duration': 60,
                'price': 500.00,
                'category_name': 'nail'
            },
            {
                'name': 'Deluxe Manicure & Pedicure',
                'description': 'Premium nail care package with spa treatment and gel polish',
                'duration': 90,
                'price': 1000.00,
                'category_name': 'nail'
            },
            {
                'name': 'Hair Color & Highlights',
                'description': 'Professional hair coloring service with highlights and styling',
                'duration': 120,
                'price': 2500.00,
                'category_name': 'hair'
            },
            {
                'name': 'Deluxe Facial & Cleanup',
                'description': 'Advanced facial treatment with deep pore cleansing and hydration',
                'duration': 90,
                'price': 1500.00,
                'category_name': 'facial'
            },
            {
                'name': 'Classic Shave & Beard Trim',
                'description': 'Traditional wet shave with hot towel treatment and beard styling',
                'duration': 30,
                'price': 300.00,
                'category_name': 'hair'
            },
            {
                'name': 'Hair Spa Treatment',
                'description': 'Deep conditioning hair treatment with scalp massage and styling',
                'duration': 90,
                'price': 800.00,
                'category_name': 'hair'
            },
            {
                'name': 'Hand & Foot Reflexology',
                'description': 'Therapeutic pressure point massage for hands and feet',
                'duration': 60,
                'price': 700.00,
                'category_name': 'massage'
            }
        ]
        
        services_added = 0
        
        for service_data in services_data:
            # Check if service already exists
            existing_service = Service.query.filter_by(name=service_data['name']).first()
            if existing_service:
                print(f"Service '{service_data['name']}' already exists, skipping...")
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
        categories = Category.query.filter_by(category_type='service', is_active=True).all()
        for category in categories:
            service_count = Service.query.filter_by(category_id=category.id, is_active=True).count()
            print(f"  {category.display_name}: {service_count} services")

if __name__ == '__main__':
    add_comprehensive_services()
