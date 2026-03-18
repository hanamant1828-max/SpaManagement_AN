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
    """Get business settings, checking both BusinessSettings and SystemSetting tables."""
    try:
        def _read(key):
            """Read value from BusinessSettings first, then SystemSetting as fallback."""
            b = BusinessSettings.query.filter_by(setting_key=key).first()
            if b and b.setting_value:
                return b.setting_value
            s = SystemSetting.query.filter_by(key=key).first()
            if s and s.value:
                return s.value
            return ''

        class SettingsObject:
            pass

        obj = SettingsObject()
        obj.business_name    = _read('business_name')
        obj.business_phone   = _read('business_phone')
        obj.business_email   = _read('business_email')
        obj.business_address = _read('business_address')
        obj.currency         = _read('currency') or 'USD'
        obj.timezone         = _read('timezone') or 'UTC'
        raw_tax              = _read('tax_rate')
        obj.tax_rate         = float(raw_tax) if raw_tax else 0.0
        return obj
    except Exception as e:
        print(f"Error getting business settings: {e}")
        return None

def update_business_settings(settings_data):
    """Update business settings in both BusinessSettings and SystemSetting tables"""
    try:
        for key, value in settings_data.items():
            str_value = str(value) if value is not None else ''

            # Save to BusinessSettings table
            setting = BusinessSettings.query.filter_by(setting_key=key).first()
            if not setting:
                setting = BusinessSettings(setting_key=key)
                db.session.add(setting)
            setting.setting_value = str_value

            # Also save to SystemSetting table so the public website reads updated values
            sys_setting = SystemSetting.query.filter_by(key=key).first()
            if not sys_setting:
                sys_setting = SystemSetting(
                    key=key,
                    value=str_value,
                    category='business',
                    display_name=key.replace('_', ' ').title()
                )
                db.session.add(sys_setting)
            else:
                sys_setting.value = str_value

        db.session.commit()
        return True
    except Exception as e:
        print(f"Error updating business settings: {e}")
        db.session.rollback()
        return False

def get_gst_settings():
    """Get GST configuration settings from database"""
    try:
        default_cgst = float(get_setting_by_key('default_cgst') or 9)
        default_sgst = float(get_setting_by_key('default_sgst') or 9)
        default_igst = float(get_setting_by_key('default_igst') or 18)

        product_cgst_raw = get_setting_by_key('product_cgst_rate')
        product_sgst_raw = get_setting_by_key('product_sgst_rate')
        service_cgst_raw = get_setting_by_key('service_cgst_rate')
        service_sgst_raw = get_setting_by_key('service_sgst_rate')

        product_cgst = float(product_cgst_raw) if product_cgst_raw is not None and product_cgst_raw != '' else default_cgst
        product_sgst = float(product_sgst_raw) if product_sgst_raw is not None and product_sgst_raw != '' else default_sgst
        service_cgst = float(service_cgst_raw) if service_cgst_raw is not None and service_cgst_raw != '' else default_cgst
        service_sgst = float(service_sgst_raw) if service_sgst_raw is not None and service_sgst_raw != '' else default_sgst

        gst_settings = {
            'enabled': get_setting_by_key('gst_enabled') == 'True',
            'gstin_number': get_setting_by_key('gstin_number') or '',
            'business_name': get_setting_by_key('gst_business_name') or '',
            'business_address': get_setting_by_key('gst_business_address') or '',
            'business_phone': get_setting_by_key('gst_phone') or '',
            'business_email': get_setting_by_key('gst_email') or '',
            'state': get_setting_by_key('gst_state') or '',
            'cgst_rate': default_cgst,
            'sgst_rate': default_sgst,
            'igst_rate': float(get_setting_by_key('default_igst') or 18),
            'product_cgst_rate': product_cgst,
            'product_sgst_rate': product_sgst,
            'product_gst_rate': product_cgst + product_sgst,
            'service_cgst_rate': service_cgst,
            'service_sgst_rate': service_sgst,
            'service_gst_rate': service_cgst + service_sgst,
        }
        return gst_settings
    except Exception as e:
        print(f"Error getting GST settings: {e}")
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
            'product_cgst_rate': 9.0,
            'product_sgst_rate': 9.0,
            'product_gst_rate': 18.0,
            'service_cgst_rate': 9.0,
            'service_sgst_rate': 9.0,
            'service_gst_rate': 18.0,
        }