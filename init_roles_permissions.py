from app import app, db
from models import Role, Permission, RolePermission, Department
from datetime import datetime

def init_roles_and_permissions():
    with app.app_context():
        print("Initializing roles and permissions...")
        
        permissions_data = [
            {'name': 'dashboard_view', 'display_name': 'View Dashboard', 'module': 'dashboard', 'description': 'Access to view dashboard'},
            {'name': 'user_management_access', 'display_name': 'User Management Access', 'module': 'user_management', 'description': 'Full access to user management system'},
            
            {'name': 'clients_view', 'display_name': 'View Clients', 'module': 'clients', 'description': 'View client list and details'},
            {'name': 'clients_create', 'display_name': 'Create Clients', 'module': 'clients', 'description': 'Add new clients'},
            {'name': 'clients_edit', 'display_name': 'Edit Clients', 'module': 'clients', 'description': 'Modify client information'},
            {'name': 'clients_delete', 'display_name': 'Delete Clients', 'module': 'clients', 'description': 'Remove clients'},
            
            {'name': 'staff_view', 'display_name': 'View Staff', 'module': 'staff', 'description': 'View staff list and details'},
            {'name': 'staff_create', 'display_name': 'Create Staff', 'module': 'staff', 'description': 'Add new staff members'},
            {'name': 'staff_edit', 'display_name': 'Edit Staff', 'module': 'staff', 'description': 'Modify staff information'},
            {'name': 'staff_delete', 'display_name': 'Delete Staff', 'module': 'staff', 'description': 'Remove staff members'},
            
            {'name': 'services_view', 'display_name': 'View Services', 'module': 'services', 'description': 'View service list and details'},
            {'name': 'services_create', 'display_name': 'Create Services', 'module': 'services', 'description': 'Add new services'},
            {'name': 'services_edit', 'display_name': 'Edit Services', 'module': 'services', 'description': 'Modify service information'},
            {'name': 'services_delete', 'display_name': 'Delete Services', 'module': 'services', 'description': 'Remove services'},
            
            {'name': 'packages_view', 'display_name': 'View Packages', 'module': 'packages', 'description': 'View package list and details'},
            {'name': 'packages_create', 'display_name': 'Create Packages', 'module': 'packages', 'description': 'Add new packages'},
            {'name': 'packages_edit', 'display_name': 'Edit Packages', 'module': 'packages', 'description': 'Modify package information'},
            {'name': 'packages_delete', 'display_name': 'Delete Packages', 'module': 'packages', 'description': 'Remove packages'},
            
            {'name': 'appointments_view', 'display_name': 'View Appointments', 'module': 'appointments', 'description': 'View appointment schedule'},
            {'name': 'appointments_create', 'display_name': 'Create Appointments', 'module': 'appointments', 'description': 'Schedule new appointments'},
            {'name': 'appointments_edit', 'display_name': 'Edit Appointments', 'module': 'appointments', 'description': 'Modify appointments'},
            {'name': 'appointments_delete', 'display_name': 'Delete Appointments', 'module': 'appointments', 'description': 'Cancel appointments'},
            
            {'name': 'billing_view', 'display_name': 'View Billing', 'module': 'billing', 'description': 'View billing and invoices'},
            {'name': 'billing_create', 'display_name': 'Create Billing', 'module': 'billing', 'description': 'Create invoices and process payments'},
            {'name': 'billing_edit', 'display_name': 'Edit Billing', 'module': 'billing', 'description': 'Modify billing records'},
            
            {'name': 'reports_view', 'display_name': 'View Reports', 'module': 'reports', 'description': 'Access analytics and reports'},
            {'name': 'reports_export', 'display_name': 'Export Reports', 'module': 'reports', 'description': 'Export report data'},
            
            {'name': 'expenses_view', 'display_name': 'View Expenses', 'module': 'expenses', 'description': 'View expense records'},
            {'name': 'expenses_create', 'display_name': 'Create Expenses', 'module': 'expenses', 'description': 'Add new expense records'},
            {'name': 'expenses_edit', 'display_name': 'Edit Expenses', 'module': 'expenses', 'description': 'Modify expense records'},
            {'name': 'expenses_delete', 'display_name': 'Delete Expenses', 'module': 'expenses', 'description': 'Remove expense records'},
            
            {'name': 'inventory_view', 'display_name': 'View Inventory', 'module': 'inventory', 'description': 'View inventory items'},
            {'name': 'inventory_create', 'display_name': 'Create Inventory', 'module': 'inventory', 'description': 'Add inventory items'},
            {'name': 'inventory_edit', 'display_name': 'Edit Inventory', 'module': 'inventory', 'description': 'Modify inventory items'},
            {'name': 'inventory_delete', 'display_name': 'Delete Inventory', 'module': 'inventory', 'description': 'Remove inventory items'},
            
            {'name': 'settings_view', 'display_name': 'View Settings', 'module': 'settings', 'description': 'View system settings'},
            {'name': 'settings_edit', 'display_name': 'Edit Settings', 'module': 'settings', 'description': 'Modify system settings'},
        ]
        
        print(f"Creating {len(permissions_data)} permissions...")
        for perm_data in permissions_data:
            existing = Permission.query.filter_by(name=perm_data['name']).first()
            if not existing:
                permission = Permission(**perm_data, is_active=True, created_at=datetime.utcnow())
                db.session.add(permission)
                print(f"  ✅ Created permission: {perm_data['name']}")
            else:
                print(f"  ⏭️  Permission already exists: {perm_data['name']}")
        
        db.session.commit()
        
        roles_data = [
            {
                'name': 'super_admin',
                'display_name': 'Super Administrator',
                'description': 'Full system access with all permissions',
                'permissions': [p['name'] for p in permissions_data]
            },
            {
                'name': 'manager',
                'display_name': 'Manager',
                'description': 'Manage operations, staff, and clients',
                'permissions': [
                    'dashboard_view', 'clients_view', 'clients_create', 'clients_edit',
                    'staff_view', 'staff_create', 'staff_edit',
                    'services_view', 'services_create', 'services_edit',
                    'packages_view', 'packages_create', 'packages_edit',
                    'appointments_view', 'appointments_create', 'appointments_edit',
                    'billing_view', 'billing_create', 'billing_edit',
                    'reports_view', 'reports_export', 'expenses_view',
                    'inventory_view'
                ]
            },
            {
                'name': 'receptionist',
                'display_name': 'Receptionist',
                'description': 'Handle appointments and client management',
                'permissions': [
                    'dashboard_view', 'clients_view', 'clients_create', 'clients_edit',
                    'services_view', 'appointments_view', 'appointments_create', 
                    'appointments_edit', 'billing_view', 'billing_create'
                ]
            },
            {
                'name': 'therapist',
                'display_name': 'Therapist / Staff',
                'description': 'View schedule and client information',
                'permissions': [
                    'dashboard_view', 'clients_view', 'services_view',
                    'appointments_view', 'billing_view'
                ]
            },
            {
                'name': 'accountant',
                'display_name': 'Accountant',
                'description': 'Manage billing, expenses, and reports',
                'permissions': [
                    'dashboard_view', 'billing_view', 'billing_create', 'billing_edit',
                    'expenses_view', 'expenses_create', 'expenses_edit',
                    'reports_view', 'reports_export'
                ]
            }
        ]
        
        print(f"\nCreating {len(roles_data)} roles...")
        for role_data in roles_data:
            existing_role = Role.query.filter_by(name=role_data['name']).first()
            if not existing_role:
                role = Role(
                    name=role_data['name'],
                    display_name=role_data['display_name'],
                    description=role_data['description'],
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.session.add(role)
                db.session.flush()
                
                for perm_name in role_data['permissions']:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        role_perm = RolePermission(role_id=role.id, permission_id=permission.id)
                        db.session.add(role_perm)
                
                print(f"  ✅ Created role: {role_data['name']} with {len(role_data['permissions'])} permissions")
            else:
                # Update existing role with any missing permissions
                print(f"  🔄 Updating existing role: {role_data['name']}")
                role = existing_role
                
                # Get current permissions for this role
                current_permissions = {rp.permission.name for rp in role.permissions if rp.permission}
                
                # Add missing permissions
                added_count = 0
                for perm_name in role_data['permissions']:
                    if perm_name not in current_permissions:
                        permission = Permission.query.filter_by(name=perm_name).first()
                        if permission:
                            # Check if this permission is already assigned to avoid duplicates
                            existing_assignment = RolePermission.query.filter_by(
                                role_id=role.id, 
                                permission_id=permission.id
                            ).first()
                            if not existing_assignment:
                                role_perm = RolePermission(role_id=role.id, permission_id=permission.id)
                                db.session.add(role_perm)
                                added_count += 1
                                print(f"    ➕ Added permission: {perm_name}")
                
                if added_count > 0:
                    print(f"  ✅ Updated role: {role_data['name']} with {added_count} new permissions")
                else:
                    print(f"  ✅ Role {role_data['name']} is up to date")
        
        db.session.commit()
        
        departments_data = [
            {'name': 'spa_services', 'display_name': 'Spa Services', 'description': 'Spa treatment providers'},
            {'name': 'front_desk', 'display_name': 'Front Desk', 'description': 'Reception and customer service'},
            {'name': 'management', 'display_name': 'Management', 'description': 'Management and administration'},
            {'name': 'finance', 'display_name': 'Finance', 'description': 'Accounting and finance'},
        ]
        
        print(f"\nCreating {len(departments_data)} departments...")
        for dept_data in departments_data:
            existing_dept = Department.query.filter_by(name=dept_data['name']).first()
            if not existing_dept:
                department = Department(**dept_data, is_active=True, created_at=datetime.utcnow())
                db.session.add(department)
                print(f"  ✅ Created department: {dept_data['name']}")
            else:
                print(f"  ⏭️  Department already exists: {dept_data['name']}")
        
        db.session.commit()
        
        print("\n✅ Roles, permissions, and departments initialized successfully!")
        print("\nCreated Roles:")
        for role in Role.query.all():
            print(f"  - {role.display_name} ({role.name}): {len(role.permissions)} permissions")

if __name__ == '__main__':
    init_roles_and_permissions()
