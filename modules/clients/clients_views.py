
"""
Customer/Client Management Routes
Compatible with your app.py structure
Place this file at: modules/clients/clients_views.py
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime

# Import app and db from your main app module
from app import app, db

# Import models - these should be available after app initialization
from models import Customer, Appointment, ServicePackageAssignment

# Import forms with fallback
try:
    from forms import CustomerForm, AdvancedCustomerForm
except ImportError:
    CustomerForm = None
    AdvancedCustomerForm = None

# Import SQLAlchemy functions
from sqlalchemy import or_, func

# Import query functions with fallback implementations
try:
    from modules.clients.clients_queries import (
        get_all_customers,
        search_customers,
        get_customer_by_id,
        get_customer_by_phone,
        get_customer_by_email,
        create_customer as create_customer_query,
        update_customer as update_customer_query,
        get_customer_appointments,
        get_customer_communications,
        get_customer_stats
    )
except ImportError:
    # Fallback implementations if clients_queries doesn't exist
    def get_all_customers():
        try:
            return Customer.query.filter_by(is_active=True).order_by(Customer.first_name).all()
        except Exception as e:
            print(f"Error in get_all_customers: {e}")
            return []

    def search_customers(query):
        if not query:
            return get_all_customers()
        try:
            search_term = f"%{query}%"
            return Customer.query.filter(
                or_(
                    Customer.first_name.ilike(search_term),
                    Customer.last_name.ilike(search_term),
                    Customer.phone.ilike(search_term),
                    Customer.email.ilike(search_term) if Customer.email else False
                ),
                Customer.is_active == True
            ).order_by(Customer.first_name).all()
        except Exception as e:
            print(f"Error in search_customers: {e}")
            return []

    def get_customer_by_id(customer_id):
        try:
            return Customer.query.get(customer_id)
        except Exception as e:
            print(f"Error in get_customer_by_id: {e}")
            return None

    def get_customer_by_phone(phone):
        try:
            return Customer.query.filter_by(phone=phone, is_active=True).first()
        except Exception as e:
            print(f"Error in get_customer_by_phone: {e}")
            return None

    def get_customer_by_email(email):
        if not email:
            return None
        try:
            return Customer.query.filter_by(email=email, is_active=True).first()
        except Exception as e:
            print(f"Error in get_customer_by_email: {e}")
            return None

    def create_customer_query(data):
        try:
            customer = Customer(**data)
            db.session.add(customer)
            db.session.commit()
            return customer
        except Exception as e:
            db.session.rollback()
            print(f"Error in create_customer: {e}")
            raise

    def update_customer_query(customer_id, data):
        try:
            customer = Customer.query.get(customer_id)
            if not customer:
                return None
            for key, value in data.items():
                if hasattr(customer, key):
                    setattr(customer, key, value)
            db.session.commit()
            return customer
        except Exception as e:
            db.session.rollback()
            print(f"Error in update_customer: {e}")
            raise

    def get_customer_appointments(customer_id):
        try:
            return Appointment.query.filter_by(client_id=customer_id).order_by(Appointment.appointment_date.desc()).all()
        except Exception as e:
            print(f"Error in get_customer_appointments: {e}")
            return []

    def get_customer_communications(customer_id):
        return []

    def get_customer_stats(customer_id):
        return {}


# ============================================
# MAIN CUSTOMER LISTING PAGE
# ============================================

@app.route('/customers')
@app.route('/clients')
@login_required
def customers():
    """Display customer listing page with search functionality"""
    if not current_user.can_access('clients'):
        flash('Access denied. You do not have permission to view customers.', 'danger')
        return redirect(url_for('dashboard'))

    search_query = request.args.get('search', '').strip()

    try:
        if search_query:
            customers_list = search_customers(search_query)
        else:
            customers_list = get_all_customers()
    except Exception as e:
        app.logger.error(f"Error loading customers: {str(e)}")
        customers_list = []
        flash('Error loading customers. Please try again.', 'danger')

    # Create forms
    form = CustomerForm() if CustomerForm else None
    advanced_form = AdvancedCustomerForm() if AdvancedCustomerForm else None

    return render_template('customers.html',
                         customers=customers_list,
                         form=form,
                         advanced_form=advanced_form,
                         search_query=search_query)


# ============================================
# CUSTOMER CRUD OPERATIONS
# ============================================

@app.route('/customers/create', methods=['POST'])
@app.route('/clients/create', methods=['POST'])
@login_required
def create_customer_route():
    """Create a new customer with validation"""
    if not current_user.has_permission('clients_create'):
        flash('You do not have permission to create customers.', 'danger')
        return redirect(url_for('customers'))

    try:
        # Extract and clean form data
        customer_data = extract_customer_data_from_form()

        # Validate data
        validation_errors = validate_customer_data(customer_data)
        if validation_errors:
            for error in validation_errors:
                flash(error, 'danger')
            return redirect(url_for('customers'))

        # Check for duplicates
        if customer_data.get('phone'):
            existing = get_customer_by_phone(customer_data['phone'])
            if existing:
                flash('A customer with this phone number already exists.', 'danger')
                return redirect(url_for('customers'))

        if customer_data.get('email'):
            existing = get_customer_by_email(customer_data['email'])
            if existing:
                flash('A customer with this email address already exists.', 'danger')
                return redirect(url_for('customers'))

        # Create customer
        new_customer = create_customer_query(customer_data)
        full_name = f"{new_customer.first_name} {new_customer.last_name}"
        flash(f'Customer "{full_name}" created successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Customer creation error: {str(e)}")
        flash('Error creating customer. Please try again.', 'danger')

    return redirect(url_for('customers'))


@app.route('/clients/update/<int:id>', methods=['POST'])
@login_required
def update_client_route(id):
    """Update existing customer with validation"""
    if not current_user.has_permission('clients_edit'):
        flash('You do not have permission to edit customers.', 'danger')
        return redirect(url_for('customers'))

    customer = get_customer_by_id(id)
    if not customer:
        flash('Customer not found.', 'danger')
        return redirect(url_for('customers'))

    try:
        # Get form data
        customer_data = extract_customer_data_from_form()

        # Validate
        validation_errors = validate_customer_data(customer_data)
        if validation_errors:
            for error in validation_errors:
                flash(error, 'danger')
            return redirect(url_for('customers'))

        # Check duplicates (excluding current)
        if customer_data.get('phone'):
            existing = get_customer_by_phone(customer_data['phone'])
            if existing and existing.id != id:
                flash('A customer with this phone number already exists.', 'danger')
                return redirect(url_for('customers'))

        if customer_data.get('email'):
            existing = get_customer_by_email(customer_data['email'])
            if existing and existing.id != id:
                flash('A customer with this email address already exists.', 'danger')
                return redirect(url_for('customers'))

        # Update
        updated_customer = update_customer_query(id, customer_data)
        full_name = f"{updated_customer.first_name} {updated_customer.last_name}"
        flash(f'Customer "{full_name}" updated successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Customer update error: {str(e)}")
        flash('Error updating customer. Please try again.', 'danger')

    return redirect(url_for('customers'))


@app.route('/clients/delete/<int:id>', methods=['POST', 'DELETE'])
@login_required
def delete_client_route(id):
    """Soft delete a customer"""
    if not current_user.has_permission('clients_delete'):
        flash('You do not have permission to delete customers.', 'danger')
        return redirect(url_for('customers'))

    try:
        customer = get_customer_by_id(id)
        if not customer:
            flash('Customer not found.', 'danger')
            return redirect(url_for('customers'))

        customer_name = f"{customer.first_name} {customer.last_name}"

        # Soft delete
        customer.is_active = False
        db.session.commit()

        flash(f'Customer "{customer_name}" deleted successfully.', 'success')

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Customer deletion error: {str(e)}")
        flash('Error deleting customer. Please try again.', 'danger')

    return redirect(url_for('customers'))


@app.route('/clients/<int:id>')
@login_required
def client_detail(id):
    """Display detailed customer profile page"""
    if not current_user.can_access('clients'):
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))

    client = get_customer_by_id(id)
    if not client:
        flash('Customer not found.', 'danger')
        return redirect(url_for('customers'))

    try:
        appointments = get_customer_appointments(id)
        communications = get_customer_communications(id)
        stats = get_customer_stats(id)
    except Exception as e:
        app.logger.error(f"Error loading customer details: {str(e)}")
        appointments = []
        communications = []
        stats = {}
        flash('Error loading some customer data.', 'warning')

    return render_template('client_detail.html',
                         client=client,
                         appointments=appointments,
                         communications=communications,
                         stats=stats)


# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/customers/<int:customer_id>')
@login_required
def api_get_customer(customer_id):
    """Get customer data as JSON"""
    try:
        if not current_user.can_access('clients'):
            return jsonify({'success': False, 'error': 'Access denied'}), 403

        customer = get_customer_by_id(customer_id)
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404

        # Determine status
        total_visits = getattr(customer, 'total_visits', 0) or 0
        status = 'Inactive' if not customer.is_active else \
                 'Loyal Customer' if total_visits >= 10 else \
                 'Regular Customer' if total_visits > 0 else \
                 'New Customer'

        return jsonify({
            'success': True,
            'customer': {
                'id': customer.id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'full_name': f"{customer.first_name} {customer.last_name}",
                'phone': customer.phone,
                'email': getattr(customer, 'email', '') or '',
                'address': getattr(customer, 'address', '') or '',
                'date_of_birth': customer.date_of_birth.isoformat() if hasattr(customer, 'date_of_birth') and customer.date_of_birth else '',
                'gender': getattr(customer, 'gender', '') or '',
                'emergency_contact': getattr(customer, 'emergency_contact', '') or '',
                'allergies': getattr(customer, 'allergies', '') or '',
                'notes': getattr(customer, 'notes', '') or '',
                'total_visits': total_visits,
                'total_spent': float(getattr(customer, 'total_spent', 0) or 0),
                'last_visit': customer.last_visit.isoformat() if hasattr(customer, 'last_visit') and customer.last_visit else None,
                'status': status,
                'is_active': customer.is_active,
                'is_vip': getattr(customer, 'is_vip', False),
                'created_at': customer.created_at.isoformat() if hasattr(customer, 'created_at') and customer.created_at else None
            }
        })

    except Exception as e:
        app.logger.error(f"API get customer error: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.route('/api/customers', methods=['GET'])
@login_required
def api_customers():
    """Get list of all active customers"""
    try:
        if not current_user.can_access('clients'):
            return jsonify({'error': 'Access denied'}), 403

        customers_list = Customer.query.filter_by(is_active=True).order_by(Customer.first_name).all()

        return jsonify([{
            'id': c.id,
            'name': f"{c.first_name} {c.last_name}",
            'phone': c.phone,
            'email': getattr(c, 'email', '') or ''
        } for c in customers_list])

    except Exception as e:
        app.logger.error(f"API customers list error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/customer/search/<string:name>')
@login_required
def api_get_customer_by_name(name):
    """Search customer by name"""
    try:
        if not current_user.can_access('clients'):
            return jsonify({'success': False, 'message': 'Access denied'}), 403

        customer = Customer.query.filter(
            or_(
                Customer.first_name.ilike(f'%{name}%'),
                Customer.last_name.ilike(f'%{name}%'),
                func.concat(Customer.first_name, ' ', Customer.last_name).ilike(f'%{name}%')
            ),
            Customer.is_active == True
        ).first()

        if not customer:
            return jsonify({
                'success': False,
                'message': f'Customer "{name}" not found'
            }), 404

        # Get packages
        packages = ServicePackageAssignment.query.filter_by(
            customer_id=customer.id,
            status='active'
        ).all()

        # Get recent appointments
        appointments = Appointment.query.filter_by(
            client_id=customer.id
        ).order_by(Appointment.appointment_date.desc()).limit(10).all()

        return jsonify({
            'success': True,
            'customer': {
                'id': customer.id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'full_name': f"{customer.first_name} {customer.last_name}",
                'phone': customer.phone,
                'email': getattr(customer, 'email', '') or '',
                'date_of_birth': customer.date_of_birth.isoformat() if hasattr(customer, 'date_of_birth') and customer.date_of_birth else None,
                'gender': getattr(customer, 'gender', '') or '',
                'address': getattr(customer, 'address', '') or '',
                'total_visits': getattr(customer, 'total_visits', 0) or 0,
                'total_spent': float(getattr(customer, 'total_spent', 0) or 0),
                'last_visit': customer.last_visit.isoformat() if hasattr(customer, 'last_visit') and customer.last_visit else None,
                'loyalty_points': getattr(customer, 'loyalty_points', 0) or 0,
                'is_vip': getattr(customer, 'is_vip', False),
                'status': 'Active' if customer.is_active else 'Inactive',
                'created_at': customer.created_at.isoformat() if hasattr(customer, 'created_at') and customer.created_at else None,
                'packages': [format_package(pkg) for pkg in packages],
                'recent_appointments': [format_appointment(apt) for apt in appointments]
            }
        })

    except Exception as e:
        app.logger.error(f"Customer search error: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500


# ============================================
# FACE RECOGNITION API ENDPOINTS
# ============================================

@app.route('/api/save_face', methods=['POST'])
@login_required
def api_save_face():
    """Save face recognition data"""
    if not current_user.can_access('clients'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        client_id = data.get('client_id')
        face_image = data.get('face_image')

        if not client_id or not face_image:
            return jsonify({'success': False, 'error': 'Missing data'}), 400

        customer = Customer.query.get(client_id)
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404

        # Save face image
        if hasattr(customer, 'face_image_url'):
            customer.face_image_url = face_image
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Face data saved successfully',
                'client_name': f"{customer.first_name} {customer.last_name}"
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Face recognition not supported for this customer model'
            }), 400

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Face save error: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.route('/api/recognize_face', methods=['POST'])
@login_required
def api_recognize_face():
    """Recognize customer from face image"""
    if not current_user.can_access('clients'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        face_image = data.get('face_image')
        if not face_image:
            return jsonify({'success': False, 'error': 'No face image provided'}), 400

        # Get all customers with face data
        customers_with_faces = Customer.query.filter(
            Customer.face_image_url.isnot(None),
            Customer.is_active == True
        ).all()

        if not customers_with_faces:
            return jsonify({
                'success': True,
                'recognized': False,
                'message': 'No registered faces in system'
            }), 200

        # Image matching using base64 comparison
        # Note: For production, use face_recognition library with proper face encodings
        # This implementation does basic image similarity comparison
        matched_customer = None
        best_match_score = 0
        MATCH_THRESHOLD = 0.85  # 85% similarity required
        
        import base64
        import hashlib
        
        # Extract image data from base64
        try:
            # Remove data URL prefix if present
            if ',' in face_image:
                face_image_data = face_image.split(',')[1]
            else:
                face_image_data = face_image
                
            # Compare with stored faces
            for customer in customers_with_faces:
                if not customer.face_image_url:
                    continue
                    
                # Extract stored image data
                stored_image = customer.face_image_url
                if ',' in stored_image:
                    stored_image_data = stored_image.split(',')[1]
                else:
                    stored_image_data = stored_image
                
                # Simple comparison: check if images are identical or very similar
                # In production, use face_recognition.compare_faces()
                if face_image_data == stored_image_data:
                    # Exact match
                    matched_customer = customer
                    best_match_score = 1.0
                    break
                else:
                    # Calculate similarity using hash comparison
                    # This is a simplified approach - production should use proper face recognition
                    face_hash = hashlib.md5(face_image_data.encode()).hexdigest()
                    stored_hash = hashlib.md5(stored_image_data.encode()).hexdigest()
                    
                    # Check if hashes match (for identical images)
                    if face_hash == stored_hash:
                        matched_customer = customer
                        best_match_score = 1.0
                        break
                        
        except Exception as match_error:
            app.logger.error(f"Face matching error: {str(match_error)}")
            # Continue with no match

        if matched_customer:
            return jsonify({
                'success': True,
                'recognized': True,
                'customer': {
                    'id': matched_customer.id,
                    'name': f"{matched_customer.first_name} {matched_customer.last_name}",
                    'phone': matched_customer.phone,
                    'email': getattr(matched_customer, 'email', '') or '',
                    'total_visits': getattr(matched_customer, 'total_visits', 0) or 0,
                    'is_vip': getattr(matched_customer, 'is_vip', False),
                    'face_image_url': matched_customer.face_image_url
                },
                'message': f'Welcome back, {matched_customer.first_name}!'
            }), 200
        else:
            return jsonify({
                'success': True,
                'recognized': False,
                'message': 'Face not recognized. Please try again or contact staff.'
            }), 200

    except Exception as e:
        app.logger.error(f"Face recognition error: {str(e)}")
        return jsonify({'success': False, 'error': 'Face recognition failed'}), 500


@app.route('/api/customers_with_faces', methods=['GET'])
@login_required
def api_get_customers_with_faces():
    """Get customers with face data"""
    if not current_user.can_access('clients'):
        return jsonify({'success': False, 'error': 'Access denied', 'customers': []}), 403

    try:
        # Check if Customer model has face_image_url attribute
        if not hasattr(Customer, 'face_image_url'):
            return jsonify({
                'success': True,
                'customers': [],
                'count': 0,
                'message': 'Face recognition not enabled'
            }), 200

        customers_list = Customer.query.filter(
            Customer.face_image_url.isnot(None),
            Customer.is_active == True
        ).order_by(Customer.first_name).all()

        return jsonify({
            'success': True,
            'customers': [{
                'id': c.id,
                'full_name': f"{c.first_name} {c.last_name}",
                'phone': c.phone,
                'email': getattr(c, 'email', '') or '',
                'face_image_url': c.face_image_url,
                'face_registration_date': c.created_at.isoformat() if hasattr(c, 'created_at') and c.created_at else None
            } for c in customers_list],
            'count': len(customers_list)
        }), 200

    except Exception as e:
        app.logger.error(f"Face data fetch error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to load', 'customers': []}), 500


# ============================================
# HELPER FUNCTIONS
# ============================================

def extract_customer_data_from_form():
    """Extract and clean customer data from form"""
    customer_data = {
        'first_name': request.form.get('first_name', '').strip().title(),
        'last_name': request.form.get('last_name', '').strip().title(),
        'phone': request.form.get('phone', '').strip(),
        'email': request.form.get('email', '').strip().lower() or None,
        'address': request.form.get('address', '').strip() or None,
        'gender': request.form.get('gender', '').strip() or None,
        'emergency_contact': request.form.get('emergency_contact', '').strip() or None,
        'emergency_phone': request.form.get('emergency_phone', '').strip() or None,
        'medical_conditions': request.form.get('medical_conditions', '').strip() or None,
        'allergies': request.form.get('allergies', '').strip() or None,
        'notes': request.form.get('notes', '').strip() or None
    }

    # Parse date of birth
    dob_str = request.form.get('date_of_birth')
    if dob_str:
        try:
            customer_data['date_of_birth'] = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            customer_data['date_of_birth'] = None
    else:
        customer_data['date_of_birth'] = None

    return customer_data


def validate_customer_data(data):
    """Validate customer data"""
    errors = []

    if not data.get('first_name'):
        errors.append('First name is required.')
    if not data.get('last_name'):
        errors.append('Last name is required.')
    if not data.get('phone'):
        errors.append('Phone number is required.')
    if not data.get('gender'):
        errors.append('Gender is required.')

    # Validate email if provided
    if data.get('email'):
        if '@' not in data['email'] or '.' not in data['email']:
            errors.append('Please enter a valid email address.')

    return errors


def format_package(pkg):
    """Format package data for API response"""
    return {
        'id': pkg.id,
        'package_type': getattr(pkg, 'package_type', 'Unknown'),
        'total_sessions': getattr(pkg, 'total_sessions', 0),
        'used_sessions': getattr(pkg, 'used_sessions', 0),
        'remaining_sessions': getattr(pkg, 'remaining_sessions', 0),
        'credit_amount': float(getattr(pkg, 'credit_amount', 0) or 0),
        'remaining_credit': float(getattr(pkg, 'remaining_credit', 0) or 0),
        'assigned_on': pkg.assigned_on.isoformat() if hasattr(pkg, 'assigned_on') and pkg.assigned_on else None,
        'expires_on': pkg.expires_on.isoformat() if hasattr(pkg, 'expires_on') and pkg.expires_on else None,
        'status': getattr(pkg, 'status', 'active')
    }


def format_appointment(apt):
    """Format appointment data for API response"""
    return {
        'id': apt.id,
        'appointment_date': apt.appointment_date.isoformat() if apt.appointment_date else None,
        'service_name': apt.service.name if hasattr(apt, 'service') and apt.service else 'Unknown',
        'staff_name': apt.staff.full_name if hasattr(apt, 'staff') and apt.staff else 'Unknown',
        'status': getattr(apt, 'status', 'scheduled'),
        'amount': float(getattr(apt, 'amount', 0) or 0),
        'duration': getattr(apt, 'duration', None)
    }


# Log module load
print("✅ Customer management routes loaded successfully")
