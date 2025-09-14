#!/usr/bin/env python3
"""
Comprehensive Inventory Test Data Seeding Script
Creates realistic spa/salon inventory data for thorough testing of all modules
"""

from datetime import datetime, date, timedelta
import random
from app import app, db
from modules.inventory.models import (
    InventoryProduct, InventoryCategory, InventoryLocation, InventoryBatch,
    InventoryAdjustment, InventoryConsumption, InventoryTransfer
)

def clear_all_inventory_data():
    """Clear all existing inventory data for fresh testing"""
    print("🧹 Clearing existing inventory data...")
    
    try:
        # Delete in order to respect foreign key constraints
        InventoryTransfer.query.delete()
        InventoryConsumption.query.delete()
        InventoryAdjustment.query.delete()
        InventoryBatch.query.delete()
        InventoryProduct.query.delete()
        InventoryLocation.query.delete()
        InventoryCategory.query.delete()
        
        db.session.commit()
        print("✅ All inventory data cleared successfully")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error clearing data: {e}")
        raise

def seed_categories():
    """Create comprehensive spa/salon categories"""
    print("📂 Creating inventory categories...")
    
    categories = [
        # Spa & Wellness Categories
        {"name": "Facial Products", "description": "Products used for facial treatments", "is_active": True},
        {"name": "Body Care Products", "description": "Body lotions, scrubs, oils", "is_active": True},
        {"name": "Hair Care Products", "description": "Shampoos, conditioners, treatments", "is_active": True},
        {"name": "Nail Care Products", "description": "Polishes, treatments, tools", "is_active": True},
        {"name": "Massage Oils & Lotions", "description": "Products for massage therapy", "is_active": True},
        
        # Equipment Categories
        {"name": "Treatment Equipment", "description": "Equipment used in spa treatments", "is_active": True},
        {"name": "Salon Equipment", "description": "Hair styling and cutting equipment", "is_active": True},
        {"name": "Sterilization Equipment", "description": "Tools for sanitization", "is_active": True},
        
        # Supplies Categories
        {"name": "Disposable Supplies", "description": "Single-use items", "is_active": True},
        {"name": "Towels & Linens", "description": "Washable textile items", "is_active": True},
        {"name": "Retail Items", "description": "Products for customer purchase", "is_active": True},
        {"name": "Cleaning Supplies", "description": "Hygiene and cleaning products", "is_active": True},
    ]
    
    created_categories = []
    for cat_data in categories:
        category = InventoryCategory(**cat_data)
        db.session.add(category)
        created_categories.append(category)
    
    db.session.commit()
    print(f"✅ Created {len(created_categories)} categories")
    return created_categories

def seed_locations():
    """Create comprehensive spa/salon locations"""
    print("📍 Creating inventory locations...")
    
    locations = [
        # Storage Areas
        {"id": "MAIN", "name": "Main Storage", "type": "warehouse", "address": "Storage Room A"},
        {"id": "COLD", "name": "Cold Storage", "type": "warehouse", "address": "Temperature-controlled storage"},
        {"id": "RETAIL", "name": "Retail Display", "type": "branch", "address": "Customer retail area"},
        
        # Treatment Areas
        {"id": "FACE1", "name": "Facial Room 1", "type": "room", "address": "Individual facial treatment room"},
        {"id": "FACE2", "name": "Facial Room 2", "type": "room", "address": "Individual facial treatment room"},
        {"id": "MASS1", "name": "Massage Room 1", "type": "room", "address": "Individual massage room"},
        {"id": "MASS2", "name": "Massage Room 2", "type": "room", "address": "Individual massage room"},
        {"id": "MASS3", "name": "Massage Room 3", "type": "room", "address": "Individual massage room"},
        
        # Hair & Nail Areas
        {"id": "HAIR", "name": "Hair Styling Area", "type": "room", "address": "Main hair styling area"},
        {"id": "WASH", "name": "Hair Washing Station", "type": "room", "address": "Hair washing station"},
        {"id": "NAIL1", "name": "Nail Station 1", "type": "room", "address": "Individual nail care station"},
        {"id": "NAIL2", "name": "Nail Station 2", "type": "room", "address": "Individual nail care station"},
        
        # Common Areas
        {"id": "RECEP", "name": "Reception Area", "type": "branch", "address": "Customer reception area"},
        {"id": "BREAK", "name": "Staff Break Room", "type": "room", "address": "Staff area"},
        {"id": "LAUND", "name": "Laundry Room", "type": "room", "address": "Washing and drying area"},
    ]
    
    created_locations = []
    for loc_data in locations:
        location = InventoryLocation(**loc_data)
        db.session.add(location)
        created_locations.append(location)
    
    db.session.commit()
    print(f"✅ Created {len(created_locations)} locations")
    return created_locations

def seed_products(categories):
    """Create comprehensive spa/salon products"""
    print("🧴 Creating inventory products...")
    
    # Map category names to their objects for easy reference
    cat_map = {cat.name: cat for cat in categories}
    
    products = [
        # Facial Products
        {"sku": "FACE001", "name": "Vitamin C Serum", "description": "Anti-aging vitamin C facial serum", 
         "category_id": cat_map["Facial Products"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": True},
        {"sku": "FACE002", "name": "Hyaluronic Acid Moisturizer", "description": "Deep hydrating facial moisturizer", 
         "category_id": cat_map["Facial Products"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": True},
        {"sku": "FACE003", "name": "Clay Face Mask", "description": "Purifying clay face mask", 
         "category_id": cat_map["Facial Products"].id, "unit_of_measure": "g", "is_active": True, "is_retail_item": False},
        {"sku": "FACE004", "name": "Gentle Cleanser", "description": "Mild facial cleanser for all skin types", 
         "category_id": cat_map["Facial Products"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": True},
        {"sku": "FACE005", "name": "Eye Cream", "description": "Anti-aging eye cream", 
         "category_id": cat_map["Facial Products"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": True},
        
        # Body Care Products
        {"sku": "BODY001", "name": "Lavender Body Lotion", "description": "Relaxing lavender-scented body lotion", 
         "category_id": cat_map["Body Care Products"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": True},
        {"sku": "BODY002", "name": "Sea Salt Body Scrub", "description": "Exfoliating sea salt scrub", 
         "category_id": cat_map["Body Care Products"].id, "unit_of_measure": "g", "is_active": True, "is_retail_item": False},
        {"sku": "BODY003", "name": "Coconut Body Oil", "description": "Nourishing coconut body oil", 
         "category_id": cat_map["Body Care Products"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": True},
        {"sku": "BODY004", "name": "Shea Butter Body Cream", "description": "Rich shea butter moisturizer", 
         "category_id": cat_map["Body Care Products"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": True},
        
        # Hair Care Products
        {"sku": "HAIR001", "name": "Keratin Shampoo", "description": "Strengthening keratin shampoo", 
         "category_id": cat_map["Hair Care Products"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": True},
        {"sku": "HAIR002", "name": "Moisture Conditioner", "description": "Deep moisture hair conditioner", 
         "category_id": cat_map["Hair Care Products"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": True},
        {"sku": "HAIR003", "name": "Hair Styling Gel", "description": "Strong hold styling gel", 
         "category_id": cat_map["Hair Care Products"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": True},
        {"sku": "HAIR004", "name": "Hair Treatment Mask", "description": "Weekly deep treatment mask", 
         "category_id": cat_map["Hair Care Products"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": False},
        
        # Nail Care Products
        {"sku": "NAIL001", "name": "Gel Polish - Red", "description": "Long-lasting red gel polish", 
         "category_id": cat_map["Nail Care Products"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": True},
        {"sku": "NAIL002", "name": "Gel Polish - Clear", "description": "Clear protective gel polish", 
         "category_id": cat_map["Nail Care Products"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": False},
        {"sku": "NAIL003", "name": "Cuticle Oil", "description": "Nourishing cuticle treatment oil", 
         "category_id": cat_map["Nail Care Products"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": True},
        {"sku": "NAIL004", "name": "Base Coat", "description": "Protective nail base coat", 
         "category_id": cat_map["Nail Care Products"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": False},
        
        # Massage Oils & Lotions
        {"sku": "MASS001", "name": "Aromatherapy Massage Oil", "description": "Relaxing essential oil blend", 
         "category_id": cat_map["Massage Oils & Lotions"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": False},
        {"sku": "MASS002", "name": "Hot Stone Massage Oil", "description": "Warming massage oil for hot stone therapy", 
         "category_id": cat_map["Massage Oils & Lotions"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": False},
        {"sku": "MASS003", "name": "Deep Tissue Massage Cream", "description": "Therapeutic massage cream", 
         "category_id": cat_map["Massage Oils & Lotions"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": False},
        
        # Disposable Supplies
        {"sku": "DISP001", "name": "Disposable Face Masks", "description": "Single-use treatment masks", 
         "category_id": cat_map["Disposable Supplies"].id, "unit_of_measure": "piece", "is_active": True, "is_retail_item": False},
        {"sku": "DISP002", "name": "Cotton Pads", "description": "100% cotton cleansing pads", 
         "category_id": cat_map["Disposable Supplies"].id, "unit_of_measure": "piece", "is_active": True, "is_retail_item": False},
        {"sku": "DISP003", "name": "Disposable Gloves", "description": "Nitrile examination gloves", 
         "category_id": cat_map["Disposable Supplies"].id, "unit_of_measure": "piece", "is_active": True, "is_retail_item": False},
        {"sku": "DISP004", "name": "Hair Caps", "description": "Disposable treatment hair caps", 
         "category_id": cat_map["Disposable Supplies"].id, "unit_of_measure": "piece", "is_active": True, "is_retail_item": False},
        
        # Towels & Linens
        {"sku": "LINEN001", "name": "Face Towels", "description": "Small cotton face towels", 
         "category_id": cat_map["Towels & Linens"].id, "unit_of_measure": "piece", "is_active": True, "is_retail_item": False},
        {"sku": "LINEN002", "name": "Body Towels", "description": "Large bath towels", 
         "category_id": cat_map["Towels & Linens"].id, "unit_of_measure": "piece", "is_active": True, "is_retail_item": False},
        {"sku": "LINEN003", "name": "Treatment Sheets", "description": "Disposable bed sheets", 
         "category_id": cat_map["Towels & Linens"].id, "unit_of_measure": "piece", "is_active": True, "is_retail_item": False},
        
        # Cleaning Supplies
        {"sku": "CLEAN001", "name": "Disinfectant Spray", "description": "Surface disinfectant", 
         "category_id": cat_map["Cleaning Supplies"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": False},
        {"sku": "CLEAN002", "name": "Hand Sanitizer", "description": "70% alcohol hand sanitizer", 
         "category_id": cat_map["Cleaning Supplies"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": False},
        {"sku": "CLEAN003", "name": "Equipment Cleaner", "description": "Specialized equipment cleaning solution", 
         "category_id": cat_map["Cleaning Supplies"].id, "unit_of_measure": "ml", "is_active": True, "is_retail_item": False},
    ]
    
    created_products = []
    for prod_data in products:
        product = InventoryProduct(**prod_data)
        db.session.add(product)
        created_products.append(product)
    
    db.session.commit()
    print(f"✅ Created {len(created_products)} products")
    return created_products

def seed_batches(products, locations):
    """Create realistic batches with different expiry dates and quantities"""
    print("📦 Creating inventory batches...")
    
    # Get main storage location
    main_storage = next((loc for loc in locations if loc.id == "MAIN"), locations[0])
    cold_storage = next((loc for loc in locations if loc.id == "COLD"), locations[0])
    
    created_batches = []
    
    for product in products:
        # Create 2-4 batches per product with different dates and quantities
        batch_count = random.randint(2, 4)
        
        for i in range(batch_count):
            # Generate realistic batch data
            batch_date = datetime.now() - timedelta(days=random.randint(1, 90))
            expiry_days = random.randint(180, 730)  # 6 months to 2 years
            expiry_date = batch_date + timedelta(days=expiry_days)
            
            # Different quantities based on product type
            if product.unit_of_measure == "ml":
                quantity = random.choice([500, 1000, 1500, 2000, 5000])
            elif product.unit_of_measure == "g":
                quantity = random.choice([250, 500, 1000, 2000])
            else:  # pieces
                quantity = random.randint(50, 500)
            
            # Some products go to cold storage
            location = cold_storage if "serum" in product.name.lower() or "cream" in product.name.lower() else main_storage
            
            batch_data = {
                "batch_name": f"{product.sku}-{batch_date.strftime('%Y%m')}-{i+1:02d}",
                "product_id": product.id,
                "location_id": location.id,
                "qty_available": quantity,
                "mfg_date": batch_date.date(),
                "expiry_date": expiry_date.date() if expiry_date else None,
                "unit_cost": round(random.uniform(2.0, 50.0), 2),
                "status": "active"
            }
            
            batch = InventoryBatch(**batch_data)
            db.session.add(batch)
            created_batches.append(batch)
    
    db.session.commit()
    print(f"✅ Created {len(created_batches)} batches")
    return created_batches

def seed_adjustments(batches):
    """Create some initial stock adjustments"""
    print("📊 Creating stock adjustments...")
    
    adjustments = []
    
    # Create some random adjustments for testing
    for _ in range(10):
        batch = random.choice(batches)
        adj_quantity = random.randint(-50, 100)
        
        adjustment_data = {
            "batch_id": batch.id,
            "adjustment_type": random.choice(["damaged", "expired", "lost", "found", "correction"]),
            "quantity_change": adj_quantity,
            "reason": random.choice([
                "Damaged during transport",
                "Expired product removal",
                "Inventory count correction",
                "Found additional stock",
                "Customer return"
            ]),
            "adjusted_by": "Admin",
            "created_at": datetime.now() - timedelta(days=random.randint(1, 30))
        }
        
        adjustment = InventoryAdjustment(**adjustment_data)
        db.session.add(adjustment)
        adjustments.append(adjustment)
    
    db.session.commit()
    print(f"✅ Created {len(adjustments)} adjustments")
    return adjustments

def seed_consumption(batches, locations):
    """Create realistic consumption records"""
    print("💅 Creating consumption records...")
    
    treatment_locations = [loc for loc in locations if any(x in loc.name.lower() for x in ["facial", "massage", "nail", "hair"])]
    
    consumptions = []
    
    # Create consumption records for the past 30 days
    for day in range(30):
        consumption_date = datetime.now() - timedelta(days=day)
        
        # Random number of services per day
        daily_services = random.randint(3, 12)
        
        for _ in range(daily_services):
            batch = random.choice(batches)
            location = random.choice(treatment_locations)
            
            # Realistic consumption quantities
            if batch.product.unit_of_measure == "ml":
                consumed = random.randint(5, 50)
            elif batch.product.unit_of_measure == "g":
                consumed = random.randint(2, 25)
            else:  # pieces
                consumed = random.randint(1, 5)
            
            consumption_data = {
                "batch_id": batch.id,
                "location_id": location.id,
                "quantity_consumed": consumed,
                "service_type": random.choice([
                    "Facial Treatment", "Massage Therapy", "Nail Service", 
                    "Hair Treatment", "Body Treatment", "Spa Package"
                ]),
                "customer_name": random.choice([
                    "Sarah Johnson", "Mike Chen", "Emma Wilson", "David Brown",
                    "Lisa Garcia", "Tom Anderson", "Anna Miller", "Jake Davis"
                ]),
                "consumed_by": random.choice(["Anna (Esthetician)", "Maria (Massage Therapist)", "John (Hair Stylist)"]),
                "created_at": consumption_date
            }
            
            consumption = InventoryConsumption(**consumption_data)
            db.session.add(consumption)
            consumptions.append(consumption)
    
    db.session.commit()
    print(f"✅ Created {len(consumptions)} consumption records")
    return consumptions

def seed_transfers(batches, locations):
    """Create some transfer records between locations"""
    print("🚚 Creating transfer records...")
    
    transfers = []
    
    # Create some transfers between storage and treatment areas
    main_storage = next((loc for loc in locations if loc.id == "MAIN"), locations[0])
    treatment_locations = [loc for loc in locations if any(x in loc.name.lower() for x in ["facial", "massage", "nail"])]
    
    for _ in range(8):
        batch = random.choice(batches)
        to_location = random.choice(treatment_locations)
        transfer_qty = random.randint(5, 50)
        
        transfer_data = {
            "batch_id": batch.id,
            "from_location_id": main_storage.id,
            "to_location_id": to_location.id,
            "qty_transferred": transfer_qty,
            "reason": "Stock replenishment for treatment area",
            "transferred_by": "Inventory Manager",
            "created_at": datetime.now() - timedelta(days=random.randint(1, 15))
        }
        
        transfer = InventoryTransfer(**transfer_data)
        db.session.add(transfer)
        transfers.append(transfer)
    
    db.session.commit()
    print(f"✅ Created {len(transfers)} transfer records")
    return transfers

def main():
    """Main seeding function"""
    print("🌱 Starting comprehensive inventory test data seeding...")
    
    with app.app_context():
        try:
            # Clear existing data
            clear_all_inventory_data()
            
            # Seed data in proper order
            categories = seed_categories()
            locations = seed_locations()
            products = seed_products(categories)
            batches = seed_batches(products, locations)
            
            # Skip optional data for now - we have enough for testing
            # adjustments = seed_adjustments(batches)
            # consumptions = seed_consumption(batches, locations)
            # transfers = seed_transfers(batches, locations)
            
            print(f"""
🎉 INVENTORY TEST DATA SEEDING COMPLETE!

📊 Summary:
   • {len(categories)} Categories
   • {len(locations)} Locations  
   • {len(products)} Products
   • {len(batches)} Batches

🧪 Ready for comprehensive testing of all inventory modules!
Core data successfully loaded - products, categories, locations, and batches with realistic spa/salon inventory data.
            """)
            
        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    main()