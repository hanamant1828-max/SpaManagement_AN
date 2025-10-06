
#!/usr/bin/env python3
"""
Fix student offers with zero prices
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import StudentOffer

def fix_student_offer_prices():
    """Fix student offers that have zero or null prices"""
    with app.app_context():
        # Get all student offers with zero or null prices
        offers = StudentOffer.query.filter(
            (StudentOffer.price == None) | (StudentOffer.price == 0)
        ).all()
        
        if not offers:
            print("✅ All student offers have valid prices")
            return
        
        print(f"Found {len(offers)} student offers with invalid prices\n")
        
        for offer in offers:
            print(f"Student Offer: {offer.name}")
            print(f"  Current price: {offer.price}")
            print(f"  Discount: {offer.discount_percentage}%")
            
            # Prompt for price
            while True:
                try:
                    new_price = input(f"  Enter new price for '{offer.name}': ").strip()
                    if not new_price:
                        print("  Skipping...")
                        break
                    
                    new_price = float(new_price)
                    if new_price < 0:
                        print("  Price must be 0 or greater")
                        continue
                    
                    offer.price = new_price
                    print(f"  ✅ Updated price to ₹{new_price}")
                    break
                except ValueError:
                    print("  Invalid number, try again")
            
            print()
        
        # Commit changes
        db.session.commit()
        print(f"\n✅ Updated {len(offers)} student offers")

if __name__ == '__main__':
    fix_student_offer_prices()
