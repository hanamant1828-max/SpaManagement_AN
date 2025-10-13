
"""
Fix corrupted face encodings in the database
This will remove face encodings that cannot be decoded properly
"""
from app import app, db
from models import Customer
import json

with app.app_context():
    print("🔍 Checking for corrupted face encodings...")
    
    customers_with_faces = Customer.query.filter(
        Customer.face_encoding.isnot(None)
    ).all()
    
    corrupted_count = 0
    fixed_count = 0
    
    for customer in customers_with_faces:
        try:
            # Try to decode as JSON
            if isinstance(customer.face_encoding, str):
                json.loads(customer.face_encoding)
                print(f"✅ Customer {customer.id} ({customer.full_name}): Valid JSON encoding")
            else:
                print(f"ℹ️ Customer {customer.id} ({customer.full_name}): Binary encoding (legacy)")
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"❌ Customer {customer.id} ({customer.full_name}): Corrupted encoding - {e}")
            print(f"   Removing corrupted face data...")
            customer.face_encoding = None
            customer.face_image_url = None
            corrupted_count += 1
            fixed_count += 1
    
    if fixed_count > 0:
        db.session.commit()
        print(f"\n✅ Fixed {fixed_count} corrupted face encodings")
    else:
        print(f"\n✅ No corrupted face encodings found")
    
    print(f"📊 Summary:")
    print(f"   - Total customers with faces: {len(customers_with_faces)}")
    print(f"   - Corrupted encodings removed: {corrupted_count}")
    print(f"\n💡 These customers will need to re-register their faces")
