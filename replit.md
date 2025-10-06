# Spa & Salon Suite Management System

## Overview
This is a comprehensive **Spa & Salon Management System** built with Flask and Python. It provides a complete solution for managing spa/salon operations including staff, clients, appointments, billing, inventory, and more. The project aims to streamline spa and salon operations, offering real-time business metrics, robust client and staff management, dynamic scheduling, and integrated billing with various package options. It focuses on enhancing user experience through detailed tracking, automated processes, and clear financial oversight.

## User Preferences
- Follow existing Flask conventions and project structure
- Use SQLAlchemy for all database operations
- Maintain modular architecture with separate view files
- Keep templates organized by feature module
- Use Bootstrap for UI components
- Implement proper error handling and logging

## System Architecture
The application is built with Flask and uses SQLAlchemy for database interactions. It follows a modular design, separating features into distinct modules (e.g., auth, clients, billing).

**UI/UX Decisions:**
- Uses Bootstrap for responsive and consistent UI components.
- Visual enhancements include distinct styling for student offers (purple gradient, graduation cap icon) and color-coded elements to differentiate package types.
- Interactive modals are used for displaying detailed information, such as student offer specifics.
- Unaki booking system features visual overlays for holidays and off-days in the calendar (Indigo for holidays, Gray for off-days).

**Technical Implementations:**
- **Core Modules:** Dashboard, Client Management, Staff Management, Shift Scheduling, Appointment Booking (Unaki integration), Integrated Billing, Service Catalog, Package Management (Prepaid, Service, Memberships, Student Offers, Kitty Party), Inventory, Check-In, Reporting, Notifications, User Roles & Permissions.
- **Package Management:** Implements type-specific billing methods for various package types (service, prepaid, membership, student offer, yearly membership, kitty party) using dedicated functions and a `switch/case` routing mechanism.
- **Billing-Package Integration:** Comprehensive API endpoint for real-time package benefit verification. Bidirectional data synchronization between `PackageBenefitTracker` and `ServicePackageAssignment` ensures consistency, handling partial usage, package expiry, and different benefit types.
- **Automatic Database Migrations:** An automatic migration system runs on startup to ensure the database schema is always up-to-date, adding missing columns as needed (e.g., for shift logs).
- **Session Management:** Utilizes Flask's session management with a `SESSION_SECRET` environment variable.

**System Design Choices:**
- **Database:** Defaults to SQLite for local development, with support for PostgreSQL. Stored in `hanamantdatabase/workspace.db` with WAL mode and foreign key constraints enabled.
- **Server:** Gunicorn is used for serving the application on port 5000.
- **Deployment:** Configured for Replit autoscale deployment and Vercel.
- **Authentication:** Managed via Flask-Login.
- **Forms:** Implemented using Flask-WTF and WTForms.

## External Dependencies
- **Backend Framework:** Flask 3.1.1
- **ORM:** SQLAlchemy 2.0.41
- **Database:** SQLite (local), PostgreSQL (optional)
- **Web Server:** Gunicorn 23.0.0
- **Authentication:** Flask-Login 0.6.3
- **Forms:** Flask-WTF 1.2.2, WTForms 3.2.1
- **Utility Libraries:** Pandas, OpenAI, BeautifulSoup4, Requests