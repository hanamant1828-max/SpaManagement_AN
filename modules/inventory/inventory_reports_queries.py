"""
Inventory Reports Database Queries
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_, desc, case
from app import db
from modules.inventory.models import (
    InventoryProduct, InventoryBatch, InventoryLocation, 
    InventoryCategory, InventoryConsumption, InventoryAdjustment,
    InventoryTransfer, InventoryAuditLog
)

def get_stock_summary_report():
    """Get overall stock summary"""
    try:
        products = InventoryProduct.query.filter_by(is_active=True).all()
        
        total_products = len(products)
        total_stock_value = 0
        total_batches = 0
        
        for product in products:
            for batch in product.batches:
                if batch.status == 'active' and batch.qty_available:
                    total_batches += 1
                    total_stock_value += float(batch.qty_available) * float(batch.unit_cost or 0)
        
        return {
            'total_products': total_products,
            'total_batches': total_batches,
            'total_stock_value': total_stock_value
        }
    except Exception as e:
        print(f"Error in get_stock_summary_report: {e}")
        return {'total_products': 0, 'total_batches': 0, 'total_stock_value': 0}

def get_stock_level_report():
    """Get stock levels by product"""
    try:
        products = InventoryProduct.query.filter_by(is_active=True).all()
        
        stock_data = []
        for product in products:
            total_stock = product.total_stock
            batch_count = product.batch_count
            
            stock_value = 0
            for batch in product.batches:
                if batch.status == 'active' and batch.qty_available:
                    stock_value += float(batch.qty_available) * float(batch.unit_cost or 0)
            
            stock_data.append({
                'product_id': product.id,
                'product_name': product.name,
                'sku': product.sku,
                'category': product.category.name if product.category else 'Uncategorized',
                'total_stock': total_stock,
                'batch_count': batch_count,
                'stock_value': stock_value,
                'stock_status': product.stock_status,
                'unit_of_measure': product.unit_of_measure
            })
        
        return sorted(stock_data, key=lambda x: x['stock_value'], reverse=True)
    except Exception as e:
        print(f"Error in get_stock_level_report: {e}")
        return []

def get_expiry_report(days_threshold=30):
    """Get batches expiring within specified days"""
    try:
        threshold_date = date.today() + timedelta(days=days_threshold)
        
        batches = InventoryBatch.query.filter(
            InventoryBatch.status == 'active',
            InventoryBatch.expiry_date <= threshold_date,
            InventoryBatch.qty_available > 0
        ).order_by(InventoryBatch.expiry_date).all()
        
        expiry_data = []
        for batch in batches:
            days_to_expiry = (batch.expiry_date - date.today()).days
            
            expiry_data.append({
                'batch_id': batch.id,
                'batch_name': batch.batch_name,
                'product_name': batch.product.name if batch.product else 'Unassigned',
                'location': batch.location.name if batch.location else 'Unassigned',
                'expiry_date': batch.expiry_date,
                'days_to_expiry': days_to_expiry,
                'quantity': float(batch.qty_available),
                'unit_cost': float(batch.unit_cost or 0),
                'stock_value': float(batch.qty_available) * float(batch.unit_cost or 0),
                'is_expired': days_to_expiry < 0,
                'severity': 'critical' if days_to_expiry < 0 else 'high' if days_to_expiry <= 7 else 'medium'
            })
        
        return expiry_data
    except Exception as e:
        print(f"Error in get_expiry_report: {e}")
        return []

def get_location_wise_report():
    """Get inventory by location"""
    try:
        locations = InventoryLocation.query.filter_by(status='active').all()
        
        location_data = []
        for location in locations:
            total_batches = 0
            total_value = 0
            products_count = set()
            
            for batch in location.batches:
                if batch.status == 'active' and batch.qty_available and batch.qty_available > 0:
                    total_batches += 1
                    if batch.product_id:
                        products_count.add(batch.product_id)
                    total_value += float(batch.qty_available) * float(batch.unit_cost or 0)
            
            location_data.append({
                'location_id': location.id,
                'location_name': location.name,
                'location_type': location.type,
                'total_batches': total_batches,
                'unique_products': len(products_count),
                'total_value': total_value
            })
        
        return sorted(location_data, key=lambda x: x['total_value'], reverse=True)
    except Exception as e:
        print(f"Error in get_location_wise_report: {e}")
        return []

def get_consumption_report(start_date, end_date):
    """Get consumption report for date range"""
    try:
        consumptions = InventoryConsumption.query.filter(
            InventoryConsumption.created_at >= start_date,
            InventoryConsumption.created_at <= end_date
        ).order_by(desc(InventoryConsumption.created_at)).all()
        
        consumption_data = []
        total_value = 0
        
        for consumption in consumptions:
            batch = consumption.batch
            product_name = batch.product.name if batch and batch.product else 'Unknown'
            cost = float(consumption.quantity) * float(batch.unit_cost or 0) if batch else 0
            total_value += cost
            
            consumption_data.append({
                'id': consumption.id,
                'date': consumption.created_at,
                'product_name': product_name,
                'batch_name': batch.batch_name if batch else 'Unknown',
                'quantity': float(consumption.quantity),
                'unit_cost': float(batch.unit_cost or 0) if batch else 0,
                'total_cost': cost,
                'issued_to': consumption.issued_to,
                'purpose': consumption.purpose,
                'created_by': consumption.user.first_name + ' ' + consumption.user.last_name if consumption.user else 'System'
            })
        
        return {
            'data': consumption_data,
            'total_value': total_value,
            'total_items': len(consumption_data)
        }
    except Exception as e:
        print(f"Error in get_consumption_report: {e}")
        return {'data': [], 'total_value': 0, 'total_items': 0}

def get_adjustment_report(start_date, end_date):
    """Get adjustment report for date range"""
    try:
        adjustments = InventoryAdjustment.query.filter(
            InventoryAdjustment.created_at >= start_date,
            InventoryAdjustment.created_at <= end_date
        ).order_by(desc(InventoryAdjustment.created_at)).all()
        
        adjustment_data = []
        total_added = 0
        total_removed = 0
        
        for adjustment in adjustments:
            batch = adjustment.batch
            product_name = batch.product.name if batch and batch.product else 'Unknown'
            quantity = float(adjustment.quantity)
            
            if adjustment.adjustment_type == 'add':
                total_added += quantity
            else:
                total_removed += quantity
            
            adjustment_data.append({
                'id': adjustment.id,
                'date': adjustment.created_at,
                'type': adjustment.adjustment_type,
                'product_name': product_name,
                'batch_name': batch.batch_name if batch else 'Unknown',
                'quantity': quantity,
                'remarks': adjustment.remarks,
                'created_by': adjustment.user.first_name + ' ' + adjustment.user.last_name if adjustment.user else 'System'
            })
        
        return {
            'data': adjustment_data,
            'total_added': total_added,
            'total_removed': total_removed,
            'total_items': len(adjustment_data)
        }
    except Exception as e:
        print(f"Error in get_adjustment_report: {e}")
        return {'data': [], 'total_added': 0, 'total_removed': 0, 'total_items': 0}

def get_category_wise_report():
    """Get inventory summary by category"""
    try:
        categories = InventoryCategory.query.filter_by(is_active=True).all()
        
        category_data = []
        for category in categories:
            total_products = len(category.products)
            total_stock = 0
            total_value = 0
            
            for product in category.products:
                if product.is_active:
                    total_stock += product.total_stock
                    for batch in product.batches:
                        if batch.status == 'active' and batch.qty_available:
                            total_value += float(batch.qty_available) * float(batch.unit_cost or 0)
            
            category_data.append({
                'category_id': category.id,
                'category_name': category.name,
                'total_products': total_products,
                'total_stock': total_stock,
                'total_value': total_value
            })
        
        return sorted(category_data, key=lambda x: x['total_value'], reverse=True)
    except Exception as e:
        print(f"Error in get_category_wise_report: {e}")
        return []

def get_low_stock_report(threshold=10):
    """Get products with low stock"""
    try:
        products = InventoryProduct.query.filter_by(is_active=True).all()
        
        low_stock_data = []
        for product in products:
            total_stock = product.total_stock
            if 0 < total_stock <= threshold:
                low_stock_data.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'sku': product.sku,
                    'category': product.category.name if product.category else 'Uncategorized',
                    'current_stock': total_stock,
                    'batch_count': product.batch_count,
                    'unit_of_measure': product.unit_of_measure
                })
        
        return sorted(low_stock_data, key=lambda x: x['current_stock'])
    except Exception as e:
        print(f"Error in get_low_stock_report: {e}")
        return []

def get_batch_movement_report(start_date, end_date):
    """Get batch movement/audit report"""
    try:
        audit_logs = InventoryAuditLog.query.filter(
            InventoryAuditLog.timestamp >= start_date,
            InventoryAuditLog.timestamp <= end_date
        ).order_by(desc(InventoryAuditLog.timestamp)).all()
        
        movement_data = []
        for log in audit_logs:
            movement_data.append({
                'id': log.id,
                'timestamp': log.timestamp,
                'action_type': log.action_type,
                'product_name': log.product.name if log.product else 'Unknown',
                'batch_name': log.batch.batch_name if log.batch else 'Unknown',
                'quantity_delta': float(log.quantity_delta),
                'stock_before': float(log.stock_before),
                'stock_after': float(log.stock_after),
                'user': log.user.first_name + ' ' + log.user.last_name if log.user else 'System',
                'notes': log.notes
            })
        
        return movement_data
    except Exception as e:
        print(f"Error in get_batch_movement_report: {e}")
        return []
