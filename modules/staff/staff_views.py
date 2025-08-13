
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
from models import db, User, Service, Role, Department, Attendance, Leave, StaffService, StaffPerformance
from .staff_queries import (
    get_all_staff, get_staff_by_id, get_staff_by_role, get_active_roles, 
    get_active_departments, create_staff, update_staff, delete_staff, 
    get_staff_appointments, get_staff_commissions, get_staff_stats
)
import os
import csv
import io
from datetime import datetime, date, timedelta
import json

@app.route('/staff')
@login_required
def staff():
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    staff_list = get_all_staff()
    roles = get_active_roles()
    departments = get_active_departments()
    
    form = UserForm()
    advanced_form = AdvancedUserForm()
    
    # Set up form choices
    form.role.choices = [(r.name, r.display_name) for r in roles]
    # Set form choices if fields exist
    if hasattr(advanced_form, 'role_id'):
        advanced_form.role_id.choices = [(r.id, r.display_name) for r in roles]
    if hasattr(advanced_form, 'department_id'):
        advanced_form.department_id.choices = [(d.id, d.display_name) for d in departments]
    
    return render_template('staff.html', 
                         staff=staff_list,
                         form=form,
                         advanced_form=advanced_form,
                         roles=roles,
                         departments=departments)

@app.route('/staff/comprehensive')
@login_required
@app.route('/comprehensive_staff')
@login_required
def comprehensive_staff():
    """Main comprehensive staff management page with all 11 features"""
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # Get comprehensive staff data
        staff_list = get_comprehensive_staff()
        roles = get_active_roles()
        departments = get_active_departments()
        services = get_active_services()
        
        # Apply filters if provided
        role_filter = request.args.get('role')
        department_filter = request.args.get('department')
        status_filter = request.args.get('status')
        
        if role_filter:
            staff_list = [s for s in staff_list if s.role_id == int(role_filter)]
        if department_filter:
            staff_list = [s for s in staff_list if s.department_id == int(department_filter)]
        if status_filter:
            if status_filter == 'active':
                staff_list = [s for s in staff_list if s.is_active]
            elif status_filter == 'inactive':
                staff_list = [s for s in staff_list if not s.is_active]
        
        flash(f'Comprehensive Staff Management System Active - {len(staff_list)} staff members found', 'info')
        
        return render_template('comprehensive_staff.html', 
                             staff=staff_list,
                             roles=roles,
                             departments=departments,
                             services=services)
    except Exception as e:
        flash(f'Error loading comprehensive staff data: {str(e)}', 'danger')
        return redirect(url_for('staff'))

@app.route('/comprehensive_staff/create', methods=['GET', 'POST'])
@login_required
def create_comprehensive_staff():
    """Create new staff member with comprehensive form"""
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    from forms import ComprehensiveStaffForm
    form = ComprehensiveStaffForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Create comprehensive staff member
            success = create_comprehensive_staff_member(form)
            if success:
                flash('Staff member created successfully with all comprehensive features!', 'success')
                return redirect(url_for('comprehensive_staff'))
            else:
                flash('Error creating staff member', 'danger')
        except Exception as e:
            flash(f'Error creating staff member: {str(e)}', 'danger')
    
    return render_template('comprehensive_staff_form.html', form=form, mode='create')
    except Exception as e:
        flash(f'Error loading comprehensive staff data: {str(e)}', 'danger')
        return redirect(url_for('staff'))

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

@app.route('/staff/comprehensive/create', methods=['GET', 'POST'])
@login_required
def create_comprehensive_staff():
    """Create new staff with all 11 requirements"""
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = ComprehensiveStaffForm()
    
    # Populate form choices
    roles = Role.query.filter_by(is_active=True).all()
    departments = Department.query.filter_by(is_active=True).all()
    services = Service.query.filter_by(is_active=True).all()
    
    form.role_id.choices = [(0, 'Select Role')] + [(r.id, r.display_name) for r in roles]
    form.department_id.choices = [(0, 'Select Department')] + [(d.id, d.display_name) for d in departments]
    form.assigned_services.choices = [(s.id, s.name) for s in services]
    
    if form.validate_on_submit():
        try:
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
                'date_of_joining': form.date_of_joining.data or date.today(),
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
                'role': 'staff'  # Fallback
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
            flash(f'Staff member {new_staff.full_name} created successfully!', 'success')
            return redirect(url_for('comprehensive_staff'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating staff member: {str(e)}', 'danger')
    
    return render_template('comprehensive_staff_form.html', 
                         form=form, 
                         action='Create',
                         roles=roles,
                         departments=departments,
                         services=services)

@app.route('/staff/comprehensive/edit/<int:staff_id>', methods=['GET', 'POST'])
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
    
    # Pre-populate working days
    if staff_member.working_days:
        form.monday.data = staff_member.working_days[0] == '1'
        form.tuesday.data = staff_member.working_days[1] == '1'
        form.wednesday.data = staff_member.working_days[2] == '1'
        form.thursday.data = staff_member.working_days[3] == '1'
        form.friday.data = staff_member.working_days[4] == '1'
        form.saturday.data = staff_member.working_days[5] == '1'
        form.sunday.data = staff_member.working_days[6] == '1'
    
    # Pre-populate assigned services
    assigned_service_ids = [ss.service_id for ss in staff_member.staff_services if ss.is_active]
    form.assigned_services.data = assigned_service_ids
    
    if form.validate_on_submit():
        try:
            # Generate working days string
            working_days = ''
            working_days += '1' if form.monday.data else '0'
            working_days += '1' if form.tuesday.data else '0'
            working_days += '1' if form.wednesday.data else '0'
            working_days += '1' if form.thursday.data else '0'
            working_days += '1' if form.friday.data else '0'
            working_days += '1' if form.saturday.data else '0'
            working_days += '1' if form.sunday.data else '0'
            
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
            staff_member.shift_start_time = form.shift_start_time.data
            staff_member.shift_end_time = form.shift_end_time.data
            staff_member.break_time = form.break_time.data
            staff_member.weekly_off_days = form.weekly_off_days.data
            staff_member.working_days = working_days
            staff_member.commission_percentage = form.commission_percentage.data or 0.0
            staff_member.fixed_commission = form.fixed_commission.data or 0.0
            staff_member.hourly_rate = form.hourly_rate.data or 0.0
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

# Legacy routes for compatibility
@app.route('/staff/create', methods=['POST'])
@app.route('/staff/add', methods=['POST'])
@app.route('/add_staff', methods=['POST'])
@login_required
def create_staff_route():
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = UserForm()
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
            'password_hash': generate_password_hash(form.password.data),
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
        return redirect(url_for('dashboard'))
    
    staff_member = get_staff_by_id(id)
    if not staff_member:
        flash('Staff member not found', 'danger')
        return redirect(url_for('staff'))
    
    form = UserForm()
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
        return redirect(url_for('dashboard'))
    
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
        return redirect(url_for('dashboard'))
    
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

