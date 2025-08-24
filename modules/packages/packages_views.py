"""
Enhanced Packages views and routes with session tracking and validity management
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from app import app, db
from forms import PackageForm
from models import Package, PackageService, ClientPackage, Service
from .packages_queries import (
    get_all_packages, get_package_by_id, create_package, update_package,
    delete_package, get_client_packages, assign_package_to_client,
    get_package_services, add_service_to_package, get_available_services,
    track_package_usage, auto_expire_packages, export_packages_csv,
    export_package_usage_csv
)
from models import Service, Category

# Packages route is now defined in routes.py as packages_enhanced

# create_package_route is now defined in routes.py as enhanced version

# edit_package route is now defined in routes.py as edit_package_route
# delete_package_route is now defined in routes.py
# assign_package_route is now defined in routes.py
# All package routes are now defined in routes.py for enhanced package management