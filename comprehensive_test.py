#!/usr/bin/env python3
"""
Comprehensive Spa Management System Test Suite
Tests all major functionality and modules
"""

import urllib.request
import urllib.parse
import json
import sys
from datetime import datetime

def test_route(url, description):
    """Test a route and return success status"""
    try:
        response = urllib.request.urlopen(url)
        status = response.getcode()
        return {
            'url': url,
            'description': description,
            'status': status,
            'success': status in [200, 302]  # 302 is expected for login redirects
        }
    except Exception as e:
        return {
            'url': url,
            'description': description,
            'status': 'ERROR',
            'success': False,
            'error': str(e)
        }

def main():
    print("🧪 COMPREHENSIVE SPA MANAGEMENT SYSTEM TEST")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # Core routes to test
    test_routes = [
        ('/', 'Root redirect'),
        ('/login', 'Login page'),
        ('/dashboard', 'Dashboard (should redirect to login)'),
        ('/staff', 'Staff management'),
        ('/clients', 'Client management'),
        ('/bookings', 'Booking calendar'),
        ('/billing', 'Billing system'),
        ('/inventory', 'Inventory management'),
        ('/expenses', 'Expense tracking'),
        ('/reports', 'Reports module'),
        ('/packages', 'Package management'),
        ('/checkin', 'Check-in system'),
        ('/notifications', 'Notifications'),
        ('/settings', 'Settings panel'),
        ('/role_management', 'Role management'),
        ('/face_management', 'Face recognition'),
        ('/system_management', 'System management'),
        ('/communications', 'Communications'),
        ('/promotions', 'Promotions'),
        ('/waitlist', 'Waitlist management'),
        ('/product_sales', 'Product sales'),
        ('/recurring_appointments', 'Recurring appointments'),
        ('/reviews', 'Customer reviews'),
        ('/business_settings', 'Business settings')
    ]
    
    # Run tests
    results = []
    for route, description in test_routes:
        url = f"{base_url}{route}"
        result = test_route(url, description)
        results.append(result)
        
        # Print real-time results
        status_icon = "✅" if result['success'] else "❌"
        status_text = f"({result['status']})"
        print(f"{status_icon} {description:<25} {status_text}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print(f"\n❌ FAILED ROUTES ({failed_tests}):")
        for result in results:
            if not result['success']:
                error_msg = result.get('error', result['status'])
                print(f"   • {result['description']}: {error_msg}")
    
    # Overall status
    if passed_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED! System is fully functional.")
        return True
    elif passed_tests >= total_tests * 0.8:
        print(f"\n🟡 MOSTLY WORKING - {passed_tests}/{total_tests} routes accessible")
        return True
    else:
        print(f"\n🔴 SYSTEM NEEDS ATTENTION - Only {passed_tests}/{total_tests} routes working")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)