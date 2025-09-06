"""
Customer views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app
from forms import CustomerForm, AdvancedCustomerForm
from .clients_queries import (
    get_all_customers, get_customer_by_id, search_customers, create_customer,
    update_customer, delete_customer, get_customer_appointments,
    get_customer_communications, get_customer_stats
)
# Import db and Customer model for face management endpoints
from models import Customer
from app import db

@app.route('/customers')
@app.route('/clients')  # Keep for backward compatibility
@login_required
def customers():
    if not current_user.can_access('clients'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    search_query = request.args.get('search', '')
    if search_query:
        customers_list = search_customers(search_query)
    else:
        customers_list = get_all_customers()

    form = CustomerForm()
    advanced_form = AdvancedCustomerForm()

    return render_template('customers.html',
                         customers=customers_list,
                         form=form,
                         advanced_form=advanced_form,
                         search_query=search_query)

@app.route('/customers/create', methods=['POST'])
@app.route('/customers/add', methods=['POST'])
@app.route('/clients/create', methods=['POST'])  # Keep for backward compatibility
@app.route('/clients/add', methods=['POST'])  # Keep for backward compatibility
@app.route('/add_client', methods=['POST'])  # Keep for backward compatibility
@login_required
def create_customer_route():
    if not current_user.can_access('clients'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    form = CustomerForm()
    if form.validate_on_submit():
        # Validate and clean data
        email_value = form.email.data
        if email_value and email_value.strip():
            email_value = email_value.strip().lower()
        else:
            email_value = None

        phone_value = form.phone.data.strip()

        # Server-side validation for duplicates
        from .clients_queries import get_customer_by_phone, get_customer_by_email

        # Check for duplicate phone number
        if get_customer_by_phone(phone_value):
            flash('A customer with this phone number already exists. Please use a different phone number.', 'danger')
            return redirect(url_for('customers'))

        # Check for duplicate email (only if email is provided)
        if email_value and get_customer_by_email(email_value):
            flash('A customer with this email address already exists. Please use a different email or update the existing customer profile.', 'danger')
            return redirect(url_for('customers'))

        customer_data = {
            'first_name': form.first_name.data.strip().title(),
            'last_name': form.last_name.data.strip().title(),
            'phone': phone_value,
            'email': email_value,
            'address': form.address.data.strip() if form.address.data else '',
            'date_of_birth': form.date_of_birth.data,
            'gender': form.gender.data if form.gender.data else None,
            'preferences': form.preferences.data.strip() if form.preferences.data else '',
            'allergies': form.allergies.data.strip() if form.allergies.data else '',
            'notes': form.notes.data.strip() if form.notes.data else ''
        }

        try:
            new_customer = create_customer(customer_data)
            flash(f'Customer "{new_customer.first_name} {new_customer.last_name}" has been created successfully!', 'success')
        except Exception as e:
            flash(f'Error creating customer: {str(e)}', 'danger')
    else:
        # Form validation failed - show specific field errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.replace("_", " ").title()}: {error}', 'danger')

    return redirect(url_for('customers'))

@app.route('/clients/edit/<int:id>', methods=['GET'])
@login_required
def edit_client_route(id):
    if not current_user.can_access('clients'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    client = get_customer_by_id(id)
    if not client:
        flash('Client not found', 'danger')
        return redirect(url_for('customers'))

    form = CustomerForm(obj=client)
    advanced_form = AdvancedCustomerForm(obj=client)

    return render_template('customers.html',
                         customers=[client],
                         form=form,
                         advanced_form=advanced_form,
                         edit_mode=True,
                         edit_client=client)

@app.route('/clients/update/<int:id>', methods=['POST'])
@login_required
def update_client_route(id):
    if not current_user.can_access('clients'):
        # Access denied
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    client = get_customer_by_id(id)
    if not client:
        # Client not found
        flash('Client not found', 'danger')
        return redirect(url_for('customers'))

    form = CustomerForm()
    if form.validate_on_submit():
        # Validate and clean data
        email_value = form.email.data
        if email_value and email_value.strip():
            email_value = email_value.strip().lower()
        else:
            email_value = None

        phone_value = form.phone.data.strip()

        # Server-side validation for duplicates (excluding current customer)
        from .clients_queries import get_customer_by_phone, get_customer_by_email

        # Check for duplicate phone number (excluding current customer)
        existing_phone_customer = get_customer_by_phone(phone_value)
        if existing_phone_customer and existing_phone_customer.id != id:
            error_msg = 'A customer with this phone number already exists. Please use a different phone number.'
            # Duplicate phone
            flash(error_msg, 'danger')
            return redirect(url_for('customers'))

        # Check for duplicate email (only if email is provided and excluding current customer)
        if email_value:
            existing_email_customer = get_customer_by_email(email_value)
            if existing_email_customer and existing_email_customer.id != id:
                error_msg = 'A customer with this email address already exists. Please use a different email or update the existing customer profile.'
                # Duplicate email
                flash(error_msg, 'danger')
                return redirect(url_for('customers'))

        customer_data = {
            'first_name': form.first_name.data.strip().title(),
            'last_name': form.last_name.data.strip().title(),
            'phone': phone_value,
            'email': email_value,
            'address': form.address.data.strip() if form.address.data else '',
            'date_of_birth': form.date_of_birth.data,
            'gender': form.gender.data if form.gender.data else None,
            'preferences': form.preferences.data.strip() if form.preferences.data else '',
            'allergies': form.allergies.data.strip() if form.allergies.data else '',
            'notes': form.notes.data.strip() if form.notes.data else ''
        }

        try:
            updated_customer = update_customer(id, customer_data)
            success_msg = f'Customer "{updated_customer.first_name} {updated_customer.last_name}" has been updated successfully!'

            flash(success_msg, 'success')
        except Exception as e:
            error_msg = f'Error updating customer: {str(e)}'
            # Update error
            flash(error_msg, 'danger')
    else:
        # Form validation failed - show specific field errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.replace("_", " ").title()}: {error}', 'danger')

    return redirect(url_for('customers'))

@app.route('/clients/delete/<int:id>', methods=['POST'])
@login_required
def delete_client_route(id):
    if not current_user.can_access('clients'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    client = get_customer_by_id(id)
    client_name = f"{client.first_name} {client.last_name}" if client else "Customer"

    try:
        if delete_customer(id):
            flash(f'Customer "{client_name}" has been deleted successfully!', 'success')
        else:
            flash(f'Unable to delete customer "{client_name}". This customer may have associated appointments or records.', 'warning')
    except Exception as e:
        flash(f'Error deleting customer "{client_name}": {str(e)}', 'danger')

    return redirect(url_for('customers'))

@app.route('/clients/<int:id>')
@login_required
def client_detail(id):
    if not current_user.can_access('clients'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    client = get_customer_by_id(id)
    if not client:
        flash('Client not found', 'danger')
        return redirect(url_for('customers'))

    appointments = get_customer_appointments(id)
    communications = get_customer_communications(id)
    stats = get_customer_stats(id)

    return render_template('client_detail.html',
                         client=client,
                         appointments=appointments,
                         communications=communications,
                         stats=stats)

@app.route('/clients/face_management')
@login_required
def clients_face_management():
    """Face management for clients"""
    if not current_user.can_access('clients'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    from .clients_queries import get_all_customers
    from models import Customer

    # Get all customers
    clients = get_all_customers()

    # Get customers with face data
    clients_with_faces = Customer.query.filter(
        Customer.facial_encoding.isnot(None),
        Customer.is_active == True
    ).all()

    return render_template('face_management.html',
                         clients=clients,
                         clients_with_faces=clients_with_faces)

@app.route('/api/customers/<int:customer_id>')
@login_required
def api_get_customer(customer_id):
    """API endpoint to get customer data"""
    try:
        if not current_user.can_access('clients'):
            return jsonify({'success': False, 'error': 'Access denied'}), 403

        customer = get_customer_by_id(customer_id)
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404

        return jsonify({
            'success': True,
            'customer': {
                'id': customer.id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'phone': customer.phone,
                'email': customer.email or '',
                'address': customer.address or '',
                'date_of_birth': customer.date_of_birth.isoformat() if customer.date_of_birth else '',
                'gender': customer.gender or '',
                'preferences': customer.preferences or '',
                'allergies': customer.allergies or '',
                'notes': customer.notes or ''
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@app.route('/api/customers', methods=['GET'])
@login_required
def api_get_customers():
    """API endpoint to get all customers for JavaScript"""
    if not current_user.can_access('clients'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        customers = get_all_customers()
        customer_data = []
        for customer in customers:
            customer_data.append({
                'id': customer.id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'full_name': customer.full_name,
                'email': customer.email,
                'phone': customer.phone,
                'gender': customer.gender,
                'date_of_birth': customer.date_of_birth.isoformat() if customer.date_of_birth else None,
                'address': customer.address,
                'total_visits': customer.total_visits,
                'total_spent': customer.total_spent,
                'last_visit': customer.last_visit.isoformat() if customer.last_visit else None,
                'is_active': customer.is_active,
                'status': customer.status,
                'loyalty_points': customer.loyalty_points,
                'is_vip': customer.is_vip
            })

        return jsonify({
            'success': True,
            'customers': customer_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_face', methods=['POST'])
@login_required
def api_save_face():
    """API endpoint to save face data for a customer"""
    if not current_user.can_access('clients'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        data = request.get_json()
        client_id = data.get('client_id')
        face_image = data.get('face_image') # This should be the base64 encoded image string

        if not client_id or not face_image:
            return jsonify({'error': 'Missing client ID or face image'}), 400

        # Get customer
        customer = Customer.query.get(client_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404

        # Save face image data (base64 string)
        # In a real application, you'd want to save this to a file storage or CDN
        # and store the URL. For this example, we'll store the base64 directly.
        customer.face_image_url = face_image

        # Optionally, you can process the image for face encoding here
        # For example, using a library like 'face_recognition'
        # import face_recognition
        # encoded_face = face_recognition.face_encodings(face_image_data)[0] # Assuming one face
        # customer.facial_encoding = encoded_face.tolist() # Convert numpy array to list

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Face data saved successfully',
            'client_name': customer.full_name
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/customers_with_faces', methods=['GET'])
@login_required
def api_get_customers_with_faces():
    """API endpoint to get customers with face data"""
    if not current_user.can_access('clients'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Fetch customers who have face_image_url and are active
        customers = Customer.query.filter(
            Customer.face_image_url.isnot(None),
            Customer.is_active == True
        ).all()

        customer_data = []
        for customer in customers:
            customer_data.append({
                'id': customer.id,
                'full_name': customer.full_name,
                'phone': customer.phone,
                'email': customer.email,
                'face_image_url': customer.face_image_url, # This would be the URL to the stored image
                'face_registration_date': customer.created_at.isoformat() if customer.created_at else None
            })

        return jsonify({
            'success': True,
            'customers': customer_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_customer_face', methods=['POST'])
@login_required
def api_save_customer_face():
    """Save face data for a customer"""
    if not current_user.can_access('clients'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        face_image = data.get('face_image')

        if not customer_id or not face_image:
            return jsonify({'error': 'Customer ID and face image are required'}), 400

        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404

        # Save face image
        import base64
        import os
        from datetime import datetime

        # Create face images directory if it doesn't exist
        face_dir = 'static/face_images'
        if not os.path.exists(face_dir):
            os.makedirs(face_dir)

        # Save the image
        image_data = face_image.split(',')[1]  # Remove data:image/jpeg;base64, prefix
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f'customer_{customer_id}_{timestamp}.jpg'
        image_path = os.path.join(face_dir, image_filename)

        with open(image_path, 'wb') as f:
            f.write(base64.b64decode(image_data))

        # Update customer record
        customer.face_image_url = f'/static/face_images/{image_filename}'
        customer.facial_encoding = 'face_encoding_stored'  # Placeholder for face encoding

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Face data saved successfully for {customer.full_name}',
            'customer_name': customer.full_name,
            'face_image_url': customer.face_image_url
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error saving face data: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to save face data: {str(e)}'
        }), 500