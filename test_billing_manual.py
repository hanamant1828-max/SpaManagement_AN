
"""
Manual Billing System Test Script
Run this to test the billing functionality step by step
"""
from app import app, db
from models import Customer, Service, EnhancedInvoice, InvoiceItem
from datetime import datetime
import json

def test_billing_components():
    """Test all billing components manually"""
    with app.app_context():
        print("🧪 Starting Manual Billing System Test")
        print("=" * 50)
        
        # Test 1: Check if billing models exist
        print("\n1. Testing Database Models...")
        try:
            # Test Customer model
            customers = Customer.query.limit(5).all()
            print(f"✅ Found {len(customers)} customers in database")
            for customer in customers:
                print(f"   - {customer.full_name} ({customer.phone})")
            
            # Test Service model
            services = Service.query.limit(5).all()
            print(f"✅ Found {len(services)} services in database")
            for service in services:
                print(f"   - {service.name}: ₹{service.price}")
            
            # Test Invoice model
            invoices = EnhancedInvoice.query.limit(5).all()
            print(f"✅ Found {len(invoices)} existing invoices")
            
        except Exception as e:
            print(f"❌ Database model error: {e}")
            return False
        
        # Test 2: Check billing routes
        print("\n2. Testing Billing Routes...")
        try:
            with app.test_client() as client:
                # Test integrated billing page
                response = client.get('/integrated-billing')
                if response.status_code == 200:
                    print("✅ Integrated billing page loads successfully")
                else:
                    print(f"❌ Integrated billing page error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Route testing error: {e}")
        
        # Test 3: Create a test invoice
        print("\n3. Creating Test Invoice...")
        try:
            if customers and services:
                test_customer = customers[0]
                test_service = services[0]
                
                # Create test invoice
                invoice = EnhancedInvoice()
                invoice.invoice_number = f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                invoice.client_id = test_customer.id
                invoice.invoice_date = datetime.utcnow()
                invoice.services_subtotal = test_service.price
                invoice.inventory_subtotal = 0
                invoice.gross_subtotal = test_service.price
                invoice.net_subtotal = test_service.price
                invoice.tax_amount = test_service.price * 0.18
                invoice.discount_amount = 0
                invoice.tips_amount = 0
                invoice.total_amount = test_service.price * 1.18
                invoice.balance_due = test_service.price * 1.18
                invoice.payment_status = 'pending'
                
                db.session.add(invoice)
                db.session.flush()
                
                # Create invoice item
                item = InvoiceItem()
                item.invoice_id = invoice.id
                item.item_type = 'service'
                item.item_id = test_service.id
                item.item_name = test_service.name
                item.description = test_service.description
                item.quantity = 1
                item.unit_price = test_service.price
                item.original_amount = test_service.price
                item.final_amount = test_service.price
                
                db.session.add(item)
                db.session.commit()
                
                print(f"✅ Test invoice created: {invoice.invoice_number}")
                print(f"   - Customer: {test_customer.full_name}")
                print(f"   - Service: {test_service.name}")
                print(f"   - Total: ₹{invoice.total_amount:.2f}")
                
        except Exception as e:
            print(f"❌ Invoice creation error: {e}")
            db.session.rollback()
        
        print("\n" + "=" * 50)
        print("🎯 Manual Testing Instructions:")
        print("1. Open your browser and go to /integrated-billing")
        print("2. Select a customer from the dropdown")
        print("3. Add a service and set quantity")
        print("4. Click 'Generate Professional Invoice'")
        print("5. Check for any JavaScript console errors")
        print("6. Verify invoice creation and database updates")
        
        return True

def test_inventory_integration():
    """Test inventory integration with billing"""
    with app.app_context():
        print("\n🏪 Testing Inventory Integration...")
        try:
            from modules.inventory.models import InventoryProduct, InventoryBatch
            
            products = InventoryProduct.query.filter_by(is_active=True).limit(3).all()
            print(f"✅ Found {len(products)} active inventory products")
            
            for product in products:
                batches = InventoryBatch.query.filter_by(
                    product_id=product.id,
                    status='active'
                ).filter(InventoryBatch.qty_available > 0).all()
                print(f"   - {product.name}: {len(batches)} batches with stock")
                
        except ImportError:
            print("⚠️  Inventory models not available - inventory integration disabled")
        except Exception as e:
            print(f"❌ Inventory integration error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Billing Test")
    test_billing_components()
    test_inventory_integration()
    print("\n✨ Test completed! Check the output above for any issues.")
