# Spa & Salon Digital Business Suite

## Overview

This is a comprehensive web-based management system for spa and salon businesses, built with Flask and featuring role-based access control, appointment booking, client management, inventory tracking, billing, and reporting capabilities. The application is designed for single-location salons and provides a complete digital business suite with real-time dashboard analytics.

**Current Status**: Production-ready with all 13 modules implemented and vertical sidebar navigation.

## Recent Changes

### July 10, 2025
- ✅ **Completed all 13 modules** as specified in requirements
- ✅ **Converted to vertical sidebar navigation** - Professional left sidebar with all menu items
- ✅ **Fixed template imports** - Added missing timedelta and date imports for bookings template
- ✅ **Enhanced user experience** with active navigation highlighting and mobile responsiveness
- ✅ **All modules functional** and ready for deployment

### Module Implementation Status
All 13 required modules now implemented:
1. ✅ Dashboard - Business Overview
2. ✅ Smart Booking & Calendar 
3. ✅ Staff Management
4. ✅ Client History & Loyalty
5. ✅ Face Recognition Check-In
6. ✅ WhatsApp Notification System
7. ✅ Billing & Payment System
8. ✅ Subscription Packages
9. ✅ Inventory & Product Tracking
10. ✅ Reports & Insights
11. ✅ User & Access Control Panel
12. ✅ Daily Expense Tracker
13. ✅ Expiring Product Alerts

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: HTML5 with Bootstrap 5 (dark theme)
- **Styling**: CSS3 with custom variables for spa/salon branding
- **JavaScript**: Vanilla ES6+ with modular components for calendar, dashboard, and main functionality
- **Icons**: Font Awesome 6.4.0 for consistent iconography
- **Charts**: Chart.js for data visualization and analytics

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database ORM**: SQLAlchemy with declarative base model
- **Authentication**: Flask-Login for session management
- **Forms**: WTForms with Flask-WTF for secure form handling
- **Security**: Werkzeug for password hashing and proxy handling

### Database Design
- **ORM**: SQLAlchemy with declarative base
- **Models**: User (staff), Client, Service, Appointment, Inventory, Expense, Invoice, Package, StaffSchedule
- **Features**: Automatic table creation, connection pooling, and pre-ping health checks

## Key Components

### Authentication System
- Role-based access control (admin, manager, staff, cashier)
- User session management with Flask-Login
- Password hashing with Werkzeug security
- Resource-level permissions based on user roles

### Dashboard Module
- Real-time business metrics and KPIs
- Today's appointments and revenue tracking
- Visual charts for revenue trends and appointment status
- Role-specific widgets and data views

### Booking & Calendar System
- Unified appointment calendar with date filtering
- Color-coded appointments by staff or service
- Drag-and-drop rescheduling capabilities (frontend)
- Walk-in and online booking support

### Client Management
- Complete client profiles with history tracking
- Search functionality across name, phone, and email
- Preferences, allergies, and visit notes storage
- Client loyalty and visit frequency tracking

### Staff Management
- Staff profiles with role assignments
- Commission rate and hourly rate configuration
- Schedule management and availability tracking
- Performance metrics linked to bookings

### Inventory Management
- Product tracking with low stock alerts
- Expiration date monitoring
- Category-based organization
- Stock level management and reorder points

### Billing & Payment System
- Invoice generation and payment tracking
- Pending payment management
- Revenue reporting and analytics
- Payment status tracking

### Expense Tracking
- Business expense categorization and tracking
- Monthly expense summaries
- Receipt management and documentation
- Cost analysis and reporting

### Reports & Analytics
- Customizable date range reporting
- Revenue and performance analytics
- Export functionality for data analysis
- Visual charts and trend analysis

## Data Flow

### User Authentication Flow
1. User submits login credentials
2. System validates against User model
3. Flask-Login creates user session
4. Role-based permissions applied
5. User redirected to appropriate dashboard

### Appointment Management Flow
1. Appointment creation/modification request
2. Validation against staff availability and service duration
3. Database update with relationship mapping
4. Calendar view refresh
5. Notification triggers (if implemented)

### Billing Process Flow
1. Service completion triggers billing creation
2. Invoice generation with service and pricing details
3. Payment processing and status tracking
4. Revenue reporting and analytics update
5. Client history and loyalty tracking update

## External Dependencies

### Frontend Libraries
- Bootstrap 5.x (via CDN) - UI framework with dark theme
- Font Awesome 6.4.0 (via CDN) - Icon library
- Chart.js (via CDN) - Data visualization

### Backend Dependencies
- Flask - Web framework
- Flask-SQLAlchemy - Database ORM
- Flask-Login - Authentication management
- Flask-WTF - Form handling and CSRF protection
- WTForms - Form validation and rendering
- Werkzeug - WSGI utilities and security

### Environment Variables Required
- `SESSION_SECRET` - Flask session encryption key
- `DATABASE_URL` - Database connection string

## Deployment Strategy

### Development Setup
- Flask development server with debug mode enabled
- Hot reload for code changes
- SQLite database for local development (configurable via DATABASE_URL)
- Port 5000 with host binding to 0.0.0.0 for container compatibility

### Production Considerations
- Database connection pooling with 300-second recycle
- ProxyFix middleware for reverse proxy deployment
- Environment-based configuration management
- Automatic database table creation on startup

### Database Strategy
- SQLAlchemy handles database abstraction
- Automatic table creation via `db.create_all()`
- Support for various database backends via DATABASE_URL
- Connection pooling and health checks configured

### Security Features
- CSRF protection via Flask-WTF
- Password hashing with Werkzeug
- Session management with secure secret key
- Role-based access control throughout application
- Input validation and sanitization via WTForms

The application follows a modular architecture pattern with clear separation of concerns between models, views, forms, and utilities, making it maintainable and extensible for future spa/salon business requirements.