# Spa Management System

## Overview
A comprehensive Flask-based spa and salon management system with advanced features for staff management, customer booking, inventory tracking, billing, and reporting.

## Recent Changes (September 26, 2025)
- **Project Import Setup**: Successfully configured for Replit environment
- **Route Conflicts Fixed**: Resolved multiple duplicate route definitions that were preventing proper application startup
- **Database Configuration**: Configured to use SQLite database with proper pragmas for development
- **Requirements Cleanup**: Removed duplicate entries from requirements.txt
- **Workflow Configuration**: Set up proper Flask development server with webview output on port 5000
- **Deployment Ready**: Configured for Replit autoscale deployment using gunicorn

## Project Architecture
- **Backend**: Flask with SQLAlchemy ORM
- **Database**: SQLite (development), PostgreSQL-ready for production
- **Frontend**: Jinja2 templates with Bootstrap CSS framework
- **Authentication**: Flask-Login with role-based access control
- **Modular Structure**: Organized into feature-specific modules (staff, customers, services, billing, etc.)

## Key Features
- Staff management and scheduling
- Customer booking system (including Unaki booking integration)
- Service and package management
- Inventory tracking with batch management
- Comprehensive billing and invoicing
- Role-based permission system
- Dashboard with analytics
- Report generation

## Technical Setup
- **Main Entry Point**: `main.py`
- **Application Configuration**: `app.py`
- **Database Models**: `models.py`
- **Routes**: Distributed across `routes.py` and module-specific view files
- **Templates**: Located in `templates/` directory with modular organization
- **Static Assets**: CSS, JavaScript, and images in `static/` directory

## Current Status
✅ **Working Features**:
- Application startup and module loading
- Database connectivity and table creation
- User authentication system
- Dashboard interface
- Static file serving
- All route conflicts resolved

🔧 **Configuration**:
- Flask development server running on port 5000
- Webview output configured for Replit Preview
- SQLite database with WAL mode for better concurrency
- Deployment configuration set for autoscale with gunicorn

## User Preferences
- Clean, production-ready code structure
- Comprehensive error handling and logging
- Modular architecture for maintainability
- Bootstrap-based responsive UI design

## Next Steps
- Test individual modules and features
- Verify role management functionality
- Complete user acceptance testing
- Production deployment optimization