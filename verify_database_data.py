
#!/usr/bin/env python3
"""
Verify database population - check all tables for data
"""
from app import app, db
from models import *
import sqlite3

def verify_database_data():
    """Check all tables and display data counts"""
    
    with app.app_context():
        print("🔍 Verifying database data...")
        print("=" * 50)
        
        # Table verification with counts
        tables_to_check = [
            (User, "Staff Users"),
            (Customer, "Customers"),
            (Service, "Services"),
            (Category, "Categories"),
            (Department, "Departments"),
            (Role, "User Roles"),
            (Inventory, "Inventory Items"),
            (Supplier, "Suppliers"),
            (Package, "Spa Packages"),
            (CustomerPackage, "Customer Packages"),
            (Appointment, "Appointments"),
            (Expense, "Expenses"),
            (Attendance, "Attendance Records"),
            (StaffPerformance, "Performance Records"),
            (Review, "Customer Reviews"),
            (StockMovement, "Stock Movements"),
            (SystemSetting, "System Settings"),
        ]
        
        total_records = 0
        
        for model, display_name in tables_to_check:
            try:
                count = model.query.count()
                total_records += count
                status = "✅" if count > 0 else "⚠️"
                print(f"{status} {display_name}: {count} records")
                
                # Show sample data for key tables
                if count > 0 and display_name in ["Staff Users", "Customers", "Services"]:
                    sample = model.query.first()
                    if hasattr(sample, 'name'):
                        print(f"   Sample: {sample.name}")
                    elif hasattr(sample, 'full_name'):
                        print(f"   Sample: {sample.full_name}")
                    elif hasattr(sample, 'username'):
                        print(f"   Sample: {sample.username}")
                        
            except Exception as e:
                print(f"❌ Error checking {display_name}: {e}")
        
        print("=" * 50)
        print(f"📊 TOTAL RECORDS IN DATABASE: {total_records}")
        
        # Check for empty critical tables
        critical_tables = [User, Customer, Service, Inventory]
        empty_critical = [model.__name__ for model in critical_tables if model.query.count() == 0]
        
        if empty_critical:
            print(f"\n⚠️ CRITICAL TABLES WITH NO DATA: {', '.join(empty_critical)}")
            print("💡 Run the population scripts to add sample data.")
        else:
            print("\n🎉 All critical tables have data!")
        
        # Check SQLite database file directly
        check_sqlite_tables()

def check_sqlite_tables():
    """Check SQLite database tables directly"""
    print("\n🗄️ Checking SQLite database structure...")
    
    try:
        conn = sqlite3.connect('instance/spa_management.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📋 Total tables in database: {len(tables)}")
        
        # Count records in each table
        for (table_name,) in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                status = "✅" if count > 0 else "⚠️"
                print(f"{status} {table_name}: {count} records")
            except Exception as e:
                print(f"❌ Error checking {table_name}: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error accessing SQLite database: {e}")

if __name__ == "__main__":
    verify_database_data()
