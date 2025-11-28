# Spa & Salon Suite Management System

## Overview
This project is a comprehensive Spa & Salon Management System built with Flask and Python. It aims to streamline spa/salon operations by managing staff, clients, appointments, billing, inventory, and more. The system provides real-time business metrics, robust client and staff management, dynamic scheduling, integrated billing with various package options, and a public-facing website. Its purpose is to enhance user experience, automate processes, and improve operational efficiency and profitability.

## User Preferences
- Follow existing Flask conventions and project structure
- Use SQLAlchemy for all database operations
- Maintain modular architecture with separate view files
- Keep templates organized by feature module
- Use Bootstrap for UI components
- Implement proper error handling and logging

## System Architecture
The application uses Flask and SQLAlchemy, following a modular design with features separated into distinct modules.

**UI/UX Decisions:**
- Employs Bootstrap for a responsive and consistent user interface.
- Utilizes distinct styling for student offers and color-coded elements for package types.
- Interactive modals are used for displaying detailed information.
- The Unaki booking system visually highlights holidays and off-days on the calendar.
- **Real-time Validation & Conflict Checking:** The bulk booking modal features a modern dropdown time picker, real-time conflict checking (staff and customer conflicts), smart end time calculation, and visual validation indicators with animated alerts.

**Technical Implementations:**
- **Core Modules:** Dashboard, Client Management, Staff Management, Shift Scheduling, Appointment Booking (Unaki integration), Integrated Billing, Service Catalog, Package Management (Prepaid, Service, Memberships, Student Offers, Kitty Party), Inventory, Check-In, Reporting, Notifications, User Roles & Permissions, User Management, Face Recognition System, and a Public Website Module.
- **Public Website Module:** A complete public-facing website with a homepage, services page (categorized listings), online booking (creates UnakiBooking records, auto-creates Customer records), contact page, and gallery. It is mobile-responsive using Bootstrap 5 and integrates with existing database models.
- **Face Recognition System:** InsightFace-based biometric authentication for customer registration and check-in, supporting webcam capture and CPU-based ONNXRuntime inference.
- **User Management System:** Administrative interface for managing users, roles, and permissions, including CRUD operations, access control matrix, and multi-layered authorization.
- **Package Management:** Implements type-specific billing methods for various package types.
- **Billing-Package Integration:** API for real-time package benefit verification and bidirectional data synchronization.
- **Automatic Database Migrations:** Ensures database schema is up-to-date on startup.
- **Session Management:** Utilizes Flask's session management.
- **Timezone Management:** Comprehensive IST timezone utilities using `pytz` for timestamps.
- **12-Hour AM/PM Format:** Implemented across all visible time fields with robust input validation.

**System Design Choices:**
- **Database:** Defaults to SQLite for local development (`hanamantdatabase/workspace.db`), with optional PostgreSQL support.
- **Server:** Gunicorn serves the application on port 5000.
- **Deployment:** Configured for Replit autoscale deployment and Vercel.
- **Authentication:** Managed via Flask-Login.
- **Forms:** Implemented using Flask-WTF and WTForms.

## External Dependencies
- **Backend Framework:** Flask
- **ORM:** SQLAlchemy
- **Database:** SQLite, PostgreSQL
- **Web Server:** Gunicorn
- **Authentication:** Flask-Login
- **Forms:** Flask-WTF, WTForms
- **Face Recognition:** InsightFace, ONNXRuntime, OpenCV-Python
- **Timezone:** pytz
- **Utility Libraries:** Pandas, OpenAI, BeautifulSoup4, Requests
- **WhatsApp Notifications:** Twilio (for appointment confirmations, reminders, and custom messaging)