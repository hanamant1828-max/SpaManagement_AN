# Spa & Salon Suite Management System

## Overview
A comprehensive spa and salon management system built with Flask, designed to streamline business operations for spas and salons. This application provides a complete suite of tools for managing clients, staff, appointments, billing, inventory, and more.

## Current State
- **Status**: Successfully migrated to Replit environment with professional Out of Office feature
- **Database**: SQLite for development (located in `hanamantdatabase/`)
- **Server**: Running on port 5000 with Gunicorn (production-ready)
- **Date**: October 4, 2025

## Technology Stack
- **Backend**: Flask 3.1.1, Python 3.11
- **Database**: SQLite (development), PostgreSQL-ready for production
- **ORM**: SQLAlchemy 2.0.41
- **Authentication**: Flask-Login 0.6.3
- **Forms**: Flask-WTF 1.2.2, WTForms 3.2.1
- **Frontend**: Bootstrap, Feather Icons, Chart.js
- **Production Server**: Gunicorn 23.0.0

## Key Features
1. **Dashboard**: Real-time business metrics and overview
2. **Client Management**: Customer profiles with visit history and loyalty tracking
3. **Staff Management**: Full CRUD operations, role assignments, department management
4. **Shift Scheduling**: Dynamic shift scheduler with day-by-day configuration
   - **Out of Office / Field Work**: Professional tracking system for staff out-of-office time
     - Single date selection
     - Specific start and return times
     - Reason tracking (max 200 characters)
     - Validation ensures data integrity
5. **Appointment Booking**: Flexible booking system (Unaki integration)
6. **Integrated Billing**: Professional invoices with GST/SGST/IGST calculations
7. **Service Catalog**: Service management with categorization, pricing, and duration
8. **Package Management**: 
   - Prepaid credits
   - Service packages
   - Memberships
   - Student discounts
   - Kitty party bundles
9. **Inventory Management**: Batch-centric stock tracking with location management
10. **Check-In System**: Staff attendance tracking with facial recognition support
11. **Reporting**: Revenue, expense, staff performance, and inventory reports
12. **Notifications**: WhatsApp reminders and automated customer communications
13. **User Roles & Permissions**: Granular access control

## Project Structure
```
.
├── app.py                    # Main Flask application configuration
├── main.py                   # Application entry point
├── models.py                 # Database models
├── routes.py                 # Route definitions
├── forms.py                  # Form definitions
├── utils.py                  # Utility functions
├── modules/                  # Feature modules
│   ├── auth/                 # Authentication
│   ├── dashboard/            # Dashboard views
│   ├── clients/              # Client management
│   ├── staff/                # Staff management
│   ├── bookings/             # Appointment booking
│   ├── billing/              # Billing and invoicing
│   ├── services/             # Service management
│   ├── inventory/            # Inventory control
│   ├── packages/             # Package management
│   ├── expenses/             # Expense tracking
│   ├── reports/              # Reporting
│   ├── settings/             # System settings
│   ├── checkin/              # Staff check-in
│   └── notifications/        # Notifications
├── templates/                # Jinja2 templates
├── static/                   # Static assets (CSS, JS, images)
├── hanamantdatabase/         # SQLite database directory
└── demo_data/                # Demo data generation scripts
```

## Environment Configuration
Required environment variables:
- `SESSION_SECRET`: Session encryption key (configured in Replit secrets)
- `DATABASE_URL`: Database connection string (configured in Replit secrets)
- `PORT`: Server port (default: 5000)

## Running the Application
The application runs automatically via Replit workflow with Gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

The server binds to `0.0.0.0:5000` to work with Replit's proxy system. The app is exposed at module level in `main.py` for WSGI compatibility.

## Database Setup
The application uses SQLite in development with automatic table creation on startup. The database is stored in `hanamantdatabase/workspace.db` with WAL mode enabled for better concurrency.

For demo data, run:
```bash
python setup_demo_database.py
```

## Default Login Credentials
Admin User:
- Username: `admin`
- Password: `admin123`

Manager:
- Username: `spa_manager`
- Password: `password123`

## Deployment
The application is configured for Replit Autoscale deployment:
- **Type**: Autoscale (stateless)
- **Command**: `gunicorn --bind 0.0.0.0:5000 --reuse-port main:app`
- **Port**: 5000

## Recent Changes
### October 4, 2025 - Shift Scheduler Integration with Unaki Booking System
- **Backend Integration**:
  - Enhanced `/api/unaki/schedule` endpoint to include comprehensive shift data:
    - Shift hours (shift_start, shift_end)
    - Break times (breaks array with start/end)
    - Out-of-office periods (ooo array with start/end/reason)
    - Staff working status and shift status
  - Created `validate_against_shift()` helper function for booking validation:
    - Validates bookings against shift hours
    - Prevents bookings during break times
    - Blocks bookings during out-of-office periods
    - Checks staff availability (absent, holiday status)
  - Integrated shift validation into `/api/unaki/check-conflicts` endpoint
- **Frontend Enhancements**:
  - Added visual overlays on Unaki booking timeline:
    - Yellow overlays for staff break times
    - Red overlays for out-of-office periods
    - Gray overlays for off-duty hours
  - Implemented `loadShiftSchedule()` to fetch shift data
  - Implemented `renderShiftOverlays()` to visualize shift constraints
  - Enhanced `checkConflicts()` to validate bookings against shift rules via backend API
  - Added real-time conflict warnings showing shift violations
- **User Experience**:
  - Staff shifts, breaks, and OOO times are now visually clear in the booking interface
  - Users receive immediate feedback when attempting to book during unavailable times
  - Booking system respects staff schedules and prevents scheduling conflicts
  - Tooltips display out-of-office reasons for transparency
  
### October 4, 2025 - Professional Out of Office Feature Implementation
- **Database Migration**: Added `out_of_office_start`, `out_of_office_end`, and `out_of_office_reason` columns to `shift_logs` table
- **Backend Enhancements**:
  - Implemented comprehensive validation (required fields, time validation, 200-char limit)
  - Added professional error handling with detailed messages
  - Ensured start time must be before end time
- **Frontend Improvements**:
  - Updated UI to single date selection (removed date range)
  - Added dedicated Start Time and Expected Return time fields
  - Implemented client-side validation with user-friendly alerts
  - Enhanced UX with success/error messages instead of alert boxes
- **Workflow Configuration**: 
  - Fixed main.py to expose app at module level for Gunicorn compatibility
  - Configured workflow with webview output type on port 5000
  - Successfully running with Gunicorn in production-ready mode

### October 3, 2025 - Replit Migration
- Migrated from GitHub to Replit environment
- Fixed syntax error in `modules/billing/integrated_billing_views.py`
- Configured Flask application for Replit proxy compatibility
- Application successfully running and accessible via webview

## Development Guidelines
1. **Database**: Always use SQLite for development, PostgreSQL for production
2. **Port**: Frontend must use port 5000 (Replit requirement)
3. **Host**: Bind to `0.0.0.0` for Replit compatibility
4. **CORS**: Configured in `app.py` for Replit Preview
5. **Cache Control**: Disabled for development to ensure live updates
6. **Session Secret**: Never hardcode, always use environment variable

## Known Issues
- Minor LSP diagnostics in `app.py`, `modules/staff/shift_scheduler_views.py`, and `templates/shift_scheduler.html` (non-critical)
- These are related to import order and type checking, not affecting runtime
- Some package views (`prepaid`, `student_offer`) have import warnings but don't affect core functionality

## File Locations
- **Logs**: `/tmp/logs/`
- **Database**: `hanamantdatabase/workspace.db`
- **Static Assets**: `static/`
- **Templates**: `templates/`

## User Preferences
None documented yet.

## Architecture Notes
- Modular design with separate feature modules
- Blueprint-based routing
- SQLAlchemy ORM with relationship management
- Flask-Login for authentication
- CSRF protection (disabled for development, enable for production)
- Proxy-aware URL generation for deployment environments
