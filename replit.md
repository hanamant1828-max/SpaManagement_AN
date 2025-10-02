# Spa Management System

## Overview
A comprehensive Flask-based spa management system featuring appointment booking, client management, billing, inventory tracking, staff scheduling, and reporting. This is an imported GitHub project now configured to run in the Replit environment.

## Recent Changes
- **2025-10-02**: Added edit functionality for booked appointments in Unaki booking view
- **2025-10-01**: Successfully configured GitHub import to run in Replit environment
- **2025-10-01**: Set up Flask Server workflow on port 5000 with webview output
- **2025-10-01**: Configured deployment settings using Gunicorn for production
- **2025-10-01**: Cleaned up .gitignore to remove duplicates and add proper Python exclusions
- **2024-09-28**: Imported from GitHub and configured for Replit environment
- **2024-09-28**: Configured to use SQLite database for local storage
- **2024-09-28**: Updated Flask configuration for Replit proxy compatibility

## User Preferences
- Using Flask with SQLite backend for local development
- Modular architecture with separate modules for different features
- Development environment setup with debug logging enabled

## Project Architecture

### Main Application Structure
- `app.py` - Main Flask application configuration and initialization
- `main.py` - Application entry point with error handling
- `models.py` - Database models and schemas
- `routes.py` - Application routes (legacy)
- `forms.py` - WTForms form definitions
- `utils.py` - Utility functions

### Module Structure
The application uses a modular architecture in the `modules/` directory:

- **auth/** - Authentication and user management
- **billing/** - Billing and invoice management
- **bookings/** - Appointment booking system
- **checkin/** - Client check-in functionality
- **clients/** - Customer/client management
- **dashboard/** - Main dashboard views
- **expenses/** - Expense tracking
- **inventory/** - Inventory management with stock control
- **notifications/** - Notification system
- **packages/** - Package and membership management
- **reports/** - Reporting and analytics
- **services/** - Service catalog management
- **settings/** - System settings and configuration
- **staff/** - Staff management and scheduling

### Templates
- `templates/` - Jinja2 templates for all views
- `templates/base.html` - Base template with navigation
- Organized by module for maintainability

### Database Configuration
- **Database**: SQLite with local file storage in `hanamantdatabase/` directory
- **Features**: WAL mode, foreign key constraints, thread-safe configuration
- **Models**: SQLAlchemy with declarative base
- **Location**: Automatically creates database files based on instance identifier

### Key Features
1. **Appointment Booking**: Comprehensive booking system with conflict detection
2. **Billing System**: Integrated billing with invoice generation
3. **Inventory Management**: Stock tracking with batch management
4. **Staff Scheduling**: Shift management and availability tracking
5. **Client Management**: Customer profiles and history
6. **Package Management**: Membership and prepaid packages
7. **Reporting**: Analytics and business intelligence
8. **Multi-user Support**: Role-based access control

### Environment Variables Required
- `SESSION_SECRET` - Flask session security key
- `PORT` - Server port (defaults to 5000)
- `SPA_DB_INSTANCE` - Optional database instance identifier (uses REPL_SLUG or 'default')

### Development Setup
- Debug mode enabled for development
- CSRF protection disabled for development
- Cache control configured for Replit environment
- ProxyFix middleware for proper HTTPS handling

### External Dependencies
- Flask ecosystem (Flask-SQLAlchemy, Flask-Login, Flask-WTF)
- PostgreSQL (psycopg2-binary)
- Gunicorn for production deployment
- Various utilities (pandas, openpyxl, requests, etc.)

## Architecture Decisions
- **Date**: 2024-09-28 - Using SQLite for local development and easy deployment in Replit environment
- **Date**: 2024-09-28 - Maintained existing modular architecture to preserve functionality
- **Date**: 2024-09-28 - Configured for Replit's proxy system with appropriate headers and CORS

## Setup Status
✅ **COMPLETED** - Application is fully configured and running in Replit environment
- All module imports successful
- Database tables created successfully
- Web interface functioning properly
- Workflow configured for development (Flask Server on port 5000)
- Deployment settings configured for production (Gunicorn with autoscale)
- Application accessible via webview

## Running the Application
- **Development**: The Flask Server workflow runs automatically
- **Port**: 5000 (configured for Replit webview)
- **Database**: SQLite database stored in `hanamantdatabase/workspace.db`
- **Login**: Use existing credentials from the imported database

## Deployment
- **Target**: Autoscale deployment (stateless web application)
- **Server**: Gunicorn with 2 workers, 4 threads per worker
- **Port**: 5000
- **Configuration**: Optimized for Replit's deployment environment