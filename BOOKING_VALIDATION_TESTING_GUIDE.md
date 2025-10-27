# Booking Acceptance Validation - Comprehensive Testing Guide

## Overview
This guide provides step-by-step instructions to test all validation scenarios for the booking acceptance system.

## Test Scenarios

### ✅ Scenario 1: Successful Booking Acceptance
**Purpose:** Verify that valid bookings can be accepted when all conditions are met

**Setup:**
1. Navigate to Online Bookings page
2. Find a pending booking that has:
   - Appointment time within staff shift hours
   - No overlap with staff's existing appointments
   - No overlap with client's existing appointments
   - Not during staff break time
   - Not during staff out-of-office period

**Steps:**
1. Click "Accept" on the booking
2. Select an available staff member from the dropdown
3. Click "Confirm Booking"

**Expected Result:**
- ✅ Success toast notification: "Successfully accepted 1 booking(s)"
- Booking status changes from "Scheduled" to "Confirmed"
- Booking appears in confirmed bookings list

---

### ❌ Scenario 2: Staff Outside Shift Hours
**Purpose:** Verify rejection when booking time is outside staff working hours

**Setup:**
1. Create or find a booking with time before staff shift starts or after shift ends
2. Example: Staff works 9:00 AM - 6:00 PM, booking is at 8:00 AM or 7:00 PM

**Steps:**
1. Click "Accept" on the booking
2. Select the staff member
3. Click "Confirm Booking"

**Expected Result:**
- ❌ Error toast notification showing:
  ```
  ❌ Cannot accept Booking #XXX (Client Name - Service Name):
  ❌ Staff Availability: Outside of shift hours (09:00 - 18:00)
  ```
- Booking remains in "Scheduled" status

---

### ❌ Scenario 3: During Staff Break Time
**Purpose:** Verify rejection when booking overlaps with staff break

**Setup:**
1. Find a booking that falls during staff break time
2. Example: Staff break is 12:00 PM - 1:00 PM, booking is at 12:30 PM

**Steps:**
1. Click "Accept" on the booking
2. Select the staff member
3. Click "Confirm Booking"

**Expected Result:**
- ❌ Error toast notification showing:
  ```
  ❌ Cannot accept Booking #XXX (Client Name - Service Name):
  ❌ Staff Availability: Staff is during break time (12:00 - 13:00)
  ```
- Booking remains in "Scheduled" status

---

### ❌ Scenario 4: Staff Out of Office
**Purpose:** Verify rejection when staff is out of office

**Setup:**
1. Set staff as out-of-office for a time period (e.g., "Meeting 2:00 PM - 3:00 PM")
2. Find a booking during that out-of-office period

**Steps:**
1. Click "Accept" on the booking
2. Select the staff member who is out of office
3. Click "Confirm Booking"

**Expected Result:**
- ❌ Error toast notification showing:
  ```
  ❌ Cannot accept Booking #XXX (Client Name - Service Name):
  ❌ Staff Availability: Staff is out of office: Meeting (14:00 - 15:00)
  ```
- Booking remains in "Scheduled" status

---

### ❌ Scenario 5: Staff Schedule Conflict
**Purpose:** Verify rejection when staff already has an appointment at that time

**Setup:**
1. Accept a booking for a staff member at a specific time (e.g., 2:00 PM - 3:00 PM)
2. Try to accept another booking for the same staff at an overlapping time (e.g., 2:30 PM - 3:30 PM)

**Steps:**
1. Click "Accept" on the second booking
2. Select the same staff member
3. Click "Confirm Booking"

**Expected Result:**
- ❌ Error toast notification showing:
  ```
  ❌ Cannot accept Booking #XXX (Client Name - Service Name):
  ❌ Staff Schedule Conflict: Staff Name already has an appointment from 02:00 PM to 03:00 PM with Client Name
  ```
- Booking remains in "Scheduled" status

---

### ❌ Scenario 6: Client Schedule Conflict
**Purpose:** Verify rejection when client already has an appointment at that time

**Setup:**
1. Accept a booking for a client at a specific time with Staff A
2. Try to accept another booking for the same client at an overlapping time with Staff B

**Steps:**
1. Click "Accept" on the second booking
2. Select a different staff member
3. Click "Confirm Booking"

**Expected Result:**
- ❌ Error toast notification showing:
  ```
  ❌ Cannot accept Booking #XXX (Client Name - Service Name):
  ❌ Client Schedule Conflict: Client Name already has an appointment from 02:00 PM to 03:00 PM with Staff Name on 2025-10-27
  ```
- Booking remains in "Scheduled" status

---

### ❌ Scenario 7: Multiple Validation Failures
**Purpose:** Verify that all validation errors are shown together

**Setup:**
1. Find a booking that violates multiple rules:
   - Outside shift hours
   - During break time
   - Staff already booked
   - Client already booked

**Steps:**
1. Click "Accept" on the booking
2. Select the staff member
3. Click "Confirm Booking"

**Expected Result:**
- ❌ Error toast notification showing multiple errors:
  ```
  ❌ Cannot accept Booking #XXX (Client Name - Service Name):
  ❌ Staff Availability: Outside of shift hours (09:00 - 18:00)
  ❌ Staff Schedule Conflict: Staff Name already has an appointment...
  ❌ Client Schedule Conflict: Client Name already has an appointment...
  ```
- Booking remains in "Scheduled" status

---

### ✅ Scenario 8: Bulk Acceptance - Mixed Results
**Purpose:** Verify that some bookings can succeed while others fail in bulk operations

**Setup:**
1. Select multiple bookings:
   - Booking A: Valid, should succeed
   - Booking B: Invalid (e.g., outside shift hours), should fail
   - Booking C: Valid, should succeed

**Steps:**
1. Select all three bookings
2. Assign staff to each
3. Click "Accept Selected"

**Expected Result:**
- ✅ Success notification: "Successfully accepted 2 booking(s)"
- ❌ Error notification: "Failed to accept 1 booking(s):"
- Detailed error for Booking B showing why it failed
- Bookings A and C are confirmed
- Booking B remains scheduled

---

## Testing Checklist

Use this checklist to track your testing progress:

- [ ] Scenario 1: Successful acceptance ✅
- [ ] Scenario 2: Outside shift hours ❌
- [ ] Scenario 3: During break time ❌
- [ ] Scenario 4: Out of office ❌
- [ ] Scenario 5: Staff conflict ❌
- [ ] Scenario 6: Client conflict ❌
- [ ] Scenario 7: Multiple failures ❌
- [ ] Scenario 8: Bulk mixed results ✅❌

## Error Message Format

All error messages follow this format:

```
❌ Cannot accept Booking #[ID] ([Client Name] - [Service Name]):
❌ [Category]: [Detailed Error Message]
```

Categories:
- **Staff Availability** - Issues with shift hours, breaks, or out-of-office
- **Staff Schedule Conflict** - Staff already has an appointment
- **Client Schedule Conflict** - Client already has an appointment

## Notes

- Error messages appear as toast notifications in the top-right corner
- Toast notifications auto-dismiss after 5 seconds
- Multiple errors are shown in separate toast notifications
- All validation happens server-side for security
- Database state is checked in real-time before accepting bookings

## Database Status

Current system state:
- Active staff members: 29
- Schedules configured: 36 (for tomorrow)
- Pending online bookings: 0

## Technical Details

### Validation Order:
1. Staff availability (shift hours, breaks, out-of-office)
2. Staff schedule conflicts (overlapping appointments)
3. Client schedule conflicts (overlapping appointments)

### Key Files:
- `modules/bookings/online_booking_queries.py` - Validation logic
- `modules/bookings/online_booking_views.py` - Route handlers and error display
- `templates/online_bookings.html` - UI with toast notifications
- `static/js/main.js` - Toast notification system
