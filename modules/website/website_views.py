from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from models import Service, Category, UnakiBooking, Customer, User, SystemSetting
from datetime import datetime, date, time, timedelta
from sqlalchemy import or_
import re

# Search functionality enabled

def get_business_settings():
    """Get common business settings for website templates"""
    business_name = SystemSetting.query.filter_by(key='business_name').first()
    business_phone = SystemSetting.query.filter_by(key='business_phone').first()
    business_logo = SystemSetting.query.filter_by(key='business_logo').first()
    business_email = SystemSetting.query.filter_by(key='gst_email').first()
    business_address = SystemSetting.query.filter_by(key='gst_business_address').first()
    
    return {
        'business_name': business_name.value if business_name else 'Spa & Salon Suite',
        'business_phone': business_phone.value if business_phone else '',
        'business_logo': business_logo.value if business_logo else None,
        'business_email': business_email.value if business_email else '',
        'business_address': business_address.value if business_address else ''
    }

@app.route('/')
@app.route('/home')
def website_home():
    """Public website homepage"""
    featured_services = Service.query.filter_by(is_active=True).limit(6).all()
    settings = get_business_settings()

    return render_template('website/home.html',
                         featured_services=featured_services,
                         **settings)

@app.route('/our-services')
def website_services():
    """Public services page - shows category selection"""
    categories = Category.query.filter_by(category_type='service', is_active=True).order_by(Category.sort_order).all()

    # Count services in each category
    categories_with_counts = []
    for category in categories:
        service_count = Service.query.filter_by(category_id=category.id, is_active=True).count()
        if service_count > 0:
            categories_with_counts.append({
                'category': category,
                'count': service_count
            })

    # Check for uncategorized services
    uncategorized_count = Service.query.filter_by(is_active=True).filter(
        (Service.category_id == None) | (Service.category_id == 0)
    ).count()

    settings = get_business_settings()
    return render_template('website/services.html',
                         categories=categories_with_counts,
                         selected_category=None,
                         uncategorized_count=uncategorized_count,
                         **settings)

@app.route('/our-services/search')
def website_services_search():
    """Search services by name or description"""
    search_query = request.args.get('q', '').strip()

    if not search_query:
        return redirect(url_for('website_services'))

    # Search in service name and description (case-insensitive)
    services = Service.query.filter(
        Service.is_active == True,
        or_(
            Service.name.ilike(f'%{search_query}%'),
            Service.description.ilike(f'%{search_query}%')
        )
    ).all()

    # Get all categories for navigation
    all_categories = Category.query.filter_by(category_type='service', is_active=True).order_by(Category.sort_order).all()
    categories_with_counts = []
    for cat in all_categories:
        service_count = Service.query.filter_by(category_id=cat.id, is_active=True).count()
        if service_count > 0:
            categories_with_counts.append({
                'category': cat,
                'count': service_count
            })

    # Check for uncategorized services
    uncategorized_count = Service.query.filter_by(is_active=True).filter(
        (Service.category_id == None) | (Service.category_id == 0)
    ).count()

    # Create a search result category object for display
    class SearchResultCategory:
        display_name = f"Search Results for '{search_query}'"
        description = f"Found {len(services)} service{'s' if len(services) != 1 else ''}"
        icon = "fas fa-search"

    settings = get_business_settings()
    return render_template('website/services.html',
                         categories=categories_with_counts,
                         selected_category=SearchResultCategory(),
                         services=services,
                         uncategorized_count=uncategorized_count,
                         search_query=search_query,
                         **settings)

@app.route('/our-services/uncategorized')
def website_services_uncategorized():
    """Show uncategorized services"""
    # Get uncategorized services
    services = Service.query.filter_by(is_active=True).filter(
        (Service.category_id == None) | (Service.category_id == 0)
    ).all()

    # Get all categories for navigation
    all_categories = Category.query.filter_by(category_type='service', is_active=True).order_by(Category.sort_order).all()
    categories_with_counts = []
    for cat in all_categories:
        service_count = Service.query.filter_by(category_id=cat.id, is_active=True).count()
        if service_count > 0:
            categories_with_counts.append({
                'category': cat,
                'count': service_count
            })

    # Check for uncategorized services
    uncategorized_count = len(services)

    # Create a fake category object for display
    class UncategorizedCategory:
        display_name = "Other Services"
        description = "Additional services and treatments"
        icon = "fas fa-spa"

    settings = get_business_settings()
    return render_template('website/services.html',
                         categories=categories_with_counts,
                         selected_category=UncategorizedCategory(),
                         services=services,
                         uncategorized_count=uncategorized_count,
                         **settings)

@app.route('/our-services/category/<int:category_id>')
def website_services_by_category(category_id):
    """Show services for a specific category"""
    category = Category.query.get_or_404(category_id)

    # Verify this is an active service category
    if category.category_type != 'service' or not category.is_active:
        flash('Category not found or inactive.', 'error')
        return redirect(url_for('website_services'))

    # Get all services in this category
    services = Service.query.filter_by(category_id=category_id, is_active=True).all()

    # Get all categories for navigation
    all_categories = Category.query.filter_by(category_type='service', is_active=True).order_by(Category.sort_order).all()
    categories_with_counts = []
    for cat in all_categories:
        service_count = Service.query.filter_by(category_id=cat.id, is_active=True).count()
        if service_count > 0:
            categories_with_counts.append({
                'category': cat,
                'count': service_count
            })

    # Check for uncategorized services
    uncategorized_count = Service.query.filter_by(is_active=True).filter(
        (Service.category_id == None) | (Service.category_id == 0)
    ).count()

    settings = get_business_settings()
    return render_template('website/services.html',
                         categories=categories_with_counts,
                         selected_category=category,
                         services=services,
                         uncategorized_count=uncategorized_count,
                         **settings)

@app.route('/book-online', methods=['GET', 'POST'])
def website_book_online():
    """Public online booking page - supports multiple service bookings"""
    if request.method == 'POST':
        try:
            data = request.form

            client_name = data.get('client_name', '').strip()
            client_phone = data.get('client_phone', '').strip()
            client_email = data.get('client_email', '').strip()  # Optional, not collected in form

            # Validate required fields
            if not client_name:
                flash('Please enter your full name.', 'error')
                return redirect(url_for('website_book_online'))

            if not client_phone:
                flash('Please enter your phone number.', 'error')
                return redirect(url_for('website_book_online'))

            # Clean and validate phone number
            client_phone = re.sub(r'[^\d+]', '', client_phone)
            if len(client_phone) < 10:
                flash('Please enter a valid phone number (at least 10 digits).', 'error')
                return redirect(url_for('website_book_online'))

            # Parse multiple services from form data
            services_data = {}
            for key in data.keys():
                if key.startswith('services['):
                    # Extract index and field name: services[0][service_id]
                    match = re.match(r'services\[(\d+)\]\[(\w+)\]', key)
                    if match:
                        index = int(match.group(1))
                        field = match.group(2)
                        if index not in services_data:
                            services_data[index] = {}
                        services_data[index][field] = data.get(key, '').strip()

            if not services_data:
                flash('Please select at least one service with date and time.', 'error')
                return redirect(url_for('website_book_online'))

            # Get or create customer - CRITICAL: Ensure customer record exists and is linked
            customer = Customer.query.filter_by(phone=client_phone).first()
            if not customer:
                # Create new customer with proper name parsing
                name_parts = client_name.strip().split(maxsplit=1)
                first_name = name_parts[0] if name_parts else 'Guest'
                last_name = name_parts[1] if len(name_parts) > 1 else ''

                customer = Customer(
                    first_name=first_name,
                    last_name=last_name,
                    phone=client_phone,
                    email=client_email if client_email and '@' in client_email else None,
                    is_active=True,
                    total_visits=0,
                    total_spent=0.0
                )
                db.session.add(customer)
                db.session.flush()  # Get the customer ID immediately

                print(f"✅ Created new customer: {customer.first_name} {customer.last_name} (ID: {customer.id}, Phone: {customer.phone})")
            else:
                print(f"✅ Found existing customer: {customer.first_name} {customer.last_name} (ID: {customer.id}, Phone: {customer.phone})")
                # Update email if provided and customer doesn't have one
                if client_email and '@' in client_email and not customer.email:
                    customer.email = client_email
                    db.session.flush()  # Ensure update is saved
                    print(f"   Updated customer email to: {client_email}")

            # Get available staff
            available_staff = User.query.filter_by(is_active=True).first()
            if not available_staff:
                flash('No staff available. Please contact us directly.', 'error')
                return redirect(url_for('website_contact'))

            # Create bookings for each service
            created_bookings = []
            validation_errors = []

            try:
                for index in sorted(services_data.keys()):
                    service_info = services_data[index]

                    service_id = service_info.get('service_id')
                    appointment_date_str = service_info.get('appointment_date')
                    appointment_time_str = service_info.get('appointment_time')
                    notes = service_info.get('notes', '')

                    print(f"Processing service {index}: service_id={service_id}, date={appointment_date_str}, time={appointment_time_str}")

                    if not all([service_id, appointment_date_str, appointment_time_str]):
                        validation_errors.append(f"Service #{index + 1}: Missing required information (service, date, or time)")
                        print(f"Skipping incomplete entry at index {index}")
                        continue  # Skip incomplete entries

                    service = Service.query.get(service_id)
                    if not service:
                        validation_errors.append(f"Service #{index + 1}: Invalid service selected")
                        print(f"Service not found: {service_id}")
                        continue  # Skip invalid services

                    # Validate appointment date is not in the past
                    try:
                        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
                        if appointment_date < date.today():
                            validation_errors.append(f"Service #{index + 1}: Cannot book appointments in the past")
                            print(f"Appointment date is in the past: {appointment_date}")
                            continue
                    except ValueError:
                        validation_errors.append(f"Service #{index + 1}: Invalid date format")
                        print(f"Invalid date format: {appointment_date_str}")
                        continue

                    # Parse time - handle both 12-hour and 24-hour formats
                    appointment_time_obj = None
                    for time_format in ['%I:%M %p', '%H:%M', '%I:%M%p']:
                        try:
                            appointment_time_obj = datetime.strptime(appointment_time_str.strip(), time_format).time()
                            break
                        except ValueError:
                            continue

                    if not appointment_time_obj:
                        validation_errors.append(f"Service #{index + 1}: Invalid time format")
                        print(f"Invalid time format: {appointment_time_str}")
                        continue

                    start_datetime = datetime.combine(appointment_date, appointment_time_obj)
                    end_datetime = start_datetime + timedelta(minutes=service.duration)

                    # Verify customer exists with valid ID
                    if not customer or not customer.id:
                        raise Exception("Customer record missing or invalid - this should not happen")

                    booking = UnakiBooking(
                        client_id=customer.id,  # Link to customer record
                        client_name=client_name,
                        client_phone=client_phone,
                        client_email=customer.email, # Use customer's email
                        staff_id=available_staff.id,
                        staff_name=f"{available_staff.first_name} {available_staff.last_name}",
                        service_id=service.id,
                        service_name=service.name,
                        service_duration=service.duration,
                        service_price=service.price,
                        appointment_date=appointment_date,
                        start_time=appointment_time_obj,
                        end_time=end_datetime.time(),
                        status='scheduled',  # Default to scheduled for online bookings - admin can confirm later
                        notes=notes,
                        booking_source='online',  # Always 'online' for website bookings
                        booking_method='online_booking',
                        amount_charged=service.price,
                        payment_status='pending',
                        created_at=datetime.utcnow()
                    )

                    print(f"📋 Creating booking with client_id: {customer.id} ({client_name})")

                    db.session.add(booking)
                    created_bookings.append(booking)

                if not created_bookings:
                    if validation_errors:
                        error_msg = 'Please fix the following issues: ' + '; '.join(validation_errors)
                        flash(error_msg, 'error')
                    else:
                        flash('No valid bookings were created. Please ensure all services have a date and time selected.', 'error')
                    return redirect(url_for('website_book_online'))

                db.session.commit()
            except Exception as booking_error:
                db.session.rollback()
                print(f"Error creating bookings: {booking_error}")
                import traceback
                traceback.print_exc()
                flash('Unable to create booking. Please contact us directly.', 'error')
                return redirect(url_for('website_book_online'))

            # Success message
            if len(created_bookings) == 1:
                flash(f'Booking confirmed! We will contact you at {client_phone} to confirm your appointment.', 'success')
            else:
                flash(f'{len(created_bookings)} appointments booked successfully! We will contact you at {client_phone} to confirm.', 'success')

            return redirect(url_for('website_booking_success', booking_id=created_bookings[0].id))

        except Exception as e:
            db.session.rollback()
            print(f"=== BOOKING ERROR ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print(f"Client name: {client_name}")
            print(f"Client phone: {client_phone}")
            print(f"Client email: {client_email}")
            import traceback
            traceback.print_exc()
            print(f"=== END BOOKING ERROR ===")
            flash(f'Booking error: {str(e)}. Please try again or contact us directly.', 'error')
            return redirect(url_for('website_book_online'))

    # Get data for the booking form (same as multi-appointment booking)
    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
    staff_members = User.query.filter_by(is_active=True).all()
    clients = Customer.query.filter_by(is_active=True).order_by(Customer.first_name, Customer.last_name).all()
    today = date.today().strftime('%Y-%m-%d')

    # Get system settings
    settings = get_business_settings()

    return render_template('website/online_booking.html',
                         services=services,
                         staff_members=staff_members,
                         clients=clients,
                         today=today,
                         **settings)

@app.route('/booking-success/<int:booking_id>')
def website_booking_success(booking_id):
    """Booking confirmation page - shows all bookings from the same submission"""
    booking = UnakiBooking.query.get_or_404(booking_id)

    # Get all bookings created within the last 5 minutes for the same customer
    # This captures all bookings from the same multi-service submission
    recent_cutoff = datetime.utcnow() - timedelta(minutes=5)
    all_bookings = UnakiBooking.query.filter(
        UnakiBooking.client_phone == booking.client_phone,
        UnakiBooking.created_at >= recent_cutoff,
        UnakiBooking.booking_source == 'online'
    ).order_by(UnakiBooking.appointment_date, UnakiBooking.start_time).all()

    # Calculate total price
    total_price = sum(b.service_price for b in all_bookings)

    settings = get_business_settings()
    return render_template('website/booking_success.html', 
                         booking=booking, 
                         all_bookings=all_bookings,
                         total_price=total_price,
                         **settings)

@app.route('/contact')
def website_contact():
    """Public contact page with map and business details"""
    settings = get_business_settings()

    # Additional settings for contact page
    keys = ['business_hours', 'google_maps_api_key', 'whatsapp_number']
    for key in keys:
        setting = SystemSetting.query.filter_by(key=key).first()
        settings[key] = setting.value if setting else ''

    if not settings['business_address']:
        settings['business_address'] = '123 Main Street, Your City, State 12345'

    return render_template('website/contact.html', **settings)

@app.route('/gallery')
def website_gallery():
    """Public image gallery page"""
    import os
    gallery_path = os.path.join(app.static_folder, 'images', 'gallery')

    images = []
    if os.path.exists(gallery_path):
        for filename in os.listdir(gallery_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                images.append(f'/static/images/gallery/{filename}')

    settings = get_business_settings()
    return render_template('website/gallery.html', images=images, **settings)

@app.route('/about')
def website_about():
    """About us page"""
    settings = get_business_settings()
    business_description = SystemSetting.query.filter_by(key='business_description').first()

    return render_template('website/about.html',
                         business_description=business_description.value if business_description else '',
                         **settings)