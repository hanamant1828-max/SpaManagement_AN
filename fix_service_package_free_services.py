
#!/usr/bin/env python3
"""
Fix free_services field for existing service packages.
This script calculates free_services = total_services - pay_for
"""

from app import app, db
from models import ServicePackage

def fix_service_package_free_services():
    """Fix free_services for all service packages"""
    with app.app_context():
        packages = ServicePackage.query.all()
        
        updated_count = 0
        for package in packages:
            # Calculate free_services if it's 0 or None
            if package.free_services == 0 or package.free_services is None:
                calculated_free = max(package.total_services - package.pay_for, 0)
                
                if calculated_free > 0:
                    print(f"Fixing package '{package.name}':")
                    print(f"  Pay for: {package.pay_for}")
                    print(f"  Total services: {package.total_services}")
                    print(f"  Current free_services: {package.free_services}")
                    print(f"  New free_services: {calculated_free}")
                    
                    package.free_services = calculated_free
                    
                    # Recalculate benefit percentage
                    if package.pay_for > 0:
                        package.benefit_percent = (calculated_free / package.pay_for) * 100
                        print(f"  New benefit_percent: {package.benefit_percent:.2f}%")
                    
                    updated_count += 1
                    print()
        
        if updated_count > 0:
            db.session.commit()
            print(f"✅ Successfully updated {updated_count} service package(s)")
        else:
            print("ℹ️ No service packages needed updating")

if __name__ == '__main__':
    fix_service_package_free_services()
