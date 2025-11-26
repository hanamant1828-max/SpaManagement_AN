
```python
#!/usr/bin/env python3
"""
Fix Payment Audit Report - Add missing payment records for paid invoices
"""

from app import app, db
from models import EnhancedInvoice, InvoicePayment
from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')

with app.app_context():
    print("🔍 Checking for paid invoices without payment records...")
    
    # Find all paid invoices
    paid_invoices = EnhancedInvoice.query.filter_by(payment_status='paid').all()
    
    print(f"Found {len(paid_invoices)} paid invoices")
    
    fixed_count = 0
    for invoice in paid_invoices:
        # Check if payment record exists
        existing_payment = InvoicePayment.query.filter_by(invoice_id=invoice.id).first()
        
        if not existing_payment:
            print(f"\n❌ Invoice {invoice.invoice_number} is marked as paid but has no payment record!")
            print(f"   Customer: {invoice.customer.full_name if invoice.customer else 'Unknown'}")
            print(f"   Amount: ₹{invoice.total_amount}")
            print(f"   Invoice Date: {invoice.invoice_date}")
            print(f"   Payment Method: {invoice.payment_method or 'Not specified'}")
            
            # Create payment record
            payment_method = invoice.payment_method or 'cash'
            
            # Use invoice_date for payment_date (convert to naive datetime)
            if invoice.invoice_date:
                payment_date = invoice.invoice_date
                if hasattr(payment_date, 'tzinfo') and payment_date.tzinfo:
                    payment_date = payment_date.replace(tzinfo=None)
            else:
                payment_date = datetime.now(IST).replace(tzinfo=None)
            
            payment = InvoicePayment(
                invoice_id=invoice.id,
                payment_method=payment_method,
                amount=invoice.total_amount,
                payment_date=payment_date,
                processed_by=1,  # System user
                notes=f"Auto-created payment record for paid invoice {invoice.invoice_number}"
            )
            
            db.session.add(payment)
            fixed_count += 1
            
            print(f"   ✅ Created payment record: {payment_method} - ₹{invoice.total_amount} on {payment_date.strftime('%Y-%m-%d')}")
    
    if fixed_count > 0:
        db.session.commit()
        print(f"\n✅ Fixed {fixed_count} invoices with missing payment records")
    else:
        print("\n✅ All paid invoices have payment records")
    
    # Show summary of today's payments
    today = datetime.now(IST).date()
    today_payments = InvoicePayment.query.filter(
        db.func.date(InvoicePayment.payment_date) == today
    ).all()
    
    print(f"\n📊 Today's Payments ({today}):")
    print(f"   Total: {len(today_payments)} payments")
    if today_payments:
        total = sum(p.amount for p in today_payments)
        print(f"   Total Amount: ₹{total}")
        for p in today_payments:
            print(f"   - Invoice {p.invoice.invoice_number}: {p.payment_method} - ₹{p.amount}")
```
