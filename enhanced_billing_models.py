"""
Enhanced Billing Models for Integrated Billing System
Supports services, packages, subscriptions, and inventory items
"""
from datetime import datetime, date
from app import db

# Enhanced Invoice Model for Integrated Billing
class EnhancedInvoice(db.Model):
    """
    Comprehensive invoice model supporting:
    - Direct service billing
    - Package session deductions
    - Subscription billing (count-based and unlimited)
    - Inventory item sales
    - Multiple payment methods
    """
    __tablename__ = 'enhanced_invoice'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(20), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    invoice_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    
    # Billing Components
    services_subtotal = db.Column(db.Float, default=0.0)
    packages_deduction = db.Column(db.Float, default=0.0)
    subscription_deduction = db.Column(db.Float, default=0.0)
    inventory_subtotal = db.Column(db.Float, default=0.0)
    
    # Calculations
    gross_subtotal = db.Column(db.Float, default=0.0)  # Before deductions
    total_deductions = db.Column(db.Float, default=0.0)  # Package + Subscription
    net_subtotal = db.Column(db.Float, default=0.0)  # After deductions
    
    # Final amounts
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    tips_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Payment tracking
    payment_status = db.Column(db.String(20), default='pending')  # pending, partial, paid, overdue
    payment_methods = db.Column(db.Text)  # JSON for multiple payment methods
    amount_paid = db.Column(db.Float, default=0.0)
    balance_due = db.Column(db.Float, default=0.0)
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer', backref='enhanced_invoices')
    invoice_items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')
    invoice_payments = db.relationship('InvoicePayment', backref='invoice', lazy=True, cascade='all, delete-orphan')

class InvoiceItem(db.Model):
    """
    Individual items on an invoice (services, inventory items, etc.)
    """
    __tablename__ = 'invoice_item'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('enhanced_invoice.id'), nullable=False)
    
    # Item details
    item_type = db.Column(db.String(20), nullable=False)  # service, package_service, inventory, subscription
    item_id = db.Column(db.Integer)  # ID of service/inventory item
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))  # For service items
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))  # For package-related items
    
    # Descriptions
    item_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Pricing
    quantity = db.Column(db.Float, default=1.0)
    unit_price = db.Column(db.Float, default=0.0)
    original_amount = db.Column(db.Float, default=0.0)  # Before any deductions
    deduction_amount = db.Column(db.Float, default=0.0)  # Package/subscription deduction
    final_amount = db.Column(db.Float, default=0.0)  # Amount actually charged
    
    # Status indicators
    is_package_deduction = db.Column(db.Boolean, default=False)
    is_subscription_deduction = db.Column(db.Boolean, default=False)
    is_extra_charge = db.Column(db.Boolean, default=False)  # Beyond package/subscription
    
    # Relationships
    appointment = db.relationship('Appointment', backref='invoice_items')
    package = db.relationship('Package', backref='invoice_items')

class InvoicePayment(db.Model):
    """
    Multiple payment records for a single invoice
    Supports mixed payment methods
    """
    __tablename__ = 'invoice_payment'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('enhanced_invoice.id'), nullable=False)
    
    payment_method = db.Column(db.String(20), nullable=False)  # cash, card, upi, wallet
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Payment method specific details
    card_last4 = db.Column(db.String(4))  # Last 4 digits of card
    transaction_id = db.Column(db.String(100))  # UPI/online transaction ID
    reference_number = db.Column(db.String(100))
    
    notes = db.Column(db.Text)
    processed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    processor = db.relationship('User', backref='processed_payments')

# Enhanced Billing Engine Functions
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
        from models import Customer, Service, CustomerPackage, CustomerPackageSession
        
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
        from models import InventoryProduct
        
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
        from models import db
        
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