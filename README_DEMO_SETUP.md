
# Demo Database Setup Guide

## Quick Setup for Client Presentations

This spa management system comes with a comprehensive demo database setup that creates realistic sample data across all modules.

### 🚀 One-Command Setup

```bash
python setup_demo_database.py
```

### 📊 What Gets Created

**System Configuration:**
- 5 User roles (Admin, Manager, Staff, Cashier, Receptionist)
- 6 Departments (Massage, Skincare, Hair, Nails, Wellness, Reception)  
- 7 Service & expense categories with colors and icons

**Staff & Users:**
- 1 Spa Manager
- 6 Service staff members across different departments
- Complete profiles with roles, departments, schedules
- Realistic contact information and specialties

**Customer Database:**
- 8 Diverse customers with detailed profiles
- Preferences, allergies, and service history
- VIP status and loyalty points
- Contact preferences and referral sources

**Service Catalog:**
- 19 Professional services across all categories
- Realistic pricing and duration
- Detailed descriptions for each service
- Organized by massage, facial, hair, nails, wellness

**Package Deals:**
- 4 Attractive package offerings
- Bridal, relaxation, beauty, and couples packages
- Proper discounting and session tracking
- Realistic validity periods

**Appointment History:**
- 30 days of past completed appointments
- Today's scheduled appointments  
- 14 days of future bookings
- Realistic appointment statuses and notes

**Financial Records:**
- Monthly expenses (rent, supplies, utilities)
- Professional invoices with tax calculations
- Payment tracking and receipt numbers
- Expense categorization

**Inventory (if available):**
- Product categories and locations
- Batch tracking with expiry dates
- Realistic stock levels
- Professional spa products

### 🔐 Login Credentials

```
Admin User:
- Username: admin
- Password: admin123

Manager:  
- Username: spa_manager
- Password: password123

Staff Members:
- All staff: password123
- Usernames: mike_therapist, anna_massage, emily_facial, etc.
```

### 📱 Features Demonstrated

- **Staff Management:** Complete CRUD, role assignments, schedules
- **Customer Management:** Detailed profiles, preferences, history
- **Service Booking:** Real-time scheduling, availability checking
- **Package Management:** Membership tracking, session usage
- **Billing & Invoicing:** Professional invoices, payment processing
- **Inventory Control:** Stock management, batch tracking
- **Reporting:** Revenue, performance, and operational reports
- **Business Settings:** Configurable system preferences

### 🎯 Client Presentation Ready

After running the setup:

1. **Start the application:** `python main.py`
2. **Login as admin:** admin/admin123  
3. **Show live data** in all modules
4. **Demonstrate workflows** with realistic scenarios
5. **Highlight key features** with actual customer data

### 🔄 Reset and Refresh

To regenerate demo data:

```bash
python setup_demo_database.py
```

The script will clear existing demo data and create fresh sample data.

### 📞 Support

This demo setup creates a production-ready environment perfect for:
- Client demonstrations
- Training sessions  
- Feature showcasing
- System testing
- User acceptance testing

All data is professionally crafted to represent a real spa business operation.
