"""
Packages related database queries
"""
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app import db
from models import Package, ClientPackage, Service

def get_all_packages():
    """Get all active packages"""
    return Package.query.filter_by(is_active=True).order_by(Package.name).all()

def get_package_by_id(package_id):
    """Get package by ID"""
    return Package.query.get(package_id)

def create_package(package_data):
    """Create new package"""
    package = Package(
        name=package_data['name'],
        description=package_data.get('description'),
        duration_months=package_data['duration_months'],
        total_price=package_data['total_price'],
        discount_percentage=package_data.get('discount_percentage', 0.0),
        is_active=package_data.get('is_active', True)
    )

    db.session.add(package)
    db.session.commit()
    return package

def update_package(package_id, package_data):
    """Update package"""
    package = Package.query.get(package_id)
    if not package:
        raise ValueError("Package not found")

    for key, value in package_data.items():
        if hasattr(package, key):
            setattr(package, key, value)

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

    db.session.delete(package)
    db.session.commit()
    return {'success': True, 'message': f'Package "{package.name}" deleted successfully'}

def get_client_packages(client_id=None):
    """Get client's active packages"""
    if client_id:
        return ClientPackage.query.filter_by(client_id=client_id, is_active=True).all()
    else:
        return ClientPackage.query.filter_by(is_active=True).all()

def assign_package_to_client(client_id, package_id):
    """Assign a package to a client"""
    package = Package.query.get(package_id)
    if not package:
        raise ValueError("Package not found")

    # Calculate expiry date
    expiry_date = datetime.utcnow() + timedelta(days=package.duration_months * 30)

    client_package = ClientPackage(
        client_id=client_id,
        package_id=package_id,
        purchase_date=datetime.utcnow(),
        expiry_date=expiry_date,
        amount_paid=package.total_price,
        is_active=True
    )

    db.session.add(client_package)
    db.session.commit()
    return client_package