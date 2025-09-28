
"""
Add sample billing data to populate the revenue dashboard
"""

from app import app, db
from models import Customer, Service, EnhancedInvoice, InvoiceItem
from datetime import datetime, timedelta
import random

def create_sample_billing_data():
    """Create sample invoice data for revenue dashboard"""
    
    with app.app_context():
        print("Creating sample billing data...")
        
        # Get existing customers and services
        customers = Customer.query.limit(10).all()
        services = Service.query.limit(10).all()
        
        if not customers:
            print("No customers found. Please add customers first.")
            return
            
        if not services:
            print("No services found. Please add services first.")
            return
        
        # Create sample invoices for the last 30 days
        sample_invoices = []
        
        for i in range(20):  # Create 20 sample invoices
            # Random customer
            customer = random.choice(customers)
            
            # Random date in last 30 days
            days_ago = random.randint(0, 30)
            invoice_date = datetime.now() - timedelta(days=days_ago)
            
            # Random services (1-3 services per invoice)
            num_services = random.randint(1, 3)
            selected_services = random.sample(services, min(num_services, len(services)))
            
            # Calculate totals
            services_subtotal = sum(service.price for service in selected_services)
            tax_amount = services_subtotal * 0.18  # 18% tax
            total_amount = services_subtotal + tax_amount
            
            # Random payment status
            payment_statuses = ['paid', 'paid', 'paid', 'pending', 'partial']  # More paid than pending
            payment_status = random.choice(payment_statuses)
            
            if payment_status == 'paid':
                amount_paid = total_amount
                balance_due = 0
            elif payment_status == 'partial':
                amount_paid = total_amount * random.uniform(0.3, 0.7)
                balance_due = total_amount - amount_paid
            else:
                amount_paid = 0
                balance_due = total_amount
            
            # Create enhanced invoice
            invoice = EnhancedInvoice(
                invoice_number=f"INV-{invoice_date.strftime('%Y%m%d')}-{i+1:04d}",
                client_id=customer.id,
                invoice_date=invoice_date,
                services_subtotal=services_subtotal,
                inventory_subtotal=0,
                gross_subtotal=services_subtotal,
                net_subtotal=services_subtotal,
                tax_amount=tax_amount,
                discount_amount=0,
                tips_amount=0,
                total_amount=total_amount,
                amount_paid=amount_paid,
                balance_due=balance_due,
                payment_status=payment_status,
                cgst_rate=9.0,
                sgst_rate=9.0,
                igst_rate=0.0,
                cgst_amount=tax_amount / 2,
                sgst_amount=tax_amount / 2,
                igst_amount=0,
                is_interstate=False,
                additional_charges=0,
                payment_terms='immediate',
                notes='Sample invoice for demo purposes'
            )
            
            db.session.add(invoice)
            db.session.flush()  # Get invoice ID
            
            # Create invoice items
            for service in selected_services:
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    item_type='service',
                    item_id=service.id,
                    item_name=service.name,
                    description=service.description or service.name,
                    quantity=1,
                    unit_price=service.price,
                    original_amount=service.price,
                    final_amount=service.price
                )
                db.session.add(item)
            
            sample_invoices.append(invoice)
        
        # Commit all changes
        db.session.commit()
        
        # Calculate and display totals
        total_revenue = sum(inv.amount_paid for inv in sample_invoices)
        pending_amount = sum(inv.balance_due for inv in sample_invoices)
        today_invoices = [inv for inv in sample_invoices if inv.invoice_date.date() == datetime.now().date()]
        today_revenue = sum(inv.amount_paid for inv in today_invoices)
        
        print(f"✅ Created {len(sample_invoices)} sample invoices")
        print(f"💰 Total Revenue: ₹{total_revenue:,.2f}")
        print(f"⏳ Pending Amount: ₹{pending_amount:,.2f}")
        print(f"📅 Today's Revenue: ₹{today_revenue:,.2f}")
        print(f"📊 Today's Invoices: {len(today_invoices)}")

if __name__ == "__main__":
    create_sample_billing_data()
