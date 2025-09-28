# Spa Management System

A comprehensive Flask-based web application for managing spa and salon operations.

## Overview
A comprehensive Flask-based spa and salon management system with advanced features for staff management, customer booking, inventory tracking, billing, and reporting.
This project is a sophisticated spa management system built with Flask that handles:
- Customer management and profiles
- Staff scheduling and management
- Service bookings and appointments
- Inventory tracking
- Billing and payment processing
- Reporting and analytics
- Package and membership management

## Recent Changes (September 26, 2025)
- **Project Import Setup**: Successfully configured for Replit environment
- **Route Conflicts Fixed**: Resolved multiple duplicate route definitions that were preventing proper application startup
- **Database Configuration**: Configured to use SQLite database with proper pragmas for development
- **Requirements Cleanup**: Removed duplicate entries from requirements.txt
- **Workflow Configuration**: Set up proper Flask development server with webview output on port 5000
- **Deployment Ready**: Configured for Replit autoscale deployment using gunicorn
## Current State
- ✅ **Status**: Successfully configured and running on Replit
- ✅ **Database**: PostgreSQL database configured and ready
- ✅ **Frontend**: Flask web application with professional UI
- ✅ **Port**: Running on port 5000 with webview configuration
- ✅ **Deployment**: Configured for autoscale deployment with Gunicorn

## Recent Changes (September 27, 2025)
- Migrated from GitHub import to Replit environment
- Updated database configuration from SQLite to PostgreSQL
- Configured proper Flask development workflow
- Set up deployment configuration for production
- Verified all components are working correctly

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
### Backend
- **Framework**: Flask 3.1+
- **Database**: PostgreSQL via Replit's built-in service
- **ORM**: SQLAlchemy 2.0+
- **Authentication**: Flask-Login
- **Forms**: WTForms with Flask-WTF

## Technical Setup
- **Main Entry Point**: `main.py`
- **Application Configuration**: `app.py`
- **Database Models**: `models.py`
- **Routes**: Distributed across `routes.py` and module-specific view files
- **Templates**: Located in `templates/` directory with modular organization
- **Static Assets**: CSS, JavaScript, and images in `static/` directory
### Frontend
- **Templates**: Jinja2
- **CSS Framework**: Bootstrap
- **JavaScript**: Vanilla JS with modern modules
- **Icons**: Font Awesome

## Current Status
✅ **Working Features**:
- Application startup and module loading
- Database connectivity and table creation
- User authentication system
- Dashboard interface
- Static file serving
- All route conflicts resolved
### Key Modules
- Authentication and user management
- Dashboard with analytics
- Staff management and scheduling
- Customer/client management
- Service management
- Appointment booking
- Inventory management
- Billing and payments
- Reporting system

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
## Development Workflow
1. The main workflow "Spa Management System" runs the Flask development server
2. Application is accessible via webview on port 5000
3. PostgreSQL database handles all data persistence
4. Hot reloading enabled for development

## Deployment
- **Target**: Autoscale deployment
- **Server**: Gunicorn WSGI server
- **Configuration**: Ready for production deployment on Replit

## Next Steps
- Test individual modules and features
- Verify role management functionality
- Complete user acceptance testing
- Production deployment optimization
## User Preferences
- Follow existing Flask project structure and conventions
- Maintain professional UI/UX design
- Use PostgreSQL for data persistence
- Prioritize security and proper authentication