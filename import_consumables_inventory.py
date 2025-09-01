
#!/usr/bin/env python3
"""
Import consumables inventory from Excel/CSV data
"""
import sqlite3
import pandas as pd
from datetime import date, timedelta
import uuid

def generate_sku(name):
    """Generate a unique SKU from item name"""
    prefix = ''.join([word[0].upper() for word in name.split()[:3]])
    suffix = str(uuid.uuid4())[:6].upper()
    return f"{prefix}-{suffix}"

def import_consumables_from_excel():
    """Import consumables from Excel file"""
    
    try:
        # Try to read the Excel file
        df = pd.read_excel('attached_assets/Unaki_consumables Inventory_1756718419258.xlsx')
        
        print("📊 Excel file loaded successfully!")
        print(f"Columns found: {list(df.columns)}")
        print(f"Total rows: {len(df)}")
        
        # Connect to database
        db_path = 'instance/spa_management.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔄 Processing inventory items...")
        
        imported_count = 0
        
        for index, row in df.iterrows():
            try:
                # Adapt these column names based on your Excel structure
                # Common column names to look for:
                item_name = None
                quantity = 0
                unit = 'pcs'
                cost_price = 0.0
                selling_price = 0.0
                category = 'consumables'
                
                # Try different possible column names
                for col in df.columns:
                    col_lower = col.lower()
                    if 'name' in col_lower or 'item' in col_lower or 'product' in col_lower:
                        item_name = str(row[col]) if pd.notna(row[col]) else None
                    elif 'qty' in col_lower or 'quantity' in col_lower or 'stock' in col_lower:
                        quantity = float(row[col]) if pd.notna(row[col]) else 0
                    elif 'unit' in col_lower:
                        unit = str(row[col]) if pd.notna(row[col]) else 'pcs'
                    elif 'cost' in col_lower or 'purchase' in col_lower:
                        cost_price = float(row[col]) if pd.notna(row[col]) else 0.0
                    elif 'price' in col_lower or 'selling' in col_lower or 'retail' in col_lower:
                        selling_price = float(row[col]) if pd.notna(row[col]) else 0.0
                    elif 'category' in col_lower or 'type' in col_lower:
                        category = str(row[col]) if pd.notna(row[col]) else 'consumables'
                
                if not item_name or item_name == 'nan':
                    continue
                
                # Generate SKU
                sku = generate_sku(item_name)
                
                # Insert inventory item
                cursor.execute("""
                    INSERT OR REPLACE INTO inventory (
                        name, sku, description, category, base_unit, selling_unit, 
                        conversion_factor, current_stock, min_stock_level, max_stock_level,
                        cost_price, selling_price, reorder_point, reorder_quantity,
                        has_expiry, supplier_name, is_service_item, 
                        is_retail_item, item_type, tracking_type, is_active, 
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item_name, sku, f"Imported consumable: {item_name}", 
                    category, unit, unit, 1.0, quantity,
                    max(5, quantity * 0.2), max(100, quantity * 2),
                    cost_price, selling_price,
                    max(10, quantity * 0.3), max(50, quantity),
                    False, 'Unaki Supplier', True, True, 'both',
                    'piece_wise', True,
                    date.today().isoformat(), date.today().isoformat()
                ))
                
                imported_count += 1
                print(f"  ✅ Imported: {item_name} - {quantity} {unit}")
                
            except Exception as e:
                print(f"  ❌ Error importing row {index}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Successfully imported {imported_count} consumable items!")
        
    except FileNotFoundError:
        print("❌ Excel file not found. Please ensure the file exists.")
    except ImportError:
        print("❌ pandas and openpyxl required. Installing...")
        import subprocess
        subprocess.run(["pip", "install", "pandas", "openpyxl"])
        print("✅ Dependencies installed. Please run the script again.")
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")

def import_consumables_from_csv():
    """Import consumables from CSV file if Excel conversion was done"""
    
    try:
        df = pd.read_csv('consumables_inventory.csv')
        
        print("📊 CSV file loaded successfully!")
        print(f"Columns: {list(df.columns)}")
        print(f"Rows: {len(df)}")
        
        # Same import logic as Excel version
        import_consumables_from_excel()  # Will work with CSV too
        
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")

def create_sample_consumables():
    """Create sample consumables based on common spa items"""
    
    sample_consumables = [
        {"name": "Disposable Face Towels", "qty": 500, "unit": "pcs", "cost": 0.25, "price": 0.0},
        {"name": "Cotton Pads", "qty": 1000, "unit": "pcs", "cost": 0.10, "price": 0.0},
        {"name": "Latex Gloves (Box)", "qty": 20, "unit": "box", "cost": 15.0, "price": 0.0},
        {"name": "Facial Tissues", "qty": 50, "unit": "box", "cost": 3.0, "price": 0.0},
        {"name": "Sanitizing Wipes", "qty": 30, "unit": "pack", "cost": 4.50, "price": 0.0},
        {"name": "Wooden Spatulas", "qty": 200, "unit": "pcs", "cost": 0.15, "price": 0.0},
        {"name": "Aluminium Foil Sheets", "qty": 500, "unit": "pcs", "cost": 0.05, "price": 0.0},
        {"name": "Headbands", "qty": 100, "unit": "pcs", "cost": 1.50, "price": 3.0},
        {"name": "Shower Caps", "qty": 200, "unit": "pcs", "cost": 0.30, "price": 0.0},
        {"name": "Paper Cups", "qty": 500, "unit": "pcs", "cost": 0.08, "price": 0.0},
    ]
    
    db_path = 'instance/spa_management.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Creating sample consumables...")
    
    for item in sample_consumables:
        sku = generate_sku(item["name"])
        
        cursor.execute("""
            INSERT OR REPLACE INTO inventory (
                name, sku, description, category, base_unit, selling_unit, 
                conversion_factor, current_stock, min_stock_level, max_stock_level,
                cost_price, selling_price, reorder_point, reorder_quantity,
                has_expiry, supplier_name, is_service_item, 
                is_retail_item, item_type, tracking_type, is_active, 
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["name"], sku, f"Sample consumable: {item['name']}", 
            'consumables', item["unit"], item["unit"], 1.0, item["qty"],
            max(5, item["qty"] * 0.2), max(100, item["qty"] * 2),
            item["cost"], item["price"],
            max(10, item["qty"] * 0.3), max(50, item["qty"]),
            False, 'Sample Supplier', True, 
            item["price"] > 0, 'consumable' if item["price"] == 0 else 'both',
            'piece_wise', True,
            date.today().isoformat(), date.today().isoformat()
        ))
        
        print(f"  ✅ Added: {item['name']} - {item['qty']} {item['unit']}")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Sample consumables created!")

if __name__ == "__main__":
    print("🧴 Consumables Inventory Import Tool")
    print("=" * 50)
    
    choice = input("""
Choose import method:
1. Import from Excel file (auto-detect columns)
2. Import from CSV file (if converted)
3. Create sample consumables
4. Show Excel file structure first

Enter choice (1-4): """).strip()
    
    if choice == "1":
        import_consumables_from_excel()
    elif choice == "2":
        import_consumables_from_csv()
    elif choice == "3":
        create_sample_consumables()
    elif choice == "4":
        try:
            df = pd.read_excel('attached_assets/Unaki_consumables Inventory_1756718419258.xlsx')
            print(f"\n📊 Excel File Structure:")
            print(f"Columns: {list(df.columns)}")
            print(f"Shape: {df.shape}")
            print(f"\nFirst 5 rows:")
            print(df.head())
            print(f"\nData types:")
            print(df.dtypes)
        except Exception as e:
            print(f"❌ Error reading Excel: {e}")
    else:
        print("Invalid choice!")
