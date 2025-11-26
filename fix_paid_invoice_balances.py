
"""
Fix balance_due for invoices that are marked as paid but have incorrect balance amounts
"""
from app import app, db
from models import EnhancedInvoice

def fix_paid_invoice_balances():
    """Update balance_due to 0 for all paid invoices"""
    
    with app.app_context():
        # Find all paid invoices with non-zero balance
        paid_invoices = EnhancedInvoice.query.filter(
            EnhancedInvoice.payment_status == 'paid',
            EnhancedInvoice.balance_due != 0
        ).all()
        
        print(f"Found {len(paid_invoices)} paid invoices with incorrect balance amounts")
        
        for invoice in paid_invoices:
            old_balance = invoice.balance_due
            old_paid = invoice.amount_paid
            
            # Fix the balance and amount_paid
            invoice.balance_due = 0.0
            invoice.amount_paid = invoice.total_amount
            
            print(f"Invoice {invoice.invoice_number}: "
                  f"Balance {old_balance} → 0.00, "
                  f"Paid {old_paid} → {invoice.total_amount}")
        
        # Commit all changes
        db.session.commit()
        print(f"✅ Fixed {len(paid_invoices)} invoices")
        
        # Verify the fix
        remaining_issues = EnhancedInvoice.query.filter(
            EnhancedInvoice.payment_status == 'paid',
            EnhancedInvoice.balance_due != 0
        ).count()
        
        if remaining_issues == 0:
            print("✅ All paid invoices now have zero balance")
        else:
            print(f"⚠️ Still {remaining_issues} invoices with issues")

if __name__ == '__main__':
    fix_paid_invoice_balances()
