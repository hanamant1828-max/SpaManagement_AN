"""
Customer views and routes
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import Customer
from .clients_queries import *

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

    try:
        # Get form data manually to handle CSRF issues
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        date_of_birth = request.form.get('date_of_birth')
        gender = request.form.get('gender', '').strip()
        preferences = request.form.get('preferences', '').strip()
        allergies = request.form.get('allergies', '').strip()
        notes = request.form.get('notes', '').strip()

        # Basic validation
        if not first_name:
            flash('First name is required. Please enter the customer\'s first name.', 'danger')
            return redirect(url_for('customers'))

        if not last_name:
            flash('Last name is required. Please enter the customer\'s last name.', 'danger')
            return redirect(url_for('customers'))

        if not phone:
            flash('Phone number is required. Please enter the customer\'s phone number.', 'danger')
            return redirect(url_for('customers'))

        # Clean email
        email_value = email.lower() if email else None

        # Server-side validation for duplicates
        from .clients_queries import get_customer_by_phone, get_customer_by_email

        # Check for duplicate phone number
        if get_customer_by_phone(phone):
            flash('A customer with this phone number already exists. Please use a different phone number.', 'danger')
            return redirect(url_for('customers'))

        # Check for duplicate email (only if email is provided)
        if email_value and get_customer_by_email(email_value):
            flash('A customer with this email address already exists. Please use a different email or update the existing customer profile.', 'danger')
            return redirect(url_for('customers'))

        # Parse date of birth
        dob = None
        if date_of_birth:
            try:
                from datetime import datetime
                dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                dob = None

        customer_data = {
            'first_name': first_name.title(),
            'last_name': last_name.title(),
            'phone': phone,
            'email': email_value,
            'address': address,
            'date_of_birth': dob,
            'gender': gender if gender else None,
            'preferences': preferences,
            'allergies': allergies,
            'notes': notes
        }

        new_customer = create_customer(customer_data)
        flash(f'Customer "{new_customer.first_name} {new_customer.last_name}" has been created successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error creating customer: {str(e)}', 'danger')
        print(f"Customer creation error: {e}")

    return redirect(url_for('customers'))

@app.route('/clients/edit/<int:id>')
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
            'first_name': (form.first_name.data or '').strip().title(),
            'last_name': (form.last_name.data or '').strip().title(),
            'phone': phone_value,
            'email': email_value,
            'address': (form.address.data or '').strip(),
            'date_of_birth': form.date_of_birth.data,
            'gender': form.gender.data if form.gender.data and form.gender.data.strip() else None,
            'preferences': (form.preferences.data or '').strip(),
            'allergies': (form.allergies.data or '').strip(),
            'notes': (form.notes.data or '').strip()
        }

        # Additional validation
        if not customer_data['first_name']:
            flash('First name is required. Please enter the customer\'s first name.', 'danger')
            return redirect(url_for('customers'))

        if not customer_data['last_name']:
            flash('Last name is required. Please enter the customer\'s last name.', 'danger')
            return redirect(url_for('customers'))

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

@app.route('/delete_customer/<int:id>', methods=['DELETE'])
@login_required
def delete_customer_api(id):
    """API endpoint to delete a customer with proper JSON responses"""
    if not current_user.can_access('clients'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    try:
        # Import Customer model with late import to avoid circular dependencies
        from models import Customer

        # Check if customer exists
        customer = Customer.query.get(id)
        if not customer:
            return jsonify({'success': False, 'message': 'Customer not found'}), 404

        customer_name = f"{customer.first_name} {customer.last_name}"

        # Soft delete - mark as inactive instead of hard delete to preserve data integrity
        customer.is_active = False
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Customer "{customer_name}" deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

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

        # Calculate visit history and status
        total_visits = customer.total_visits or 0
        total_spent = customer.total_spent or 0.0
        last_visit = customer.last_visit.isoformat() if customer.last_visit else None

        # Determine customer status
        status = 'New Customer'
        if not customer.is_active:
            status = 'Inactive'
        elif total_visits >= 10:
            status = 'Loyal Customer'
        elif total_visits > 0:
            status = 'Regular Customer'

        return jsonify({
            'success': True,
            'customer': {
                'id': customer.id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'full_name': customer.full_name,
                'phone': customer.phone,
                'email': customer.email or '',
                'address': customer.address or '',
                'date_of_birth': customer.date_of_birth.isoformat() if customer.date_of_birth else '',
                'gender': customer.gender or '',
                'preferences': customer.preferences or '',
                'allergies': customer.allergies or '',
                'notes': customer.notes or '',
                'total_visits': total_visits,
                'total_spent': total_spent,
                'last_visit': last_visit,
                'status': status,
                'is_active': customer.is_active,
                'created_at': customer.created_at.isoformat() if customer.created_at else None
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@app.route('/api/customers', methods=['GET'])
@login_required
def api_customers():
    from models import Customer

    customers = Customer.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': c.id,
        'name': c.full_name,
        'phone': c.phone,
        'email': c.email
    } for c in customers])


@app.route('/api/save_face', methods=['POST'])
@login_required
def api_save_face():
    """API endpoint to save face data for a customer"""
    if not current_user.can_access('clients'):
        return jsonify({'error': 'Access denied'}), 403

    try:
        data = request.get_json()
        client_id = data.get('client_id')
        face_image = data.get('face_image')

        if not client_id or not face_image:
            return jsonify({'error': 'Missing client ID or face image'}), 400

        # Get customer
        customer = Customer.query.get(client_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404

        # Save face image data (base64 string)
        customer.face_image_url = face_image

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
                'face_image_url': customer.face_image_url,
                'face_registration_date': customer.created_at.isoformat() if customer.created_at else None
            })

        return jsonify({
            'success': True,
            'customers': customer_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500