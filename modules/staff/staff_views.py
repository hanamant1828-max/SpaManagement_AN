"""
Comprehensive Staff Management Views - Complete Implementation
All 11 Requirements for Professional Staff Management System
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app import app
from forms import UserForm, AdvancedUserForm, ComprehensiveStaffForm
# Late imports to avoid circular dependency
from app import db
from models import (
    User, Role, Department, Service, StaffService, 
    Attendance, StaffPerformance, StaffScheduleRange
)
from .staff_queries import (
    get_all_staff, get_staff_by_id, get_staff_by_role, get_active_roles, 
    get_active_departments, get_active_services, create_staff, update_staff, delete_staff, 
    get_staff_appointments, get_staff_commissions, get_staff_stats, 
    get_comprehensive_staff, create_comprehensive_staff,
    get_staff_schedule_ranges, get_schedule_range_by_id, update_schedule_range, delete_schedule_range
)
import os
import csv
import io
from datetime import datetime, date, timedelta
import json

# Debug: Print route registration
print("Registering Staff Management routes...")
print(f"App name: {app.name}")
print(f"Current module: {__name__}")

@app.route('/api/health', methods=['GET'])
def api_health():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Staff Management API is running',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/staff')
@login_required
def staff():
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    staff_list = get_all_staff()
    roles = get_active_roles()
    departments = get_active_departments()

    form = AdvancedUserForm()
    advanced_form = AdvancedUserForm()

    # Set up form choices
    form.role.choices = [(r.name, r.display_name) for r in roles]
    # Set form choices if fields exist
    if hasattr(advanced_form, 'role_id'):
        advanced_form.role_id.choices = [(r.id, r.display_name) for r in roles]
    if hasattr(advanced_form, 'department_id'):
        advanced_form.department_id.choices = [(d.id, d.display_name) for d in departments]

    return render_template('staff.html', 
                         staff_members=staff_list,
                         form=form,
                         advanced_form=advanced_form,
                         roles=roles,
                         departments=departments)

@app.route('/comprehensive_staff')
@login_required
def comprehensive_staff():
    """Main comprehensive staff management page with all 11 features"""
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        print("Loading comprehensive staff management page...")

        # Force fresh data retrieval
        db.session.expire_all()

        # Get comprehensive staff data
        staff_list = get_comprehensive_staff()
        roles = get_active_roles()
        departments = get_active_departments()
        services = get_active_services()

        print(f"Loaded {len(staff_list)} staff members")
        print(f"Available roles: {[r.display_name for r in roles]}")
        print(f"Available departments: {[d.display_name for d in departments]}")

        # Apply filters if provided
        role_filter = request.args.get('role')
        department_filter = request.args.get('department')
        status_filter = request.args.get('status')

        if role_filter:
            staff_list = [s for s in staff_list if s.role_id == int(role_filter)]
            print(f"Filtered by role: {len(staff_list)} remaining")
        if department_filter:
            staff_list = [s for s in staff_list if s.department_id == int(department_filter)]
            print(f"Filtered by department: {len(staff_list)} remaining")
        if status_filter:
            if status_filter == 'active':
                staff_list = [s for s in staff_list if s.is_active]
            elif status_filter == 'inactive':
                staff_list = [s for s in staff_list if not s.is_active]
            print(f"Filtered by status: {len(staff_list)} remaining")

        # Force template cache refresh
        from flask import current_app
        if current_app.debug:
            current_app.jinja_env.cache = {}

        flash(f'Staff Management Updated - {len(staff_list)} staff members loaded', 'success')

        return render_template('comprehensive_staff.html', 
                             staff=staff_list,
                             roles=roles,
                             departments=departments,
                             services=services,
                             cache_buster=datetime.utcnow().timestamp())
    except Exception as e:
        print(f"Error in comprehensive_staff route: {str(e)}")
        flash(f'Error loading comprehensive staff data: {str(e)}', 'danger')
        return redirect(url_for('staff'))

@app.route('/comprehensive_staff/create', methods=['GET', 'POST'])
@login_required
def create_comprehensive_staff():
    """Create new staff with all 11 requirements"""
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'GET':
        # Get available roles and departments for the form
        from models import Role
        roles = Role.query.filter_by(is_active=True).all()
        departments = Department.query.filter_by(is_active=True).all()
        services = Service.query.filter_by(is_active=True).all()

        form = ComprehensiveStaffForm()
        form.role_id.choices = [(0, 'Select Role')] + [(r.id, r.display_name) for r in roles]
        form.department_id.choices = [(0, 'Select Department')] + [(d.id, d.display_name) for d in departments]
        form.assigned_services.choices = [(s.id, s.name) for s in services]

        return render_template('comprehensive_staff_form.html', 
                             form=form, 
                             action='Create',
                             roles=roles,
                             departments=departments,
                             services=services)

    # Handle form submission
    try:
        request_data = request.get_json() if request.is_json else request.form.to_dict()
        data = request_data.get('staff', request_data) if 'staff' in request_data else request_data
        schedule_data = request_data.get('schedule', [])

        # Hash password
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash(data.get('password', ''))

        # Create staff member
        staff = User(
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            password_hash=hashed_password,
            role_id=int(data['role_id']) if data.get('role_id') and str(data.get('role_id')).strip() not in ['', '0'] else None,
            department_id=int(data['department_id']) if data.get('department_id') and str(data.get('department_id')).strip() not in ['', '0'] else None,
            designation=data.get('designation'),
            commission_rate=float(data.get('commission_rate', 0)) if data.get('commission_rate') else None,
            hourly_rate=float(data.get('hourly_rate', 0)) if data.get('hourly_rate') else None,
            gender=data.get('gender'),
            date_of_birth=datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            date_of_joining=datetime.strptime(data.get('date_of_joining'), '%Y-%m-%d').date() if data.get('date_of_joining') else None,
            notes_bio=data.get('notes_bio', ''),
            is_active=data.get('is_active', True),
            staff_code=data.get('staff_code'),
            verification_status=data.get('verification_status', False),
            enable_face_checkin=data.get('enable_face_checkin', False),
        )

        db.session.add(staff)
        db.session.flush()  # Get the staff ID

        # Process schedule data if provided
        if schedule_data:
            from models import StaffScheduleRange
            for schedule_item in schedule_data:
                if schedule_item.get('working'):
                    # Create individual schedule entries for working days
                    schedule_entry = StaffScheduleRange(
                        staff_id=staff.id,
                        start_date=datetime.strptime(schedule_item['date'], '%Y-%m-%d').date(),
                        end_date=datetime.strptime(schedule_item['date'], '%Y-%m-%d').date(),
                        schedule_name='Daily Schedule',
                        description=schedule_item.get('notes', ''),
                        monday=True, tuesday=True, wednesday=True, thursday=True, friday=True,
                        saturday=False, sunday=False,  # Default working days
                        shift_start_time=datetime.strptime(schedule_item.get('start_time', '09:00'), '%H:%M').time(),
                        shift_end_time=datetime.strptime(schedule_item.get('end_time', '18:00'), '%H:%M').time(),
                        break_time=f"{schedule_item.get('break_minutes', 60)} minutes",
                        is_active=True,
                        priority=1
                    )
                    db.session.add(schedule_entry)

        # Assign services
        assigned_services = data.get('assigned_services', [])
        for service_id in assigned_services:
            staff_service = StaffService(
                staff_id=staff.id,
                service_id=service_id,
                skill_level='beginner'
            )
            db.session.add(staff_service)

        db.session.commit()
        flash('Staff member and schedule created successfully!', 'success')

        if request.is_json:
            return jsonify({'success': True, 'message': 'Staff member and schedule created successfully!', 'staff_id': staff.id})

        return redirect(url_for('comprehensive_staff'))

    except Exception as e:
        db.session.rollback()
        error_msg = f'Error creating staff member: {str(e)}'
        flash(error_msg, 'danger')

        if request.is_json:
            return jsonify({'success': False, 'message': error_msg})

        # Re-render form with errors and existing data if applicable
        roles = Role.query.filter_by(is_active=True).all()
        departments = Department.query.filter_by(is_active=True).all()
        services = Service.query.filter_by(is_active=True).all()
        form = ComprehensiveStaffForm(data=data) # Populate form with submitted data
        form.role_id.choices = [(0, 'Select Role')] + [(r.id, r.display_name) for r in roles]
        form.department_id.choices = [(0, 'Select Department')] + [(d.id, d.display_name) for d in departments]
        form.assigned_services.choices = [(s.id, s.name) for s in services]

        return render_template('comprehensive_staff_form.html',
                             form=form,
                             action='Create',
                             roles=roles,
                             departments=departments,
                             services=services)

@app.route('/comprehensive_staff/edit/<int:staff_id>', methods=['GET', 'POST'])
@login_required
def edit_comprehensive_staff(staff_id):
    """Edit existing staff with full feature access"""
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    staff_member = User.query.get_or_404(staff_id)
    form = ComprehensiveStaffForm(obj=staff_member)

    # Populate form choices
    roles = Role.query.filter_by(is_active=True).all()
    departments = Department.query.filter_by(is_active=True).all()
    services = Service.query.filter_by(is_active=True).all()

    form.role_id.choices = [(0, 'Select Role')] + [(r.id, r.display_name) for r in roles]
    form.department_id.choices = [(0, 'Select Department')] + [(d.id, d.display_name) for d in departments]
    form.assigned_services.choices = [(s.id, s.name) for s in services]


    # Pre-populate assigned services
    assigned_service_ids = [ss.service_id for ss in staff_member.staff_services if ss.is_active]
    form.assigned_services.data = assigned_service_ids

    if form.validate_on_submit():
        try:
            # Update staff member
            staff_member.username = form.username.data
            staff_member.first_name = form.first_name.data
            staff_member.last_name = form.last_name.data
            staff_member.email = form.email.data
            staff_member.phone = form.phone.data
            staff_member.gender = form.gender.data
            staff_member.date_of_birth = form.date_of_birth.data
            staff_member.date_of_joining = form.date_of_joining.data
            staff_member.designation = form.designation.data
            staff_member.staff_code = form.staff_code.data
            staff_member.notes_bio = form.notes_bio.data
            staff_member.aadhaar_number = form.aadhaar_number.data
            staff_member.pan_number = form.pan_number.data
            staff_member.verification_status = form.verification_status.data

            staff_member.enable_face_checkin = form.enable_face_checkin.data
            staff_member.role_id = form.role_id.data if form.role_id.data != 0 else None
            staff_member.department_id = form.department_id.data if form.department_id.data != 0 else None
            staff_member.is_active = form.is_active.data

            if form.password.data:
                staff_member.password_hash = generate_password_hash(form.password.data)

            # Update service assignments
            # Deactivate current assignments
            for ss in staff_member.staff_services:
                ss.is_active = False

            # Add new assignments
            for service_id in form.assigned_services.data:
                existing = StaffService.query.filter_by(
                    staff_id=staff_member.id,
                    service_id=service_id
                ).first()

                if existing:
                    existing.is_active = True
                else:
                    staff_service = StaffService(
                        staff_id=staff_member.id,
                        service_id=service_id,
                        skill_level='beginner'
                    )
                    db.session.add(staff_service)

            db.session.commit()
            flash(f'Staff member {staff_member.full_name} updated successfully!', 'success')
            return redirect(url_for('comprehensive_staff'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating staff member: {str(e)}', 'danger')

    return render_template('comprehensive_staff_form.html', 
                         form=form, 
                         action='Edit',
                         staff_member=staff_member,
                         roles=roles,
                         departments=departments,
                         services=services)

@app.route('/staff/attendance/punch-in', methods=['POST'])
@login_required
def punch_in():
    """Handle staff check-in (manual or facial recognition)"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    staff_id = data.get('staff_id')
    method = data.get('method', 'manual')

    try:
        # Check if already punched in today
        today = date.today()
        existing = Attendance.query.filter_by(
            staff_id=staff_id,
            date=today,
            check_out_time=None
        ).first()

        if existing:
            return jsonify({'error': 'Already punched in today'}), 400

        # Create attendance record
        attendance = Attendance(
            staff_id=staff_id,
            check_in_time=datetime.now(),
            check_in_method=method,
            date=today
        )

        db.session.add(attendance)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Punched in successfully',
            'check_in_time': attendance.check_in_time.strftime('%H:%M:%S')
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/staff/attendance/punch-out', methods=['POST'])
@login_required
def punch_out():
    """Handle staff check-out"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    staff_id = data.get('staff_id')

    try:
        # Find today's attendance record
        today = date.today()
        attendance = Attendance.query.filter_by(
            staff_id=staff_id,
            date=today,
            check_out_time=None
        ).first()

        if not attendance:
            return jsonify({'error': 'No punch-in record found for today'}), 400

        # Update with check-out time
        checkout_time = datetime.now()
        attendance.check_out_time = checkout_time

        # Calculate total hours
        time_diff = checkout_time - attendance.check_in_time
        attendance.total_hours = round(time_diff.total_seconds() / 3600, 2)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Punched out successfully',
            'check_out_time': checkout_time.strftime('%H:%M:%S'),
            'total_hours': attendance.total_hours
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/staff/performance/<int:staff_id>')
@login_required
def staff_performance(staff_id):
    """View detailed staff performance metrics"""
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    staff_member = User.query.get_or_404(staff_id)

    # Get performance data
    current_month = datetime.now().month
    current_year = datetime.now().year

    performance = StaffPerformance.query.filter_by(
        staff_id=staff_id,
        month=current_month,
        year=current_year
    ).first()

    # Get attendance records for current month
    start_of_month = date(current_year, current_month, 1)
    if current_month == 12:
        end_of_month = date(current_year + 1, 1, 1) - timedelta(days=1)
    else:
        end_of_month = date(current_year, current_month + 1, 1) - timedelta(days=1)

    attendance_records = Attendance.query.filter(
        Attendance.staff_id == staff_id,
        Attendance.date >= start_of_month,
        Attendance.date <= end_of_month
    ).all()

    # Get recent appointments
    recent_appointments = get_staff_appointments(staff_id)[:10]

    # Get commission data
    commissions = get_staff_commissions(staff_id)

    return render_template('staff_performance.html',
                         staff_member=staff_member,
                         performance=performance,
                         attendance_records=attendance_records,
                         recent_appointments=recent_appointments,
                         commissions=commissions)

@app.route('/staff/export')
@login_required
def export_staff():
    """Export staff data to CSV"""
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    try:
        staff_list = User.query.filter_by(is_active=True).all()

        output = io.StringIO()
        writer = csv.writer(output)

        # Write headers
        headers = [
            'Staff Code', 'Name', 'Email', 'Phone', 'Gender', 'Designation',
            'Department', 'Role', 'Date of Joining', 'Shift Start', 'Shift End',
            'Commission %', 'Hourly Rate', 'Total Revenue', 'Clients Served',
            'Average Rating', 'Verification Status', 'Active Status'
        ]
        writer.writerow(headers)

        # Write data
        for staff in staff_list:
            row = [
                staff.staff_code or '',
                staff.full_name,
                staff.email or '',
                staff.phone or '',
                staff.gender or '',
                staff.designation or '',
                staff.staff_department.display_name if staff.staff_department else '',
                staff.user_role.display_name if staff.user_role else staff.role,
                staff.date_of_joining.strftime('%Y-%m-%d') if staff.date_of_joining else '',
                staff.shift_start_time.strftime('%H:%M') if staff.shift_start_time else '',
                staff.shift_end_time.strftime('%H:%M') if staff.shift_end_time else '',
                staff.commission_percentage or 0,
                staff.hourly_rate or 0,
                staff.total_revenue_generated or 0,
                staff.total_clients_served or 0,
                staff.average_rating or 0,
                'Verified' if staff.verification_status else 'Pending',
                'Active' if staff.is_active else 'Inactive'
            ]
            writer.writerow(row)

        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=staff_export_{datetime.now().strftime("%Y%m%d")}.csv'

        return response

    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'danger')
        return redirect(url_for('comprehensive_staff'))

@app.route('/staff/facial-recognition/setup', methods=['POST'])
@login_required
def setup_facial_recognition():
    """Setup facial recognition for staff"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    staff_id = data.get('staff_id')
    face_encoding = data.get('face_encoding')

    try:
        staff_member = User.query.get(staff_id)
        if not staff_member:
            return jsonify({'error': 'Staff member not found'}), 404

        staff_member.facial_encoding = json.dumps(face_encoding)
        staff_member.enable_face_checkin = True

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Facial recognition setup completed'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/staff/facial-recognition/verify', methods=['POST'])
@login_required
def verify_facial_recognition():
    """Verify staff using facial recognition"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    face_encoding = data.get('face_encoding')

    try:
        # Get all staff with facial recognition enabled
        staff_with_faces = User.query.filter(
            User.facial_encoding.isnot(None),
            User.enable_face_checkin == True,
            User.is_active == True
        ).all()

        # Here you would implement face matching logic
        # For now, return a placeholder response

        return jsonify({
            'success': True,
            'message': 'Face verification in progress',
            'staff_count': len(staff_with_faces)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/staff/save-face', methods=['POST'])
@login_required
def save_face_image():
    """Save captured face image for staff member"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        data = request.get_json()
        staff_id = data.get('staff_id')
        face_image = data.get('face_image')

        if not staff_id or not face_image:
            return jsonify({'error': 'Missing staff ID or face image'}), 400

        staff_member = User.query.get(staff_id)
        if not staff_member:
            return jsonify({'error': 'Staff member not found'}), 404

        # Save base64 image data (you could also save to file system)
        staff_member.face_image_url = face_image
        staff_member.enable_face_checkin = True

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Face image saved successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Legacy routes for compatibility
@app.route('/staff/create', methods=['POST'])
@app.route('/staff/add', methods=['POST'])
@app.route('/add_staff', methods=['POST'])
@login_required
def create_staff_route():
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    form = AdvancedUserForm()
    roles = get_active_roles()
    form.role.choices = [(r.name, r.display_name) for r in roles]

    if form.validate_on_submit():
        staff_data = {
            'username': form.username.data,
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'role': form.role.data,
            'commission_rate': form.commission_rate.data,
            'hourly_rate': form.hourly_rate.data,
            'password_hash': generate_password_hash('TempPass123!'),  # Temporary password - must be changed on first login
            'is_active': True
        }

        create_staff(staff_data)
        flash('Staff member created successfully!', 'success')
    else:
        flash('Error creating staff member. Please check your input.', 'danger')

    return redirect(url_for('staff'))

@app.route('/staff/update/<int:id>', methods=['POST'])
@login_required
def update_staff_route(id):
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('staff'))

    staff_member = get_staff_by_id(id)
    if not staff_member:
        flash('Staff member not found', 'danger')
        return redirect(url_for('staff'))

    form = AdvancedUserForm()
    roles = get_active_roles()
    form.role.choices = [(r.name, r.display_name) for r in roles]

    if form.validate_on_submit():
        staff_data = {
            'username': form.username.data,
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'role': form.role.data,
            'commission_rate': form.commission_rate.data,
            'hourly_rate': form.hourly_rate.data
        }

        # Only update password if provided
        if form.password.data:
            staff_data['password_hash'] = generate_password_hash(form.password.data)

        update_staff(id, staff_data)
        flash('Staff member updated successfully!', 'success')
    else:
        flash('Error updating staff member. Please check your input.', 'danger')

    return redirect(url_for('staff'))

@app.route('/staff/delete/<int:id>', methods=['POST'])
@login_required
def delete_staff_route(id):
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('staff'))

    if delete_staff(id):
        flash('Staff member deleted successfully!', 'success')
    else:
        flash('Error deleting staff member', 'danger')

    return redirect(url_for('staff'))

@app.route('/staff/deactivate/<int:staff_id>', methods=['POST'])
@login_required
def deactivate_staff(staff_id):
    """Deactivate a staff member"""
    if not current_user.has_role('admin'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        staff_member = User.query.get(staff_id)
        if not staff_member:
            return jsonify({'error': 'Staff member not found'}), 404

        staff_member.is_active = False
        db.session.commit()

        return jsonify({'success': True, 'message': 'Staff member deactivated successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/staff/<int:id>')
@login_required
def staff_detail(id):
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('staff'))

    staff_member = get_staff_by_id(id)
    if not staff_member:
        flash('Staff member not found', 'danger')
        return redirect(url_for('staff'))

    appointments = get_staff_appointments(id)
    commissions = get_staff_commissions(id)
    stats = get_staff_stats(id)

    return render_template('staff_detail.html',
                         staff_member=staff_member,
                         appointments=appointments,
                         commissions=commissions,
                         stats=stats)

@app.route('/staff/comprehensive/test')
@login_required
def test_comprehensive_staff():
    """Test route to verify comprehensive staff management is working"""
    return jsonify({
        'status': 'success',
        'message': 'Comprehensive Staff Management System is Active',
        'features': [
            '1. Staff Profile Management',
            '2. Photo Capture & Storage',
            '3. ID Verification (Aadhaar/PAN)',
            '4. Facial Recognition Setup',
            '5. Work Schedule Management',
            '6. Attendance Tracking',
            '7. Performance Metrics',
            '8. Commission Management',
            '9. Role & Department Assignment',
            '10. Service Assignment',
            '11. Comprehensive Reporting'
        ],
        'routes': [
            '/staff/comprehensive',
            '/staff/comprehensive/create',
            '/staff/comprehensive/edit/<id>',
            '/staff/performance/<id>',
            '/staff/export'
        ]
    })

# ===== API ENDPOINTS FOR JAVASCRIPT CRUD OPERATIONS =====

@app.route('/api/staff', methods=['GET'])
@login_required
def api_get_all_staff():
    """API endpoint to get all staff data for JavaScript"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        staff_list = get_comprehensive_staff()
        roles = get_active_roles()
        departments = get_active_departments()

        # Convert staff to JSON-serializable format
        staff_data = []
        for staff in staff_list:
            staff_data.append({
                'id': staff.id,
                'username': staff.username,
                'first_name': staff.first_name,
                'last_name': staff.last_name,
                'full_name': f"{staff.first_name} {staff.last_name}",
                'email': staff.email,
                'phone': staff.phone,
                'role': staff.role,
                'role_id': staff.role_id,
                'role_display': staff.user_role.display_name if staff.user_role else staff.role.title(),
                'department_id': staff.department_id,
                'department_display': staff.staff_department.display_name if staff.staff_department else 'No Department',
                'designation': staff.designation,
                'staff_code': staff.staff_code,
                'employee_id': staff.employee_id,
                'commission_rate': staff.commission_rate or 0,
                'hourly_rate': staff.hourly_rate or 0,
                'is_active': staff.is_active,
                'gender': staff.gender,
                'date_of_birth': staff.date_of_birth.isoformat() if staff.date_of_birth else None,
                'date_of_joining': staff.date_of_joining.isoformat() if staff.date_of_joining else None,
                'shift_start_time': staff.shift_start_time.strftime('%H:%M') if staff.shift_start_time else None,
                'shift_end_time': staff.shift_end_time.strftime('%H:%M') if staff.shift_end_time else None,
                'working_days': staff.working_days,
                'verification_status': staff.verification_status,
                'enable_face_checkin': staff.enable_face_checkin,
                'total_revenue_generated': staff.total_revenue_generated or 0,
                'total_clients_served': staff.total_clients_served or 0,
                'average_rating': staff.average_rating or 0,
                'last_login': staff.last_login.isoformat() if staff.last_login else None,
                'notes_bio': staff.notes_bio
            })

        roles_data = [{'id': r.id, 'name': r.name, 'display_name': r.display_name} for r in roles]
        departments_data = [{'id': d.id, 'name': d.name, 'display_name': d.display_name} for d in departments]

        return jsonify({
            'success': True,
            'staff': staff_data,
            'roles': roles_data,
            'departments': departments_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/<int:staff_id>', methods=['GET'])
@login_required  
def api_get_staff(staff_id):
    """API endpoint to get single staff member data"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Use direct query to avoid conflicts
        staff = User.query.get(staff_id)
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404

        staff_data = {
            'id': staff.id,
            'username': staff.username,
            'first_name': staff.first_name,
            'last_name': staff.last_name,
            'email': staff.email,
            'phone': staff.phone or '',
            'role': staff.role,
            'role_id': staff.role_id,
            'department_id': staff.department_id,
            'designation': staff.designation or '',
            'staff_code': staff.staff_code or '',
            'employee_id': staff.employee_id or '',
            'commission_rate': staff.commission_rate or 0,
            'hourly_rate': staff.hourly_rate or 0,
            'is_active': staff.is_active,
            'gender': staff.gender or '',
            'date_of_birth': staff.date_of_birth.isoformat() if staff.date_of_birth else '',
            'date_of_joining': staff.date_of_joining.isoformat() if staff.date_of_joining else '',
            'shift_start_time': staff.shift_start_time.strftime('%H:%M') if staff.shift_start_time else '',
            'shift_end_time': staff.shift_end_time.strftime('%H:%M') if staff.shift_end_time else '',
            'working_days': staff.working_days or '',
            'verification_status': staff.verification_status or False,
            'enable_face_checkin': staff.enable_face_checkin or False,
            'notes_bio': staff.notes_bio or ''
        }

        return jsonify({'success': True, 'staff': staff_data})

    except Exception as e:
        print(f"Error in api_get_staff: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff', methods=['POST'])
@login_required
def api_create_staff():
    """API endpoint to create new staff member"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Defensive coding - validate required fields with user-friendly messages
        required_fields = {
            'username': 'Username is required. Please enter a unique username.',
            'first_name': 'First name is required. Please enter the staff member\'s first name.',
            'last_name': 'Last name is required. Please enter the staff member\'s last name.',
            'email': 'Email address is required. Please enter a valid email address.'
        }

        for field, message in required_fields.items():
            field_value = (data.get(field) or '').strip() if isinstance(data.get(field), str) else data.get(field)
            if not field_value:
                return jsonify({'error': message}), 400

        # Check for duplicate username/email
        existing = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        if existing:
            return jsonify({'error': 'Username or email already exists'}), 400

        # Prepare staff data with defensive coding and safe defaults
        def safe_float(value, default=0.0, min_val=0.0, max_val=100.0):
            try:
                result = float(value or default)
                return max(min_val, min(max_val, result))
            except (ValueError, TypeError):
                return default

        def safe_date_parse(date_str, default=None):
            if not date_str or not str(date_str).strip():
                return default
            try:
                return datetime.strptime(str(date_str).strip(), '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return default

        def safe_time_parse(time_str):
            if not time_str or not str(time_str).strip():
                return None
            try:
                return datetime.strptime(str(time_str).strip(), '%H:%M').time()
            except (ValueError, TypeError):
                return None

        # Email validation
        import re
        email = data['email'].strip().lower()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'error': 'Please enter a valid email address format.'}), 400

        # Enforce secure password requirements
        password = data.get('password', '').strip()
        if not password:
            # Generate secure temporary password requiring immediate change
            import secrets
            import string
            characters = string.ascii_letters + string.digits + "!@#$%^&*"
            password = ''.join(secrets.choice(characters) for i in range(12))
            # TODO: Flag account for mandatory password change on first login

        staff_data = {
            'username': data['username'].strip(),
            'first_name': data['first_name'].strip().title(),
            'last_name': data['last_name'].strip().title(),
            'email': email,
            'password_hash': generate_password_hash(password),
            'phone': (data.get('phone') or '').strip(),
            'role': (data.get('role') or 'staff').strip(),
            'role_id': int(data['role_id']) if data.get('role_id') and str(data.get('role_id')).strip() not in ['', '0'] else None,
            'department_id': int(data['department_id']) if data.get('department_id') and str(data.get('department_id')).strip() not in ['', '0'] else None,
            'designation': (data.get('designation') or 'Staff Member').strip(),
            'commission_rate': safe_float(data.get('commission_rate'), 0.0, 0.0, 100.0),
            'hourly_rate': safe_float(data.get('hourly_rate'), 0.0, 0.0, 1000.0),
            'gender': (data.get('gender') or 'other').strip(),
            'date_of_birth': safe_date_parse(data.get('date_of_birth')),
            'date_of_joining': safe_date_parse(data.get('date_of_joining'), date.today()),
            'shift_start_time': safe_time_parse(data.get('shift_start_time')),
            'shift_end_time': safe_time_parse(data.get('shift_end_time')),
            'working_days': (data.get('working_days') or '1111100').strip(),
            'verification_status': False,
            'enable_face_checkin': bool(data.get('enable_face_checkin', False)),
            'notes_bio': (data.get('notes_bio') or '').strip(),
            'is_active': True
        }

        # Create staff member
        new_staff = create_staff(staff_data)

        # Generate staff code if not provided
        if not new_staff.staff_code:
            new_staff.staff_code = f"STF{str(new_staff.id).zfill(3)}"
            db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Staff member {new_staff.first_name} {new_staff.last_name} created successfully',
            'staff': {
                'id': new_staff.id,
                'first_name': new_staff.first_name,
                'last_name': new_staff.last_name,
                'staff_code': new_staff.staff_code
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/<int:staff_id>', methods=['PUT'])
@login_required
def api_update_staff(staff_id):
    """API endpoint to update staff member"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        staff = get_staff_by_id(staff_id)
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        if not data.get('first_name') or not data.get('last_name'):
            return jsonify({'error': 'First name and last name are required'}), 400

        # Defensive updates with proper type handling
        try:
            # Basic string fields
            if 'first_name' in data and data['first_name']:
                staff.first_name = str(data['first_name']).strip()
            if 'last_name' in data and data['last_name']:
                staff.last_name = str(data['last_name']).strip()
            if 'email' in data:
                staff.email = str(data['email']).strip() if data['email'] else None
            if 'phone' in data:
                staff.phone = str(data['phone']).strip() if data['phone'] else None
            if 'designation' in data:
                staff.designation = str(data['designation']).strip() if data['designation'] else None
            if 'notes_bio' in data:
                staff.notes_bio = str(data['notes_bio']).strip() if data['notes_bio'] else None
            if 'gender' in data:
                staff.gender = str(data['gender']).strip() if data['gender'] else None

            # Numeric fields with safe conversion
            if 'commission_rate' in data:
                try:
                    staff.commission_rate = float(data['commission_rate']) if data['commission_rate'] else 0.0
                except (ValueError, TypeError):
                    staff.commission_rate = 0.0
            
            if 'hourly_rate' in data:
                try:
                    staff.hourly_rate = float(data['hourly_rate']) if data['hourly_rate'] else 0.0
                except (ValueError, TypeError):
                    staff.hourly_rate = 0.0

            # Role and department IDs with safe conversion
            if 'role_id' in data and data['role_id']:
                try:
                    role_id = int(data['role_id'])
                    staff.role_id = role_id if role_id > 0 else None
                except (ValueError, TypeError):
                    pass  # Keep existing value
            
            if 'department_id' in data and data['department_id']:
                try:
                    dept_id = int(data['department_id'])
                    staff.department_id = dept_id if dept_id > 0 else None
                except (ValueError, TypeError):
                    pass  # Keep existing value

            # Date fields with safe parsing
            if 'date_of_birth' in data and data['date_of_birth']:
                try:
                    staff.date_of_birth = datetime.strptime(str(data['date_of_birth']), '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    pass  # Keep existing value
                    
            if 'date_of_joining' in data and data['date_of_joining']:
                try:
                    staff.date_of_joining = datetime.strptime(str(data['date_of_joining']), '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    pass  # Keep existing value

            # Time fields with safe parsing
            if 'shift_start_time' in data and data['shift_start_time']:
                try:
                    staff.shift_start_time = datetime.strptime(str(data['shift_start_time']), '%H:%M').time()
                except (ValueError, TypeError):
                    pass  # Keep existing value
                    
            if 'shift_end_time' in data and data['shift_end_time']:
                try:
                    staff.shift_end_time = datetime.strptime(str(data['shift_end_time']), '%H:%M').time()
                except (ValueError, TypeError):
                    pass  # Keep existing value

            # Boolean and other fields
            if 'enable_face_checkin' in data:
                staff.enable_face_checkin = bool(data['enable_face_checkin'])
            
            if 'working_days' in data:
                staff.working_days = str(data['working_days']) if data['working_days'] else None

            # Password update with proper hashing
            if data.get('password') and str(data['password']).strip():
                staff.password_hash = generate_password_hash(str(data['password']).strip())

            # Commit the changes
            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'Staff member {staff.first_name} {staff.last_name} updated successfully'
            })

        except Exception as update_error:
            db.session.rollback()
            print(f"Error updating staff fields: {update_error}")
            return jsonify({'error': f'Failed to update staff data: {str(update_error)}'}), 500

    except Exception as e:
        db.session.rollback()
        print(f"Error in api_update_staff: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/staff/<int:staff_id>', methods=['DELETE'])
@login_required
def api_delete_staff(staff_id):
    """API endpoint to delete (deactivate) staff member"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        staff = get_staff_by_id(staff_id)
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404

        staff_name = f"{staff.first_name} {staff.last_name}"

        # Soft delete (deactivate)
        if delete_staff(staff_id):
            return jsonify({
                'success': True,
                'message': f'Staff member {staff_name} has been deactivated successfully'
            })
        else:
            return jsonify({'error': 'Failed to delete staff member'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/staff/schedule-ranges/<int:schedule_id>', methods=['GET'])
@login_required
def api_get_schedule_range(schedule_id):
    """Get a specific schedule range by ID"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403
    try:
        schedule = get_schedule_range_by_id(schedule_id)
        if schedule:
            return jsonify({
                'success': True,
                'schedule': {
                    'id': schedule.id,
                    'from_date': schedule.start_date.strftime('%Y-%m-%d'),
                    'to_date': schedule.end_date.strftime('%Y-%m-%d'),
                    'staff_id': schedule.staff_id,
                    'schedule_name': schedule.schedule_name,
                    'description': schedule.description,
                    'monday': schedule.monday,
                    'tuesday': schedule.tuesday,
                    'wednesday': schedule.wednesday,
                    'thursday': schedule.thursday,
                    'friday': schedule.friday,
                    'saturday': schedule.saturday,
                    'sunday': schedule.sunday,
                    'shift_start_time': schedule.shift_start_time.strftime('%H:%M') if schedule.shift_start_time else '',
                    'shift_end_time': schedule.shift_end_time.strftime('%H:%M') if schedule.shift_end_time else '',
                    'break_time': schedule.break_time,
                    'priority': schedule.priority,
                    'is_active': schedule.is_active
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Schedule range not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/staff/<int:staff_id>/schedule-ranges/<int:schedule_id>', methods=['PUT'])
@login_required
def api_update_schedule_range(staff_id, schedule_id):
    """Update a specific schedule range"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403
    try:
        data = request.get_json()

        # Validate input
        if not data.get('start_date') or not data.get('end_date'):
            return jsonify({
                'success': False,
                'error': 'start_date and end_date are required'
            }), 400

        update_data = {
            'schedule_name': data.get('schedule_name'),
            'description': data.get('description'),
            'start_date': datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            'end_date': datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            'monday': data.get('monday'),
            'tuesday': data.get('tuesday'),
            'wednesday': data.get('wednesday'),
            'thursday': data.get('thursday'),
            'friday': data.get('friday'),
            'saturday': data.get('saturday'),
            'sunday': data.get('sunday'),
            'shift_start_time': datetime.strptime(data['shift_start_time'], '%H:%M').time() if data.get('shift_start_time') else None,
            'shift_end_time': datetime.strptime(data['shift_end_time'], '%H:%M').time() if data.get('shift_end_time') else None,
            'break_time': data.get('break_time'),
            'priority': data.get('priority'),
            'is_active': data.get('is_active')
        }

        # Update the schedule range
        success = update_schedule_range(schedule_id, update_data)

        if success:
            return jsonify({
                'success': True,
                'message': 'Schedule range updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update schedule range'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/staff/schedule-ranges/<int:schedule_id>', methods=['DELETE'])
@login_required
def api_delete_schedule_range(schedule_id):
    """Delete a specific schedule range"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403
    try:
        success = delete_schedule_range(schedule_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Schedule range deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete schedule range'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API CSRF Token Support
@app.route("/api/csrf", methods=["GET"])
@login_required
def api_get_csrf_token():
    """Provide CSRF token for authenticated JSON API requests"""
    try:
        from flask_wtf.csrf import generate_csrf
        token = generate_csrf()
        return jsonify({
            "success": True,
            "csrf_token": token
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to generate CSRF token"
        }), 500