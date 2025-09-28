# Spa Management System

## Project Overview
This is a comprehensive Flask-based spa and salon management system that includes multiple modules for managing all aspects of a spa business.

## Recent Changes (2025-09-28)
- ✅ Imported from GitHub successfully
- ✅ Set up Replit environment with Python 3.11
- ✅ Configured PostgreSQL database integration (Neon-backed)
- ✅ Fixed main.py to use PostgreSQL instead of SQLite in Replit
- ✅ Set up Flask workflow with webview output on port 5000
- ✅ Configured deployment for autoscale with Gunicorn
- ✅ All views and routes loaded successfully

## Project Architecture
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL (Neon) in Replit, SQLite fallback for local
- **Frontend**: Bootstrap with custom CSS/JS
- **Authentication**: Flask-Login with session management
- **Structure**: Modular design with separate blueprints for each feature

## Key Modules
- Dashboard
- Staff Management & Shift Scheduler  
- Client History & Loyalty
- Services Management
- Bookings & Appointments
- Check-In System
- Billing & Payment Processing
- Inventory Management
- Reports & Analytics
- WhatsApp Notifications

## Configuration
- Host: 0.0.0.0:5000 for development
- Database: PostgreSQL via DATABASE_URL environment variable
- Session: Configured for Replit proxy environment
- CORS: Enabled for Replit webview

## Current Status
- ✅ Application running successfully
- ✅ Login page loads with proper styling
- ✅ All JavaScript components initialized
- ✅ PostgreSQL database connected
- ✅ Ready for deployment

## User Preferences
- Professional spa management system
- Clean, modern UI with Bootstrap
- Comprehensive feature set for spa operations
- Production-ready deployment configuration