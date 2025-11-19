"""
Customers-related database queries
"""
from sqlalchemy import or_, func
from app import db
from models import Customer, Appointment, Communication

def get_all_customers():
    """Get all active customers"""
    return Customer.query.filter_by(is_active=True).order_by(Customer.first_name).all()

def get_customer_by_id(customer_id):
    """Get customer by ID"""
    return Customer.query.get(customer_id)

def get_customer_by_phone(phone):
    """Get customer by phone number"""
    return Customer.query.filter_by(phone=phone, is_active=True).first()

def get_customer_by_email(email):
    """Get customer by email address"""
    if email and email.strip():
        return Customer.query.filter_by(email=email, is_active=True).first()
    return None

def search_customers(query):
    """Search customers by name, phone, or email"""
    return Customer.query.filter(
        Customer.is_active == True,
        or_(
            Customer.first_name.ilike(f'%{query}%'),
            Customer.last_name.ilike(f'%{query}%'),
            Customer.phone.ilike(f'%{query}%'),
            Customer.email.ilike(f'%{query}%')
        )
    ).order_by(Customer.first_name).all()

def create_customer(customer_data):
    """Create a new customer"""
    try:
        customer = Customer(**customer_data)
        db.session.add(customer)
        db.session.commit()
        return customer
    except Exception as e:
        db.session.rollback()
        raise e

def update_customer(customer_id, customer_data):
    """Update an existing customer"""
    try:
        customer = Customer.query.get(customer_id)
        if customer:
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
    from models import Customer
    try:
        customer = Customer.query.get(customer_id)
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
    customer = Customer.query.get(customer_id)
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
        'last_visit': customer.last_visit,
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