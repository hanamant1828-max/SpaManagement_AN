"""
NEW Package Management System - Redirects to new separate package types
"""
from flask import redirect, url_for
from flask_login import login_required
from app import app

# Import all new package management endpoints
from .new_packages_views import *

# Legacy routes that redirect to new system
@app.route('/packages/old')
@login_required  
def packages_old():
    """Redirect old package route to new system"""
    return redirect(url_for('packages'))

# All the new package management functionality is in new_packages_views.py
# This file exists only for compatibility and to prevent import errors