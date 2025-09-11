
from app import app, db
from models import Service, Category

def create_default_services():
    """Create default services for the spa system"""
    with app.app_context():
        # Check if services already exist
        existing_services = Service.query.count()
        if existing_services > 0:
            print(f"Services already exist ({existing_services} found). Skipping creation.")
            return

        # Get or create service categories
        facial_category = Category.query.filter_by(name='service_facial').first()
        massage_category = Category.query.filter_by(name='service_massage').first()
        hair_category = Category.query.filter_by(name='service_hair').first()

        # Create default services
        default_services = [
            {
                'name': 'Classic Facial',
                'description': 'Deep cleansing facial with moisturizing',
                'price': 80.00,
                'duration': 60,
                'category_id': facial_category.id if facial_category else None,
                'is_active': True
            },
            {
                'name': 'Anti-Aging Facial',
                'description': 'Advanced anti-aging treatment',
                'price': 120.00,
                'duration': 75,
                'category_id': facial_category.id if facial_category else None,
                'is_active': True
            },
            {
                'name': 'Swedish Massage',
                'description': 'Relaxing full body massage',
                'price': 100.00,
                'duration': 60,
                'category_id': massage_category.id if massage_category else None,
                'is_active': True
            },
            {
                'name': 'Deep Tissue Massage',
                'description': 'Therapeutic deep tissue massage',
                'price': 120.00,
                'duration': 60,
                'category_id': massage_category.id if massage_category else None,
                'is_active': True
            },
            {
                'name': 'Hair Cut & Style',
                'description': 'Professional hair cut and styling',
                'price': 65.00,
                'duration': 45,
                'category_id': hair_category.id if hair_category else None,
                'is_active': True
            },
            {
                'name': 'Hair Color & Highlights',
                'description': 'Hair coloring and highlight service',
                'price': 150.00,
                'duration': 120,
                'category_id': hair_category.id if hair_category else None,
                'is_active': True
            }
        ]

        try:
            for service_data in default_services:
                service = Service(**service_data)
                db.session.add(service)
            
            db.session.commit()
            print(f"✅ Created {len(default_services)} default services successfully!")
            
            # List created services
            print("\nCreated services:")
            for service in Service.query.all():
                print(f"  - {service.name}: ${service.price} ({service.duration} min)")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating services: {e}")

if __name__ == "__main__":
    create_default_services()
