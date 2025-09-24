# Spa Management System

## Overview
This is a comprehensive spa management system built with Flask that provides complete business management functionality for spa and wellness centers. The system includes modules for staff management, customer management, booking systems, inventory control, billing, and reporting.

## Recent Changes
- **2025-09-24**: Successfully set up project in Replit environment
- **2025-09-24**: Installed all Python dependencies via pip package manager
- **2025-09-24**: Configured SQLite database for development (workspace.db)
- **2025-09-24**: Set up Flask development server on port 5000 with webview output
- **2025-09-24**: Configured deployment settings for production using Gunicorn
- **2025-09-24**: All modules successfully loading and application running
- **2025-09-24**: Verified frontend accessibility through Replit proxy

## Project Architecture

### Technology Stack
- **Backend**: Flask 3.0.3, SQLAlchemy 2.0.41, Flask-Login, Flask-WTF
- **Database**: PostgreSQL (production), SQLite (development fallback)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Deployment**: Gunicorn WSGI server

### Key Components

#### Core Application (`app.py`)
- Flask application factory with environment detection
- Database configuration (PostgreSQL for production, SQLite for development)
- Security headers and CORS configuration for Replit environment
- Login manager and user authentication setup

#### Database Models (`models.py`)
- Comprehensive data models for all business entities
- Dynamic role and permission system
- User management with staff-specific fields
- Service, booking, and billing models
- Inventory management models

#### Routing (`routes.py`)
- Main application routes and default data creation
- System management endpoints
- API endpoints for role and permission management

### Module Structure
The application is organized into feature-based modules:

- **auth/**: User authentication and authorization
- **dashboard/**: Main dashboard and overview
- **staff/**: Staff management and scheduling
- **clients/**: Customer management
- **services/**: Service catalog management
- **bookings/**: Appointment and booking system
- **inventory/**: Stock and inventory control
- **billing/**: Invoicing and payment processing
- **packages/**: Service packages and memberships
- **reports/**: Business analytics and reporting
- **expenses/**: Expense tracking
- **settings/**: System configuration

### Configuration
- **Development**: Debug mode enabled, SQLite database, relaxed security
- **Production**: Security headers, PostgreSQL database, CSRF protection
- **Environment Variables**: SESSION_SECRET, DATABASE_URL automatically configured

### Default Credentials
- **Username**: admin
- **Password**: admin123
- **Email**: admin@spa.com

## Running the Application

### Development
The application runs automatically via the configured workflow:
- **Command**: `python main.py`
- **Port**: 5000
- **Host**: 0.0.0.0 (required for Replit environment)

### Production Deployment
Configured for autoscale deployment:
- **Server**: Gunicorn WSGI
- **Command**: `gunicorn --bind 0.0.0.0:5000 --reuse-port main:app`

## Database Setup
- PostgreSQL database automatically created in Replit environment
- All required tables created on first run
- Default admin user and sample data populated automatically

## Features
- Multi-role user management system
- Complete booking and appointment system
- Inventory management with batch tracking
- Integrated billing and invoicing
- Staff scheduling and time management
- Customer package and membership management
- Comprehensive reporting system
- Mobile-responsive design

## Notes
- Application successfully tested and running
- All static files (CSS, JS) properly served
- Bootstrap UI framework fully functional
- Database connections and queries working correctly
- Authentication system operational