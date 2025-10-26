from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from models import Service, Category, UnakiBooking, Customer, User, SystemSetting
from datetime import datetime, date, time, timedelta
import re

@app.route('/')
@app.route('/home')
def website_home():
    """Public website homepage"""
    featured_services = Service.query.filter_by(is_active=True).limit(6).all()
    business_name = SystemSetting.query.filter_by(key='business_name').first()
    business_phone = SystemSetting.query.filter_by(key='business_phone').first()

    return render_template('website/home.html',
                         featured_services=featured_services,
                         business_name=business_name.value if business_name else 'Spa & Salon Suite',
                         business_phone=business_phone.value if business_phone else '')

@app.route('/our-services')
def website_services():
    """Public services page with categories"""
    categories = Category.query.filter_by(category_type='service', is_active=True).order_by(Category.sort_order).all()
    services_by_category = {}

    for category in categories:
        services = Service.query.filter_by(category_id=category.id, is_active=True).all()
        if services:
            services_by_category[category] = services

    uncategorized_services = Service.query.filter_by(is_active=True).filter(
        (Service.category_id == None) | (Service.category_id == 0)
    ).all()

    return render_template('website/services.html',
                         services_by_category=services_by_category,
                         uncategorized_services=uncategorized_services)

@app.route('/book-online', methods=['GET', 'POST'])
def website_book_online():
    """Public online booking page - supports multiple service bookings"""
    if request.method == 'POST':
        try:
            data = request.form

            client_name = data.get('client_name', '').strip()
            client_phone = data.get('client_phone', '').strip()
            client_email = data.get('client_email', '').strip()

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
            
            # Validate email format if provided
            if client_email and client_email.strip():
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, client_email.strip()):
                    flash('Please enter a valid email address.', 'error')
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

            # Create or get customer - ALWAYS search by phone first
            customer = Customer.query.filter_by(phone=client_phone).first()

            if not customer:
                # Customer doesn't exist, create new one
                name_parts = client_name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''

                # Only set email if it's provided and not empty
                email_value = None
                if client_email and client_email.strip():
                    email_value = client_email.strip().lower()

                customer = Customer(
                    first_name=first_name,
                    last_name=last_name,
                    phone=client_phone,
                    email=email_value,
                    created_at=datetime.utcnow()
                )
                db.session.add(customer)
                db.session.flush()
            else:
                # Customer exists - update email if provided and different
                if client_email and client_email.strip():
                    new_email = client_email.strip().lower()
                    if customer.email != new_email:
                        # Check if the new email is already used by another customer
                        existing_email_customer = Customer.query.filter(
                            Customer.email == new_email,
                            Customer.id != customer.id
                        ).first()
                        if not existing_email_customer:
                            customer.email = new_email
                            db.session.flush()

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

                    # Only set email if it's provided and not empty
                    email_value = None
                    if client_email and client_email.strip():
                        email_value = client_email.strip().lower()

                    booking = UnakiBooking(
                        client_id=customer.id,
                        client_name=client_name,
                        client_phone=client_phone,
                        client_email=email_value,
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
                        booking_source='online',
                        booking_method='website',
                        amount_charged=service.price,
                        payment_status='pending',
                        created_at=datetime.utcnow()
                    )

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

    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
    categories = Category.query.filter_by(category_type='service', is_active=True).order_by(Category.sort_order).all()

    today = date.today()
    available_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, 30)]

    # Generate time slots (9 AM to 6 PM, 15-minute intervals) in 12-hour format
    time_slots = []
    current_time = datetime.combine(date.today(), time(9, 0))
    end_time = datetime.combine(date.today(), time(18, 0))

    while current_time <= end_time:
        # Format as 12-hour with AM/PM
        time_slots.append(current_time.strftime('%I:%M %p'))
        current_time += timedelta(minutes=15)

    return render_template('website/book_online.html',
                         services=services,
                         categories=categories,
                         available_dates=available_dates,
                         time_slots=time_slots)

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

    return render_template('website/booking_success.html', 
                         booking=booking, 
                         all_bookings=all_bookings,
                         total_price=total_price)

@app.route('/contact')
def website_contact():
    """Public contact page with map and business details"""
    business_settings = {}

    keys = ['business_name', 'business_address', 'business_phone', 'business_email', 
            'business_hours', 'google_maps_api_key', 'whatsapp_number']

    for key in keys:
        setting = SystemSetting.query.filter_by(key=key).first()
        business_settings[key] = setting.value if setting else ''

    if not business_settings['business_name']:
        business_settings['business_name'] = 'Spa & Salon Suite'
    if not business_settings['business_address']:
        business_settings['business_address'] = '123 Main Street, Your City, State 12345'
    if not business_settings['business_phone']:
        business_settings['business_phone'] = '+1-555-123-4567'

    return render_template('website/contact.html', **business_settings)

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

    return render_template('website/gallery.html', images=images)

@app.route('/about')
def website_about():
    """About us page"""
    business_name = SystemSetting.query.filter_by(key='business_name').first()
    business_description = SystemSetting.query.filter_by(key='business_description').first()

    return render_template('website/about.html',
                         business_name=business_name.value if business_name else 'Spa & Salon Suite',
                         business_description=business_description.value if business_description else '')