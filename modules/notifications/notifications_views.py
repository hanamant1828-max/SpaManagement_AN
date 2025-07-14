"""
Notifications views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app
from .notifications_queries import (
    get_recent_communications, get_pending_notifications,
    create_notification, mark_notification_sent, get_clients_for_reminders
)

@app.route('/notifications')
@login_required
def notifications():
    if not current_user.can_access('notifications'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    recent_communications = get_recent_communications()
    pending_notifications = get_pending_notifications()
    
    return render_template('notifications.html', 
                         recent_communications=recent_communications,
                         pending_notifications=pending_notifications)

@app.route('/notifications/send-reminders', methods=['POST'])
@login_required
def send_appointment_reminders():
    if not current_user.can_access('notifications'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    appointments = get_clients_for_reminders()
    sent_count = 0
    
    for appointment in appointments:
        notification_data = {
            'client_id': appointment.client_id,
            'communication_type': 'sms',
            'subject': 'Appointment Reminder',
            'content': f'Hi {appointment.client.first_name}, you have an appointment tomorrow at {appointment.appointment_date.strftime("%I:%M %p")}',
            'status': 'pending',
            'created_by': current_user.id
        }
        
        create_notification(notification_data)
        sent_count += 1
    
    flash(f'Sent {sent_count} appointment reminders', 'success')
    return redirect(url_for('notifications'))

@app.route('/notifications/mark-sent/<int:id>', methods=['POST'])
@login_required
def mark_notification_sent_route(id):
    if not current_user.can_access('notifications'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    notification = mark_notification_sent(id)
    if notification:
        flash('Notification marked as sent', 'success')
    else:
        flash('Notification not found', 'danger')
    
    return redirect(url_for('notifications'))