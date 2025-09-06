"""
Enhanced Billing Engine for Integrated Billing System
Supports services, packages, subscriptions, and inventory items
"""
import json
from datetime import datetime
from app import db
from models import (Customer, Service, CustomerPackage, CustomerPackageSession, 
                   InventoryProduct, EnhancedInvoice, InvoiceItem, InvoicePayment)

class BillingEngine:
    """
    Comprehensive billing calculation engine
    """
    
    @staticmethod
    def calculate_service_billing(client_id, services_data):
        """
        Calculate billing for services with package/subscription integration
        
        services_data: [{'service_id': int, 'appointment_id': int, 'quantity': float}]
        Returns: {'items': [], 'total': float, 'deductions': float}
        """
        client = Customer.query.get(client_id)
        if not client:
            return {'error': 'Client not found'}
        
        invoice_items = []
        total_amount = 0.0
        total_deductions = 0.0
        
        # Get active packages and subscriptions
        active_packages = CustomerPackage.query.filter_by(
            client_id=client_id, 
            is_active=True
        ).all()
        
        for service_data in services_data:
            service = Service.query.get(service_data['service_id'])
            if not service:
                continue
            
            quantity = service_data.get('quantity', 1)
            original_amount = service.price * quantity
            deduction_amount = 0.0
            is_package_deduction = False
            is_subscription_deduction = False
            
            # Check if service can be covered by packages
            for package in active_packages:
                # Check if package has sessions for this service
                package_session = CustomerPackageSession.query.filter_by(
                    client_package_id=package.id,
                    service_id=service.id
                ).first()
                
                if package_session and package_session.sessions_remaining >= quantity:
                    # Deduct from package
                    deduction_amount = original_amount
                    is_package_deduction = True
                    
                    # Update package session
                    package_session.sessions_used += quantity
                    total_deductions += deduction_amount
                    break
            
            # Create invoice item
            final_amount = original_amount - deduction_amount
            total_amount += final_amount
            
            invoice_items.append({
                'item_type': 'service',
                'item_id': service.id,
                'appointment_id': service_data.get('appointment_id'),
                'item_name': service.name,
                'description': f"Service: {service.name}",
                'quantity': quantity,
                'unit_price': service.price,
                'original_amount': original_amount,
                'deduction_amount': deduction_amount,
                'final_amount': final_amount,
                'is_package_deduction': is_package_deduction,
                'is_subscription_deduction': is_subscription_deduction,
                'is_extra_charge': not (is_package_deduction or is_subscription_deduction)
            })
        
        return {
            'items': invoice_items,
            'services_subtotal': total_amount,
            'total_deductions': total_deductions,
            'net_amount': total_amount
        }
    
    @staticmethod
    def calculate_inventory_billing(inventory_items_data):
        """
        Calculate billing for inventory items and reduce stock
        
        inventory_items_data: [{'product_id': int, 'quantity': float}]
        Returns: {'items': [], 'total': float, 'stock_movements': []}
        """
        invoice_items = []
        total_amount = 0.0
        stock_movements = []
        
        for item_data in inventory_items_data:
            product = InventoryProduct.query.get(item_data['product_id'])
            if not product:
                continue
                
            quantity = item_data.get('quantity', 1)
            
            # Check stock availability
            if product.current_stock < quantity:
                return {'error': f'Insufficient stock for {product.name}. Available: {product.current_stock}'}
            
            # Calculate amount
            amount = product.selling_price * quantity
            total_amount += amount
            
            # Create invoice item
            invoice_items.append({
                'item_type': 'inventory',
                'item_id': product.product_id,
                'item_name': product.name,
                'description': f"Product: {product.name}",
                'quantity': quantity,
                'unit_price': product.selling_price,
                'original_amount': amount,
                'deduction_amount': 0.0,
                'final_amount': amount,
                'is_package_deduction': False,
                'is_subscription_deduction': False,
                'is_extra_charge': True
            })
            
            # Record stock movement
            stock_movements.append({
                'product_id': product.product_id,
                'quantity_reduction': quantity,
                'new_stock': product.current_stock - quantity
            })
            
            # Update stock
            product.current_stock -= quantity
        
        return {
            'items': invoice_items,
            'inventory_subtotal': total_amount,
            'stock_movements': stock_movements
        }
    
    @staticmethod
    def create_comprehensive_invoice(client_id, billing_data):
        """
        Create comprehensive invoice with all billing components
        
        billing_data: {
            'services': [...],
            'inventory_items': [...],
            'tax_rate': float,
            'discount_amount': float,
            'tips_amount': float,
            'notes': str
        }
        """
        try:
            # Calculate services billing
            services_result = BillingEngine.calculate_service_billing(
                client_id, 
                billing_data.get('services', [])
            )
            
            if 'error' in services_result:
                return services_result
            
            # Calculate inventory billing
            inventory_result = BillingEngine.calculate_inventory_billing(
                billing_data.get('inventory_items', [])
            )
            
            if 'error' in inventory_result:
                return inventory_result
            
            # Combine all items
            all_items = services_result['items'] + inventory_result['items']
            
            # Calculate totals
            services_subtotal = services_result.get('services_subtotal', 0.0)
            inventory_subtotal = inventory_result.get('inventory_subtotal', 0.0)
            total_deductions = services_result.get('total_deductions', 0.0)
            
            gross_subtotal = services_subtotal + inventory_subtotal + total_deductions
            net_subtotal = services_subtotal + inventory_subtotal
            
            # Apply tax and discounts
            tax_rate = billing_data.get('tax_rate', 0.18)  # 18% GST
            discount_amount = billing_data.get('discount_amount', 0.0)
            tips_amount = billing_data.get('tips_amount', 0.0)
            
            tax_amount = (net_subtotal - discount_amount) * tax_rate
            total_amount = net_subtotal + tax_amount - discount_amount + tips_amount
            
            # Generate invoice number
            invoice_count = EnhancedInvoice.query.count() + 1
            invoice_number = f"INV-{datetime.now().strftime('%Y%m')}-{invoice_count:04d}"
            
            # Create invoice
            invoice = EnhancedInvoice(
                invoice_number=invoice_number,
                client_id=client_id,
                services_subtotal=services_subtotal,
                packages_deduction=total_deductions,
                inventory_subtotal=inventory_subtotal,
                gross_subtotal=gross_subtotal,
                total_deductions=total_deductions,
                net_subtotal=net_subtotal,
                tax_amount=tax_amount,
                discount_amount=discount_amount,
                tips_amount=tips_amount,
                total_amount=total_amount,
                balance_due=total_amount,
                notes=billing_data.get('notes', '')
            )
            
            db.session.add(invoice)
            db.session.flush()  # Get invoice ID
            
            # Create invoice items
            for item_data in all_items:
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    **item_data
                )
                db.session.add(item)
            
            db.session.commit()
            
            return {
                'success': True,
                'invoice': invoice,
                'message': f'Invoice {invoice_number} created successfully',
                'total_amount': total_amount,
                'deductions_applied': total_deductions
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to create invoice: {str(e)}'}