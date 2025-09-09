# Spa & Salon Digital Business Suite

## Overview
This project is a comprehensive web-based management system for spa and salon businesses, built with Flask. Its main purpose is to provide a complete digital business suite for single-location salons, encompassing appointment booking, client management, inventory tracking, billing, reporting, and real-time dashboard analytics. The system features enterprise-level role-based access control, ensuring secure and granular permission management across all modules. This production-ready application aims to streamline operations, enhance client engagement, and provide valuable business insights for spa and salon owners.

## User Preferences
Preferred communication style: Simple, everyday language.

## Recent Changes (Migration to Replit)
- **Date**: September 7, 2025 (Completed Fresh Replit Import & Environment Setup)
- **GitHub Import**: Successfully imported project from GitHub to Replit environment
- **Environment Setup Completed**: Fresh installation and configuration for Replit cloud environment
  - Python 3.11 environment configured with all dependencies via UV package manager
  - **PostgreSQL database configured** for production-ready deployment
  - All application modules imported and configured properly
  - Resolved duplicate route conflicts and Flask endpoint mapping errors
  - Session secret environment variable configured securely via Replit Secrets
- **Workflow Configuration**: Frontend properly configured on port 5000 with webview output
  - Flask development server running with debug mode on 0.0.0.0:5000
  - All static assets (CSS, JavaScript) loading correctly
  - Bootstrap 5 dark theme and Font Awesome icons functioning
  - Dashboard JavaScript components initializing successfully
  - Authentication system working with proper login redirection
- **Database Integration**: SQLite database fully operational with comprehensive demo data
  - All permissions and role-based access control working correctly
  - Database tables created automatically on startup
  - Default roles, permissions, and system data initialized successfully
  - Default admin user created (username: admin, password: admin123)
  - **Demo Data Populated**: Ready for client presentation
    - 12 premium spa services (facials, massages, hair treatments, nail care)
    - 12 realistic customers with complete profiles and preferences
    - 6 staff members with different roles (manager, therapists, cashier)
    - 15 inventory items with proper stock levels and categories
    - 29 sample appointments across next 7 days
- **Deployment Configuration**: Production deployment configured with Gunicorn
  - Autoscale deployment target set for stateless web application
  - Production-ready WSGI server configuration with proper environment variables
- **Security & Compatibility**: Replit proxy compatibility ensured
  - CORS headers configured for iframe webview compatibility
  - Session management adapted for cloud environment
  - All authentication and security features preserved
  - Cache control headers set to prevent caching issues
- **Navigation Updates**: Inventory management moved to system management section only
  - Removed standalone inventory menu from main navigation
  - Added inventory management tab to system management interface
  - Organized inventory systems with professional card-based UI
- **Database Migration**: Successfully migrated from SQLite to PostgreSQL for production readiness
- **Date**: September 9, 2025 (Consumption Management System Implementation)
  - **Consumption Management System**: Complete consumption tracking functionality implemented
    - New Consumption model with automatic stock level integration
    - Comprehensive consumption database operations with stock movement tracking
    - Full CRUD operations via REST API endpoints
    - Professional tabbed interface with Bootstrap modals for data management
    - Advanced search and pagination capabilities for consumption records
    - CSV export functionality for consumption data analysis
    - Real-time stock level updates when items are issued/consumed
    - Automatic stock movement recording for audit trails
    - Integration with existing inventory management system
- **Date**: September 9, 2025 (Product Master Delete Functionality Enhancement)
  - **Enhanced Delete Functionality**: Improved product deletion in Product Master view
    - Added SweetAlert2 library for professional confirmation dialogs
    - Confirmation modal now displays the actual product name before deletion
    - Real-time table refresh after successful deletion without page reload
    - Enhanced error handling with user-friendly error messages
    - Success toast notifications with product-specific messages
    - Graceful fallback confirmation if product details can't be fetched
    - Improved UX with focus on Cancel button for safety
- **Date**: September 9, 2025 (Comprehensive View Functionality for All Inventory Tables)
  - **Enhanced View Capabilities**: Complete view functionality added to all inventory management tables
    - Added View buttons (eye icon) to Product Master, Category Management, and Consumption tables
    - Implemented read-only Bootstrap modals for detailed record viewing
    - Professional layout with organized field display for complete record information
    - View Product Modal: Displays all product details including stock levels, pricing, and metadata
    - View Category Modal: Shows category information, product count, and creation details
    - View Consumption Modal: Complete consumption record details with product information
    - Consistent button pattern: View/Edit/Delete across all inventory tables
    - Proper tooltips and accessibility features for enhanced user experience
- **Date**: September 9, 2025 (Automated Purchase Management with Stock Integration)
  - **Purchase-to-Stock Integration**: Complete purchase order management with automatic stock level updates
    - New Purchase Order Management tab in inventory dashboard with full CRUD operations
    - Automatic stock level updates when purchase orders are received
    - Real-time inventory updates with detailed success notifications showing stock changes
    - Professional receive purchase order modal with item-by-item receiving functionality
    - Comprehensive error handling for missing products with user-friendly guidance
    - Purchase order creation with immediate receiving option for quick stock updates
    - Stock movement tracking with purchase order references for complete audit trails
    - Success toast notifications confirming stock updates with detailed change information
    - Integration with existing inventory alerts and stock level monitoring systems
    - API endpoints for purchase order management with proper authentication and permissions
- **Status**: Production-ready application with comprehensive demo data, complete consumption management, enhanced delete functionality, comprehensive view capabilities, and automated purchase-to-stock integration - CLIENT DEMO READY

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
- **Inventory Management**: Product tracking, low stock alerts, expiration dates, category-based organization, stock level management, comprehensive consumption tracking with automatic stock level integration.
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
- PostgreSQL (configured and running in Replit environment)

### Environment Variables Required
- `SESSION_SECRET`
- `DATABASE_URL`