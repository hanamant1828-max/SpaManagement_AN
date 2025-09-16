
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
shift_scheduler_bp = Blueprint('shift_scheduler', __name__)

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
    """Main shift scheduler interface"""
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    # Get all active staff members
    staff_members = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()

    return render_template('shift_scheduler.html',
                         staff_members=staff_members,
                         today=date.today().strftime('%Y-%m-%d'))

# API endpoint to get existing schedules
@shift_scheduler_bp.route('/api/shift-scheduler', methods=['GET'])
@login_required
def api_get_shift_schedules():
    """Get existing shift schedules for a staff member in date range"""
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

        # Create shift management entry
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

            shift_log = ShiftLogs(
                shift_management_id=shift_management.id,
                individual_date=day_date,
                shift_start_time=start_time,
                shift_end_time=end_time,
                break_start_time=break_start,
                break_end_time=break_end,
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
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get all schedules from all staff members for management table
@shift_scheduler_bp.route('/api/all-schedules', methods=['GET'])
@login_required
def api_get_all_schedules():
    """Get consolidated schedule view using new shift management schema"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Get all shift managements with staff information
        schedules = db.session.query(ShiftManagement, User).join(
            User, ShiftManagement.staff_id == User.id
        ).filter(
            User.is_active == True
        ).order_by(User.first_name, User.last_name, ShiftManagement.from_date).all()

        # Group schedules by staff member
        staff_schedules = {}
        for schedule, staff in schedules:
            staff_key = f"{staff.id}_{staff.first_name}_{staff.last_name}"

            if staff_key not in staff_schedules:
                staff_schedules[staff_key] = {
                    'staff_id': staff.id,
                    'staff_name': f"{staff.first_name} {staff.last_name}",
                    'schedules': [],
                    'earliest_start': schedule.from_date,
                    'latest_end': schedule.to_date,
                    'total_ranges': 0
                }

            # Track earliest start and latest end dates
            if schedule.from_date < staff_schedules[staff_key]['earliest_start']:
                staff_schedules[staff_key]['earliest_start'] = schedule.from_date
            if schedule.to_date > staff_schedules[staff_key]['latest_end']:
                staff_schedules[staff_key]['latest_end'] = schedule.to_date

            staff_schedules[staff_key]['schedules'].append(schedule)
            staff_schedules[staff_key]['total_ranges'] += 1

        # Create consolidated list
        schedule_list = []
        for staff_key, data in staff_schedules.items():
            # Get the most recent schedule for display info
            latest_schedule = max(data['schedules'], key=lambda x: x.created_at)

            # Get first shift log for working days info
            first_log = ShiftLogs.query.filter_by(shift_management_id=latest_schedule.id).first()
            
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

            schedule_list.append({
                'id': latest_schedule.id,
                'staff_id': data['staff_id'],
                'staff_name': data['staff_name'],
                'schedule_name': f"Shift ({data['total_ranges']} range{'s' if data['total_ranges'] > 1 else ''})",
                'description': '',
                'start_date': data['earliest_start'].strftime('%Y-%m-%d'),
                'end_date': data['latest_end'].strftime('%Y-%m-%d'),
                'working_days': working_days,
                'working_days_str': working_days_str,
                'shift_start_time': shift_start_time,
                'shift_end_time': shift_end_time,
                'shift_start_time_12h': first_log.shift_start_time.strftime('%I:%M %p') if first_log and first_log.shift_start_time else '',
                'shift_end_time_12h': first_log.shift_end_time.strftime('%I:%M %p') if first_log and first_log.shift_end_time else '',
                'break_time': break_time,
                'priority': 1,
                'created_at': latest_schedule.created_at.strftime('%Y-%m-%d %H:%M') if latest_schedule.created_at else '',
                'total_ranges': data['total_ranges'],
                'is_consolidated': True
            })

        return jsonify({
            'success': True,
            'schedules': schedule_list,
            'total_count': len(schedule_list)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete schedules
@shift_scheduler_bp.route('/shift-scheduler/delete', methods=['POST'])
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

print("Shift Scheduler views registered successfully")
