
# GST Calculation Guide - Complete System Overview

## 📋 GST Application Rules

### **Package Assignment (assign_packages_routes.py)**

| Package Type | GST Applied | Rate | Calculation |
|-------------|------------|------|-------------|
| **Service Package** | ✅ YES | 18% (9% CGST + 9% SGST) | Applied on net amount (after discount) |
| **Prepaid Package** | ❌ NO | 0% | Price is final |
| **Membership** | ❌ NO | 0% | Price is final |
| **Student Offer** | ❌ NO | 0% | Price is final |
| **Yearly Membership** | ❌ NO | 0% | Price is final |
| **Kitty Party** | ❌ NO | 0% | Price is final |

### **Billing System (integrated_billing_views.py)**

| Item Type | GST Treatment | Rate | Calculation |
|-----------|--------------|------|-------------|
| **Services** | GST INCLUSIVE | 18% | Extract GST from price: `base = price / 1.18` |
| **Products** | NO GST | 0% | MRP is final (GST already in MRP) |

---

## 🧮 Calculation Examples

### **Example 1: Service Package Assignment**

**Input:**
- Service: Facial (₹1000 per session)
- Package: Pay for 5, Get 2 Free (7 total sessions)
- Discount from 2 free sessions: ₹2000

**Calculation:**
```
Subtotal (5 paid sessions)     = ₹5,000
Discount (2 free sessions)      = ₹2,000
Net Amount                      = ₹3,000
GST @ 18%                       = ₹540
  - CGST (9%)                   = ₹270
  - SGST (9%)                   = ₹270
GRAND TOTAL                     = ₹3,540
```

### **Example 2: Prepaid Package Assignment**

**Input:**
- Prepaid Package: ₹10,000 credit
- Customer pays: ₹10,000

**Calculation:**
```
Package Price                   = ₹10,000
GST                            = ₹0 (NO GST)
GRAND TOTAL                     = ₹10,000
```

### **Example 3: Billing Invoice (Service + Product)**

**Input:**
- Service: Massage (₹2,000 - GST inclusive)
- Product: Face Cream (MRP ₹500)

**Calculation:**
```
SERVICE CALCULATION:
Price (inclusive)               = ₹2,000
Base Amount                     = ₹2,000 / 1.18 = ₹1,694.92
GST Amount                      = ₹305.08
  - CGST (9%)                   = ₹152.54
  - SGST (9%)                   = ₹152.54

PRODUCT CALCULATION:
MRP (final price)               = ₹500
GST                            = ₹0 (already in MRP)

INVOICE TOTAL:
Services Subtotal               = ₹1,694.92
Products Subtotal               = ₹500.00
Total Tax (from services only)  = ₹305.08
GRAND TOTAL                     = ₹2,500.00
```

---

## 📊 Frontend Display Rules

### **Package Assignment Modal**
```javascript
// Service Package: Show GST breakdown
Subtotal:     ₹3,000
Discount:     ₹2,000
Net Price:    ₹3,000
GST (18%):    ₹540
Grand Total:  ₹3,540

// Other Packages: No GST
Price:        ₹10,000
Grand Total:  ₹10,000 (No GST)
```

### **Billing Invoice**
```javascript
Services:     ₹1,694.92 (base)
Products:     ₹500.00 (MRP)
CGST (9%):    ₹152.54
SGST (9%):    ₹152.54
Grand Total:  ₹2,500.00
```

---

## 🔧 Implementation Details

### **Backend (Python)**

**Service Package GST:**
```python
if package_type == 'service_package':
    tax_rate = 0.18
    tax_amount = taxable_amount * tax_rate
    cgst_amount = tax_amount / 2  # 9%
    sgst_amount = tax_amount / 2  # 9%
    grand_total = taxable_amount + tax_amount
else:
    # No GST for other packages
    tax_amount = 0
    grand_total = taxable_amount
```

**Billing GST (Services - Inclusive):**
```python
if total_gst_rate > 0:
    service_base_amount = services_subtotal / (1 + total_gst_rate)
    service_gst_amount = services_subtotal - service_base_amount
else:
    service_base_amount = services_subtotal
    service_gst_amount = 0
```

### **Frontend (JavaScript)**

**Service Package:**
```javascript
if (packageType === 'service_package') {
    const tax = netPrice * 0.18;  // 18% GST
    const grandTotal = netPrice + tax;
} else {
    const tax = 0;  // No GST
    const grandTotal = netPrice;
}
```

**Billing:**
```javascript
// Services: Extract GST (inclusive)
const serviceBase = servicesSubtotal / 1.18;
const serviceGst = servicesSubtotal - serviceBase;

// Products: No GST calculation
const productBase = productsSubtotal;
const productGst = 0;
```

---

## ✅ Validation Checklist

- [ ] Service packages apply 18% GST on net amount
- [ ] Other packages have NO GST (price is final)
- [ ] Billing services extract GST (inclusive pricing)
- [ ] Billing products use MRP (no GST calculation)
- [ ] CGST and SGST split equally (9% each)
- [ ] Frontend matches backend calculations
- [ ] Receipt/invoice shows correct GST breakdown
- [ ] Package assignment receipt shows GST for service packages only

---

## 🚨 Common Pitfalls

1. **Don't add GST to prepaid/membership packages** - Price is final
2. **Services in billing are GST INCLUSIVE** - Extract, don't add
3. **Products use MRP** - No GST calculation needed
4. **Service packages are GST EXCLUSIVE** - Add 18% to net price
5. **Always split GST equally** - 9% CGST + 9% SGST

---

## 📝 Testing Scenarios

### Test 1: Service Package Assignment
- Create service package with 5 paid + 2 free sessions
- Verify 18% GST is added to net price
- Check receipt shows CGST and SGST breakdown

### Test 2: Prepaid Package Assignment
- Create prepaid package worth ₹10,000
- Verify NO GST is added
- Check receipt shows final price only

### Test 3: Mixed Billing Invoice
- Add 1 service + 1 product
- Verify service has GST extracted (inclusive)
- Verify product has no GST calculation
- Check total matches expected amount
