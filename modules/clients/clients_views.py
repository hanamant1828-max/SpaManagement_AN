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
        customer_data = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'phone': form.phone.data,
            'email': form.email.data,
            'address': form.address.data or '',
            'date_of_birth': form.date_of_birth.data,
            'gender': form.gender.data,
            'preferences': form.preferences.data or '',
            'allergies': form.allergies.data or '',
            'notes': form.notes.data or ''
        }
        
        create_customer(customer_data)
        flash('Customer created successfully!', 'success')
    else:
        flash('Error creating customer. Please check your input.', 'danger')
    
    return redirect(url_for('customers'))

@app.route('/clients/update/<int:id>', methods=['POST'])
@login_required
def update_client_route(id):
    if not current_user.can_access('clients'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    client = get_client_by_id(id)
    if not client:
        flash('Client not found', 'danger')
        return redirect(url_for('clients'))
    
    form = ClientForm()
    if form.validate_on_submit():
        client_data = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'phone': form.phone.data,
            'email': form.email.data,
            'address': form.address.data or '',
            'date_of_birth': form.date_of_birth.data,
            'gender': form.gender.data,
            'preferences': form.preferences.data or '',
            'allergies': form.allergies.data or '',
            'notes': form.notes.data or ''
        }
        
        update_client(id, client_data)
        flash('Client updated successfully!', 'success')
    else:
        flash('Error updating client. Please check your input.', 'danger')
    
    return redirect(url_for('clients'))

@app.route('/clients/delete/<int:id>', methods=['POST'])
@login_required
def delete_client_route(id):
    if not current_user.can_access('clients'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    if delete_client(id):
        flash('Client deleted successfully!', 'success')
    else:
        flash('Error deleting client', 'danger')
    
    return redirect(url_for('clients'))

@app.route('/clients/<int:id>')
@login_required
def client_detail(id):
    if not current_user.can_access('clients'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    client = get_client_by_id(id)
    if not client:
        flash('Client not found', 'danger')
        return redirect(url_for('clients'))
    
    appointments = get_client_appointments(id)
    communications = get_client_communications(id)
    stats = get_client_stats(id)
    
    return render_template('client_detail.html',
                         client=client,
                         appointments=appointments,
                         communications=communications,
                         stats=stats)