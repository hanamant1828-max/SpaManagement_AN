# Face Recognition Check-In - Testing Guide

## Login Credentials
- **Admin User**: admin@spa.com (check with system admin for password)
- **Alternative**: Use any staff email from the user table

## Test Scenarios

### ✅ Scenario 1: Successful Login and Access
1. Navigate to login page
2. Enter valid credentials
3. Navigate to Check-In page
4. **Expected**: Page loads successfully with camera controls

### ✅ Scenario 2: Face Recognition - Happy Path
1. Login to the application
2. Navigate to Client Check-In page
3. Click "Start Recognition" button
4. **Expected**: 
   - Blue circular overlay appears on camera feed (6px thick, with glow effect)
   - Camera activates and shows live video feed
   - Circle pulses with animation while scanning
5. Position face in the circle
6. **Expected**:
   - Circle turns GREEN when face recognized (3 seconds display)
   - Customer info card appears on right side
   - "Go to Billing" button becomes available
   - Camera stops after 3 seconds
   - Customer info remains visible for 10 minutes

### ✅ Scenario 3: No Face Match Found
1. Login and start face recognition
2. Position face in circle (customer not in database)
3. **Expected**:
   - Circle briefly flashes RED
   - Returns to BLUE scanning mode
   - Status shows attempt count: "Face detection attempt X. Please ensure your face is clearly visible"
   - Continues scanning automatically

### ❌ Scenario 4: Not Logged In (Access Denied)
1. Navigate directly to /checkin without logging in
2. Click "Start Recognition"
3. **Expected**:
   - Redirected to login page with warning: "Please log in to access this page"
   - If camera starts, API returns: "Please log in to access this feature"
   - Recognition automatically stops
   - Clear message: "Authentication Required - Your session may have expired. Please refresh and log in again"

### ❌ Scenario 5: Camera Permission Denied
1. Login to application
2. Navigate to Check-In page
3. Click "Start Recognition"
4. Deny camera permission in browser popup
5. **Expected**:
   - Error message: "Camera Error: Please allow camera access and try again"
   - Camera placeholder remains visible
   - Start button remains enabled for retry

### ❌ Scenario 6: No Camera Available
1. Login on device without camera
2. Navigate to Check-In and click "Start Recognition"
3. **Expected**:
   - Error message: "Camera Error: No camera found on this device"
   - Start button remains enabled

### ❌ Scenario 7: Camera In Use by Another App
1. Open camera in another application
2. Login and try to start face recognition
3. **Expected**:
   - Error message: "Camera Error: Camera is already in use by another application"
   - Clear instructions to close other apps

### ❌ Scenario 8: Network/Connection Error
1. Login and start face recognition
2. Disconnect internet during recognition
3. **Expected**:
   - Circle turns RED
   - Error: "Connection Error: Unable to connect to face recognition service"
   - Instructions: "Please check your internet connection and try again"

## Visual Indicators

### Circle Overlay Colors:
- **Blue (#667eea)** - Scanning/Searching for faces
- **Green (#28a745)** - Face successfully recognized
- **Red (#dc3545)** - Error or no match found
- **Yellow (#ffc107)** - Warning (duplicate faces detected)

### Circle Properties:
- Border: 6px solid
- Size: 280px × 280px
- Glow effect when active
- Animation: Pulse effect while scanning
- Z-index: 100 (always on top)

## Error Messages - User Friendly

### Authentication Errors:
✅ "Your session may have expired. Please refresh the page and log in again."

### Camera Errors:
✅ "Please allow camera access and try again"
✅ "No camera found on this device"
✅ "Camera is already in use by another application"

### Network Errors:
✅ "Unable to connect to face recognition service. Please check your internet connection"

### Recognition Errors:
✅ "Face detection attempt X. Please ensure your face is clearly visible in the circle"
✅ "No registered faces in database"

## Known Issues Fixed:
1. ✅ Circle overlay not visible - Fixed with explicit inline styles
2. ✅ Access denied on API calls - Fixed unauthorized handler for JSON requests
3. ✅ Green circle disappearing too fast - Extended to 3 seconds
4. ✅ Border color not applying - Changed from borderColor to full border property

## How to Test Face Recognition:

1. **Login**: Use admin@spa.com or any valid staff account
2. **Navigate**: Go to "Client Check-In" from main menu
3. **Start Camera**: Click green "Start Recognition" button
4. **Grant Permission**: Allow camera access when browser prompts
5. **Position Face**: Center your face in the blue circle
6. **Wait for Recognition**: Circle will turn green if recognized, red if not
7. **View Results**: Customer info appears on right, billing button available

## Default Password (if needed):
- Check with system administrator
- Or use password reset functionality
- Common test password: "password" or "admin123" (verify with admin)
