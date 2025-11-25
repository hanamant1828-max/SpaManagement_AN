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
- **Core Modules:** Dashboard, Client Management, Staff Management, Shift Scheduling, Appointment Booking (Unaki integration), Integrated Billing, Service Catalog, Package Management (Prepaid, Service, Memberships, Student Offers, Kitty Party), Inventory, Check-In, Reporting, Notifications, User Roles & Permissions, User Management, Face Recognition System, and **Public Website Module**.
- **Public Website Module (NEW):** A complete public-facing website for customer engagement, featuring:
  - **Homepage (/):** Hero section with background image, featured services showcase, call-to-action buttons, and WhatsApp integration
  - **Services Page (/our-services):** Categorized service listings with pricing, duration, and descriptions pulled from the Service and Category database models
  - **Online Booking (/book-online):** Customer-friendly booking form that creates UnakiBooking records with `booking_source='online'`, auto-creates Customer records, and sends booking confirmations
  - **Contact Page (/contact):** Business information, Google Maps embed, phone/email/WhatsApp contact buttons, and business hours display
  - **Gallery Page (/gallery):** Responsive image gallery with placeholder images from Unsplash, ready for custom salon photos
  - **Mobile-Responsive Design:** Bootstrap 5 framework with professional spa/salon color scheme (gold/brown tones), sticky navigation, and WhatsApp floating chat button
  - **Database Integration:** Seamlessly integrates with existing models (Service, Category, UnakiBooking, Customer, SystemSetting) to ensure data consistency between public and admin systems
  - **Separate Route Structure:** Public routes (/, /our-services, /book-online, /contact, /gallery) are distinct from admin routes (/login, /admin, /services) to avoid conflicts while maintaining staff access via "Staff Login" button in navigation
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

## Configured Integrations
- **WhatsApp Notifications (Twilio):** ✅ Successfully configured on November 19, 2025. Twilio credentials are securely stored as environment secrets (TWILIO_ACCOUNT_SID, TWILIO_API_KEY, TWILIO_API_SECRET, TWILIO_WHATSAPP_NUMBER). The system can now send WhatsApp notifications for appointment confirmations, booking reminders, custom notifications, and bulk messaging to clients. Integration uses Twilio's WhatsApp API with proper authentication through API keys.

## Recent Fixes
- **November 25, 2025 (Latest):** Completed comprehensive 360-degree testing of Integrated Billing View (`/integrated-billing`). Fixed dropdown arrow visibility issue where all 9 billing dropdowns (customer, service, staff, product, batch, payment terms, payment method, discount type) were missing visual dropdown indicators. Added CSS rules (`static/css/style.css`, lines 957-973) to restore SVG dropdown arrows for all `.form-select` and `.form-select-lg` elements using data URIs with proper positioning and sizing. Removed test data service "awfsdg" (₹25,254.00) from database. Created comprehensive test report documenting all billing features, data integrity checks, revenue analysis (₹1,023,050.91 paid, ₹139,664.50 pending), and validation of invoice workflows, package benefits, inventory management, and tax calculations. All 9 dropdowns now display consistently with proper visual indicators. System verified as production-ready with 113 invoices processed across 121 active customers.
- **November 24, 2025:** Fixed critical "Saving..." button bug in Staff Management form. When form validation failed, the Save button remained stuck in "Saving..." state (disabled with spinning icon), preventing users from retrying. Fixed by adding explicit button state reset when validation fails (`templates/comprehensive_staff.html`, lines 836-837) plus safety net in finally block (lines 884-887). Additionally eliminated console warnings for optional fields (shiftStart, shiftEnd, workingDays) by implementing `optional` parameter in `getFieldValue` function. Created comprehensive automated test suite (`test_staff_management_comprehensive.py`) achieving 100% pass rate (11/11 tests) covering page loading, API endpoints, validation, and staff creation.
- **November 23, 2025:** Fixed Staff Management page data loading issue. Staff data was not appearing automatically on page load; it only displayed after clicking the "Clear" button. The root cause was the `showLoading(false)` call in the finally block of `loadStaffData()` executing AFTER the UI decision logic (showTable/showEmptyState), which was hiding the table immediately after it was displayed. Fixed by moving `showLoading(false)` to execute BEFORE the UI decision logic in both success and error paths (`templates/comprehensive_staff.html`, lines 1111 and 1141). Staff data now loads and displays automatically on page load without requiring manual filter clearing.
- **November 19, 2025:** Fixed Customer Management search button functionality. The search input was only performing client-side filtering without submitting queries to the server. Wrapped the search input in a form (`templates/customers.html`, lines 485-493) that submits GET requests to `/customers` with the search parameter. Users can now search by:
  - Clicking the search icon to submit the query
  - Pressing Enter in the search box (default form behavior)
  - The backend `search_customers()` function already supports server-side search by name, phone, and email
- **November 19, 2025:** Verified online booking customer visibility in Client Management. All customers created through the online booking system (`/book-online`) are correctly stored with `is_active=True` and appear in the Client Management list (`/customers`). The customer creation code in `modules/website/website_views.py` (lines 214-222) explicitly sets `is_active=True`, ensuring all customers are visible regardless of booking source. Database verification confirmed all 111 customers have `is_active=1`. The query functions in `modules/clients/clients_queries.py` correctly filter by `is_active=True` without any booking source discrimination.
- **November 19, 2025:** Fixed Internal Server Error caused by missing blueprint registration. The `assign_packages_bp` blueprint was imported but not registered with the Flask app, causing `BuildError` when trying to access the "Assign & Pay" navigation link. Fixed by adding `app.register_blueprint(assign_packages_bp)` in `app.py` line 612. All Flask blueprints must be explicitly registered to make their routes accessible.