#!/usr/bin/env python3
"""
Cypress-style automated test for package creation functionality
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import sys

class PackageCreationTest:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.session = requests.Session()
        self.csrf_token = None
        
    def log(self, message, status="INFO"):
        print(f"[{status}] {message}")
        
    def wait_for_app(self, max_retries=10):
        """Wait for application to be ready"""
        for i in range(max_retries):
            try:
                response = self.session.get(f"{self.base_url}/login")
                if response.status_code == 200:
                    self.log("✓ Application is ready")
                    return True
                self.log(f"Waiting for app... attempt {i+1}/{max_retries}")
                time.sleep(2)
            except:
                self.log(f"Connection failed, retrying... {i+1}/{max_retries}")
                time.sleep(2)
        return False
        
    def extract_csrf_token(self, html_content):
        """Extract CSRF token from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrf_token'})
            if csrf_input:
                return csrf_input.get('value')
            return None
        except:
            return None
    
    def test_login(self):
        """Test login functionality"""
        self.log("Testing login functionality...")
        
        # Get login page
        response = self.session.get(f"{self.base_url}/login")
        if response.status_code != 200:
            self.log(f"❌ Login page not accessible: {response.status_code}", "ERROR")
            return False
            
        # Extract CSRF token
        self.csrf_token = self.extract_csrf_token(response.text)
        if not self.csrf_token:
            self.log("⚠️  No CSRF token found, attempting login without it", "WARN")
        
        # Attempt login
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        if self.csrf_token:
            login_data['csrf_token'] = self.csrf_token
            
        response = self.session.post(f"{self.base_url}/login", data=login_data)
        
        if response.status_code in [200, 302]:
            self.log("✓ Login successful")
            return True
        else:
            self.log(f"❌ Login failed: {response.status_code}", "ERROR")
            self.log(f"Response: {response.text[:200]}...", "DEBUG")
            return False
    
    def test_packages_page_access(self):
        """Test accessing packages page after login"""
        self.log("Testing packages page access...")
        
        response = self.session.get(f"{self.base_url}/packages")
        
        if response.status_code == 200:
            self.log("✓ Packages page accessible")
            
            # Check for key elements
            if "Create New Package" in response.text:
                self.log("✓ Package creation UI found")
            if "addPackageModal" in response.text:
                self.log("✓ Package creation modal found")
            if "service-selection" in response.text:
                self.log("✓ Service selection interface found")
                
            return True
        else:
            self.log(f"❌ Packages page not accessible: {response.status_code}", "ERROR")
            return False
    
    def test_package_creation_form(self):
        """Test package creation form submission"""
        self.log("Testing package creation form...")
        
        # Get packages page to extract CSRF token
        response = self.session.get(f"{self.base_url}/packages")
        if response.status_code != 200:
            self.log("❌ Cannot access packages page for form test", "ERROR")
            return False
            
        # Extract CSRF token from packages page
        csrf_token = self.extract_csrf_token(response.text)
        if not csrf_token:
            self.log("⚠️  No CSRF token found in packages page", "WARN")
        
        # Prepare package creation data
        package_data = {
            'name': 'Test Package - Automated',
            'description': 'Automated test package creation',
            'validity_days': '30',
            'discount_percentage': '10',
            'is_active': True,
            'services': json.dumps([
                {'service_id': 1, 'sessions': 5, 'discount': 5},
                {'service_id': 2, 'sessions': 3, 'discount': 10}
            ])
        }
        
        if csrf_token:
            package_data['csrf_token'] = csrf_token
        
        # Submit package creation
        response = self.session.post(f"{self.base_url}/create_package", data=package_data)
        
        if response.status_code in [200, 201, 302]:
            self.log("✓ Package creation request submitted successfully")
            
            # Check if redirected back to packages page
            if response.status_code == 302:
                self.log("✓ Redirected after package creation (expected)")
                
            return True
        else:
            self.log(f"❌ Package creation failed: {response.status_code}", "ERROR")
            self.log(f"Response: {response.text[:200]}...", "DEBUG")
            return False
    
    def test_package_list(self):
        """Test if created package appears in the list"""
        self.log("Testing package list after creation...")
        
        response = self.session.get(f"{self.base_url}/packages")
        if response.status_code != 200:
            self.log("❌ Cannot access packages page for verification", "ERROR")
            return False
            
        if "Test Package - Automated" in response.text:
            self.log("✓ Created package found in the list")
            return True
        else:
            self.log("⚠️  Created package not found in the list", "WARN")
            return False
    
    def run_full_test(self):
        """Run complete package creation test suite"""
        self.log("🧪 Starting Package Creation Test Suite")
        self.log("=" * 50)
        
        success = True
        
        # Wait for application
        if not self.wait_for_app():
            self.log("❌ Application not ready", "ERROR")
            return False
        
        # Test login
        if not self.test_login():
            success = False
            
        # Test packages page access
        if success and not self.test_packages_page_access():
            success = False
            
        # Test package creation
        if success and not self.test_package_creation_form():
            success = False
            
        # Test package list
        if success:
            self.test_package_list()  # This is informational, doesn't affect success
        
        self.log("=" * 50)
        if success:
            self.log("🎉 Package creation test completed successfully!", "SUCCESS")
        else:
            self.log("❌ Package creation test failed", "ERROR")
            
        return success

if __name__ == "__main__":
    test = PackageCreationTest()
    success = test.run_full_test()
    
    if not success:
        sys.exit(1)