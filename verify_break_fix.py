
"""
Quick verification script for break time fix
"""
import requests
from datetime import date

def quick_verify():
    """Quick verification of the break time fix"""
    print("🔍 Quick Break Time Fix Verification")
    print("=" * 40)
    
    try:
        # Check if the app is running
        response = requests.get("http://127.0.0.1:5000/staff-availability")
        
        if response.status_code == 200:
            print("✅ App is running and accessible")
            
            # Check for key indicators in the HTML
            html = response.text
            
            # Look for break time elements
            break_checks = {
                "Break Time text": "Break Time" in html,
                "Warning background": "bg-warning" in html,
                "Coffee icon": "fas fa-coffee" in html,
                "Break status": 'status": "break"' in html or "status-break" in html
            }
            
            print("\n🔍 Break Time Indicators:")
            for check, result in break_checks.items():
                status = "✅" if result else "❌"
                print(f"  {status} {check}: {result}")
            
            # Count potential issues
            book_buttons = html.count('btn btn-success btn-sm w-100 quick-book-btn')
            break_slots = html.count('Break Time') + html.count('bg-warning')
            
            print(f"\n📊 Statistics:")
            print(f"  📗 Book buttons found: {book_buttons}")
            print(f"  ☕ Break slots found: {break_slots}")
            
            if break_slots > 0:
                print("✅ Break time slots are being rendered")
            else:
                print("⚠️  No break time slots found - check if schedules have break times set")
                
        else:
            print(f"❌ App not accessible: HTTP {response.status_code}")
            print("Make sure the Flask app is running on port 5000")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the app")
        print("Please ensure the Flask app is running: python main.py")
    except Exception as e:
        print(f"❌ Error during verification: {e}")
    
    print("\n🎯 Manual Check Recommended:")
    print("1. Open http://127.0.0.1:5000/staff-availability")
    print("2. Look for staff with scheduled break times")
    print("3. Verify break time slots show 'Break Time' not 'Book'")
    print("4. Break times should have yellow/warning background")

if __name__ == "__main__":
    quick_verify()
