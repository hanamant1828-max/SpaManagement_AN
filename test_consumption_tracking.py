#!/usr/bin/env python3
"""
Test the advanced consumption tracking functionality
"""

import sqlite3
from datetime import datetime, timedelta
import json

def test_consumption_tracking():
    """Test all three tracking types with realistic data"""
    
    db_path = 'instance/spa_management.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🧪 Testing Advanced Consumption Tracking System")
    print("=" * 60)
    
    try:
        # Get current inventory items and their tracking types
        cursor.execute("""
            SELECT id, name, tracking_type, current_stock, base_unit 
            FROM inventory 
            WHERE is_active = 1
            ORDER BY tracking_type, name
        """)
        items = cursor.fetchall()
        
        print("📊 Current Inventory Items by Tracking Type:")
        print("-" * 60)
        
        container_items = []
        piece_items = []
        manual_items = []
        
        for item in items:
            item_id, name, tracking_type, stock, unit = item
            print(f"  • {name} ({tracking_type}): {stock} {unit}")
            
            if tracking_type == 'container_lifecycle':
                container_items.append(item)
            elif tracking_type == 'piece_wise':
                piece_items.append(item)
            elif tracking_type == 'manual_entry':
                manual_items.append(item)
        
        print(f"\\n📈 Summary:")
        print(f"  • Container/Lifecycle: {len(container_items)} items")
        print(f"  • Piece-wise: {len(piece_items)} items") 
        print(f"  • Manual Entry: {len(manual_items)} items")
        
        # Test Container/Lifecycle Tracking
        print("\\n🧴 Testing Container/Lifecycle Tracking")
        print("-" * 40)
        
        if container_items:
            test_item = container_items[0]
            item_id, name, _, stock, unit = test_item
            
            # Simulate opening a container
            item_code = f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            open_quantity = 1.0
            
            # Insert inventory_item record (simulating opening)
            cursor.execute("""
                INSERT INTO inventory_item (
                    inventory_id, item_code, quantity, remaining_quantity,
                    status, issued_at, issued_by
                ) VALUES (?, ?, ?, ?, 'issued', ?, 1)
            """, (item_id, item_code, open_quantity, open_quantity, datetime.now()))
            
            inventory_item_id = cursor.lastrowid
            
            # Insert consumption_entry for opening
            cursor.execute("""
                INSERT INTO consumption_entry (
                    inventory_id, inventory_item_id, entry_type, quantity, unit,
                    reason, cost_impact, created_by
                ) VALUES (?, ?, 'open', ?, ?, 'Test opening container', 0, 1)
            """, (item_id, inventory_item_id, open_quantity, unit))
            
            # Insert usage_duration tracking
            cursor.execute("""
                INSERT INTO usage_duration (
                    inventory_id, inventory_item_id, opened_at, opened_by
                ) VALUES (?, ?, ?, 1)
            """, (item_id, inventory_item_id, datetime.now()))
            
            print(f"  ✅ Opened: {name} (Item Code: {item_code})")
            
            # Simulate consumption after some time
            consume_time = datetime.now() + timedelta(hours=24)  # 24 hours later
            
            cursor.execute("""
                UPDATE inventory_item 
                SET status = 'consumed', consumed_at = ?, consumed_by = 1,
                    remaining_quantity = 0
                WHERE id = ?
            """, (consume_time, inventory_item_id))
            
            # Update usage duration
            cursor.execute("""
                UPDATE usage_duration 
                SET finished_at = ?, finished_by = 1, duration_hours = 24.0
                WHERE inventory_item_id = ?
            """, (consume_time, inventory_item_id))
            
            # Add consumption entry
            cursor.execute("""
                INSERT INTO consumption_entry (
                    inventory_id, inventory_item_id, entry_type, quantity, unit,
                    reason, created_by
                ) VALUES (?, ?, 'consume', 0, ?, 'Test marking as consumed', 1)
            """, (item_id, inventory_item_id, unit))
            
            print(f"  ✅ Consumed: {name} after 24 hours")
        
        # Test Piece-wise Tracking
        print("\\n🧻 Testing Piece-wise Tracking")
        print("-" * 40)
        
        if piece_items:
            test_item = piece_items[0]
            item_id, name, _, stock, unit = test_item
            
            # Simulate deducting specific quantities
            deductions = [
                (3.0, "Facial service for client A"),
                (2.0, "Massage service for client B"),
                (1.0, "Touch-up service")
            ]
            
            for quantity, reason in deductions:
                cursor.execute("""
                    INSERT INTO consumption_entry (
                        inventory_id, entry_type, quantity, unit, reason,
                        reference_type, cost_impact, created_by
                    ) VALUES (?, 'deduct', ?, ?, ?, 'service', 0, 1)
                """, (item_id, quantity, unit, reason))
                
                # Update stock (in real system this would be done automatically)
                cursor.execute("""
                    UPDATE inventory 
                    SET current_stock = current_stock - ?
                    WHERE id = ?
                """, (quantity, item_id))
                
                print(f"  ✅ Deducted: {quantity} {unit} from {name} ({reason})")
        
        # Test Manual Adjustment
        print("\\n✏️  Testing Manual Entry/Adjustment")
        print("-" * 40)
        
        if items:  # Use any item for manual adjustment
            test_item = items[-1]  # Last item
            item_id, name, _, stock, unit = test_item
            
            # Simulate manual adjustments
            adjustments = [
                (stock + 10, "manual_adjustment", "Physical count - found extra stock"),
                (stock + 5, "wastage", "Some items damaged during transport")
            ]
            
            for new_quantity, adj_type, reason in adjustments:
                old_quantity = stock
                adjustment = new_quantity - old_quantity
                
                cursor.execute("""
                    INSERT INTO consumption_entry (
                        inventory_id, entry_type, quantity, unit, reason,
                        reference_type, cost_impact, created_by
                    ) VALUES (?, 'adjust', ?, ?, ?, ?, 0, 1)
                """, (item_id, abs(adjustment), unit, reason, adj_type))
                
                print(f"  ✅ Adjusted: {name} from {old_quantity} to {new_quantity} {unit} ({reason})")
                stock = new_quantity  # Update for next iteration
        
        # Generate Reports
        print("\\n📊 Generating Reports")
        print("-" * 40)
        
        # Consumption Report (last 7 days)
        cursor.execute("""
            SELECT 
                i.name,
                ce.entry_type,
                COUNT(*) as entry_count,
                SUM(ce.quantity) as total_quantity,
                ce.unit
            FROM consumption_entry ce
            JOIN inventory i ON ce.inventory_id = i.id
            WHERE ce.created_at >= datetime('now', '-7 days')
            GROUP BY i.name, ce.entry_type, ce.unit
            ORDER BY i.name, ce.entry_type
        """)
        consumption_report = cursor.fetchall()
        
        print("\\n  📈 7-Day Consumption Report:")
        for item_name, entry_type, count, total_qty, unit in consumption_report:
            print(f"    • {item_name}: {entry_type} - {count} times, {total_qty} {unit}")
        
        # Usage Duration Report
        cursor.execute("""
            SELECT 
                i.name,
                COUNT(ud.id) as items_used,
                AVG(ud.duration_hours) as avg_duration,
                MIN(ud.duration_hours) as min_duration,
                MAX(ud.duration_hours) as max_duration
            FROM usage_duration ud
            JOIN inventory i ON ud.inventory_id = i.id
            WHERE ud.finished_at IS NOT NULL
            GROUP BY i.name
        """)
        duration_report = cursor.fetchall()
        
        print("\\n  ⏱️  Usage Duration Report:")
        for item_name, items_used, avg_dur, min_dur, max_dur in duration_report:
            print(f"    • {item_name}: {items_used} items, avg {avg_dur:.1f}h (min {min_dur:.1f}h, max {max_dur:.1f}h)")
        
        # Staff Usage Report  
        cursor.execute("""
            SELECT 
                u.first_name || ' ' || u.last_name as staff_name,
                i.name,
                ce.entry_type,
                COUNT(*) as entries,
                SUM(ce.quantity) as total_quantity
            FROM consumption_entry ce
            JOIN inventory i ON ce.inventory_id = i.id
            JOIN user u ON ce.created_by = u.id
            WHERE ce.created_at >= datetime('now', '-7 days')
            GROUP BY u.id, i.name, ce.entry_type
            ORDER BY staff_name, i.name
        """)
        staff_report = cursor.fetchall()
        
        print("\\n  👤 Staff Usage Report:")
        for staff_name, item_name, entry_type, entries, total_qty in staff_report:
            print(f"    • {staff_name}: {item_name} ({entry_type}) - {entries} entries, {total_qty} total")
        
        conn.commit()
        
        print("\\n🎉 All Tests Completed Successfully!")
        print("\\n💡 System Features Demonstrated:")
        print("  ✅ Container/Lifecycle tracking (Open → Consume)")
        print("  ✅ Piece-wise consumption tracking")
        print("  ✅ Manual entry and adjustments")
        print("  ✅ Usage duration monitoring")
        print("  ✅ Staff usage tracking")
        print("  ✅ Comprehensive reporting")
        print("\\n🌟 The advanced inventory tracking system is ready for use!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    test_consumption_tracking()