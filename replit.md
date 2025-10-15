# Spa & Salon Suite Management System

## Overview
This project is a comprehensive **Spa & Salon Management System** built with Flask and Python. It provides a complete solution for managing spa/salon operations, including staff, clients, appointments, billing, inventory, and more. The system aims to streamline operations by offering real-time business metrics, robust client and staff management, dynamic scheduling, and integrated billing with various package options. It focuses on enhancing user experience through detailed tracking, automated processes, and clear financial oversight, ultimately improving operational efficiency and profitability.

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
- Utilizes distinct styling for student offers (purple gradient, graduation cap) and color-coded elements to differentiate package types.
- Interactive modals are used for displaying detailed information.
- The Unaki booking system visually highlights holidays and off-days on the calendar (Indigo for holidays, Gray for off-days).
- **Real-time Validation & Conflict Checking:** The bulk booking modal now features:
  - Modern dropdown time picker with 15-minute intervals (9 AM - 9 PM) replacing prompt-based selection
  - Real-time conflict checking that triggers immediately when users select service, staff, date, or time
  - Smart end time calculation that only triggers after a service is selected (since duration depends on service)
  - Dual conflict detection: Staff conflicts (same staff at same time) AND customer conflicts (same customer can't be in two places at once)
  - Visual validation indicators (green checkmarks for valid fields, red borders for conflicts)
  - Animated conflict alerts with shake effects for better user awareness
  - Instant feedback as users fill in fields, preventing booking conflicts before submission

**Technical Implementations:**
- **Core Modules:** Dashboard, Client Management, Staff Management, Shift Scheduling, Appointment Booking (Unaki integration), Integrated Billing, Service Catalog, Package Management (Prepaid, Service, Memberships, Student Offers, Kitty Party), Inventory, Check-In, Reporting, Notifications, User Roles & Permissions, User Management, and a Face Recognition System.
- **Face Recognition System:** InsightFace-based biometric authentication for customer registration and check-in, supporting face registration via webcam and recognition using cosine similarity. It handles RGBA-to-BGR color conversion for browser captures and uses CPU-based ONNXRuntime inference.
- **User Management System:** Provides a complete administrative interface for managing users, roles, and permissions, including CRUD operations, role assignment, permission management across modules, an access control matrix, and multi-layered authorization.
- **Package Management:** Implements type-specific billing methods for various package types (service, prepaid, membership, student offer, yearly membership, kitty party) using dedicated functions.
- **Billing-Package Integration:** Features an API for real-time package benefit verification and bidirectional data synchronization to ensure consistency with partial usage, expiry, and different benefit types.
- **Automatic Database Migrations:** An automatic migration system ensures the database schema is up-to-date on startup, adding missing columns as needed.
- **Session Management:** Utilizes Flask's session management with a `SESSION_SECRET` environment variable.
- **Timezone Management:** Comprehensive IST timezone utilities using `pytz` for `UnakiBooking` and `ShiftLogs` timestamps, storing them as naive datetimes in IST.
- **12-Hour AM/PM Format:** Implemented across all visible time fields with robust input validation and synchronization, while 24-hour format is used for backend processing.

**System Design Choices:**
- **Database:** Defaults to SQLite for local development (`hanamantdatabase/workspace.db` with WAL mode and foreign key constraints enabled), with optional PostgreSQL support.
- **Server:** Gunicorn serves the application on port 5000.
- **Deployment:** Configured for Replit autoscale deployment and Vercel.
- **Authentication:** Managed via Flask-Login.
- **Forms:** Implemented using Flask-WTF and WTForms.

## External Dependencies
- **Backend Framework:** Flask 3.1.1
- **ORM:** SQLAlchemy 2.0.41
- **Database:** SQLite, PostgreSQL
- **Web Server:** Gunicorn 23.0.0
- **Authentication:** Flask-Login 0.6.3
- **Forms:** Flask-WTF 1.2.2, WTForms 3.2.1
- **Face Recognition:** InsightFace 0.7.3, ONNXRuntime 1.20.1, OpenCV-Python 4.10.0.84
- **Timezone:** pytz
- **Utility Libraries:** Pandas, OpenAI, BeautifulSoup4, Requests

## Pending Integrations
- **WhatsApp Notifications (Twilio):** To enable WhatsApp notifications for appointment bookings, the Twilio integration needs to be set up through Replit's integration system. This will allow automatic WhatsApp messages to be sent to clients with their booking details (appointment time, service, staff, etc.). The integration setup was dismissed and needs to be completed for this feature to work.