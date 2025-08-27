"""
Enhanced Packages related database queries with session tracking and validity management
"""
import csv
from datetime import datetime, timedelta
from io import StringIO
from sqlalchemy import func, and_
from app import db
from models import Package, ClientPackage, Service, PackageService, Client

def get_all_packages():
    """Get all active packages with enhanced features"""
    return Package.query.filter_by(is_active=True).order_by(Package.sort_order, Package.name).all()

def get_package_by_id(package_id):
    """Get package by ID"""
    return Package.query.get(package_id)

def create_package(package_data, included_services=None):
    """Create new package with multiple services and individual pricing"""
    package = Package(
        name=package_data['name'],
        description=package_data.get('description'),
        package_type=package_data.get('package_type', 'regular'),
        duration_months=package_data.get('duration_months', 1),
        total_sessions=package_data.get('total_sessions', 1),
        validity_days=package_data.get('validity_days', 30),
        total_price=package_data['total_price'],
        discount_percentage=package_data.get('discount_percentage', 0.0),
        is_active=package_data.get('is_active', True)
    )

    db.session.add(package)
    db.session.flush()  # Get the package ID

    # Add included services with individual pricing
    if included_services:
        for service_data in included_services:
            service = Service.query.get(service_data['service_id'])
            if service:
                # Use service-specific pricing if provided, otherwise fall back to service defaults
                original_price = service_data.get('original_price', service.price)
                service_discount = service_data.get('service_discount', 0.0)
                final_price = service_data.get('final_price', original_price * (1 - (service_discount / 100)))
                sessions = service_data.get('sessions', 1)

                package_service = PackageService(
                    package_id=package.id,
                    service_id=service_data['service_id'],
                    sessions_included=sessions,
                    service_discount=service_discount,
                    original_price=original_price,
                    discounted_price=final_price
                )
                db.session.add(package_service)

    db.session.commit()
    return package

def update_package(package_id, package_data, included_services=None):
    """Update package with services"""
    package = Package.query.get(package_id)
    if not package:
        raise ValueError("Package not found")

    # Update package data
    for key, value in package_data.items():
        if hasattr(package, key):
            setattr(package, key, value)

    # Update services if provided
    if included_services is not None:
        # Remove existing services
        PackageService.query.filter_by(package_id=package_id).delete()

        # Add new services
        for service_id in included_services:
            service = Service.query.get(service_id)
            if service:
                package_service = PackageService(
                    package_id=package_id,
                    service_id=service_id,
                    sessions_included=1,
                    service_discount=package_data.get('discount_percentage', 0.0),
                    original_price=service.price,
                    discounted_price=service.price * (1 - (package_data.get('discount_percentage', 0.0) / 100))
                )
                db.session.add(package_service)

    db.session.commit()
    return package

def delete_package(package_id):
    """Delete package if not assigned to any clients"""
    package = Package.query.get(package_id)
    if not package:
        return {'success': False, 'message': 'Package not found'}

    # Check if package is assigned to any clients
    client_count = ClientPackage.query.filter_by(package_id=package_id, is_active=True).count()
    if client_count > 0:
        return {
            'success': False,
            'message': f'Cannot delete package. It is assigned to {client_count} client(s).'
        }

    # Soft delete - mark as inactive
    package.is_active = False
    db.session.commit()
    return {'success': True, 'message': f'Package "{package.name}" deleted successfully'}

def get_client_packages(client_id=None):
    """Get client's active packages"""
    query = ClientPackage.query.filter_by(is_active=True)
    if client_id:
        query = query.filter_by(client_id=client_id)
    return query.all()

def assign_package_to_client(client_id, package_id):
    """Assign a package to a client with enhanced tracking"""
    package = Package.query.get(package_id)
    if not package:
        raise ValueError("Package not found")

    # Calculate expiry date based on validity_days
    expiry_date = datetime.utcnow() + timedelta(days=package.validity_days)

    client_package = ClientPackage(
        client_id=client_id,
        package_id=package_id,
        purchase_date=datetime.utcnow(),
        expiry_date=expiry_date,
        sessions_remaining=package.total_sessions,
        sessions_used=0,
        amount_paid=package.total_price,
        is_active=True
    )

    db.session.add(client_package)
    db.session.commit()
    return client_package

def get_package_services(package_id):
    """Get all services included in a package"""
    return PackageService.query.filter_by(package_id=package_id).all()

def add_service_to_package(package_id, service_id, sessions_included=1, service_discount=0.0):
    """Add a service to an existing package"""
    service = Service.query.get(service_id)
    if not service:
        raise ValueError("Service not found")

    package_service = PackageService(
        package_id=package_id,
        service_id=service_id,
        sessions_included=sessions_included,
        service_discount=service_discount,
        original_price=service.price,
        discounted_price=service.price * (1 - (service_discount / 100))
    )

    db.session.add(package_service)
    db.session.commit()
    return package_service

def get_available_services():
    """Get all available services for package creation"""
    return Service.query.filter_by(is_active=True).order_by(Service.name).all()

def track_package_usage(client_package_id):
    """Track package usage for a specific client package"""
    client_package = ClientPackage.query.get(client_package_id)
    if not client_package:
        raise ValueError("Client package not found")

    # Get usage statistics
    usage_data = {
        'client_package': client_package,
        'package': client_package.package,
        'client': Client.query.get(client_package.client_id),
        'sessions_total': client_package.package.total_sessions,
        'sessions_used': getattr(client_package, 'sessions_used', 0),
        'sessions_remaining': getattr(client_package, 'sessions_remaining', client_package.package.total_sessions),
        'usage_percentage': (getattr(client_package, 'sessions_used', 0) / client_package.package.total_sessions) * 100,
        'days_remaining': (client_package.expiry_date - datetime.utcnow()).days if client_package.expiry_date > datetime.utcnow() else 0,
        'is_expired': client_package.expiry_date < datetime.utcnow(),
        'package_services': get_package_services(client_package.package_id)
    }

    return usage_data

def auto_expire_packages():
    """Automatically expire packages based on validity period"""
    expired_packages = ClientPackage.query.filter(
        and_(
            ClientPackage.expiry_date < datetime.utcnow(),
            ClientPackage.is_active == True
        )
    ).all()

    for client_package in expired_packages:
        client_package.is_active = False

    if expired_packages:
        db.session.commit()

    return len(expired_packages)

def export_packages_csv():
    """Export packages data to CSV format"""
    packages = get_all_packages()

    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'Package Name', 'Description', 'Package Type', 'Total Sessions', 
        'Validity Days', 'Total Price', 'Discount %', 'Active Clients', 'Status'
    ])

    # Write package data
    for package in packages:
        active_clients = ClientPackage.query.filter_by(package_id=package.id, is_active=True).count()
        writer.writerow([
            package.name,
            package.description or '',
            getattr(package, 'package_type', 'regular'),
            package.total_sessions,
            package.validity_days,
            package.total_price,
            package.discount_percentage,
            active_clients,
            'Active' if package.is_active else 'Inactive'
        ])

    return output.getvalue()

def export_package_usage_csv():
    """Export package usage data to CSV format"""
    client_packages = get_client_packages()

    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'Client Name', 'Package Name', 'Purchase Date', 'Expiry Date', 
        'Sessions Total', 'Sessions Used', 'Sessions Remaining', 'Amount Paid', 'Status'
    ])

    # Write usage data
    for client_package in client_packages:
        client = Client.query.get(client_package.client_id)
        package = client_package.package

        sessions_used = getattr(client_package, 'sessions_used', 0)
        sessions_remaining = getattr(client_package, 'sessions_remaining', package.total_sessions)
        status = 'Active'

        if client_package.expiry_date < datetime.utcnow():
            status = 'Expired'
        elif sessions_remaining <= 0:
            status = 'Completed'

        writer.writerow([
            f"{client.first_name} {client.last_name}",
            package.name,
            client_package.purchase_date.strftime('%Y-%m-%d'),
            client_package.expiry_date.strftime('%Y-%m-%d'),
            package.total_sessions,
            sessions_used,
            sessions_remaining,
            client_package.amount_paid,
            status
        ])

    return output.getvalue()

def get_package_statistics():
    """Get comprehensive package statistics"""
    total_packages = Package.query.filter_by(is_active=True).count()
    active_assignments = ClientPackage.query.filter_by(is_active=True).count()
    total_revenue = db.session.query(func.sum(ClientPackage.amount_paid)).filter_by(is_active=True).scalar() or 0

    # Monthly package sales
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_sales = ClientPackage.query.filter(
        ClientPackage.purchase_date >= current_month_start,
        ClientPackage.is_active == True
    ).count()

    return {
        'total_packages': total_packages,
        'active_assignments': active_assignments,
        'total_revenue': total_revenue,
        'monthly_sales': monthly_sales
    }

def create_package_with_services(name, description, package_type, validity_days, 
                                   total_price, discount_percentage, is_active, services_data):
    """Create a package with associated services"""
    try:
        # Calculate total sessions from services
        total_sessions = sum(service['sessions'] for service in services_data)

        # Calculate duration_months from validity_days
        duration_months = max(1, validity_days // 30)

        # Create the package
        package = Package(
            name=name,
            description=description,
            package_type=package_type,
            validity_days=validity_days,
            duration_months=duration_months,
            total_sessions=total_sessions,
            total_price=total_price,
            discount_percentage=discount_percentage,
            is_active=is_active
        )

        db.session.add(package)
        db.session.flush()  # Get the package ID

        # Add services to the package
        for service_data in services_data:
            service = Service.query.get(service_data['service_id'])
            if service:
                package_service = PackageService(
                    package_id=package.id,
                    service_id=service.id,
                    sessions_included=service_data['sessions'],
                    service_discount_percentage=service_data.get('service_discount', 0)
                )
                db.session.add(package_service)

        db.session.commit()
        return package

    except Exception as e:
        db.session.rollback()
        print(f"Error creating package: {str(e)}")
        return None