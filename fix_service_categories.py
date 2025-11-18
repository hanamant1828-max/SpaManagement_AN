
from app import app, db
from models import Service, Category

with app.app_context():
    print("Fixing services with missing category names...")
    
    # Get all services with category_id but no category name
    services = Service.query.filter(
        Service.category_id.isnot(None),
        db.or_(Service.category.is_(None), Service.category == '')
    ).all()
    
    print(f"Found {len(services)} services to fix")
    
    for service in services:
        category = Category.query.get(service.category_id)
        if category:
            service.category = category.name
            print(f"✅ Updated service '{service.name}' with category '{category.name}'")
        else:
            service.category = 'general'
            print(f"⚠️ Category ID {service.category_id} not found for service '{service.name}', set to 'general'")
    
    # Fix services with no category_id at all
    services_no_category = Service.query.filter(
        db.or_(Service.category_id.is_(None), Service.category_id == 0),
        db.or_(Service.category.is_(None), Service.category == '')
    ).all()
    
    print(f"\nFound {len(services_no_category)} services with no category")
    
    for service in services_no_category:
        service.category = 'general'
        print(f"✅ Set service '{service.name}' category to 'general'")
    
    db.session.commit()
    print("\n✅ All services updated successfully!")
    
    # Show summary
    all_services = Service.query.all()
    print(f"\n📊 Summary:")
    print(f"Total services: {len(all_services)}")
    for svc in all_services:
        cat_name = svc.service_category.display_name if svc.service_category else 'None'
        print(f"  - {svc.name}: category={svc.category}, category_id={svc.category_id}, display={cat_name}")
