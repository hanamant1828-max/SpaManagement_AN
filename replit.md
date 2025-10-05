# Spa & Salon Suite Management System

## Project Overview
This is a comprehensive **Spa & Salon Management System** built with Flask and Python. It provides a complete solution for managing spa/salon operations including staff, clients, appointments, billing, inventory, and more.

## Recent Changes (October 5, 2025)
### Package Type-Specific Billing Methods (Latest)
- **Switch/Case Package Routing**: Implemented package-type-specific calculation methods in `package_billing_service.py`
  - Created 6 dedicated methods for each package type:
    1. `_apply_service_package_benefit()` - For service packages with free session tracking
    2. `_apply_prepaid_package_benefit()` - For prepaid credit deduction
    3. `_apply_membership_package_benefit()` - For unlimited access memberships
    4. `_apply_student_offer_package_benefit()` - For student discount offers
    5. `_apply_yearly_membership_package_benefit()` - For yearly unlimited memberships
    6. `_apply_kitty_party_package_benefit()` - For group/kitty party packages
  
- **Enhanced Routing Logic**:
  - Modified `_apply_benefit_by_type()` to use switch/case (if/elif) routing based on `package_type`
  - Each package type method properly delegates to underlying benefit logic:
    - Service packages → `_apply_free_benefit()` (free sessions)
    - Prepaid packages → `_apply_prepaid_benefit()` (balance deduction)
    - Memberships → `_apply_unlimited_benefit()` (unlimited access)
    - Student offers → `_apply_discount_benefit()` (discount percentage)
    - Yearly memberships → `_apply_unlimited_benefit()` (unlimited access)
    - Kitty party → `_apply_free_benefit()` or `_apply_discount_benefit()` (based on config)
  
- **Benefits**:
  - ✅ Clear separation of concerns - each package type has dedicated logic
  - ✅ Easier maintenance and debugging with explicit routing
  - ✅ Backward compatibility maintained with fallback to benefit_type
  - ✅ All package types properly tracked with usage and balance management
  - ✅ Improved code readability with descriptive method names

### Billing-Package Integration Enhancements
- **Comprehensive API Endpoint**: Added `/integrated-billing/check-package-benefits` endpoint for real-time package benefit verification
  - Supports all benefit types: free sessions, prepaid credit, discount packages, and unlimited memberships
  - Returns detailed benefit information including coverage amounts and package usage
  - Handles partial session coverage and prepaid credit deduction
  
- **Data Synchronization**: Implemented bidirectional sync between PackageBenefitTracker and ServicePackageAssignment
  - Added `_sync_assignment_with_tracker()` method to ensure data consistency
  - Automatically syncs after every benefit application (free, discount, prepaid)
  - Updates package status (active → completed/expired) based on usage and expiry
  - Prevents data drift between dual tracking systems
  
- **Real-World Scenario Handling**:
  - **Partial Usage**: Package benefits can now partially cover service costs
    - If customer has 0.5 sessions remaining, they get 50% discount
    - Prepaid credit deducts the lesser of (service cost, remaining balance)
  - **Package Expiry**: Automatic expiry check and status updates
  - **Multiple Package Types**: Support for free sessions, discounts, prepaid, and unlimited benefits
  - **Session Exhaustion**: Auto-deactivates packages when fully used
  
- **Frontend JavaScript Updates** (integrated_billing.html):
  - Updated `BillingState` to track `selectedCustomerId` for benefit checking
  - Fixed `checkPackageBenefit()` to use consistent field names:
    - `benefit_type` instead of `package_type`
    - `remaining_count` instead of `sessions.remaining`
    - `balance_remaining` instead of `credit.remaining`
    - `assignment_id` for package identification
  - Added support for all 4 package benefit types in frontend:
    1. Free sessions (benefit_type: 'free')
    2. Prepaid credit (benefit_type: 'prepaid')
    3. Discount packages (benefit_type: 'discount')
    4. Unlimited memberships (benefit_type: 'unlimited')
  - Package benefits now display in real-time as services are added to invoice
  
- **Backend Service Layer** (package_billing_service.py):
  - Enhanced `_apply_free_benefit()` to handle partial session coverage
  - Enhanced `_apply_discount_benefit()` with proper sync
  - Enhanced `_apply_prepaid_benefit()` with partial credit deduction
  - All benefit methods now call `_sync_assignment_with_tracker()` after updates
  
- **Benefits**:
  - ✅ Eliminates data inconsistency between tracking models
  - ✅ Handles real-world scenarios like partial usage and expiry
  - ✅ Provides accurate, real-time package benefit information
  - ✅ Supports all package types (service, prepaid, discount, unlimited)
  - ✅ Frontend and backend now use consistent data structure

## Recent Changes (October 4, 2025)
- **Project Import Completed**: Successfully imported from GitHub and configured for Replit
- **Database**: Using SQLite database stored in `hanamantdatabase/workspace.db`
  - SQLite chosen as requested by user for local storage
  - Database automatically created on first run
  - No external database services required
- **Server**: Running on port 5000 with Gunicorn in webview mode
- **Environment**: SESSION_SECRET configured and working
- **Workflow**: Configured with webview output type for easy access
- **Deployment**: Configured for Replit autoscale deployment
- **Shift Scheduler Fix**: Added automatic database migration system that runs on startup
  - Automatically adds missing columns (out_of_office_start, out_of_office_end, out_of_office_reason) to shift_logs table
  - **This fix is permanent** - anyone cloning this project will have the database schema automatically corrected on first run
  - No manual database fixes needed after cloning from GitHub
- **Holiday & Off-Day Support**: Implemented visual holiday/off-day tracking in Unaki booking system
  - Added `day_status` field to shift_logs (values: "holiday", "off", or "scheduled")
  - Visual overlays in booking calendar:
    - Holidays: Indigo color (#6366f1) overlay with "Holiday" label
    - Off-days: Gray overlay with "Off Day" label
  - Test data script available: `test_shift_holidays.py`
  - Test dates (Oct 4-9):
    - Oct 4: All staff scheduled (9am-5pm)
    - Oct 5: All staff on HOLIDAY
    - Oct 6: Mixed schedule with some staff absent
    - Oct 7-8: Regular scheduled shifts
    - Oct 9: All staff on LEAVE (off-day)

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

### Automatic Database Migrations
The application includes an automatic migration system that runs on every startup:
- **Location**: `run_automatic_migrations()` function in `app.py`
- **Purpose**: Ensures database schema is always up to date when cloning from GitHub
- **How it works**:
  1. Checks if tables exist
  2. Compares current columns with required columns
  3. Automatically adds any missing columns
  4. Logs all changes to the console
- **Benefits**: No manual database fixes needed after cloning the project

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
