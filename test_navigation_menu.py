
#!/usr/bin/env python3
"""
Comprehensive Navigation Menu Test Script
Tests all menu items in the spa management system
"""

import requests
import time
from urllib.parse import urljoin
import sys

# Base URL of the application
BASE_URL = "http://0.0.0.0:5000"

# All menu items from the sidebar navigation
MENU_ITEMS = [
    # Main Navigation
    {"name": "Dashboard", "url": "/dashboard", "icon": "fas fa-tachometer-alt"},
    {"name": "Smart Booking & Calendar", "url": "/bookings", "icon": "fas fa-calendar-alt"},
    {"name": "Staff Availability", "url": "/staff_availability", "icon": "fas fa-users-cog"},
    {"name": "Manage Appointments", "url": "/appointments_management", "icon": "fas fa-calendar-check"},
    {"name": "Client History & Loyalty", "url": "/customers", "icon": "fas fa-users"},
    {"name": "Staff Management", "url": "/comprehensive_staff", "icon": "fas fa-users"},
    {"name": "Check-In", "url": "/checkin", "icon": "fas fa-user-check"},
    {"name": "WhatsApp Notifications", "url": "/notifications", "icon": "fas fa-bell"},
    {"name": "Billing System", "url": "/integrated_billing", "icon": "fas fa-cash-register"},
    {"name": "Services Management", "url": "/services", "icon": "fas fa-spa"},
    {"name": "Package Management", "url": "/packages", "icon": "fas fa-gift"},
    {"name": "Reports & Insights", "url": "/reports", "icon": "fas fa-chart-bar"},
    {"name": "Daily Expense Tracker", "url": "/expenses", "icon": "fas fa-receipt"},
    {"name": "Inventory Management", "url": "/inventory_dashboard", "icon": "fas fa-boxes"},
    {"name": "Expiring Product Alerts", "url": "/alerts", "icon": "fas fa-exclamation-triangle"},
    
    # System Management
    {"name": "System Management", "url": "/system_management", "icon": "fas fa-server"},
    {"name": "Role Management", "url": "/role_management", "icon": "fas fa-users-cog"},
    {"name": "User & Access Control", "url": "/settings", "icon": "fas fa-user-cog"},
]

class MenuNavigationTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        self.login_successful = False
        
    def login(self):
        """Login to the system"""
        try:
            # First get the login page to check if it's accessible
            login_url = urljoin(BASE_URL, "/login")
            response = self.session.get(login_url)
            
            if response.status_code == 200:
                print("✅ Login page accessible")
                
                # Attempt to login
                login_data = {
                    'username': 'admin',
                    'password': 'admin123'
                }
                
                response = self.session.post(login_url, data=login_data, allow_redirects=True)
                
                if response.status_code == 200 and 'dashboard' in response.url.lower():
                    print("✅ Login successful - redirected to dashboard")
                    self.login_successful = True
                    return True
                else:
                    print(f"❌ Login failed - Status: {response.status_code}, URL: {response.url}")
                    return False
                    
            else:
                print(f"❌ Login page not accessible - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def test_menu_item(self, item):
        """Test a single menu item"""
        name = item['name']
        url = item['url']
        
        try:
            full_url = urljoin(BASE_URL, url)
            print(f"\n🔍 Testing: {name} ({url})")
            
            response = self.session.get(full_url, timeout=10)
            
            result = {
                'name': name,
                'url': url,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'content_length': len(response.content),
                'success': False,
                'issues': []
            }
            
            # Check status code
            if response.status_code == 200:
                print(f"  ✅ Status: {response.status_code}")
                result['success'] = True
            elif response.status_code == 302:
                print(f"  ⚠️  Status: {response.status_code} (Redirect)")
                result['issues'].append(f"Redirected to: {response.headers.get('Location', 'Unknown')}")
            elif response.status_code == 403:
                print(f"  ⚠️  Status: {response.status_code} (Access Denied)")
                result['issues'].append("Access denied - check permissions")
            else:
                print(f"  ❌ Status: {response.status_code}")
                result['issues'].append(f"HTTP {response.status_code}")
            
            # Check content
            content = response.text.lower()
            
            # Check for common error indicators
            if 'error' in content and 'alert-danger' in content:
                result['issues'].append("Error message detected on page")
                print("  ⚠️  Error message detected")
            
            if 'traceback' in content or 'internal server error' in content:
                result['issues'].append("Server error detected")
                print("  ❌ Server error detected")
            
            # Check for basic HTML structure
            if '<html' in content and '</html>' in content:
                print("  ✅ Valid HTML structure")
            else:
                result['issues'].append("Invalid HTML structure")
                print("  ❌ Invalid HTML structure")
            
            # Check for navigation elements
            if 'navbar' in content or 'nav-link' in content:
                print("  ✅ Navigation present")
            else:
                result['issues'].append("Navigation elements missing")
                print("  ⚠️  Navigation elements missing")
            
            # Check response time
            if result['response_time'] < 2.0:
                print(f"  ✅ Response time: {result['response_time']:.2f}s")
            else:
                print(f"  ⚠️  Slow response time: {result['response_time']:.2f}s")
                result['issues'].append(f"Slow response ({result['response_time']:.2f}s)")
            
            return result
            
        except requests.exceptions.Timeout:
            print(f"  ❌ Timeout error")
            return {
                'name': name, 'url': url, 'status_code': 0,
                'response_time': 0, 'content_length': 0,
                'success': False, 'issues': ['Timeout']
            }
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return {
                'name': name, 'url': url, 'status_code': 0,
                'response_time': 0, 'content_length': 0,
                'success': False, 'issues': [f'Exception: {str(e)}']
            }
    
    def test_all_menu_items(self):
        """Test all menu items"""
        print(f"🚀 Starting comprehensive menu navigation test")
        print(f"📍 Base URL: {BASE_URL}")
        print(f"📋 Total menu items to test: {len(MENU_ITEMS)}")
        
        # Login first
        if not self.login():
            print("❌ Cannot proceed without login")
            return False
        
        print(f"\n{'='*80}")
        print("TESTING MENU NAVIGATION")
        print(f"{'='*80}")
        
        # Test each menu item
        for i, item in enumerate(MENU_ITEMS, 1):
            print(f"\n[{i}/{len(MENU_ITEMS)}]", end="")
            result = self.test_menu_item(item)
            self.results.append(result)
            
            # Small delay between requests
            time.sleep(0.5)
        
        return True
    
    def generate_report(self):
        """Generate comprehensive test report"""
        if not self.results:
            print("❌ No test results to report")
            return
        
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        with_issues = [r for r in self.results if r['issues']]
        
        print(f"\n{'='*80}")
        print("COMPREHENSIVE TEST REPORT")
        print(f"{'='*80}")
        
        print(f"\n📊 SUMMARY:")
        print(f"  Total pages tested: {len(self.results)}")
        print(f"  ✅ Successful: {len(successful)} ({len(successful)/len(self.results)*100:.1f}%)")
        print(f"  ❌ Failed: {len(failed)} ({len(failed)/len(self.results)*100:.1f}%)")
        print(f"  ⚠️  With issues: {len(with_issues)} ({len(with_issues)/len(self.results)*100:.1f}%)")
        
        if successful:
            print(f"\n✅ SUCCESSFUL PAGES ({len(successful)}):")
            for result in successful:
                status = "✅" if not result['issues'] else "⚠️ "
                print(f"  {status} {result['name']} ({result['url']}) - {result['response_time']:.2f}s")
        
        if failed:
            print(f"\n❌ FAILED PAGES ({len(failed)}):")
            for result in failed:
                print(f"  ❌ {result['name']} ({result['url']})")
                for issue in result['issues']:
                    print(f"     - {issue}")
        
        if with_issues:
            print(f"\n⚠️  PAGES WITH ISSUES ({len(with_issues)}):")
            for result in with_issues:
                if result['success']:  # Only show successful pages with issues
                    print(f"  ⚠️  {result['name']} ({result['url']})")
                    for issue in result['issues']:
                        print(f"     - {issue}")
        
        # Performance analysis
        avg_response_time = sum(r['response_time'] for r in self.results if r['response_time'] > 0) / len([r for r in self.results if r['response_time'] > 0])
        slow_pages = [r for r in self.results if r['response_time'] > 2.0]
        
        print(f"\n🚀 PERFORMANCE ANALYSIS:")
        print(f"  Average response time: {avg_response_time:.2f}s")
        if slow_pages:
            print(f"  Slow pages (>2s): {len(slow_pages)}")
            for page in slow_pages:
                print(f"    - {page['name']}: {page['response_time']:.2f}s")
        else:
            print(f"  All pages load quickly (<2s)")
        
        print(f"\n{'='*80}")

def main():
    """Main test execution"""
    print("🧪 Spa Management System - Menu Navigation Test")
    print(f"⏰ Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        tester = MenuNavigationTester()
        
        if tester.test_all_menu_items():
            tester.generate_report()
            
            # Check if we need to exit with error code
            failed_tests = [r for r in tester.results if not r['success']]
            if failed_tests:
                print(f"\n❌ Test completed with {len(failed_tests)} failures")
                sys.exit(1)
            else:
                print(f"\n✅ All tests passed successfully!")
                sys.exit(0)
        else:
            print(f"\n❌ Test execution failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
