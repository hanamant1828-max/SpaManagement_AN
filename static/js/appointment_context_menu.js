/**
 * Appointment Context Menu for Right-Click "Go to Integrated Billing"
 * Works with all booking templates and appointment blocks
 */

// Global context menu variables
let contextMenu = null;
let currentAppointmentId = null;

// Initialize context menu when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeAppointmentContextMenu();
});

function initializeAppointmentContextMenu() {
    // Create context menu HTML
    createContextMenu();
    
    // Add event listeners for appointment blocks
    addAppointmentListeners();
    
    // Hide context menu when clicking elsewhere
    document.addEventListener('click', hideContextMenu);
    
    console.log('✅ Appointment context menu initialized');
}

function createContextMenu() {
    // Remove existing context menu if any
    const existing = document.getElementById('appointmentContextMenu');
    if (existing) {
        existing.remove();
    }
    
    // Create new context menu
    contextMenu = document.createElement('div');
    contextMenu.id = 'appointmentContextMenu';
    contextMenu.className = 'context-menu';
    contextMenu.style.cssText = `
        position: fixed;
        background: white;
        border: 1px solid #ccc;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        display: none;
        min-width: 200px;
        padding: 8px 0;
    `;
    
    contextMenu.innerHTML = `
        <div class="context-menu-item" onclick="goToIntegratedBilling()" style="
            padding: 12px 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            font-size: 14px;
            color: #333;
            border-bottom: 1px solid #eee;
        ">
            <i class="fas fa-cash-register" style="margin-right: 8px; color: #28a745;"></i>
            Bill All Customer Bookings
        </div>
        <div class="context-menu-item" onclick="viewAppointmentDetails()" style="
            padding: 12px 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            font-size: 14px;
            color: #333;
            border-bottom: 1px solid #eee;
        ">
            <i class="fas fa-eye" style="margin-right: 8px; color: #007bff;"></i>
            View Details
        </div>
        <div class="context-menu-item" onclick="editAppointment()" style="
            padding: 12px 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            font-size: 14px;
            color: #333;
        ">
            <i class="fas fa-edit" style="margin-right: 8px; color: #ffc107;"></i>
            Edit Appointment
        </div>
    `;
    
    // Add hover effects
    const menuItems = contextMenu.querySelectorAll('.context-menu-item');
    menuItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
        });
        item.addEventListener('mouseleave', function() {
            this.style.backgroundColor = 'transparent';
        });
    });
    
    document.body.appendChild(contextMenu);
}

function addAppointmentListeners() {
    // Target multiple appointment selectors with more comprehensive coverage
    const appointmentSelectors = [
        '.appointment-block',
        '.appointment-item',
        '.booking-slot',
        '.schedule-appointment',
        '.appointment',
        '[data-appointment-id]'
    ];
    
    // Also target staff header columns for staff-level context menu
    const staffSelectors = [
        '.staff-cell',
        '.staff-header-column',
        '.staff-name',
        '.staff-row'
    ];
    
    // Add listeners for appointment blocks with improved detection
    appointmentSelectors.forEach(selector => {
        const appointments = document.querySelectorAll(selector);
        console.log(`🔍 Found ${appointments.length} appointments for selector: ${selector}`);
        
        appointments.forEach((appointment, index) => {
            // Skip if already has context menu attached (avoid duplicates)
            if (appointment.hasAttribute('data-context-menu-ready')) {
                return;
            }
            
            // Remove existing listeners to prevent duplicates
            appointment.removeEventListener('contextmenu', handleAppointmentRightClick);
            
            // Add right-click listener with proper event handling
            appointment.addEventListener('contextmenu', function(event) {
                console.log(`🎯 Context menu triggered for appointment ${index + 1}`);
                handleAppointmentRightClick(event);
            });
            
            // Make sure appointment has cursor pointer
            appointment.style.cursor = 'pointer';
            
            // Mark as having context menu attached
            appointment.setAttribute('data-context-menu-ready', 'true');
            
            // Debug: Log appointment details
            const appointmentId = appointment.dataset.appointmentId || appointment.getAttribute('data-appointment-id');
            console.log(`✅ Context menu attached to appointment ${index + 1}: ID ${appointmentId}`);
        });
    });
    
    // Add listeners for staff header columns
    staffSelectors.forEach(selector => {
        const staffHeaders = document.querySelectorAll(selector);
        console.log(`🔍 Found ${staffHeaders.length} staff headers for selector: ${selector}`);
        
        staffHeaders.forEach((staffHeader, index) => {
            // Remove existing listeners to prevent duplicates
            staffHeader.removeEventListener('contextmenu', handleStaffHeaderRightClick);
            
            // Add right-click listener
            staffHeader.addEventListener('contextmenu', handleStaffHeaderRightClick);
            
            // Make sure staff header has cursor pointer
            staffHeader.style.cursor = 'pointer';
            
            // Debug: Log staff header details
            const staffName = staffHeader.querySelector('.staff-name')?.textContent || 
                             staffHeader.textContent || 
                             staffHeader.dataset.staffName;
            console.log(`✅ Context menu attached to staff header ${index + 1}: ${staffName}`);
        });
    });
    
    // Also try to find appointments in the entire schedule grid
    const scheduleGrid = document.getElementById('scheduleGrid');
    if (scheduleGrid) {
        const allAppointmentBlocks = scheduleGrid.querySelectorAll('.appointment-block');
        console.log(`🔍 Total appointment blocks found in schedule grid: ${allAppointmentBlocks.length}`);
        
        allAppointmentBlocks.forEach((block, index) => {
            // Ensure each block has the right-click listener
            if (!block.hasAttribute('data-context-menu-attached')) {
                block.removeEventListener('contextmenu', handleAppointmentRightClick);
                block.addEventListener('contextmenu', handleAppointmentRightClick);
                block.style.cursor = 'pointer';
                block.setAttribute('data-context-menu-attached', 'true');
                
                const appointmentId = block.dataset.appointmentId || block.getAttribute('data-appointment-id');
                console.log(`✅ Context menu attached to grid appointment ${index + 1}: ID ${appointmentId}`);
            }
        });
    }
}

function handleAppointmentRightClick(event) {
    event.preventDefault();
    event.stopPropagation();
    
    // Get appointment ID from various possible attributes
    const appointmentElement = event.currentTarget;
    
    // Debug: Log all attributes to understand what we're working with
    console.log('🔍 Right-click element:', appointmentElement);
    console.log('🔍 Element class:', appointmentElement.className);
    console.log('🔍 All data attributes:', appointmentElement.dataset);
    console.log('🔍 data-appointment-id attribute:', appointmentElement.getAttribute('data-appointment-id'));
    console.log('🔍 data-id attribute:', appointmentElement.getAttribute('data-id'));
    
    currentAppointmentId = appointmentElement.dataset.appointmentId || 
                          appointmentElement.dataset.id ||
                          appointmentElement.getAttribute('data-appointment-id') ||
                          appointmentElement.getAttribute('data-id');
    
    // If no ID found, try to extract from nearby elements
    if (!currentAppointmentId) {
        const idElement = appointmentElement.querySelector('[data-appointment-id], [data-id]');
        if (idElement) {
            currentAppointmentId = idElement.dataset.appointmentId || idElement.dataset.id;
            console.log('🔍 Found ID in child element:', currentAppointmentId);
        }
    }
    
    console.log('🔍 Right-clicked appointment ID:', currentAppointmentId);
    
    if (!currentAppointmentId) {
        console.warn('⚠️ No appointment ID found for context menu');
        console.warn('⚠️ Element HTML:', appointmentElement.outerHTML);
        return;
    }
    
    // Show context menu at cursor position
    showContextMenu(event.pageX, event.pageY);
}

function handleStaffHeaderRightClick(event) {
    event.preventDefault();
    event.stopPropagation();
    
    // Get staff information from the header element
    const staffElement = event.currentTarget;
    
    // Debug: Log staff header information
    console.log('🎯 Staff header right-click detected!');
    console.log('🔍 Right-click staff element:', staffElement);
    console.log('🔍 Staff element class:', staffElement.className);
    console.log('🔍 Staff data attributes:', staffElement.dataset);
    
    // Get staff name and ID from multiple possible sources
    const staffName = staffElement.querySelector('.staff-name')?.textContent || 
                     staffElement.textContent?.trim() || 
                     staffElement.dataset.staffName || 
                     staffElement.getAttribute('data-staff-name') ||
                     'Unknown Staff';
    
    const staffId = staffElement.dataset.staffId || 
                   staffElement.getAttribute('data-staff-id') ||
                   staffElement.closest('[data-staff-id]')?.dataset.staffId ||
                   staffElement.getAttribute('data-staff') ||
                   extractStaffIdFromElement(staffElement);
    
    console.log('🎯 Staff header click - Staff:', staffName, 'ID:', staffId);
    
    // Set current appointment ID to null since this is a staff header click
    currentAppointmentId = null;
    
    // Store staff information for context menu actions
    window.currentStaffId = staffId;
    window.currentStaffName = staffName;
    
    // Show context menu at cursor position
    showContextMenu(event.pageX, event.pageY);
}

function extractStaffIdFromElement(element) {
    // Try to extract staff ID from various attributes or text content
    const allAttributes = Array.from(element.attributes);
    for (let attr of allAttributes) {
        if (attr.name.includes('staff') || attr.name.includes('id')) {
            return attr.value;
        }
    }
    return null;
}

function showContextMenu(x, y) {
    if (!contextMenu) return;
    
    // Hide any existing context menu
    hideContextMenu();
    
    // Position and show context menu
    contextMenu.style.left = x + 'px';
    contextMenu.style.top = y + 'px';
    contextMenu.style.display = 'block';
    
    // Adjust position if menu goes off screen
    const rect = contextMenu.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    if (rect.right > viewportWidth) {
        contextMenu.style.left = (x - rect.width) + 'px';
    }
    
    if (rect.bottom > viewportHeight) {
        contextMenu.style.top = (y - rect.height) + 'px';
    }
}

function hideContextMenu() {
    if (contextMenu) {
        contextMenu.style.display = 'none';
    }
}

// Context menu action functions
function goToIntegratedBilling() {
    hideContextMenu();
    
    // Handle staff header clicks - bill all appointments for that staff
    if (!currentAppointmentId && window.currentStaffId) {
        console.log('🔄 Navigating to integrated billing for staff:', window.currentStaffName, 'ID:', window.currentStaffId);
        
        // Navigate to staff billing route or integrated billing with staff filter
        window.location.href = `/integrated-billing?staff_id=${window.currentStaffId}`;
        return;
    }
    
    // Handle individual appointment clicks
    if (!currentAppointmentId) {
        alert('No appointment or staff selected');
        return;
    }
    
    console.log('🔄 Navigating to integrated billing for appointment:', currentAppointmentId);
    
    // Navigate to the appointment billing route
    window.location.href = `/appointment/${currentAppointmentId}/go-to-billing`;
}

function viewAppointmentDetails() {
    hideContextMenu();
    
    // Handle staff header clicks - show staff schedule or details
    if (!currentAppointmentId && window.currentStaffId) {
        console.log('👁️ Viewing staff details:', window.currentStaffName, 'ID:', window.currentStaffId);
        
        // Navigate to staff management or staff schedule
        window.location.href = `/staff-management?staff_id=${window.currentStaffId}`;
        return;
    }
    
    // Handle individual appointment clicks
    if (!currentAppointmentId) {
        alert('No appointment or staff selected');
        return;
    }
    
    console.log('👁️ Viewing appointment details:', currentAppointmentId);
    
    // Navigate to appointment details
    window.location.href = `/appointments/view/${currentAppointmentId}`;
}

function editAppointment() {
    hideContextMenu();
    
    // Handle staff header clicks - edit staff or create new appointment
    if (!currentAppointmentId && window.currentStaffId) {
        console.log('✏️ Creating new appointment for staff:', window.currentStaffName, 'ID:', window.currentStaffId);
        
        // Navigate to create new appointment with staff pre-selected
        window.location.href = `/unaki-booking?staff_id=${window.currentStaffId}`;
        return;
    }
    
    // Handle individual appointment clicks
    if (!currentAppointmentId) {
        alert('No appointment or staff selected');
        return;
    }
    
    console.log('✏️ Editing appointment:', currentAppointmentId);
    
    // Navigate to appointment edit
    window.location.href = `/appointments/edit/${currentAppointmentId}`;
}

// Re-initialize context menu when new content is loaded (for dynamic content)
function reinitializeContextMenu() {
    console.log('🔄 Reinitializing appointment context menu...');
    
    // Clear any existing markers
    document.querySelectorAll('[data-context-menu-attached]').forEach(element => {
        element.removeAttribute('data-context-menu-attached');
    });
    document.querySelectorAll('[data-context-menu-ready]').forEach(element => {
        element.removeAttribute('data-context-menu-ready');
    });
    
    setTimeout(() => {
        addAppointmentListeners();
        console.log('✅ Context menu reinitialized');
        
        // Verify that all appointment blocks have context menu
        const totalBlocks = document.querySelectorAll('.appointment-block').length;
        const attachedBlocks = document.querySelectorAll('[data-context-menu-ready]').length;
        console.log(`📊 Context menu coverage: ${attachedBlocks}/${totalBlocks} appointment blocks`);
    }, 500);
}

// Export functions for global use
window.reinitializeContextMenu = reinitializeContextMenu;
window.goToIntegratedBilling = goToIntegratedBilling;
window.viewAppointmentDetails = viewAppointmentDetails;
window.editAppointment = editAppointment;

// Removed duplicate class-based implementation to prevent conflicts
// The global function-based implementation above provides all necessary functionality