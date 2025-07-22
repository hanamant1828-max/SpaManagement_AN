#!/usr/bin/env python3
"""
Test the fixed package creation functionality
"""
import requests
import json
import re

def test_fixed_package_creation():
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print("🎯 Testing FIXED Package Creation")
    print("=" * 40)
    
    # Login process
    login_response = session.get(f"{base_url}/login")
    csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_response.text)
    csrf_token = csrf_match.group(1) if csrf_match else None
    
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrf_token': csrf_token
    }
    
    login_result = session.post(f"{base_url}/login", data=login_data)
    print(f"Login: {'✓ Success' if login_result.status_code in [200, 302] else '❌ Failed'}")
    
    # Get packages page for CSRF token
    packages_response = session.get(f"{base_url}/packages")
    csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', packages_response.text)
    new_csrf_token = csrf_match.group(1) if csrf_match else csrf_token
    
    # Test package creation with proper data
    package_data = {
        'name': 'Wellness Package - Fixed',
        'description': 'Complete wellness package with multiple services',
        'validity_days': '60',  # 2 months validity
        'total_price': '750.00',
        'discount_percentage': '15',
        'is_active': True,
        'selected_services': json.dumps([
            {'service_id': 1, 'sessions': 4, 'discount': 10},  # Facial Treatment
            {'service_id': 2, 'sessions': 2, 'discount': 15},  # Full Body Massage
            {'service_id': 3, 'sessions': 3, 'discount': 5}    # Hair Cut & Style
        ]),
        'csrf_token': new_csrf_token
    }
    
    print("Creating package with data:")
    print(f"  Name: {package_data['name']}")
    print(f"  Services: 3 services with multiple sessions")
    print(f"  Total Price: ₹{package_data['total_price']}")
    print(f"  Validity: {package_data['validity_days']} days")
    
    # Create package
    create_response = session.post(f"{base_url}/packages/create", data=package_data)
    print(f"\nCreation Status: {create_response.status_code}")
    
    if create_response.status_code == 200:
        # Check for success/error messages
        flash_matches = re.findall(r'alert-(\w+).*?>(.*?)</div>', create_response.text, re.DOTALL)
        for alert_type, message in flash_matches:
            clean_message = re.sub(r'<[^>]+>', '', message).strip()
            if clean_message:
                print(f"  {alert_type.upper()}: {clean_message}")
    elif create_response.status_code == 302:
        print("  ✓ Successfully redirected (package likely created)")
    
    # Verify package in database
    print("\nDatabase Verification:")
    from app import app, db
    from models import Package, PackageService
    
    with app.app_context():
        packages = Package.query.filter_by(name='Wellness Package - Fixed').all()
        if packages:
            package = packages[0]
            print(f"  ✓ Package found: {package.name}")
            print(f"    - ID: {package.id}")
            print(f"    - Duration: {package.duration_months} months")
            print(f"    - Validity: {package.validity_days} days")
            print(f"    - Total Sessions: {package.total_sessions}")
            print(f"    - Price: ₹{package.total_price}")
            print(f"    - Discount: {package.discount_percentage}%")
            print(f"    - Active: {package.is_active}")
            
            # Check package services
            services = PackageService.query.filter_by(package_id=package.id).all()
            print(f"    - Package Services: {len(services)}")
            
            for ps in services:
                print(f"      * Service {ps.service_id}: {ps.sessions_included} sessions, {ps.service_discount}% discount")
            
            return True
        else:
            print("  ❌ Package not found in database")
            return False

if __name__ == "__main__":
    success = test_fixed_package_creation()
    
    if success:
        print("\n🎉 PACKAGE CREATION FIXED!")
        print("The package insertion functionality is now working correctly.")
    else:
        print("\n❌ Package creation still has issues.")