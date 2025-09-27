
#!/usr/bin/env python3
"""
Clear all data from the Spa Management System database
This will remove all records but keep the table structure intact
"""

import os
import sys
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import *

def clear_all_data():
    """Clear all data from all tables while preserving structure"""
    
    with app.app_context():
        try:
            print("🧹 Starting complete data cleanup...")
            print("⚠️  This will remove ALL data from the database!")
            print("📋 Table structure will be preserved")
            
            # Get all table names
            tables_cleared = []
            records_deleted = 0
            
            # Clear data in dependency order (child tables first)
            
            # 1. Clear appointment-related data
            print("\n🗓️  Clearing appointment data...")
            
            # UnakiBooking
            unaki_count = UnakiBooking.query.count()
            if unaki_count > 0:
                UnakiBooking.query.delete()
                tables_cleared.append(f"UnakiBooking ({unaki_count} records)")
                records_deleted += unaki_count
            
            # Regular Appointments
            appointment_count = Appointment.query.count()
            if appointment_count > 0:
                Appointment.query.delete()
                tables_cleared.append(f"Appointment ({appointment_count} records)")
                records_deleted += appointment_count
            
            # 2. Clear package-related data
            print("📦 Clearing package data...")
            
            # Package usage and assignments
            try:
                package_usage_count = PackageUsage.query.count()
                if package_usage_count > 0:
                    PackageUsage.query.delete()
                    tables_cleared.append(f"PackageUsage ({package_usage_count} records)")
                    records_deleted += package_usage_count
            except:
                pass
            
            try:
                customer_package_item_count = CustomerPackageItem.query.count()
                if customer_package_item_count > 0:
                    CustomerPackageItem.query.delete()
                    tables_cleared.append(f"CustomerPackageItem ({customer_package_item_count} records)")
                    records_deleted += customer_package_item_count
            except:
                pass
            
            try:
                customer_package_count = CustomerPackage.query.count()
                if customer_package_count > 0:
                    CustomerPackage.query.delete()
                    tables_cleared.append(f"CustomerPackage ({customer_package_count} records)")
                    records_deleted += customer_package_count
            except:
                pass
            
            try:
                service_package_assignment_count = ServicePackageAssignment.query.count()
                if service_package_assignment_count > 0:
                    ServicePackageAssignment.query.delete()
                    tables_cleared.append(f"ServicePackageAssignment ({service_package_assignment_count} records)")
                    records_deleted += service_package_assignment_count
            except:
                pass
            
            # 3. Clear billing data
            print("💰 Clearing billing data...")
            
            try:
                invoice_payment_count = InvoicePayment.query.count()
                if invoice_payment_count > 0:
                    InvoicePayment.query.delete()
                    tables_cleared.append(f"InvoicePayment ({invoice_payment_count} records)")
                    records_deleted += invoice_payment_count
            except:
                pass
            
            try:
                invoice_item_count = InvoiceItem.query.count()
                if invoice_item_count > 0:
                    InvoiceItem.query.delete()
                    tables_cleared.append(f"InvoiceItem ({invoice_item_count} records)")
                    records_deleted += invoice_item_count
            except:
                pass
            
            try:
                enhanced_invoice_count = EnhancedInvoice.query.count()
                if enhanced_invoice_count > 0:
                    EnhancedInvoice.query.delete()
                    tables_cleared.append(f"EnhancedInvoice ({enhanced_invoice_count} records)")
                    records_deleted += enhanced_invoice_count
            except:
                pass
            
            try:
                invoice_count = Invoice.query.count()
                if invoice_count > 0:
                    Invoice.query.delete()
                    tables_cleared.append(f"Invoice ({invoice_count} records)")
                    records_deleted += invoice_count
            except:
                pass
            
            # 4. Clear staff-related data
            print("👥 Clearing staff data...")
            
            try:
                shift_logs_count = ShiftLogs.query.count()
                if shift_logs_count > 0:
                    ShiftLogs.query.delete()
                    tables_cleared.append(f"ShiftLogs ({shift_logs_count} records)")
                    records_deleted += shift_logs_count
            except:
                pass
            
            try:
                shift_management_count = ShiftManagement.query.count()
                if shift_management_count > 0:
                    ShiftManagement.query.delete()
                    tables_cleared.append(f"ShiftManagement ({shift_management_count} records)")
                    records_deleted += shift_management_count
            except:
                pass
            
            try:
                attendance_count = Attendance.query.count()
                if attendance_count > 0:
                    Attendance.query.delete()
                    tables_cleared.append(f"Attendance ({attendance_count} records)")
                    records_deleted += attendance_count
            except:
                pass
            
            # 5. Clear customer data
            print("👤 Clearing customer data...")
            
            customer_count = Customer.query.count()
            if customer_count > 0:
                Customer.query.delete()
                tables_cleared.append(f"Customer ({customer_count} records)")
                records_deleted += customer_count
            
            # 6. Clear expense data
            print("💸 Clearing expense data...")
            
            expense_count = Expense.query.count()
            if expense_count > 0:
                Expense.query.delete()
                tables_cleared.append(f"Expense ({expense_count} records)")
                records_deleted += expense_count
            
            # 7. Clear staff data (keep admin user)
            print("🔧 Clearing staff data (keeping admin user)...")
            
            non_admin_users = User.query.filter(User.username != 'admin').all()
            non_admin_count = len(non_admin_users)
            if non_admin_count > 0:
                for user in non_admin_users:
                    db.session.delete(user)
                tables_cleared.append(f"User (non-admin) ({non_admin_count} records)")
                records_deleted += non_admin_count
            
            # 8. Clear package templates
            print("📋 Clearing package templates...")
            
            # Service package relationships
            try:
                membership_service_count = MembershipService.query.count()
                if membership_service_count > 0:
                    MembershipService.query.delete()
                    tables_cleared.append(f"MembershipService ({membership_service_count} records)")
                    records_deleted += membership_service_count
            except:
                pass
            
            try:
                kitty_party_service_count = KittyPartyService.query.count()
                if kitty_party_service_count > 0:
                    KittyPartyService.query.delete()
                    tables_cleared.append(f"KittyPartyService ({kitty_party_service_count} records)")
                    records_deleted += kitty_party_service_count
            except:
                pass
            
            try:
                student_offer_service_count = StudentOfferService.query.count()
                if student_offer_service_count > 0:
                    StudentOfferService.query.delete()
                    tables_cleared.append(f"StudentOfferService ({student_offer_service_count} records)")
                    records_deleted += student_offer_service_count
            except:
                pass
            
            # Package templates
            try:
                prepaid_package_count = PrepaidPackage.query.count()
                if prepaid_package_count > 0:
                    PrepaidPackage.query.delete()
                    tables_cleared.append(f"PrepaidPackage ({prepaid_package_count} records)")
                    records_deleted += prepaid_package_count
            except:
                pass
            
            try:
                service_package_count = ServicePackage.query.count()
                if service_package_count > 0:
                    ServicePackage.query.delete()
                    tables_cleared.append(f"ServicePackage ({service_package_count} records)")
                    records_deleted += service_package_count
            except:
                pass
            
            try:
                membership_count = Membership.query.count()
                if membership_count > 0:
                    Membership.query.delete()
                    tables_cleared.append(f"Membership ({membership_count} records)")
                    records_deleted += membership_count
            except:
                pass
            
            try:
                student_offer_count = StudentOffer.query.count()
                if student_offer_count > 0:
                    StudentOffer.query.delete()
                    tables_cleared.append(f"StudentOffer ({student_offer_count} records)")
                    records_deleted += student_offer_count
            except:
                pass
            
            try:
                yearly_membership_count = YearlyMembership.query.count()
                if yearly_membership_count > 0:
                    YearlyMembership.query.delete()
                    tables_cleared.append(f"YearlyMembership ({yearly_membership_count} records)")
                    records_deleted += yearly_membership_count
            except:
                pass
            
            try:
                kitty_party_count = KittyParty.query.count()
                if kitty_party_count > 0:
                    KittyParty.query.delete()
                    tables_cleared.append(f"KittyParty ({kitty_party_count} records)")
                    records_deleted += kitty_party_count
            except:
                pass
            
            # 9. Clear services (keep core structure)
            print("🛠️  Clearing services...")
            
            service_count = Service.query.count()
            if service_count > 0:
                Service.query.delete()
                tables_cleared.append(f"Service ({service_count} records)")
                records_deleted += service_count
            
            # 10. Clear inventory data (if exists)
            print("📦 Clearing inventory data...")
            
            try:
                # Try to clear inventory tables if they exist
                from modules.inventory.models import InventoryProduct, InventoryBatch, InventoryAuditLog
                
                inventory_audit_count = InventoryAuditLog.query.count()
                if inventory_audit_count > 0:
                    InventoryAuditLog.query.delete()
                    tables_cleared.append(f"InventoryAuditLog ({inventory_audit_count} records)")
                    records_deleted += inventory_audit_count
                
                inventory_batch_count = InventoryBatch.query.count()
                if inventory_batch_count > 0:
                    InventoryBatch.query.delete()
                    tables_cleared.append(f"InventoryBatch ({inventory_batch_count} records)")
                    records_deleted += inventory_batch_count
                
                inventory_product_count = InventoryProduct.query.count()
                if inventory_product_count > 0:
                    InventoryProduct.query.delete()
                    tables_cleared.append(f"InventoryProduct ({inventory_product_count} records)")
                    records_deleted += inventory_product_count
                    
            except ImportError:
                print("   📋 Inventory models not found - skipping")
            except Exception as e:
                print(f"   ⚠️  Error clearing inventory: {e}")
            
            # Commit all deletions
            db.session.commit()
            
            print(f"\n✅ Data cleanup completed successfully!")
            print(f"📊 Summary:")
            print(f"   🗑️  Total records deleted: {records_deleted}")
            print(f"   📋 Tables cleared: {len(tables_cleared)}")
            
            print(f"\n📜 Detailed breakdown:")
            for table_info in tables_cleared:
                print(f"   ✓ {table_info}")
            
            print(f"\n🔐 Admin user preserved for login")
            print(f"💾 Database structure intact")
            print(f"🚀 Ready for fresh data!")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during data cleanup: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🧹 COMPLETE DATA CLEANUP TOOL")
    print("=" * 50)
    print("⚠️  WARNING: This will remove ALL data from your spa management system!")
    print("📋 Only table structure and admin user will be preserved")
    print()
    
    response = input("Are you sure you want to continue? (type 'YES' to confirm): ")
    
    if response == 'YES':
        print("\n🚀 Starting cleanup process...")
        success = clear_all_data()
        
        if success:
            print("\n🎉 Cleanup completed successfully!")
            print("💡 You can now add fresh data or restart the application")
        else:
            print("\n💥 Cleanup failed. Check the error messages above.")
    else:
        print("\n🛑 Cleanup cancelled. No data was removed.")
