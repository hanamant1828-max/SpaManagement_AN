
#!/usr/bin/env python3
"""
Test script to verify package-service matching in integrated billing system
"""

from app import app, db
from models import Customer, Service, ServicePackageAssignment
from datetime import datetime, timedelta

def test_package_service_matching():
    """Test that packages are correctly matched to services"""
    
    with app.app_context():
        print("\n" + "="*60)
        print("TESTING PACKAGE-SERVICE MATCHING IN BILLING SYSTEM")
        print("="*60 + "\n")
        
        # Find a customer with service packages
        customer = Customer.query.filter_by(first_name='Michael', last_name='Chen').first()
        
        if not customer:
            print("❌ Test customer 'Michael Chen' not found")
            return False
            
        print(f"✅ Testing with customer: {customer.full_name} (ID: {customer.id})")
        print()
        
        # Get their service package assignments
        assignments = ServicePackageAssignment.query.filter_by(
            customer_id=customer.id,
            package_type='service_package',
            status='active'
        ).all()
        
        if not assignments:
            print("❌ No active service package assignments found")
            return False
            
        print(f"📦 Found {len(assignments)} active service package(s):")
        print()
        
        all_tests_passed = True
        
        for assignment in assignments:
            print(f"Package Assignment ID: {assignment.id}")
            print(f"  Service ID: {assignment.service_id}")
            print(f"  Total Sessions: {assignment.total_sessions}")
            print(f"  Used Sessions: {assignment.used_sessions}")
            print(f"  Remaining Sessions: {assignment.remaining_sessions}")
            
            # Get the service details
            if assignment.service_id:
                service = Service.query.get(assignment.service_id)
                if service:
                    print(f"  ✅ Service Found: {service.name} (ID: {service.id}, Price: ₹{service.price})")
                    
                    # Test the matching logic
                    if assignment.service_id == service.id:
                        print(f"  ✅ SERVICE MATCHING TEST PASSED")
                        print(f"     - Package service_id ({assignment.service_id}) == Service id ({service.id})")
                    else:
                        print(f"  ❌ SERVICE MATCHING TEST FAILED")
                        print(f"     - Package service_id ({assignment.service_id}) != Service id ({service.id})")
                        all_tests_passed = False
                else:
                    print(f"  ❌ Service with ID {assignment.service_id} not found in database")
                    all_tests_passed = False
            else:
                print(f"  ⚠️ No service_id assigned to this package")
            
            print()
        
        # Test API endpoint response format
        print("-" * 60)
        print("TESTING API RESPONSE FORMAT")
        print("-" * 60)
        
        from modules.billing.integrated_billing_views import get_customer_packages
        from flask import Flask
        from flask.testing import FlaskClient
        
        with app.test_client() as client:
            # Simulate login
            with client.session_transaction() as sess:
                sess['_user_id'] = '1'  # Admin user
            
            response = client.get(f'/integrated-billing/customer-packages/{customer.id}')
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ API Response Status: 200 OK")
                print(f"   Packages returned: {len(data.get('packages', []))}")
                
                for pkg in data.get('packages', []):
                    if pkg.get('package_type') == 'service_package':
                        print(f"\n   Package: {pkg.get('name')}")
                        print(f"     - service_id: {pkg.get('service_id')} (type: {type(pkg.get('service_id')).__name__})")
                        print(f"     - service_name: {pkg.get('service_name')}")
                        print(f"     - remaining_count: {pkg.get('sessions', {}).get('remaining')}")
                        
                        if pkg.get('service_id') and pkg.get('service_name'):
                            print(f"     ✅ Both service_id and service_name present")
                        else:
                            print(f"     ❌ Missing service_id or service_name")
                            all_tests_passed = False
            else:
                print(f"❌ API Response Status: {response.status_code}")
                all_tests_passed = False
        
        print("\n" + "="*60)
        if all_tests_passed:
            print("✅ ALL TESTS PASSED - Package matching is working correctly")
        else:
            print("❌ SOME TESTS FAILED - Review the output above")
        print("="*60 + "\n")
        
        return all_tests_passed

if __name__ == '__main__':
    test_package_service_matching()
