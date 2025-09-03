
"""
Service Category Management Views
CRUD operations for service categories
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import Category

def get_all_service_categories():
    """Get all service categories ordered by sort_order"""
    return Category.query.filter_by(category_type='service').order_by(
        Category.sort_order, Category.display_name
    ).all()

def get_service_category_by_id(category_id):
    """Get service category by ID"""
    return Category.query.filter_by(id=category_id, category_type='service').first()

def create_service_category(data):
    """Create new service category"""
    category = Category(
        name=data['name'],
        display_name=data['display_name'],
        description=data.get('description'),
        category_type='service',
        color=data.get('color', '#007bff'),
        icon=data.get('icon', 'fas fa-spa'),
        is_active=data.get('is_active', True),
        sort_order=data.get('sort_order', 0)
    )
    
    db.session.add(category)
    db.session.commit()
    return category

def update_service_category(category_id, data):
    """Update service category"""
    category = get_service_category_by_id(category_id)
    if not category:
        raise ValueError("Category not found")
    
    for key, value in data.items():
        if hasattr(category, key):
            setattr(category, key, value)
    
    db.session.commit()
    return category

# Helper functions only - routes are defined in services_views.py to avoid conflicts
