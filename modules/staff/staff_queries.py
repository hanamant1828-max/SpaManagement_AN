"""
Comprehensive Staff Management Database Queries
Supporting all 11 requirements for professional staff management
"""
from sqlalchemy import and_, func, desc, or_
from app import db
# Import models to avoid NameError issues
from models import (
    User, Role, Department, Service, StaffService,
    Attendance, StaffPerformance,
    Appointment, Commission
)
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
    try:
        staff_member = User.query.get(staff_id)
        if staff_member:
            # Only update fields if they are truly empty and won't cause conflicts
            updated = False
            if not staff_member.staff_code:
                # Generate unique staff code
                existing_codes = set([u.staff_code for u in User.query.filter(User.staff_code.isnot(None)).all()])
                code_num = staff_member.id
                potential_code = f"STF{str(code_num).zfill(3)}"
                while potential_code in existing_codes:
                    code_num += 1
                    potential_code = f"STF{str(code_num).zfill(3)}"
                staff_member.staff_code = potential_code
                updated = True
            if not staff_member.designation:
                staff_member.designation = staff_member.role.title()
                updated = True
            if not staff_member.date_of_joining:
                staff_member.date_of_joining = staff_member.created_at.date() if staff_member.created_at else date.today()
                updated = True

            if updated:
                db.session.commit()
        return staff_member
    except Exception as e:
        print(f"Error getting staff by ID: {e}")
        db.session.rollback()
        return None

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
        departments = Department.query.filter_by(is_active=True).order_by(Department.display_name).all()
        print(f"Found {len(departments)} active departments")
        for dept in departments:
            print(f"  - {dept.name}: {dept.display_name}")
        return departments
    except Exception as e:
        print(f"Error getting active departments: {e}")
        # If no departments exist, create some basic ones
        return create_default_departments()

def create_default_departments():
    """Create default departments if none exist"""
    try:
        from models import Department
        from app import db

        default_depts = [
            {'name': 'spa_services', 'display_name': 'Spa Services', 'description': 'Spa and wellness services'},
            {'name': 'reception', 'display_name': 'Reception', 'description': 'Front desk operations'},
            {'name': 'management', 'display_name': 'Management', 'description': 'Administrative roles'}
        ]

        created_depts = []
        for dept_data in default_depts:
            dept = Department(**dept_data)
            db.session.add(dept)
            created_depts.append(dept)

        db.session.commit()
        print(f"Created {len(created_depts)} default departments")
        return created_depts
    except Exception as e:
        print(f"Error creating default departments: {e}")
        db.session.rollback()
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
    try:
        # Create User object by explicitly setting each field
        staff = User()

        # Set all the fields from staff_data
        for field, value in staff_data.items():
            if hasattr(staff, field):
                setattr(staff, field, value)

        db.session.add(staff)
        db.session.commit()
        return staff

    except Exception as e:
        print(f"Error in create_staff: {e}")
        db.session.rollback()
        raise e

def update_staff(staff_id, staff_data):
    """Update an existing staff member"""
    try:
        staff = User.query.get(staff_id)
        if not staff:
            return None

        # Safely update each field
        for key, value in staff_data.items():
            if hasattr(staff, key):
                setattr(staff, key, value)
            else:
                print(f"Warning: Staff model does not have attribute '{key}'")

        db.session.commit()
        return staff
    except Exception as e:
        print(f"Error updating staff: {e}")
        db.session.rollback()
        return None

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
    """Get all staff with comprehensive details"""
    try:
        # Force fresh query from database
        db.session.expire_all()

        staff_members = User.query.options(
            db.joinedload(User.user_role),
            db.joinedload(User.staff_department),
            db.joinedload(User.staff_services)
        ).filter(
            User.role.in_(['staff', 'manager', 'admin']),
            User.is_active == True
        ).order_by(User.first_name).all()

        # Only update fields that are truly missing, avoid conflicts
        existing_codes = set([u.staff_code for u in User.query.filter(User.staff_code.isnot(None)).all()])

        for member in staff_members:
            try:
                updated = False
                if not member.staff_code:
                    # Generate unique staff code
                    code_num = len(existing_codes) + 1
                    potential_code = f"STF{str(code_num).zfill(3)}"
                    while potential_code in existing_codes:
                        code_num += 1
                        potential_code = f"STF{str(code_num).zfill(3)}"

                    member.staff_code = potential_code
                    existing_codes.add(potential_code)
                    updated = True

                if not member.designation:
                    member.designation = member.role.title()
                    updated = True

                if not member.date_of_joining:
                    member.date_of_joining = member.created_at.date() if member.created_at else date.today()
                    updated = True

                if updated:
                    db.session.flush()  # Flush individual changes
            except Exception as member_error:
                print(f"Error updating member {member.id}: {member_error}")
                continue

        try:
            db.session.commit()
        except Exception as commit_error:
            print(f"Error committing staff updates: {commit_error}")
            db.session.rollback()

        print(f"Retrieved {len(staff_members)} staff members from database")
        return staff_members
    except Exception as e:
        print(f"Error getting comprehensive staff: {e}")
        db.session.rollback()
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
        departments = Department.query.filter_by(is_active=True).order_by(Department.display_name).all()
        print(f"Found {len(departments)} active departments")
        for dept in departments:
            print(f"  - {dept.name}: {dept.display_name}")
        return departments
    except Exception as e:
        print(f"Error getting active departments: {e}")
        # If no departments exist, create some basic ones
        return create_default_departments()

def create_default_departments():
    """Create default departments if none exist"""
    try:
        from models import Department
        from app import db

        default_depts = [
            {'name': 'spa_services', 'display_name': 'Spa Services', 'description': 'Spa and wellness services'},
            {'name': 'reception', 'display_name': 'Reception', 'description': 'Front desk operations'},
            {'name': 'management', 'display_name': 'Management', 'description': 'Administrative roles'}
        ]

        created_depts = []
        for dept_data in default_depts:
            dept = Department(**dept_data)
            db.session.add(dept)
            created_depts.append(dept)

        db.session.commit()
        print(f"Created {len(created_depts)} default departments")
        return created_depts
    except Exception as e:
        print(f"Error creating default departments: {e}")
        db.session.rollback()
        return []

def get_active_services():
    """Get all active services"""
    try:
        return Service.query.filter_by(is_active=True).all()
    except Exception as e:
        print(f"Error getting active services: {e}")
        return []

def create_comprehensive_staff(form_data):
    """Create new staff member with comprehensive details"""
    try:
        from werkzeug.security import generate_password_hash

        # Generate staff code if not provided
        staff_code = form_data.get('staff_code')
        if not staff_code:
            # Get next available staff code
            try:
                last_staff = User.query.filter(User.staff_code.isnot(None)).order_by(User.id.desc()).first()
                if last_staff and last_staff.staff_code and last_staff.staff_code.startswith('STF'):
                    last_num = int(last_staff.staff_code[3:])
                    staff_code = f"STF{str(last_num + 1).zfill(3)}"
                else:
                    staff_code = f"STF001"
            except Exception:
                # Fallback to counting all staff
                staff_count = User.query.filter(User.role.in_(['staff', 'manager', 'admin'])).count()
                staff_code = f"STF{str(staff_count + 1).zfill(3)}"

        staff_member = User(
            username=form_data['username'],
            email=form_data.get('email') if form_data.get('email') and form_data.get('email').strip() else None,
            first_name=form_data['first_name'],
            last_name=form_data['last_name'],
            phone=form_data.get('phone'),
            role=form_data.get('role', 'staff'),

            # Enhanced Profile Details
            profile_photo_url=form_data.get('profile_photo_url'),
            gender=form_data.get('gender', 'other'),
            date_of_birth=form_data.get('date_of_birth'),
            date_of_joining=form_data.get('date_of_joining') or date.today(),
            staff_code=staff_code,
            notes_bio=form_data.get('notes_bio'),
            designation=form_data.get('designation') or form_data.get('role', 'staff').title(),

            # ID Proofs
            aadhaar_number=form_data.get('aadhaar_number'),
            aadhaar_card_url=form_data.get('aadhaar_card_url'),
            pan_number=form_data.get('pan_number'),
            pan_card_url=form_data.get('pan_card_url'),
            verification_status=form_data.get('verification_status', False),

            # Facial Recognition
            face_image_url=form_data.get('face_image_url'),
            facial_encoding=form_data.get('facial_encoding'),
            enable_face_checkin=form_data.get('enable_face_checkin', True),

            # Commission
            commission_percentage=float(form_data.get('commission_percentage') or 0.0),
            fixed_commission=float(form_data.get('fixed_commission') or 0.0),
            hourly_rate=float(form_data.get('hourly_rate') or 0.0),
            total_revenue_generated=0.0,
            total_clients_served=0,
            average_rating=0.0,

            # Role and Department
            role_id=form_data.get('role_id') if form_data.get('role_id') and form_data.get('role_id') != 0 else None,
            department_id=form_data.get('department_id') if form_data.get('department_id') and form_data.get('department_id') != 0 else None,

            is_active=form_data.get('is_active', True),
            created_at=datetime.utcnow()
        )

        # Set password if provided
        if form_data.get('password'):
            staff_member.password_hash = generate_password_hash(form_data['password'])
        else:
            # Set default password
            staff_member.password_hash = generate_password_hash('password123')

        db.session.add(staff_member)
        db.session.flush()  # Get the ID for service assignments
        db.session.commit()  # Commit the transaction to database

        print(f"Successfully created staff member: {staff_member.full_name} with code: {staff_code}")
        return staff_member

    except Exception as e:
        db.session.rollback()
        print(f"Error creating comprehensive staff: {e}")
        return None

def get_staff_schedule_ranges(staff_id):
    """Get all schedule ranges for a staff member"""
    try:
        from models import StaffScheduleRange
        return StaffScheduleRange.query.filter_by(
            staff_id=staff_id,
            is_active=True
        ).order_by(StaffScheduleRange.start_date).all()
    except Exception as e:
        print(f"Error getting staff schedule ranges: {e}")
        return []

def get_schedule_range_by_id(schedule_id):
    """Get a specific schedule range by ID"""
    try:
        from models import StaffScheduleRange
        return StaffScheduleRange.query.get(schedule_id)
    except Exception as e:
        print(f"Error getting schedule range by ID: {e}")
        return None

def update_schedule_range(schedule_id, update_data):
    """Update a schedule range"""
    try:
        from models import StaffScheduleRange
        schedule = StaffScheduleRange.query.get(schedule_id)
        if schedule:
            for key, value in update_data.items():
                if hasattr(schedule, key):
                    setattr(schedule, key, value)
            db.session.commit()
            return True
        return False
    except Exception as e:
        print(f"Error updating schedule range: {e}")
        db.session.rollback()
        return False

def delete_schedule_range(schedule_id):
    """Soft delete a schedule range"""
    try:
        from models import StaffScheduleRange
        schedule = StaffScheduleRange.query.get(schedule_id)
        if schedule:
            schedule.is_active = False
            db.session.commit()
            return True
        return False
    except Exception as e:
        print(f"Error deleting schedule range: {e}")
        db.session.rollback()
        return False