
#!/usr/bin/env python3
"""
Billing System Validation and Testing Script
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_billing_system():
    """Test the billing system for common issues"""
    print("🧪 Testing Billing System...")
    
    try:
        from app import app, db
        from models import Customer, Service, EnhancedInvoice, InvoiceItem
        
        with app.app_context():
            print("✅ App context created successfully")
            
            # Test 1: Check if required models exist
            print("\n📋 Test 1: Model Validation")
            try:
                customers = Customer.query.count()
                services = Service.query.count()
                invoices = EnhancedInvoice.query.count()
                print(f"✅ Customers: {customers}")
                print(f"✅ Services: {services}")
                print(f"✅ Enhanced Invoices: {invoices}")
            except Exception as e:
                print(f"❌ Model validation failed: {e}")
                return False
            
            # Test 2: Check database schema
            print("\n🗄️ Test 2: Database Schema Check")
            try:
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                
                # Check if enhanced_invoice table exists
                if 'enhanced_invoice' in inspector.get_table_names():
                    columns = inspector.get_columns('enhanced_invoice')
                    column_names = [col['name'] for col in columns]
                    
                    required_columns = [
                        'cgst_rate', 'sgst_rate', 'igst_rate', 
                        'cgst_amount', 'sgst_amount', 'igst_amount',
                        'is_interstate', 'additional_charges'
                    ]
                    
                    missing_columns = [col for col in required_columns if col not in column_names]
                    
                    if missing_columns:
                        print(f"⚠️ Missing columns in enhanced_invoice: {missing_columns}")
                        print("💡 Run: python fix_billing_table.py to add missing columns")
                    else:
                        print("✅ All required columns present in enhanced_invoice table")
                else:
                    print("❌ enhanced_invoice table not found")
                    return False
                    
            except Exception as e:
                print(f"❌ Database schema check failed: {e}")
                return False
            
            # Test 3: Test invoice number generation
            print("\n🔢 Test 3: Invoice Number Generation")
            try:
                from datetime import datetime
                current_date = datetime.now()
                latest_invoice = EnhancedInvoice.query.order_by(EnhancedInvoice.id.desc()).first()
                
                if latest_invoice:
                    print(f"✅ Latest invoice: {latest_invoice.invoice_number}")
                else:
                    print("ℹ️ No invoices found in database")
                
                # Generate test invoice number
                invoice_sequence = 1
                if latest_invoice and latest_invoice.invoice_number.startswith(f"INV-{current_date.strftime('%Y%m%d')}"):
                    try:
                        last_sequence = int(latest_invoice.invoice_number.split('-')[-1])
                        invoice_sequence = last_sequence + 1
                    except (ValueError, IndexError):
                        invoice_sequence = 1
                
                test_invoice_number = f"INV-{current_date.strftime('%Y%m%d')}-{invoice_sequence:04d}"
                print(f"✅ Next invoice number would be: {test_invoice_number}")
                
            except Exception as e:
                print(f"❌ Invoice number generation test failed: {e}")
                return False
            
            # Test 4: Test billing routes
            print("\n🌐 Test 4: Billing Routes Test")
            try:
                with app.test_client() as client:
                    # Test main billing route
                    response = client.get('/integrated-billing')
                    if response.status_code == 200:
                        print("✅ Main billing route accessible")
                    elif response.status_code == 302:
                        print("⚠️ Billing route redirects (probably needs login)")
                    else:
                        print(f"❌ Billing route failed: {response.status_code}")
                        
            except Exception as e:
                print(f"❌ Billing routes test failed: {e}")
                return False
            
            print("\n🎉 Billing System Validation Complete!")
            return True
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        return False

if __name__ == "__main__":
    success = test_billing_system()
    sys.exit(0 if success else 1)
