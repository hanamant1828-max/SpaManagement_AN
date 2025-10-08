#!/usr/bin/env python3
import sqlite3
import os

# Connect to the SQLite database
db_path = os.path.join(os.getcwd(), 'hanamantdatabase', 'workspace.db')
print(f"Checking database: {db_path}")

if not os.path.exists(db_path):
    print("Database file does not exist!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List all inventory tables
print("\n=== INVENTORY TABLES ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'inventory%' ORDER BY name")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

# Check counts for each inventory table
print("\n=== TABLE COUNTS ===")
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"  {table_name}: {count} records")

# Check inventory products
print("\n=== INVENTORY PRODUCTS (first 10) ===")
cursor.execute("SELECT id, sku, name, category_id FROM inventory_products LIMIT 10")
products = cursor.fetchall()
for p in products:
    print(f"  ID: {p[0]}, SKU: {p[1]}, Name: {p[2]}, Category: {p[3]}")

# Check inventory categories
print("\n=== INVENTORY CATEGORIES ===")
cursor.execute("SELECT id, name, type FROM inventory_categories")
categories = cursor.fetchall()
for c in categories:
    print(f"  ID: {c[0]}, Name: {c[1]}, Type: {c[2]}")

# Check inventory locations
print("\n=== INVENTORY LOCATIONS ===")
cursor.execute("SELECT id, name, type FROM inventory_locations")
locations = cursor.fetchall()
for loc in locations:
    print(f"  ID: {loc[0]}, Name: {loc[1]}, Type: {loc[2]}")

# Check inventory batches
print("\n=== INVENTORY BATCHES (first 10) ===")
cursor.execute("SELECT id, batch_name, product_id, location_id, qty_available FROM inventory_batches LIMIT 10")
batches = cursor.fetchall()
for b in batches:
    print(f"  ID: {b[0]}, Batch: {b[1]}, Product: {b[2]}, Location: {b[3]}, Qty: {b[4]}")

conn.close()
print("\n✅ Database check complete")
