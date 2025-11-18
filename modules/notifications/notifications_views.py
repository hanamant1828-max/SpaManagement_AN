"""
Notifications views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app
from models import Communication, Customer # Import Customer model
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

    import os
    
    return render_template('notifications.html',
                         recent_communications=recent_communications,
                         pending_notifications=pending_notifications,
                         all_customers=all_customers,
                         upcoming_appointments=upcoming_appointments,
                         expiring_packages=expiring_packages,
                         config={
                             'TWILIO_ACCOUNT_SID': os.environ.get('TWILIO_ACCOUNT_SID'),
                             'TWILIO_AUTH_TOKEN': os.environ.get('TWILIO_AUTH_TOKEN')
                         })

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

    # This part of the code seems to be a duplicate and unreachable
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

    # Check if Twilio is configured
    from modules.notifications.notifications_queries import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
    
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        flash('WhatsApp messaging is not configured. Please add Twilio credentials in Secrets (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER)', 'danger')
        return redirect(url_for('notifications'))
    
    if sent_count > 0:
        flash(f'Successfully sent {sent_count} message(s)', 'success')
    if failed_count > 0:
        flash(f'Failed to send {failed_count} message(s). Please check Twilio credentials and phone number format.', 'warning')

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

@app.route('/notifications/report')
@login_required
def notifications_report():
    """WhatsApp messaging report with statistics"""
    if not current_user.can_access('notifications'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from datetime import datetime, timedelta
    from sqlalchemy import func

    # Get date filters
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    status_filter = request.args.get('status', '')

    # Build query with proper joins to load client data
    query = Communication.query.outerjoin(
        Customer, Communication.client_id == Customer.id
    ).filter(
        Communication.type == 'whatsapp',
        Communication.created_at >= datetime.strptime(start_date, '%Y-%m-%d'),
        Communication.created_at <= datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
    ).add_columns(
        Customer.first_name,
        Customer.last_name,
        Customer.phone
    )

    if status_filter:
        query = query.filter(Communication.status == status_filter)

    # Get results and attach client info
    results = query.order_by(Communication.created_at.desc()).all()

    # Process results to attach client info
    messages = []
    for item in results:
        msg = item[0]  # Communication object
        # Attach client info as attributes for template access
        if len(item) > 1 and item[1]:  # Has client data
            msg.client_first_name = item[1]
            msg.client_last_name = item[2]
            msg.client_phone = item[3]
        else:
            msg.client_first_name = None
            msg.client_last_name = None
            msg.client_phone = None
        messages.append(msg)

    # Calculate statistics
    total_messages = len(messages)
    sent_count = sum(1 for m in messages if m.status == 'sent')
    failed_count = sum(1 for m in messages if m.status == 'failed')
    success_rate = round((sent_count / total_messages * 100) if total_messages > 0 else 0, 1)

    return render_template('notifications_report.html',
                         messages=messages,
                         total_messages=total_messages,
                         sent_count=sent_count,
                         failed_count=failed_count,
                         success_rate=success_rate,
                         start_date=start_date,
                         end_date=end_date,
                         status_filter=status_filter)

@app.route('/api/notifications/message/<int:message_id>')
@login_required
def get_message_detail(message_id):
    """Get message details API"""
    if not current_user.can_access('notifications'):
        return jsonify({'error': 'Access denied'}), 403

    message = Communication.query.get_or_404(message_id)

    return jsonify({
        'id': message.id,
        'client_name': message.client.full_name if message.client else 'N/A',
        'phone': message.client.phone if message.client else 'N/A',
        'type': message.type,
        'subject': message.subject,
        'message': message.message,
        'status': message.status,
        'created_at': message.created_at.strftime('%Y-%m-%d %I:%M %p') if message.created_at else None,
        'sent_at': message.sent_at.strftime('%Y-%m-%d %I:%M %p') if message.sent_at else None,
        'sent_by': message.creator.full_name if message.creator else 'System'
    })

@app.route('/api/notifications/retry/<int:message_id>', methods=['POST'])
@login_required
def retry_message(message_id):
    """Retry sending a failed message"""
    if not current_user.can_access('notifications'):
        return jsonify({'error': 'Access denied'}), 403

    from .notifications_queries import send_whatsapp_message

    message = Communication.query.get_or_404(message_id)

    if message.client and message.client.phone:
        success = send_whatsapp_message(message.client.phone, message.message)

        if success:
            message.status = 'sent'
            message.sent_at = datetime.utcnow()
            from app import db
            db.session.commit()
            return jsonify({'success': True, 'message': 'Message sent successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to send message'})

    return jsonify({'success': False, 'error': 'No phone number available'})

@app.route('/notifications/report/export')
@login_required
def export_notifications_report():
    """Export messaging report as CSV"""
    if not current_user.can_access('notifications'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from datetime import datetime, timedelta
    import csv
    from io import StringIO
    from flask import make_response

    # Get filters
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    status_filter = request.args.get('status', '')

    # Build query with proper joins to load client data
    query = Communication.query.outerjoin(
        Customer, Communication.client_id == Customer.id
    ).filter(
        Communication.type == 'whatsapp',
        Communication.created_at >= datetime.strptime(start_date, '%Y-%m-%d'),
        Communication.created_at <= datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
    ).add_columns(
        Customer.first_name,
        Customer.last_name,
        Customer.phone
    )

    if status_filter:
        query = query.filter(Communication.status == status_filter)

    # Get results and attach client info
    results = query.order_by(Communication.created_at.desc()).all()

    # Process results to attach client info
    messages = []
    for item in results:
        msg = item[0]  # Communication object
        # Attach client info as attributes for template access
        if len(item) > 1 and item[1]:  # Has client data
            msg.client_first_name = item[1]
            msg.client_last_name = item[2]
            msg.client_phone = item[3]
        else:
            msg.client_first_name = None
            msg.client_last_name = None
            msg.client_phone = None
        messages.append(msg)

    # Create CSV
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Date/Time', 'Client', 'Phone', 'Type', 'Subject', 'Status', 'Sent By', 'Message'])

    for msg in messages:
        writer.writerow([
            msg.created_at.strftime('%Y-%m-%d %I:%M %p') if msg.created_at else 'N/A',
            f"{msg.client_first_name} {msg.client_last_name}" if msg.client_first_name else 'N/A',
            msg.client_phone if msg.client_phone else 'N/A',
            msg.type,
            msg.subject or 'N/A',
            msg.status,
            msg.creator.full_name if msg.creator else 'System',
            msg.message or ''
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=whatsapp_report_{start_date}_to_{end_date}.csv"
    output.headers["Content-type"] = "text/csv"

    return output