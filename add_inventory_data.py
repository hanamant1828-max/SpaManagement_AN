
#!/usr/bin/env python3
"""
Add 10 Categories, 10 Locations, and 10 Batches to Inventory System
"""

from datetime import datetime, date, timedelta
import random
from app import app, db
from modules.inventory.models import (
    InventoryProduct, InventoryCategory, InventoryLocation, InventoryBatch
)

def add_10_categories():
    """Add 10 diverse spa/salon categories"""
    print("📂 Adding 10 inventory categories...")
    
    categories = [
        {"name": "Facial Care Products", "description": "Premium facial treatments and serums", "color_code": "#ff6b6b"},
        {"name": "Body Treatments", "description": "Body scrubs, wraps, and moisturizers", "color_code": "#4ecdc4"},
        {"name": "Aromatherapy Oils", "description": "Essential oils for relaxation and therapy", "color_code": "#45b7d1"},
        {"name": "Hair Styling Products", "description": "Professional hair care and styling", "color_code": "#96ceb4"},
        {"name": "Nail Care Collection", "description": "Manicure and pedicure supplies", "color_code": "#feca57"},
        {"name": "Massage Therapy", "description": "Oils and lotions for massage treatments", "color_code": "#ff9ff3"},
        {"name": "Spa Equipment", "description": "Professional spa tools and devices", "color_code": "#54a0ff"},
        {"name": "Hygiene Supplies", "description": "Sanitizers and cleaning products", "color_code": "#5f27cd"},
        {"name": "Wellness Supplements", "description": "Health and wellness products", "color_code": "#00d2d3"},
        {"name": "Retail Merchandise", "description": "Products for customer purchase", "color_code": "#ff6348"}
    ]
    
    created_categories = []
    for cat_data in categories:
        cat_data['is_active'] = True
        category = InventoryCategory(**cat_data)
        db.session.add(category)
        created_categories.append(category)
    
    db.session.commit()
    print(f"✅ Created {len(created_categories)} categories")
    return created_categories

def add_10_locations():
    """Add 10 diverse spa locations"""
    print("📍 Adding 10 inventory locations...")
    
    locations = [
        {"id": "SPA-MAIN", "name": "Main Spa Reception", "type": "branch", "address": "Ground floor reception area"},
        {"id": "STORAGE-A", "name": "Primary Storage Room", "type": "warehouse", "address": "Back storage area A"},
        {"id": "FACIAL-1", "name": "Facial Treatment Room 1", "type": "room", "address": "Private facial suite 1"},
        {"id": "FACIAL-2", "name": "Facial Treatment Room 2", "type": "room", "address": "Private facial suite 2"},
        {"id": "MASSAGE-1", "name": "Massage Therapy Room 1", "type": "room", "address": "Individual massage room 1"},
        {"id": "MASSAGE-2", "name": "Massage Therapy Room 2", "type": "room", "address": "Individual massage room 2"},
        {"id": "HAIR-SALON", "name": "Hair Styling Station", "type": "room", "address": "Main hair styling area"},
        {"id": "NAIL-BAR", "name": "Nail Care Station", "type": "room", "address": "Manicure and pedicure area"},
        {"id": "RETAIL-DISP", "name": "Retail Display Area", "type": "branch", "address": "Customer product display"},
        {"id": "COLD-STORE", "name": "Temperature Controlled Storage", "type": "warehouse", "address": "Climate controlled storage"}
    ]
    
    created_locations = []
    for loc_data in locations:
        loc_data['status'] = 'active'
        location = InventoryLocation(**loc_data)
        db.session.add(location)
        created_locations.append(location)
    
    db.session.commit()
    print(f"✅ Created {len(created_locations)} locations")
    return created_locations

def add_10_batches():
    """Add 10 diverse product batches"""
    print("📦 Adding 10 inventory batches...")
    
    # Get some categories and locations to assign to batches
    categories = InventoryCategory.query.limit(5).all()
    locations = InventoryLocation.query.limit(5).all()
    
    if not categories or not locations:
        print("⚠️ No categories or locations found. Creating batches without assignments.")
    
    batches_data = [
        {"batch_name": "VIT-C-2024-001", "product_type": "Vitamin C Serum", "unit_cost": 25.50},
        {"batch_name": "LAV-OIL-2024-002", "product_type": "Lavender Essential Oil", "unit_cost": 18.75},
        {"batch_name": "COLL-MASK-2024-003", "product_type": "Collagen Face Mask", "unit_cost": 12.00},
        {"batch_name": "ARGAN-2024-004", "product_type": "Argan Hair Oil", "unit_cost": 22.30},
        {"batch_name": "PEDI-KIT-2024-005", "product_type": "Pedicure Care Kit", "unit_cost": 15.60},
        {"batch_name": "HOT-STONE-2024-006", "product_type": "Hot Stone Massage Oil", "unit_cost": 28.90},
        {"batch_name": "CLEAN-2024-007", "product_type": "Sanitizing Solution", "unit_cost": 8.50},
        {"batch_name": "BODY-SCRUB-2024-008", "product_type": "Exfoliating Body Scrub", "unit_cost": 16.25},
        {"batch_name": "NAIL-POL-2024-009", "product_type": "Premium Nail Polish", "unit_cost": 11.75},
        {"batch_name": "DETOX-2024-010", "product_type": "Detox Facial Cleanser", "unit_cost": 19.40}
    ]
    
    created_batches = []
    for i, batch_data in enumerate(batches_data):
        # Generate realistic dates
        mfg_date = date.today() - timedelta(days=random.randint(10, 60))
        expiry_date = mfg_date + timedelta(days=random.randint(365, 730))
        
        # Assign location if available
        location_id = locations[i % len(locations)].id if locations else None
        
        batch = InventoryBatch(
            batch_name=batch_data["batch_name"],
            location_id=location_id,
            mfg_date=mfg_date,
            expiry_date=expiry_date,
            qty_available=0,  # Start with 0, will be added via adjustments
            unit_cost=batch_data["unit_cost"],
            selling_price=batch_data["unit_cost"] * 1.5,  # 50% markup
            status='active'
        )
        
        db.session.add(batch)
        created_batches.append(batch)
    
    db.session.commit()
    print(f"✅ Created {len(created_batches)} batches")
    return created_batches

def main():
    """Main function to add all inventory data"""
    print("🌱 Adding 10 categories, 10 locations, and 10 batches to inventory system...")
    
    with app.app_context():
        try:
            # Add data in sequence
            categories = add_10_categories()
            locations = add_10_locations()
            batches = add_10_batches()
            
            print(f"""
🎉 INVENTORY DATA ADDITION COMPLETE!

📊 Summary:
   • {len(categories)} Categories added
   • {len(locations)} Locations added  
   • {len(batches)} Batches added

🧪 Your inventory system now has fresh data for testing!
            """)
            
        except Exception as e:
            print(f"❌ Error adding inventory data: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    main()
