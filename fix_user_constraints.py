
"""
Fix user foreign key constraints in inventory tables
"""
from app import app, db

def fix_user_constraints():
    """Make created_by and user_id fields nullable in inventory tables"""
    with app.app_context():
        try:
            # Make created_by nullable in inventory_adjustments
            db.engine.execute("""
                ALTER TABLE inventory_adjustments 
                ALTER COLUMN created_by DROP NOT NULL;
            """)
            
            # Make created_by nullable in inventory_consumption
            db.engine.execute("""
                ALTER TABLE inventory_consumption 
                ALTER COLUMN created_by DROP NOT NULL;
            """)
            
            # Make created_by nullable in inventory_transfers
            db.engine.execute("""
                ALTER TABLE inventory_transfers 
                ALTER COLUMN created_by DROP NOT NULL;
            """)
            
            # Make user_id nullable in inventory_audit_log
            db.engine.execute("""
                ALTER TABLE inventory_audit_log 
                ALTER COLUMN user_id DROP NOT NULL;
            """)
            
            print("✅ Successfully updated inventory table constraints")
            
        except Exception as e:
            print(f"❌ Error updating constraints: {e}")
            print("This might be expected if constraints were already updated")

if __name__ == "__main__":
    fix_user_constraints()
