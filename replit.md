# Spa & Salon Management Suite

## Overview
A comprehensive Flask-based spa and salon management system with features for appointment booking, client management, staff scheduling, billing, inventory management, and more.

## Project Status
**Current State:** Fully functional and running in Replit environment
**Last Updated:** October 3, 2025

## Key Features
- **Dashboard:** Real-time overview of business metrics
- **Client Management:** Detailed customer profiles with history and loyalty tracking
- **Staff Management:** Comprehensive CRUD operations with roles, departments, and schedules
- **Shift Scheduler:** Dynamic shift scheduling with day-by-day configuration
- **Appointment Booking:** Flexible booking system with multiple booking sources (Unaki, etc.)
- **Integrated Billing:** Professional invoicing with GST/SGST/IGST calculations
- **Services Management:** Service catalog with categories, pricing, and durations
- **Package Management:** Prepaid packages, memberships, student offers, and kitty party packages
- **Inventory Management:** Batch-centric stock tracking with location management
- **Check-In System:** Staff attendance and facial recognition support
- **Reports:** Revenue, expenses, staff performance, and inventory reports
- **WhatsApp Notifications:** Automated customer communications
- **User Roles & Permissions:** Granular access control system

## Architecture

### Technology Stack
- **Backend:** Flask 3.1.1 with SQLAlchemy 2.0.41
- **Database:** SQLite (development) with PostgreSQL support
- **Authentication:** Flask-Login with role-based access control
- **Frontend:** Bootstrap 5 with custom CSS and vanilla JavaScript
- **Deployment:** Gunicorn with autoscale configuration

### Project Structure
```
/
├── app.py                  # Main Flask application configuration
├── main.py                 # Application entry point
├── models.py               # SQLAlchemy database models
├── forms.py                # WTForms form definitions
├── routes.py               # Legacy route definitions
├── utils.py                # Utility functions
├── requirements.txt        # Python dependencies
├── modules/                # Modular application components
│   ├── auth/              # Authentication and authorization
│   ├── dashboard/         # Dashboard views and queries
│   ├── clients/           # Customer management
│   ├── staff/             # Staff management and shift scheduling
│   ├── services/          # Service catalog management
│   ├── bookings/          # Appointment booking system
│   ├── billing/           # Integrated billing and invoicing
│   ├── inventory/         # Inventory management
│   ├── packages/          # Package management (memberships, offers)
│   ├── expenses/          # Expense tracking
│   ├── reports/           # Business reporting
│   ├── settings/          # System and business settings
│   ├── checkin/           # Staff check-in system
│   └── notifications/     # Communication system
├── templates/             # Jinja2 HTML templates
├── static/                # CSS, JavaScript, and assets
├── hanamantdatabase/      # SQLite database directory (gitignored)
├── instance/              # Flask instance folder
└── demo_data/             # Demo data generation scripts
```

### Database Configuration
- **Development:** SQLite database stored in `hanamantdatabase/` directory
- **Production:** Supports PostgreSQL via `DATABASE_URL` environment variable
- **Schema:** Comprehensive relational database with 50+ tables
- **Key Tables:** User, Customer, Service, Appointment, Invoice, Inventory, Package, ShiftManagement

## Replit Environment Setup

### Environment Variables
- `SESSION_SECRET`: Required for Flask session management (configured)
- `DATABASE_URL`: Optional PostgreSQL connection string (defaults to SQLite)
- `PORT`: Server port (defaults to 5000)

### Workflow Configuration
- **Name:** Spa Management App
- **Command:** `python main.py`
- **Port:** 5000
- **Output Type:** webview
- **Purpose:** Runs the Flask development server with hot reload

### Deployment Configuration
- **Type:** autoscale (stateless web application)
- **Command:** `gunicorn --bind 0.0.0.0:5000 --reuse-port main:app`
- **Port:** 5000

## Development Notes

### Flask Configuration
- The app is configured to listen on `0.0.0.0:5000` for Replit proxy compatibility
- CORS headers are enabled for Replit Preview functionality
- Cache control headers are set to disable caching for development
- Session cookies are configured with `SameSite=Lax` for development

### Database Management
- Database is automatically initialized on first run
- Demo data can be loaded using scripts in `demo_data/` directory
- Multiple seed scripts available for testing different scenarios

### Default Login Credentials
```
Admin User:
- Username: admin
- Password: admin123

Manager:
- Username: spa_manager
- Password: password123
```

## Recent Changes
- **October 3, 2025:** Staff tracking for product sales
  - Added staff assignment dropdowns for all product rows in integrated billing
  - Implemented backend validation requiring staff for every product sale
  - Extended staff metrics (total_revenue_generated, total_sales, total_clients_served) to track product sales
  - Staff performance now reflects both service and product sales activity
  - Applied changes across all invoice creation flows (professional, v2, and draft)
  
- **October 3, 2025:** Initial Replit environment setup
  - Cleaned up duplicate entries in requirements.txt
  - Configured Flask server for Replit proxy (0.0.0.0:5000)
  - Set up workflow with webview output on port 5000
  - Configured deployment with autoscale and Gunicorn
  - Verified application is running successfully

## Known Issues
- LSP diagnostics show some unused imports in app.py and models.py (non-critical)
- Dashboard charts may not display on first load (requires data)

## Testing
- Application loads successfully at root URL
- Login page displays correctly with professional UI
- All modules are loading without errors
- Static assets (CSS, JS) are serving correctly

## Future Enhancements
- Integration with external appointment booking systems
- Mobile app integration
- Advanced analytics and reporting
- Multi-location support
- Payment gateway integration
