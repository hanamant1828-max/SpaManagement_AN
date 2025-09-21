# Spa Management System - Replit Setup

## Overview
A comprehensive Flask-based Spa Management System with full CRUD operations for managing spa services, staff, customers, appointments, inventory, billing, and reporting.

## Recent Changes (September 21, 2025)
- Successfully imported GitHub project to Replit environment
- Configured PostgreSQL database with proper environment variables
- Set up Flask application to run on port 5000 with webview output
- Verified all major dependencies are available and working
- Configured production deployment with Gunicorn
- Application successfully running and tested

## Project Architecture
- **Backend**: Flask 3.0.3 with SQLAlchemy ORM
- **Database**: PostgreSQL (production) with SQLite fallback (development)
- **Authentication**: Flask-Login with role-based access control
- **Frontend**: Server-side rendered templates with Bootstrap UI
- **Modular Structure**: Organized by feature modules (auth, billing, inventory, etc.)

## Key Features
- Multi-role user management (Admin, Manager, Staff, Cashier)
- Customer management with loyalty tracking
- Service and appointment scheduling
- Comprehensive inventory management
- Billing and invoice system
- Package management (Prepaid, Service, Memberships)
- Staff scheduling with shift management
- Reporting and analytics

## User Preferences
- Application configured for Replit environment with proper host settings
- Uses existing project structure and conventions
- PostgreSQL database for scalability
- Production-ready deployment configuration

## Access Information
- Default admin login: username `admin`, password `admin123`
- Application accessible via Replit webview on port 5000
- Development mode enabled with debug logging

## Deployment
- Configured for autoscale deployment
- Uses Gunicorn production server
- Bound to 0.0.0.0:5000 for proper Replit compatibility