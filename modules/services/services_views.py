"""
Enhanced Service and Category Management Views
Implements comprehensive CRUD operations as per requirements document
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from app import app, db
from models import Service
from forms import ServiceForm
try:
    from .services_queries import (
        get_all_services, get_service_by_id, create_service, update_service, delete_service,
        export_services_csv
    )
    print("Services queries imported successfully")
except ImportError as e:
    print(f"Error importing services queries: {e}")
    # Fallback imports or create placeholder functions
    def get_all_services(category_filter=None):
        from models import Service
        query = Service.query
        if category_filter:
            query = query.filter_by(category_id=category_filter)
        return query.all()
    
    
    
    def get_service_by_id(service_id):
        from models import Service
        return Service.query.get(service_id)
    
    def create_service(data):
        from models import Service
        service = Service(**data)
        db.session.add(service)
        db.session.commit()
        return service
    
    def update_service(service_id, data):
        service = get_service_by_id(service_id)
        for key, value in data.items():
            setattr(service, key, value)
        db.session.commit()
        return service
    
    def delete_service(service_id):
        service = get_service_by_id(service_id)
        if service:
            db.session.delete(service)
            db.session.commit()
            return {'success': True, 'message': 'Service deleted successfully'}
        return {'success': False, 'message': 'Service not found'}



# Enhanced Service Management Routes
@app.route('/services')
@login_required
def services():
    """Enhanced Service Management with filtering and CRUD"""
    print(f"Services route accessed by user: {current_user.username if current_user.is_authenticated else 'Anonymous'}")
    
    try:
        # Remove access check temporarily to debug the issue
        # if not current_user.can_access('services'):
        #     flash('Access denied', 'danger')
        #     return redirect(url_for('dashboard'))
        
        # Get category filter from query parameters
        category_filter = request.args.get('category', '').strip()
        print(f"Category filter from request: '{category_filter}'")
        
        # Pass None if empty string to show all services
        filter_value = category_filter if category_filter else None
        services_list = get_all_services(filter_value)
        print(f"Retrieved {len(services_list)} services from database")
        
        # Get categories for the dropdown
        from models import Category
        categories = Category.query.filter_by(category_type='service', is_active=True).all()
        print(f"Retrieved {len(categories)} categories")
        
        form = ServiceForm()
        
        print(f"Services loaded: {len(services_list)} services")
        
        return render_template('services.html', 
                             services=services_list,
                             categories=categories,
                             category_filter=category_filter,
                             form=form)
    except Exception as e:
        print(f"Error in services route: {str(e)}")
        flash(f'Error loading services: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/services/create', methods=['POST'])
@login_required
def create_service_route():
    """Create new service"""
    if not current_user.has_permission('services_create'):
        flash('You do not have permission to create services', 'danger')
        return redirect(url_for('services'))
    
    try:
        # Defensive coding - safe extraction with validation
        name = (request.form.get('name') or '').strip()
        description = (request.form.get('description') or '').strip()
        
        # Safe numeric conversions with validation
        try:
            duration = int(request.form.get('duration', 60))
            if duration <= 0:
                duration = 60  # Default to 60 minutes
        except (ValueError, TypeError):
            duration = 60
            
        try:
            price = float(request.form.get('price', 0))
            if price < 0:
                price = 0.0
        except (ValueError, TypeError):
            price = 0.0
        
        category_id = request.form.get('category_id')
        is_active = bool(request.form.get('is_active', False))
        
        # Enhanced validation with user-friendly messages
        if not name:
            flash('Service name is required. Please enter a descriptive service name.', 'danger')
            return redirect(url_for('services'))
            
        if len(name) > 200:
            flash('Service name must be less than 200 characters.', 'danger')
            return redirect(url_for('services'))
        
        if price <= 0:
            flash('Service price must be greater than 0. Please enter a valid price.', 'danger')
            return redirect(url_for('services'))
            
        if duration < 15:
            flash('Service duration must be at least 15 minutes.', 'danger')
            return redirect(url_for('services'))
        
        # Create service
        try:
            service = create_service({
                'name': name,
                'description': description,
                'duration': duration,
                'price': price,
                'category_id': int(category_id) if category_id else None,
                'is_active': is_active
            })
            flash(f'Service "{service.name}" created successfully', 'success')
        except Exception as create_error:
            flash(f'Failed to create service: {str(create_error)}', 'danger')
            print(f"Service creation error: {create_error}")
            return redirect(url_for('services'))
        
    except Exception as e:
        flash(f'Error creating service: {str(e)}', 'danger')
    
    return redirect(url_for('services'))

@app.route('/services/<int:service_id>/edit', methods=['POST'])
@login_required
def edit_service(service_id):
    """Edit service"""
    if not current_user.has_permission('services_edit'):
        return jsonify({'success': False, 'message': 'You do not have permission to edit services'})
    
    service = get_service_by_id(service_id)
    if not service:
        return jsonify({'success': False, 'message': 'Service not found'})
    
    try:
        # Validate required fields
        name = request.form.get('name', '').strip()
        if not name:
            return jsonify({'success': False, 'message': 'Service name is required'})
        
        try:
            duration = int(request.form.get('duration', 60))
            price = float(request.form.get('price', 0))
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Invalid numeric values provided'})
        
        if price <= 0:
            return jsonify({'success': False, 'message': 'Price must be greater than 0'})
        
        if duration < 15:
            return jsonify({'success': False, 'message': 'Duration must be at least 15 minutes'})
        
        # Get form data
        data = {
            'name': name,
            'description': request.form.get('description', '').strip(),
            'duration': duration,
            'price': price,
            'category_id': int(request.form.get('category_id')) if request.form.get('category_id') else None,
            'is_active': request.form.get('is_active') == 'on'
        }
        
        update_service(service_id, data)
        return jsonify({'success': True, 'message': 'Service updated successfully'})
        
    except Exception as e:
        print(f"Error updating service {service_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Error updating service: {str(e)}'})

@app.route('/services/<int:service_id>/delete', methods=['POST'])
@login_required
def delete_service_route(service_id):
    """Delete service"""
    if not current_user.has_permission('services_delete'):
        return jsonify({'success': False, 'message': 'You do not have permission to delete services'})
    
    try:
        print(f"Attempting to delete service ID: {service_id}")
        result = delete_service(service_id)
        print(f"Delete result: {result}")
        return jsonify(result)
        
    except Exception as e:
        error_msg = f'Error deleting service: {str(e)}'
        print(f"Delete error: {error_msg}")
        return jsonify({'success': False, 'message': error_msg})

@app.route('/services/<int:service_id>/toggle', methods=['POST'])
@login_required
def toggle_service(service_id):
    """Toggle service active status"""
    if not current_user.can_access('services'):
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        service = get_service_by_id(service_id)
        if not service:
            return jsonify({'success': False, 'message': 'Service not found'})
        
        new_status = not service.is_active
        print(f"Toggling service {service_id} from {service.is_active} to {new_status}")
        
        update_service(service_id, {'is_active': new_status})
        status = 'activated' if new_status else 'deactivated'
        
        return jsonify({
            'success': True, 
            'message': f'Service {status} successfully',
            'is_active': new_status
        })
    except Exception as e:
        print(f"Error toggling service {service_id}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/services/export')
@login_required
def export_services():
    """Export services to CSV"""
    if not current_user.can_access('services'):
        flash('Access denied', 'danger')
        return redirect(url_for('services'))
    
    try:
        category_filter = request.args.get('category', '')
        csv_data = export_services_csv(category_filter)
        
        filename = 'services.csv'
        if category_filter:
            filename = f'services_{category_filter}.csv'
            
        response = make_response(csv_data)
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        response.headers['Content-Type'] = 'text/csv'
        return response
    except Exception as e:
        flash(f'Error exporting services: {str(e)}', 'danger')
        return redirect(url_for('services'))

# Test route for debugging
@app.route('/test-services')
@login_required
def test_services():
    """Test route to check if services module is working"""
    try:
        from models import Service
        services = Service.query.all()
        active_services = Service.query.filter_by(is_active=True).all()
        
        return jsonify({
            'status': 'success',
            'message': 'Services module is working',
            'user': current_user.username if current_user.is_authenticated else 'anonymous',
            'total_services': len(services),
            'active_services': len(active_services),
            'services': [{'id': s.id, 'name': s.name, 'price': s.price, 'active': s.is_active} for s in services]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'user': current_user.username if current_user.is_authenticated else 'anonymous'
        })

@app.route('/create-sample-services')
@login_required
def create_sample_services():
    """Create sample services for testing"""
    try:
        from models import Service
        from app import db
        
        # Check if services already exist
        existing_services = Service.query.count()
        if existing_services > 0:
            return jsonify({
                'status': 'info',
                'message': f'{existing_services} services already exist',
                'services': existing_services
            })
        
        # Create sample services
        sample_services = [
            {'name': 'Basic Haircut', 'description': 'Standard haircut and styling', 'duration': 30, 'price': 25.00, 'category': 'hair'},
            {'name': 'Hair Wash & Blow Dry', 'description': 'Professional hair washing and blow drying', 'duration': 45, 'price': 35.00, 'category': 'hair'},
            {'name': 'Classic Manicure', 'description': 'Traditional manicure with nail polish', 'duration': 60, 'price': 40.00, 'category': 'nails'},
            {'name': 'Relaxing Facial', 'description': 'Deep cleansing and moisturizing facial', 'duration': 90, 'price': 80.00, 'category': 'skincare'},
            {'name': 'Swedish Massage', 'description': '60-minute full body Swedish massage', 'duration': 60, 'price': 75.00, 'category': 'massage'},
            {'name': 'Deep Tissue Massage', 'description': 'Therapeutic deep tissue massage', 'duration': 90, 'price': 95.00, 'category': 'massage'},
            {'name': 'Express Facial', 'description': 'Quick 30-minute facial treatment', 'duration': 30, 'price': 45.00, 'category': 'skincare'},
            {'name': 'Premium Pedicure', 'description': 'Luxurious pedicure with spa treatment', 'duration': 75, 'price': 65.00, 'category': 'nails'}
        ]
        
        created_services = []
        for service_data in sample_services:
            service = Service(
                name=service_data['name'],
                description=service_data['description'],
                duration=service_data['duration'],
                price=service_data['price'],
                category=service_data['category'],
                is_active=True
            )
            db.session.add(service)
            created_services.append(service_data['name'])
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Created {len(created_services)} sample services',
            'services': created_services
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Error creating sample services: {str(e)}'
        })

# Service Category Management Routes
@app.route('/service-categories/create', methods=['POST'])
@login_required
def create_service_category():
    """Create new service category"""
    try:
        from models import Category
        from datetime import datetime
        
        # Get form data with proper validation
        name = request.form.get('name', '').strip()
        display_name = request.form.get('display_name', '').strip()
        
        if not name or not display_name:
            flash('Category name and display name are required', 'danger')
            return redirect(url_for('services'))
        
        # Convert name to lowercase with underscores
        internal_name = name.lower().replace(' ', '_')
        
        # Check if category already exists
        existing = Category.query.filter_by(name=internal_name, category_type='service').first()
        if existing:
            flash(f'Category "{internal_name}" already exists', 'warning')
            return redirect(url_for('services'))
        
        category = Category(
            name=internal_name,
            display_name=display_name,
            description=request.form.get('description', ''),
            category_type='service',
            color=request.form.get('color', '#007bff'),
            sort_order=int(request.form.get('sort_order', 0)),
            is_active=True if request.form.get('is_active') == 'on' else False,
            created_at=datetime.utcnow()
        )
        
        db.session.add(category)
        db.session.commit()
        
        print(f"✅ Category created: {category.name} (ID: {category.id}, Active: {category.is_active})")
        flash(f'Category "{display_name}" created successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating category: {str(e)}")
        flash(f'Error creating category: {str(e)}', 'danger')
    
    return redirect(url_for('services'))

@app.route('/service-categories/<int:category_id>/edit', methods=['POST'])
@login_required
def edit_service_category(category_id):
    """Edit service category"""
    try:
        from models import Category
        
        category = Category.query.get_or_404(category_id)
        category.display_name = request.form.get('display_name')
        category.description = request.form.get('description')
        category.color = request.form.get('color')
        category.sort_order = int(request.form.get('sort_order', 0))
        category.is_active = bool(request.form.get('is_active'))
        
        db.session.commit()
        flash('Category updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating category: {str(e)}', 'danger')
    
    return redirect(url_for('services'))

@app.route('/service-categories/<int:category_id>/toggle', methods=['POST'])
@login_required
def toggle_service_category(category_id):
    """Toggle service category status"""
    try:
        from models import Category
        
        category = Category.query.get_or_404(category_id)
        category.is_active = not category.is_active
        db.session.commit()
        
        status = 'activated' if category.is_active else 'deactivated'
        return jsonify({'success': True, 'message': f'Category {status} successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/service-categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_service_category(category_id):
    """Delete service category"""
    try:
        from models import Category
        
        category = Category.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Category deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/categories/<int:category_id>')
@login_required
def api_get_service_category(category_id):
    """Get service category data for AJAX calls"""
    try:
        from models import Category
        
        category = Category.query.get_or_404(category_id)
        return jsonify({
            'id': category.id,
            'display_name': category.display_name,
            'description': category.description,
            'color': category.color,
            'sort_order': category.sort_order,
            'is_active': category.is_active
        })
    except Exception as e:
        return jsonify({'error': str(e)})

# API Endpoints for AJAX operations
@app.route('/api/services/category/<int:category_id>')
@login_required
def get_services_by_category(category_id):
    """Get services by category for AJAX calls"""
    try:
        from models import Service
        services = Service.query.filter_by(category_id=category_id, is_active=True).all()
        return jsonify({
            'services': [
                {
                    'id': s.id,
                    'name': s.name,
                    'price': float(s.price),
                    'duration': s.duration
                } for s in services
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/services/<int:service_id>')
@login_required
def get_service_api(service_id):
    """Get service data for AJAX calls"""
    if not current_user.can_access('services'):
        return jsonify({'error': 'Access denied'})
    
    try:
        service = get_service_by_id(service_id)
        if not service:
            return jsonify({'error': 'Service not found'})
            
        return jsonify({
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'duration': service.duration,
            'price': service.price,
            'category_id': service.category_id,
            'is_active': service.is_active
        })
    except Exception as e:
        return jsonify({'error': str(e)})

