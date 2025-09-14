"""
Staff Shift Scheduler Views
Complete implementation with CRUD operations for staff scheduling
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.exceptions import BadRequest
from app import app, db
from models import User, StaffScheduleRange
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
                # Handle date field normalization (date -> start_date/end_date)
                if 'date' in item and ('start_date' not in item or 'end_date' not in item):
                    item['start_date'] = item['date']
                    item['end_date'] = item['date']
                
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
        
        # If no schedules were created or updated, return error instead of success
        if created_count == 0 and updated_count == 0:
            return jsonify({
                'success': False,
                'error': 'No schedules were saved. Please check your data and try again.',
                'errors': errors
            }), 400
        
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

# Enhanced update that supports date range changes
@shift_scheduler_bp.route('/api/schedule/<int:schedule_id>/update-with-range', methods=['PUT'])
@login_required 
def api_update_schedule_with_range(schedule_id):
    """Update a schedule with support for date range changes"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        schedule = StaffScheduleRange.query.get_or_404(schedule_id)
        data = request.get_json()
        
        # Get original dates for comparison
        original_start = schedule.start_date
        original_end = schedule.end_date
        
        # Parse new dates
        new_start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else original_start
        new_end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else original_end
        
        # Check if this is a date range update
        date_range_changed = (new_start_date != original_start or new_end_date != original_end)
        
        if date_range_changed:
            # Create a new schedule with the new date range and delete the old one
            # This ensures proper date range handling
            
            # Create new schedule with updated data
            new_schedule = StaffScheduleRange(
                staff_id=schedule.staff_id,
                schedule_name=data.get('schedule_name', schedule.schedule_name),
                description=data.get('description', schedule.description),
                start_date=new_start_date,
                end_date=new_end_date,
                monday=data.get('monday', schedule.monday),
                tuesday=data.get('tuesday', schedule.tuesday),
                wednesday=data.get('wednesday', schedule.wednesday),
                thursday=data.get('thursday', schedule.thursday),
                friday=data.get('friday', schedule.friday),
                saturday=data.get('saturday', schedule.saturday),
                sunday=data.get('sunday', schedule.sunday),
                shift_start_time=datetime.strptime(data['shift_start_time'], '%H:%M').time() if data.get('shift_start_time') else schedule.shift_start_time,
                shift_end_time=datetime.strptime(data['shift_end_time'], '%H:%M').time() if data.get('shift_end_time') else schedule.shift_end_time,
                break_time=data.get('break_time', schedule.break_time),
                priority=data.get('priority', schedule.priority),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Add new schedule and mark old one as inactive
            db.session.add(new_schedule)
            schedule.is_active = False
            schedule.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Schedule updated with new date range ({new_start_date} to {new_end_date})',
                'new_schedule_id': new_schedule.id,
                'date_range_changed': True
            })
        else:
            # Regular update without date range change
            if 'schedule_name' in data:
                schedule.schedule_name = data['schedule_name']
            if 'description' in data:
                schedule.description = data['description']
            
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
                'message': 'Schedule updated successfully',
                'date_range_changed': False
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

# Get single schedule details
@shift_scheduler_bp.route('/api/schedule/<int:schedule_id>/details', methods=['GET'])
@login_required
def api_get_schedule_details(schedule_id):
    """Get detailed information for a single schedule"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        schedule = StaffScheduleRange.query.get(schedule_id)
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        # Get staff information
        staff = User.query.get(schedule.staff_id)
        
        # Get working days list
        working_days = []
        if schedule.monday: working_days.append('Mon')
        if schedule.tuesday: working_days.append('Tue') 
        if schedule.wednesday: working_days.append('Wed')
        if schedule.thursday: working_days.append('Thu')
        if schedule.friday: working_days.append('Fri')
        if schedule.saturday: working_days.append('Sat')
        if schedule.sunday: working_days.append('Sun')
        
        schedule_data = {
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
            'working_days': working_days,
            'shift_start_time': schedule.shift_start_time.strftime('%H:%M') if schedule.shift_start_time else '',
            'shift_end_time': schedule.shift_end_time.strftime('%H:%M') if schedule.shift_end_time else '',
            'break_time': schedule.break_time or '',
            'priority': schedule.priority or 1,
            'is_active': schedule.is_active,
            'staff_id': schedule.staff_id,
            'staff_name': f"{staff.first_name} {staff.last_name}" if staff else 'Unknown',
            'created_at': schedule.created_at.strftime('%Y-%m-%d %H:%M') if schedule.created_at else ''
        }
        
        return jsonify({
            'success': True,
            'schedule': schedule_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get staff details with schedules
@shift_scheduler_bp.route('/api/staff/<int:staff_id>/details', methods=['GET'])
@login_required
def api_get_staff_details(staff_id):
    """Get complete staff details including schedules"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get staff information
        staff = User.query.get_or_404(staff_id)
        
        # Get all schedules for this staff member
        schedules = StaffScheduleRange.query.filter_by(
            staff_id=staff_id, 
            is_active=True
        ).order_by(StaffScheduleRange.start_date).all()
        
        # Format staff data
        staff_data = {
            'id': staff.id,
            'first_name': staff.first_name,
            'last_name': staff.last_name,
            'email': staff.email,
            'phone': getattr(staff, 'phone', None),
            'address': getattr(staff, 'address', None),
            'role': staff.role,
            'hire_date': getattr(staff, 'hire_date', None),
            'is_active': staff.is_active,
            'created_at': staff.created_at.strftime('%Y-%m-%d') if hasattr(staff, 'created_at') and staff.created_at else None
        }
        
        # Format schedules data
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
            
            # Format working days string
            if len(working_days) == 7:
                working_days_str = "All Days"
            elif len(working_days) == 5 and 'Sat' not in working_days and 'Sun' not in working_days:
                working_days_str = "Mon to Fri"
            else:
                working_days_str = ", ".join(working_days)
            
            schedule_list.append({
                'id': schedule.id,
                'schedule_name': schedule.schedule_name,
                'description': schedule.description or '',
                'start_date': schedule.start_date.strftime('%Y-%m-%d'),
                'end_date': schedule.end_date.strftime('%Y-%m-%d'),
                'working_days': working_days,
                'working_days_str': working_days_str,
                'shift_start_time': schedule.shift_start_time.strftime('%H:%M') if schedule.shift_start_time else '',
                'shift_end_time': schedule.shift_end_time.strftime('%H:%M') if schedule.shift_end_time else '',
                'break_time': schedule.break_time or '',
                'priority': schedule.priority or 1,
                'created_at': schedule.created_at.strftime('%Y-%m-%d %H:%M') if schedule.created_at else ''
            })
        
        return jsonify({
            'success': True,
            'staff': staff_data,
            'schedules': schedule_list,
            'schedules_count': len(schedule_list)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Save daily schedule with day-by-day configuration
@shift_scheduler_bp.route('/api/shift-scheduler/save-daily-schedule', methods=['POST'])
@login_required
def save_daily_schedule():
    """Save schedule with day-by-day configuration"""
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
        
        # Group consecutive days with same settings into ranges
        ranges_created = 0
        current_range = None
        
        for day in schedule_days:
            if not day.get('working', False):
                continue  # Skip non-working days
            
            day_date = datetime.strptime(day['date'], '%Y-%m-%d').date()
            
            # Convert day of week to boolean fields
            day_of_week = day_date.weekday()  # Monday = 0, Sunday = 6
            day_booleans = {
                'monday': day_of_week == 0,
                'tuesday': day_of_week == 1,
                'wednesday': day_of_week == 2,
                'thursday': day_of_week == 3,
                'friday': day_of_week == 4,
                'saturday': day_of_week == 5,
                'sunday': day_of_week == 6
            }
            
            # Check if we can extend current range or need to create new one
            if (current_range and 
                current_range['end_date'] == day_date - timedelta(days=1) and
                current_range['start_time'] == day.get('startTime') and
                current_range['end_time'] == day.get('endTime') and
                current_range['break_minutes'] == day.get('breakMinutes')):
                
                # Extend current range
                current_range['end_date'] = day_date
                # Update day boolean
                for day_key, day_val in day_booleans.items():
                    if day_val:
                        current_range[day_key] = True
            else:
                # Save previous range if exists
                if current_range:
                    save_range(current_range, staff_id, schedule_name, description, priority)
                    ranges_created += 1
                
                # Start new range
                current_range = {
                    'start_date': day_date,
                    'end_date': day_date,
                    'start_time': day.get('startTime'),
                    'end_time': day.get('endTime'),
                    'break_minutes': day.get('breakMinutes', 60),
                    **day_booleans
                }
        
        # Save final range
        if current_range:
            save_range(current_range, staff_id, schedule_name, description, priority)
            ranges_created += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Schedule saved successfully! Created {ranges_created} schedule range(s)',
            'ranges_created': ranges_created
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def save_range(range_data, staff_id, schedule_name, description, priority):
    """Helper function to save a schedule range"""
    shift_start_time = None
    shift_end_time = None
    
    if range_data.get('start_time'):
        shift_start_time = datetime.strptime(range_data['start_time'], '%H:%M').time()
    if range_data.get('end_time'):
        shift_end_time = datetime.strptime(range_data['end_time'], '%H:%M').time()
    
    schedule_range = StaffScheduleRange(
        staff_id=staff_id,
        schedule_name=f"{schedule_name} ({range_data['start_date']} to {range_data['end_date']})",
        description=description,
        start_date=range_data['start_date'],
        end_date=range_data['end_date'],
        monday=range_data.get('monday', False),
        tuesday=range_data.get('tuesday', False),
        wednesday=range_data.get('wednesday', False),
        thursday=range_data.get('thursday', False),
        friday=range_data.get('friday', False),
        saturday=range_data.get('saturday', False),
        sunday=range_data.get('sunday', False),
        shift_start_time=shift_start_time,
        shift_end_time=shift_end_time,
        break_time=f"{range_data.get('break_minutes', 60)} minutes",
        priority=priority
    )
    
    db.session.add(schedule_range)

# Get all schedules from all staff members for management table
@shift_scheduler_bp.route('/api/all-schedules', methods=['GET'])
@login_required
def api_get_all_schedules():
    """Get all existing schedules from all staff members for the management table"""
    if not current_user.can_access('staff'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get all active schedules with staff information
        schedules = db.session.query(StaffScheduleRange, User).join(
            User, StaffScheduleRange.staff_id == User.id
        ).filter(
            StaffScheduleRange.is_active == True,
            User.is_active == True
        ).order_by(User.first_name, User.last_name, StaffScheduleRange.start_date).all()
        
        schedule_list = []
        for schedule, staff in schedules:
            # Get working days list
            working_days = []
            if schedule.monday: working_days.append('Mon')
            if schedule.tuesday: working_days.append('Tue') 
            if schedule.wednesday: working_days.append('Wed')
            if schedule.thursday: working_days.append('Thu')
            if schedule.friday: working_days.append('Fri')
            if schedule.saturday: working_days.append('Sat')
            if schedule.sunday: working_days.append('Sun')
            
            # Format working days string
            if len(working_days) == 7:
                working_days_str = "All Days"
            elif len(working_days) == 5 and 'Sat' not in working_days and 'Sun' not in working_days:
                working_days_str = "Mon to Fri"
            else:
                working_days_str = ", ".join(working_days)
            
            schedule_list.append({
                'id': schedule.id,
                'staff_id': staff.id,
                'staff_name': f"{staff.first_name} {staff.last_name}",
                'schedule_name': schedule.schedule_name,
                'description': schedule.description or '',
                'start_date': schedule.start_date.strftime('%Y-%m-%d'),
                'end_date': schedule.end_date.strftime('%Y-%m-%d'),
                'working_days': working_days,
                'working_days_str': working_days_str,
                'shift_start_time': schedule.shift_start_time.strftime('%H:%M') if schedule.shift_start_time else '',
                'shift_end_time': schedule.shift_end_time.strftime('%H:%M') if schedule.shift_end_time else '',
                'break_time': schedule.break_time or '',
                'priority': schedule.priority or 1,
                'created_at': schedule.created_at.strftime('%Y-%m-%d %H:%M') if schedule.created_at else ''
            })
        
        return jsonify({
            'success': True,
            'schedules': schedule_list,
            'total_count': len(schedule_list)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

print("Shift Scheduler views registered successfully")