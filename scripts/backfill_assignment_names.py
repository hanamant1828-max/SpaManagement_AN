import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import ServicePackageAssignment
from modules.packages.name_resolver import resolve_package_display_name, resolve_service_name

def main():
    with app.app_context():
        print("Backfilling assignment names...")
        
        q = (ServicePackageAssignment.query
             .filter((ServicePackageAssignment.package_name.is_(None)) | 
                     (ServicePackageAssignment.package_name == "")))
        
        count = 0
        for a in q.all():
            a.package_name = resolve_package_display_name(a.package_type, a.package_reference_id)
            
            # For service packages, also set service_name if available
            if a.package_type in ("service", "service_package") and a.service_id:
                service_name = resolve_service_name(a.service_id)
                if service_name:
                    a.service_name = service_name
            
            count += 1
        
        db.session.commit()
        print(f"✅ Backfilled {count} assignments with package_name.")

if __name__ == "__main__":
    main()
