"""
Notifications related database queries
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from app import db
from models import Communication, Customer, Appointment
import os

# WhatsApp configuration
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
BUSINESS_WHATSAPP_NUMBER = '+918746084638'

def send_whatsapp_message(to_number, message_body):
    """Send WhatsApp message using Twilio"""
    try:
        from twilio.rest import Client
        
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            print("⚠️ Twilio credentials not configured - WhatsApp messages disabled")
            print("💡 To enable WhatsApp: Add TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN to Secrets")
            return False
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Format phone number for WhatsApp
        if not to_number.startswith('whatsapp:'):
            # Ensure phone number starts with +
            if not to_number.startswith('+'):
                to_number = f'+{to_number}'
            to_number = f'whatsapp:{to_number}'
        
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message_body,
            to=to_number
        )
        
        print(f"✅ WhatsApp message sent: {message.sid}")
        return True
    except ImportError:
        print("⚠️ Twilio library not installed - WhatsApp messages disabled")
        print("💡 To enable WhatsApp: Run 'pip install twilio'")
        return False
    except Exception as e:
        print(f"❌ Error sending WhatsApp message: {e}")
        return False

def get_recent_communications():
    """Get recent communications/notifications"""
    return Communication.query.order_by(Communication.created_at.desc()).limit(50).all()

def get_pending_notifications():
    """Get pending notifications"""
    return Communication.query.filter_by(status='pending').all()

def create_notification(data):
    """Create a new notification record"""
    notification = Communication(
        client_id=data.get('client_id'),
        type=data.get('type'),
        subject=data.get('subject'),
        message=data.get('message'),
        status=data.get('status', 'pending'),
        created_by=data.get('created_by')
    )
    db.session.add(notification)
    db.session.commit()
    return notification

def mark_notification_sent(notification_id):
    """Mark notification as sent"""
    notification = Communication.query.get(notification_id)
    if notification:
        notification.status = 'sent'
        db.session.commit()
    return notification

def get_clients_for_reminders():
    """Get appointments that need reminders"""
    tomorrow = date.today() + timedelta(days=1)
    return Appointment.query.filter(
        and_(
            func.date(Appointment.appointment_date) == tomorrow,
            Appointment.status == 'confirmed'
        )
    ).all()

def get_pending_notifications():
    """Get pending notifications to send"""
    return Communication.query.filter_by(status='pending').order_by(Communication.created_at).all()

def create_notification(notification_data):
    """Create a new notification"""
    notification = Communication(**notification_data)
    db.session.add(notification)
    db.session.commit()
    return notification

def mark_notification_sent(notification_id):
    """Mark notification as sent"""
    notification = Communication.query.get(notification_id)
    if notification:
        notification.status = 'sent'
        notification.sent_at = datetime.utcnow()
        db.session.commit()
    return notification

def get_clients_for_reminders():
    """Get clients who need appointment reminders"""
    tomorrow = date.today() + timedelta(days=1)
    return Appointment.query.filter(
        func.date(Appointment.appointment_date) == tomorrow,
        Appointment.status.in_(['scheduled', 'confirmed'])
    ).all()