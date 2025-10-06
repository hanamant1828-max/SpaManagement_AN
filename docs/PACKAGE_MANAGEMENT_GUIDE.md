
# 📦 Package Management & Pay-Assign System

## Table of Contents
1. [Overview](#overview)
2. [Package Types](#package-types)
3. [Creating Packages](#creating-packages)
4. [Assigning Packages](#assigning-packages)
5. [Using Packages in Billing](#using-packages-in-billing)
6. [Database Schema](#database-schema)
7. [API Endpoints](#api-endpoints)

---

## Overview

The Package Management system allows you to create and manage subscription packages for your spa. Customers can purchase packages and use them during billing to receive benefits (free sessions, discounts, or credit).

**Key Features:**
- 6 package types (Prepaid, Service, Membership, Student Offer, Yearly, Kitty Party)
- Integrated with billing system
- Automatic benefit calculation
- Package assignment with payment collection
- Real-time balance tracking

---

## Package Types

### 1. Prepaid Packages (Credit-based)
**Use Case:** Customer loads money in advance

**Template Fields:**
- `actual_price`: Amount customer pays (e.g., ₹15,000)
- `after_value`: Credit customer receives (e.g., ₹17,500)
- `benefit_percent`: Bonus percentage (calculated: 16.67%)
- `validity_months`: How long credit is valid

**Assignment Fields:**
- `customer_id`: Which customer
- `price_paid`: Actual amount paid
- `credit_amount`: Total credit (from template)
- `remaining_credit`: Decreases with each use
- `used_credit`: Track how much spent

**Billing Integration:**
- Service price is deducted from `remaining_credit`
- No cash payment needed if sufficient credit
- Overage is charged separately

---

### 2. Service Packages (Session-based)
**Use Case:** Buy X sessions, get Y total (with free sessions)

**Template Fields:**
- `name`: "3+1 Package"
- `pay_for`: Sessions customer pays for (3)
- `total_services`: Total sessions customer gets (4)
- `free_sessions`: Bonus sessions (1)
- `benefit_percent`: Calculated (33.33%)
- `validity_months`: Package expiry

**Assignment Fields:**
- `customer_id`: Which customer
- `service_id`: **REQUIRED** - Which service this package covers
- `total_sessions`: From template (4)
- `remaining_sessions`: Decreases with use (starts at 4)
- `used_sessions`: Track consumption

**Billing Integration:**
- When service matches `service_id` AND `remaining_sessions > 0`
- Price is marked as ₹0 (FREE)
- `remaining_sessions` decrements by quantity
- If no sessions left, charge full price

**CRITICAL:** Service must be selected during assignment, NOT during template creation!

---

### 3. Memberships
**Use Case:** Unlimited access to specific services

**Template Fields:**
- `name`: "Gold Membership"
- `price`: ₹50,000
- `validity_months`: 12
- `services_included`: Text description or linked services

**Assignment:**
- Customer pays membership fee
- Gets unlimited access to included services

**Billing Integration:**
- Check if service is in membership
- If yes, price = ₹0 (FREE)
- If no, charge full price

---

### 4. Student Offers
**Use Case:** Discount for students

**Template Fields:**
- `discount_percentage`: 20%
- `valid_from`: Start date
- `valid_to`: End date
- `valid_days`: "Mon-Fri"
- `conditions`: "Valid with Student ID"

**Billing Integration:**
- Apply discount percentage to service price
- Only on valid dates and days

---

### 5. Yearly Memberships
**Use Case:** Annual subscription with extra benefits

**Template Fields:**
- `price`: ₹1,00,000
- `discount_percent`: 15%
- `validity_months`: 12
- `extra_benefits`: "Free spa session on birthday"

---

### 6. Kitty Party Packages
**Use Case:** Group events

**Template Fields:**
- `price`: ₹20,000
- `after_value`: ₹25,000
- `min_guests`: 10
- `services_included`: List of services

---

## Creating Packages

### Step 1: Navigate to Package Management
**URL:** `/packages`

### Step 2: Select Package Type Tab
- Click on the tab for the package type you want to create

### Step 3: Fill Template Form

**Prepaid Package Example:**
```
Name: "Prepaid ₹15,000"
Actual Price: 15000
After Value: 17500
Benefit %: 16.67 (auto-calculated)
Validity: 60 days
```

**Service Package Example:**
```
Name: "3+1 Facial Package"
Pay For: 3
Total Services: 4
Free Services: 1 (auto-calculated)
Benefit %: 33.33 (auto-calculated)
Validity: 3 months
```

**IMPORTANT:** For Service Packages, do NOT select a service in the template. Service is chosen during assignment!

### Step 4: Save Template
- Click "Create Package"
- Template is now available for assignment

---

## Assigning Packages

### Method 1: From Package Management Page
1. Go to `/packages`
2. Find the package in the table
3. Click **"Assign"** button
4. Fill assignment form
5. Collect payment
6. Generate receipt

### Method 2: From Assign Packages Page
**URL:** `/assign-packages`

**Step-by-Step:**
1. Select customer
2. Select package type (dropdown)
3. Select specific package
4. **For Service Packages:** Select which service this package covers
5. Set expiry date (optional - defaults to template validity)
6. Add notes (optional)
7. Enter payment details:
   - Payment method (Cash, Card, UPI, etc.)
   - Amount
   - Reference number
8. Click **"Assign & Collect Payment"**

**What Happens:**
- Package assignment is created
- Payment is recorded
- Receipt is generated (PDF)
- Package is now active for customer

---

## Using Packages in Billing

### Integrated Billing Flow
**URL:** `/integrated-billing`

### Step 1: Select Customer
- Dropdown shows all customers
- Upon selection, **Active Packages** table loads automatically

### Step 2: View Active Packages
The table shows:
- Package name
- Type (Prepaid, Service, etc.)
- Balance (sessions or credit remaining)
- Expiry date
- Status

**Example:**
```
Package: 3+1 Facial Package
Type: Service Package
Service: Hydrating Facial
Balance: 4/4 sessions (100% remaining)
Expiry: 2025-10-31
Status: Active
```

### Step 3: Add Services
- Click "Add Service"
- Select service from dropdown
- **Automatic Benefit Check:**
  - System checks if selected service matches any active package
  - If match found AND balance > 0:
    - Price is set to ₹0 (FREE)
    - Green badge shows "Package Applied: [Name]"
  - If no match or balance = 0:
    - Normal price applies

### Step 4: Review Summary Panel
**Right side panel shows:**
```
Package Subtotal: ₹0.00 (free from package)
Services Subtotal: ₹1,200.00
Products Subtotal: ₹500.00
──────────────────────────
Subtotal: ₹1,700.00
Discount: -₹100.00
CGST (9%): ₹144.00
SGST (9%): ₹144.00
──────────────────────────
GRAND TOTAL: ₹1,888.00
```

### Step 5: Submit Invoice
- Select payment method
- Click "Generate Invoice"
- **Backend Processing:**
  - Creates invoice
  - Deducts package balance
  - Records usage
  - Generates PDF receipt

---

## Database Schema

### Core Tables

#### 1. `service_package_assignment`
Stores all package assignments (all types)

**Key Columns:**
```sql
id                      INTEGER PRIMARY KEY
customer_id             INTEGER (FK to client.id)
package_type            VARCHAR (prepaid, service_package, membership, etc.)
package_reference_id    INTEGER (FK to specific package table)
service_id              INTEGER (for service packages - which service)
assigned_on             DATETIME
expires_on              DATETIME
price_paid              DECIMAL(10,2)
discount                DECIMAL(10,2)
status                  VARCHAR (active, completed, expired, paused)

-- Service Package Tracking
total_sessions          INTEGER
remaining_sessions      INTEGER
used_sessions           INTEGER

-- Prepaid Tracking
credit_amount           DECIMAL(10,2)
remaining_credit        DECIMAL(10,2)
used_credit             DECIMAL(10,2)
```

#### 2. `package_benefit_tracker`
**CRITICAL FOR BILLING INTEGRATION**

```sql
id                      INTEGER PRIMARY KEY
customer_id             INTEGER
package_assignment_id   INTEGER (FK to service_package_assignment)
service_id              INTEGER (which service gets the benefit)
benefit_type            VARCHAR (free, discount, prepaid, unlimited)

-- Balance Tracking
total_allocated         INTEGER (for sessions)
used_count              INTEGER
remaining_count         INTEGER

balance_total           DECIMAL(10,2) (for credit)
balance_used            DECIMAL(10,2)
balance_remaining       DECIMAL(10,2)

discount_percentage     DECIMAL(5,2) (for discount-based)

valid_from              DATETIME
valid_to                DATETIME
is_active               BOOLEAN
```

**This table enables:**
- Fast lookup during billing (by customer_id + service_id)
- Automatic benefit application
- Real-time balance checking

---

## API Endpoints

### Package Management

#### Get All Packages by Type
```
GET /api/prepaid-packages
GET /api/service-packages
GET /api/memberships
GET /api/student-offers
GET /api/yearly-memberships
GET /api/kitty-parties
```

**Response:**
```json
{
  "success": true,
  "packages": [
    {
      "id": 1,
      "name": "3+1 Package",
      "pay_for": 3,
      "total_services": 4,
      "benefit_percent": 33.33,
      "validity_months": 3
    }
  ]
}
```

#### Create Package
```
POST /api/service-packages
Content-Type: application/json

{
  "name": "3+1 Package",
  "pay_for": 3,
  "total_services": 4,
  "validity_months": 3
}
```

### Package Assignment

#### Assign Package with Payment
```
POST /packages/api/assign-and-pay
Content-Type: application/json

{
  "assignment": {
    "customer_id": 23,
    "package_type": "service_package",
    "package_id": 1,
    "service_id": 10,
    "price_paid": 1200.00,
    "discount": 0,
    "expires_on": "2025-10-31",
    "notes": "Birthday gift"
  },
  "payment": {
    "collect": true,
    "method": "cash",
    "amount": 1200.00,
    "reference": ""
  },
  "invoice": {
    "create": true,
    "tax_rate": 18.0
  },
  "receipt": {
    "generate": true,
    "pdf": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "assignment_id": 27,
  "payment_id": 45,
  "receipt_id": 67,
  "receipt_number": "REC-20251005-0001",
  "receipt_url": "/receipts/67",
  "receipt_pdf_url": "/receipts/67/download"
}
```

#### Get Customer Packages
```
GET /integrated-billing/customer-packages/{customer_id}
```

**Response:**
```json
{
  "success": true,
  "packages": [
    {
      "id": 27,
      "assignment_id": 27,
      "name": "3+1",
      "package_type": "service_package",
      "service_id": 10,
      "service_name": "Hydrating Facial",
      "status": "active",
      "assigned_on": "2025-10-05T10:41:14",
      "expires_on": "2025-10-31T00:00:00",
      "sessions": {
        "total": 4,
        "used": 0,
        "remaining": 4
      },
      "credit": {
        "total": 0,
        "remaining": 0
      }
    }
  ]
}
```

---

## Troubleshooting

### Issue: Package benefit not applying in billing

**Debug Steps:**
1. Check console logs for:
   ```
   📦 Checking package: {...}
   🔍 Service package match check: {...}
   ```
2. Verify:
   - `service_id` matches between package and selected service
   - `remaining_sessions > 0`
   - Package status is `active`
   - Package is not expired

**Fix:**
- Ensure `PackageBenefitTracker` record exists
- Run: `python scripts/backfill_assignment_names.py`

### Issue: "Service package NOT applied"

**Common Causes:**
1. Service ID mismatch
2. No remaining sessions
3. Package expired
4. Missing benefit tracker record

**Solution:**
Check the assignment:
```sql
SELECT * FROM service_package_assignment WHERE id = 27;
SELECT * FROM package_benefit_tracker WHERE package_assignment_id = 27;
```

---

## Best Practices

### 1. Template Naming
Use descriptive names:
- ✅ "3+1 Facial Package"
- ✅ "Prepaid ₹15,000 (17.5K credit)"
- ❌ "Package 1"

### 2. Service Selection
**For Service Packages:**
- Template: Don't select service
- Assignment: MUST select service
- Reason: Same template can be used for different services

### 3. Expiry Management
- Set reasonable expiry dates
- Auto-update status based on expiry
- Notify customers before expiry

### 4. Balance Tracking
- Always use `PackageBenefitTracker` for billing
- Don't directly modify `remaining_sessions` in UI
- Let backend handle deductions

---

## Summary

**Package Lifecycle:**
1. **Create Template** → `/packages` → Save to database
2. **Assign to Customer** → `/assign-packages` → Collect payment
3. **Use in Billing** → `/integrated-billing` → Auto-apply benefits
4. **Track Usage** → Backend updates balances automatically
5. **Complete/Expire** → Status changes when exhausted or expired

**Key Tables:**
- Package templates (6 separate tables)
- `service_package_assignment` (unified assignments)
- `package_benefit_tracker` (billing integration)

**Integration Points:**
- Billing system checks benefits automatically
- Staff management (who performed service)
- Inventory (product sales)
- Reporting (package revenue)
