"""
Enhanced Service and Category Management Queries
Database operations for comprehensive service/category CRUD
"""
from app import db
from models import Service, Category
from sqlalchemy import and_, or_
from datetime import datetime
import csv
from io import StringIO

# Service Queries
def get_all_services(category_filter=''):
    """Get all services with optional category filtering"""
    try:
        query = Service.query.filter_by(is_active=True)
        
        if category_filter:
            if category_filter.isdigit():
                query = query.filter_by(category_id=int(category_filter))
            else:
                # Support legacy category filtering
                category = Category.query.filter_by(name=category_filter).first()
                if category:
                    query = query.filter_by(category_id=category.id)
        
        services = query.order_by(Service.name).all()
        print(f"Retrieved {len(services)} services from database")
        return services
    except Exception as e:
        print(f"Error retrieving services: {e}")
        return []

def get_service_by_id(service_id):
    """Get service by ID"""
    try:
        return Service.query.get(service_id)
    except Exception as e:
        print(f"Error retrieving service {service_id}: {e}")
        return None

def create_service(data):
    """Create new service"""
    from models import Service, Category
    try:
        # Create service instance
        service = Service()
        service.name = data['name']
        service.description = data.get('description', '')
        service.duration = data['duration']
        service.price = data['price']
        service.category_id = data.get('category_id')
        service.is_active = data.get('is_active', True)
        service.created_at = datetime.utcnow()
        
        # Handle legacy category field for backward compatibility
        if data.get('category_id'):
            try:
                category = Category.query.get(data['category_id'])
                if category:
                    service.category = category.name
                else:
                    service.category = 'general'  # fallback category
            except:
                service.category = 'general'  # fallback category
        else:
            service.category = 'general'  # fallback category
        
        # Add commission rate if it exists in the model
        if hasattr(service, 'commission_rate'):
            service.commission_rate = data.get('commission_rate', 10.0)
        
        print(f"Creating service: {service.name}, price: {service.price}, duration: {service.duration}")
        
        db.session.add(service)
        db.session.commit()
        
        print(f"Service created successfully with ID: {service.id}")
        return service
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating service: {str(e)}")
        raise e

def update_service(service_id, data):
    """Update existing service"""
    try:
        service = Service.query.get(service_id)
        if not service:
            raise ValueError("Service not found")
        
        for key, value in data.items():
            if hasattr(service, key):
                setattr(service, key, value)
        
        # Handle legacy category field
        if 'category_id' in data and data['category_id']:
            category = Category.query.get(data['category_id'])
            if category:
                service.category = category.name
        
        db.session.commit()
        return service
    except Exception as e:
        db.session.rollback()
        raise e

def delete_service(service_id):
    """Delete service with safety checks"""
    try:
        service = Service.query.get(service_id)
        if not service:
            return {'success': False, 'message': 'Service not found'}
        
        # Check if service is used in appointments or packages
        from models import Appointment, PackageService
        
        appointments_count = Appointment.query.filter_by(service_id=service_id).count()
        packages_count = PackageService.query.filter_by(service_id=service_id).count()
        
        if appointments_count > 0 or packages_count > 0:
            # Soft delete - mark as inactive
            service.is_active = False
            db.session.commit()
            return {'success': True, 'message': 'Service deactivated (has associated records)'}
        else:
            # Hard delete if no associations
            db.session.delete(service)
            db.session.commit()
            return {'success': True, 'message': 'Service deleted successfully'}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}

# Service Category Queries
def get_all_service_categories():
    """Get all service categories"""
    try:
        categories = Category.query.filter_by(
            category_type='service',
            is_active=True
        ).order_by(Category.sort_order, Category.display_name).all()
        
        print(f"Retrieved {len(categories)} service categories from database")
        return categories
    except Exception as e:
        print(f"Error retrieving service categories: {e}")
        return []

def get_category_by_id(category_id):
    """Get category by ID"""
    try:
        return Category.query.get(category_id)
    except Exception as e:
        print(f"Error retrieving category {category_id}: {e}")
        return None

def create_category(data):
    """Create new service category"""
    try:
        category = Category(
            name=data['name'],
            display_name=data['display_name'],
            description=data.get('description', ''),
            category_type='service',
            color=data.get('color', '#007bff'),
            icon=data.get('icon', 'fas fa-spa'),
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 0),
            created_at=datetime.utcnow()
        )
        
        db.session.add(category)
        db.session.commit()
        return category
    except Exception as e:
        db.session.rollback()
        raise e

def update_category(category_id, data):
    """Update existing category"""
    try:
        category = Category.query.get(category_id)
        if not category:
            raise ValueError("Category not found")
        
        for key, value in data.items():
            if hasattr(category, key):
                setattr(category, key, value)
        
        db.session.commit()
        return category
    except Exception as e:
        db.session.rollback()
        raise e

def delete_category(category_id):
    """Delete category if no services are associated"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return {'success': False, 'message': 'Category not found'}
        
        # Check if category has associated services
        service_count = Service.query.filter_by(category_id=category_id).count()
        if service_count > 0:
            return {'success': False, 'message': f'Cannot delete category with {service_count} associated services'}
        
        db.session.delete(category)
        db.session.commit()
        return {'success': True, 'message': 'Category deleted successfully'}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}

def reorder_category(category_ids):
    """Reorder categories based on provided list"""
    try:
        for index, category_id in enumerate(category_ids):
            category = Category.query.get(category_id)
            if category:
                category.sort_order = index
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e

# Export Functions
def export_services_csv(category_filter=''):
    """Export services to CSV format"""
    try:
        services = get_all_services(category_filter)
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'ID', 'Name', 'Description', 'Duration (min)', 
            'Price', 'Category', 'Commission Rate', 'Status', 'Created Date'
        ])
        
        # Data rows
        for service in services:
            category_name = ''
            if hasattr(service, 'service_category') and service.service_category:
                category_name = service.service_category.display_name
            elif hasattr(service, 'category') and service.category:
                category_name = service.category.replace('_', ' ').title()
            
            writer.writerow([
                service.id,
                service.name,
                service.description or '',
                service.duration,
                service.price,
                category_name,
                getattr(service, 'commission_rate', 10),
                'Active' if service.is_active else 'Inactive',
                service.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(service, 'created_at') and service.created_at else ''
            ])
        
        return output.getvalue()
    except Exception as e:
        raise e

def export_categories_csv():
    """Export categories to CSV format"""
    try:
        categories = get_all_service_categories()
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'ID', 'Name', 'Display Name', 'Description', 
            'Color', 'Sort Order', 'Status', 'Created Date'
        ])
        
        # Data rows
        for category in categories:
            writer.writerow([
                category.id,
                category.name,
                category.display_name,
                category.description or '',
                category.color,
                category.sort_order,
                'Active' if category.is_active else 'Inactive',
                category.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(category, 'created_at') and category.created_at else ''
            ])
        
        return output.getvalue()
    except Exception as e:
        raise e

# Additional Helper Functions
def search_services(search_term, category_filter=None):
    """Search services by name or description"""
    try:
        query = Service.query.filter_by(is_active=True)
        
        if category_filter:
            query = query.filter_by(category_id=category_filter)
        
        if search_term:
            search_filter = or_(
                Service.name.ilike(f'%{search_term}%'),
                Service.description.ilike(f'%{search_term}%')
            )
            query = query.filter(search_filter)
        
        return query.order_by(Service.name).all()
    except Exception as e:
        print(f"Error searching services: {e}")
        return []

def get_services_by_category(category_id):
    """Get services by category ID"""
    return Service.query.filter_by(category_id=category_id, is_active=True).order_by(Service.name).all()

def get_services_by_price_range(min_price=None, max_price=None, category_filter=None):
    """Get services within price range"""
    try:
        query = Service.query.filter_by(is_active=True)
        
        if category_filter:
            query = query.filter_by(category_id=category_filter)
        
        if min_price is not None:
            query = query.filter(Service.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Service.price <= max_price)
        
        return query.order_by(Service.price).all()
    except Exception as e:
        print(f"Error filtering services by price: {e}")
        return []