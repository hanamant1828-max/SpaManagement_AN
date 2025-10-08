
#!/usr/bin/env python3
"""
Fix paid appointments by changing payment_status back to pending
"""

from app import app, db
from models import UnakiBooking
from datetime import date

def fix_paid_appointments():
    """Change paid appointments to pending so they appear in Unaki view"""
    with app.app_context():
        today = date.today()
        
        # Find all paid appointments for today
        paid_appointments = UnakiBooking.query.filter_by(
            appointment_date=today,
            payment_status='paid'
        ).all()
        
        print(f"Found {len(paid_appointments)} paid appointments for {today}")
        
        if paid_appointments:
            for apt in paid_appointments:
                print(f"  - {apt.client_name} - {apt.service_name} ({apt.start_time} - {apt.end_time}) - Changing to pending")
                apt.payment_status = 'pending'
            
            db.session.commit()
            print(f"✅ Successfully updated {len(paid_appointments)} appointments to 'pending' status")
        else:
            print("No paid appointments found for today")

if __name__ == '__main__':
    fix_paid_appointments()
