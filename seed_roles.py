
#!/usr/bin/env python3
"""
Seed default roles for the staff management system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Role

def seed_roles():
    """Create default roles"""
    with app.app_context():
        try:
            # Check if roles already exist
            existing_roles = Role.query.all()
            print(f"Existing roles: {len(existing_roles)}")
            for role in existing_roles:
                print(f"  - {role.name}: {role.display_name}")
            
            # Default roles to create
            default_roles = [
                {
                    'name': 'admin',
                    'display_name': 'Administrator',
                    'description': 'Full system access with all permissions',
                    'is_active': True
                },
                {
                    'name': 'manager',
                    'display_name': 'Manager',
                    'description': 'Management level access to most features',
                    'is_active': True
                },
                {
                    'name': 'staff',
                    'display_name': 'Staff Member',
                    'description': 'Standard staff access to basic features',
                    'is_active': True
                },
                {
                    'name': 'receptionist',
                    'display_name': 'Receptionist',
                    'description': 'Front desk and customer service access',
                    'is_active': True
                },
                {
                    'name': 'therapist',
                    'display_name': 'Therapist',
                    'description': 'Service provider with client management access',
                    'is_active': True
                },
                {
                    'name': 'cashier',
                    'display_name': 'Cashier',
                    'description': 'Billing and payment processing access',
                    'is_active': True
                }
            ]
            
            roles_created = 0
            for role_data in default_roles:
                # Check if role already exists
                existing_role = Role.query.filter_by(name=role_data['name']).first()
                if not existing_role:
                    new_role = Role(
                        name=role_data['name'],
                        display_name=role_data['display_name'],
                        description=role_data['description'],
                        is_active=role_data['is_active']
                    )
                    db.session.add(new_role)
                    roles_created += 1
                    print(f"✅ Created role: {role_data['display_name']}")
                else:
                    print(f"⏭️ Role already exists: {role_data['display_name']}")
            
            if roles_created > 0:
                db.session.commit()
                print(f"\n🎉 Successfully created {roles_created} new roles!")
            else:
                print("\n✅ All default roles already exist!")
            
            # Verify roles were created
            all_roles = Role.query.all()
            print(f"\nTotal roles in database: {len(all_roles)}")
            for role in all_roles:
                print(f"  - ID {role.id}: {role.display_name} ({role.name}) - Active: {role.is_active}")
                
        except Exception as e:
            print(f"❌ Error seeding roles: {e}")
            db.session.rollback()

if __name__ == '__main__':
    print("🌱 SEEDING DEFAULT ROLES")
    print("=" * 50)
    seed_roles()
    print("=" * 50)
    print("✅ Role seeding complete!")
