# 📊 Spa Management System - Database Guide

## 🎯 Overview

This document explains how data is organized in your Spa Management System. Think of it like file cabinets where each table is a drawer storing specific information.

---

## 👥 USER MANAGEMENT

### 👤 Users (Staff & Employees)
**What it stores:** All staff members, therapists, receptionists, managers, and admin users

**Key Information:**
- Personal details (name, email, phone)
- Login credentials (username, password)
- Role and department
- Profile photo and ID proofs (Aadhaar, PAN)
- Work schedule and shift timings
- Commission rates and salary details
- Facial recognition data for check-in

**Example:** "Sarah Johnson" - Massage Therapist, works Mon-Fri 9am-5pm, 10% commission

---

### 🏢 Roles & Permissions
**What it stores:** Different job roles and what they can access

**Available Roles:**
- **Admin** - Can do everything
- **Manager** - Can manage staff, customers, and bookings
- **Staff** - Can view their schedule and customers
- **Receptionist** - Can handle bookings and check-ins
- **Cashier** - Can handle billing

**Permissions:** Each role has specific permissions like "view dashboard", "edit staff", "create bookings"

---

### 🏬 Departments
**What it stores:** Different departments in your spa

**Examples:**
- Massage Department
- Skincare Department  
- Hair & Beauty
- Nails & Manicure
- Wellness & Yoga

---

## 📅 SCHEDULING

### 🕐 Shift Management
**What it stores:** Staff work schedules for specific date ranges

**Example:** 
- "John works from Jan 1 to Jan 31"
- Shift: 9:00 AM - 6:00 PM
- Break: 1:00 PM - 2:00 PM

### 📝 Shift Logs
**What it stores:** Daily attendance records for each staff member

**Information tracked:**
- Date of work
- Actual shift times
- Break times
- Status: Scheduled, Present, Absent, Holiday, Completed

**Example:** "Jan 15: John worked 9am-6pm with 1hr break, Status: Completed"

---

## 👨‍👩‍👧‍👦 CUSTOMERS

### 🧑 Customer Records
**What it stores:** All customer information

**Personal Details:**
- Name, phone, email, address
- Date of birth, gender
- Emergency contact

**Visit History:**
- Total visits
- Total money spent
- Last visit date
- Favorite services

**Preferences:**
- Allergies (e.g., "allergic to lavender")
- Preferences (e.g., "prefers soft pressure massage")
- Communication preference (email, SMS, WhatsApp)

**Loyalty Program:**
- VIP status
- Loyalty points
- Referral source (how they found you)

**Example:** "Emma Wilson, visited 15 times, spent $1,500, VIP customer, prefers aromatherapy"

---

## 💆 SERVICES

### 🛎️ Service Catalog
**What it stores:** All services you offer

**For each service:**
- Name (e.g., "Swedish Massage")
- Description
- Duration (e.g., 60 minutes)
- Price (e.g., $80)
- Category (Massage, Facial, etc.)
- Active/Inactive status

**Example:** "Hot Stone Massage - 90 minutes - $120 - Active"

### 📂 Service Categories
**What it stores:** Groups services together

**Examples:**
- 💆 Massage Services (Blue)
- 🧖 Facial Services (Pink)
- 💇 Hair Services (Purple)
- 💅 Nail Services (Red)

---

## 📆 APPOINTMENTS & BOOKINGS

### 📋 Regular Appointments
**What it stores:** Standard appointment bookings

**Information:**
- Customer name
- Service requested
- Staff member assigned
- Date and time
- Status (Scheduled, Confirmed, In Progress, Completed, Cancelled)
- Payment status
- Notes

**Example:** "Emma Wilson - Swedish Massage with Sarah - Jan 20 at 2pm - Confirmed - $80 paid"

### 🗓️ Unaki Bookings
**What it stores:** Advanced appointment system with drag-and-drop scheduling

**Additional features:**
- Visual timeline booking
- Multiple booking sources (phone, walk-in, online)
- Real-time staff availability
- Break time management
- Consecutive booking support

---

## 🎁 PACKAGES & MEMBERSHIPS

### 💳 Prepaid Packages
**What it stores:** "Pay X, Get Y" packages

**Example:** 
- Package: "Pay $500, Get $600 credit"
- Customer pays: $500
- They get: $600 to spend
- Savings: $100
- Valid for: 6 months

### 🎫 Service Packages
**What it stores:** "Buy X services, get Y total" deals

**Example:**
- Package: "Buy 5 massages, get 7 total"
- Customer pays for: 5 massages ($400)
- They get: 7 massage sessions
- Free sessions: 2
- Valid for: 3 months

### 👑 Memberships
**What it stores:** Annual membership programs

**Example:**
- Gold Membership: $1,200/year
- Includes: Unlimited basic facials + 20% off all services
- Valid: 12 months

### 🎓 Student Offers
**What it stores:** Special discounts for students

**Example:**
- 25% off all services
- Valid: Jan 1 - Dec 31
- Requires: Valid student ID

### 🎉 Kitty Party Packages
**What it stores:** Group event packages

**Example:**
- Minimum: 8 people
- Maximum: 15 people
- $50 per person
- Includes: Mini facial + refreshments
- Valid: 6 months

### 📊 Package Tracking
**What it stores:** Customer package assignments and usage

**Tracks:**
- Which customer has which package
- When it was purchased
- How much they've used
- How much remains
- Expiry date

**Example:** "Emma has Prepaid Package, bought Jan 1, used $200, remaining $400, expires Jun 30"

---

## 💰 BILLING & PAYMENTS

### 🧾 Invoices
**What it stores:** Professional invoices for customers

**Invoice includes:**
- Invoice number (e.g., INV-2024-001)
- Customer details
- Date
- List of services/products
- Individual item prices
- Package deductions (if applicable)
- Discounts
- Taxes (CGST, SGST, IGST)
- Tips
- Total amount
- Payment status

**Example Invoice:**
```
Invoice: INV-2024-001
Customer: Emma Wilson
Date: Jan 20, 2024

Services:
- Swedish Massage (90 min) - $100
  Package Deduction: -$100 (Prepaid Package)
  Final Amount: $0

- Aromatherapy Add-on - $20
  Subtotal: $20

Tax (18%): $3.60
Tips: $5
Total: $28.60
Status: Paid (Card)
```

### 💵 Payments
**What it stores:** Multiple payment methods for one invoice

**Example:**
- Total invoice: $100
- Paid $50 by Cash
- Paid $50 by Card (ending 4321)
- Status: Fully Paid

---

## 📦 INVENTORY MANAGEMENT

### 📍 Storage Locations
**What it stores:** Where inventory is kept

**Examples:**
- Main Branch
- Downtown Warehouse
- Treatment Room 1
- Reception Storage

### 🏷️ Products
**What it stores:** All products/items you use or sell

**Examples:**
- "Lavender Massage Oil"
- "Organic Face Cream"
- "Disposable Towels"
- "Aromatherapy Candles"

### 📦 Batches
**What it stores:** Individual batches of products (with expiry dates)

**Why batches?** Different purchases of the same product may have different expiry dates

**Example:**
- Batch: "LOT-2024-001"
- Product: Lavender Oil
- Manufacturing: Jan 1, 2024
- Expiry: Jan 1, 2026
- Quantity: 50 bottles
- Location: Main Branch
- Cost: $10 per bottle

### 📝 Stock Movements
**What it stores:** Every time stock changes

**Actions tracked:**
- **Add Stock:** New purchase received
- **Remove Stock:** Product used in service
- **Transfer:** Moved between locations
- **Adjustment:** Correction/damage/expiry

**Example:** "Jan 15: Used 2 bottles of Lavender Oil for massage services, Stock before: 50, Stock after: 48"

### 🔔 Inventory Alerts
**What it stores:** Automatic warnings

**Alert types:**
- Low Stock Warning (only 5 left!)
- Out of Stock Alert
- Near Expiry Warning (expires in 30 days)
- Expired Items Alert

---

## 💼 EXPENSES

### 💸 Expense Records
**What it stores:** All business expenses

**Examples:**
- Rent payment: $2,000
- Electricity bill: $150
- Product purchase: $500
- Staff salary: $3,000
- Marketing: $200

**Categories:**
- Rent & Utilities
- Supplies & Products
- Salaries & Payroll
- Marketing & Advertising
- Maintenance & Repairs

---

## 📊 REPORTS & ANALYTICS

### 📈 Staff Performance
**What it stores:** Monthly performance metrics

**Tracks:**
- Total appointments completed
- Revenue generated
- Customer ratings
- Punctuality score
- Client satisfaction

**Example:** "Sarah - Jan 2024: 85 appointments, $6,800 revenue, 4.8/5 rating"

### ⏰ Attendance
**What it stores:** Daily staff attendance

**Records:**
- Check-in time
- Check-out time
- Status (Present, Absent, Late, Half Day)
- Notes

---

## 🌟 CUSTOMER ENGAGEMENT

### ⭐ Reviews & Ratings
**What it stores:** Customer feedback

**Example:**
- Customer: Emma Wilson
- Service: Swedish Massage
- Staff: Sarah Johnson
- Rating: 5/5 stars
- Comment: "Best massage ever! Sarah was amazing!"
- Date: Jan 20, 2024

### 💬 Communications
**What it stores:** All messages sent to customers

**Types:**
- Email confirmations
- SMS reminders
- WhatsApp messages
- Phone call logs
- In-person conversations

**Example:** "Jan 19: SMS reminder sent to Emma for tomorrow's appointment"

### ⏳ Waitlist
**What it stores:** Customers waiting for fully booked slots

**Example:** "David wants Swedish Massage on Jan 25 at 3pm, added to waitlist"

---

## 🔄 RECURRING APPOINTMENTS

### 🔁 Recurring Bookings
**What it stores:** Automatic repeat appointments

**Example:**
- Customer: Emma Wilson
- Service: Facial
- Frequency: Every 2 weeks
- Day: Saturdays at 2pm
- Start: Jan 1, 2024
- End: Dec 31, 2024
- Status: Active

---

## 🎯 HOW EVERYTHING CONNECTS

### Example Customer Journey:

1. **New Customer** → Saved in **Customer** table
2. **Books Appointment** → Saved in **Appointments** table
3. **Buys Package** → Saved in **Package Assignment** table
4. **Uses Package** → Tracked in **Package Usage** table
5. **Service Completed** → **Invoice** created
6. **Payment Made** → Saved in **Payments** table
7. **Leaves Review** → Saved in **Reviews** table
8. **Inventory Used** → Updated in **Inventory** tables

---

## 📌 KEY CONCEPTS

### 🔐 Security
- All passwords are encrypted
- Facial recognition for staff check-in
- Role-based access control
- Audit logs for all changes

### 💾 Data Integrity
- Every action is logged
- Can't delete used records (marked inactive instead)
- Package usage prevents double-charging
- Stock movements are tracked and auditable

### 🔄 Automation
- Automatic low stock alerts
- Automatic expiry warnings
- Automatic appointment reminders
- Automatic loyalty point calculations

---

## 🎓 QUICK REFERENCE

### Common Questions:

**Q: Where is customer information stored?**
A: In the **Customer** table

**Q: How do I track staff schedules?**
A: Use **Shift Management** and **Shift Logs** tables

**Q: Where are invoices stored?**
A: In the **Enhanced Invoice** table with line items in **Invoice Item** table

**Q: How does package tracking work?**
A: **Package Assignment** → assigns package to customer
   **Package Benefit Tracker** → tracks available benefits
   **Package Usage History** → records each use

**Q: Where is inventory tracked?**
A: **Products** → what items you have
   **Batches** → specific stock with expiry dates
   **Audit Log** → every stock movement

---

## 📞 Support

For technical questions about the database, refer to:
- `models.py` - Main database models
- `modules/inventory/models.py` - Inventory-specific models
- `replit.md` - Project documentation

**Database Type:** SQLite (development), PostgreSQL (production)
**Total Tables:** 50+
**Framework:** Flask + SQLAlchemy

---

*Last Updated: October 3, 2025*
