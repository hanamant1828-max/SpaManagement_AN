
#!/usr/bin/env python3
"""
Main Demo Database Setup Script
Run this script to create a complete demo database for client presentations
"""

import sys
import os
from datetime import datetime

def setup_complete_demo():
    """Setup complete demo database with all sample data"""
    
    print("🚀 Setting up Complete Demo Database for Spa Management System")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import and run the demo data generator
        from demo_data.demo_data_generator import DemoDataGenerator
        
        generator = DemoDataGenerator()
        generator.generate_all_demo_data()
        
        print(f"\n✅ Demo setup completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🎯 NEXT STEPS:")
        print("1. Start your Flask application: python main.py")
        print("2. Login with: admin / admin123")
        print("3. Explore all modules with realistic demo data")
        print("4. Show clients the fully functional spa management system")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure all required modules are available")
        return False
        
    except Exception as e:
        print(f"❌ Setup Error: {e}")
        print("Check your database connection and try again")
        return False

if __name__ == "__main__":
    success = setup_complete_demo()
    if success:
        print("\n🎉 Demo database is ready for client presentations!")
    else:
        print("\n😞 Demo setup failed. Please check the errors above.")
        sys.exit(1)
