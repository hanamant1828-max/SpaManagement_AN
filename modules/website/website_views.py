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

            if not all([client_name, client_phone]):
                flash('Please fill in all required fields.', 'error')
                return redirect(url_for('website_book_online'))

            # Parse multiple services from form data
            services_data = {}
            for key in data.keys():
                if key.startswith('services['):
                    # Extract index and field name: services[0][service_id]
                    import re
                    match = re.match(r'services\[(\d+)\]\[(\w+)\]', key)
                    if match:
                        index = int(match.group(1))
                        field = match.group(2)
                        if index not in services_data:
                            services_data[index] = {}
                        services_data[index][field] = data.get(key, '').strip()

            if not services_data:
                flash('Please select at least one service.', 'error')
                return redirect(url_for('website_book_online'))

            # Create or get customer - ALWAYS search by phone first
            customer = Customer.query.filter_by(phone=client_phone).first()
            
            if not customer:
                # Customer doesn't exist, create new one
                name_parts = client_name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                customer = Customer(
                    first_name=first_name,
                    last_name=last_name,
                    phone=client_phone,
                    email=client_email if client_email else None,
                    created_at=datetime.utcnow()
                )
                db.session.add(customer)
                db.session.flush()
            else:
                # Customer exists - update email if provided and different
                if client_email and customer.email != client_email:
                    customer.email = client_email
                    db.session.flush()

            # Get available staff
            available_staff = User.query.filter_by(is_active=True).first()
            if not available_staff:
                flash('No staff available. Please contact us directly.', 'error')
                return redirect(url_for('website_contact'))

            # Create bookings for each service
            created_bookings = []
            for index in sorted(services_data.keys()):
                service_info = services_data[index]

                service_id = service_info.get('service_id')
                appointment_date_str = service_info.get('appointment_date')
                appointment_time_str = service_info.get('appointment_time')
                notes = service_info.get('notes', '')

                if not all([service_id, appointment_date_str, appointment_time_str]):
                    continue  # Skip incomplete entries

                service = Service.query.get(service_id)
                if not service:
                    continue  # Skip invalid services

                appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
                appointment_time_obj = datetime.strptime(appointment_time_str, '%H:%M').time()

                start_datetime = datetime.combine(appointment_date, appointment_time_obj)
                end_datetime = start_datetime + timedelta(minutes=service.duration)

                booking = UnakiBooking(
                    client_id=customer.id,
                    client_name=client_name,
                    client_phone=client_phone,
                    client_email=client_email,
                    staff_id=available_staff.id,
                    staff_name=f"{available_staff.first_name} {available_staff.last_name}",
                    service_id=service.id,
                    service_name=service.name,
                    service_duration=service.duration,
                    service_price=service.price,
                    appointment_date=appointment_date,
                    start_time=appointment_time_obj,
                    end_time=end_datetime.time(),
                    status='pending',  # Default to pending for online bookings - admin must review
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
                flash('No valid bookings were created. Please check your entries.', 'error')
                return redirect(url_for('website_book_online'))

            db.session.commit()

            # Success message
            if len(created_bookings) == 1:
                flash(f'Booking confirmed! We will contact you at {client_phone} to confirm your appointment.', 'success')
            else:
                flash(f'{len(created_bookings)} appointments booked successfully! We will contact you at {client_phone} to confirm.', 'success')

            return redirect(url_for('website_booking_success', booking_id=created_bookings[0].id))

        except Exception as e:
            db.session.rollback()
            print(f"Booking error: {e}")
            import traceback
            traceback.print_exc()
            flash('An error occurred. Please try again or contact us directly.', 'error')
            return redirect(url_for('website_book_online'))

    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
    categories = Category.query.filter_by(category_type='service', is_active=True).order_by(Category.sort_order).all()

    today = date.today()
    available_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, 30)]

    time_slots = []
    for hour in range(9, 20):
        for minute in [0, 30]:
            time_slots.append(f"{hour:02d}:{minute:02d}")

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