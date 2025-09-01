
#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Inventory

def debug_inventory_for_dropdown():
    """Debug inventory items available for dropdown"""
    with app.app_context():
        print("=== DEBUGGING INVENTORY DROPDOWN ===")
        
        # Get all active inventory items
        items = Inventory.query.filter_by(is_active=True).all()
        print(f"\nTotal active inventory items: {len(items)}")
        
        if not items:
            print("❌ No inventory items found!")
            print("💡 Try running: python add_sample_inventory_items.py")
            return
        
        print("\n📦 Available Inventory Items:")
        print("-" * 60)
        
        for i, item in enumerate(items, 1):
            print(f"{i:2d}. {item.name}")
            print(f"     ID: {item.id}")
            print(f"     Stock: {item.current_stock} {getattr(item, 'base_unit', 'units')}")
            print(f"     Category: {getattr(item, 'category', 'N/A')}")
            print(f"     Service Item: {getattr(item, 'is_service_item', False)}")
            print(f"     Tracking Type: {getattr(item, 'tracking_type', 'piece_wise')}")
            print(f"     Active: {item.is_active}")
            print()
        
        # Check if items meet dropdown criteria
        trackable_items = [
            item for item in items 
            if getattr(item, 'is_service_item', True) and item.current_stock > 0
        ]
        
        print(f"📊 Items suitable for 'Open Item' dropdown: {len(trackable_items)}")
        for item in trackable_items:
            print(f"  ✓ {item.name} ({item.current_stock} {getattr(item, 'base_unit', 'units')})")
        
        if not trackable_items:
            print("❌ No items available for consumption tracking!")
            print("💡 This might be why the dropdown is empty.")

if __name__ == "__main__":
    debug_inventory_for_dropdown()
