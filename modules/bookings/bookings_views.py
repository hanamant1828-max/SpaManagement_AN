"""
Bookings Module - Main Entry Point

This file serves as the main entry point for the bookings module.
The module has been refactored into a modular structure for better maintainability:

**Module Structure:**
1. booking_helpers.py - Helper functions and utilities
2. booking_services.py - Business logic and validation
3. booking_api.py - All API endpoints (/api/* routes)
4. booking_routes.py - View routes (template rendering)
5. bookings_queries.py - Database queries

All routes are registered automatically when these modules are imported.
"""

# Import all modular components to register their routes
# The routes are registered via @app.route decorators in each module
from . import booking_helpers
from . import booking_services
from . import booking_api
from . import booking_routes

# Note: bookings_queries is imported by other modules as needed

# This file now serves as a clean entry point that imports all booking functionality
# All routes, helpers, services, and queries are organized in their respective modules
