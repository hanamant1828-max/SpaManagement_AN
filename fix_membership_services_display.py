"""
Fix membership services_included field for existing memberships
This script updates the services_included text field based on the linked services
"""
from app import app, db
from models import Membership, MembershipService, Service

def fix_membership_services():
    """Update services_included field for all memberships"""
    with app.app_context():
        memberships = Membership.query.all()
        updated_count = 0
        
        for membership in memberships:
            # Check if services_included is empty or null
            if not membership.services_included or membership.services_included.strip() == '':
                # Get linked services
                service_names = []
                for ms in membership.membership_services:
                    if ms.service:
                        service_names.append(ms.service.name)
                
                # Update the field if there are services
                if service_names:
                    membership.services_included = ', '.join(service_names)
                    updated_count += 1
                    print(f"Updated membership '{membership.name}' with services: {membership.services_included}")
        
        if updated_count > 0:
            db.session.commit()
            print(f"\n✅ Successfully updated {updated_count} memberships")
        else:
            print("\n✅ All memberships already have services_included populated")

if __name__ == '__main__':
    fix_membership_services()
