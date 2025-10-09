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

## Recent Changes (October 9, 2025)
### Integrated Billing Form - Critical Bug Fixes ✅ (Latest)
- **Duplicate Service Rows Fix**: Fixed appointment-to-bill feature that always created new rows instead of reusing empty first row
- **Double Select2 Dropdowns Fix**: Properly destroy and reinitialize Select2 on cloned rows to prevent duplicate dropdown rendering
- **JavaScript Injection Vulnerability Fix**: Migrated from inline onclick strings to secure data attributes for appointment buttons - fixes service names with quotes/special chars (e.g., "Women's Spa")
- **Empty Container Edge Case**: addServiceRow() now synthesizes template row from scratch when container is completely empty (no UI deadlock)
- **Last Row Protection**: removeRow() prevents deletion of last row by clearing it instead, maintaining form usability
- **Variable Scope Bug Fix**: Fixed ReferenceError in addAppointmentToBill() where isFirstRowEmpty variable was accessed outside its scope
- **Smart Row Reuse**: addAppointmentToBill() intelligently detects empty rows and reuses them before creating new ones
- **Architect Review**: All 7 bugs fixed and approved - complete edge case coverage, security vulnerability closed, no regressions
- **Production Ready**: Billing form fully functional with robust error handling and security improvements
- **Documentation**: Comprehensive bug report created in `BILLING_FORM_BUG_FIXES.md` with testing scenarios

## Recent Changes (October 8, 2025)
### InsightFace-Based Face Recognition System Migration ✅
- **Technology Migration**: Migrated from dlib/face_recognition to InsightFace + ONNXRuntime for improved accuracy and easier installation
- **RGBA Color Channel Support**: Fixed critical color conversion bug - browser webcam captures send RGBA (4-channel) images, now properly converted to BGR for InsightFace processing
- **Face Registration**: Updated `/api/save_face` endpoint to use InsightFace FaceAnalysis for face detection and embedding extraction
- **Face Recognition**: Updated `/api/recognize_face` endpoint to use cosine similarity matching with 0.3 threshold (replaces Euclidean distance)
- **Multi-Point Conversion**: All three color conversion touchpoints fixed (registration, recognition incoming, recognition stored images)
- **Production Ready**: Face recognition fully functional for Customer Management (registration) and Check-In (recognition) workflows
- **Architect Review**: All changes reviewed and approved - RGBA handling complete, no security issues, end-to-end flow verified
- **Dependencies Installed**: insightface==0.7.3, onnxruntime==1.20.1, opencv-python==4.10.0.84

## Recent Changes (October 6, 2025)
### IST Timezone Implementation for Unaki Booking System ✅
- **Timezone Utilities**: Added comprehensive IST timezone utilities (get_ist_now(), IST timezone) using pytz library
- **Database Storage**: All UnakiBooking and ShiftLogs timestamps now stored as naive datetimes in IST timezone
- **API IST Support**: Schedule API now returns current_ist_time and timezone='Asia/Kolkata' to frontend
- **Frontend Integration**: Frontend uses server-provided IST time for current time indicator instead of client-side calculation
- **Booking Timestamps**: New bookings created with IST timestamps (created_at, updated_at, confirmed_at)
- **Documentation**: Added clear comments documenting that database stores naive IST datetimes (not UTC)
- **Testing**: All timezone tests pass with no ValueError exceptions, IST times display correctly
- **Production Ready**: IST timezone support fully implemented and tested for Unaki booking system

### Shift Scheduler & Unaki Booking System Bug Fixes ✅
- **Duplicate Staff Records Resolution**: Created intelligent cleanup script using staff_code as primary identifier, preventing wrongful deactivation of legitimate staff with same names
- **UnakiBooking API Enhancements**: Added DELETE and PATCH endpoints with proper validation and error handling
- **Status Enum Implementation**: Added status enum to UnakiBooking model (scheduled, confirmed, in_progress, completed, cancelled, no_show) for better data integrity
- **Shift Time Validation**: Implemented comprehensive validation ensuring shift_end > shift_start, break_end > break_start, and breaks within shift hours
- **Off-Day Staff Rendering Fix**: Modified schedule API to set null shift times for off-duty staff with day_status='off' and off_reason fields, preventing incorrect timeline overlays
- **Architect Review**: All fixes reviewed and approved - no security issues, no data integrity problems, all critical blockers resolved
- **Production Readiness**: Enhanced from 7/10 to 9/10 with all critical gaps addressed

### Unaki Booking System - Comprehensive End-to-End Testing ✅
- Created comprehensive test suite with 20 test scenarios across 2 test scripts
- Achieved 70% pass rate (14/20 tests passed) - core functionality fully operational
- Validated all critical booking scenarios: standard appointments, quick bookings, consecutive bookings, multi-service bookings
- Verified conflict detection for overlapping appointments (working correctly)
- Tested all 4 booking sources: unaki_system, phone, walk_in, online (all functional)
- Validated input validation: missing fields, invalid formats, non-existent staff (all working)
- Identified 3 critical gaps: shift/break configuration missing, deletion endpoint not implemented, partial updates not supported
- Created detailed documentation: `UNAKI_TESTING_FINAL_REPORT.md` with comprehensive findings and recommendations
- **Production Readiness**: 7/10 - Core booking functionality is production-ready, with identified gaps for future enhancement
- **Architect Review**: Testing complete with critical gaps identified but core functionality verified

### User Management System Implementation ✅
- Created comprehensive user management system with full CRUD operations
- Implemented dedicated user management module (`modules/user_management/`)
- Added role-based access control (RBAC) with permission management
- Created 37 granular permissions across 11 modules (dashboard, clients, staff, services, packages, appointments, billing, reports, expenses, inventory, settings, user_management)
- Seeded 5 default roles: Super Administrator, Manager, Receptionist, Therapist, Accountant
- Created 4 departments: Spa Services, Front Desk, Management, Finance
- Built admin-only decorator with multi-layered authorization (role + permission checks)
- Implemented user management dashboard with statistics and quick access
- Added access control matrix view showing all user permissions
- Fixed authorization flaw to properly support super_admin role
- All features reviewed and approved by architect

### User Management Testing & Bug Fixes ✅
- Completed comprehensive end-to-end testing of all user management features
- Fixed critical staff route 404 error by adding @app.route('/staff') decorator
- Fixed template error (true.has_role → current_user.has_role) in staff.html
- Resolved Flask endpoint conflict by renaming duplicate punch_out function in inventory module
- All 10 regression tests now pass at 100% success rate
- Verified login, user creation, profile management, role/permission system, and staff attendance

## System Architecture
The application is built with Flask and uses SQLAlchemy for database interactions. It follows a modular design, separating features into distinct modules (e.g., auth, clients, billing).

**UI/UX Decisions:**
- Uses Bootstrap for responsive and consistent UI components.
- Visual enhancements include distinct styling for student offers (purple gradient, graduation cap icon) and color-coded elements to differentiate package types.
- Interactive modals are used for displaying detailed information, such as student offer specifics.
- Unaki booking system features visual overlays for holidays and off-days in the calendar (Indigo for holidays, Gray for off-days).

**Technical Implementations:**
- **Core Modules:** Dashboard, Client Management, Staff Management, Shift Scheduling, Appointment Booking (Unaki integration), Integrated Billing, Service Catalog, Package Management (Prepaid, Service, Memberships, Student Offers, Kitty Party), Inventory, Check-In, Reporting, Notifications, User Roles & Permissions, User Management, **Face Recognition System (NEW)**.
- **Face Recognition System:** InsightFace-based biometric authentication for customer registration and check-in:
  - Face registration via webcam in Customer Management module (stores face embeddings in database)
  - Face recognition matching in Check-In module (cosine similarity with 0.3 threshold)
  - RGBA-to-BGR color space conversion for browser webcam captures
  - CPU-based inference using ONNXRuntime (no GPU dependencies required)
  - Base64 image encoding/decoding for frontend-backend communication
- **User Management System:** Complete administrative interface for managing users, roles, and permissions with:
  - User CRUD operations (create, read, update, delete)
  - Role management with permission assignment
  - Permission management across all system modules
  - Access control matrix visualization
  - Multi-layered authorization (role-based + permission-based)
  - Support for both legacy and dynamic RBAC models
  - Admin-only access with `admin_required` decorator
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
- **Face Recognition:** InsightFace 0.7.3, ONNXRuntime 1.20.1, OpenCV-Python 4.10.0.84
- **Utility Libraries:** Pandas, OpenAI, BeautifulSoup4, Requests