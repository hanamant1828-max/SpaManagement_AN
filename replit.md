# Spa Management System

A comprehensive Flask-based web application for managing spa and salon operations.

## Overview
This project is a sophisticated spa management system built with Flask that handles:
- Customer management and profiles
- Staff scheduling and management
- Service bookings and appointments
- Inventory tracking
- Billing and payment processing
- Reporting and analytics
- Package and membership management

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

### Backend
- **Framework**: Flask 3.1+
- **Database**: PostgreSQL via Replit's built-in service
- **ORM**: SQLAlchemy 2.0+
- **Authentication**: Flask-Login
- **Forms**: WTForms with Flask-WTF

### Frontend
- **Templates**: Jinja2
- **CSS Framework**: Bootstrap
- **JavaScript**: Vanilla JS with modern modules
- **Icons**: Font Awesome

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

## Development Workflow
1. The main workflow "Spa Management System" runs the Flask development server
2. Application is accessible via webview on port 5000
3. PostgreSQL database handles all data persistence
4. Hot reloading enabled for development

## Deployment
- **Target**: Autoscale deployment
- **Server**: Gunicorn WSGI server
- **Configuration**: Ready for production deployment on Replit

## User Preferences
- Follow existing Flask project structure and conventions
- Maintain professional UI/UX design
- Use PostgreSQL for data persistence
- Prioritize security and proper authentication