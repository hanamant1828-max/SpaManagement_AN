// Main JavaScript functionality for Spa & Salon Management Suite

// Global application state and utilities
window.SpaApp = {
    currentUser: null,
    notifications: [],
    settings: {
        autoRefresh: true,
        refreshInterval: 30000,
        theme: 'dark'
    }
};

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    initializeBootstrapComponents();
});

function initializeApp() {
    setupGlobalEventListeners();
    initializeComponents();
    setupFormValidation();
    setupNotifications();
    loadUserPreferences();

    // Auto-refresh data if enabled
    if (SpaApp.settings.autoRefresh) {
        startAutoRefresh();
    }
}

// Global event listeners
function setupGlobalEventListeners() {
    // Handle all modal events
    document.addEventListener('show.bs.modal', handleModalShow);
    document.addEventListener('hidden.bs.modal', handleModalHidden);

    // Auto-hide mobile sidebar when clicking navigation links
    setupMobileSidebarAutoHide();

    // Initialize face capture functionality only on pages that need it
    if (window.location.pathname.includes('/staff') || window.location.pathname.includes('/face')) {
        initializeFaceCapture();
    }

    // Handle form submissions
    document.addEventListener('submit', handleFormSubmit);

    // Specifically handle edit customer form
    const editCustomerForm = document.getElementById('editCustomerForm');
    if (editCustomerForm) {
        editCustomerForm.addEventListener('submit', handleEditCustomerSubmit);
    }

    // Handle button clicks
    document.addEventListener('click', handleButtonClick);

    // Handle input changes
    document.addEventListener('change', handleInputChange);

    // Handle keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);

    // Handle window resize
    window.addEventListener('resize', handleWindowResize);

    // Handle connection status
    window.addEventListener('online', handleOnlineStatus);
    window.addEventListener('offline', handleOfflineStatus);

    // Setup right-click context menu
    setupContextMenu();
}

// Face Capture Functionality - only initialize when needed
function initializeFaceCapture() {
    console.log('Initializing face capture functionality...');

    // Initialize camera buttons when page loads
    setupCameraButtons();
    
    // Also set up event listeners for tab switching
    document.addEventListener('shown.bs.tab', function(event) {
        if (event.target.getAttribute('data-bs-target') === '#face-capture') {
            console.log('Face capture tab activated, setting up camera buttons...');
            setTimeout(setupCameraButtons, 100); // Small delay to ensure DOM is ready
        }
    });
}

let currentStream = null;
let faceStream = null;

// Declare currentStaffId only once globally
// currentStaffId moved to specific modules to avoid conflicts

function setupCameraButtons() {
    // Only run on pages that actually have camera buttons
    if (!document.getElementById('startCameraBtn') && 
        !document.getElementById('startRecognitionBtn') && 
        !document.getElementById('startFaceCamera')) {
        return; // No camera buttons found, skip setup
    }
    
    console.log('Setting up camera buttons...');
    
    // Wait for DOM to be ready
    setTimeout(() => {
        // Setup face management camera buttons
        const startCameraBtn = document.getElementById('startCameraBtn');
        const startRecognitionBtn = document.getElementById('startRecognitionBtn');
        const startFaceCameraBtn = document.getElementById('startFaceCamera');

        if (startCameraBtn) {
            startCameraBtn.addEventListener('click', function() {
                console.log('Start camera button clicked');
                if (typeof startFaceCameraForTab === 'function') {
                    startFaceCameraForTab();
                } else if (typeof startFaceCamera === 'function') {
                    startFaceCamera('faceVideo', 'faceCaptureArea');
                } else {
                    console.error('No face camera function available');
                }
            });
        }

        if (startRecognitionBtn) {
            startRecognitionBtn.addEventListener('click', function() {
                startFaceCamera('recognitionVideo', 'recognitionCaptureArea');
            });
        }

        if (startFaceCameraBtn) {
            startFaceCameraBtn.addEventListener('click', function() {
                console.log('Start face camera button clicked');
                if (typeof startFaceCameraForTab === 'function') {
                    startFaceCameraForTab();
                }
            });
        }
    }, 200);
}

// New function specifically for the face management tab
async function startFaceCameraForTab() {
    console.log('Starting face camera for tab');
    
    try {
        const video = document.getElementById('faceVideo');
        const placeholder = document.getElementById('faceCameraPlaceholder');
        const captureBtn = document.getElementById('captureFacePhoto');
        const saveBtn = document.getElementById('saveFaceData');
        const startBtn = document.getElementById('startFaceCamera');

        if (!video) {
            console.error('Face video element not found');
            alert('Camera element not found');
            return;
        }

        // Request camera access
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            }
        });

        console.log('Camera access granted for face tab');

        // Set video source and show it
        video.srcObject = stream;
        video.style.display = 'block';
        
        // Hide placeholder
        if (placeholder) {
            placeholder.style.display = 'none';
        }

        // Update button states
        if (startBtn) startBtn.style.display = 'none';
        if (captureBtn) {
            captureBtn.disabled = false;
            captureBtn.style.display = 'inline-block';
        }

        // Add capture photo event listener
        if (captureBtn) {
            captureBtn.onclick = function() {
                captureFacePhotoForTab();
            };
        }

        console.log('Face camera started successfully');

    } catch (error) {
        console.error('Error accessing camera:', error);

        let errorMessage = 'Camera access failed. ';
        if (error.name === 'NotAllowedError') {
            errorMessage += 'Please allow camera permissions and try again.';
        } else if (error.name === 'NotFoundError') {
            errorMessage += 'No camera found on this device.';
        } else {
            errorMessage += 'Please check your camera settings and try again.';
        }

        alert(errorMessage);
    }
}

// Capture photo function for face management tab
function captureFacePhotoForTab() {
    console.log('Capturing face photo for tab');
    
    const video = document.getElementById('faceVideo');
    const canvas = document.getElementById('faceCanvas');
    const saveBtn = document.getElementById('saveFaceData');
    
    if (!video || !canvas) {
        alert('Video or canvas element not found');
        return;
    }
    
    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Get canvas context and draw video frame
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Show canvas and enable save button
    canvas.style.display = 'block';
    video.style.display = 'none';
    
    if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.onclick = function() {
            saveFaceDataForTab();
        };
    }
    
    console.log('Photo captured successfully');
}

// Save face data function for face management tab
function saveFaceDataForTab() {
    console.log('Saving face data for tab');
    
    const clientSelect = document.getElementById('faceClientSelect');
    const canvas = document.getElementById('faceCanvas');
    
    if (!clientSelect || !clientSelect.value) {
        alert('Please select a customer first');
        return;
    }
    
    if (!canvas) {
        alert('No photo captured');
        return;
    }
    
    // Get image data from canvas
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    
    // Send to server
    fetch('/api/save_face', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            client_id: clientSelect.value,
            face_image: imageData
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Face data saved successfully for ' + data.client_name);
            // Reset the interface
            resetFaceInterface();
        } else {
            alert('Error saving face data: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error saving face data. Please try again.');
    });
}

// Reset face interface after saving
function resetFaceInterface() {
    const video = document.getElementById('faceVideo');
    const canvas = document.getElementById('faceCanvas');
    const placeholder = document.getElementById('faceCameraPlaceholder');
    const startBtn = document.getElementById('startFaceCamera');
    const captureBtn = document.getElementById('captureFacePhoto');
    const saveBtn = document.getElementById('saveFaceData');
    
    // Stop video stream
    if (video && video.srcObject) {
        video.srcObject.getTracks().forEach(track => track.stop());
        video.srcObject = null;
    }
    
    // Reset display states
    if (video) video.style.display = 'none';
    if (canvas) canvas.style.display = 'none';
    if (placeholder) placeholder.style.display = 'flex';
    if (startBtn) startBtn.style.display = 'inline-block';
    if (captureBtn) {
        captureBtn.style.display = 'none';
        captureBtn.disabled = true;
    }
    if (saveBtn) {
        saveBtn.style.display = 'none';
        saveBtn.disabled = true;
    }
}

async function startFaceCamera(videoId, areaId) {
    console.log('Starting face camera:', videoId);

    try {
        const video = document.getElementById(videoId);
        const area = document.getElementById(areaId);

        if (!video) {
            console.error('Video element not found:', videoId);
            alert('Camera element not found');
            return;
        }

        // Request camera access
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            }
        });

        console.log('Camera access granted');

        // Store stream reference
        if (videoId === 'video') {
            currentStream = stream;
        } else {
            faceStream = stream;
        }

        // Set video source and show it
        video.srcObject = stream;
        video.style.display = 'block';

        // Hide placeholder and show controls
        const prompt = document.getElementById(videoId === 'video' ? 'capturePrompt' : 'recognitionPrompt');
        if (prompt) {
            prompt.style.display = 'none';
        }

        if (area) {
            area.classList.add('active');
        }

        // Update button visibility
        if (videoId === 'video') {
            document.getElementById('startCameraBtn').style.display = 'none';
            document.getElementById('captureBtn').style.display = 'inline-block';
        } else {
            document.getElementById('startRecognitionBtn').style.display = 'none';
            document.getElementById('recognizeFaceBtn').style.display = 'inline-block';
        }

        console.log('Camera started successfully');

    } catch (error) {
        console.error('Error accessing camera:', error);

        let errorMessage = 'Camera access failed. ';
        if (error.name === 'NotAllowedError') {
            errorMessage += 'Please allow camera permissions and try again.';
        } else if (error.name === 'NotFoundError') {
            errorMessage += 'No camera found on this device.';
        } else {
            errorMessage += 'Please check your camera settings and try again.';
        }

        alert(errorMessage);
    }
}

async function setupFacialRecognition(staffId) {
    currentStaffId = staffId;
    const modal = new bootstrap.Modal(document.getElementById('faceRecognitionModal'));
    modal.show();

    try {
        await startCamera();
    } catch (error) {
        console.error('Camera access failed:', error);
        alert('Camera access failed. Please ensure you have granted camera permissions.');
    }
}

async function startCamera() {
    const video = document.getElementById('faceVideo');
    const captureBtn = document.getElementById('captureFaceBtn');

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: 400,
                height: 300,
                facingMode: 'user'
            }
        });

        currentStream = stream;
        video.srcObject = stream;
        video.style.display = 'block';

        if (captureBtn) {
            captureBtn.disabled = false;
            captureBtn.onclick = captureFace;
        }

        // Add close event to stop camera
        const modal = document.getElementById('faceRecognitionModal');
        if (modal) {
            modal.addEventListener('hidden.bs.modal', stopCamera);
        }

        console.log('Staff camera started successfully');

    } catch (error) {
        console.error('Error accessing camera:', error);
        throw error;
    }
}

function captureFace() {
    const video = document.getElementById('faceVideo');
    const canvas = document.getElementById('faceCanvas');
    const ctx = canvas.getContext('2d');

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Capture current video frame
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to base64
    const imageData = canvas.toDataURL('image/jpeg', 0.8);

    // Send to server
    saveFaceImage(currentStaffId, imageData);
}

function stopCamera() {
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
        currentStream = null;
    }
    if (faceStream) {
        faceStream.getTracks().forEach(track => track.stop());
        faceStream = null;
    }

    const video = document.getElementById('faceVideo');
    if (video) {
        video.srcObject = null;
        video.style.display = 'none';
    }

    // Reset all face management videos
    const videos = ['video', 'recognitionVideo'];
    videos.forEach(videoId => {
        const videoElement = document.getElementById(videoId);
        if (videoElement && videoElement.srcObject) {
            videoElement.srcObject.getTracks().forEach(track => track.stop());
            videoElement.srcObject = null;
            videoElement.style.display = 'none';
        }
    });

    console.log('All cameras stopped');
}

function stopFaceCamera(videoId) {
    const video = document.getElementById(videoId);

    if (video && video.srcObject) {
        video.srcObject.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        video.style.display = 'none';
    }

    // Reset UI
    const prompt = document.getElementById(videoId === 'video' ? 'capturePrompt' : 'recognitionPrompt');
    if (prompt) {
        prompt.style.display = 'block';
    }

    const area = document.getElementById(videoId === 'video' ? 'faceCaptureArea' : 'recognitionCaptureArea');
    if (area) {
        area.classList.remove('active');
    }

    // Reset buttons
    if (videoId === 'video') {
        document.getElementById('startCameraBtn').style.display = 'inline-block';
        document.getElementById('captureBtn').style.display = 'none';
    } else {
        document.getElementById('startRecognitionBtn').style.display = 'inline-block';
        document.getElementById('recognizeFaceBtn').style.display = 'none';
    }

    console.log('Face camera stopped for:', videoId);
}

async function saveFaceImage(staffId, imageData) {
    try {
        const response = await fetch('/staff/save-face', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                staff_id: staffId,
                face_image: imageData
            })
        });

        const result = await response.json();

        if (result.success) {
            alert('Face capture successful! Facial recognition is now enabled for this staff member.');
            stopCamera();
            bootstrap.Modal.getInstance(document.getElementById('faceRecognitionModal')).hide();
            // Refresh the staff data to show updated face status
            setTimeout(() => window.location.reload(), 1000);
        } else {
            alert('Error saving face image: ' + result.error);
        }
    } catch (error) {
        console.error('Error saving face image:', error);
        alert('Error saving face image. Please try again.');
    }
}

// Modal event handlers
function handleModalShow(event) {
    const modal = event.target;
    const modalId = modal.id;

    // Initialize modal-specific functionality
    switch(modalId) {
        case 'addAppointmentModal':
            initializeAppointmentModal(modal);
            break;
        case 'addClientModal':
            initializeClientModal(modal);
            break;
        case 'addStaffModal':
            initializeStaffModal(modal);
            break;
        case 'addInventoryModal':
            initializeInventoryModal(modal);
            break;
        case 'updateStockModal':
            initializeStockModal(modal);
            break;
        case 'editCustomerModal': // Added case for editCustomerModal
            const customerId = window.currentCustomerId; // Assume customerId is stored globally
            loadCustomerDataForEdit(customerId);
            break;
    }
}

function handleModalHidden(event) {
    const modal = event.target;

    // Clear form data and reset validation
    const forms = modal.querySelectorAll('form');
    forms.forEach(form => {
        form.reset();
        clearFormValidation(form);
    });

    // Clear customer ID after modal closes to prevent stale data
    if (modal.id === 'editCustomerModal') {
        window.currentCustomerId = null;
    }

    // Force remove any lingering backdrops to prevent UI blocking
    setTimeout(() => {
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => {
            if (backdrop.parentNode) {
                backdrop.parentNode.removeChild(backdrop);
            }
        });

        // Ensure body classes are cleaned up
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    }, 100);
}

// Form submission handler
function handleFormSubmit(event) {
    const form = event.target;
    const formId = form.id;

    // Handle specific forms that need custom submission
    switch(formId) {
        case 'appointmentForm':
            return handleAppointmentSubmit(event);
        case 'clientForm':
            return handleClientSubmit(event);
        case 'inventoryForm':
            return handleInventorySubmit(event);
        case 'editCustomerForm': // Handle edit customer form submission
            return handleEditCustomerSubmit(event);
        default:
            // For regular forms, just show loading state
            showFormLoading(form);
            break;
    }
}

// Button click handler
function handleButtonClick(event) {
    const button = event.target.closest('button');
    if (!button) return;

    const action = button.dataset.action;
    const id = button.dataset.id;

    switch(action) {
        case 'delete':
            handleDeleteAction(button, id);
            break;
        case 'toggle-status':
            handleToggleStatus(button, id);
            break;
        case 'mark-paid':
            handleMarkPaid(button, id);
            break;
        case 'send-notification':
            handleSendNotification(button, id);
            break;
        case 'export-data':
            handleExportData(button);
            break;
        case 'print':
            handlePrint(button);
            break;
        case 'edit': // Handle edit button click
            const customerIdToEdit = button.dataset.customerId;
            if (customerIdToEdit) {
                editCustomer(customerIdToEdit);
            }
            break;
        case 'book': // Handle book appointment button click
            const customerIdToBook = button.dataset.customerId;
            if (customerIdToBook) {
                bookAppointment(customerIdToBook);
            }
            break;
        case 'view': // Handle view customer button click
            const customerIdToView = button.dataset.customerId;
            if (customerIdToView) {
                viewCustomer(customerIdToView);
            }
            break;
    }
}

// Input change handler
function handleInputChange(event) {
    const input = event.target;

    // Real-time validation only on blur, not on every input change
    // Handle specific input types
    switch(input.type) {
        case 'tel':
            formatPhoneNumber(input);
            break;
        case 'email':
            // Only clear errors on input, don't validate until blur
            clearFieldError(input);
            break;
        case 'number':
            // Only clear errors on input, don't validate until blur
            clearFieldError(input);
            break;
    }

    // Handle dependent fields
    if (input.id === 'service_id') {
        handleServiceSelection(input);
    } else if (input.id === 'client_id') {
        loadClientData(input.value);
    }
}

// Email field validation for input handling
function validateEmailField(input) {
    if (input.value && !isValidEmail(input.value)) {
        showFieldError(input, 'Please enter a valid email address');
    } else {
        clearFieldError(input);
    }
}

// Initialize components
function initializeComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Initialize date pickers
    initializeDatePickers();

    // Initialize search functionality
    initializeSearch();

    // Initialize data tables
    initializeDataTables();

    // Initialize charts
    initializeCharts();
}

// Initialize Bootstrap components properly
function initializeBootstrapComponents() {
    try {
        // Wait for Bootstrap to be fully loaded
        if (typeof bootstrap === 'undefined') {
            console.warn('Bootstrap not yet loaded, retrying...');
            setTimeout(initializeBootstrapComponents, 100);
            return;
        }

        // Initialize all existing alerts with proper error handling
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            try {
                if (!bootstrap.Alert.getInstance(alert)) {
                    new bootstrap.Alert(alert);
                }
            } catch (e) {
                console.warn('Error initializing alert:', e);
            }
        });

        // Initialize offcanvas components for mobile sidebar
        const offcanvasElements = document.querySelectorAll('.offcanvas');
        offcanvasElements.forEach(offcanvasEl => {
            try {
                if (!bootstrap.Offcanvas.getInstance(offcanvasEl)) {
                    new bootstrap.Offcanvas(offcanvasEl);
                }
            } catch (e) {
                console.warn('Error initializing offcanvas:', e);
            }
        });

        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(tooltipTriggerEl => {
            try {
                if (!bootstrap.Tooltip.getInstance(tooltipTriggerEl)) {
                    new bootstrap.Tooltip(tooltipTriggerEl);
                }
            } catch (e) {
                console.warn('Error initializing tooltip:', e);
            }
        });

        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.forEach(popoverTriggerEl => {
            try {
                if (!bootstrap.Popover.getInstance(popoverTriggerEl)) {
                    new bootstrap.Popover(popoverTriggerEl);
                }
            } catch (e) {
                console.warn('Error initializing popover:', e);
            }
        });

        // Initialize dropdowns
        const dropdownTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="dropdown"]'));
        dropdownTriggerList.forEach(dropdownTriggerEl => {
            try {
                if (!bootstrap.Dropdown.getInstance(dropdownTriggerEl)) {
                    new bootstrap.Dropdown(dropdownTriggerEl);
                }
            } catch (e) {
                console.warn('Error initializing dropdown:', e);
            }
        });

        // Initialize modals
        const modalElements = document.querySelectorAll('.modal');
        modalElements.forEach(modalEl => {
            try {
                if (!bootstrap.Modal.getInstance(modalEl)) {
                    new bootstrap.Modal(modalEl);
                }
            } catch (e) {
                console.warn('Error initializing modal:', e);
            }
        });

        console.log('Bootstrap components initialized successfully');

    } catch (error) {
        console.error('Error in initializeBootstrapComponents:', error);
    }
}

// Setup auto-hide functionality for mobile sidebar
function setupMobileSidebarAutoHide() {
    // Auto-hide offcanvas sidebar when clicking nav links on mobile
    const sidebarNavLinks = document.querySelectorAll('#sidebar .nav-link');
    sidebarNavLinks.forEach(link => {
        link.addEventListener('click', function() {
            // Only auto-hide on mobile screens
            if (window.innerWidth < 992) {
                const sidebar = document.getElementById('sidebar');
                if (sidebar) {
                    const offcanvasInstance = bootstrap.Offcanvas.getOrCreateInstance(sidebar);
                    if (offcanvasInstance) {
                        // Small delay to allow navigation to start
                        setTimeout(() => {
                            offcanvasInstance.hide();
                        }, 100);
                    }
                }
            }
        });
    });
}

// Form validation
function setupFormValidation() {
    // Add validation classes to all forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.noValidate = true;
        setupFormFieldValidation(form);
    });
}

function setupFormFieldValidation(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => clearFieldError(input));
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');

    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });

    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    const required = field.hasAttribute('required');

    // Clear previous validation
    clearFieldError(field);

    // Required field validation
    if (required && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }

    if (!value) return true; // Skip validation for empty non-required fields

    // Type-specific validation
    switch(type) {
        case 'email':
            if (!isValidEmail(value)) {
                showFieldError(field, 'Please enter a valid email address');
                return false;
            }
            break;

        case 'tel':
            if (!isValidPhone(value)) {
                showFieldError(field, 'Please enter a valid phone number');
                return false;
            }
            break;

        case 'number':
            const min = parseFloat(field.min);
            const max = parseFloat(field.max);
            const numValue = parseFloat(value);

            if (isNaN(numValue)) {
                showFieldError(field, 'Please enter a valid number');
                return false;
            }

            if (!isNaN(min) && numValue < min) {
                showFieldError(field, `Value must be at least ${min}`);
                return false;
            }

            if (!isNaN(max) && numValue > max) {
                showFieldError(field, `Value must be no more than ${max}`);
                return false;
            }
            break;

        case 'date':
        case 'datetime-local':
            if (!isValidDate(value)) {
                showFieldError(field, 'Please enter a valid date');
                return false;
            }
            break;
    }

    // Custom validation rules
    if (field.dataset.validation) {
        return validateCustomRules(field, value);
    }

    return true;
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');

    // Remove existing error message
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }

    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid', 'is-valid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function clearFormValidation(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.classList.remove('is-invalid', 'is-valid');
    });

    const errorDivs = form.querySelectorAll('.invalid-feedback');
    errorDivs.forEach(div => div.remove());
}

// Validation utilities
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
}

function isValidDate(dateString) {
    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date);
}

// Numeric input validation for forms
function validateNumericInput(input) {
    const value = parseFloat(input.value);
    const min = parseFloat(input.min);
    const max = parseFloat(input.max);

    if (isNaN(value)) {
        showFieldError(input, 'Please enter a valid number');
        return false;
    }

    if (!isNaN(min) && value < min) {
        showFieldError(input, `Value must be at least ${min}`);
        return false;
    }

    if (!isNaN(max) && value > max) {
        showFieldError(input, `Value must be no more than ${max}`);
        return false;
    }

    clearFieldError(input);
    return true;
}

// Notification system
function setupNotifications() {
    createNotificationContainer();
    checkForSystemNotifications();
}

function createNotificationContainer() {
    if (!document.getElementById('notificationContainer')) {
        const container = document.createElement('div');
        container.id = 'notificationContainer';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
}

function showNotification(message, type = 'info', duration = 5000) {
    const container = document.getElementById('notificationContainer');
    const notification = document.createElement('div');

    const bgClass = {
        'success': 'bg-success',
        'error': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-info'
    }[type] || 'bg-info';

    notification.className = `toast ${bgClass} text-white`;
    notification.setAttribute('role', 'alert');
    notification.innerHTML = `
        <div class="toast-header ${bgClass} text-white border-0">
            <i class="fas fa-${getNotificationIcon(type)} me-2"></i>
            <strong class="me-auto">Notification</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;

    container.appendChild(notification);

    const toast = new bootstrap.Toast(notification, {
        delay: duration
    });

    toast.show();

    // Auto-remove after animation
    notification.addEventListener('hidden.bs.toast', () => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    });
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Modal initialization functions
function initializeAppointmentModal(modal) {
    const serviceSelect = modal.querySelector('#service_id');
    const amountInput = modal.querySelector('#amount');

    if (serviceSelect && amountInput) {
        // Clear existing options first
        serviceSelect.innerHTML = '<option value="">Select a service...</option>';

        // Show loading state
        const loadingOption = document.createElement('option');
        loadingOption.textContent = 'Loading services...';
        loadingOption.disabled = true;
        serviceSelect.appendChild(loadingOption);

        // Fetch services and populate the dropdown
        fetch('/api/services')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(services => {
                // Clear loading option
                serviceSelect.innerHTML = '<option value="">Select a service...</option>';

                console.log('Services loaded successfully:', services.length);

                if (services && services.length > 0) {
                    services.forEach(service => {
                        const option = document.createElement('option');
                        option.value = service.id;
                        option.textContent = `${service.name} ($${service.price.toFixed(2)})`;
                        option.dataset.price = service.price.toFixed(2);
                        serviceSelect.appendChild(option);
                    });

                    // Enable amount input
                    amountInput.disabled = false;

                    // Trigger change event if a service is already selected (e.g., when editing)
                    if (serviceSelect.value) {
                        handleServiceSelection(serviceSelect);
                    }

                    showNotification(`${services.length} services loaded successfully`, 'success', 3000);
                } else {
                    // Handle case where no services are found
                    const option = document.createElement('option');
                    option.textContent = 'No services available - Please add services first';
                    option.disabled = true;
                    serviceSelect.appendChild(option);
                    amountInput.value = '0.00';
                    amountInput.disabled = true;

                    showNotification('No services available. Please add services in the Services section.', 'warning', 5000);
                }
            })
            .catch(error => {
                console.error('Error fetching services:', error);
                // Clear loading option and show error
                serviceSelect.innerHTML = '<option value="">Select a service...</option>';

                const errorOption = document.createElement('option');
                errorOption.textContent = 'Error loading services - Please try again';
                errorOption.disabled = true;
                serviceSelect.appendChild(errorOption);
                amountInput.value = '0.00';
                amountInput.disabled = true;

                showNotification('Failed to load services. Please refresh and try again.', 'error');
            });

        // Listener for service selection change
        serviceSelect.addEventListener('change', function() {
            handleServiceSelection(this);
        });

        // Set default date to today
        const dateInput = modal.querySelector('#appointment_date');
        if (dateInput && !dateInput.value) {
            const now = new Date();
            const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
                .toISOString().slice(0, 16);
            dateInput.value = localDateTime;
        }
    }
}

function initializeClientModal(modal) {
    const phoneInput = modal.querySelector('input[type="tel"]');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            formatPhoneNumber(this);
        });
    }
}

function initializeStaffModal(modal) {
    const roleSelect = modal.querySelector('#role');
    const commissionInput = modal.querySelector('#commission_rate');

    if (roleSelect && commissionInput) {
        roleSelect.addEventListener('change', function() {
            if (this.value === 'cashier') {
                commissionInput.value = '0';
                commissionInput.disabled = true;
            } else {
                commissionInput.disabled = false;
            }
        });
    }
}

function initializeInventoryModal(modal) {
    const categorySelect = modal.querySelector('#category');
    const expiryInput = modal.querySelector('#expiry_date');

    if (categorySelect && expiryInput) {
        categorySelect.addEventListener('change', function() {
            if (this.value === 'equipment') {
                expiryInput.disabled = true;
                expiryInput.value = '';
            } else {
                expiryInput.disabled = false;
            }
        });
    }
}

function initializeStockModal(modal) {
    const adjustmentInput = modal.querySelector('#stockAdjustment');
    const currentStockInput = modal.querySelector('#currentStock');
    const newStockInput = modal.querySelector('#newStock');

    if (adjustmentInput && currentStockInput && newStockInput) {
        adjustmentInput.addEventListener('input', function() {
            const current = parseInt(currentStockInput.value) || 0;
            const adjustment = parseInt(this.value) || 0;
            const newStock = Math.max(0, current + adjustment);
            newStockInput.value = newStock;
        });
    }
}

// Action handlers
function handleDeleteAction(button, id) {
    const itemType = button.dataset.type || 'item';
    const confirmMessage = 'Are you sure you want to delete this ' + itemType + '? This action cannot be undone.';

    if (confirm(confirmMessage)) {
        // Show loading state
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        // In a real app, this would make an API call
        setTimeout(() => {
            button.closest('tr')?.remove();
            showNotification(itemType + ' deleted successfully', 'success');
        }, 1000);
    }
}

function handleToggleStatus(button, id) {
    const currentStatus = button.dataset.status === 'true';
    const newStatus = !currentStatus;
    const action = newStatus ? 'activate' : 'deactivate';

    if (confirm('Are you sure you want to ' + action + ' this item?')) {
        button.disabled = true;

        // Update button state
        setTimeout(() => {
            button.dataset.status = newStatus.toString();
            button.innerHTML = newStatus ?
                '<i class="fas fa-eye-slash"></i>' :
                '<i class="fas fa-eye"></i>';
            button.disabled = false;

            showNotification('Item ' + action + 'd successfully', 'success');
        }, 500);
    }
}

function handleMarkPaid(button, id) {
    if (confirm('Mark this payment as received?')) {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        setTimeout(() => {
            const row = button.closest('tr');
            if (row) {
                row.classList.add('table-success');
                button.innerHTML = '<i class="fas fa-check"></i> Paid';
                button.className = 'btn btn-sm btn-success';
            }

            showNotification('Payment marked as received', 'success');
        }, 1000);
    }
}

// Utility functions
function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');

    if (value.length >= 6) {
        value = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
    } else if (value.length >= 3) {
        value = value.replace(/(\d{3})(\d{1,3})/, '($1) $2');
    }

    input.value = value;
}

function updateServiceDependentFields(serviceSelect) {
    const selectedOption = serviceSelect.options[serviceSelect.selectedIndex];
    const amountInput = document.getElementById('amount');

    if (selectedOption && amountInput) {
        const priceMatch = selectedOption.text.match(/\$([0-9.]+)/);
        if (priceMatch) {
            amountInput.value = priceMatch[1];
        }
    }
}

function loadClientData(clientId) {
    if (!clientId) return;

    // In a real app, this would fetch client data from the server
    console.log('Loading client data for ID:', clientId);
}

// Search functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('input[type="search"], .search-input');

    searchInputs.forEach(input => {
        let searchTimeout;

        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value, this.dataset.target);
            }, 300);
        });
    });
}

function performSearch(query, target) {
    const rows = document.querySelectorAll(target + ' tbody tr');

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const matches = text.includes(query.toLowerCase());
        row.style.display = matches ? '' : 'none';
    });
}

// Data table initialization
function initializeDataTables() {
    const tables = document.querySelectorAll('.data-table');

    tables.forEach(table => {
        // Add sorting functionality
        setupTableSorting(table);

        // Add row selection
        setupRowSelection(table);
    });
}

function setupRowSelection(table) {
    const rows = table.querySelectorAll('tbody tr');

    rows.forEach(row => {
        row.addEventListener('click', function() {
            // Toggle selection
            this.classList.toggle('selected');

            // Add visual feedback
            if (this.classList.contains('selected')) {
                this.style.backgroundColor = '#e3f2fd';
            } else {
                this.style.backgroundColor = '';
            }
        });
    });
}

function setupTableSorting(table) {
    const headers = table.querySelectorAll('th[data-sortable]');

    headers.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => {
            sortTable(table, header);
        });
    });
}

function sortTable(table, header) {
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const isAscending = header.dataset.sortDirection !== 'asc';

    rows.sort((a, b) => {
        const aValue = a.children[columnIndex].textContent.trim();
        const bValue = b.children[columnIndex].textContent.trim();

        const comparison = aValue.localeCompare(bValue, undefined, { numeric: true });
        return isAscending ? comparison : -comparison;
    });

    // Update table
    const tbody = table.querySelector('tbody');
    rows.forEach(row => tbody.appendChild(row));

    // Update sort indicator
    header.dataset.sortDirection = isAscending ? 'asc' : 'desc';

    // Update header appearance
    table.querySelectorAll('th').forEach(th => {
        th.classList.remove('sorted-asc', 'sorted-desc');
    });
    header.classList.add('sorted-' + header.dataset.sortDirection);
}

// Auto-refresh functionality
function startAutoRefresh() {
    setInterval(() => {
        if (document.visibilityState === 'visible') {
            refreshPageData();
        }
    }, SpaApp.settings.refreshInterval);
}

function refreshPageData() {
    const refreshableElements = document.querySelectorAll('[data-auto-refresh]');

    refreshableElements.forEach(element => {
        // Add subtle loading indicator
        element.classList.add('refreshing');

        // Remove indicator after a short delay
        setTimeout(() => {
            element.classList.remove('refreshing');
        }, 1000);
    });
}

// Keyboard shortcuts
function handleKeyboardShortcuts(event) {
    // Only handle shortcuts when not typing in input fields
    if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
        return;
    }

    if (event.ctrlKey || event.metaKey) {
        switch(event.key) {
            case 's':
                event.preventDefault();
                saveCurrentForm();
                break;
            case 'n':
                event.preventDefault();
                openNewItemModal();
                break;
            case 'f':
                event.preventDefault();
                focusSearch();
                break;
        }
    }

    // Escape key to close modals
    if (event.key === 'Escape') {
        closeTopModal();
    }
}

function saveCurrentForm() {
    const forms = document.querySelectorAll('form:not([hidden])');
    if (forms.length > 0) {
        const lastForm = forms[forms.length - 1];
        if (validateForm(lastForm)) {
            lastForm.submit();
        }
    }
}

function openNewItemModal() {
    const addButtons = document.querySelectorAll('[data-bs-toggle="modal"]');
    if (addButtons.length > 0) {
        addButtons[0].click();
    }
}

function focusSearch() {
    const searchInput = document.querySelector('input[type="search"], .search-input');
    if (searchInput) {
        searchInput.focus();
    }
}

function closeTopModal() {
    const openModals = document.querySelectorAll('.modal.show');
    if (openModals.length > 0) {
        const topModal = openModals[openModals.length - 1];
        const modalInstance = bootstrap.Modal.getInstance(topModal);
        if (modalInstance) {
            modalInstance.hide();
        }
    }

    // Force cleanup any stuck backdrops
    setTimeout(() => {
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => {
            if (backdrop.parentNode) {
                backdrop.parentNode.removeChild(backdrop);
            }
        });
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    }, 100);
}

// Modal cleanup utility function
function forceCleanupModals() {
    // Remove all modal backdrops
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(backdrop => {
        if (backdrop.parentNode) {
            backdrop.parentNode.removeChild(backdrop);
        }
    });

    // Clean up body classes and styles
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';

    // Hide any open modals
    const openModals = document.querySelectorAll('.modal.show');
    openModals.forEach(modal => {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
            modalInstance.hide();
        }
    });
}

// Add click handler for modal close buttons
document.addEventListener('click', function(event) {
    // Handle close button clicks
    if (event.target.matches('[data-bs-dismiss="modal"]') ||
        event.target.closest('[data-bs-dismiss="modal"]')) {
        setTimeout(forceCleanupModals, 200);
    }

    // Handle backdrop clicks
    if (event.target.classList.contains('modal')) {
        setTimeout(forceCleanupModals, 200);
    }
});

// Connection status handlers
function handleOnlineStatus() {
    showNotification('Connection restored', 'success', 3000);
    document.body.classList.remove('offline');
}

function handleOfflineStatus() {
    showNotification('Connection lost. Some features may not work properly.', 'warning', 5000);
    document.body.classList.add('offline');
}

// Window resize handler
function handleWindowResize() {
    // Refresh any charts or components that need to adjust to new size
    if (window.Chart) {
        Chart.helpers.each(Chart.instances, function(instance) {
            instance.resize();
        });
    }
}

// Form loading states
function showFormLoading(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
        submitButton.dataset.originalText = originalText;
    }
}

function hideFormLoading(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton && submitButton.dataset.originalText) {
        submitButton.disabled = false;
        submitButton.innerHTML = submitButton.dataset.originalText;
        delete submitButton.dataset.originalText;
    }
}

// Date picker initialization
function initializeDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"], input[type="datetime-local"]');

    dateInputs.forEach(input => {
        // Set min date to today for future appointments
        if (input.dataset.minToday === 'true') {
            const today = new Date().toISOString().split('T')[0];
            input.min = today;
        }
    });
}

// Chart initialization
function initializeCharts() {
    // Initialize any charts present on the page
    const chartElements = document.querySelectorAll('canvas[id$="Chart"]');

    chartElements.forEach(canvas => {
        if (canvas.dataset.initialized !== 'true') {
            initializeSpecificChart(canvas);
            canvas.dataset.initialized = 'true';
        }
    });
}

function initializeSpecificChart(canvas) {
    // Chart initialization would be handled by specific page scripts
    console.log('Initializing chart:', canvas.id);
}

// Load user preferences
function loadUserPreferences() {
    const savedPreferences = localStorage.getItem('spaAppPreferences');
    if (savedPreferences) {
        try {
            const preferences = JSON.parse(savedPreferences);
            Object.assign(SpaApp.settings, preferences);
        } catch (e) {
            console.warn('Failed to load user preferences:', e);
        }
    }
}

// Save user preferences
function saveUserPreferences() {
    localStorage.setItem('spaAppPreferences', JSON.stringify(SpaApp.settings));
}

// Export functions
function exportTableData(table, filename) {
    const rows = table.querySelectorAll('tr');
    const csvContent = Array.from(rows).map(row => {
        const cells = row.querySelectorAll('th, td');
        return Array.from(cells).map(cell => {
            return '"' + cell.textContent.trim().replace(/"/g, '""') + '"';
        }).join(',');
    }).join('\n');

    downloadCSV(csvContent, filename);
}

function downloadCSV(content, filename) {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Print functionality
function printElement(element) {
    const printWindow = window.open('', '', 'width=800,height=600');
    const styles = Array.from(document.styleSheets).map(sheet => {
        try {
            return Array.from(sheet.cssRules).map(rule => rule.cssText).join('\n');
        } catch (e) {
            return '';
        }
    }).join('\n');

    printWindow.document.write(`
        <html>
            <head>
                <title>Print</title>
                <style>${styles}</style>
            </head>
            <body>
                ${element.outerHTML}
            </body>
        </html>
    `);

    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
    printWindow.close();
}

// System notifications check
function checkForSystemNotifications() {
    // Check for various system notifications
    setTimeout(() => {
        checkLowStockNotifications();
        checkExpiringItemsNotifications();
        checkUpcomingAppointmentsNotifications();
    }, 2000);
}

function checkLowStockNotifications() {
    const lowStockElements = document.querySelectorAll('[data-low-stock="true"]');
    if (lowStockElements.length > 0) {
        showNotification(lowStockElements.length + ' items are low in stock', 'warning');
    }
}

function checkExpiringItemsNotifications() {
    const expiringElements = document.querySelectorAll('[data-expiring="true"]');
    if (expiringElements.length > 0) {
        showNotification(expiringElements.length + ' items are expiring soon', 'warning');
    }
}

function checkUpcomingAppointmentsNotifications() {
    const upcomingElements = document.querySelectorAll('[data-upcoming="true"]');
    if (upcomingElements.length > 0) {
        showNotification(upcomingElements.length + ' appointments coming up', 'info');
    }
}

// Customer management functions
function bookAppointment(customerId) {
    try {
        // Redirect to bookings page with customer pre-selected
        window.location.href = `/bookings?customer_id=${customerId}`;
    } catch (error) {
        console.error('Error booking appointment:', error);
        showNotification('Error navigating to bookings page', 'error');
    }
}

function editCustomer(customerId) {
    try {
        console.log('Edit customer called with ID:', customerId);

        // Validate customer ID
        if (!customerId || customerId === 'null' || customerId === null) {
            console.error('Invalid customer ID provided:', customerId);
            showNotification('Invalid customer ID', 'error');
            return;
        }

        const editModal = document.getElementById('editCustomerModal');
        if (!editModal) {
            console.error('Edit modal not found');
            showNotification('Edit modal not available', 'error');
            return;
        }

        // Store customer ID for form submission
        window.currentCustomerId = customerId;

        // Set up the form
        const form = editModal.querySelector('#editCustomerForm');
        if (form) {
            form.dataset.customerId = customerId;
            // Clear any previous data
            form.reset();
        }

        // Show modal first, then load data
        const modal = new bootstrap.Modal(editModal);
        modal.show();

        // Load customer data after modal is shown
        setTimeout(() => {
            loadCustomerDataForEdit(customerId);
        }, 100);

    } catch (error) {
        console.error('Error in editCustomer function:', error);
        showNotification('Error opening customer editor', 'error');
    }
}

function viewCustomer(customerId) {
    try {
        // Store current customer ID for modal actions
        window.currentCustomerId = customerId;

        // Show loading in modal
        const customerDetails = document.getElementById('customerDetails');
        if (customerDetails) {
            customerDetails.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading customer details...</p>
                </div>
            `;
        }

        // In a real implementation, this would fetch customer details via AJAX
        setTimeout(() => {
            if (customerDetails) {
                customerDetails.innerHTML = `
                    <div class="alert alert-info">
                        Customer details would be loaded here via AJAX call to /api/customers/${customerId}
                    </div>
                `;
            }
        }, 1000);

    } catch (error) {
        console.error('Error viewing customer:', error);
        showNotification('Error loading customer details', 'error');
    }
}

function bookAppointment(customerId) {
    try {
        console.log('Book appointment for customer:', customerId);

        // Redirect to bookings page with customer ID
        window.location.href = `/bookings?customer_id=${customerId}`;
    } catch (error) {
        console.error('Error booking appointment:', error);
        showNotification('Error booking appointment', 'error');
    }
}

function bookAppointmentFromModal() {
    try {
        if (window.currentCustomerId) {
            bookAppointment(window.currentCustomerId);
        } else {
            showNotification('No customer selected', 'warning');
        }
    } catch (error) {
        console.error('Error booking appointment from modal:', error);
        showNotification('Error booking appointment', 'error');
    }
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function loadCustomerDataForEdit(customerId) {
    console.log('Loading customer data for editing:', customerId);

    // Validate customer ID again
    if (!customerId || customerId === 'null' || customerId === null) {
        console.error('Invalid customer ID provided to loadCustomerDataForEdit:', customerId);
        showNotification('Invalid customer ID', 'error');
        return;
    }

    // Show loading indicator in modal
    const modalBody = document.querySelector('#editCustomerModal .modal-body');
    if (modalBody) {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'loading-indicator';
        loadingDiv.className = 'text-center p-3';
        loadingDiv.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading customer data...</p>
        `;
        modalBody.appendChild(loadingDiv);
    }

    fetch(`/api/customers/${customerId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    })
    .then(response => {
        console.log('API response status:', response.status);

        // Remove loading indicator
        const loadingDiv = document.getElementById('loading-indicator');
        if (loadingDiv) {
            loadingDiv.remove();
        }

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Customer data received:', data);

        if (data.success && data.customer) {
            populateEditForm(data.customer);
            showNotification('Customer data loaded successfully', 'success', 2000);
        } else {
            throw new Error(data.error || 'Customer data not found');
        }
    })
    .catch(error => {
        console.error('Error fetching customer data:', error);

        // Remove loading indicator if still present
        const loadingDiv = document.getElementById('loading-indicator');
        if (loadingDiv) {
            loadingDiv.remove();
        }

        showNotification('Error loading customer data. Please try again.', 'error');
    });
}

function deleteCustomer(customerId, customerName) {
    if (confirm(`Are you sure you want to delete customer "${customerName}"?\n\nThis action cannot be undone and will remove all customer data.`)) {
        // Show loading notification
        showNotification('Deleting customer...', 'info');

        // Create form data for DELETE request
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/clients/delete/${customerId}`;

        // Submit the form
        document.body.appendChild(form);
        form.submit();
    }
}

function populateEditForm(customer) {
    console.log('Populating edit form with customer data:', customer);

    const form = document.querySelector('#editCustomerForm');
    if (!form) {
        console.error('Edit customer form not found');
        return;
    }

    if (!customer) {
        console.error('No customer data provided');
        return;
    }

    try {
        // Clear form first
        form.reset();

        // Populate form fields with safe fallbacks
        const fields = {
            'first_name': customer.first_name || '',
            'last_name': customer.last_name || '',
            'phone': customer.phone || '',
            'email': customer.email || '',
            'address': customer.address || '',
            'date_of_birth': customer.date_of_birth || '',
            'gender': customer.gender || '',
            'preferences': customer.preferences || '',
            'allergies': customer.allergies || '',
            'notes': customer.notes || ''
        };

        // Set each field value
        Object.entries(fields).forEach(([fieldName, value]) => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.value = value;
                console.log(`Set ${fieldName} to:`, value);
            } else {
                console.warn(`Field ${fieldName} not found in form`);
            }
        });

        // Store customer ID in form
        form.dataset.customerId = customer.id;
        window.currentCustomerId = customer.id;

        // Set the form action dynamically
        form.action = `/clients/update/${customer.id}`;

        console.log('Edit form populated successfully');

    } catch (error) {
        console.error('Error populating edit form:', error);
        showNotification('Error loading customer data into form', 'error');
    }
}

// Handle edit customer form submission
function handleEditCustomerSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');

    // Prevent double submission
    if (submitBtn.disabled) {
        return;
    }

    const customerId = form.dataset.customerId || window.currentCustomerId;

    if (!customerId) {
        showNotification('Error: Customer ID not found.', 'error');
        return;
    }

    // Show loading and disable button
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Updating...';

    // Validate form action is set
    if (!form.action || form.action.endsWith('/clients')) {
        form.action = `/clients/update/${customerId}`;
    }

    // Submit form normally - let Flask handle it with proper redirect and flash messages
    form.submit();
}

// Load metadata function for staff management - defined early
function loadMetadata() {
    console.log('Metadata loading handled in loadStaffData');
    // This function is called from comprehensive_staff.html
    // The actual metadata loading is handled in the loadStaffData function
    return Promise.resolve();
}

// Make functions globally available immediately
window.loadMetadata = loadMetadata;
window.showNotification = showNotification;
window.exportTableData = exportTableData;
window.printElement = printElement;
window.validateForm = validateForm;
window.saveUserPreferences = saveUserPreferences;
window.updateServicePrice = updateServicePrice;
window.bookAppointment = bookAppointment;
window.editCustomer = editCustomer;
window.viewCustomer = viewCustomer;
window.bookAppointmentFromModal = bookAppointmentFromModal;
window.showContextMenu = showContextMenu;
window.hideContextMenu = hideContextMenu;
// window.handleEditCustomerSubmit = handleEditCustomerSubmit; // Not needed globally if called by form submission


// Context Menu Functionality
function setupContextMenu() {
    createContextMenuHTML();
    
    // Prevent default context menu and show custom menu
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        showContextMenu(e.pageX, e.pageY);
    });

    // Hide context menu on click or scroll
    document.addEventListener('click', hideContextMenu);
    document.addEventListener('scroll', hideContextMenu);
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            hideContextMenu();
        }
    });
}

function createContextMenuHTML() {
    // Remove existing context menu if present
    const existingMenu = document.getElementById('spaContextMenu');
    if (existingMenu) {
        existingMenu.remove();
    }

    const contextMenu = document.createElement('div');
    contextMenu.id = 'spaContextMenu';
    contextMenu.className = 'spa-context-menu';
    contextMenu.innerHTML = `
        <div class="context-menu-header">
            <i class="fas fa-spa me-2"></i>Quick Navigation
        </div>
        <div class="context-menu-item" data-url="/dashboard">
            <i class="fas fa-tachometer-alt me-2"></i>Dashboard
        </div>
        <div class="context-menu-item" data-url="/bookings">
            <i class="fas fa-calendar-alt me-2"></i>Smart Booking & Calendar
        </div>
        <div class="context-menu-item" data-url="/staff_availability">
            <i class="fas fa-users-cog me-2"></i>Staff Availability
        </div>
        <div class="context-menu-item" data-url="/appointments_management">
            <i class="fas fa-calendar-check me-2"></i>Manage Appointments
        </div>
        <div class="context-menu-item" data-url="/customers">
            <i class="fas fa-users me-2"></i>Client History & Loyalty
        </div>
        <div class="context-menu-item" data-url="/comprehensive_staff">
            <i class="fas fa-users me-2"></i>Staff Management
        </div>
        <div class="context-menu-item" data-url="/checkin">
            <i class="fas fa-user-check me-2"></i>Check-In
        </div>
        <div class="context-menu-item" data-url="/notifications">
            <i class="fas fa-bell me-2"></i>WhatsApp Notifications
        </div>
        <div class="context-menu-item" data-url="/integrated_billing">
            <i class="fas fa-cash-register me-2"></i>Billing System
        </div>
        <div class="context-menu-item" data-url="/services">
            <i class="fas fa-spa me-2"></i>Services Management
        </div>
        <div class="context-menu-item" data-url="/packages">
            <i class="fas fa-gift me-2"></i>Package Management
        </div>
        <div class="context-menu-item" data-url="/reports">
            <i class="fas fa-chart-bar me-2"></i>Reports & Insights
        </div>
        <div class="context-menu-item" data-url="/expenses">
            <i class="fas fa-receipt me-2"></i>Daily Expense Tracker
        </div>
        <div class="context-menu-item" data-url="/inventory_dashboard">
            <i class="fas fa-boxes me-2"></i>Inventory Management
        </div>
        <div class="context-menu-item" data-url="/alerts">
            <i class="fas fa-exclamation-triangle me-2"></i>Expiring Product Alerts
        </div>
        <div class="context-menu-divider"></div>
        <div class="context-menu-item" data-url="/system_management">
            <i class="fas fa-server me-2"></i>System Management
        </div>
        <div class="context-menu-item" data-url="/role_management">
            <i class="fas fa-users-cog me-2"></i>Role Management
        </div>
        <div class="context-menu-item" data-url="/settings">
            <i class="fas fa-user-cog me-2"></i>User & Access Control
        </div>
    `;

    // Add click handlers to menu items
    contextMenu.addEventListener('click', function(e) {
        e.stopPropagation();
        const item = e.target.closest('.context-menu-item');
        if (item && item.dataset.url) {
            const url = item.dataset.url;
            hideContextMenu();
            
            // Add loading feedback
            showNotification('Navigating...', 'info', 1000);
            
            // Navigate to the selected page
            window.location.href = url;
        }
    });

    document.body.appendChild(contextMenu);
}

function showContextMenu(x, y) {
    const contextMenu = document.getElementById('spaContextMenu');
    if (!contextMenu) return;

    // Calculate position to keep menu within viewport
    const menuWidth = 250;
    const menuHeight = 400;
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let posX = x;
    let posY = y;

    // Adjust horizontal position
    if (x + menuWidth > viewportWidth) {
        posX = x - menuWidth;
    }

    // Adjust vertical position
    if (y + menuHeight > viewportHeight) {
        posY = y - menuHeight;
    }

    // Ensure menu doesn't go off-screen
    posX = Math.max(10, Math.min(posX, viewportWidth - menuWidth - 10));
    posY = Math.max(10, Math.min(posY, viewportHeight - menuHeight - 10));

    contextMenu.style.left = posX + 'px';
    contextMenu.style.top = posY + 'px';
    contextMenu.style.display = 'block';

    // Add animation class
    setTimeout(() => {
        contextMenu.classList.add('show');
    }, 10);
}

function hideContextMenu() {
    const contextMenu = document.getElementById('spaContextMenu');
    if (contextMenu) {
        contextMenu.classList.remove('show');
        setTimeout(() => {
            contextMenu.style.display = 'none';
        }, 200);
    }
}

// CSS for dynamic features
const additionalStyles = `
<style>
.refreshing {
    position: relative;
    opacity: 0.7;
}

.refreshing::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    animation: refreshing 1s infinite;
}

@keyframes refreshing {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.offline {
    filter: grayscale(20%);
}

.offline::before {
    content: 'Offline Mode';
    position: fixed;
    top: 60px;
    right: 20px;
    background: #dc3545;
    color: white;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 0.8em;
    z-index: 9998;
}

.sorted-asc::after {
    content: ' ↑';
    font-weight: bold;
}

.sorted-desc::after {
    content: ' ↓';
    font-weight: bold;
}

th[data-sortable]:hover {
    background-color: rgba(0,0,0,0.05);
}

.toast-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
}

/* Context Menu Styles */
.spa-context-menu {
    position: fixed;
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    min-width: 250px;
    max-width: 300px;
    z-index: 10000;
    display: none;
    opacity: 0;
    transform: scale(0.95);
    transition: all 0.2s ease-out;
    backdrop-filter: blur(10px);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.spa-context-menu.show {
    opacity: 1;
    transform: scale(1);
}

.context-menu-header {
    padding: 12px 16px;
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    font-weight: 600;
    font-size: 14px;
    border-radius: 8px 8px 0 0;
    border-bottom: 1px solid #e0e0e0;
}

.context-menu-item {
    padding: 12px 16px;
    cursor: pointer;
    font-size: 14px;
    color: #333;
    display: flex;
    align-items: center;
    transition: all 0.15s ease;
    border-left: 3px solid transparent;
}

.context-menu-item:hover {
    background: #f8f9fa;
    border-left-color: #007bff;
    color: #007bff;
    transform: translateX(2px);
}

.context-menu-item:active {
    background: #e9ecef;
}

.context-menu-item i {
    width: 16px;
    text-align: center;
    opacity: 0.7;
}

.context-menu-item:hover i {
    opacity: 1;
}

.context-menu-divider {
    height: 1px;
    background: #e0e0e0;
    margin: 8px 0;
}

@media print {
    .no-print, .spa-context-menu {
        display: none !important;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .spa-context-menu {
        background: #2c2c2c;
        border-color: #444;
        color: #fff;
    }
    
    .context-menu-item {
        color: #fff;
    }
    
    .context-menu-item:hover {
        background: #3c3c3c;
    }
    
    .context-menu-divider {
        background: #444;
    }
}
</style>
`;

// Inject additional styles
if (document.head) {
    document.head.insertAdjacentHTML('beforeend', additionalStyles);
}

// ========== VERTICAL SIDEBAR NAVIGATION FUNCTIONS ==========

// Set active navigation link based on current page
function setActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('#sidebar .nav-link');
    const dropdownItems = document.querySelectorAll('#sidebar .dropdown-item, #sidebar .collapse-item');

    // Remove active class from all nav links
    navLinks.forEach(link => {
        link.classList.remove('active');
    });

    // Check main navigation links (not dropdown toggles)
    navLinks.forEach(link => {
        // Skip dropdown toggle links (they have href="#" or data-toggle)
        if (link.getAttribute('href') === '#' || link.getAttribute('data-toggle') === 'collapse') {
            return;
        }

        // Check if link href matches current path
        try {
            const linkPath = new URL(link.href).pathname;
            if (linkPath === currentPath || (currentPath === '/' && linkPath.includes('dashboard'))) {
                link.classList.add('active');
            }
        } catch (e) {
            // Skip invalid URLs
        }
    });

    // Check dropdown items and mark parent as active if needed
    dropdownItems.forEach(item => {
        try {
            const itemPath = new URL(item.href).pathname;
            if (itemPath === currentPath) {
                item.classList.add('active');

                // Find and expand the parent dropdown
                const parentCollapse = item.closest('.collapse');
                if (parentCollapse) {
                    parentCollapse.classList.add('show');

                    // Find the dropdown toggle button and mark as active
                    const toggleButton = document.querySelector(`[data-target="#${parentCollapse.id}"]`);
                    if (toggleButton) {
                        toggleButton.classList.add('active');
                        toggleButton.setAttribute('aria-expanded', 'true');
                    }
                }
            }
        } catch (e) {
            // Skip invalid URLs
        }
    });
}

// Setup mobile sidebar auto-close functionality
function setupMobileSidebarClose() {
    const sidebarLinks = document.querySelectorAll('#sidebar .nav-link');
    const sidebar = document.getElementById('sidebar');

    if (sidebar) {
        sidebarLinks.forEach(link => {
            link.addEventListener('click', function() {
                // Close sidebar on mobile after clicking a link
                if (window.innerWidth < 992) {
                    const offcanvas = bootstrap.Offcanvas.getInstance(sidebar);
                    if (offcanvas) {
                        offcanvas.hide();
                    }
                }
            });
        });
    }
}

// Setup sidebar auto-minimize on hover out
function setupSidebarAutoMinimize() {
    const sidebar = document.getElementById('sidebar');
    const body = document.body;
    let hoverTimeout;

    if (sidebar && window.innerWidth >= 992) {
        // Add hover event listeners
        sidebar.addEventListener('mouseenter', function() {
            clearTimeout(hoverTimeout);
            sidebar.classList.remove('minimized');
            body.classList.remove('sidebar-minimized');
        });

        sidebar.addEventListener('mouseleave', function() {
            // Add a small delay before minimizing to prevent flickering
            hoverTimeout = setTimeout(() => {
                sidebar.classList.add('minimized');
                body.classList.add('sidebar-minimized');
            }, 500); // 500ms delay
        });

        // Initialize as minimized
        setTimeout(() => {
            sidebar.classList.add('minimized');
            body.classList.add('sidebar-minimized');
        }, 1000); // Wait 1 second after page load
    }
}

// Initialize sidebar functionality when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    setActiveNavLink();
    setupMobileSidebarClose();
    setupSidebarAutoMinimize();

    // Update active link on page navigation
    window.addEventListener('popstate', setActiveNavLink);

    // Handle sidebar state on window resize
    window.addEventListener('resize', function() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar && window.innerWidth >= 992) {
            // Hide offcanvas on desktop
            const offcanvas = bootstrap.Offcanvas.getInstance(sidebar);
            if (offcanvas) {
                offcanvas.hide();
            }
            // Re-initialize auto-minimize for desktop
            setupSidebarAutoMinimize();
        } else if (sidebar) {
            // Remove minimize classes on mobile
            sidebar.classList.remove('minimized');
            document.body.classList.remove('sidebar-minimized');
        }
    });
});

// Define updateServicePrice function globally first
function updateServicePrice(serviceId, price) {
    try {
        console.log('Service ' + serviceId + ' selected with price: ' + price);

        // Update any price display elements
        const priceDisplays = document.querySelectorAll('[data-service-price="' + serviceId + '"]');
        priceDisplays.forEach(display => {
            display.textContent = formatCurrency(price);
        });

        // Update service-specific price elements
        const priceElements = document.querySelectorAll('.service-price');
        priceElements.forEach(element => {
            if (element.dataset.serviceId === serviceId) {
                element.textContent = '$' + price;
            }
        });

        // Update amount input if exists
        const amountField = document.getElementById('amount');
        if (amountField) {
            amountField.value = price;
        }

        const serviceAmountField = document.getElementById('service_amount');
        if (serviceAmountField) {
            serviceAmountField.value = price;
        }

        // Trigger total calculation if on billing page
        if (typeof calculateTotal === 'function') {
            calculateTotal();
        }

        // Trigger custom price update events
        document.dispatchEvent(new CustomEvent('servicePriceUpdated', {
            detail: { serviceId: serviceId, price: price }
        }));

        return true;

    } catch (error) {
        console.error('Error updating service price:', error);
        return false;
    }
}

// Make it globally available immediately
window.updateServicePrice = updateServicePrice;

// Staff management navigation function
function navigateToStaffManagement() {
    window.location.href = '/comprehensive_staff';
}

// Update service price function - consolidated and fixed
function updateServicePrice(serviceId, price) {
    try {
        console.log('Service ' + serviceId + ' selected with price: ' + price);

        // Update any price display elements
        const priceDisplays = document.querySelectorAll('[data-service-price="' + serviceId + '"]');
        priceDisplays.forEach(display => {
            display.textContent = formatCurrency(price);
        });

        // Update service-specific price elements
        const priceElements = document.querySelectorAll('.service-price');
        priceElements.forEach(element => {
            if (element.dataset.serviceId === serviceId) {
                element.textContent = '$' + price;
            }
        });

        // Update amount input if exists
        const amountField = document.getElementById('amount');
        if (amountField) {
            amountField.value = price;
        }

        const serviceAmountField = document.getElementById('service_amount');
        if (serviceAmountField) {
            serviceAmountField.value = price;
        }

        // Trigger total calculation if on billing page
        if (typeof calculateTotal === 'function') {
            calculateTotal();
        }

        // Trigger custom price update events
        document.dispatchEvent(new CustomEvent('servicePriceUpdated', {
            detail: { serviceId: serviceId, price: price }
        }));

        document.dispatchEvent(new CustomEvent('servicePriceChanged', {
            detail: { serviceId, price }
        }));

    } catch (error) {
        console.error('Error updating service price:', error);
    }
}

// Service selection handler for forms
function handleServiceSelection(selectElement) {
    try {
        if (!selectElement) return;

        const selectedOption = selectElement.options[selectElement.selectedIndex];
        if (selectedOption && selectedOption.dataset.price) {
            const price = selectedOption.dataset.price;
            updateServicePrice(selectElement.value, price);

            // Update amount field if exists
            const amountField = document.getElementById('amount');
            if (amountField) {
                amountField.value = price;
            }
        }
    } catch (error) {
        console.error('Error handling service selection:', error);
    }
}

// Format currency helper function
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Calculate total function for billing forms
function calculateTotal() {
    try {
        let total = 0;
        const serviceSelects = document.querySelectorAll('select[data-price]');

        serviceSelects.forEach(select => {
            if (select.value && select.selectedOptions[0]) {
                const price = parseFloat(select.selectedOptions[0].dataset.price || 0);
                total += price;
            }
        });

        // Update total display
        const totalDisplay = document.getElementById('total-amount');
        if (totalDisplay) {
            totalDisplay.textContent = '$' + total.toFixed(2);
        }

        // Update hidden total field
        const totalField = document.getElementById('total_amount');
        if (totalField) {
            totalField.value = total.toFixed(2);
        }

    } catch (error) {
        console.error('Error calculating total:', error);
    }
}

// Face recognition functionality
let video, canvas, context;
let isRecognizing = false;

// Export functions globally to avoid conflicts
window.editCustomer = editCustomer;
window.viewCustomer = viewCustomer;
window.bookAppointment = bookAppointment;