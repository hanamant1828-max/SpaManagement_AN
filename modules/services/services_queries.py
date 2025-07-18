"""
Enhanced Service and Category Management Queries
Database operations for comprehensive service/category CRUD
"""
from app import db
from models import Service, Category
from datetime import datetime
import csv
import io

# Service Category Queries
def get_all_service_categories():
    """Get all service categories ordered by sort_order"""
    return Category.query.filter_by(category_type='service').order_by(
        Category.sort_order, Category.display_name
    ).all()

def get_category_by_id(category_id):
    """Get category by ID"""
    return Category.query.get(category_id)

def create_category(data):
    """Create new service category"""
    category = Category(
        name=data['name'],
        display_name=data['display_name'],
        description=data.get('description'),
        category_type='service',
        color=data.get('color', '#007bff'),
        is_active=data.get('is_active', True),
        sort_order=data.get('sort_order', 0)
    )
    
    db.session.add(category)
    db.session.commit()
    return category

def update_category(category_id, data):
    """Update service category"""
    category = Category.query.get(category_id)
    if not category:
        raise ValueError("Category not found")
    
    for key, value in data.items():
        if hasattr(category, key):
            setattr(category, key, value)
    
    db.session.commit()
    return category

def delete_category(category_id):
    """Delete category only if no services under it"""
    category = Category.query.get(category_id)
    if not category:
        return {'success': False, 'message': 'Category not found'}
    
    # Check if any services use this category
    services_count = Service.query.filter_by(category_id=category_id).count()
    if services_count > 0:
        return {
            'success': False, 
            'message': f'Cannot delete category. {services_count} service(s) are using this category.'
        }
    
    db.session.delete(category)
    db.session.commit()
    return {'success': True, 'message': f'Category "{category.display_name}" deleted successfully'}

def reorder_category(category_ids):
    """Reorder categories based on provided ID list"""
    for index, category_id in enumerate(category_ids):
        category = Category.query.get(category_id)
        if category:
            category.sort_order = index
    
    db.session.commit()

def export_categories_csv():
    """Export service categories to CSV"""
    categories = get_all_service_categories()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # CSV Headers
    writer.writerow([
        'ID', 'Category Name', 'Display Name', 'Description', 
        'Status', 'Sort Order', 'Color', 'Created Date'
    ])
    
    # Data rows
    for category in categories:
        writer.writerow([
            category.id,
            category.name,
            category.display_name,
            category.description or '',
            'Active' if category.is_active else 'Inactive',
            category.sort_order,
            category.color,
            category.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    output.seek(0)
    return output.getvalue()

# Enhanced Service Queries
def get_all_services(category_filter=''):
    """Get all services with optional category filtering"""
    query = Service.query
    
    if category_filter:
        if category_filter.isdigit():
            query = query.filter_by(category_id=int(category_filter))
        else:
            # Support legacy category filtering
            query = query.filter_by(category=category_filter)
    
    return query.order_by(Service.name).all()

def get_service_by_id(service_id):
    """Get service by ID"""
    return Service.query.get(service_id)

def create_service(data):
    """Create new service"""
    # Get category for fallback compatibility
    category = Category.query.get(data['category_id']) if data.get('category_id') else None
    
    service = Service(
        name=data['name'],
        description=data.get('description'),
        duration=data['duration'],
        price=data['price'],
        category_id=data.get('category_id'),
        category=category.name if category else 'other',  # Fallback
        is_active=data.get('is_active', True)
    )
    
    db.session.add(service)
    db.session.commit()
    return service

def update_service(service_id, data):
    """Update service"""
    service = Service.query.get(service_id)
    if not service:
        raise ValueError("Service not found")
    
    # Update category fallback if category_id is provided
    if 'category_id' in data and data['category_id']:
        category = Category.query.get(data['category_id'])
        if category:
            data['category'] = category.name
    
    for key, value in data.items():
        if hasattr(service, key):
            setattr(service, key, value)
    
    db.session.commit()
    return service

def delete_service(service_id):
    """Delete service"""
    service = Service.query.get(service_id)
    if not service:
        return {'success': False, 'message': 'Service not found'}
    
    # Check if service is used in appointments or packages
    from models import Appointment, PackageService
    
    appointments_count = Appointment.query.filter_by(service_id=service_id).count()
    packages_count = PackageService.query.filter_by(service_id=service_id).count()
    
    if appointments_count > 0 or packages_count > 0:
        return {
            'success': False, 
            'message': f'Cannot delete service. It is used in {appointments_count} appointment(s) and {packages_count} package(s).'
        }
    
    db.session.delete(service)
    db.session.commit()
    return {'success': True, 'message': f'Service "{service.name}" deleted successfully'}

def export_services_csv(category_filter=''):
    """Export services to CSV with optional category filtering"""
    services = get_all_services(category_filter)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # CSV Headers
    writer.writerow([
        'ID', 'Service Name', 'Category', 'Duration (Minutes)', 
        'Price (₹)', 'Description', 'Status', 'Created Date'
    ])
    
    # Data rows
    for service in services:
        category_name = ''
        if service.service_category:
            category_name = service.service_category.display_name
        elif service.category:
            category_name = service.category.replace('_', ' ').title()
        
        writer.writerow([
            service.id,
            service.name,
            category_name,
            service.duration,
            service.price,
            service.description or '',
            'Active' if service.is_active else 'Inactive',
            service.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    output.seek(0)
    return output.getvalue()

def get_services_by_category(category_id):
    """Get services by category ID"""
    return Service.query.filter_by(category_id=category_id, is_active=True).order_by(Service.name).all()