"""
Settings-related database queries
"""
from app import db
# Late imports to avoid circular dependency

def get_system_settings():
    """Get all system settings"""
    from models import SystemSetting
    return SystemSetting.query.order_by(SystemSetting.category, SystemSetting.display_name).all()

def get_setting_by_key(key):
    """Get setting by key"""
    return SystemSetting.query.filter_by(key=key).first()

def update_setting(key, value):
    """Update a system setting"""
    setting = SystemSetting.query.filter_by(key=key).first()
    if setting:
        setting.value = value
        db.session.commit()
    return setting

def get_business_settings():
    """Get business settings"""
    return BusinessSettings.query.first()

def update_business_settings(settings_data):
    """Update business settings"""
    business_settings = BusinessSettings.query.first()
    if business_settings:
        for key, value in settings_data.items():
            setattr(business_settings, key, value)
        db.session.commit()
    else:
        business_settings = BusinessSettings(**settings_data)
        db.session.add(business_settings)
        db.session.commit()
    return business_settings