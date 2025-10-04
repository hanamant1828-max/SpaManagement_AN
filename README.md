# Spa & Salon Suite Management System

A comprehensive Flask-based management system for spas and salons with full-featured modules for staff, clients, appointments, billing, inventory, and more.

## 🚀 Quick Start

### Running on Replit

The application is already configured to run automatically in Replit:

1. Click the **Run** button
2. Navigate to the login page
3. Use these credentials:
   - **Admin**: Username: `admin` | Password: `admin123`
   - **Manager**: Username: `spa_manager` | Password: `password123`

### Demo Database Setup

To populate the database with sample data:

```bash
python setup_demo_database.py
```

This will create sample data including:
- 5 User roles (Admin, Manager, Staff, Cashier, Receptionist)
- 6 Departments (Massage, Skincare, Hair, Nails, Wellness, Reception)
- 20 Staff members with complete profiles
- 30 Sample customers with detailed information
- 19 Professional services across all categories
- Package deals and memberships
- 30 days of appointment history
- Financial records and invoices

## ✨ Features

### Core Modules

- **Dashboard**: Real-time overview of business metrics, revenue, bookings, and performance
- **Client Management**: Complete client profiles with visit history, loyalty tracking, and preferences
- **Staff Management**: Full CRUD operations, role assignments, department management, and performance tracking
- **Shift Scheduling**: Dynamic day-by-day shift scheduler with break management
- **Out of Office Tracking**: Professional system to track staff absences with detailed reasons and durations
- **Appointment Booking**: Unaki integration with drag-and-drop scheduling and real-time availability
- **Integrated Billing**: Professional invoice generation with GST/SGST/IGST calculations
- **Service Catalog**: Complete service management with categories, pricing, and duration tracking
- **Package Management**:
  - Prepaid credit packages
  - Service packages (Buy X, Get Y free)
  - Memberships (annual programs)
  - Student offers with discounts
  - Kitty party packages for group events
- **Inventory Management**: Batch-centric stock tracking with expiry dates and location management
- **Check-In System**: Staff attendance tracking with facial recognition support
- **Reporting**: Comprehensive reports on revenue, expenses, staff performance, client activity, and inventory
- **Notifications**: Automated customer reminders (WhatsApp) and system alerts (low stock, expiring items)
- **User Roles & Permissions**: Granular access control based on defined roles

## 🛠️ Technology Stack

- **Backend**: Flask 3.1.1
- **Database**: SQLite 3 (default) with PostgreSQL support
- **ORM**: SQLAlchemy 2.0.41
- **Server**: Gunicorn 23.0.0
- **Authentication**: Flask-Login 0.6.3
- **Forms**: Flask-WTF 1.2.2, WTForms 3.2.1
- **Frontend**: Bootstrap, Jinja2 templates
- **Additional Libraries**: 
  - Pandas (data processing)
  - OpenAI (AI integration)
  - BeautifulSoup4 (web scraping)
  - Requests (HTTP client)

## 📁 Project Structure

```
.
├── app.py                    # Main Flask application setup
├── main.py                   # Application entry point
├── models.py                 # SQLAlchemy database models
├── routes.py                 # Application routes
├── forms.py                  # WTForms definitions
├── utils.py                  # Utility functions
├── modules/                  # Feature modules
│   ├── auth/                 # Authentication & authorization
│   ├── dashboard/            # Dashboard views
│   ├── clients/              # Client management
│   ├── staff/                # Staff & shift management
│   ├── bookings/             # Appointment booking
│   ├── billing/              # Billing & invoicing
│   ├── services/             # Service catalog
│   ├── packages/             # Package management
│   ├── inventory/            # Inventory tracking
│   ├── checkin/              # Check-in system
│   ├── expenses/             # Expense tracking
│   ├── reports/              # Reporting module
│   ├── settings/             # System settings
│   └── notifications/        # Notification system
├── templates/                # Jinja2 HTML templates
├── static/                   # CSS, JavaScript, images
├── hanamantdatabase/         # SQLite database storage
├── instance/                 # Instance-specific files
└── demo_data/                # Demo data generation scripts
```

## 🔧 Configuration

### Environment Variables

- `SESSION_SECRET`: Flask session secret key (required)
- `DATABASE_URL`: Database connection URL (optional, defaults to SQLite)
- `SPA_DB_INSTANCE`: Database instance identifier (optional)
- `PORT`: Server port (default: 5000)

### Database Configuration

The application uses SQLite by default:
- **Location**: `hanamantdatabase/<instance>.db`
- **Features**:
  - WAL mode for better concurrency
  - Foreign key constraints enabled
  - Automatic schema creation via SQLAlchemy

To use PostgreSQL instead:
1. Set `DATABASE_URL` environment variable
2. The application will automatically detect and use PostgreSQL

## 🌐 API Endpoints

- `GET /api/unaki/services` - Get all active services
- `GET /api/unaki/staff` - Get all active staff members
- `GET /api/unaki/clients` - Get all active clients
- `GET /api/unaki/schedule` - Get schedule data with shift integration

## 📦 Deployment

### Replit (Current Platform)
The application is configured to run on Replit with:
- Automatic workflow setup on port 5000
- Webview output type for preview
- Environment variables managed through Replit Secrets

### Vercel
Configuration available in `vercel.json` for serverless deployment.

### Publishing to Production
1. Ensure all environment variables are set
2. Click the **Publish** button in Replit
3. The deployment is configured as "autoscale" for optimal performance

## 🔒 Security Features

- CSRF protection (Flask-WTF)
- Secure password hashing (Werkzeug)
- Session management (Flask-Login)
- Role-based access control
- SQL injection protection (SQLAlchemy ORM)
- Proxy-aware configuration (ProxyFix)

## 🐛 Known Issues

- Database schema missing some columns in `shift_logs` table:
  - `out_of_office_start`
  - `out_of_office_end`
  - `out_of_office_reason`
  
  These columns are referenced in the code but may not exist in older databases. Run migrations or recreate the database to fix.

## 🤝 Contributing

This is a comprehensive spa management system designed for professional use. When contributing:

1. Follow the existing Flask application structure
2. Use SQLAlchemy for all database operations
3. Maintain the modular architecture
4. Keep templates organized by feature
5. Use Bootstrap for UI consistency
6. Implement proper error handling

## 📄 License

This project is part of a commercial spa management solution.

## 📞 Support

For issues or questions about this system, please refer to the project documentation in `replit.md`.

---

**Built with ❤️ for Spa & Salon Management**
