
#!/usr/bin/env python3
"""
Create sample inventory adjustments for testing
"""
from app import app, db
from models import InventoryAdjustment, InventoryProduct, InventoryBatch, User
from datetime import datetime, date, timedelta
import random

def create_sample_adjustments():
    """Create sample inventory adjustments"""
    with app.app_context():
        print("🔧 Creating sample inventory adjustments...")
        
        # Get existing products and batches
        products = InventoryProduct.query.filter_by(is_active=True).all()
        batches = InventoryBatch.query.filter_by(status='active').all()
        
        if not products:
            print("❌ No products found. Please create products first.")
            return
        
        if not batches:
            print("❌ No batches found. Please create batches first.")
            return
        
        # Get admin user for created_by
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User.query.first()
        
        # Clear existing adjustments
        InventoryAdjustment.query.delete()
        db.session.commit()
        print("✅ Cleared existing adjustments")
        
        # Sample adjustment reasons
        increase_reasons = [
            'Stock correction - recount',
            'Supplier bonus',
            'Return from customer',
            'Found missing items',
            'Damaged items replaced'
        ]
        
        decrease_reasons = [
            'Damaged during handling',
            'Expired products',
            'Theft/Loss',
            'Quality issues',
            'Stock correction - recount'
        ]
        
        # Create adjustments for the last 30 days
        adjustments_created = 0
        today = date.today()
        
        for i in range(20):  # Create 20 sample adjustments
            # Random date in last 30 days
            days_ago = random.randint(0, 30)
            adjustment_date = today - timedelta(days=days_ago)
            
            # Random batch
            batch = random.choice(batches)
            product = batch.product
            
            # Random adjustment type
            adjustment_type = random.choice(['increase', 'decrease'])
            
            # Random quantity (1-10)
            quantity = random.randint(1, 10)
            
            # Select appropriate reason
            reason = random.choice(increase_reasons if adjustment_type == 'increase' else decrease_reasons)
            
            # Create adjustment
            adjustment = InventoryAdjustment(
                product_id=product.id,
                batch_id=batch.id,
                quantity=quantity,
                adjustment_type=adjustment_type,
                adjustment_date=adjustment_date,
                remarks=reason,
                reference_id=f'ADJ-{adjustment_date.strftime("%Y%m%d")}-{i+1:03d}',
                created_by=admin_user.id if admin_user else None,
                created_at=datetime.combine(adjustment_date, datetime.min.time())
            )
            
            db.session.add(adjustment)
            adjustments_created += 1
            
            print(f"  ✓ Created adjustment: {adjustment.reference_id} - {product.name} ({adjustment_type} {quantity})")
        
        db.session.commit()
        print(f"\n✅ Successfully created {adjustments_created} sample adjustments!")
        
        # Verify
        total_adjustments = InventoryAdjustment.query.count()
        print(f"📊 Total adjustments in database: {total_adjustments}")

if __name__ == "__main__":
    create_sample_adjustments()
