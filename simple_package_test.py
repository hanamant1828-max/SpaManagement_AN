#!/usr/bin/env python3
"""
Simple test to verify package functionality works
"""

from app import app, db
import sqlite3

def test_package_query():
    """Test querying packages from the database"""
    
    with app.app_context():
        try:
            # Test direct SQL query
            conn = sqlite3.connect('spa_management.db')
            cursor = conn.cursor()
            
            # Insert a test package
            cursor.execute('''
                INSERT INTO package (id, name, description, "listPrice", "discountType", 
                                   "discountValue", "totalPrice", "validityDays", 
                                   "maxRedemptions", "targetAudience", active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', ('pkg_test_001', 'Test Package', 'A test package', 
                  100.00, 'PERCENT', 10.00, 90.00, 30, 5, 'ALL', 1))
            
            # Query packages
            cursor.execute('SELECT * FROM package')
            packages = cursor.fetchall()
            
            print("✅ Package table accessible")
            print(f"Found {len(packages)} package(s)")
            
            if packages:
                print("Package details:")
                for pkg in packages:
                    print(f"  ID: {pkg[0]}, Name: {pkg[1]}, Price: {pkg[3]}")
            
            conn.commit()
            conn.close()
            
            print("✅ Direct SQL test successful")
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

if __name__ == "__main__":
    print("🧪 Testing package functionality...")
    if test_package_query():
        print("🎉 Package functionality test passed!")
    else:
        print("💥 Package functionality test failed!")