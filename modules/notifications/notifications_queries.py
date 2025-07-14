"""
Notifications related database queries
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from app import db
from models import Communication, Client, Appointment

def get_recent_communications():
    """Get recent communications/notifications"""
    return Communication.query.order_by(Communication.created_at.desc()).limit(50).all()

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