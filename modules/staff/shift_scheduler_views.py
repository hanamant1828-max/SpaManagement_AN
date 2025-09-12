"""
Staff Shift Scheduler Views
Complete implementation with CRUD operations for staff scheduling
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from werkzeug.exceptions import BadRequest
from app import app, db
from models import User, StaffScheduleRange
from datetime import datetime, date, timedelta
import json

# Create Blueprint for shift scheduler
shift_scheduler_bp = Blueprint('shift_scheduler', __name__)

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

# API endpoint to get existing schedules for UI hydration
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
        
        # Get all schedule ranges that overlap with the requested date range
        schedules = StaffScheduleRange.query.filter(
            StaffScheduleRange.staff_id == staff_id,
            StaffScheduleRange.is_active == True,
            StaffScheduleRange.start_date <= end_date,
            StaffScheduleRange.end_date >= start_date
        ).order_by(StaffScheduleRange.start_date).all()
        
        schedule_data = []
        for schedule in schedules:
            schedule_data.append({
                'id': schedule.id,
                'schedule_name': schedule.schedule_name,
                'description': schedule.description or '',
                'start_date': schedule.start_date.strftime('%Y-%m-%d'),
                'end_date': schedule.end_date.strftime('%Y-%m-%d'),
                'monday': schedule.monday,
                'tuesday': schedule.tuesday,
                'wednesday': schedule.wednesday,
                'thursday': schedule.thursday,
                'friday': schedule.friday,
                'saturday': schedule.saturday,
                'sunday': schedule.sunday,
                'shift_start_time': schedule.shift_start_time.strftime('%H:%M') if schedule.shift_start_time else '',
                'shift_end_time': schedule.shift_end_time.strftime('%H:%M') if schedule.shift_end_time else '',
                'break_time': schedule.break_time or '',
                'priority': schedule.priority or 1
            })
        
        return jsonify({
            'success': True,
            'schedules': schedule_data,
            'staff_id': staff_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Bulk save schedule ranges
@shift_scheduler_bp.route('/shift-scheduler/save', methods=['POST'])
@login_required
def save_shift_schedule():
    """Bulk save/update shift schedules"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403
    
    # CSRF Protection
    try:
        validate_csrf(request.form.get('csrf_token') or request.json.get('csrf_token'))
    except Exception as e:
        return jsonify({'error': 'CSRF token validation failed'}), 400
    
    try:
        data = request.get_json()
        staff_id = data.get('staff_id')
        schedule_data = data.get('schedule_data', [])
        
        if not staff_id or not schedule_data:
            return jsonify({'error': 'Missing required data'}), 400
        
        # Verify staff member exists
        staff = User.query.get(staff_id)
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404
        
        created_count = 0
        updated_count = 0
        errors = []
        
        for item in schedule_data:
            try:
                # Parse dates
                start_date = datetime.strptime(item['start_date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(item['end_date'], '%Y-%m-%d').date()
                
                # Parse times
                shift_start_time = None
                shift_end_time = None
                if item.get('shift_start_time'):
                    shift_start_time = datetime.strptime(item['shift_start_time'], '%H:%M').time()
                if item.get('shift_end_time'):
                    shift_end_time = datetime.strptime(item['shift_end_time'], '%H:%M').time()
                
                # Check if schedule already exists for this date range
                existing_schedule = StaffScheduleRange.query.filter(
                    StaffScheduleRange.staff_id == staff_id,
                    StaffScheduleRange.start_date == start_date,
                    StaffScheduleRange.end_date == end_date,
                    StaffScheduleRange.is_active == True
                ).first()
                
                if existing_schedule:
                    # Update existing schedule
                    existing_schedule.schedule_name = item.get('schedule_name', 'Updated Schedule')
                    existing_schedule.description = item.get('description', '')
                    existing_schedule.monday = item.get('monday', True)
                    existing_schedule.tuesday = item.get('tuesday', True)
                    existing_schedule.wednesday = item.get('wednesday', True)
                    existing_schedule.thursday = item.get('thursday', True)
                    existing_schedule.friday = item.get('friday', True)
                    existing_schedule.saturday = item.get('saturday', False)
                    existing_schedule.sunday = item.get('sunday', False)
                    existing_schedule.shift_start_time = shift_start_time
                    existing_schedule.shift_end_time = shift_end_time
                    existing_schedule.break_time = item.get('break_time', '')
                    existing_schedule.priority = item.get('priority', 1)
                    existing_schedule.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    # Create new schedule
                    new_schedule = StaffScheduleRange(
                        staff_id=staff_id,
                        schedule_name=item.get('schedule_name', 'New Schedule'),
                        description=item.get('description', ''),
                        start_date=start_date,
                        end_date=end_date,
                        monday=item.get('monday', True),
                        tuesday=item.get('tuesday', True),
                        wednesday=item.get('wednesday', True),
                        thursday=item.get('thursday', True),
                        friday=item.get('friday', True),
                        saturday=item.get('saturday', False),
                        sunday=item.get('sunday', False),
                        shift_start_time=shift_start_time,
                        shift_end_time=shift_end_time,
                        break_time=item.get('break_time', ''),
                        priority=item.get('priority', 1)
                    )
                    db.session.add(new_schedule)
                    created_count += 1
                    
            except Exception as item_error:
                errors.append(f"Error processing item: {str(item_error)}")
                continue
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Schedule saved successfully. Created: {created_count}, Updated: {updated_count}',
            'created_count': created_count,
            'updated_count': updated_count,
            'errors': errors
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Bulk delete schedules
@shift_scheduler_bp.route('/shift-scheduler/delete', methods=['POST'])
@login_required
def delete_shift_schedules():
    """Bulk delete shift schedules by IDs or date range"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403
    
    # CSRF Protection
    try:
        validate_csrf(request.form.get('csrf_token') or request.json.get('csrf_token'))
    except Exception as e:
        return jsonify({'error': 'CSRF token validation failed'}), 400
    
    try:
        data = request.get_json()
        schedule_ids = data.get('schedule_ids', [])
        staff_id = data.get('staff_id')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        
        deleted_count = 0
        
        if schedule_ids:
            # Delete by specific IDs
            schedules = StaffScheduleRange.query.filter(
                StaffScheduleRange.id.in_(schedule_ids),
                StaffScheduleRange.is_active == True
            ).all()
            
            for schedule in schedules:
                schedule.is_active = False
                deleted_count += 1
                
        elif staff_id and start_date_str and end_date_str:
            # Delete by date range
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            schedules = StaffScheduleRange.query.filter(
                StaffScheduleRange.staff_id == staff_id,
                StaffScheduleRange.start_date >= start_date,
                StaffScheduleRange.end_date <= end_date,
                StaffScheduleRange.is_active == True
            ).all()
            
            for schedule in schedules:
                schedule.is_active = False
                deleted_count += 1
        else:
            return jsonify({'error': 'Must provide either schedule_ids or staff_id with date range'}), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted {deleted_count} schedule(s)',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get all existing schedules for a staff member
@shift_scheduler_bp.route('/api/staff/<int:staff_id>/all-schedules', methods=['GET'])
@login_required
def api_get_all_staff_schedules(staff_id):
    """Get all existing schedules for a staff member"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        schedules = StaffScheduleRange.query.filter_by(
            staff_id=staff_id, 
            is_active=True
        ).order_by(StaffScheduleRange.start_date).all()
        
        schedule_list = []
        for schedule in schedules:
            # Get working days list
            working_days = []
            if schedule.monday: working_days.append('Mon')
            if schedule.tuesday: working_days.append('Tue') 
            if schedule.wednesday: working_days.append('Wed')
            if schedule.thursday: working_days.append('Thu')
            if schedule.friday: working_days.append('Fri')
            if schedule.saturday: working_days.append('Sat')
            if schedule.sunday: working_days.append('Sun')
            
            schedule_list.append({
                'id': schedule.id,
                'schedule_name': schedule.schedule_name,
                'description': schedule.description or '',
                'start_date': schedule.start_date.strftime('%Y-%m-%d'),
                'end_date': schedule.end_date.strftime('%Y-%m-%d'),
                'working_days': working_days,
                'shift_start_time': schedule.shift_start_time.strftime('%H:%M') if schedule.shift_start_time else '',
                'shift_end_time': schedule.shift_end_time.strftime('%H:%M') if schedule.shift_end_time else '',
                'break_time': schedule.break_time or '',
                'priority': schedule.priority or 1,
                'created_at': schedule.created_at.strftime('%Y-%m-%d %H:%M') if schedule.created_at else ''
            })
        
        return jsonify({
            'success': True,
            'schedules': schedule_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update single schedule
@shift_scheduler_bp.route('/api/schedule/<int:schedule_id>', methods=['PUT'])
@login_required 
def api_update_schedule(schedule_id):
    """Update a single schedule"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        schedule = StaffScheduleRange.query.get_or_404(schedule_id)
        data = request.get_json()
        
        # Update fields
        if 'schedule_name' in data:
            schedule.schedule_name = data['schedule_name']
        if 'description' in data:
            schedule.description = data['description']
        if 'start_date' in data:
            schedule.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in data:
            schedule.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        # Update working days
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            if day in data:
                setattr(schedule, day, data[day])
        
        # Update times
        if 'shift_start_time' in data and data['shift_start_time']:
            schedule.shift_start_time = datetime.strptime(data['shift_start_time'], '%H:%M').time()
        if 'shift_end_time' in data and data['shift_end_time']:
            schedule.shift_end_time = datetime.strptime(data['shift_end_time'], '%H:%M').time()
        if 'break_time' in data:
            schedule.break_time = data['break_time']
        if 'priority' in data:
            schedule.priority = data['priority']
        
        schedule.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Schedule updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete single schedule
@shift_scheduler_bp.route('/api/schedule/<int:schedule_id>', methods=['DELETE'])
@login_required
def api_delete_schedule(schedule_id):
    """Delete a single schedule"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        schedule = StaffScheduleRange.query.get_or_404(schedule_id)
        schedule.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Schedule deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

print("Shift Scheduler views registered successfully")