"""
Customers-related database queries
"""
from sqlalchemy import or_, func
from app import db
from models import Client, Customer, Appointment, Communication

def get_all_customers():
    """Get all active customers"""
    try:
        return Client.query.filter_by(is_active=True).order_by(Client.name).all()
    except Exception as e:
        # Fallback if name column doesn't exist
        print(f"Error in get_all_customers: {e}")
        return Client.query.filter_by(is_active=True).all()

def get_customer_by_id(customer_id):
    """Get customer by ID"""
    return Client.query.get(customer_id)

def get_customer_by_phone(phone):
    """Get customer by phone number"""
    return Client.query.filter_by(phone=phone, is_active=True).first()

def get_customer_by_email(email):
    """Get customer by email address - deprecated in simplified model"""
    return None

def search_customers(query):
    """Search customers by name or phone"""
    try:
        return Client.query.filter(
            Client.is_active == True,
            or_(
                Client.name.ilike(f'%{query}%'),
                Client.phone.ilike(f'%{query}%')
            )
        ).order_by(Client.name).all()
    except Exception as e:
        # Fallback if name column doesn't exist
        print(f"Error in search_customers: {e}")
        return Client.query.filter(
            Client.is_active == True,
            Client.phone.ilike(f'%{query}%')
        ).all()

def create_customer(customer_data):
    """Create a new customer"""
    try:
        # Ensure name field is populated from first_name and last_name if provided
        if 'first_name' in customer_data and 'last_name' in customer_data:
            first_name = customer_data.get('first_name', '').strip()
            last_name = customer_data.get('last_name', '').strip()
            customer_data['name'] = f"{first_name} {last_name}".strip()
        elif 'name' not in customer_data or not customer_data['name']:
            # Fallback name generation
            customer_data['name'] = customer_data.get('first_name', 'New Client')
        
        customer = Client(**customer_data)
        db.session.add(customer)
        db.session.commit()
        return customer
    except Exception as e:
        db.session.rollback()
        raise e

def update_customer(customer_id, customer_data):
    """Update an existing customer"""
    try:
        customer = Client.query.get(customer_id)
        if customer:
            # Ensure name field is populated from first_name and last_name if provided
            if 'first_name' in customer_data and 'last_name' in customer_data:
                first_name = customer_data.get('first_name', '').strip()
                last_name = customer_data.get('last_name', '').strip()
                customer_data['name'] = f"{first_name} {last_name}".strip()
            
            for key, value in customer_data.items():
                setattr(customer, key, value)
            db.session.commit()
            return customer
        return None
    except Exception as e:
        db.session.rollback()
        raise e

def delete_customer(customer_id):
    """Soft delete a customer"""
    try:
        customer = Client.query.get(customer_id)
        if customer:
            customer.is_active = False
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting customer {customer_id}: {e}")
        return False

def get_customer_appointments(customer_id):
    """Get appointments for a customer"""
    return Appointment.query.filter_by(client_id=customer_id).order_by(Appointment.appointment_date.desc()).all()

def get_customer_communications(customer_id):
    """Get communications for a customer"""
    return Communication.query.filter_by(client_id=customer_id).order_by(Communication.created_at.desc()).all()

def get_customer_stats(customer_id):
    """Get customer statistics"""
    customer = Client.query.get(customer_id)
    if not customer:
        return None
    
    total_appointments = Appointment.query.filter_by(client_id=customer_id).count()
    total_spent = db.session.query(func.sum(Appointment.amount)).filter(
        Appointment.client_id == customer_id,
        Appointment.is_paid == True
    ).scalar() or 0
    
    return {
        'total_appointments': total_appointments,
        'total_spent': total_spent,
        'last_visit': None,  # Simplified client model doesn't track last_visit
        'member_since': customer.created_at
    }

# Backward compatibility aliases
get_all_clients = get_all_customers
get_client_by_id = get_customer_by_id
search_clients = search_customers
create_client = create_customer
update_client = update_customer
delete_client = delete_customer
get_client_appointments = get_customer_appointments
get_client_communications = get_customer_communications
get_client_stats = get_customer_stats