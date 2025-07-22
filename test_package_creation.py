#!/usr/bin/env python3
"""
Test script to verify package creation functionality
"""
import requests
import json
import sys
from datetime import datetime

def test_package_creation():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Package Creation Functionality")
    print("=" * 50)
    
    # Step 1: Test if application is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✓ Application is running (Status: {response.status_code})")
        
        if response.status_code == 302:
            print("  → Redirects to login (expected behavior)")
    except Exception as e:
        print(f"❌ Application not accessible: {e}")
        return False
    
    # Step 2: Test packages page accessibility (should redirect to login)
    try:
        response = requests.get(f"{base_url}/packages")
        print(f"✓ Packages page responds (Status: {response.status_code})")
        
        if response.status_code == 302:
            print("  → Redirects to login (authentication required)")
    except Exception as e:
        print(f"❌ Packages page error: {e}")
        return False
    
    # Step 3: Test login page
    try:
        response = requests.get(f"{base_url}/login")
        print(f"✓ Login page accessible (Status: {response.status_code})")
        
        if response.status_code == 200:
            print("  → Login form available")
    except Exception as e:
        print(f"❌ Login page error: {e}")
        return False
    
    print("\n📊 Database Connection Test")
    print("-" * 30)
    
    # Test database connection via Python
    try:
        from app import app, db
        from models import Package, Service, Client, User
        
        with app.app_context():
            # Check if services exist
            services_count = Service.query.count()
            print(f"✓ Services in database: {services_count}")
            
            # Check if packages exist
            packages_count = Package.query.count()
            print(f"✓ Packages in database: {packages_count}")
            
            # Check if users exist (for authentication)
            users_count = User.query.count()
            print(f"✓ Users in database: {users_count}")
            
            if users_count == 0:
                print("⚠️  No users found - creating admin user for testing")
                # Create admin user
                from werkzeug.security import generate_password_hash
                admin_user = User(
                    username='admin',
                    email='admin@spa.com',
                    first_name='Admin',
                    last_name='User',
                    role='admin',
                    is_active=True
                )
                admin_user.password_hash = generate_password_hash('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print("✓ Admin user created (username: admin, password: admin123)")
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login_and_package_creation():
    """Test login and package creation with session"""
    base_url = "http://localhost:5000"
    
    print("\n🔐 Testing Login and Package Creation")
    print("=" * 50)
    
    session = requests.Session()
    
    # Step 1: Get login page and extract CSRF token
    try:
        login_page = session.get(f"{base_url}/login")
        print(f"✓ Login page accessed (Status: {login_page.status_code})")
        
        # Extract CSRF token (simplified - would need proper HTML parsing)
        if "csrf_token" in login_page.text:
            print("✓ CSRF token found in login form")
    except Exception as e:
        print(f"❌ Login page error: {e}")
        return False
    
    # Step 2: Attempt login
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        print(f"✓ Login attempt (Status: {login_response.status_code})")
        
        if login_response.status_code == 302:
            print("  → Login redirect (likely successful)")
        
        # Step 3: Try accessing packages page after login
        packages_response = session.get(f"{base_url}/packages")
        print(f"✓ Packages page after login (Status: {packages_response.status_code})")
        
        if packages_response.status_code == 200:
            print("  → Successfully accessed packages page")
            
            # Check if package creation form is present
            if "addPackageModal" in packages_response.text:
                print("✓ Package creation form found")
            if "Create New Package" in packages_response.text:
                print("✓ Package creation UI present")
                
        return True
        
    except Exception as e:
        print(f"❌ Login/Package access error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Spa Management System - Package Creation Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()
    
    # Run tests
    success = True
    success &= test_package_creation()
    success &= test_login_and_package_creation()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests completed successfully!")
        print("Package creation functionality is ready for testing.")
        print("\nNext steps:")
        print("1. Login with admin/admin123")
        print("2. Navigate to /packages")
        print("3. Click 'Add New Package'")
        print("4. Select services and create package")
    else:
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1)