"""
NEW Package Management Queries - Redirects to new separate package types
"""

# Import all new package query functions
from .new_packages_queries import *

# This file exists only for compatibility and to prevent import errors
# All the new package management functionality is in new_packages_queries.py

# Legacy function stubs for compatibility (now redirected to new system)
def get_all_packages():
    """Legacy function - use new separate package type functions instead"""
    return []

def get_package_by_id(package_id):
    """Legacy function - use new separate package type functions instead"""
    return None