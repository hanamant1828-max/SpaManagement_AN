"""
Comprehensive Staff Management Database Queries
Supporting all 11 requirements for professional staff management
"""
from sqlalchemy import and_, func, desc, or_
from app import db
from models import User, Role, Department, Appointment, Commission, Attendance, StaffService, Service, StaffPerformance
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash

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
    try:
        return Role.query.filter_by(is_active=True).all()
    except Exception as e:
        print(f"Error getting active roles: {e}")
        return []

def get_active_departments():
    """Get all active departments"""
    try:
        return Department.query.filter_by(is_active=True).all()
    except Exception as e:
        print(f"Error getting active departments: {e}")
        return []

def get_active_services():
    """Get all active services"""
    try:
        return Service.query.filter_by(is_active=True).all()
    except Exception as e:
        print(f"Error getting active services: {e}")
        return []

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

def get_staff_performance_data(staff_id):
    """Get performance data for specific staff member"""
    try:
        from models import Commission, Appointment

        # Get commission data
        commissions = Commission.query.filter_by(staff_id=staff_id).order_by(Commission.pay_period_start.desc()).all()

        # Get appointment data
        appointments = Appointment.query.filter_by(staff_id=staff_id).order_by(Appointment.appointment_date.desc()).limit(20).all()

        return {
            'commissions': commissions,
            'appointments': appointments,
            'total_commission': sum(c.commission_amount for c in commissions if c.commission_amount),
            'total_services': len(appointments)
        }
    except Exception as e:
        print(f"Error getting staff performance data: {e}")
        return {
            'commissions': [],
            'appointments': [],
            'total_commission': 0,
            'total_services': 0
        }

def get_comprehensive_staff():
    """Get all staff with comprehensive information"""
    try:
        staff = User.query.filter(User.role.in_(['staff', 'manager', 'admin'])).all()
        return staff
    except Exception as e:
        print(f"Error getting comprehensive staff: {e}")
        return []

def get_active_roles():
    """Get all active roles"""
    try:
        return Role.query.filter_by(is_active=True).all()
    except Exception as e:
        print(f"Error getting active roles: {e}")
        return []

def get_active_departments():
    """Get all active departments"""
    try:
        return Department.query.filter_by(is_active=True).all()
    except Exception as e:
        print(f"Error getting active departments: {e}")
        return []

def get_active_services():
    """Get all active services"""
    try:
        return Service.query.filter_by(is_active=True).all()
    except Exception as e:
        print(f"Error getting active services: {e}")
        return []

def create_comprehensive_staff_member(form):
    """Create a comprehensive staff member from form data"""
    try:
        from werkzeug.security import generate_password_hash

        # Generate working days string
        working_days = ''
        working_days += '1' if form.monday.data else '0'
        working_days += '1' if form.tuesday.data else '0'
        working_days += '1' if form.wednesday.data else '0'
        working_days += '1' if form.thursday.data else '0'
        working_days += '1' if form.friday.data else '0'
        working_days += '1' if form.saturday.data else '0'
        working_days += '1' if form.sunday.data else '0'

        # Create new staff member
        staff_data = {
            'username': form.username.data,
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'gender': form.gender.data,
            'date_of_birth': form.date_of_birth.data,
            'date_of_joining': form.date_of_joining.data or datetime.now().date(),
            'designation': form.designation.data,
            'staff_code': form.staff_code.data,
            'notes_bio': form.notes_bio.data,
            'aadhaar_number': form.aadhaar_number.data,
            'pan_number': form.pan_number.data,
            'verification_status': form.verification_status.data,
            'shift_start_time': form.shift_start_time.data,
            'shift_end_time': form.shift_end_time.data,
            'break_time': form.break_time.data,
            'weekly_off_days': form.weekly_off_days.data,
            'working_days': working_days,
            'commission_percentage': form.commission_percentage.data or 0.0,
            'fixed_commission': form.fixed_commission.data or 0.0,
            'hourly_rate': form.hourly_rate.data or 0.0,
            'enable_face_checkin': form.enable_face_checkin.data,
            'role_id': form.role_id.data if form.role_id.data != 0 else None,
            'department_id': form.department_id.data if form.department_id.data != 0 else None,
            'is_active': form.is_active.data,
            'role': 'staff'
        }

        if form.password.data:
            staff_data['password_hash'] = generate_password_hash(form.password.data)

        # Create staff member
        new_staff = User(**staff_data)
        db.session.add(new_staff)
        db.session.flush()  # Get the ID

        # Assign services
        for service_id in form.assigned_services.data:
            staff_service = StaffService(
                staff_id=new_staff.id,
                service_id=service_id,
                skill_level='beginner'
            )
            db.session.add(staff_service)

        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Error creating comprehensive staff member: {e}")
        return False