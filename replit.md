# Spa Management System

## Overview
This is a comprehensive Flask-based spa management system that handles customer management, appointments, staff scheduling, inventory, billing, and packages. The system provides a complete solution for spa operations with an advanced database structure and modern web interface.

## Project Architecture
- **Backend**: Flask (Python) with SQLAlchemy ORM
- **Database**: SQLite for development (configured for PostgreSQL compatibility)
- **Frontend**: HTML templates with Bootstrap, jQuery, and JavaScript
- **Authentication**: Flask-Login with role-based access control
- **Deployment**: Configured for Replit with gunicorn for production

## Key Features
- Customer management with facial recognition support
- Staff management with shift scheduling
- Service and package management
- Inventory management with batch tracking
- Comprehensive billing and invoicing system
- Appointment booking and management
- Role-based permission system
- Reporting and analytics

## Current Configuration
- **Development Server**: Flask dev server on port 5000
- **Production Deployment**: Gunicorn with autoscale deployment target
- **Database**: SQLite with proper PRAGMA settings for concurrent access
- **Environment**: Configured for Replit environment with proxy support

## Recent Changes
- 2025-09-27: **Successfully imported from GitHub and configured for Replit environment**
  - ✅ Installed all Python dependencies from requirements.txt
  - ✅ Configured SQLite database with proper connection settings
  - ✅ Set up Flask application with Replit-compatible configuration (proxy headers, CORS, cache control)
  - ✅ Created Flask Frontend workflow running on port 5000 with webview output
  - ✅ Tested application - login page and navigation working perfectly
  - ✅ Configured deployment settings for production use with gunicorn and autoscale
  - ✅ All core modules loading successfully (auth, dashboard, clients, services, inventory, etc.)
  - ✅ Application running smoothly in Replit environment

## Project Structure
```
/
├── app.py                 # Main Flask application configuration
├── main.py               # Application entry point
├── models.py             # Database models
├── modules/              # Modular application components
│   ├── auth/            # Authentication module
│   ├── billing/         # Billing and invoicing
│   ├── staff/           # Staff management and scheduling
│   ├── inventory/       # Inventory management
│   ├── packages/        # Package management
│   └── ...              # Other modules
├── templates/           # HTML templates
├── static/             # CSS, JS, and assets
└── hanamantdatabase/   # SQLite database files
```

## User Preferences
- Production-ready design with professional UI
- Modular architecture for maintainability
- Comprehensive error handling and logging
- Security-focused with proper authentication

## Development Notes
- SQLite configured with WAL mode for better concurrency
- Flask app configured with proper proxy headers for Replit
- All routes registered through modular blueprint system
- Environment variables properly configured for security