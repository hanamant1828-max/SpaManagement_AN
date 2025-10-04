# Spa & Salon Suite Management System

## Project Overview
This is a comprehensive **Spa & Salon Management System** built with Flask and Python. It provides a complete solution for managing spa/salon operations including staff, clients, appointments, billing, inventory, and more.

## Recent Changes (October 4, 2025)
- **Project Setup**: Configured for Replit environment with proper workflow setup
- **Database**: Using SQLite database stored in `hanamantdatabase/` directory
- **Server**: Running on port 5000 with Gunicorn
- **Environment**: Configured with SESSION_SECRET and DATABASE_URL environment variables
- **Shift Scheduler Fix**: Added missing database columns (out_of_office_start, out_of_office_end, out_of_office_reason) to shift_logs table to fix shift scheduler errors

## Technology Stack
- **Backend**: Flask 3.1.1, SQLAlchemy 2.0.41
- **Database**: SQLite (local) with option for PostgreSQL
- **Server**: Gunicorn 23.0.0
- **Authentication**: Flask-Login 0.6.3
- **Forms**: Flask-WTF 1.2.2, WTForms 3.2.1
- **Additional Libraries**: Pandas, OpenAI, BeautifulSoup4, Requests

## Key Features

### Core Modules
1. **Dashboard**: Real-time business metrics overview
2. **Client Management**: Detailed profiles with visit history and loyalty tracking
3. **Staff Management**: Full CRUD operations, role assignments, department management
4. **Shift Scheduling**: Dynamic shift scheduler with day-by-day configuration
5. **Appointment Booking**: Unaki integration with drag-and-drop and real-time availability
6. **Integrated Billing**: Professional invoices with GST/SGST/IGST calculations
7. **Service Catalog**: Service management with categorization and pricing
8. **Package Management**:
   - Prepaid credit packages
   - Service packages (Buy X, Get Y)
   - Memberships (annual programs)
   - Student offers with discounts
   - Kitty party packages
9. **Inventory Management**: Batch-centric stock tracking with expiry dates
10. **Check-In System**: Staff attendance tracking with facial recognition support
11. **Reporting**: Revenue, expenses, staff performance, client activity reports
12. **Notifications**: Automated customer reminders and system alerts
13. **User Roles & Permissions**: Granular access control

## Project Structure
```
.
├── app.py                    # Main application setup and initialization
├── main.py                   # Entry point for the application
├── models.py                 # Database models
├── routes.py                 # Application routes
├── forms.py                  # WTForms definitions
├── utils.py                  # Utility functions
├── modules/                  # Feature modules
│   ├── auth/                 # Authentication
│   ├── dashboard/            # Dashboard views
│   ├── clients/              # Client management
│   ├── staff/                # Staff management
│   ├── bookings/             # Appointment booking
│   ├── billing/              # Billing and invoicing
│   ├── services/             # Service catalog
│   ├── packages/             # Package management
│   ├── inventory/            # Inventory management
│   ├── checkin/              # Check-in system
│   ├── expenses/             # Expense tracking
│   ├── reports/              # Reporting
│   ├── settings/             # Settings
│   └── notifications/        # Notifications
├── templates/                # Jinja2 templates
├── static/                   # CSS, JS, images
├── hanamantdatabase/         # SQLite database storage
└── instance/                 # Instance-specific files

## Development Setup

### Running the Application
The application is configured to run automatically in Replit:
- **Command**: `gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app`
- **Port**: 5000
- **Host**: 0.0.0.0 (allows all hosts for Replit proxy)

### Demo Database Setup
To populate the database with demo data:
```bash
python setup_demo_database.py
```

This creates:
- 5 User roles
- 6 Departments
- 7 Service categories
- Staff members and users
- 8 Sample customers
- 19 Professional services
- Package deals
- 30 days of appointment history
- Financial records

### Login Credentials
**Admin User:**
- Username: `admin`
- Password: `admin123`

**Manager:**
- Username: `spa_manager`
- Password: `password123`

## Environment Variables
- `SESSION_SECRET`: Secret key for Flask sessions (required)
- `DATABASE_URL`: Database connection URL (optional, defaults to SQLite)
- `SPA_DB_INSTANCE`: Database instance identifier (optional)
- `REPL_SLUG`: Replit slug for database naming (optional)
- `PORT`: Server port (default: 5000)

## Database Configuration
The application uses SQLite by default with the database stored in:
- Path: `hanamantdatabase/<instance>.db`
- WAL mode enabled for better concurrency
- Foreign key constraints enabled
- Automatic schema creation via SQLAlchemy

## API Endpoints
- `/api/unaki/services` - Get active services
- `/api/unaki/staff` - Get active staff members
- `/api/unaki/clients` - Get active clients
- `/api/unaki/schedule` - Get schedule data with shift integration

## Deployment
The application is configured for deployment on Replit and Vercel:
- **Vercel**: Configuration in `vercel.json`
- **Replit**: Automatic deployment with workflow configuration

## User Preferences
- Follow existing Flask conventions and project structure
- Use SQLAlchemy for all database operations
- Maintain modular architecture with separate view files
- Keep templates organized by feature module
- Use Bootstrap for UI components
- Implement proper error handling and logging
