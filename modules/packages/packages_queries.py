"""
Packages related database queries
"""
from datetime import datetime, date
from sqlalchemy import func, and_
from app import db
from models import Package, ClientPackage, PackageService, Service

def get_all_packages():
    """Get all packages with their services"""
    try:
        packages = Package.query.order_by(Package.created_at.desc()).all()
        return packages
    except Exception as e:
        print(f"Error getting packages: {e}")
        return []

def get_package_by_id(package_id):
    """Get package by ID"""
    return Package.query.get(package_id)

def create_package(package_data, service_ids=None):
    """Create new package with multiple services"""
    package = Package(
        name=package_data['name'],
        description=package_data.get('description'),
        total_sessions=package_data.get('total_sessions', 1),
        validity_days=package_data.get('validity_days', 90),
        total_price=package_data['total_price'],
        discount_percentage=package_data.get('discount_percentage', 0.0),
        is_active=package_data.get('is_active', True),
        duration_months=package_data.get('validity_days', 90) // 30  # Convert days to months for compatibility
    )

    db.session.add(package)
    db.session.flush()  # Get package ID

    # Add services to package if provided
    if service_ids:
        for service_id in service_ids:
            package_service = PackageService(
                package_id=package.id,
                service_id=service_id,
                sessions_included=1  # Default to 1 session per service
            )
            db.session.add(package_service)

    db.session.commit()
    return package

def update_package(package_id, package_data, service_ids=None):
    """Update package and its services"""
    package = Package.query.get(package_id)
    if not package:
        raise ValueError("Package not found")

    # Update package data
    for key, value in package_data.items():
        if hasattr(package, key):
            setattr(package, key, value)

    # Update duration_months for compatibility
    if 'validity_days' in package_data:
        package.duration_months = package_data['validity_days'] // 30

    # Update services if provided
    if service_ids is not None:
        # Remove existing services and add new ones
        PackageService.query.filter_by(package_id=package_id).delete()

        for service_id in service_ids:
            package_service = PackageService(
                package_id=package_id,
                service_id=service_id,
                sessions_included=1
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
    client_count = ClientPackage.query.filter_by(package_id=package_id).count()
    if client_count > 0:
        return {
            'success': False,
            'message': f'Cannot delete package. It is assigned to {client_count} client(s).'
        }

    # Delete package services first
    PackageService.query.filter_by(package_id=package_id).delete()

    db.session.delete(package)
    db.session.commit()
    return {'success': True, 'message': f'Package "{package.name}" deleted successfully'}

def get_client_packages(client_id=None):
    """Get client's active packages or all if no client_id specified"""
    if client_id:
        return ClientPackage.query.filter_by(client_id=client_id, is_active=True).all()
    else:
        return ClientPackage.query.filter_by(is_active=True).all()

def assign_package_to_client(client_id, package_id):
    """Assign a package to a client with validity tracking"""
    from datetime import datetime, timedelta

    package = Package.query.get(package_id)
    if not package:
        raise ValueError("Package not found")

    # Calculate expiry date based on validity days
    expiry_date = datetime.utcnow() + timedelta(days=package.validity_days)

    client_package = ClientPackage(
        client_id=client_id,
        package_id=package_id,
        purchase_date=datetime.utcnow(),
        expiry_date=expiry_date,
        sessions_remaining=package.total_sessions,
        is_active=True
    )

    db.session.add(client_package)
    db.session.commit()
    return client_package

def get_package_services(package_id):
    """Get services included in a package"""
    return PackageService.query.filter_by(package_id=package_id).all()

def add_service_to_package(package_id, service_id, sessions_included):
    """Add a service to a package"""
    package_service = PackageService(
        package_id=package_id,
        service_id=service_id,
        sessions_included=sessions_included
    )
    db.session.add(package_service)
    db.session.commit()
    return package_service

def get_available_services():
    """Get all available services"""
    return Service.query.filter_by(is_active=True).order_by(Service.name).all()

def create_package(package_data, service_ids):
    """Create new package with multiple services"""
    package = Package(
        name=package_data['name'],
        description=package_data.get('description'),
        total_sessions=package_data['total_sessions'],
        validity_days=package_data['validity_days'],
        total_price=package_data['total_price'],
        discount_percentage=package_data.get('discount_percentage', 0.0),
        is_active=package_data.get('is_active', True),
        duration_months=package_data.get('validity_days', 90) // 30  # Convert days to months for compatibility
    )

    db.session.add(package)
    db.session.flush()  # Get package ID

    # Add services to package
    for service_id in service_ids:
        package_service = PackageService(
            package_id=package.id,
            service_id=service_id,
            sessions_included=1  # Default to 1 session per service
        )
        db.session.add(package_service)

    db.session.commit()
    return package

def update_package(package_id, package_data, service_ids):
    """Update package and its services"""
    package = Package.query.get(package_id)
    if not package:
        raise ValueError("Package not found")

    # Update package data
    for key, value in package_data.items():
        if hasattr(package, key):
            setattr(package, key, value)

    # Update duration_months for compatibility
    if 'validity_days' in package_data:
        package.duration_months = package_data['validity_days'] // 30

    # Remove existing services and add new ones
    PackageService.query.filter_by(package_id=package_id).delete()

    for service_id in service_ids:
        package_service = PackageService(
            package_id=package_id,
            service_id=service_id,
            sessions_included=1
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
    client_count = ClientPackage.query.filter_by(package_id=package_id).count()
    if client_count > 0:
        return {
            'success': False,
            'message': f'Cannot delete package. It is assigned to {client_count} client(s).'
        }

    # Delete package services first
    PackageService.query.filter_by(package_id=package_id).delete()

    db.session.delete(package)
    db.session.commit()
    return {'success': True, 'message': f'Package "{package.name}" deleted successfully'}

def track_package_usage(client_package_id):
    """Track detailed package usage for a client"""
    from models import Appointment

    client_package = ClientPackage.query.get(client_package_id)
    if not client_package:
        raise ValueError("Client package not found")

    # Get appointments booked using this package
    appointments = Appointment.query.filter_by(
        client_id=client_package.client_id,
        package_id=client_package.package_id
    ).order_by(Appointment.appointment_date.desc()).all()

    # Calculate usage statistics
    total_sessions = client_package.package.total_sessions
    used_sessions = len([a for a in appointments if a.status == 'completed'])
    remaining_sessions = total_sessions - used_sessions

    # Check if expired
    from datetime import datetime
    is_expired = client_package.expiry_date < datetime.utcnow() if client_package.expiry_date else False

    return {
        'client_package': client_package,
        'total_sessions': total_sessions,
        'used_sessions': used_sessions,
        'remaining_sessions': remaining_sessions,
        'is_expired': is_expired,
        'appointments': appointments,
        'services_included': [ps.service for ps in client_package.package.services]
    }

def auto_expire_packages():
    """Auto-expire packages based on validity period"""
    from datetime import datetime

    expired_packages = ClientPackage.query.filter(
        ClientPackage.expiry_date < datetime.utcnow(),
        ClientPackage.is_active == True
    ).all()

    for client_package in expired_packages:
        client_package.is_active = False

    if expired_packages:
        db.session.commit()

    return len(expired_packages)

def export_packages_csv():
    """Export all packages to CSV"""
    packages = get_all_packages()

    import io
    import csv

    output = io.StringIO()
    writer = csv.writer(output)

    # CSV Headers
    writer.writerow([
        'ID', 'Package Name', 'Description', 'Total Sessions',
        'Validity (Days)', 'Price (₹)', 'Discount (%)', 'Services Included',
        'Status', 'Created Date'
    ])

    # Data rows
    for package in packages:
        services_list = ', '.join([ps.service.name for ps in package.services if ps.service])

        writer.writerow([
            package.id,
            package.name,
            package.description or '',
            package.total_sessions,
            package.validity_days,
            package.total_price,
            package.discount_percentage,
            services_list,
            'Active' if package.is_active else 'Inactive',
            package.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    output.seek(0)
    return output.getvalue()

def export_package_usage_csv():
    """Export package usage data to CSV"""
    from datetime import datetime
    client_packages = get_client_packages()

    import io
    import csv

    output = io.StringIO()
    writer = csv.writer(output)

    # CSV Headers
    writer.writerow([
        'Client Name', 'Package Name', 'Purchase Date', 'Expiry Date',
        'Total Sessions', 'Used Sessions', 'Remaining Sessions',
        'Status', 'Total Paid (₹)'
    ])

    # Data rows
    for cp in client_packages:
        if cp.client and cp.package:
            # Calculate used sessions (simplified - would need appointment tracking)
            used_sessions = cp.package.total_sessions - (cp.sessions_remaining or 0)

            status = 'Active'
            if not cp.is_active:
                status = 'Expired'
            elif cp.expiry_date and cp.expiry_date < datetime.utcnow():
                status = 'Expired'
            elif cp.sessions_remaining <= 0:
                status = 'Completed'

            writer.writerow([
                cp.client.full_name,
                cp.package.name,
                cp.purchase_date.strftime('%Y-%m-%d') if cp.purchase_date else '',
                cp.expiry_date.strftime('%Y-%m-%d') if cp.expiry_date else '',
                cp.package.total_sessions,
                used_sessions,
                cp.sessions_remaining or 0,
                status,
                cp.package.total_price
            ])

    output.seek(0)
    return output.getvalue()