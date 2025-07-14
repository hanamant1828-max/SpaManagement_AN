"""
Clients-related database queries
"""
from sqlalchemy import or_, func
from app import db
from models import Client, Appointment, Communication

def get_all_clients():
    """Get all active clients"""
    return Client.query.filter_by(is_active=True).order_by(Client.first_name).all()

def get_client_by_id(client_id):
    """Get client by ID"""
    return Client.query.get(client_id)

def search_clients(query):
    """Search clients by name, phone, or email"""
    return Client.query.filter(
        Client.is_active == True,
        or_(
            Client.first_name.ilike(f'%{query}%'),
            Client.last_name.ilike(f'%{query}%'),
            Client.phone.ilike(f'%{query}%'),
            Client.email.ilike(f'%{query}%')
        )
    ).order_by(Client.first_name).all()

def create_client(client_data):
    """Create a new client"""
    client = Client(**client_data)
    db.session.add(client)
    db.session.commit()
    return client

def update_client(client_id, client_data):
    """Update an existing client"""
    client = Client.query.get(client_id)
    if client:
        for key, value in client_data.items():
            setattr(client, key, value)
        db.session.commit()
    return client

def delete_client(client_id):
    """Soft delete a client"""
    client = Client.query.get(client_id)
    if client:
        client.is_active = False
        db.session.commit()
        return True
    return False

def get_client_appointments(client_id):
    """Get appointments for a client"""
    return Appointment.query.filter_by(client_id=client_id).order_by(Appointment.appointment_date.desc()).all()

def get_client_communications(client_id):
    """Get communications for a client"""
    return Communication.query.filter_by(client_id=client_id).order_by(Communication.created_at.desc()).all()

def get_client_stats(client_id):
    """Get client statistics"""
    client = Client.query.get(client_id)
    if not client:
        return None
    
    total_appointments = Appointment.query.filter_by(client_id=client_id).count()
    total_spent = db.session.query(func.sum(Appointment.amount)).filter(
        Appointment.client_id == client_id,
        Appointment.is_paid == True
    ).scalar() or 0
    
    return {
        'total_appointments': total_appointments,
        'total_spent': total_spent,
        'last_visit': client.last_visit,
        'member_since': client.created_at
    }