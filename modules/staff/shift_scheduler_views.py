"""
Staff Shift Scheduler Views
Handles shift scheduling functionality for staff management
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models import User, StaffSchedule
from .staff_queries import get_all_staff
from datetime import datetime, timedelta

# Create blueprint for shift scheduler
shift_scheduler_bp = Blueprint('shift_scheduler', __name__, url_prefix='/shift-scheduler')

@shift_scheduler_bp.route('/')
@login_required
def shift_scheduler():
    """Main shift scheduler page"""
    if not current_user.can_access('staff'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get all staff members for selection
    staff_members = get_all_staff()
    
    return render_template('shift_scheduler.html', staff_members=staff_members)

@shift_scheduler_bp.route('/api/staff/<int:staff_id>/day-schedule', methods=['POST'])
@login_required
def api_staff_day_schedule(staff_id):
    """API endpoint for saving day schedule"""
    if not current_user.can_access('staff'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Process the schedule data here
        # This is a placeholder - implement based on your StaffSchedule model structure
        
        return jsonify({'success': True, 'message': 'Schedule saved successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@shift_scheduler_bp.route('/api/staff/<int:staff_id>/schedule', methods=['GET'])
@login_required
def api_get_staff_schedule(staff_id):
    """API endpoint for getting staff schedule"""
    if not current_user.can_access('staff'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Get existing schedules for the staff member
        # This is a placeholder - implement based on your StaffSchedule model structure
        schedules = []
        
        return jsonify({'success': True, 'schedules': schedules})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500