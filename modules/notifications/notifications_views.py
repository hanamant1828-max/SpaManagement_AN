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
    
    from modules.clients.clients_queries import get_all_customers
    from models import Appointment
    from datetime import datetime, timedelta
    
    recent_communications = get_recent_communications()
    pending_notifications = get_pending_notifications()
    
    # Get all active customers for the message sending feature
    all_customers = get_all_customers()
    
    # Get upcoming appointments for reminders
    tomorrow = datetime.now() + timedelta(days=1)
    upcoming_appointments = Appointment.query.filter(
        Appointment.appointment_date >= datetime.now(),
        Appointment.appointment_date <= tomorrow,
        Appointment.status.in_(['scheduled', 'confirmed'])
    ).all()
    
    # Get expiring packages (placeholder for now)
    expiring_packages = []
    
    return render_template('notifications.html', 
                         recent_communications=recent_communications,
                         pending_notifications=pending_notifications,
                         all_customers=all_customers,
                         upcoming_appointments=upcoming_appointments,
                         expiring_packages=expiring_packages)

@app.route('/notifications/send-reminders', methods=['POST'])
@login_required
def send_appointment_reminders():
    if not current_user.can_access('notifications'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    from .notifications_queries import send_whatsapp_message
    
    appointments = get_clients_for_reminders()
    sent_count = 0
    failed_count = 0
    
    for appointment in appointments:
        client = appointment.client
        message = f"Hi {client.first_name}, this is a reminder that you have an appointment tomorrow at {appointment.appointment_date.strftime('%I:%M %p')} for {appointment.service.name}. See you soon!"
        
        # Send WhatsApp message
        if client.phone:
            success = send_whatsapp_message(client.phone, message)
            
            # Log the communication
            notification_data = {
                'client_id': appointment.client_id,
                'type': 'whatsapp',
                'subject': 'Appointment Reminder',
                'message': message,
                'status': 'sent' if success else 'failed',
                'created_by': current_user.id
            }
            create_notification(notification_data)
            
            if success:
                sent_count += 1
            else:
                failed_count += 1
        else:
            failed_count += 1
    
    if failed_count > 0:
        flash(f'Sent {sent_count} WhatsApp reminders, {failed_count} failed', 'warning')
    else:
        flash(f'Sent {sent_count} WhatsApp reminders successfully', 'success')
    
    return redirect(url_for('notifications'))


@app.route('/notifications/send-single-whatsapp/<int:appointment_id>', methods=['POST'])
@login_required
def send_single_whatsapp_reminder(appointment_id):
    """Send WhatsApp reminder for a single appointment"""
    if not current_user.can_access('notifications'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    from models import Appointment
    from .notifications_queries import send_whatsapp_message
    
    appointment = Appointment.query.get_or_404(appointment_id)
    client = appointment.client
    
    if not client.phone:
        flash('Client has no phone number', 'danger')
        return redirect(url_for('notifications'))
    
    message = f"Hi {client.first_name}, this is a reminder that you have an appointment on {appointment.appointment_date.strftime('%B %d at %I:%M %p')} for {appointment.service.name}. See you soon!"
    
    success = send_whatsapp_message(client.phone, message)
    
    # Log the communication
    notification_data = {
        'client_id': appointment.client_id,
        'type': 'whatsapp',
        'subject': 'Appointment Reminder',
        'message': message,
        'status': 'sent' if success else 'failed',
        'created_by': current_user.id
    }
    create_notification(notification_data)
    
    if success:
        flash(f'WhatsApp reminder sent to {client.full_name}', 'success')
    else:
        flash(f'Failed to send WhatsApp reminder to {client.full_name}', 'danger')
    
    return redirect(url_for('notifications'))
    
    if failed_count > 0:
        flash(f'Sent {sent_count} WhatsApp reminders, {failed_count} failed', 'warning')
    else:
        flash(f'Sent {sent_count} WhatsApp reminders successfully', 'success')
    
    return redirect(url_for('notifications'))

@app.route('/notifications/send-whatsapp', methods=['POST'])
@login_required
def send_whatsapp_message():
    """Send WhatsApp message to selected recipients"""
    if not current_user.can_access('notifications'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    from .notifications_queries import send_whatsapp_message as send_msg
    from models import Customer
    
    recipient_type = request.form.get('recipient_type')
    message = request.form.get('message')
    
    if not message:
        flash('Message is required', 'danger')
        return redirect(url_for('notifications'))
    
    sent_count = 0
    failed_count = 0
    
    if recipient_type == 'single':
        customer_id = request.form.get('customer_id')
        if customer_id:
            customer = Customer.query.get(customer_id)
            if customer and customer.phone:
                success = send_msg(customer.phone, message)
                
                # Log the communication
                notification_data = {
                    'client_id': customer.id,
                    'type': 'whatsapp',
                    'subject': 'Custom Message',
                    'message': message,
                    'status': 'sent' if success else 'failed',
                    'created_by': current_user.id
                }
                create_notification(notification_data)
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
    
    elif recipient_type == 'multiple':
        customer_ids = request.form.getlist('customer_ids[]')
        for customer_id in customer_ids:
            customer = Customer.query.get(customer_id)
            if customer and customer.phone:
                success = send_msg(customer.phone, message)
                
                # Log the communication
                notification_data = {
                    'client_id': customer.id,
                    'type': 'whatsapp',
                    'subject': 'Bulk Message',
                    'message': message,
                    'status': 'sent' if success else 'failed',
                    'created_by': current_user.id
                }
                create_notification(notification_data)
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
    
    elif recipient_type == 'custom':
        custom_phone = request.form.get('custom_phone')
        if custom_phone:
            success = send_msg(custom_phone, message)
            if success:
                sent_count += 1
            else:
                failed_count += 1
    
    if sent_count > 0:
        flash(f'Successfully sent {sent_count} message(s)', 'success')
    if failed_count > 0:
        flash(f'Failed to send {failed_count} message(s)', 'warning')
    
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