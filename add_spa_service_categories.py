
#!/usr/bin/env python3
"""
Script to add comprehensive spa service categories
"""

from app import app, db
from models import Category
from datetime import datetime

def add_spa_service_categories():
    """Add comprehensive spa service categories to the database"""
    
    with app.app_context():
        try:
            # Comprehensive spa service categories
            categories_data = [
                {
                    'name': 'hair_services',
                    'display_name': 'Hair Services',
                    'description': 'General hair cutting, styling and basic treatments',
                    'category_type': 'service',
                    'color': '#FF6B6B',
                    'icon': 'fas fa-cut',
                    'sort_order': 1
                },
                {
                    'name': 'hair_colouring_treatments',
                    'display_name': 'Hair Colouring & Treatments',
                    'description': 'Hair coloring, highlights, lowlights and chemical treatments',
                    'category_type': 'service',
                    'color': '#FF8E53',
                    'icon': 'fas fa-palette',
                    'sort_order': 2
                },
                {
                    'name': 'hair_rituals',
                    'display_name': 'Hair Rituals',
                    'description': 'Specialized hair care rituals and therapeutic treatments',
                    'category_type': 'service',
                    'color': '#FF9FF3',
                    'icon': 'fas fa-leaf',
                    'sort_order': 3
                },
                {
                    'name': 'facials_skin_rituals',
                    'display_name': 'Facials & Skin Rituals',
                    'description': 'Facial treatments, skincare rituals and anti-aging services',
                    'category_type': 'service',
                    'color': '#4ECDC4',
                    'icon': 'fas fa-spa',
                    'sort_order': 4
                },
                {
                    'name': 'hands_feet_care',
                    'display_name': 'Hands & Feet Care',
                    'description': 'Manicures, pedicures, nail treatments and hand/foot care',
                    'category_type': 'service',
                    'color': '#45B7D1',
                    'icon': 'fas fa-hand-sparkles',
                    'sort_order': 5
                },
                {
                    'name': 'threading',
                    'display_name': 'Threading',
                    'description': 'Eyebrow threading, facial hair removal and shaping',
                    'category_type': 'service',
                    'color': '#96CEB4',
                    'icon': 'fas fa-eye',
                    'sort_order': 6
                },
                {
                    'name': 'waxing',
                    'display_name': 'Waxing',
                    'description': 'Body waxing, facial waxing and hair removal services',
                    'category_type': 'service',
                    'color': '#FFEAA7',
                    'icon': 'fas fa-user-times',
                    'sort_order': 7
                },
                {
                    'name': 'detan_treatments',
                    'display_name': 'De-Tan Treatments',
                    'description': 'Skin de-tanning, brightening and sun damage repair',
                    'category_type': 'service',
                    'color': '#FD79A8',
                    'icon': 'fas fa-sun',
                    'sort_order': 8
                },
                {
                    'name': 'bleach_treatments',
                    'display_name': 'Bleach Treatments',
                    'description': 'Facial bleaching, skin lightening and brightening treatments',
                    'category_type': 'service',
                    'color': '#FDCB6E',
                    'icon': 'fas fa-magic',
                    'sort_order': 9
                },
                {
                    'name': 'makeup_bridal_groom',
                    'display_name': 'Makeup, Bridal & Groom Services',
                    'description': 'Professional makeup, bridal packages and groom grooming',
                    'category_type': 'service',
                    'color': '#E17055',
                    'icon': 'fas fa-heart',
                    'sort_order': 10
                },
                {
                    'name': 'massages',
                    'display_name': 'Massages',
                    'description': 'Therapeutic massages, body relaxation and wellness treatments',
                    'category_type': 'service',
                    'color': '#A29BFE',
                    'icon': 'fas fa-hands',
                    'sort_order': 11
                },
                {
                    'name': 'body_scrubs_polishing',
                    'display_name': 'Body Scrubs & Polishing',
                    'description': 'Body exfoliation, scrubs and skin polishing treatments',
                    'category_type': 'service',
                    'color': '#6C5CE7',
                    'icon': 'fas fa-sparkles',
                    'sort_order': 12
                },
                {
                    'name': 'body_wraps',
                    'display_name': 'Body Wraps',
                    'description': 'Detoxifying body wraps, slimming treatments and body contouring',
                    'category_type': 'service',
                    'color': '#74B9FF',
                    'icon': 'fas fa-compress-alt',
                    'sort_order': 13
                },
                {
                    'name': 'signature_rituals',
                    'display_name': 'Signature Rituals',
                    'description': 'Exclusive spa signature treatments and luxury experiences',
                    'category_type': 'service',
                    'color': '#FD79A8',
                    'icon': 'fas fa-crown',
                    'sort_order': 14
                },
                {
                    'name': 'nail_affair',
                    'display_name': 'The Nail Affair (Nail Services)',
                    'description': 'Premium nail services, nail art, extensions and specialized nail care',
                    'category_type': 'service',
                    'color': '#E84393',
                    'icon': 'fas fa-gem',
                    'sort_order': 15
                }
            ]
            
            # Create categories
            created_categories = []
            updated_categories = []
            
            for cat_data in categories_data:
                existing_cat = Category.query.filter_by(name=cat_data['name'], category_type='service').first()
                if not existing_cat:
                    category = Category(**cat_data)
                    category.is_active = True
                    category.created_at = datetime.utcnow()
                    db.session.add(category)
                    db.session.flush()  # Get the ID
                    created_categories.append(cat_data['display_name'])
                    print(f"✅ Created category: {cat_data['display_name']}")
                else:
                    # Update existing category with new display name and description
                    existing_cat.display_name = cat_data['display_name']
                    existing_cat.description = cat_data['description']
                    existing_cat.color = cat_data['color']
                    existing_cat.icon = cat_data['icon']
                    existing_cat.sort_order = cat_data['sort_order']
                    updated_categories.append(cat_data['display_name'])
                    print(f"🔄 Updated category: {cat_data['display_name']}")
            
            db.session.commit()
            
            print(f"\n🎉 Successfully processed {len(categories_data)} spa service categories!")
            print(f"📊 Created: {len(created_categories)} new categories")
            print(f"🔄 Updated: {len(updated_categories)} existing categories")
            
            if created_categories:
                print(f"\n✨ New Categories Added:")
                for cat in created_categories:
                    print(f"   • {cat}")
            
            if updated_categories:
                print(f"\n🔄 Categories Updated:")
                for cat in updated_categories:
                    print(f"   • {cat}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding spa service categories: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = add_spa_service_categories()
    if success:
        print("\n🎊 All spa service categories have been successfully added to your system!")
        print("💡 You can now create services under these categories from the Services page.")
    else:
        print("\n💥 Failed to add categories. Please check the error messages above.")
