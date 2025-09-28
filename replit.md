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
- **Database Location**: `hanamantdatabase/workspace.db`

## Recent Changes
- 2025-09-28: **Successfully configured for Replit environment with SQLite database**
  - ✅ Installed all Python dependencies from requirements.txt
  - ✅ Configured SQLite database with optimized settings (WAL mode, foreign keys enabled)
  - ✅ Updated Flask application configuration for SQLite compatibility
  - ✅ Set up Flask Frontend workflow running on port 5000 with webview output
  - ✅ Created admin user with credentials (admin/admin123)
  - ✅ Configured deployment settings for production use with gunicorn and autoscale
  - ✅ All core modules loading successfully (auth, dashboard, clients, services, inventory, etc.)
  - ✅ Application running smoothly in Replit environment with SQLite backend
  - ✅ Import and setup process completed - application is ready for use and deployment

- 2025-09-28: **Successfully fixed billing calculation system**
  - ✅ Enhanced `updateTaxCalculations()` function with comprehensive debugging
  - ✅ Improved `addUnakiAppointmentToBill()` function for better service addition
  - ✅ Added proper price data validation and DOM update handling
  - ✅ Implemented enhanced billing calculation logging and error detection
  - ✅ Fixed service selection logic to ensure proper billing totals
  - ✅ Verified system loads 30 customers and 24 services correctly
  - ✅ Billing system now properly calculates and displays totals when services are added
  - ✅ All billing calculation functions working correctly with enhanced debugging

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