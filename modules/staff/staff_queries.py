"""
Staff-related database queries
"""
from sqlalchemy import and_, func
from app import db
from models import User, Role, Department, Appointment, Commission

def get_all_staff():
    """Get all active staff members"""
    return User.query.filter_by(is_active=True).order_by(User.first_name).all()

def get_staff_by_id(staff_id):
    """Get staff member by ID"""
    return User.query.get(staff_id)

def get_staff_by_role(role_name):
    """Get staff members by role"""
    return User.query.filter(
        User.role == role_name,
        User.is_active == True
    ).order_by(User.first_name).all()

def get_active_roles():
    """Get all active roles"""
    return Role.query.filter_by(is_active=True).order_by(Role.display_name).all()

def get_active_departments():
    """Get all active departments"""
    return Department.query.filter_by(is_active=True).order_by(Department.display_name).all()

def create_staff(staff_data):
    """Create a new staff member"""
    staff = User(**staff_data)
    db.session.add(staff)
    db.session.commit()
    return staff

def update_staff(staff_id, staff_data):
    """Update an existing staff member"""
    staff = User.query.get(staff_id)
    if staff:
        for key, value in staff_data.items():
            setattr(staff, key, value)
        db.session.commit()
    return staff

def delete_staff(staff_id):
    """Soft delete a staff member"""
    staff = User.query.get(staff_id)
    if staff:
        staff.is_active = False
        db.session.commit()
        return True
    return False

def get_staff_appointments(staff_id):
    """Get appointments for a staff member"""
    return Appointment.query.filter_by(staff_id=staff_id).order_by(Appointment.appointment_date.desc()).all()

def get_staff_commissions(staff_id):
    """Get commissions for a staff member"""
    return Commission.query.filter_by(staff_id=staff_id).order_by(Commission.created_at.desc()).all()

def get_staff_stats(staff_id):
    """Get staff statistics"""
    staff = User.query.get(staff_id)
    if not staff:
        return None
    
    total_appointments = Appointment.query.filter_by(staff_id=staff_id).count()
    total_revenue = db.session.query(func.sum(Appointment.amount)).filter(
        Appointment.staff_id == staff_id,
        Appointment.is_paid == True
    ).scalar() or 0
    
    return {
        'total_appointments': total_appointments,
        'total_revenue': total_revenue,
        'total_clients_served': staff.total_clients_served,
        'average_rating': staff.average_rating
    }