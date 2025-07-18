"""
Enhanced Service and Category Management Views
Implements comprehensive CRUD operations as per requirements document
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from app import app, db
from models import Service, Category
from forms import ServiceForm, CategoryForm
from .services_queries import (
    get_all_services, get_service_by_id, create_service, update_service, delete_service,
    get_all_service_categories, get_category_by_id, create_category, update_category, 
    delete_category, reorder_category, export_services_csv, export_categories_csv
)

# Service Category Management Routes
@app.route('/service-categories')
@login_required
def service_categories():
    """Service Category Management with CRUD operations"""
    if not current_user.can_access('services'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    categories = get_all_service_categories()
    form = CategoryForm()
    
    return render_template('service_categories.html', 
                         categories=categories, 
                         form=form)

@app.route('/service-categories/create', methods=['POST'])
@login_required
def create_service_category():
    """Create new service category"""
    if not current_user.can_access('services'):
        flash('Access denied', 'danger')
        return redirect(url_for('services'))
    
    try:
        # Get form data directly from request
        name = request.form.get('name', '').strip()
        display_name = request.form.get('display_name', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', '#007bff')
        sort_order = int(request.form.get('sort_order', 0))
        is_active = 'is_active' in request.form
        
        # Basic validation
        if not name or not display_name:
            flash('Category name and display name are required', 'danger')
            return redirect(url_for('services'))
        
        # Create category
        category = create_category({
            'name': name.lower().replace(' ', '_'),
            'display_name': display_name,
            'description': description,
            'category_type': 'service',
            'color': color,
            'is_active': is_active,
            'sort_order': sort_order
        })
        flash(f'Service category "{category.display_name}" created successfully', 'success')
        
    except Exception as e:
        flash(f'Error creating category: {str(e)}', 'danger')
    
    return redirect(url_for('services'))

@app.route('/service-categories/<int:category_id>/edit', methods=['POST'])
@login_required
def edit_service_category(category_id):
    """Edit service category"""
    if not current_user.can_access('services'):
        flash('Access denied', 'danger')
        return redirect(url_for('service_categories'))
    
    category = get_category_by_id(category_id)
    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('service_categories'))
    
    form = CategoryForm()
    if form.validate_on_submit():
        try:
            update_category(category_id, {
                'display_name': form.display_name.data,
                'description': form.description.data,
                'color': form.color.data,
                'is_active': form.is_active.data,
                'sort_order': form.sort_order.data or 0
            })
            flash(f'Category "{category.display_name}" updated successfully', 'success')
        except Exception as e:
            flash(f'Error updating category: {str(e)}', 'danger')
    
    return redirect(url_for('service_categories'))

@app.route('/service-categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_service_category(category_id):
    """Delete service category (only if no services under it)"""
    if not current_user.can_access('services'):
        flash('Access denied', 'danger')
        return redirect(url_for('service_categories'))
    
    try:
        result = delete_category(category_id)
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'warning')
    except Exception as e:
        flash(f'Error deleting category: {str(e)}', 'danger')
    
    return redirect(url_for('service_categories'))

@app.route('/service-categories/<int:category_id>/toggle', methods=['POST'])
@login_required
def toggle_service_category(category_id):
    """Toggle category active status"""
    if not current_user.can_access('services'):
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        category = get_category_by_id(category_id)
        if not category:
            return jsonify({'success': False, 'message': 'Category not found'})
        
        update_category(category_id, {'is_active': not category.is_active})
        status = 'activated' if not category.is_active else 'deactivated'
        
        return jsonify({
            'success': True, 
            'message': f'Category {status} successfully',
            'is_active': not category.is_active
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/service-categories/reorder', methods=['POST'])
@login_required
def reorder_service_categories():
    """Reorder categories via drag/drop"""
    if not current_user.can_access('services'):
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        category_ids = request.json.get('category_ids', [])
        reorder_category(category_ids)
        return jsonify({'success': True, 'message': 'Categories reordered successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/service-categories/export')
@login_required
def export_service_categories():
    """Export categories to CSV"""
    if not current_user.can_access('services'):
        flash('Access denied', 'danger')
        return redirect(url_for('service_categories'))
    
    try:
        csv_data = export_categories_csv()
        response = make_response(csv_data)
        response.headers['Content-Disposition'] = 'attachment; filename=service_categories.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response
    except Exception as e:
        flash(f'Error exporting categories: {str(e)}', 'danger')
        return redirect(url_for('service_categories'))

# Enhanced Service Management Routes
@app.route('/services')
@login_required
def services():
    """Enhanced Service Management with filtering and CRUD"""
    if not current_user.can_access('services'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    category_filter = request.args.get('category', '')
    services_list = get_all_services(category_filter)
    categories = get_all_service_categories()
    
    form = ServiceForm()
    
    return render_template('services.html', 
                         services=services_list,
                         categories=categories,
                         form=form,
                         category_filter=category_filter)

@app.route('/services/create', methods=['POST'])
@login_required
def create_service_route():
    """Create new service"""
    if not current_user.can_access('services'):
        flash('Access denied', 'danger')
        return redirect(url_for('services'))
    
    try:
        # Get form data directly from request
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        duration = int(request.form.get('duration', 60))
        price = float(request.form.get('price', 0))
        category_id = request.form.get('category_id')
        commission_rate = float(request.form.get('commission_rate', 10))
        is_active = 'is_active' in request.form
        
        # Basic validation
        if not name:
            flash('Service name is required', 'danger')
            return redirect(url_for('services'))
        
        if price <= 0:
            flash('Price must be greater than 0', 'danger')
            return redirect(url_for('services'))
        
        # Create service
        service = create_service({
            'name': name,
            'description': description,
            'duration': duration,
            'price': price,
            'category_id': int(category_id) if category_id else None,
            'commission_rate': commission_rate,
            'is_active': is_active
        })
        flash(f'Service "{service.name}" created successfully', 'success')
        
    except Exception as e:
        flash(f'Error creating service: {str(e)}', 'danger')
    
    return redirect(url_for('services'))

@app.route('/services/<int:service_id>/edit', methods=['POST'])
@login_required
def edit_service(service_id):
    """Edit service"""
    if not current_user.can_access('services'):
        flash('Access denied', 'danger')
        return redirect(url_for('services'))
    
    service = get_service_by_id(service_id)
    if not service:
        flash('Service not found', 'danger')
        return redirect(url_for('services'))
    
    form = ServiceForm()
    if form.validate_on_submit():
        try:
            update_service(service_id, {
                'name': form.name.data,
                'description': form.description.data,
                'duration': form.duration.data,
                'price': form.price.data,
                'category_id': form.category_id.data,
                'is_active': form.is_active.data
            })
            flash(f'Service "{service.name}" updated successfully', 'success')
        except Exception as e:
            flash(f'Error updating service: {str(e)}', 'danger')
    
    return redirect(url_for('services'))

@app.route('/services/<int:service_id>/delete', methods=['POST'])
@login_required
def delete_service_route(service_id):
    """Delete service"""
    if not current_user.can_access('services'):
        flash('Access denied', 'danger')
        return redirect(url_for('services'))
    
    try:
        result = delete_service(service_id)
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'warning')
    except Exception as e:
        flash(f'Error deleting service: {str(e)}', 'danger')
    
    return redirect(url_for('services'))

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
        
        update_service(service_id, {'is_active': not service.is_active})
        status = 'activated' if not service.is_active else 'deactivated'
        
        return jsonify({
            'success': True, 
            'message': f'Service {status} successfully',
            'is_active': not service.is_active
        })
    except Exception as e:
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

# API Endpoints for AJAX operations
@app.route('/api/services/category/<int:category_id>')
@login_required
def get_services_by_category(category_id):
    """Get services by category for AJAX calls"""
    if not current_user.can_access('services'):
        return jsonify({'error': 'Access denied'})
    
    try:
        services = Service.query.filter_by(category_id=category_id, is_active=True).all()
        return jsonify({
            'services': [
                {
                    'id': s.id,
                    'name': s.name,
                    'price': s.price,
                    'duration': s.duration
                } for s in services
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)})