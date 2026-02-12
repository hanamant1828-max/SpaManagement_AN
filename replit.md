# Spa & Salon Suite

## Overview
A comprehensive Spa & Salon Management System built with Flask. Features include client management, appointment booking, staff management, billing, inventory, packages/memberships, expense tracking, reports, and more.

## Recent Changes
- 2026-02-12: Completed import to Replit environment. Installed all Python dependencies, configured workflow, verified app runs successfully.
- 2026-02-11: Migrated project to Replit environment. Cleaned up duplicate workflows and requirements.txt. Configured deployment settings.

## Project Architecture
- **Framework**: Flask (Python 3.11)
- **Database**: SQLite (stored in `hanamantdatabase/` folder)
- **Authentication**: Flask-Login with session-based auth
- **Frontend**: Server-side rendered templates with Jinja2, Bootstrap CSS
- **WSGI Server**: Gunicorn (production), Flask dev server (development via main.py)

### Key Files
- `app.py` - Main Flask application setup, database config, route registration
- `main.py` - Entry point for running the application
- `models.py` - SQLAlchemy database models
- `routes.py` - Additional route definitions
- `forms.py` - WTForms form definitions
- `utils.py` - Utility functions

### Module Structure
The app uses a modular structure under `modules/`:
- `modules/auth/` - Authentication views
- `modules/dashboard/` - Dashboard views
- `modules/clients/` - Client management
- `modules/services/` - Service management
- `modules/bookings/` - Appointment booking
- `modules/staff/` - Staff management & shift scheduling
- `modules/billing/` - Billing & invoicing
- `modules/inventory/` - Inventory management
- `modules/packages/` - Packages & memberships
- `modules/expenses/` - Expense tracking
- `modules/reports/` - Reporting
- `modules/settings/` - System settings
- `modules/notifications/` - Notifications
- `modules/checkin/` - Client check-in (with face recognition)

### Templates
HTML templates are in `templates/` using Jinja2 with Bootstrap.

### Static Files
CSS, JS, and uploads in `static/`.

## User Preferences
- IST (Asia/Kolkata) timezone for all datetime operations
- Currency formatting via utils module

## Running
- Development: `python main.py` (Flask dev server on port 5000)
- Production: `gunicorn --bind 0.0.0.0:5000 main:app`
