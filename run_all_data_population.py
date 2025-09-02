
#!/usr/bin/env python3
"""
Master script to run all data population scripts in correct order
"""
import subprocess
import sys
import os

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}:")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"⚠️ Script {script_name} not found, skipping...")
        return False

def main():
    """Run all data population scripts"""
    print("🚀 Starting comprehensive data population process...")
    print("=" * 60)
    
    # List of scripts to run in order
    scripts_to_run = [
        ("create_comprehensive_permissions.py", "Creating comprehensive permissions"),
        ("assign_comprehensive_permissions.py", "Assigning permissions to roles"),
        ("migrate_database.py", "Running database migrations"),
        ("populate_all_database_tables.py", "Populating all database tables"),
        ("add_services.py", "Adding comprehensive spa services"),
        ("add_sample_inventory_items.py", "Adding sample inventory items"),
        ("create_spa_packages.py", "Creating spa packages"),
    ]
    
    success_count = 0
    total_scripts = len(scripts_to_run)
    
    for script_name, description in scripts_to_run:
        if run_script(script_name, description):
            success_count += 1
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY: {success_count}/{total_scripts} scripts completed successfully")
    
    if success_count == total_scripts:
        print("🎉 ALL DATA POPULATION COMPLETED SUCCESSFULLY!")
        print("\n📋 Your spa management system now has:")
        print("  ✅ User roles and permissions")
        print("  ✅ Staff members and departments")
        print("  ✅ Sample customers")
        print("  ✅ Comprehensive spa services")
        print("  ✅ Inventory items and suppliers")
        print("  ✅ Spa packages and memberships")
        print("  ✅ Sample appointments")
        print("  ✅ Expense records")
        print("  ✅ Attendance and performance data")
        print("  ✅ Customer reviews")
        print("  ✅ Business settings")
        print("\n🌟 Your system is now ready for use!")
    else:
        print("⚠️ Some scripts had errors. Please check the output above.")
        print("💡 You can run individual scripts manually if needed.")

if __name__ == "__main__":
    main()
