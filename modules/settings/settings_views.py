"""
Settings and Department Management Views
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import Department, User

# Department Management API Routes
@app.route('/api/departments', methods=['GET'])
@login_required
def api_get_departments():
    """Get all departments"""
    try:
        departments = Department.query.order_by(Department.name).all()
        return jsonify({
            'success': True,
            'departments': [{
                'id': dept.id,
                'name': dept.name,
                'display_name': dept.display_name,
                'description': dept.description,
                'is_active': dept.is_active,
                'created_at': dept.created_at.isoformat() if dept.created_at else None
            } for dept in departments]
        })
    except Exception as e:
        print(f"Error loading departments: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/departments/<int:department_id>', methods=['GET'])
@login_required
def api_get_department(department_id):
    """Get single department by ID"""
    try:
        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'success': False,
                'error': 'Department not found'
            }), 404

        return jsonify({
            'id': department.id,
            'name': department.name,
            'display_name': department.display_name,
            'description': department.description,
            'is_active': department.is_active,
            'created_at': department.created_at.isoformat() if department.created_at else None
        })
    except Exception as e:
        print(f"Error loading department {department_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/departments', methods=['POST'])
@login_required
def api_create_department():
    """Create new department"""
    try:
        if not current_user.can_access('settings'):
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403

        # Get form data
        name = request.form.get('name', '').strip()
        display_name = request.form.get('display_name', '').strip()
        description = request.form.get('description', '').strip()
        is_active = request.form.get('is_active') == 'on'

        # Validate required fields
        if not name or not display_name:
            return jsonify({
                'success': False,
                'message': 'Name and display name are required'
            }), 400

        # Check for duplicate name
        existing = Department.query.filter_by(name=name).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'Department with this name already exists'
            }), 400

        # Create department
        department = Department(
            name=name,
            display_name=display_name,
            description=description,
            is_active=is_active
        )

        db.session.add(department)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Department created successfully',
            'department_id': department.id
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error creating department: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/departments/<int:department_id>', methods=['PUT'])
@login_required
def api_update_department(department_id):
    """Update existing department"""
    try:
        if not current_user.can_access('settings'):
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403

        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'success': False,
                'message': 'Department not found'
            }), 404

        # Get form data
        name = request.form.get('name', '').strip()
        display_name = request.form.get('display_name', '').strip()
        description = request.form.get('description', '').strip()
        is_active = request.form.get('is_active') == 'on'

        # Validate required fields
        if not name or not display_name:
            return jsonify({
                'success': False,
                'message': 'Name and display name are required'
            }), 400

        # Check for duplicate name (excluding current department)
        existing = Department.query.filter(
            Department.name == name,
            Department.id != department_id
        ).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'Department with this name already exists'
            }), 400

        # Update department
        department.name = name
        department.display_name = display_name
        department.description = description
        department.is_active = is_active

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Department updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error updating department {department_id}: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/departments/<int:department_id>', methods=['DELETE'])
@login_required
def api_delete_department(department_id):
    """Delete department"""
    try:
        if not current_user.can_access('settings'):
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403

        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'success': False,
                'message': 'Department not found'
            }), 404

        # Check if department has staff members
        staff_count = User.query.filter_by(department_id=department_id).count()
        if staff_count > 0:
            return jsonify({
                'success': False,
                'message': f'Cannot delete department with {staff_count} staff member(s)'
            }), 400

        db.session.delete(department)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Department deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting department {department_id}: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# GST Configuration API Routes
@app.route('/api/gst/configuration', methods=['GET'])
@login_required
def api_get_gst_configuration():
    """Get GST configuration"""
    try:
        from models import SystemSetting

        # Get GST settings
        gstin_number = SystemSetting.query.filter_by(key='gstin_number').first()
        gst_business_name = SystemSetting.query.filter_by(key='gst_business_name').first()
        gst_business_address = SystemSetting.query.filter_by(key='gst_business_address').first()
        gst_state = SystemSetting.query.filter_by(key='gst_state').first()
        gst_enabled = SystemSetting.query.filter_by(key='gst_enabled').first()
        default_cgst = SystemSetting.query.filter_by(key='default_cgst').first()
        default_sgst = SystemSetting.query.filter_by(key='default_sgst').first()
        default_igst = SystemSetting.query.filter_by(key='default_igst').first()

        # Get phone and email settings
        gst_phone = SystemSetting.query.filter_by(key='gst_phone').first()
        gst_email = SystemSetting.query.filter_by(key='gst_email').first()

        return jsonify({
            'success': True,
            'configuration': {
                'gstin_number': gstin_number.value if gstin_number else '',
                'business_name': gst_business_name.value if gst_business_name else '',
                'business_address': gst_business_address.value if gst_business_address else '',
                'phone': gst_phone.value if gst_phone else '',
                'email': gst_email.value if gst_email else '',
                'state': gst_state.value if gst_state else '',
                'gst_enabled': gst_enabled.value == 'true' if gst_enabled else False,
                'default_cgst': float(default_cgst.value) if default_cgst else 9.0,
                'default_sgst': float(default_sgst.value) if default_sgst else 9.0,
                'default_igst': float(default_igst.value) if default_igst else 18.0
            }
        })
    except Exception as e:
        print(f"Error loading GST configuration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/gst/configuration', methods=['POST'])
@login_required
def api_save_gst_configuration():
    """Save GST configuration"""
    try:
        if not current_user.can_access('settings'):
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403

        from models import SystemSetting

        # Get form data
        gstin_number = request.form.get('gstin_number', '').strip()
        gst_business_name = request.form.get('gst_business_name', '').strip()
        gst_business_address = request.form.get('gst_business_address', '').strip()
        gst_phone = request.form.get('gst_phone', '').strip()
        gst_email = request.form.get('gst_email', '').strip()
        gst_state = request.form.get('gst_state', '').strip()
        gst_enabled = request.form.get('gst_enabled') == 'on'
        default_cgst = request.form.get('default_cgst', '9')
        default_sgst = request.form.get('default_sgst', '9')
        default_igst = request.form.get('default_igst', '18')

        # Update or create settings
        settings_to_update = {
            'gstin_number': gstin_number,
            'gst_business_name': gst_business_name,
            'gst_business_address': gst_business_address,
            'gst_phone': gst_phone,
            'gst_email': gst_email,
            'gst_state': gst_state,
            'gst_enabled': 'true' if gst_enabled else 'false',
            'default_cgst': str(default_cgst),
            'default_sgst': str(default_sgst),
            'default_igst': str(default_igst)
        }

        for setting_key, setting_value in settings_to_update.items():
            setting = SystemSetting.query.filter_by(key=setting_key).first()
            if setting:
                setting.value = setting_value
            else:
                setting = SystemSetting(
                    key=setting_key,
                    value=setting_value,
                    category='gst',
                    display_name=setting_key.replace('_', ' ').title(),
                    data_type='string'
                )
                db.session.add(setting)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'GST configuration saved successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error saving GST configuration: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/gst/rates', methods=['GET'])
@login_required
def api_get_gst_rates():
    """Get all GST rates"""
    try:
        from models import GSTRate

        rates = GSTRate.query.order_by(GSTRate.service_category).all()

        print(f"📊 Found {len(rates)} GST rates in database")

        gst_rates_list = []
        for rate in rates:
            try:
                gst_data = {
                    'id': rate.id,
                    'service_category': rate.service_category or 'Uncategorized',
                    'hsn_sac_code': rate.hsn_sac_code or '',
                    'cgst_rate': float(rate.cgst_rate) if rate.cgst_rate is not None else 9.0,
                    'sgst_rate': float(rate.sgst_rate) if rate.sgst_rate is not None else 9.0,
                    'igst_rate': float(rate.igst_rate) if rate.igst_rate is not None else 18.0,
                    'is_active': getattr(rate, 'is_active', True),
                    'created_at': rate.created_at.isoformat() if hasattr(rate, 'created_at') and rate.created_at else None
                }
                gst_rates_list.append(gst_data)
                print(f"  ✓ {gst_data['service_category']}: CGST {gst_data['cgst_rate']}%, SGST {gst_data['sgst_rate']}%, IGST {gst_data['igst_rate']}%")
            except Exception as rate_error:
                print(f"  ✗ Error processing GST rate {rate.id}: {rate_error}")
                continue

        print(f"📤 Returning {len(gst_rates_list)} GST rates to frontend")

        return jsonify({
            'success': True,
            'gst_rates': gst_rates_list,
            'total': len(gst_rates_list)
        })
    except Exception as e:
        print(f"❌ Error loading GST rates: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to load GST rates',
            'gst_rates': [],
            'total': 0
        }), 500

@app.route('/api/gst/rates', methods=['POST'])
@login_required
def api_create_gst_rate():
    """Create new GST rate"""
    try:
        if not current_user.can_access('settings'):
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403

        from models import GSTRate

        service_category = request.form.get('service_category', '').strip()
        hsn_sac_code = request.form.get('hsn_sac_code', '').strip()
        cgst_rate = float(request.form.get('cgst_rate', 9.0))
        sgst_rate = float(request.form.get('sgst_rate', 9.0))
        igst_rate = float(request.form.get('igst_rate', 18.0))

        if not service_category:
            return jsonify({
                'success': False,
                'message': 'Service category is required'
            }), 400

        gst_rate = GSTRate(
            service_category=service_category,
            hsn_sac_code=hsn_sac_code,
            cgst_rate=cgst_rate,
            sgst_rate=sgst_rate,
            igst_rate=igst_rate
        )

        db.session.add(gst_rate)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'GST rate created successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error creating GST rate: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/gst/rates/<int:rate_id>', methods=['GET'])
@login_required
def api_get_gst_rate(rate_id):
    """Get single GST rate"""
    try:
        from models import GSTRate

        gst_rate = GSTRate.query.get(rate_id)
        if not gst_rate:
            return jsonify({
                'success': False,
                'error': 'GST rate not found'
            }), 404

        return jsonify({
            'success': True,
            'gst_rate': {
                'id': gst_rate.id,
                'service_category': gst_rate.service_category,
                'hsn_sac_code': gst_rate.hsn_sac_code,
                'cgst_rate': float(gst_rate.cgst_rate) if gst_rate.cgst_rate else 0.0,
                'sgst_rate': float(gst_rate.sgst_rate) if gst_rate.sgst_rate else 0.0,
                'igst_rate': float(gst_rate.igst_rate) if gst_rate.igst_rate else 0.0
            }
        })
    except Exception as e:
        print(f"Error loading GST rate: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/gst/rates/<int:rate_id>', methods=['PUT'])
@login_required
def api_update_gst_rate(rate_id):
    """Update GST rate"""
    try:
        if not current_user.can_access('settings'):
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403

        from models import GSTRate

        gst_rate = GSTRate.query.get(rate_id)
        if not gst_rate:
            return jsonify({
                'success': False,
                'message': 'GST rate not found'
            }), 404

        gst_rate.service_category = request.form.get('service_category', gst_rate.service_category)
        gst_rate.hsn_sac_code = request.form.get('hsn_sac_code', gst_rate.hsn_sac_code)
        gst_rate.cgst_rate = float(request.form.get('cgst_rate', gst_rate.cgst_rate))
        gst_rate.sgst_rate = float(request.form.get('sgst_rate', gst_rate.sgst_rate))
        gst_rate.igst_rate = float(request.form.get('igst_rate', gst_rate.igst_rate))

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'GST rate updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error updating GST rate: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/gst/rates/<int:rate_id>', methods=['DELETE'])
@login_required
def api_delete_gst_rate(rate_id):
    """Delete GST rate"""
    try:
        if not current_user.can_access('settings'):
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403

        from models import GSTRate

        gst_rate = GSTRate.query.get(rate_id)
        if not gst_rate:
            return jsonify({
                'success': False,
                'message': 'GST rate not found'
            }), 404

        db.session.delete(gst_rate)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'GST rate deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting GST rate: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Logo Management API Routes
@app.route('/api/settings/logo', methods=['GET'])
@login_required
def api_get_logo():
    """Get current logo"""
    try:
        from models import SystemSetting
        
        logo_setting = SystemSetting.query.filter_by(key='business_logo').first()
        
        if logo_setting and logo_setting.value:
            return jsonify({
                'success': True,
                'logo_url': logo_setting.value
            })
        
        return jsonify({
            'success': True,
            'logo_url': None
        })
    except Exception as e:
        print(f"Error getting logo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/settings/logo', methods=['POST'])
@login_required
def api_upload_logo():
    """Upload business logo"""
    try:
        if not current_user.can_access('settings'):
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403

        import os
        from werkzeug.utils import secure_filename
        from models import SystemSetting

        # Check if file was uploaded
        if 'logo' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file uploaded'
            }), 400

        file = request.files['logo']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400

        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'message': f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}'
            }), 400

        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join('static', 'uploads', 'logos')
        os.makedirs(upload_dir, exist_ok=True)
        
        print(f"Upload directory: {upload_dir}")
        print(f"Upload directory exists: {os.path.exists(upload_dir)}")

        # Generate unique filename
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f'logo_{timestamp}.{file_ext}'
        file_path = os.path.join(upload_dir, new_filename)
        
        print(f"Saving file to: {file_path}")
        
        # Save file
        file.save(file_path)
        
        print(f"File saved successfully: {os.path.exists(file_path)}")
        
        # Store path in database
        logo_url = f'/static/uploads/logos/{new_filename}'
        logo_setting = SystemSetting.query.filter_by(key='business_logo').first()
        
        if logo_setting:
            # Delete old logo file if it exists
            if logo_setting.value:
                old_file_path = logo_setting.value.replace('/static/', 'static/')
                if os.path.exists(old_file_path):
                    try:
                        os.remove(old_file_path)
                    except Exception as e:
                        print(f"Warning: Could not delete old logo: {e}")
            
            logo_setting.value = logo_url
        else:
            logo_setting = SystemSetting(
                key='business_logo',
                value=logo_url,
                category='business',
                display_name='Business Logo',
                data_type='string'
            )
            db.session.add(logo_setting)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Logo uploaded successfully',
            'logo_url': logo_url
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error uploading logo: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/settings/logo', methods=['DELETE'])
@login_required
def api_delete_logo():
    """Delete business logo"""
    try:
        if not current_user.can_access('settings'):
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403

        import os
        from models import SystemSetting

        logo_setting = SystemSetting.query.filter_by(key='business_logo').first()
        
        if not logo_setting or not logo_setting.value:
            return jsonify({
                'success': False,
                'message': 'No logo found'
            }), 404

        # Delete file from filesystem
        file_path = logo_setting.value.replace('/static/', 'static/')
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not delete logo file: {e}")

        # Remove from database
        logo_setting.value = None
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Logo deleted successfully'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error deleting logo: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/system_management')
@login_required
def system_management():
    """System management page"""
    if not current_user.can_access('settings'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('system_management.html')

"""
Settings views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import SystemSetting, Department
from .settings_queries import get_system_settings, update_setting

# Import settings queries with error handling
try:
    from .settings_queries import (
        get_system_settings, get_setting_by_key, update_setting,
        get_business_settings, update_business_settings
    )
except ImportError as e:
    print(f"Warning: Settings queries import error: {e}")
    # Provide fallback functions
    def get_system_settings():
        return {}
    def get_setting_by_key(key):
        return None
    def update_setting(key, value):
        return True
    def get_business_settings():
        return {}
    def update_business_settings(data):
        return True

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

    # Fetch departments for table view
    try:
        departments = Department.query.filter_by(is_active=True).all()
    except Exception as e:
        flash(f"Error fetching departments: {e}", "danger")
        departments = []
    
    # Get WhatsApp settings from database
    whatsapp_settings = {
        'business_whatsapp_number': get_setting_by_key('business_whatsapp_number') or '',
        'enable_notifications': get_setting_by_key('whatsapp_enable_notifications') == 'true'
    }

    return render_template('settings.html',
                         system_settings=system_settings,
                         business_settings=business_settings,
                         business_form=business_form,
                         system_form=system_form,
                         departments=departments,
                         whatsapp_settings=whatsapp_settings)


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

@app.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    if not current_user.has_permission('settings_edit'):
        flash('You do not have permission to update settings', 'danger')
        return redirect(url_for('settings'))

    try:
        for key in request.form.keys():
            if key != 'csrf_token':
                value = request.form.get(key)
                update_setting(key, value)

        flash('Settings updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating settings: {str(e)}', 'danger')

    return redirect(url_for('settings'))

# Department API endpoints
@app.route('/api/departments', methods=['GET'])
@login_required
def get_departments_api():
    """Get all departments"""
    try:
        departments = Department.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'departments': [{
                'id': dept.id,
                'name': dept.name,
                'display_name': dept.display_name,
                'description': dept.description,
                'is_active': dept.is_active
            } for dept in departments]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/departments/<int:department_id>', methods=['GET'])
@login_required
def get_department_api(department_id):
    """Get single department"""
    try:
        dept = Department.query.get_or_404(department_id)
        return jsonify({
            'id': dept.id,
            'name': dept.name,
            'display_name': dept.display_name,
            'description': dept.description,
            'is_active': dept.is_active
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/departments', methods=['POST'])
@login_required
def create_department_api():
    """Create new department"""
    try:
        name = request.form.get('name')
        display_name = request.form.get('display_name')
        description = request.form.get('description', '')
        is_active = request.form.get('is_active') == 'on'

        department = Department(
            name=name,
            display_name=display_name,
            description=description,
            is_active=is_active
        )

        db.session.add(department)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Department created successfully',
            'department': {
                'id': department.id,
                'name': department.name,
                'display_name': department.display_name
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/departments/<int:department_id>', methods=['PUT'])
@login_required
def update_department_api(department_id):
    """Update department"""
    try:
        dept = Department.query.get_or_404(department_id)

        dept.name = request.form.get('name', dept.name)
        dept.display_name = request.form.get('display_name', dept.display_name)
        dept.description = request.form.get('description', dept.description)
        dept.is_active = request.form.get('is_active') == 'on'

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Department updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/departments/<int:department_id>', methods=['DELETE'])
@login_required
def delete_department_api(department_id):
    """Delete department"""
    try:
        dept = Department.query.get_or_404(department_id)

        # Check if department has staff assigned
        from models import User
        staff_count = User.query.filter_by(department_id=department_id).count()

        if staff_count > 0:
            return jsonify({
                'success': False,
                'message': f'Cannot delete department with {staff_count} staff members assigned'
            }), 400

        db.session.delete(dept)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Department deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# WhatsApp Configuration Routes
@app.route('/api/whatsapp/status')
@login_required
def whatsapp_status_api():
    """Check WhatsApp configuration status"""
    import os
    
    twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_number = os.environ.get('TWILIO_WHATSAPP_NUMBER')
    
    configured = bool(twilio_sid and twilio_token and twilio_number)
    
    return jsonify({
        'configured': configured,
        'has_account_sid': bool(twilio_sid),
        'has_auth_token': bool(twilio_token),
        'has_whatsapp_number': bool(twilio_number)
    })


@app.route('/settings/whatsapp', methods=['POST'])
@login_required
def update_whatsapp_settings():
    """Update WhatsApp configuration settings"""
    if not current_user.can_access('settings'):
        flash('Access denied', 'danger')
        return redirect(url_for('settings'))
    
    try:
        business_number = request.form.get('business_whatsapp_number', '').strip()
        enable_notifications = request.form.get('enable_notifications') == 'on'
        
        # Save settings to database
        update_setting('business_whatsapp_number', business_number)
        update_setting('whatsapp_enable_notifications', 'true' if enable_notifications else 'false')
        
        flash('WhatsApp settings updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating WhatsApp settings: {str(e)}', 'danger')
    
    return redirect(url_for('settings'))


@app.route('/api/whatsapp/test', methods=['POST'])
@login_required
def test_whatsapp_api():
    """Test WhatsApp connection by sending a test message"""
    if not current_user.can_access('settings'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        
        if not phone_number:
            return jsonify({'success': False, 'error': 'Phone number is required'}), 400
        
        # Import WhatsApp function
        from modules.notifications.notifications_queries import send_whatsapp_message
        
        # Send test message
        test_message = f"🔔 This is a test message from {get_setting_by_key('business_name') or 'Spa & Salon Suite'}. Your WhatsApp integration is working correctly!"
        
        success = send_whatsapp_message(phone_number, test_message)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Test message sent successfully! Check your WhatsApp.'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send message. Please check your Twilio credentials in Replit Secrets.'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error sending test message: {str(e)}'
        }), 500
