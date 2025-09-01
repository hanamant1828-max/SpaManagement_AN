
#!/usr/bin/env python3
"""
Debug consumption tracking functionality
"""

import sqlite3
import requests
import json

def test_inventory_api():
    """Test the inventory API endpoints"""
    
    print("🔍 Testing Inventory API Endpoints")
    print("=" * 50)
    
    try:
        # Test direct database query
        db_path = 'instance/spa_management.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, current_stock, base_unit FROM inventory WHERE is_active = 1 LIMIT 10")
        items = cursor.fetchall()
        
        print(f"📊 Direct DB Query: Found {len(items)} active inventory items")
        for item in items:
            print(f"  • ID: {item[0]}, Name: {item[1]}, Stock: {item[2]}, Unit: {item[3]}")
        
        conn.close()
        
        # Test API endpoint (if app is running)
        print("\n🌐 Testing API Endpoint...")
        try:
            response = requests.get('http://localhost:5000/api/inventory/status/all', timeout=5)
            print(f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"API Response: {json.dumps(data, indent=2)}")
            else:
                print(f"API Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"API Request Failed: {e}")
            print("Note: Make sure the Flask app is running on port 5000")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_inventory_api()
