# Spa & Salon Digital Business Suite

## Overview
This project is a comprehensive Flask-based web management system for spa and salon businesses. It aims to provide a complete digital business suite for single-location salons, encompassing appointment booking, client management, inventory tracking, billing, reporting, and real-time dashboard analytics. The system features enterprise-level role-based access control. This production-ready application is designed to streamline operations, enhance client engagement, and provide valuable business insights.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: HTML5 with Bootstrap 5 (dark theme)
- **Styling**: CSS3 with custom variables
- **JavaScript**: Vanilla ES6+ with modular components
- **Icons**: Font Awesome 6.4.0
- **Charts**: Chart.js for data visualization

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database ORM**: SQLAlchemy with declarative base model
- **Authentication**: Flask-Login for session management
- **Forms**: WTForms with Flask-WTF for secure form handling
- **Security**: Werkzeug for password hashing and proxy handling

### Modular Architecture
The system employs a modular design, separating concerns into distinct business modules. Each module has dedicated files for route handlers (`_views.py`) and database queries/business logic (`_queries.py`) to promote maintainability and scalability.

### Database Design
- **ORM**: SQLAlchemy
- **Core Models**: User (staff), Client, Service, Appointment, Inventory, Expense, Invoice, Package, StaffSchedule, and various system configuration models.
- **Features**: Automatic table creation, connection pooling, pre-ping health checks, comprehensive relationships, dynamic CRUD operations.

### Key Features
- **Authentication System**: Role-based access control with granular permissions, user session management, password hashing.
- **Dashboard**: Real-time business metrics, KPIs, appointment tracking, revenue trends, role-specific widgets.
- **Booking & Calendar**: Unified calendar, color-coded appointments, drag-and-drop rescheduling, walk-in/online booking, timetable view.
- **Client Management**: Comprehensive profiles, history, search, preferences, loyalty tracking, communication.
- **Staff Management**: Profiles, role assignments, commission/hourly rates, schedule, availability, performance metrics.
- **Inventory Management**: Product tracking, low stock alerts, expiration dates, category-based organization, stock level management, comprehensive consumption tracking with automatic stock level integration, purchase order management with stock integration, and full CRUD operations with stock reversal.
- **Billing & Payment**: Invoice generation, payment tracking, pending payment management, revenue reporting.
- **Expense Tracking**: Categorization, monthly summaries, receipt management, cost analysis.
- **Reports & Analytics**: Customizable date range reporting, revenue/performance analytics, export functionality, visual charts.
- **Subscription Packages**: Comprehensive package system with multi-service selection, discounts, validity periods, session tracking.
- **Real-World Business Operations**: Includes marketing promotions, client waitlist, POS integration, recurring appointments, customer review system, and configurable business settings.
- **Dynamic Configuration System**: Manage roles, permissions, categories, departments, and system settings dynamically.

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
- `SESSION_SECRET` - ✅ Configured
- `DATABASE_URL` - ✅ Configured

## Recent Changes
**September 10, 2025** - Project successfully imported and configured for Replit environment:
- Installed all Python dependencies via packager tool
- Created PostgreSQL database and configured DATABASE_URL environment variable
- Set up SESSION_SECRET environment variable for secure session management
- Configured Flask application for webview compatibility with proper CORS headers
- Set up workflow to run on port 5000 with webview output type
- Configured deployment settings for autoscale with Gunicorn
- Verified application runs successfully with login page accessible
- All modules loading correctly and default data initialization working

**September 10, 2025** - MAJOR INVENTORY SYSTEM REFACTORING - BATCH-CENTRIC APPROACH:
- ✅ Refactored InventoryProduct model - removed all stock tracking fields (current_stock, reserved_stock, available_stock)
- ✅ Updated InventoryBatch model - made batch_name globally unique, added proper relationships
- ✅ Created new InventoryAuditLog model for comprehensive batch transaction tracking
- ✅ Completely rewrote queries.py with clean batch-centric functions (reduced LSP errors from 42 to 26)
- ✅ Updated API endpoints in views.py to use batch-centric approach
- ✅ Implemented batch-first workflow for adjustments, consumption, and stock management
- ✅ Added validation for expired batches and insufficient stock at batch level
- ✅ Created audit log system for tracking all batch-level stock changes
- 🔄 Frontend UI updates needed to implement batch-first workflow with proper dropdowns
- 🔄 Need to fix remaining dashboard references to old stock fields
- 🔄 Transfer APIs need to be implemented for batch-to-batch transfers

## Project Status
🔄 **REFACTORING IN PROGRESS** - The spa management system's inventory module has been successfully refactored to use a batch-centric approach. The backend models, queries, and API endpoints are updated and working. The application runs successfully with the new architecture. Remaining work includes updating the frontend UI and fixing dashboard references to complete the transition.