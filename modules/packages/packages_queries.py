"""
Packages related database queries
"""
from datetime import datetime, date
from sqlalchemy import func, and_
from app import db
from models import Package, ClientPackage, PackageService, Service

def get_all_packages():
    """Get all active packages"""
    return Package.query.filter_by(is_active=True).order_by(Package.name).all()

def get_package_by_id(package_id):
    """Get package by ID"""
    return Package.query.get(package_id)

def create_package(package_data):
    """Create a new package"""
    package = Package(**package_data)
    db.session.add(package)
    db.session.commit()
    return package

def update_package(package_id, package_data):
    """Update an existing package"""
    package = Package.query.get(package_id)
    if package:
        for key, value in package_data.items():
            setattr(package, key, value)
        db.session.commit()
    return package

def delete_package(package_id):
    """Soft delete a package"""
    package = Package.query.get(package_id)
    if package:
        package.is_active = False
        db.session.commit()
        return True
    return False

def get_client_packages(client_id):
    """Get client's active packages"""
    return ClientPackage.query.filter_by(client_id=client_id, is_active=True).all()

def assign_package_to_client(client_id, package_id):
    """Assign a package to a client"""
    client_package = ClientPackage(
        client_id=client_id,
        package_id=package_id,
        purchase_date=datetime.utcnow(),
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