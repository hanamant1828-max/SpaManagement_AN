"""
Settings views and routes
"""
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import app
from forms import BusinessSettingsForm, SystemSettingForm
from .settings_queries import (
    get_system_settings, get_setting_by_key, update_setting,
    get_business_settings, update_business_settings
)

@app.route('/settings')
@login_required
def settings():
    if not current_user.can_access('settings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    system_settings = get_system_settings()
    business_settings = get_business_settings()
    
    business_form = BusinessSettingsForm()
    system_form = SystemSettingForm()
    
    return render_template('settings.html',
                         system_settings=system_settings,
                         business_settings=business_settings,
                         business_form=business_form,
                         system_form=system_form)

@app.route('/settings/business', methods=['POST'])
@login_required
def update_business_settings_route():
    if not current_user.can_access('settings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = BusinessSettingsForm()
    if form.validate_on_submit():
        settings_data = {
            'business_name': form.business_name.data,
            'business_phone': form.business_phone.data,
            'business_email': form.business_email.data,
            'business_address': form.business_address.data,
            'tax_rate': form.tax_rate.data,
            'currency': form.currency.data,
            'timezone': form.timezone.data
        }
        
        update_business_settings(settings_data)
        flash('Business settings updated successfully!', 'success')
    else:
        flash('Error updating business settings. Please check your input.', 'danger')
    
    return redirect(url_for('settings'))

@app.route('/settings/system', methods=['POST'])
@login_required
def update_system_setting_route():
    if not current_user.can_access('settings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    setting_key = request.form.get('key')
    setting_value = request.form.get('value')
    
    if setting_key and setting_value is not None:
        update_setting(setting_key, setting_value)
        flash('System setting updated successfully!', 'success')
    else:
        flash('Invalid setting data', 'danger')
    
    return redirect(url_for('settings'))