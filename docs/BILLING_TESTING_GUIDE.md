
# Billing System Manual Testing Guide

## 🧪 Step-by-Step Testing Instructions

### Test 1: Access Billing System
1. **Action**: Navigate to `/integrated-billing`
2. **Expected**: Page loads with billing dashboard
3. **Check**: 
   - Form loads correctly
   - Customer dropdown populated
   - Services dropdown populated
   - No JavaScript errors in console (F12)

### Test 2: Create Service Invoice
1. **Action**: Select a customer from dropdown
2. **Expected**: Customer packages section updates
3. **Action**: Select a service and quantity
4. **Expected**: Tax calculations update automatically
5. **Action**: Click "Generate Professional Invoice"
6. **Expected**: Invoice creation success message
7. **Check**: Invoice number generated correctly

### Test 3: View Invoice
1. **Action**: Click "View Invoice" from success modal
2. **Expected**: Invoice detail page loads
3. **Check**: 
   - All invoice details displayed
   - Tax breakdown shown correctly
   - Action buttons present (Print, Email, etc.)

### Test 4: Print Invoice
1. **Action**: Click "Print Invoice" button
2. **Expected**: Professional invoice opens in new tab
3. **Check**: 
   - GST details shown correctly
   - Company information present
   - Terms and conditions included

### Test 5: Create Product Invoice
1. **Action**: Go back to billing page
2. **Action**: Select customer and product
3. **Expected**: Batch dropdown loads for product
4. **Action**: Select batch and quantity
5. **Expected**: Price auto-fills, stock validation works
6. **Action**: Create invoice
7. **Expected**: Stock reduced from selected batch

### Test 6: Mixed Invoice (Service + Product)
1. **Action**: Create invoice with both service and product
2. **Expected**: Both items appear in invoice
3. **Check**: Separate subtotals for services and inventory

### Test 7: Tax Calculations
1. **Action**: Toggle between Intrastate/Interstate
2. **Expected**: Tax fields switch between CGST+SGST / IGST
3. **Action**: Change discount type and value
4. **Expected**: Calculations update automatically
5. **Action**: Add additional charges and tips
6. **Expected**: Total amount updates correctly

### Test 8: Payment Processing
1. **Action**: Open an unpaid invoice
2. **Action**: Click "Process Payment"
3. **Action**: Enter payment details
4. **Expected**: Payment recorded, balance updated

### Test 9: Error Handling
1. **Action**: Try to create invoice without customer
2. **Expected**: Error message shown
3. **Action**: Try to use more stock than available
4. **Expected**: Stock validation prevents submission

### Test 10: Navigation
1. **Action**: Test all navigation buttons
2. **Expected**: All links work correctly
3. **Check**: Back buttons, modal closures, page redirects

## 🔍 What to Look For

### UI Elements
- [ ] All buttons responsive
- [ ] Dropdowns populated correctly
- [ ] Form validation working
- [ ] Modal windows open/close properly
- [ ] Tables display data correctly

### Functionality
- [ ] Invoice creation successful
- [ ] Tax calculations accurate
- [ ] Stock deduction working
- [ ] Payment processing functional
- [ ] Print functionality working

### Data Integrity
- [ ] Customer data displayed correctly
- [ ] Service prices accurate
- [ ] Product stock updated
- [ ] Invoice numbers sequential
- [ ] Payment records created

## 🚨 Common Issues to Check

1. **Template Not Found**: Missing HTML templates
2. **Empty Dropdowns**: Database not populated
3. **JavaScript Errors**: Check browser console
4. **Calculation Errors**: Tax or total amount wrong
5. **Stock Issues**: Inventory not reducing
6. **Database Errors**: Check server logs

## 📝 Test Results Template

```
Test Date: ___________
Tester: ___________

Test 1 - Billing Page Load: ✅ PASS / ❌ FAIL
Test 2 - Service Invoice: ✅ PASS / ❌ FAIL
Test 3 - View Invoice: ✅ PASS / ❌ FAIL
Test 4 - Print Invoice: ✅ PASS / ❌ FAIL
Test 5 - Product Invoice: ✅ PASS / ❌ FAIL
Test 6 - Mixed Invoice: ✅ PASS / ❌ FAIL
Test 7 - Tax Calculations: ✅ PASS / ❌ FAIL
Test 8 - Payment Processing: ✅ PASS / ❌ FAIL
Test 9 - Error Handling: ✅ PASS / ❌ FAIL
Test 10 - Navigation: ✅ PASS / ❌ FAIL

Overall Result: ✅ PASS / ❌ FAIL
Notes: ___________
```

## 🔧 Quick Fixes

If tests fail:
1. Check server logs for errors
2. Verify database has test data
3. Run `python test_billing_ui_comprehensive.py`
4. Clear browser cache and try again
5. Check if all required templates exist
