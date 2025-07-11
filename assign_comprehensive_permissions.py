#!/usr/bin/env python3
"""
Assign comprehensive permissions to each role based on their responsibility levels
"""

from app import app, db
from models import Role, Permission, RolePermission

def assign_comprehensive_permissions():
    with app.app_context():
        # Clear all existing role permissions
        RolePermission.query.delete()
        
        # Define comprehensive role permission mappings
        role_mappings = {
            'admin': [
                # Admin gets the special 'all' permission which grants everything
                'all'
            ],
            
            'manager': [
                # Dashboard - Full access
                'dashboard_view', 'dashboard_revenue_metrics', 'dashboard_appointment_overview',
                'dashboard_client_stats', 'dashboard_staff_performance', 'dashboard_export_data',
                
                # Bookings - Full management
                'bookings_view', 'bookings_create', 'bookings_edit', 'bookings_delete',
                'bookings_cancel', 'bookings_reschedule', 'bookings_confirm', 'bookings_checkin',
                'bookings_calendar_view', 'bookings_bulk_operations',
                
                # Staff - Management level (no deletion)
                'staff_view', 'staff_create', 'staff_edit', 'staff_schedule_view',
                'staff_schedule_edit', 'staff_performance_view', 'staff_commission_view',
                'staff_payroll_view',
                
                # Clients - Full management
                'clients_view', 'clients_create', 'clients_edit', 'clients_history_view',
                'clients_notes_edit', 'clients_preferences_edit', 'clients_loyalty_manage',
                'clients_communication_view', 'clients_export_data',
                
                # Face Recognition - Management access
                'face_checkin_view', 'face_management_view', 'face_register_clients',
                
                # Communications - Full access
                'communications_view', 'communications_send_email', 'communications_send_sms',
                'communications_send_whatsapp', 'communications_templates', 'communications_history',
                'communications_bulk_send', 'communications_marketing',
                
                # Billing - Full access
                'billing_view', 'billing_create_invoice', 'billing_edit_invoice',
                'billing_process_payment', 'billing_refunds', 'billing_reports',
                
                # Packages - Full management
                'packages_view', 'packages_create', 'packages_edit', 'packages_assign_client',
                'packages_track_usage', 'packages_renewal', 'packages_pricing',
                
                # Inventory - Full management
                'inventory_view', 'inventory_create', 'inventory_edit', 'inventory_stock_adjust',
                'inventory_low_stock_alerts', 'inventory_supplier_manage', 'inventory_categories',
                'inventory_reports',
                
                # Reports - Full access
                'reports_view', 'reports_revenue', 'reports_appointments', 'reports_staff_performance',
                'reports_client_analytics', 'reports_inventory', 'reports_custom', 'reports_export',
                
                # User Management - View only (no creation/deletion)
                'users_view', 'users_login_logs',
                
                # Expenses - Full management
                'expenses_view', 'expenses_create', 'expenses_edit', 'expenses_categories',
                'expenses_approval', 'expenses_reports', 'expenses_budgets',
                
                # Advanced Features
                'promotions_view', 'promotions_create', 'promotions_edit', 'promotions_activate',
                'promotions_analytics',
                'waitlist_view', 'waitlist_add_client', 'waitlist_manage', 'waitlist_notifications',
                'pos_view', 'pos_create_sale', 'pos_refunds', 'pos_reports',
                'reviews_view', 'reviews_respond', 'reviews_analytics'
            ],
            
            'staff': [
                # Dashboard - Basic view
                'dashboard_view', 'dashboard_appointment_overview',
                
                # Bookings - Basic operations
                'bookings_view', 'bookings_create', 'bookings_edit', 'bookings_confirm',
                'bookings_checkin', 'bookings_calendar_view',
                
                # Staff - Own info only
                'staff_view', 'staff_schedule_view', 'staff_performance_view',
                
                # Clients - Basic management
                'clients_view', 'clients_create', 'clients_edit', 'clients_history_view',
                'clients_notes_edit', 'clients_preferences_edit',
                
                # Face Recognition - Check-in only
                'face_checkin_view',
                
                # Communications - Basic sending
                'communications_view', 'communications_send_email',
                
                # Inventory - View only
                'inventory_view',
                
                # POS - Basic sales
                'pos_view', 'pos_create_sale',
                
                # Waitlist - Basic operations
                'waitlist_view', 'waitlist_add_client'
            ],
            
            'cashier': [
                # Dashboard - Basic view
                'dashboard_view',
                
                # Bookings - Check-in only
                'bookings_view', 'bookings_checkin',
                
                # Clients - Basic view and history
                'clients_view', 'clients_history_view',
                
                # Face Recognition - Check-in
                'face_checkin_view',
                
                # Billing - Full access (primary responsibility)
                'billing_view', 'billing_create_invoice', 'billing_edit_invoice',
                'billing_process_payment', 'billing_refunds', 'billing_reports',
                'billing_payment_methods',
                
                # Packages - Sales operations
                'packages_view', 'packages_assign_client', 'packages_track_usage',
                
                # POS - Full access
                'pos_view', 'pos_create_sale', 'pos_refunds', 'pos_reports',
                
                # Inventory - View for sales
                'inventory_view'
            ]
        }
        
        # Assign permissions to roles
        for role_name, permission_names in role_mappings.items():
            role = Role.query.filter_by(name=role_name).first()
            if role:
                print(f"Assigning permissions to {role_name}...")
                
                for perm_name in permission_names:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        role_permission = RolePermission(
                            role_id=role.id,
                            permission_id=permission.id
                        )
                        db.session.add(role_permission)
                    else:
                        print(f"  Warning: Permission '{perm_name}' not found")
                
                print(f"  Assigned {len(permission_names)} permissions to {role_name}")
        
        db.session.commit()
        print("\nPermission assignment completed!")
        
        # Print summary
        print("\n" + "="*60)
        print("COMPREHENSIVE ROLE-BASED PERMISSION SYSTEM")
        print("="*60)
        
        for role in Role.query.all():
            permissions = [rp.permission.name for rp in role.permissions]
            print(f"\n{role.display_name.upper()} ({len(permissions)} permissions):")
            
            if 'all' in permissions:
                print("  → Full system access (all permissions)")
            else:
                # Group permissions by module
                permission_by_module = {}
                for perm_name in permissions:
                    perm = Permission.query.filter_by(name=perm_name).first()
                    if perm:
                        if perm.module not in permission_by_module:
                            permission_by_module[perm.module] = []
                        permission_by_module[perm.module].append(perm.display_name)
                
                for module, perms in permission_by_module.items():
                    print(f"  → {module.replace('_', ' ').title()}: {len(perms)} permissions")

if __name__ == "__main__":
    assign_comprehensive_permissions()