"""
Settings database queries
"""
from app import db
from models import SystemSetting, BusinessSettings

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
    """Get business settings as a dictionary-like object"""
    try:
        # Create a simple object to hold settings
        class SettingsObject:
            def __init__(self):
                self.business_name = ''
                self.business_phone = ''
                self.business_email = ''
                self.business_address = ''
                self.tax_rate = 0.0
                self.currency = 'USD'
                self.timezone = 'UTC'

        settings_obj = SettingsObject()

        # Get all settings from database
        all_settings = BusinessSettings.query.all()

        # Map settings to object attributes
        for setting in all_settings:
            if setting.setting_key == 'business_name':
                settings_obj.business_name = setting.setting_value or ''
            elif setting.setting_key == 'business_phone':
                settings_obj.business_phone = setting.setting_value or ''
            elif setting.setting_key == 'business_email':
                settings_obj.business_email = setting.setting_value or ''
            elif setting.setting_key == 'business_address':
                settings_obj.business_address = setting.setting_value or ''
            elif setting.setting_key == 'tax_rate':
                settings_obj.tax_rate = float(setting.setting_value) if setting.setting_value else 0.0
            elif setting.setting_key == 'currency':
                settings_obj.currency = setting.setting_value or 'USD'
            elif setting.setting_key == 'timezone':
                settings_obj.timezone = setting.setting_value or 'UTC'

        return settings_obj
    except Exception as e:
        print(f"Error getting business settings: {e}")
        return None

def update_business_settings(settings_data):
    """Update business settings"""
    try:
        for key, value in settings_data.items():
            # Find or create setting
            setting = BusinessSettings.query.filter_by(setting_key=key).first()
            if not setting:
                setting = BusinessSettings(setting_key=key)
                db.session.add(setting)

            # Update value
            setting.setting_value = str(value) if value is not None else ''

        db.session.commit()
        return True
    except Exception as e:
        print(f"Error updating business settings: {e}")
        db.session.rollback()
        return False

def get_gst_settings():
    """Get GST configuration settings from database"""
    try:
        # Fetch all GST-related settings using correct database keys
        gst_settings = {
            'enabled': get_setting_by_key('gst_enabled') == 'True',
            'gstin_number': get_setting_by_key('gstin_number') or '',
            'business_name': get_setting_by_key('gst_business_name') or '',
            'business_address': get_setting_by_key('gst_business_address') or '',
            'business_phone': get_setting_by_key('gst_phone') or '',  # Fixed: was gst_business_phone
            'business_email': get_setting_by_key('gst_email') or '',  # Fixed: was gst_business_email
            'state': get_setting_by_key('gst_state') or '',
            'cgst_rate': float(get_setting_by_key('default_cgst') or 9),
            'sgst_rate': float(get_setting_by_key('default_sgst') or 9),
            'igst_rate': float(get_setting_by_key('default_igst') or 18),
        }
        return gst_settings
    except Exception as e:
        print(f"Error getting GST settings: {e}")
        # Return default values if there's an error
        return {
            'enabled': False,
            'gstin_number': '',
            'business_name': '',
            'business_address': '',
            'business_phone': '',
            'business_email': '',
            'state': '',
            'cgst_rate': 9.0,
            'sgst_rate': 9.0,
            'igst_rate': 18.0,
        }