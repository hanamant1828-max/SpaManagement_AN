
#!/usr/bin/env python3
"""
Runner script for Staff Management UI Test Suite
Simplified execution with error handling
"""

import subprocess
import sys
import time
import requests

def check_server_running():
    """Check if the Flask server is running"""
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=5)
        return True
    except:
        return False

def main():
    """Main runner function"""
    print("🚀 Staff Management UI Test Runner")
    print("=" * 50)
    
    # Check if server is running
    if not check_server_running():
        print("❌ Flask server is not running on http://127.0.0.1:5000")
        print("📝 Please start the server first:")
        print("   python main.py")
        print("   or click the Run button in Replit")
        return False
    
    print("✅ Server is running")
    print("🔄 Starting UI test suite...")
    
    try:
        # Run the test suite
        result = subprocess.run([sys.executable, "test_staff_management_ui_complete.py"], 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n🎉 All tests completed successfully!")
        else:
            print(f"\n⚠️ Tests completed with some issues (exit code: {result.returncode})")
            
        return True
        
    except FileNotFoundError:
        print("❌ Test file not found. Please ensure test_staff_management_ui_complete.py exists")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {str(e)}")
        return False

if __name__ == "__main__":
    main()
