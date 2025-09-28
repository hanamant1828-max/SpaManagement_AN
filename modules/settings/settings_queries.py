
"""
Settings database queries
"""
from app import db
from models import BusinessSettings, SystemSetting

def get_system_settings():
    """Get all system settings"""
    try:
        settings = SystemSetting.query.all()
        return {setting.key: setting.value for setting in settings}
    except Exception as e:
        print(f"Error getting system settings: {e}")
        return {}

def get_setting_by_key(key):
    """Get specific setting by key"""
    try:
        setting = SystemSetting.query.filter_by(key=key).first()
        return setting.value if setting else None
    except Exception as e:
        print(f"Error getting setting {key}: {e}")
        return None

def update_setting(key, value):
    """Update or create system setting"""
    try:
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = SystemSetting(key=key, value=value)
            db.session.add(setting)
        
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error updating setting {key}: {e}")
        db.session.rollback()
        return False

def get_business_settings():
    """Get business settings"""
    try:
        settings = BusinessSettings.query.first()
        if not settings:
            # Create default business settings
            settings = BusinessSettings(
                business_name='Spa Management System',
                business_phone='',
                business_email='',
                business_address='',
                tax_rate=0.0,
                currency='USD',
                timezone='UTC'
            )
            db.session.add(settings)
            db.session.commit()
        return settings
    except Exception as e:
        print(f"Error getting business settings: {e}")
        return None

def update_business_settings(settings_data):
    """Update business settings"""
    try:
        settings = BusinessSettings.query.first()
        if not settings:
            settings = BusinessSettings()
            db.session.add(settings)
        
        for key, value in settings_data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error updating business settings: {e}")
        db.session.rollback()
        return False
