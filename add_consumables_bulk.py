#!/usr/bin/env python3
"""
Bulk add consumable inventory items from Excel file
"""
import pandas as pd
from app import app, db
from models import Inventory, Category
import uuid
import re

def clean_sku(name):
    """Generate clean SKU from item name"""
    # Remove special characters and create clean SKU
    clean_name = re.sub(r'[^A-Za-z0-9\s]', '', name).strip()
    words = clean_name.split()[:3]  # Take first 3 words
    sku_base = ''.join(word[:3].upper() for word in words)
    return sku_base[:6] if sku_base else 'ITEM'

def is_consumable_item(description):
    """Determine if an item is consumable based on description"""
    consumable_keywords = [
        'wax', 'disposable', 'towel', 'cape', 'napkin', 'sheet', 'apron', 
        'panties', 'head band', 'cap', 'boxer', 'spatuala', 'gown', 'jacket',
        'gloves', 'tissue', 'roll', 'strips', 'buds', 'bleach', 'foil', 'cream'
    ]
    
    # Equipment/tools that are NOT consumable
    non_consumable_keywords = [
        'chair', 'trolley', 'steamer', 'stool', 'steriliser', 'iron', 'tong',
        'dryer', 'scissor', 'razor', 'crimper', 'trim', 'waver', 'brush',
        'clip', 'comb', 'dispenser', 'bowl', 'scale', 'massager', 'remover',
        'galvanic', 'mirror', 'nipper', 'pusher', 'trimmer', 'buffer', 'scrapper',
        'heater', 'rest', 'ikonic', 'kinley', 'maverick', 'kennedy', 'jax',
        'orion', 'ayumi', 'vibe', 'gleam', 'dynamite', 'diffuser', 'master',
        'pro', 'ccb', 'paddle', 'bungee', 'teasing', 'steel', 'asbah'
    ]
    
    description_lower = description.lower()
    
    # Check for non-consumable keywords first
    for keyword in non_consumable_keywords:
        if keyword in description_lower:
            return False
    
    # Check for consumable keywords
    for keyword in consumable_keywords:
        if keyword in description_lower:
            return True
    
    return False

def add_consumables_from_excel():
    """Add consumable items from Excel file to inventory"""
    
    # Read Excel file
    try:
        df = pd.read_excel('attached_assets/Unaki_consumables Inventory_1756726046303.xlsx')
        print(f"Loaded {len(df)} items from Excel file")
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return
    
    with app.app_context():
        # Create or get Consumables category
        consumables_category = Category.query.filter_by(
            name='consumables', 
            category_type='product'
        ).first()
        
        if not consumables_category:
            consumables_category = Category(
                name='consumables',
                display_name='Consumables',
                description='Items that are consumed during services',
                category_type='product',
                color='#28a745',
                icon='fas fa-recycle'
            )
            db.session.add(consumables_category)
            db.session.commit()
            print("Created 'Consumables' category")
        
        added_count = 0
        skipped_count = 0
        
        for index, row in df.iterrows():
            # Skip rows with NaN values in critical fields
            if pd.isna(row['Description']) or pd.isna(row['Qty']) or pd.isna(row['MRP']):
                skipped_count += 1
                continue
                
            description = str(row['Description']).strip()
            quantity = float(row['Qty'])
            mrp = float(row['MRP'])
            
            # Check if item is consumable
            if not is_consumable_item(description):
                print(f"Skipping non-consumable: {description}")
                skipped_count += 1
                continue
            
            # Check if item already exists
            existing_item = Inventory.query.filter_by(name=description).first()
            if existing_item:
                print(f"Item already exists: {description}")
                skipped_count += 1
                continue
            
            # Generate unique SKU
            sku_base = clean_sku(description)
            sku = f"{sku_base}-{str(uuid.uuid4())[:8].upper()}"
            
            # Ensure SKU is unique
            while Inventory.query.filter_by(sku=sku).first():
                sku = f"{sku_base}-{str(uuid.uuid4())[:8].upper()}"
            
            # Create inventory item
            inventory_item = Inventory(
                name=description,
                description=f"Consumable item - {description}",
                sku=sku,
                category_id=consumables_category.id,
                category='consumables',
                current_stock=quantity,
                min_stock_level=max(1, quantity * 0.1),  # 10% of current stock
                max_stock_level=quantity * 3,  # 3x current stock
                reorder_point=max(1, quantity * 0.2),  # 20% of current stock
                reorder_quantity=quantity,  # Same as initial quantity
                base_unit='pcs',
                selling_unit='pcs',
                conversion_factor=1.0,
                cost_price=mrp * 0.7,  # Assume 30% margin
                selling_price=mrp,
                markup_percentage=30.0,
                item_type='consumable',
                is_service_item=True,
                is_retail_item=True,
                tracking_type='piece_wise',
                enable_low_stock_alert=True,
                is_active=True
            )
            
            try:
                db.session.add(inventory_item)
                db.session.commit()
                print(f"Added: {description} (Qty: {quantity}, MRP: ₹{mrp})")
                added_count += 1
            except Exception as e:
                db.session.rollback()
                print(f"Error adding {description}: {e}")
                skipped_count += 1
        
        print(f"\n=== BULK ADDITION COMPLETE ===")
        print(f"Total items processed: {len(df)}")
        print(f"Items added: {added_count}")
        print(f"Items skipped: {skipped_count}")
        print(f"Consumables category ID: {consumables_category.id}")

if __name__ == '__main__':
    add_consumables_from_excel()