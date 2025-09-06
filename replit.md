# Spa & Salon Digital Business Suite

## Overview
This project is a comprehensive web-based management system for spa and salon businesses, built with Flask. Its main purpose is to provide a complete digital business suite for single-location salons, encompassing appointment booking, client management, inventory tracking, billing, reporting, and real-time dashboard analytics. The system features enterprise-level role-based access control, ensuring secure and granular permission management across all modules. This production-ready application aims to streamline operations, enhance client engagement, and provide valuable business insights for spa and salon owners.

## User Preferences
Preferred communication style: Simple, everyday language.

## Recent Changes (Migration to Replit)
- **Date**: September 6, 2025 (Completed Replit Import)
- **GitHub Import**: Successfully imported project from GitHub to Replit environment
- **Environment Setup Completed**: Fresh installation and configuration for Replit cloud environment
  - Python 3.11 environment configured with all dependencies via UV package manager
  - PostgreSQL database connected and initialized successfully  
  - All application modules imported and configured properly
  - Resolved duplicate route conflicts and Flask endpoint mapping errors
  - Session secret environment variable configured securely
- **Workflow Configuration**: Frontend properly configured on port 5000 with webview output
  - Flask development server running with debug mode on 0.0.0.0:5000
  - All static assets (CSS, JavaScript) loading correctly
  - Bootstrap 5 dark theme and Font Awesome icons functioning
  - Dashboard JavaScript components initializing successfully
  - Authentication system working with proper login redirection
- **Database Integration**: PostgreSQL database fully operational
  - All permissions and role-based access control working correctly
  - Database tables created automatically on startup
  - Default roles, permissions, and system data initialized successfully
  - Default admin user created (username: admin, password: admin123)
- **Deployment Configuration**: Production deployment configured with Gunicorn
  - Autoscale deployment target set for stateless web application
  - Production-ready WSGI server configuration with proper environment variables
- **Security & Compatibility**: Replit proxy compatibility ensured
  - CORS headers configured for iframe webview compatibility
  - Session management adapted for cloud environment
  - All authentication and security features preserved
  - Cache control headers set to prevent caching issues
- **Status**: Production-ready application successfully migrated and fully functional on Replit

## System Architecture

### Frontend Architecture
- **Framework**: HTML5 with Bootstrap 5 (dark theme)
- **Styling**: CSS3 with custom variables for spa/salon branding
- **JavaScript**: Vanilla ES6+ with modular components for calendar, dashboard, and main functionality
- **Icons**: Font Awesome 6.4.0
- **Charts**: Chart.js for data visualization

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database ORM**: SQLAlchemy with declarative base model
- **Authentication**: Flask-Login for session management
- **Forms**: WTForms with Flask-WTF for secure form handling
- **Security**: Werkzeug for password hashing and proxy handling

### Modular Architecture
The system is designed with a modular approach, separating concerns into distinct business modules. Each module follows a consistent pattern with dedicated files for route handlers (`_views.py`) and database queries/business logic (`_queries.py`). This structure promotes maintainability, independent development, and scalability.

### Database Design
- **ORM**: SQLAlchemy
- **Core Models**: User (staff), Client, Service, Appointment, Inventory, Expense, Invoice, Package, StaffSchedule.
- **Advanced Models**: Location, Commission, ProductSale, Promotion, Communication, Waitlist, RecurringAppointment, Review, BusinessSettings.
- **Dynamic System Models**: Role, Permission, RolePermission, Category, Department, SystemSetting.
- **Features**: Automatic table creation, connection pooling, pre-ping health checks, comprehensive relationships, dynamic CRUD operations.

### Key Features
- **Authentication System**: Role-based access control (132 granular permissions), user session management, password hashing, resource-level permissions.
- **Dashboard**: Real-time business metrics, KPIs, appointment tracking, revenue trends, role-specific widgets.
- **Booking & Calendar**: Unified calendar, color-coded appointments, drag-and-drop rescheduling (frontend), walk-in/online booking, timetable view with staff columns and time slots.
- **Client Management**: Comprehensive profiles, history, search, preferences, allergies, loyalty tracking, communication tracking (email, SMS, WhatsApp, calls).
- **Staff Management**: Profiles, role assignments, commission/hourly rates, schedule, availability, performance metrics.
- **Inventory Management**: Product tracking, low stock alerts, expiration dates, category-based organization, stock level management.
- **Billing & Payment**: Invoice generation, payment tracking, pending payment management, revenue reporting.
- **Expense Tracking**: Categorization, monthly summaries, receipt management, cost analysis.
- **Reports & Analytics**: Customizable date range reporting, revenue/performance analytics, export functionality, visual charts.
- **Subscription Packages**: Comprehensive package system with multi-service selection, individual discounts, validity periods, session tracking, client assignment, CSV export.
- **Real-World Business Operations**: Includes marketing promotions, client waitlist, POS integration for product sales, recurring appointment setup, customer review system, and configurable business settings.
- **Dynamic Configuration System**: Manage roles, permissions, categories, departments, and system settings dynamically through the application.

## External Dependencies

### Frontend Libraries
- Bootstrap 5.x (via CDN)
- Font Awesome 6.4.0 (via CDN)
- Chart.js (via CDN)

### Backend Dependencies
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- WTForms
- Werkzeug

### Database
- PostgreSQL (for production environment)

### Environment Variables Required
- `SESSION_SECRET`
- `DATABASE_URL`