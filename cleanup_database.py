
#!/usr/bin/env python3
"""
Script to clean up the database and keep only service categories and services
Removes all other data including customers, appointments, staff, inventory, etc.
"""

from app import app, db
from models import *
from sqlalchemy import text

def cleanup_database():
    """Remove all data except service categories and services"""
    
    with app.app_context():
        try:
            print("🧹 Starting database cleanup...")
            print("⚠️  This will remove ALL data except service categories and services!")
            
            # Disable foreign key checks temporarily
            db.session.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
            
            # List of tables to clear (everything except categories and services)
            tables_to_clear = [
                # Appointments and related
                'appointment',
                'recurring_appointment',
                'waitlist',
                
                # Clients/Customers
                'client',
                'client_package',
                'client_package_session',
                'review',
                'communication',
                
                # Staff and users
                'user',
                'staff_schedule',
                'staff_service',
                'staff_performance',
                'attendance',
                'leave',
                'commission',
                
                # Billing and invoices
                'invoice',
                'enhanced_invoice',
                'invoice_item',
                'invoice_payment',
                
                # Packages
                'package',
                'package_service',
                
                # Inventory (all inventory related tables)
                'inventory_product',
                'inventory_category',
                'inventory_supplier',
                'inventory_location',
                'inventory_transaction',
                'inventory_alert',
                'inventory_stock_count',
                'inventory_reorder_rule',
                'stock_movement',
                'inventory_item',
                'service_inventory_item',
                'consumption_entry',
                'usage_duration',
                'inventory_adjustment',
                
                # Hanaman inventory
                'hanaman_product',
                'hanaman_category',
                'hanaman_stock_movement',
                'hanaman_supplier',
                'product_master',
                
                # Expenses
                'expense',
                
                # Other business data
                'promotion',
                'location',
                'business_settings',
                
                # System data
                'role',
                'permission',
                'role_permission',
                'department',
                'system_setting'
            ]
            
            # Clear each table
            for table in tables_to_clear:
                try:
                    db.session.execute(text(f'DELETE FROM {table}'))
                    print(f"✅ Cleared table: {table}")
                except Exception as e:
                    print(f"⚠️  Could not clear table {table}: {str(e)}")
            
            # Re-enable foreign key checks
            db.session.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
            
            # Commit all changes
            db.session.commit()
            
            # Verify what's left
            remaining_categories = Category.query.filter_by(category_type='service').count()
            remaining_services = Service.query.count()
            
            print(f"\n✅ Database cleanup completed!")
            print(f"📊 Data remaining:")
            print(f"   - Service Categories: {remaining_categories}")
            print(f"   - Services: {remaining_services}")
            print(f"\n🎯 All other data has been removed.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during cleanup: {str(e)}")
            raise e

if __name__ == "__main__":
    cleanup_database()
