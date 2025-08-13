"""
Comprehensive Staff Management Database Queries
Supporting all 11 requirements for professional staff management
"""
from sqlalchemy import and_, func, desc
from app import db
from models import User, Role, Department, Appointment, Commission, Attendance, StaffService, Service, StaffPerformance
from datetime import datetime, date, timedelta

def get_all_staff():
    """Get all active staff members with comprehensive data"""
    return User.query.filter_by(is_active=True).order_by(User.first_name).all()

def get_comprehensive_staff():
    """Get all staff with comprehensive information including relationships"""
    return User.query.options(
        db.joinedload(User.user_role),
        db.joinedload(User.staff_department),
        db.joinedload(User.staff_services)
    ).filter_by(is_active=True).order_by(User.first_name).all()

def get_staff_by_id(staff_id):
    """Get staff member by ID with full details"""
    return User.query.options(
        db.joinedload(User.user_role),
        db.joinedload(User.staff_department),
        db.joinedload(User.staff_services)
    ).get(staff_id)

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

def get_active_services():
    """Get all active services"""
    return Service.query.filter_by(is_active=True).order_by(Service.name).all()

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

def get_staff_appointments(staff_id, limit=None):
    """Get appointments for a staff member"""
    query = Appointment.query.filter_by(staff_id=staff_id).order_by(desc(Appointment.appointment_date))
    if limit:
        query = query.limit(limit)
    return query.all()

def get_staff_commissions(staff_id):
    """Get commission data for a staff member"""
    return Commission.query.filter_by(staff_id=staff_id).order_by(desc(Commission.created_at)).all()

def get_staff_stats(staff_id):
    """Get comprehensive statistics for a staff member"""
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # Basic stats
    total_appointments = Appointment.query.filter_by(staff_id=staff_id).count()
    monthly_appointments = Appointment.query.filter(
        Appointment.staff_id == staff_id,
        func.extract('month', Appointment.appointment_date) == current_month,
        func.extract('year', Appointment.appointment_date) == current_year
    ).count()
    
    # Attendance stats
    monthly_attendance = Attendance.query.filter(
        Attendance.staff_id == staff_id,
        func.extract('month', Attendance.date) == current_month,
        func.extract('year', Attendance.date) == current_year
    ).all()
    
    total_hours = sum([att.total_hours or 0 for att in monthly_attendance])
    
    return {
        'total_appointments': total_appointments,
        'monthly_appointments': monthly_appointments,
        'monthly_hours': total_hours,
        'attendance_days': len(monthly_attendance)
    }

def get_staff_attendance(staff_id, start_date=None, end_date=None):
    """Get attendance records for a staff member"""
    query = Attendance.query.filter_by(staff_id=staff_id)
    
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    
    return query.order_by(desc(Attendance.date)).all()

def get_staff_performance(staff_id, month=None, year=None):
    """Get performance metrics for a staff member"""
    if not month:
        month = datetime.now().month
    if not year:
        year = datetime.now().year
    
    return StaffPerformance.query.filter_by(
        staff_id=staff_id,
        month=month,
        year=year
    ).first()

def create_staff_performance_record(staff_id, month, year, metrics):
    """Create or update staff performance record"""
    performance = StaffPerformance.query.filter_by(
        staff_id=staff_id,
        month=month,
        year=year
    ).first()
    
    if performance:
        for key, value in metrics.items():
            setattr(performance, key, value)
    else:
        performance = StaffPerformance(
            staff_id=staff_id,
            month=month,
            year=year,
            **metrics
        )
        db.session.add(performance)
    
    db.session.commit()
    return performance

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