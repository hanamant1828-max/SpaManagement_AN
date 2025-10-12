
#!/usr/bin/env python3
"""
Migration script to add approval workflow columns to expenses table
"""
from app import app, db
from sqlalchemy import text

def add_approval_columns():
    with app.app_context():
        try:
            # Add vendor_name column
            db.session.execute(text('''
                ALTER TABLE expense ADD COLUMN vendor_name VARCHAR(100)
            '''))
            print("✓ Added vendor_name column")
            
            # Add approval_status column
            db.session.execute(text('''
                ALTER TABLE expense ADD COLUMN approval_status VARCHAR(20) DEFAULT 'pending'
            '''))
            print("✓ Added approval_status column")
            
            # Add approved_by column
            db.session.execute(text('''
                ALTER TABLE expense ADD COLUMN approved_by INTEGER
            '''))
            print("✓ Added approved_by column")
            
            # Add approved_at column
            db.session.execute(text('''
                ALTER TABLE expense ADD COLUMN approved_at DATETIME
            '''))
            print("✓ Added approved_at column")
            
            # Add rejection_reason column
            db.session.execute(text('''
                ALTER TABLE expense ADD COLUMN rejection_reason TEXT
            '''))
            print("✓ Added rejection_reason column")
            
            # Add receipt_image column
            db.session.execute(text('''
                ALTER TABLE expense ADD COLUMN receipt_image VARCHAR(255)
            '''))
            print("✓ Added receipt_image column")
            
            db.session.commit()
            print("\n✅ All approval columns added successfully!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

def create_reconciliation_table():
    with app.app_context():
        try:
            db.session.execute(text('''
                CREATE TABLE IF NOT EXISTS daily_reconciliation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    reconciliation_date DATE NOT NULL,
                    system_balance FLOAT NOT NULL,
                    actual_counted FLOAT NOT NULL,
                    difference FLOAT NOT NULL,
                    status VARCHAR(20) DEFAULT 'balanced',
                    reconciled_by INTEGER NOT NULL,
                    reconciled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (account_id) REFERENCES petty_cash_account(id),
                    FOREIGN KEY (reconciled_by) REFERENCES user(id)
                )
            '''))
            db.session.commit()
            print("✅ Daily reconciliation table created successfully!")
        except Exception as e:
            print(f"❌ Error creating reconciliation table: {e}")
            db.session.rollback()

if __name__ == '__main__':
    print("🔄 Starting migration...")
    add_approval_columns()
    create_reconciliation_table()
    print("\n✅ Migration completed!")
