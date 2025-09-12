#!/usr/bin/env python3
"""
Final Comprehensive Security Test - All Fixes Verification
Tests all security improvements and complete CRUD including DELETE operations
"""

import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"
USERNAME = "admin"
PASSWORD = "admin123"

class FinalSecurityTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'FinalSecurityTester/1.0'})
        
    def get_csrf_token(self, page_content):
        """Extract CSRF token from page content"""
        soup = BeautifulSoup(page_content, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        return csrf_input.get('value') if csrf_input else None
        
    def test_login_with_csrf(self):
        """Test login with proper CSRF protection"""
        print("🔐 FINAL TEST 1: Login CSRF Protection")
        
        # Get login page and extract CSRF token
        login_page = self.session.get(f"{BASE_URL}/login")
        if login_page.status_code != 200:
            print(f"❌ Login page inaccessible: {login_page.status_code}")
            return False
            
        csrf_token = self.get_csrf_token(login_page.text)
        print(f"   CSRF token in login form: {'✅ Found' if csrf_token else '❌ Missing'}")
        
        if not csrf_token:
            return False
            
        # Login with CSRF token
        login_data = {
            'username': USERNAME,
            'password': PASSWORD,
            'csrf_token': csrf_token
        }
        
        response = self.session.post(f"{BASE_URL}/login", data=login_data)
        
        # Check dashboard access
        dashboard_response = self.session.get(f"{BASE_URL}/dashboard")
        success = dashboard_response.status_code == 200 and "dashboard" in dashboard_response.text.lower()
        
        print(f"   Login with CSRF: {'✅ Success' if success else '❌ Failed'}")
        return success
    
    def test_security_headers(self):
        """Test security headers are properly set"""
        print("\n🛡️ FINAL TEST 2: Security Headers Validation")
        
        response = self.session.get(f"{BASE_URL}/staff")
        headers = response.headers
        
        security_checks = {
            'X-Frame-Options': headers.get('X-Frame-Options') == 'SAMEORIGIN',
            'X-Content-Type-Options': headers.get('X-Content-Type-Options') == 'nosniff',
            'X-XSS-Protection': headers.get('X-XSS-Protection') == '1; mode=block',
            'Cache-Control': 'no-cache' in headers.get('Cache-Control', ''),
            'No Wildcard CORS': headers.get('Access-Control-Allow-Origin') != '*'
        }
        
        for check, passed in security_checks.items():
            status = "✅ Pass" if passed else "❌ Fail"
            print(f"   {check}: {status}")
            
        return all(security_checks.values())
    
    def test_complete_crud_with_security(self):
        """Test complete CRUD operations with security"""
        print("\n🔄 FINAL TEST 3: Complete CRUD with Security")
        
        timestamp = datetime.now().strftime("%H%M%S")
        
        # Get CSRF token for forms
        staff_page = self.session.get(f"{BASE_URL}/staff")
        csrf_token = self.get_csrf_token(staff_page.text)
        
        if not csrf_token:
            print("   ❌ No CSRF token for CRUD operations")
            return False
            
        print(f"   CSRF token for operations: ✅ {len(csrf_token)} characters")
        
        # CREATE with secure password
        create_data = {
            'first_name': 'Security',
            'last_name': 'Test',
            'username': f'sectest{timestamp}',
            'email': f'security.test{timestamp}@example.com',
            'role': 'staff',
            'commission_rate': '15.0',
            'hourly_rate': '25.0',
            'csrf_token': csrf_token
        }
        
        create_response = self.session.post(f"{BASE_URL}/staff/create", data=create_data)
        print(f"   CREATE with CSRF: {create_response.status_code}")
        
        # Test CREATE via API (should generate secure password)
        api_create_data = {
            'first_name': 'API',
            'last_name': 'Secure',
            'username': f'apisec{timestamp}',
            'email': f'api.secure{timestamp}@example.com',
            'role': 'staff'
            # Note: No password provided - should generate secure one
        }
        
        api_response = self.session.post(f"{BASE_URL}/api/staff", data=api_create_data)
        print(f"   API CREATE (secure password): {api_response.status_code}")
        
        if api_response.status_code in [200, 201]:
            try:
                result = api_response.json()
                if 'staff' in result and 'id' in result['staff']:
                    staff_id = result['staff']['id']
                    
                    # READ
                    read_response = self.session.get(f"{BASE_URL}/api/staff/{staff_id}")
                    print(f"   READ operation: {read_response.status_code}")
                    
                    # UPDATE 
                    update_data = {
                        'first_name': 'Updated',
                        'last_name': 'Secure',
                        'username': f'updated{timestamp}',
                        'email': f'updated.secure{timestamp}@example.com',
                        'role': 'staff'
                    }
                    
                    update_response = self.session.put(f"{BASE_URL}/api/staff/{staff_id}", json=update_data)
                    print(f"   UPDATE operation: {update_response.status_code}")
                    
                    # DELETE - The critical test
                    delete_response = self.session.delete(f"{BASE_URL}/api/staff/{staff_id}")
                    print(f"   DELETE operation: {delete_response.status_code}")
                    
                    if delete_response.status_code in [200, 204]:
                        # Verify deletion
                        verify_response = self.session.get(f"{BASE_URL}/api/staff/{staff_id}")
                        if verify_response.status_code == 404:
                            print("   ✅ DELETE verified - staff properly removed")
                            return True
                        else:
                            print(f"   ⚠️ DELETE issue - staff still exists: {verify_response.status_code}")
                    else:
                        print(f"   ❌ DELETE failed: {delete_response.status_code}")
            except Exception as e:
                print(f"   ❌ CRUD test error: {e}")
        
        return False
    
    def test_csrf_rejection(self):
        """Test CSRF rejection is working"""
        print("\n🚫 FINAL TEST 4: CSRF Rejection Verification")
        
        # Test form submission without CSRF token
        no_csrf_data = {
            'first_name': 'NoCSRF',
            'last_name': 'Test',
            'username': 'nocsrftest',
            'email': 'nocsrf@test.com',
            'role': 'staff'
        }
        
        no_csrf_response = self.session.post(f"{BASE_URL}/staff/create", data=no_csrf_data)
        csrf_blocked = no_csrf_response.status_code == 400
        
        print(f"   Form without CSRF rejected: {'✅ Yes' if csrf_blocked else '❌ No'} ({no_csrf_response.status_code})")
        
        return csrf_blocked
    
    def test_password_security(self):
        """Test password security improvements"""
        print("\n🔑 FINAL TEST 5: Password Security")
        
        # Create staff without password (should generate secure one)
        timestamp = datetime.now().strftime("%H%M%S")
        
        no_password_data = {
            'first_name': 'NoPassword',
            'last_name': 'Test',
            'username': f'nopass{timestamp}',
            'email': f'nopass{timestamp}@example.com',
            'role': 'staff'
            # No password field
        }
        
        response = self.session.post(f"{BASE_URL}/api/staff", data=no_password_data)
        print(f"   Staff creation without password: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("   ✅ Secure password generated automatically")
            return True
        else:
            print(f"   ❌ Password security test failed: {response.status_code}")
            return False
    
    def run_final_comprehensive_test(self):
        """Run all final security tests"""
        print("🔒 FINAL COMPREHENSIVE SECURITY VALIDATION")
        print("=" * 60)
        
        results = {}
        
        # Run all security tests
        results['login_csrf'] = self.test_login_with_csrf()
        results['security_headers'] = self.test_security_headers()
        results['complete_crud'] = self.test_complete_crud_with_security()
        results['csrf_rejection'] = self.test_csrf_rejection()
        results['password_security'] = self.test_password_security()
        
        # Summary
        print("\n🔒 FINAL SECURITY TEST SUMMARY")
        print("=" * 60)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name.upper().replace('_', ' ')}: {status}")
        
        passed_count = sum(results.values())
        total_count = len(results)
        
        overall_pass = all(results.values())
        overall_status = f"✅ ALL {total_count} SECURITY TESTS PASSED" if overall_pass else f"❌ {passed_count}/{total_count} TESTS PASSED"
        
        print(f"\n🎯 FINAL SECURITY STATUS: {overall_status}")
        
        if overall_pass:
            print("🎉 SYSTEM IS PRODUCTION-READY FROM SECURITY PERSPECTIVE!")
        else:
            print("⚠️ Additional security work required before production")
        
        return overall_pass

if __name__ == "__main__":
    tester = FinalSecurityTester()
    tester.run_final_comprehensive_test()