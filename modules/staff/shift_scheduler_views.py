
"""
Staff Shift Scheduler Views
Complete implementation with CRUD operations for staff scheduling using new schema
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.exceptions import BadRequest
from app import app, db
from models import User, ShiftManagement, ShiftLogs
from datetime import datetime, date, timedelta
import json

# Create Blueprint for shift scheduler
shift_scheduler_bp = Blueprint('shift_scheduler', __name__, url_prefix='/shift-scheduler')

# Redirect route for /shift-scheduler to /shift-scheduler/shift-scheduler
@shift_scheduler_bp.route('/')
def shift_scheduler_redirect():
    """Redirect /shift-scheduler to /shift-scheduler/shift-scheduler"""
    from flask import redirect, url_for
    return redirect(url_for('shift_scheduler.shift_scheduler'))

# Add shift scheduler page
@shift_scheduler_bp.route('/shift-scheduler/add')
@login_required
def add_shift_scheduler():
    """Add shift scheduler page with day-by-day configuration"""
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get all active staff members
    staff_members = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()

    return render_template('add_shift_scheduler.html',
                         staff_members=staff_members,
                         today=date.today().strftime('%Y-%m-%d'))

# Main shift scheduler interface
@shift_scheduler_bp.route('/shift-scheduler')
@login_required
def shift_scheduler():
    """Main shift scheduler page"""
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get all active staff members
    staff_members = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()

    return render_template('shift_scheduler.html',
                         staff_members=staff_members,
                         today=date.today().strftime('%Y-%m-%d'))

# Add alias route for the main interface to match template expectations
@shift_scheduler_bp.route('/')
@login_required  
def index():
    """Alias for main shift scheduler interface"""
    return shift_scheduler()

# API endpoint to get existing schedules
@shift_scheduler_bp.route('/api/shift-scheduler', methods=['GET'])
@login_required
def api_staff_day_schedule(staff_id):
    """API endpoint for saving day schedule"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        staff_id = request.args.get('staff_id', type=int)
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not staff_id or not start_date_str or not end_date_str:
            return jsonify({'error': 'Missing required parameters'}), 400

        # Parse dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Get all shift managements that overlap with the requested date range
        schedules = ShiftManagement.query.filter(
            ShiftManagement.staff_id == staff_id,
            ShiftManagement.from_date <= end_date,
            ShiftManagement.to_date >= start_date
        ).order_by(ShiftManagement.from_date).all()

        schedule_data = []
        for schedule in schedules:
            # Get first shift log for this management entry to show times
            first_log = ShiftLogs.query.filter_by(shift_management_id=schedule.id).first()
            
            schedule_data.append({
                'id': schedule.id,
                'schedule_name': f"Shift {schedule.from_date.strftime('%Y-%m-%d')} to {schedule.to_date.strftime('%Y-%m-%d')}",
                'description': '',
                'start_date': schedule.from_date.strftime('%Y-%m-%d'),
                'end_date': schedule.to_date.strftime('%Y-%m-%d'),
                'shift_start_time': first_log.shift_start_time.strftime('%H:%M') if first_log and first_log.shift_start_time else '',
                'shift_end_time': first_log.shift_end_time.strftime('%H:%M') if first_log and first_log.shift_end_time else '',
                'shift_start_time_12h': first_log.shift_start_time.strftime('%I:%M %p') if first_log and first_log.shift_start_time else '',
                'shift_end_time_12h': first_log.shift_end_time.strftime('%I:%M %p') if first_log and first_log.shift_end_time else '',
                'break_time': first_log.get_break_time_display() if first_log else '',
                'priority': 1
            })

        return jsonify({
            'success': True,
            'schedules': schedule_data,
            'staff_id': staff_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Save daily schedule with day-by-day configuration
@shift_scheduler_bp.route('/api/shift-scheduler/save-daily-schedule', methods=['POST'])
@login_required
def save_daily_schedule():
    """Save schedule with day-by-day configuration using new schema"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        data = request.get_json()
        staff_id = data.get('staff_id')
        schedule_name = data.get('schedule_name')
        description = data.get('description', '')
        priority = data.get('priority', 1)
        schedule_days = data.get('schedule_days', [])

        if not staff_id or not schedule_name or not schedule_days:
            return jsonify({'error': 'Missing required data'}), 400

        # Verify staff member exists
        staff = User.query.get(staff_id)
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404

        # Get date range from schedule days
        working_days = [day for day in schedule_days if day.get('working', False)]
        if not working_days:
            return jsonify({'error': 'No working days specified'}), 400

        # Sort days by date
        working_days.sort(key=lambda x: x['date'])
        from_date = datetime.strptime(working_days[0]['date'], '%Y-%m-%d').date()
        to_date = datetime.strptime(working_days[-1]['date'], '%Y-%m-%d').date()

        # Check if shift management already exists for this staff member
        existing_management = ShiftManagement.query.filter_by(staff_id=staff_id).first()
        
        if existing_management:
            # Update existing entry - extend date range and clear old logs
            existing_management.from_date = min(existing_management.from_date, from_date)
            existing_management.to_date = max(existing_management.to_date, to_date)
            existing_management.updated_at = datetime.utcnow()
            
            # Clear existing shift logs for this management entry
            ShiftLogs.query.filter_by(shift_management_id=existing_management.id).delete()
            shift_management = existing_management
        else:
            # Create new shift management entry
            shift_management = ShiftManagement(
                staff_id=staff_id,
                from_date=from_date,
                to_date=to_date
            )
            db.session.add(shift_management)
            db.session.flush()  # Get the ID

        # Create shift logs for each working day
        logs_created = 0
        for day in working_days:
            day_date = datetime.strptime(day['date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(day['startTime'], '%H:%M').time() if day.get('startTime') else None
            end_time = datetime.strptime(day['endTime'], '%H:%M').time() if day.get('endTime') else None
            break_start = datetime.strptime(day['breakStart'], '%H:%M').time() if day.get('breakStart') else None
            break_end = datetime.strptime(day['breakEnd'], '%H:%M').time() if day.get('breakEnd') else None
            
            # Out of office / field work
            out_start = datetime.strptime(day['outOfOfficeStart'], '%H:%M').time() if day.get('outOfOfficeStart') else None
            out_end = datetime.strptime(day['outOfOfficeEnd'], '%H:%M').time() if day.get('outOfOfficeEnd') else None
            out_reason = day.get('outOfOfficeReason', '')

            shift_log = ShiftLogs(
                shift_management_id=shift_management.id,
                individual_date=day_date,
                shift_start_time=start_time,
                shift_end_time=end_time,
                break_start_time=break_start,
                break_end_time=break_end,
                out_of_office_start=out_start,
                out_of_office_end=out_end,
                out_of_office_reason=out_reason,
                status='scheduled'
            )
            db.session.add(shift_log)
            logs_created += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Schedule saved successfully! Created {logs_created} shift log(s)',
            'shift_management_id': shift_management.id,
            'logs_created': logs_created
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Get all schedules from all staff members for management table
@shift_scheduler_bp.route('/api/all-schedules', methods=['GET'])
@login_required
def api_get_all_schedules():
    """Get consolidated schedule view using new shift management schema"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Get all shift managements with staff information, ordered by most recent first
        schedules = db.session.query(ShiftManagement, User).join(
            User, ShiftManagement.staff_id == User.id
        ).filter(
            User.is_active == True
        ).order_by(ShiftManagement.created_at.desc(), User.first_name, User.last_name).all()

        # Create schedule list directly - one entry per staff since we now have unique constraint
        schedule_list = []
        for schedule, staff in schedules:
            # Get first shift log for working days info
            first_log = ShiftLogs.query.filter_by(shift_management_id=schedule.id).first()
            
            # Default working days
            working_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
            working_days_str = "Mon to Fri"
            
            shift_start_time = ''
            shift_end_time = ''
            break_time = ''
            
            if first_log:
                shift_start_time = first_log.shift_start_time.strftime('%H:%M') if first_log.shift_start_time else ''
                shift_end_time = first_log.shift_end_time.strftime('%H:%M') if first_log.shift_end_time else ''
                break_time = first_log.get_break_time_display()

            # Get total working days for this staff
            total_logs = ShiftLogs.query.filter_by(shift_management_id=schedule.id).count()

            schedule_list.append({
                'id': schedule.id,
                'staff_id': staff.id,
                'staff_name': f"{staff.first_name} {staff.last_name}",
                'schedule_name': f"Staff Schedule ({total_logs} days)",
                'description': '',
                'start_date': schedule.from_date.strftime('%Y-%m-%d'),
                'end_date': schedule.to_date.strftime('%Y-%m-%d'),
                'working_days': working_days,
                'working_days_str': working_days_str,
                'shift_start_time': shift_start_time,
                'shift_end_time': shift_end_time,
                'shift_start_time_12h': first_log.shift_start_time.strftime('%I:%M %p') if first_log and first_log.shift_start_time else '',
                'shift_end_time_12h': first_log.shift_end_time.strftime('%I:%M %p') if first_log and first_log.shift_end_time else '',
                'break_time': break_time,
                'priority': 1,
                'created_at': schedule.created_at.strftime('%Y-%m-%d %H:%M') if schedule.created_at else '',
                'total_working_days': total_logs,
                'is_consolidated': False
            })

        return jsonify({
            'success': True,
            'schedules': schedule_list,
            'total_count': len(schedule_list)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoint to get schedule details for view modal
@shift_scheduler_bp.route('/api/staff/<int:staff_id>/schedule-details', methods=['GET'])
@login_required
def api_get_staff_schedule_details(staff_id):
    """Get detailed schedule information for a staff member"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Get staff information
        staff = User.query.get(staff_id)
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404

        # Get the single shift management for this staff
        shift_management = ShiftManagement.query.filter_by(staff_id=staff_id).first()
        
        if not shift_management:
            return jsonify({
                'success': False,
                'error': 'No schedule found for this staff member'
            }), 404
        
        # Get all shift logs for this staff
        logs = ShiftLogs.query.filter_by(shift_management_id=shift_management.id).order_by(ShiftLogs.individual_date).all()
        all_logs = []
        for log in logs:
            all_logs.append({
                'range_id': shift_management.id,
                'date': log.individual_date.strftime('%Y-%m-%d'),
                'day_name': log.individual_date.strftime('%A'),
                'is_working': True,
                'start_time_12h': log.shift_start_time.strftime('%I:%M %p') if log.shift_start_time else None,
                'end_time_12h': log.shift_end_time.strftime('%I:%M %p') if log.shift_end_time else None,
                'break_time_display': log.get_break_time_display(),
                'out_of_office_display': log.get_out_of_office_display() if log.out_of_office_start else None,
                'notes': '',
                'status': log.status
            })

        # Prepare schedule range (single entry)
        first_log = ShiftLogs.query.filter_by(shift_management_id=shift_management.id).first()
        
        schedule_ranges = [{
            'id': shift_management.id,
            'schedule_name': f"Staff Schedule ({shift_management.from_date.strftime('%Y-%m-%d')} to {shift_management.to_date.strftime('%Y-%m-%d')})",
            'start_date': shift_management.from_date.strftime('%Y-%m-%d'),
            'end_date': shift_management.to_date.strftime('%Y-%m-%d'),
            'shift_start_time_12h': first_log.shift_start_time.strftime('%I:%M %p') if first_log and first_log.shift_start_time else '',
            'shift_end_time_12h': first_log.shift_end_time.strftime('%I:%M %p') if first_log and first_log.shift_end_time else '',
            'working_days_str': f'Total {len(logs)} working days',
            'break_time': first_log.get_break_time_display() if first_log else 'No break',
            'description': f'Last updated: {shift_management.updated_at.strftime("%Y-%m-%d %H:%M") if shift_management.updated_at else "N/A"}'
        }]

        return jsonify({
            'success': True,
            'staff': {
                'id': staff.id,
                'name': f"{staff.first_name} {staff.last_name}",
                'role': staff.role
            },
            'schedule_ranges': schedule_ranges,
            'daily_schedules': all_logs
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoint to get schedule details for edit mode
@shift_scheduler_bp.route('/api/schedule/<int:schedule_id>/details', methods=['GET'])
@login_required
def api_get_schedule_details(schedule_id):
    """Get detailed schedule information for edit mode"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Get shift management record
        shift_management = ShiftManagement.query.get(schedule_id)
        if not shift_management:
            return jsonify({'error': 'Schedule not found'}), 404

        # Get staff information
        staff = User.query.get(shift_management.staff_id)
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404

        # Get all shift logs for this management record
        shift_logs = ShiftLogs.query.filter_by(shift_management_id=schedule_id).order_by(ShiftLogs.individual_date).all()

        # Prepare schedule days data
        schedule_days = []
        for log in shift_logs:
            # Calculate break minutes safely
            break_minutes = 60  # Default
            if log.break_start_time and log.break_end_time:
                break_start_minutes = log.break_start_time.hour * 60 + log.break_start_time.minute
                break_end_minutes = log.break_end_time.hour * 60 + log.break_end_time.minute
                break_minutes = max(0, break_end_minutes - break_start_minutes)
            
            schedule_days.append({
                'date': log.individual_date.strftime('%Y-%m-%d'),
                'working': True,  # All logs represent working days
                'startTime': log.shift_start_time.strftime('%H:%M') if log.shift_start_time else '09:00',
                'endTime': log.shift_end_time.strftime('%H:%M') if log.shift_end_time else '17:00',
                'breakStart': log.break_start_time.strftime('%H:%M') if log.break_start_time else '13:00',
                'breakEnd': log.break_end_time.strftime('%H:%M') if log.break_end_time else '14:00',
                'breakMinutes': break_minutes,
                'notes': ''
            })

        # Prepare schedule data
        schedule_data = {
            'id': shift_management.id,
            'staff_id': shift_management.staff_id,
            'staff_name': f"{staff.first_name} {staff.last_name}",
            'schedule_name': f"Shift {shift_management.from_date.strftime('%Y-%m-%d')} to {shift_management.to_date.strftime('%Y-%m-%d')}",
            'description': '',
            'priority': 1,  # Default priority
            'start_date': shift_management.from_date.strftime('%Y-%m-%d'),
            'end_date': shift_management.to_date.strftime('%Y-%m-%d'),
            'shift_start_time': schedule_days[0]['startTime'] if schedule_days else '09:00',
            'shift_end_time': schedule_days[0]['endTime'] if schedule_days else '17:00',
            'schedule_days': schedule_days
        }

        return jsonify({
            'success': True,
            'schedule': schedule_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete schedules
@shift_scheduler_bp.route('/delete', methods=['POST'])
@login_required
def delete_shift_schedules():
    """Delete shift schedules by IDs"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        data = request.get_json()
        schedule_ids = data.get('schedule_ids', [])

        if not schedule_ids:
            return jsonify({'error': 'No schedule IDs provided'}), 400

        deleted_count = 0
        for schedule_id in schedule_ids:
            schedule = ShiftManagement.query.get(schedule_id)
            if schedule:
                # Delete associated shift logs first (handled by cascade)
                db.session.delete(schedule)
                deleted_count += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Successfully deleted {deleted_count} schedule(s)',
            'deleted_count': deleted_count
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete single schedule by ID (for frontend compatibility)
@shift_scheduler_bp.route('/api/schedule/<int:schedule_id>', methods=['DELETE'])
@login_required
def delete_single_schedule(schedule_id):
    """Delete a single schedule by ID - Frontend compatibility endpoint"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        schedule = ShiftManagement.query.get(schedule_id)
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        # Delete the schedule (cascade will handle shift logs)
        db.session.delete(schedule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Schedule deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Update existing schedule
@shift_scheduler_bp.route('/api/shift-scheduler/update-daily-schedule/<int:schedule_id>', methods=['PUT'])
@login_required
def update_daily_schedule(schedule_id):
    """Update existing schedule with day-by-day configuration"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        data = request.get_json()
        staff_id = data.get('staff_id')
        schedule_name = data.get('schedule_name')
        description = data.get('description', '')
        priority = data.get('priority', 1)
        schedule_days = data.get('schedule_days', [])

        if not staff_id or not schedule_name or not schedule_days:
            return jsonify({'error': 'Missing required data'}), 400

        # Get existing shift management record
        shift_management = ShiftManagement.query.get(schedule_id)
        if not shift_management:
            return jsonify({'error': 'Schedule not found'}), 404

        # Verify staff member exists
        staff = User.query.get(staff_id)
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404

        # Get date range from schedule days
        working_days = [day for day in schedule_days if day.get('working', False)]
        if not working_days:
            return jsonify({'error': 'No working days specified'}), 400

        # Sort days by date
        working_days.sort(key=lambda x: x['date'])
        from_date = datetime.strptime(working_days[0]['date'], '%Y-%m-%d').date()
        to_date = datetime.strptime(working_days[-1]['date'], '%Y-%m-%d').date()

        # Update shift management entry
        shift_management.staff_id = staff_id
        shift_management.from_date = from_date
        shift_management.to_date = to_date

        # Delete existing shift logs
        ShiftLogs.query.filter_by(shift_management_id=schedule_id).delete()

        # Create new shift logs for each working day
        logs_updated = 0
        for day in working_days:
            day_date = datetime.strptime(day['date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(day['startTime'], '%H:%M').time() if day.get('startTime') else None
            end_time = datetime.strptime(day['endTime'], '%H:%M').time() if day.get('endTime') else None
            break_start = datetime.strptime(day['breakStart'], '%H:%M').time() if day.get('breakStart') else None
            break_end = datetime.strptime(day['breakEnd'], '%H:%M').time() if day.get('breakEnd') else None
            
            # Out of office / field work
            out_start = datetime.strptime(day['outOfOfficeStart'], '%H:%M').time() if day.get('outOfOfficeStart') else None
            out_end = datetime.strptime(day['outOfOfficeEnd'], '%H:%M').time() if day.get('outOfOfficeEnd') else None
            out_reason = day.get('outOfOfficeReason', '')

            shift_log = ShiftLogs(
                shift_management_id=shift_management.id,
                individual_date=day_date,
                shift_start_time=start_time,
                shift_end_time=end_time,
                break_start_time=break_start,
                break_end_time=break_end,
                out_of_office_start=out_start,
                out_of_office_end=out_end,
                out_of_office_reason=out_reason,
                status='scheduled'
            )
            db.session.add(shift_log)
            logs_updated += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Schedule updated successfully! Updated {logs_updated} shift log(s)',
            'shift_management_id': shift_management.id,
            'logs_updated': logs_updated
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API endpoint to view database records - shows SQL INSERT statements
@shift_scheduler_bp.route('/api/database-records', methods=['GET'])
@login_required
def api_get_database_records():
    """Get database records as SQL INSERT statements for demonstration"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Get all shift managements
        shift_managements = ShiftManagement.query.order_by(ShiftManagement.created_at.desc()).all()
        
        # Get all shift logs
        shift_logs = ShiftLogs.query.join(ShiftManagement).order_by(
            ShiftManagement.created_at.desc(), 
            ShiftLogs.individual_date
        ).all()

        # Prepare management records with SQL statements
        management_records = []
        for management in shift_managements:
            staff = User.query.get(management.staff_id)
            created_at_str = management.created_at.strftime('%Y-%m-%d %H:%M:%S') if management.created_at else 'NOW()'
            
            sql_statement = f"INSERT INTO shift_management (staff_id, from_date, to_date, created_at) VALUES ({management.staff_id}, '{management.from_date}', '{management.to_date}', '{created_at_str}')"
            
            management_records.append({
                'sql_statement': sql_statement,
                'record_data': {
                    'staff_name': f"{staff.first_name} {staff.last_name}" if staff else 'Unknown',
                    'from_date': management.from_date.strftime('%Y-%m-%d'),
                    'to_date': management.to_date.strftime('%Y-%m-%d')
                }
            })

        # Prepare log records with SQL statements
        log_records = []
        for log in shift_logs:
            created_at_str = log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else 'NOW()'
            break_start = log.break_start_time.strftime('%H:%M:%S') if log.break_start_time else 'NULL'
            break_end = log.break_end_time.strftime('%H:%M:%S') if log.break_end_time else 'NULL'
            
            sql_statement = f"INSERT INTO shift_logs (shift_management_id, individual_date, shift_start_time, shift_end_time, break_start_time, break_end_time, status, created_at) VALUES ({log.shift_management_id}, '{log.individual_date}', '{log.shift_start_time}', '{log.shift_end_time}', {break_start if break_start != 'NULL' else break_start}, {break_end if break_end != 'NULL' else break_end}, '{log.status}', '{created_at_str}')"
            
            log_records.append({
                'sql_statement': sql_statement,
                'record_data': {
                    'day_name': log.individual_date.strftime('%A'),
                    'individual_date': log.individual_date.strftime('%Y-%m-%d'),
                    'shift_start_time': log.shift_start_time.strftime('%H:%M:%S') if log.shift_start_time else 'NULL',
                    'shift_end_time': log.shift_end_time.strftime('%H:%M:%S') if log.shift_end_time else 'NULL',
                    'break_start_time': log.break_start_time.strftime('%H:%M:%S') if log.break_start_time else 'None',
                    'break_end_time': log.break_end_time.strftime('%H:%M:%S') if log.break_end_time else 'None'
                }
            })

        # Create summary
        summary = f"Found {len(management_records)} shift management records and {len(log_records)} individual shift log records in the database."

        return jsonify({
            'success': True,
            'summary': summary,
            'total_management_records': len(management_records),
            'total_log_records': len(log_records),
            'management_records': management_records,
            'log_records': log_records
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

print("Shift Scheduler views registered successfully")
