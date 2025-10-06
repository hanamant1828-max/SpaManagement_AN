
#!/usr/bin/env python3
"""Check student offer prices in database"""

from app import app, db
from models import StudentOffer

def check_student_offers():
    with app.app_context():
        offers = StudentOffer.query.all()
        print(f"\n📊 Found {len(offers)} student offers:")
        print("-" * 80)
        
        for offer in offers:
            print(f"\nID: {offer.id}")
            print(f"Name: {offer.name}")
            print(f"Price: {offer.price}")
            print(f"Discount %: {offer.discount_percentage}")
            print(f"Active: {offer.is_active}")
            
            if offer.price is None or offer.price == 0:
                print("⚠️  WARNING: Price is missing or zero!")
            else:
                print(f"✅ Price is set: ₹{offer.price}")

if __name__ == '__main__':
    check_student_offers()
