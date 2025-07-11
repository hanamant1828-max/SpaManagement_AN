#!/usr/bin/env python3
"""
Comprehensive Module Testing Script for Spa & Salon Management System
This script tests all modules and generates a detailed bug report.
"""

import requests
import json
from datetime import datetime
import sys

class SpaSystemTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.bugs = []
        self.successes = []
        
    def log_bug(self, module, issue, severity="Medium"):
        self.bugs.append({
            "module": module,
            "issue": issue,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })
        
    def log_success(self, module, test):
        self.successes.append({
            "module": module,
            "test": test,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_csrf_token(self, url):
        """Extract CSRF token from a page"""
        try:
            response = self.session.get(url)
            if 'csrf_token' in response.text:
                # Simple extraction - in real implementation would use BeautifulSoup
                start = response.text.find('name="csrf_token" type="hidden" value="') + 40
                end = response.text.find('"', start)
                return response.text[start:end]
        except Exception as e:
            self.log_bug("Authentication", f"CSRF token extraction failed: {str(e)}", "High")
        return None
        
    def test_authentication(self):
        """Test login/logout functionality"""
        print("Testing Authentication...")
        
        # Test login page access
        try:
            response = self.session.get(f"{self.base_url}/login")
            if response.status_code == 200:
                self.log_success("Authentication", "Login page accessible")
            else:
                self.log_bug("Authentication", f"Login page returned {response.status_code}", "High")
        except Exception as e:
            self.log_bug("Authentication", f"Cannot access login page: {str(e)}", "Critical")
            return False
            
        # Test login with admin credentials
        csrf_token = self.get_csrf_token(f"{self.base_url}/login")
        if csrf_token:
            login_data = {
                "username": "admin",
                "password": "admin123",
                "csrf_token": csrf_token
            }
            
            try:
                response = self.session.post(f"{self.base_url}/login", data=login_data)
                if response.status_code == 302 or "dashboard" in response.text.lower():
                    self.log_success("Authentication", "Admin login successful")
                    return True
                else:
                    self.log_bug("Authentication", "Admin login failed", "Critical")
            except Exception as e:
                self.log_bug("Authentication", f"Login request failed: {str(e)}", "Critical")
        
        return False
        
    def test_dashboard(self):
        """Test dashboard functionality"""
        print("Testing Dashboard...")
        
        try:
            response = self.session.get(f"{self.base_url}/dashboard")
            if response.status_code == 200:
                self.log_success("Dashboard", "Dashboard accessible")
                
                # Check for key dashboard elements
                content = response.text.lower()
                if "total revenue" in content:
                    self.log_success("Dashboard", "Revenue metrics displayed")
                if "appointments" in content:
                    self.log_success("Dashboard", "Appointment metrics displayed")
                if "clients" in content:
                    self.log_success("Dashboard", "Client metrics displayed")
            else:
                self.log_bug("Dashboard", f"Dashboard returned {response.status_code}", "High")
        except Exception as e:
            self.log_bug("Dashboard", f"Dashboard access failed: {str(e)}", "High")
            
    def test_clients_module(self):
        """Test client management functionality"""
        print("Testing Clients Module...")
        
        try:
            response = self.session.get(f"{self.base_url}/clients")
            if response.status_code == 200:
                self.log_success("Clients", "Clients page accessible")
                
                # Check for client management features
                content = response.text.lower()
                if "add client" in content or "new client" in content:
                    self.log_success("Clients", "Add client functionality available")
                if "search" in content:
                    self.log_success("Clients", "Client search functionality available")
            else:
                self.log_bug("Clients", f"Clients page returned {response.status_code}", "High")
        except Exception as e:
            self.log_bug("Clients", f"Clients module access failed: {str(e)}", "High")
            
    def test_bookings_module(self):
        """Test booking/calendar functionality"""
        print("Testing Bookings Module...")
        
        try:
            response = self.session.get(f"{self.base_url}/bookings")
            if response.status_code == 200:
                self.log_success("Bookings", "Bookings page accessible")
                
                content = response.text.lower()
                if "calendar" in content:
                    self.log_success("Bookings", "Calendar functionality available")
                if "appointment" in content:
                    self.log_success("Bookings", "Appointment functionality available")
            else:
                self.log_bug("Bookings", f"Bookings page returned {response.status_code}", "High")
        except Exception as e:
            self.log_bug("Bookings", f"Bookings module access failed: {str(e)}", "High")
            
    def test_staff_module(self):
        """Test staff management functionality"""
        print("Testing Staff Module...")
        
        try:
            response = self.session.get(f"{self.base_url}/staff")
            if response.status_code == 200:
                self.log_success("Staff", "Staff page accessible")
                
                content = response.text.lower()
                if "staff member" in content or "employee" in content:
                    self.log_success("Staff", "Staff management functionality available")
            else:
                self.log_bug("Staff", f"Staff page returned {response.status_code}", "High")
        except Exception as e:
            self.log_bug("Staff", f"Staff module access failed: {str(e)}", "High")
            
    def test_face_recognition(self):
        """Test face recognition functionality"""
        print("Testing Face Recognition...")
        
        try:
            response = self.session.get(f"{self.base_url}/checkin")
            if response.status_code == 200:
                self.log_success("Face Recognition", "Check-in page accessible")
                
                content = response.text.lower()
                if "camera" in content:
                    self.log_success("Face Recognition", "Camera interface available")
                if "face" in content and "recognition" in content:
                    self.log_success("Face Recognition", "Face recognition interface available")
                else:
                    self.log_bug("Face Recognition", "Face recognition interface incomplete", "Medium")
            else:
                self.log_bug("Face Recognition", f"Check-in page returned {response.status_code}", "High")
        except Exception as e:
            self.log_bug("Face Recognition", f"Face recognition module access failed: {str(e)}", "High")
            
    def test_inventory_module(self):
        """Test inventory management"""
        print("Testing Inventory Module...")
        
        try:
            response = self.session.get(f"{self.base_url}/inventory")
            if response.status_code == 200:
                self.log_success("Inventory", "Inventory page accessible")
                
                content = response.text.lower()
                if "stock" in content:
                    self.log_success("Inventory", "Stock management available")
                if "product" in content:
                    self.log_success("Inventory", "Product management available")
            else:
                self.log_bug("Inventory", f"Inventory page returned {response.status_code}", "High")
        except Exception as e:
            self.log_bug("Inventory", f"Inventory module access failed: {str(e)}", "High")
            
    def test_billing_module(self):
        """Test billing and payment functionality"""
        print("Testing Billing Module...")
        
        try:
            response = self.session.get(f"{self.base_url}/billing")
            if response.status_code == 200:
                self.log_success("Billing", "Billing page accessible")
                
                content = response.text.lower()
                if "invoice" in content:
                    self.log_success("Billing", "Invoice functionality available")
                if "payment" in content:
                    self.log_success("Billing", "Payment functionality available")
            else:
                self.log_bug("Billing", f"Billing page returned {response.status_code}", "High")
        except Exception as e:
            self.log_bug("Billing", f"Billing module access failed: {str(e)}", "High")
            
    def test_system_management(self):
        """Test dynamic CRUD system management"""
        print("Testing System Management...")
        
        try:
            response = self.session.get(f"{self.base_url}/system_management")
            if response.status_code == 200:
                self.log_success("System Management", "System management page accessible")
                
                content = response.text.lower()
                if "role" in content:
                    self.log_success("System Management", "Role management available")
                if "permission" in content:
                    self.log_success("System Management", "Permission management available")
                if "category" in content:
                    self.log_success("System Management", "Category management available")
            elif response.status_code == 404:
                self.log_bug("System Management", "System management route not found", "High")
            else:
                self.log_bug("System Management", f"System management page returned {response.status_code}", "Medium")
        except Exception as e:
            self.log_bug("System Management", f"System management access failed: {str(e)}", "High")
            
    def test_advanced_features(self):
        """Test advanced features like communications, promotions, etc."""
        print("Testing Advanced Features...")
        
        advanced_modules = [
            ("communications", "Communications"),
            ("promotions", "Promotions"),
            ("waitlist", "Waitlist"),
            ("product_sales", "Product Sales"),
            ("reviews", "Reviews")
        ]
        
        for endpoint, module_name in advanced_modules:
            try:
                response = self.session.get(f"{self.base_url}/{endpoint}")
                if response.status_code == 200:
                    self.log_success("Advanced Features", f"{module_name} accessible")
                else:
                    self.log_bug("Advanced Features", f"{module_name} returned {response.status_code}", "Medium")
            except Exception as e:
                self.log_bug("Advanced Features", f"{module_name} access failed: {str(e)}", "Medium")
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("=" * 60)
        print("SPA & SALON MANAGEMENT SYSTEM - COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        
        if self.test_authentication():
            self.test_dashboard()
            self.test_clients_module()
            self.test_bookings_module()
            self.test_staff_module()
            self.test_face_recognition()
            self.test_inventory_module()
            self.test_billing_module()
            self.test_system_management()
            self.test_advanced_features()
        else:
            print("Authentication failed - skipping other tests")
            
        self.generate_report()
        
    def generate_report(self):
        """Generate detailed bug report"""
        print("\n" + "=" * 60)
        print("TESTING COMPLETED - GENERATING REPORT")
        print("=" * 60)
        
        print(f"\n✅ SUCCESSFUL TESTS: {len(self.successes)}")
        for success in self.successes:
            print(f"   [{success['module']}] {success['test']}")
            
        print(f"\n❌ BUGS FOUND: {len(self.bugs)}")
        
        # Group bugs by severity
        critical = [b for b in self.bugs if b['severity'] == 'Critical']
        high = [b for b in self.bugs if b['severity'] == 'High']
        medium = [b for b in self.bugs if b['severity'] == 'Medium']
        
        if critical:
            print(f"\n🔴 CRITICAL ISSUES ({len(critical)}):")
            for bug in critical:
                print(f"   [{bug['module']}] {bug['issue']}")
                
        if high:
            print(f"\n🟡 HIGH PRIORITY ({len(high)}):")
            for bug in high:
                print(f"   [{bug['module']}] {bug['issue']}")
                
        if medium:
            print(f"\n🟠 MEDIUM PRIORITY ({len(medium)}):")
            for bug in medium:
                print(f"   [{bug['module']}] {bug['issue']}")
        
        # Overall assessment
        total_tests = len(self.successes) + len(self.bugs)
        success_rate = (len(self.successes) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL SYSTEM HEALTH: {success_rate:.1f}% ({len(self.successes)}/{total_tests} tests passed)")
        
        if success_rate >= 90:
            print("🟢 EXCELLENT - System is production ready")
        elif success_rate >= 75:
            print("🟡 GOOD - Minor issues need attention")
        elif success_rate >= 50:
            print("🟠 FAIR - Several issues need fixing")
        else:
            print("🔴 POOR - Major issues require immediate attention")
            
        # Save detailed report to file
        report = {
            "timestamp": datetime.now().isoformat(),
            "success_rate": success_rate,
            "total_tests": total_tests,
            "successes": self.successes,
            "bugs": self.bugs
        }
        
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📄 Detailed report saved to: test_report.json")

if __name__ == "__main__":
    tester = SpaSystemTester()
    tester.run_all_tests()