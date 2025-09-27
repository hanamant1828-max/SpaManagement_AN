
// Appointment Context Menu Implementation
class AppointmentContextMenu {
    constructor() {
        this.contextMenu = null;
        this.currentAppointmentId = null;
        this.isInitialized = false;
        this.init();
    }

    init() {
        this.createContextMenuHTML();
        this.attachGlobalEventListeners();
        this.isInitialized = true;
        console.log('🎛️ Context menu system initialized');
    }

    createContextMenuHTML() {
        // Remove existing context menu if it exists
        const existingMenu = document.getElementById('appointment-context-menu');
        if (existingMenu) {
            existingMenu.remove();
        }

        // Create context menu HTML
        const contextMenuHTML = `
            <div id="appointment-context-menu" class="context-menu" style="display: none;">
                <div class="context-menu-header">
                    <strong id="context-menu-title">Appointment Actions</strong>
                </div>
                <div class="context-menu-divider"></div>
                <ul class="context-menu-list">
                    <li class="context-menu-item" data-action="view">
                        <i class="fas fa-eye"></i> View Details
                    </li>
                    <li class="context-menu-item" data-action="edit">
                        <i class="fas fa-edit"></i> Edit Appointment
                    </li>
                    <li class="context-menu-item" data-action="reschedule">
                        <i class="fas fa-calendar-alt"></i> Reschedule
                    </li>
                    <li class="context-menu-divider"></li>
                    <li class="context-menu-item" data-action="complete">
                        <i class="fas fa-check-circle"></i> Mark Completed
                    </li>
                    <li class="context-menu-item" data-action="cancel">
                        <i class="fas fa-times-circle"></i> Cancel Appointment
                    </li>
                    <li class="context-menu-divider"></li>
                    <li class="context-menu-item" data-action="billing">
                        <i class="fas fa-dollar-sign"></i> Go to Billing
                    </li>
                    <li class="context-menu-item danger" data-action="delete">
                        <i class="fas fa-trash"></i> Delete Appointment
                    </li>
                </ul>
            </div>
        `;

        // Add to body
        document.body.insertAdjacentHTML('beforeend', contextMenuHTML);
        this.contextMenu = document.getElementById('appointment-context-menu');

        // Add context menu styles if not already present
        this.addContextMenuStyles();

        // Add click handlers to menu items
        this.attachContextMenuHandlers();
    }

    addContextMenuStyles() {
        const existingStyle = document.getElementById('context-menu-styles');
        if (existingStyle) return;

        const style = document.createElement('style');
        style.id = 'context-menu-styles';
        style.textContent = `
            .context-menu {
                position: fixed;
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 10000;
                min-width: 200px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 14px;
            }

            .context-menu-header {
                padding: 12px 16px 8px;
                font-weight: 600;
                color: #333;
                border-bottom: 1px solid #eee;
            }

            .context-menu-list {
                list-style: none;
                margin: 0;
                padding: 8px 0;
            }

            .context-menu-item {
                padding: 10px 16px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
                transition: background-color 0.2s;
            }

            .context-menu-item:hover {
                background-color: #f5f5f5;
            }

            .context-menu-item.danger {
                color: #dc3545;
            }

            .context-menu-item.danger:hover {
                background-color: #fff5f5;
                color: #dc3545;
            }

            .context-menu-divider {
                height: 1px;
                background-color: #eee;
                margin: 4px 0;
            }

            .context-menu-item i {
                width: 16px;
                text-align: center;
            }
        `;
        document.head.appendChild(style);
    }

    attachContextMenuHandlers() {
        const menuItems = this.contextMenu.querySelectorAll('.context-menu-item[data-action]');
        menuItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleContextMenuAction(action);
                this.hideContextMenu();
            });
        });
    }

    attachGlobalEventListeners() {
        // Hide context menu on click outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#appointment-context-menu')) {
                this.hideContextMenu();
            }
        });

        // Hide context menu on scroll
        document.addEventListener('scroll', () => {
            this.hideContextMenu();
        });

        // Hide context menu on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideContextMenu();
            }
        });
    }

    showContextMenu(x, y, appointmentId) {
        this.currentAppointmentId = appointmentId;
        
        if (!this.contextMenu) {
            console.error('Context menu not initialized');
            return;
        }

        // Position the menu
        this.contextMenu.style.left = `${x}px`;
        this.contextMenu.style.top = `${y}px`;
        this.contextMenu.style.display = 'block';

        // Ensure menu stays within viewport
        this.adjustMenuPosition();

        // Update header with appointment info
        this.updateContextMenuHeader(appointmentId);

        console.log(`🎯 Context menu shown for appointment ${appointmentId} at (${x}, ${y})`);
    }

    adjustMenuPosition() {
        const menu = this.contextMenu;
        const menuRect = menu.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;

        // Adjust horizontal position
        if (menuRect.right > viewportWidth) {
            menu.style.left = `${viewportWidth - menuRect.width - 10}px`;
        }

        // Adjust vertical position
        if (menuRect.bottom > viewportHeight) {
            menu.style.top = `${viewportHeight - menuRect.height - 10}px`;
        }
    }

    updateContextMenuHeader(appointmentId) {
        // Find appointment data
        const appointmentElement = document.querySelector(`[data-appointment-id="${appointmentId}"]`);
        if (appointmentElement) {
            const clientName = appointmentElement.querySelector('.appointment-client')?.textContent || 'Unknown Client';
            const serviceName = appointmentElement.querySelector('.appointment-service')?.textContent || 'Unknown Service';
            
            const header = this.contextMenu.querySelector('#context-menu-title');
            header.textContent = `${clientName} - ${serviceName}`;
        }
    }

    hideContextMenu() {
        if (this.contextMenu) {
            this.contextMenu.style.display = 'none';
            this.currentAppointmentId = null;
        }
    }

    handleContextMenuAction(action) {
        if (!this.currentAppointmentId) {
            console.error('No appointment ID set for context menu action');
            return;
        }

        console.log(`🎬 Context menu action: ${action} for appointment ${this.currentAppointmentId}`);

        switch (action) {
            case 'view':
                this.viewAppointment(this.currentAppointmentId);
                break;
            case 'edit':
                this.editAppointment(this.currentAppointmentId);
                break;
            case 'reschedule':
                this.rescheduleAppointment(this.currentAppointmentId);
                break;
            case 'complete':
                this.completeAppointment(this.currentAppointmentId);
                break;
            case 'cancel':
                this.cancelAppointment(this.currentAppointmentId);
                break;
            case 'billing':
                this.goToBilling(this.currentAppointmentId);
                break;
            case 'delete':
                this.deleteAppointment(this.currentAppointmentId);
                break;
            default:
                console.log(`Unknown action: ${action}`);
        }
    }

    viewAppointment(appointmentId) {
        // Implement view appointment functionality
        console.log(`Viewing appointment ${appointmentId}`);
        // You can implement a modal or navigation to appointment details
        alert(`View appointment ${appointmentId} (implement actual view functionality)`);
    }

    editAppointment(appointmentId) {
        console.log(`Editing appointment ${appointmentId}`);
        // Open edit modal or form
        if (typeof openEditAppointmentModal === 'function') {
            openEditAppointmentModal(appointmentId);
        } else {
            alert(`Edit appointment ${appointmentId} (implement actual edit functionality)`);
        }
    }

    rescheduleAppointment(appointmentId) {
        console.log(`Rescheduling appointment ${appointmentId}`);
        alert(`Reschedule appointment ${appointmentId} (implement actual reschedule functionality)`);
    }

    completeAppointment(appointmentId) {
        if (confirm('Mark this appointment as completed?')) {
            this.updateAppointmentStatus(appointmentId, 'completed');
        }
    }

    cancelAppointment(appointmentId) {
        if (confirm('Cancel this appointment?')) {
            this.updateAppointmentStatus(appointmentId, 'cancelled');
        }
    }

    goToBilling(appointmentId) {
        console.log(`Redirecting to billing for appointment ${appointmentId}`);
        
        // Redirect to the existing appointment billing route
        window.location.href = `/appointment/${appointmentId}/go-to-billing`;
    }

    deleteAppointment(appointmentId) {
        if (confirm('Are you sure you want to delete this appointment? This action cannot be undone.')) {
            // Make API call to delete appointment
            fetch(`/api/unaki/appointments/${appointmentId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('✅ Appointment deleted successfully');
                    // Remove from DOM
                    const appointmentElement = document.querySelector(`[data-appointment-id="${appointmentId}"]`);
                    if (appointmentElement) {
                        appointmentElement.remove();
                    }
                    // Show success message
                    if (typeof showNotification === 'function') {
                        showNotification('Appointment deleted successfully', 'success');
                    }
                    // Refresh schedule
                    if (typeof refreshSchedule === 'function') {
                        refreshSchedule();
                    }
                } else {
                    console.error('Failed to delete appointment:', data.error);
                    alert('Failed to delete appointment: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error deleting appointment:', error);
                alert('Error deleting appointment. Please try again.');
            });
        }
    }

    updateAppointmentStatus(appointmentId, status) {
        fetch(`/api/unaki/bookings/${appointmentId}/update-status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: status })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log(`✅ Appointment ${appointmentId} status updated to ${status}`);
                // Update visual indication
                const appointmentElement = document.querySelector(`[data-appointment-id="${appointmentId}"]`);
                if (appointmentElement) {
                    appointmentElement.classList.add(`status-${status}`);
                }
                // Show success message
                if (typeof showNotification === 'function') {
                    showNotification(`Appointment marked as ${status}`, 'success');
                }
                // Refresh schedule
                if (typeof refreshSchedule === 'function') {
                    refreshSchedule();
                }
            } else {
                console.error(`Failed to update appointment status:`, data.error);
                alert(`Failed to update appointment status: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error updating appointment status:', error);
            alert('Error updating appointment status. Please try again.');
        });
    }

    reinitializeForAppointments() {
        // This function is called after DOM updates to reattach event listeners
        console.log('🔄 Reinitializing context menu for appointments');
        
        // Find all appointment blocks
        const appointmentBlocks = document.querySelectorAll('.appointment-block');
        console.log(`🔍 Found ${appointmentBlocks.length} appointment blocks to initialize`);

        appointmentBlocks.forEach((block, index) => {
            // Remove existing right-click listeners
            const clone = block.cloneNode(true);
            block.parentNode.replaceChild(clone, block);
            
            // Add right-click event listener
            clone.addEventListener('contextmenu', (event) => {
                event.preventDefault();
                event.stopPropagation();
                
                const appointmentId = this.getAppointmentId(clone);
                if (appointmentId) {
                    console.log(`🎯 Right-click detected on appointment ${appointmentId}`);
                    this.showContextMenu(event.pageX, event.pageY, appointmentId);
                } else {
                    console.error('No appointment ID found for right-clicked element');
                }
            });

            // Mark as context menu ready
            clone.setAttribute('data-context-menu-ready', 'true');
            console.log(`✅ Context menu attached to appointment ${index + 1}: ID ${this.getAppointmentId(clone)}`);
        });

        console.log('✅ Context menu reinitialized');
        console.log(`📊 Context menu coverage: ${appointmentBlocks.length}/${appointmentBlocks.length} appointment blocks`);
    }

    getAppointmentId(element) {
        // Try multiple ways to get appointment ID
        return element.dataset.appointmentId || 
               element.getAttribute('data-appointment-id') || 
               element.getAttribute('data-id') ||
               null;
    }
}

// Global instance
let appointmentContextMenu = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    appointmentContextMenu = new AppointmentContextMenu();
});

// Global functions for compatibility
window.reinitializeContextMenu = function() {
    if (appointmentContextMenu) {
        appointmentContextMenu.reinitializeForAppointments();
    } else {
        console.error('Context menu not initialized yet');
    }
};

window.handleAppointmentRightClick = function(event) {
    if (appointmentContextMenu) {
        event.preventDefault();
        event.stopPropagation();
        
        const appointmentElement = event.currentTarget;
        const appointmentId = appointmentContextMenu.getAppointmentId(appointmentElement);
        
        if (appointmentId) {
            console.log(`🎯 Right-click detected on appointment ${appointmentId}`);
            appointmentContextMenu.showContextMenu(event.pageX, event.pageY, appointmentId);
        }
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AppointmentContextMenu };
}
