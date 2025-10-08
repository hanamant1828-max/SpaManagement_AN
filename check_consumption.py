#!/usr/bin/env python3
import sqlite3
import os

# Connect to the SQLite database
db_path = os.path.join(os.getcwd(), 'hanamantdatabase', 'workspace.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check consumption table schema
print("=== CONSUMPTION TABLE SCHEMA ===")
cursor.execute("PRAGMA table_info(inventory_consumption)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Check consumption records with relationships
print("\n=== CONSUMPTION RECORDS ===")
cursor.execute("""
    SELECT 
        c.id, c.batch_id, c.quantity, c.issued_to, c.reference, c.created_by, c.created_at,
        b.batch_name, b.product_id,
        p.name as product_name
    FROM inventory_consumption c
    LEFT JOIN inventory_batches b ON c.batch_id = b.id
    LEFT JOIN inventory_products p ON b.product_id = p.id
""")
consumptions = cursor.fetchall()
for c in consumptions:
    print(f"\n  ID: {c[0]}")
    print(f"    Batch ID: {c[1]}, Batch Name: {c[7]}")
    print(f"    Product ID: {c[8]}, Product Name: {c[9]}")
    print(f"    Quantity: {c[2]}")
    print(f"    Issued To: {c[3]}")
    print(f"    Reference: {c[4]}")
    print(f"    Created By: {c[5]}")
    print(f"    Created At: {c[6]}")

# Check if batch relationships are valid
print("\n=== CHECKING BATCH RELATIONSHIPS ===")
cursor.execute("""
    SELECT c.id, c.batch_id, b.id as actual_batch_id, b.batch_name
    FROM inventory_consumption c
    LEFT JOIN inventory_batches b ON c.batch_id = b.id
""")
relationships = cursor.fetchall()
for r in relationships:
    status = "✅ OK" if r[1] == r[2] else "❌ BROKEN"
    print(f"  Consumption {r[0]}: batch_id={r[1]}, actual_batch={r[2]} ({r[3]}) - {status}")

conn.close()
print("\n✅ Check complete")
