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
        # Convert empty email to None to avoid unique constraint violation
        email_value = form.email.data
        if email_value and email_value.strip():
            email_value = email_value.strip()
        else:
            email_value = None
            
        customer_data = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'phone': form.phone.data,
            'email': email_value,
            'address': form.address.data or '',
            'date_of_birth': form.date_of_birth.data,
            'gender': form.gender.data,
            'preferences': form.preferences.data or '',
            'allergies': form.allergies.data or '',
            'notes': form.notes.data or ''
        }

        try:
            create_customer(customer_data)
            flash('Customer created successfully!', 'success')
        except Exception as e:
            flash(f'Error creating customer: {str(e)}', 'danger')
    else:
        flash('Error creating customer. Please check your input.', 'danger')

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
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    client = get_customer_by_id(id)
    if not client:
        flash('Client not found', 'danger')
        return redirect(url_for('customers'))

    form = CustomerForm()
    if form.validate_on_submit():
        # Convert empty email to None to avoid unique constraint violation
        email_value = form.email.data
        if email_value and email_value.strip():
            email_value = email_value.strip()
        else:
            email_value = None
            
        customer_data = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'phone': form.phone.data,
            'email': email_value,
            'address': form.address.data or '',
            'date_of_birth': form.date_of_birth.data,
            'gender': form.gender.data,
            'preferences': form.preferences.data or '',
            'allergies': form.allergies.data or '',
            'notes': form.notes.data or ''
        }

        update_customer(id, customer_data)
        flash('Customer updated successfully!', 'success')
    else:
        flash('Error updating customer. Please check your input.', 'danger')

    return redirect(url_for('customers'))

@app.route('/clients/delete/<int:id>', methods=['POST'])
@login_required
def delete_client_route(id):
    if not current_user.can_access('clients'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    if delete_customer(id):
        flash('Customer deleted successfully!', 'success')
    else:
        flash('Error deleting customer', 'danger')

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

@app.route('/api/customers/<int:customer_id>')
@login_required
def api_get_customer(customer_id):
    """API endpoint to get customer data"""
    if not current_user.can_access('clients'):
        return jsonify({'error': 'Access denied'}), 403

    customer = get_customer_by_id(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    return jsonify({
        'success': True,
        'customer': {
            'id': customer.id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'phone': customer.phone,
            'email': customer.email,
            'address': customer.address or '',
            'date_of_birth': customer.date_of_birth.isoformat() if customer.date_of_birth else None,
            'gender': customer.gender,
            'preferences': customer.preferences or '',
            'allergies': customer.allergies or '',
            'notes': customer.notes or ''
        }
    })