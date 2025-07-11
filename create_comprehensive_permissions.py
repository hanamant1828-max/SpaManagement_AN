#!/usr/bin/env python3
"""
Create comprehensive role-based permission system for all 13 core modules
with detailed sub-module permissions and role assignments.
"""

from app import app, db
from models import Role, Permission, RolePermission

def create_comprehensive_permissions():
    with app.app_context():
        # Define all 13 core modules with their sub-permissions
        module_permissions = {
            # 1. Dashboard Module
            'dashboard': [
                'dashboard_view',
                'dashboard_revenue_metrics',
                'dashboard_appointment_overview',
                'dashboard_client_stats',
                'dashboard_staff_performance',
                'dashboard_export_data'
            ],
            
            # 2. Smart Booking & Calendar
            'bookings': [
                'bookings_view',
                'bookings_create',
                'bookings_edit',
                'bookings_delete',
                'bookings_cancel',
                'bookings_reschedule',
                'bookings_confirm',
                'bookings_checkin',
                'bookings_calendar_view',
                'bookings_bulk_operations'
            ],
            
            # 3. Staff Management  
            'staff': [
                'staff_view',
                'staff_create',
                'staff_edit',
                'staff_delete',
                'staff_schedule_view',
                'staff_schedule_edit',
                'staff_performance_view',
                'staff_commission_view',
                'staff_payroll_view',
                'staff_role_assignments'
            ],
            
            # 4. Client Management
            'clients': [
                'clients_view',
                'clients_create',
                'clients_edit',
                'clients_delete',
                'clients_history_view',
                'clients_notes_edit',
                'clients_preferences_edit',
                'clients_loyalty_manage',
                'clients_communication_view',
                'clients_export_data'
            ],
            
            # 5. Face Recognition System
            'face_recognition': [
                'face_checkin_view',
                'face_management_view',
                'face_register_clients',
                'face_remove_data',
                'face_recognition_settings',
                'face_recognition_logs'
            ],
            
            # 6. WhatsApp & Communications
            'communications': [
                'communications_view',
                'communications_send_email',
                'communications_send_sms',
                'communications_send_whatsapp',
                'communications_templates',
                'communications_history',
                'communications_bulk_send',
                'communications_marketing'
            ],
            
            # 7. Billing & Payment System
            'billing': [
                'billing_view',
                'billing_create_invoice',
                'billing_edit_invoice',
                'billing_delete_invoice',
                'billing_process_payment',
                'billing_refunds',
                'billing_payment_methods',
                'billing_reports',
                'billing_tax_settings'
            ],
            
            # 8. Subscription Packages
            'packages': [
                'packages_view',
                'packages_create',
                'packages_edit',
                'packages_delete',
                'packages_assign_client',
                'packages_track_usage',
                'packages_renewal',
                'packages_pricing'
            ],
            
            # 9. Inventory & Product Tracking
            'inventory': [
                'inventory_view',
                'inventory_create',
                'inventory_edit',
                'inventory_delete',
                'inventory_stock_adjust',
                'inventory_low_stock_alerts',
                'inventory_supplier_manage',
                'inventory_categories',
                'inventory_barcode_scan',
                'inventory_reports'
            ],
            
            # 10. Reports & Insights
            'reports': [
                'reports_view',
                'reports_revenue',
                'reports_appointments',
                'reports_staff_performance',
                'reports_client_analytics',
                'reports_inventory',
                'reports_custom',
                'reports_export',
                'reports_dashboard_config'
            ],
            
            # 11. User & Access Control
            'user_management': [
                'users_view',
                'users_create',
                'users_edit',
                'users_delete',
                'users_role_assign',
                'users_permissions_manage',
                'users_login_logs',
                'users_security_settings'
            ],
            
            # 12. Daily Expense Tracker
            'expenses': [
                'expenses_view',
                'expenses_create',
                'expenses_edit',
                'expenses_delete',
                'expenses_categories',
                'expenses_receipts',
                'expenses_approval',
                'expenses_reports',
                'expenses_budgets'
            ],
            
            # 13. System Management
            'system_management': [
                'system_roles_manage',
                'system_permissions_manage',
                'system_categories_manage',
                'system_departments_manage',
                'system_settings_manage',
                'system_backup',
                'system_logs_view',
                'system_maintenance'
            ],
            
            # Advanced Features
            'promotions': [
                'promotions_view',
                'promotions_create',
                'promotions_edit',
                'promotions_delete',
                'promotions_activate',
                'promotions_analytics'
            ],
            
            'waitlist': [
                'waitlist_view',
                'waitlist_add_client',
                'waitlist_manage',
                'waitlist_notifications',
                'waitlist_analytics'
            ],
            
            'product_sales': [
                'pos_view',
                'pos_create_sale',
                'pos_refunds',
                'pos_reports',
                'pos_inventory_sync'
            ],
            
            'reviews': [
                'reviews_view',
                'reviews_respond',
                'reviews_analytics',
                'reviews_moderate'
            ]
        }
        
        # Create all permissions
        print("Creating comprehensive permissions...")
        for module, permissions in module_permissions.items():
            for perm_name in permissions:
                permission = Permission(
                    name=perm_name,
                    display_name=f"{perm_name.replace('_', ' ').title()}",
                    description=f"{perm_name.replace('_', ' ').title()}",
                    module=module,
                    is_active=True
                )
                db.session.add(permission)
        
        # Add special admin permission
        admin_permission = Permission(
            name='all',
            display_name='All Permissions',
            description='Full system access - all permissions',
            module='system',
            is_active=True
        )
        db.session.add(admin_permission)
        
        db.session.commit()
        print(f"Created {len(Permission.query.all())} permissions")
        
        # Define role permission mappings
        role_mappings = {
            'admin': ['all'],  # Admin gets everything
            
            'manager': [
                # Dashboard access
                'dashboard_view', 'dashboard_revenue_metrics', 'dashboard_appointment_overview',
                'dashboard_client_stats', 'dashboard_staff_performance', 'dashboard_export_data',
                
                # Full booking management
                'bookings_view', 'bookings_create', 'bookings_edit', 'bookings_delete',
                'bookings_cancel', 'bookings_reschedule', 'bookings_confirm', 'bookings_checkin',
                'bookings_calendar_view', 'bookings_bulk_operations',
                
                # Staff management (except deletion)
                'staff_view', 'staff_create', 'staff_edit', 'staff_schedule_view',
                'staff_schedule_edit', 'staff_performance_view', 'staff_commission_view',
                'staff_payroll_view',
                
                # Full client management
                'clients_view', 'clients_create', 'clients_edit', 'clients_history_view',
                'clients_notes_edit', 'clients_preferences_edit', 'clients_loyalty_manage',
                'clients_communication_view', 'clients_export_data',
                
                # Basic face recognition
                'face_checkin_view', 'face_management_view',
                
                # Communications
                'communications_view', 'communications_send_email', 'communications_send_sms',
                'communications_templates', 'communications_history',
                
                # Billing management
                'billing_view', 'billing_create_invoice', 'billing_edit_invoice',
                'billing_process_payment', 'billing_reports',
                
                # Package management
                'packages_view', 'packages_create', 'packages_edit', 'packages_assign_client',
                'packages_track_usage', 'packages_renewal',
                
                # Inventory management
                'inventory_view', 'inventory_create', 'inventory_edit', 'inventory_stock_adjust',
                'inventory_low_stock_alerts', 'inventory_supplier_manage', 'inventory_categories',
                'inventory_reports',
                
                # Full reports access
                'reports_view', 'reports_revenue', 'reports_appointments', 'reports_staff_performance',
                'reports_client_analytics', 'reports_inventory', 'reports_export',
                
                # Expense management
                'expenses_view', 'expenses_create', 'expenses_edit', 'expenses_categories',
                'expenses_approval', 'expenses_reports',
                
                # Promotions and advanced features
                'promotions_view', 'promotions_create', 'promotions_edit', 'promotions_activate',
                'waitlist_view', 'waitlist_add_client', 'waitlist_manage',
                'pos_view', 'pos_create_sale', 'pos_reports',
                'reviews_view', 'reviews_respond', 'reviews_analytics'
            ],
            
            'staff': [
                # Basic dashboard
                'dashboard_view', 'dashboard_appointment_overview',
                
                # Booking operations
                'bookings_view', 'bookings_create', 'bookings_edit', 'bookings_confirm',
                'bookings_checkin', 'bookings_calendar_view',
                
                # View staff info
                'staff_view', 'staff_schedule_view', 'staff_performance_view',
                
                # Client management
                'clients_view', 'clients_create', 'clients_edit', 'clients_history_view',
                'clients_notes_edit', 'clients_preferences_edit',
                
                # Face recognition
                'face_checkin_view',
                
                # Basic communications
                'communications_view', 'communications_send_email',
                
                # Basic inventory view
                'inventory_view',
                
                # Basic POS
                'pos_view', 'pos_create_sale'
            ],
            
            'cashier': [
                # Basic dashboard
                'dashboard_view',
                
                # Appointment view only
                'bookings_view', 'bookings_checkin',
                
                # Client basics
                'clients_view', 'clients_history_view',
                
                # Face recognition
                'face_checkin_view',
                
                # Full billing access
                'billing_view', 'billing_create_invoice', 'billing_edit_invoice',
                'billing_process_payment', 'billing_reports',
                
                # Package sales
                'packages_view', 'packages_assign_client', 'packages_track_usage',
                
                # Full POS access
                'pos_view', 'pos_create_sale', 'pos_refunds', 'pos_reports',
                
                # Basic inventory for sales
                'inventory_view'
            ]
        }
        
        # Create role-permission mappings
        print("Creating role-permission mappings...")
        for role_name, permission_names in role_mappings.items():
            role = Role.query.filter_by(name=role_name).first()
            if role:
                # Clear existing permissions
                RolePermission.query.filter_by(role_id=role.id).delete()
                
                for perm_name in permission_names:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        role_permission = RolePermission(
                            role_id=role.id,
                            permission_id=permission.id
                        )
                        db.session.add(role_permission)
                
                print(f"Assigned {len(permission_names)} permissions to {role_name}")
        
        db.session.commit()
        print("Role-permission mappings created successfully!")
        
        # Print summary
        print("\n" + "="*60)
        print("COMPREHENSIVE PERMISSION SYSTEM CREATED")
        print("="*60)
        
        for role in Role.query.all():
            permissions = [rp.permission.name for rp in role.permissions]
            print(f"\n{role.name.upper()} ({len(permissions)} permissions):")
            if 'all' in permissions:
                print("  - Full system access (all permissions)")
            else:
                for perm in sorted(permissions)[:10]:  # Show first 10
                    print(f"  - {perm}")
                if len(permissions) > 10:
                    print(f"  - ... and {len(permissions) - 10} more")

if __name__ == "__main__":
    create_comprehensive_permissions()